"""Verify the new worker in ephemeral Modal sandboxes; does not deploy either API."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import time


def fixture(directory):
    root = directory / 'packages/0/fixture'
    for folder in ('src', 'app', 'test'):
        (root / folder).mkdir(parents=True, exist_ok=True)
    (root / 'fpm.toml').write_text('name="verification-fixture"\n')
    (root / 'src/math.f90').write_text('module fixture_math\ncontains\ninteger function answer()\nanswer=42\nend function\nend module\n')
    (root / 'app/alpha.f90').write_text('program alpha\ninteger n\nread(*,*) n\nprint *, n+1\nend program\n')
    (root / 'app/beta.f90').write_text('program beta\nprint *, "BETA"\nend program\n')
    (root / 'test/check.f90').write_text('program check\nuse fixture_math\nif(answer()/=42)error stop\nprint *, "TEST PASS"\nend program\n')
    return root.relative_to(directory).as_posix()


def main():
    import modal
    from fpm_sources import Preparer, validate_request
    from xfpm_modal import ROOT, bundle_sources, execute_job, runtime_image

    app = modal.App('fortran-playground-fpm-verification')
    results = []

    def trial(name, payload, *, use_fixture=False, expected_ok=True, marker='', needs_target=False):
        started = time.monotonic()
        payload = validate_request(payload)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            if use_fixture:
                root = fixture(directory)
                packages = []
            else:
                root, packages = Preparer(directory).prepare(payload)
            message = {'request': payload, 'root': root, 'bundle': bundle_sources(directory)}
        sandbox = modal.Sandbox.create('python', '/opt/fpm/xfpm_worker.py', app=app,
            image=runtime_image, runtime='gvisor', workdir='/work', timeout=250,
            cpu=(0.5, 1.0), memory=(512, 1024), block_network=True, secrets=[], volumes={},
            include_oidc_identity_token=False, env={'OMP_NUM_THREADS': '1', 'HOME': '/work'})
        try:
            sandbox.stdin.write((json.dumps(message) + '\n').encode())
            sandbox.stdin.write_eof()
            sandbox.stdin.drain()
            sandbox.wait()
            output = sandbox.stdout.read()
            try:
                result = json.loads(output)
            except ValueError:
                result = {'ok': False, 'error': sandbox.stderr.read()[-3000:] + output[-3000:]}
            checked = result.get('ok') == expected_ok and sandbox.returncode == 0
            checked = checked and (not marker or marker in json.dumps(result))
            checked = checked and (not needs_target or result.get('needs_target'))
            record = {'name': name, 'verified': bool(checked), 'expected_ok': expected_ok,
                      'seconds': round(time.monotonic() - started, 3), 'packages': packages, 'result': deepcopy(result)}
            # Keep the committed evidence compact, including output-limit probes.
            for stage in record['result'].get('stages', []):
                for field in ('stdout', 'stderr'):
                    if len(stage.get(field, '')) > 4000:
                        stage[field] = stage[field][:4000] + '\n[verification report excerpt]\n'
            results.append(record)
            print(f'{name}: {"VERIFIED" if checked else "FAILED"} {record["seconds"]:.3f} seconds', flush=True)
            if not checked:
                print(json.dumps(record['result'])[-6000:], flush=True)
        finally:
            sandbox.terminate()

    with modal.enable_output(), app.run():
        for package in json.loads((ROOT / 'site/fpm/examples.json').read_text()):
            trial('consumer-' + package['name'], {'url': 'https://github.com/' + package['repository'],
                'revision': package['revision'], 'source': package['source']}, marker='PASS ' + package['name'])
        base = {'url': 'https://github.com/example/fixture', 'workflow': 'package'}
        trial('package-build', {**base, 'action': 'build'}, use_fixture=True)
        trial('target-discovery', base, use_fixture=True, expected_ok=False, needs_target=True)
        trial('target-and-stdin', {**base, 'target': 'alpha', 'stdin': '41\n'}, use_fixture=True, marker='42')
        trial('package-test', {**base, 'action': 'test'}, use_fixture=True, marker='TEST PASS')
        trial('compile-failure', {**base, 'workflow': 'consumer', 'source': 'this is not Fortran'},
              use_fixture=True, expected_ok=False, marker='Build')
        noisy = 'program main\ninteger i\ndo i=1,100000\nprint *, repeat("X",100)\nend do\nend program\n'
        trial('output-bound', {**base, 'workflow': 'consumer', 'source': noisy}, use_fixture=True,
              expected_ok=False, marker='200000-byte')
        catalog = json.loads((ROOT / 'site/fpm/examples.json').read_text())
        for name in ('datetime', 'pchip', 'toml'):
            package = next(item for item in catalog if item['name'] == name)
            trial('upstream-tests-' + name, {'url': 'https://github.com/' + package['repository'],
                'revision': package['revision'], 'workflow': 'package', 'action': 'test'})
        package = next(item for item in catalog if item['name'] == 'pchip')
        payload = validate_request({'url': 'https://github.com/' + package['repository'],
                                    'revision': package['revision'], 'source': package['source']})
        result = execute_job('verification', payload, sandbox_app=app, sandbox_image=runtime_image, cancelled=lambda: False)
        checked = result.get('ok') and 'PASS pchip' in json.dumps(result) and bool(result.get('packages'))
        results.append({'name': 'coordinator-complete', 'verified': bool(checked), 'result': result})
        print(f'coordinator-complete: {"VERIFIED" if checked else "FAILED"}', flush=True)
        checks = iter([False, True])
        payload['source'] = 'program forever\ndo\nend do\nend program\n'
        result = execute_job('verification', payload, sandbox_app=app, sandbox_image=runtime_image,
                             cancelled=lambda: next(checks, True))
        checked = not result.get('ok') and result.get('error') == 'Cancelled.'
        results.append({'name': 'coordinator-cancel', 'verified': bool(checked), 'result': result})
        print(f'coordinator-cancel: {"VERIFIED" if checked else "FAILED"}', flush=True)
    report = {'compiler': 'gfortran 16.2.0', 'fpm': '0.12.0', 'network': 'blocked',
              'build_timeout': 180, 'run_timeout': 30, 'sandbox_timeout': 250, 'runs': results}
    (ROOT / 'docs/fpm-validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if all(item['verified'] for item in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
