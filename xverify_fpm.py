"""Verify the new worker in ephemeral Modal sandboxes; does not deploy either API."""
from copy import deepcopy
import argparse
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compilers', nargs='+', choices=['gfortran', 'gfortran17', 'ifx', 'flang'], default=['gfortran'])
    parser.add_argument('--report', default='docs/fpm-validation.json')
    parser.add_argument('--plotting-only', action='store_true', help='Verify PNG results with the fixture and upstream pyplot-fortran')
    args = parser.parse_args()
    import modal
    from fpm_sources import Preparer, validate_request
    from xfpm_modal import ROOT, bundle_sources, execute_job, runtime_images

    app = modal.App('fortran-playground-fpm-verification')
    results = []
    images = runtime_images(args.compilers)
    current_compiler = args.compilers[0]

    def trial(name, payload, *, use_fixture=False, expected_ok=True, marker='', needs_target=False, known_failure='', expected_plot=False):
        started = time.monotonic()
        payload = validate_request({**payload, 'compiler': current_compiler})
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            if use_fixture:
                root = fixture(directory)
                packages = []
            else:
                root, packages = Preparer(directory).prepare(payload)
            message = {'request': payload, 'root': root, 'bundle': bundle_sources(directory)}
        sandbox = modal.Sandbox.create('python', '/opt/fpm/xfpm_worker.py', app=app,
            image=images[current_compiler], runtime='gvisor', workdir='/work', timeout=250,
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
            if expected_plot:
                import base64
                from fortran_plot import valid_png
                checked = checked and bool(result.get('plots')) and all(valid_png(base64.b64decode(plot['data'])) for plot in result.get('plots', []))
            limitation = bool(known_failure and not result.get('ok') and known_failure in json.dumps(result))
            checked = checked or limitation
            record = {'name': name, 'compiler': current_compiler, 'verified': bool(checked), 'expected_ok': expected_ok,
                      'seconds': round(time.monotonic() - started, 3), 'packages': packages, 'result': deepcopy(result)}
            for plot in record['result'].get('plots', []):
                plot['base64_bytes'] = len(plot.pop('data'))
            if limitation:
                record['known_failure'] = 'GNU 17 internal compiler error in test-drive: ' + known_failure
            # Keep the committed evidence compact, including output-limit probes.
            for stage in record['result'].get('stages', []):
                for field in ('stdout', 'stderr'):
                    if len(stage.get(field, '')) > 4000:
                        stage[field] = stage[field][:4000] + '\n[verification report excerpt]\n'
            results.append(record)
            status = 'KNOWN COMPILER FAILURE' if limitation else 'VERIFIED' if checked else 'FAILED'
            print(f'{current_compiler} {name}: {status} {record["seconds"]:.3f} seconds', flush=True)
            if not checked:
                print(json.dumps(record['result'])[-6000:], flush=True)
        finally:
            sandbox.terminate()

    def compiler_trials():
        if args.plotting_only:
            source = (ROOT / 'docs/examples/plot_trig.f90').read_text()
            trial('plotting-consumer', {'url': 'https://github.com/example/fixture', 'source': source},
                  use_fixture=True, expected_plot=True)
            pin = json.loads((ROOT / 'vendor/pyplot-fortran/upstream.json').read_text())
            trial('plotting-upstream-library', {'url': pin['repository'], 'revision': pin['revision'], 'source': source}, expected_plot=True)
            return
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
                'revision': package['revision'], 'workflow': 'package', 'action': 'test'},
                known_failure='gfc_get_location_with_offset' if name == 'toml' and current_compiler == 'gfortran17' else '')
        package = next(item for item in catalog if item['name'] == 'pchip')
        payload = validate_request({'url': 'https://github.com/' + package['repository'],
                                    'revision': package['revision'], 'source': package['source']})
        payload['compiler'] = current_compiler
        result = execute_job('verification', payload, sandbox_app=app, sandbox_image=images[current_compiler], cancelled=lambda: False)
        checked = result.get('ok') and 'PASS pchip' in json.dumps(result) and bool(result.get('packages'))
        results.append({'name': 'coordinator-complete', 'compiler': current_compiler, 'verified': bool(checked), 'result': result})
        print(f'coordinator-complete: {"VERIFIED" if checked else "FAILED"}', flush=True)
        checks = iter([False, True])
        payload['source'] = 'program forever\ndo\nend do\nend program\n'
        result = execute_job('verification', payload, sandbox_app=app, sandbox_image=images[current_compiler],
                             cancelled=lambda: next(checks, True))
        checked = not result.get('ok') and result.get('error') == 'Cancelled.'
        results.append({'name': 'coordinator-cancel', 'compiler': current_compiler, 'verified': bool(checked), 'result': result})
        print(f'coordinator-cancel: {"VERIFIED" if checked else "FAILED"}', flush=True)
    with modal.enable_output(), app.run():
        for current_compiler in args.compilers:
            compiler_trials()
    report = {'compilers': args.compilers, 'fpm': '0.12.0', 'network': 'blocked',
              'build_timeout': 180, 'run_timeout': 30, 'sandbox_timeout': 250, 'runs': results}
    (ROOT / args.report).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if all(item['verified'] for item in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
