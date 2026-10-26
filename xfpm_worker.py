"""Execute prepared FPM sources inside a disposable network-blocked Linux sandbox."""
import base64
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time
import tomllib

from fpm_sources import extract_archive, validate_request
from fpm_compilers import COMPILERS, compiler_flags
from fpm_cache import consumer_project, cached_request_matches, library_inventory
from fortran_plot import uses_pyplot, install_module, collect_plots, plotting_environment, provides_pyplot


def stage(command, directory, timeout, stdin=''):
    started = time.monotonic()
    # A regular file avoids pipe deadlock with large standard input.
    input_path = Path('/work/stdin.txt')
    input_path.write_text(stdin, encoding='utf-8')
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    reason = ''
    with input_path.open('rb') as input_stream:
        process = subprocess.Popen(command, cwd=directory, stdin=input_stream, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ, 'stdout')
            selector.register(process.stderr, selectors.EVENT_READ, 'stderr')
            # Also supervise processes which close both pipes before exiting.
            while selector.get_map() or process.poll() is None:
                if time.monotonic() - started > timeout:
                    reason = f'Timed out after {timeout} seconds.'
                if reason:
                    break
                for key, _ in selector.select(timeout=0.05):
                    chunk = key.fileobj.read1(4096)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue
                    available = 200000 - sum(map(len, buffers.values()))
                    buffers[key.data].extend(chunk[:max(0, available)])
                    if len(chunk) > available:
                        reason = 'Output exceeded the 200000-byte stage limit.'
        # Kill descendants too, even if the original process already exited.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=5)
        process.stdout.close()
        process.stderr.close()
    return {'command': command, 'seconds': round(time.monotonic() - started, 3),
            'ok': process.returncode == 0 and not reason, 'exit_code': process.returncode,
            'error': reason, **{key: value.decode('utf-8', errors='replace') for key, value in buffers.items()}}


def targets(project, kind):
    return sorted({path.name for path in (project / 'build').glob(f'*/{kind}/*')
                   if path.is_file() and os.access(path, os.X_OK)})


def execute(message):
    os.environ.update(plotting_environment())
    payload = validate_request(message['request'])
    compiler = payload['compiler']
    if compiler != os.environ.get('FPM_COMPILER', 'gfortran'):
        raise ValueError('Requested compiler does not match this sandbox image.')
    cached = None
    if message.get('cache_key'):
        cached = json.loads(Path('/work/precompiled.json').read_text())
        if not cached_request_matches(payload, cached) or cached['key'] != message['cache_key']:
            raise ValueError('Precompiled package does not match the request.')
        bundle = Path('/work/sources/bundle')
        root = cached['root']
    else:
        bundle = extract_archive(base64.b64decode(message['bundle'], validate=True), Path('/work/sources'),
                                 require_manifest=False)
        root = message['root']
    package = (bundle / root).resolve()
    if not package.is_relative_to(bundle.resolve()) or not (package / 'fpm.toml').is_file():
        raise ValueError('Invalid staged package root.')
    project = package
    if payload['workflow'] == 'consumer':
        project = consumer_project(package, payload['source'])
    os.environ.update(plotting_environment(directory=project))
    flags = compiler_flags(compiler)
    version = subprocess.check_output([COMPILERS[compiler]['command'], '--version'], text=True, timeout=10).splitlines()[0]
    if COMPILERS[compiler]['version'] not in version:
        raise ValueError('Installed compiler version does not match the selected toolchain.')
    result = {'ok': False, 'compiler': version, 'compiler_id': compiler, 'fpm': '0.12.0', 'stages': []}
    build_command = ['fpm', 'build', *flags] + (['--tests'] if payload['action'] == 'test' else [])
    build = stage(build_command, project, 180)
    result['stages'].append({'name': 'Build', **build})
    if cached:
        inventory = library_inventory(main_modules=cached.get('main_modules', []))
        changes = [path for path, stat in cached['inventory'].items() if inventory.get(path) != stat]
        result['cache'] = {'package': cached['id'], 'compiler': 'GNU Fortran 16.2.0',
                           'key': cached['key'], 'library_reused': inventory == cached['inventory'],
                           'changed_artifacts': [{'path': p, 'before': cached['inventory'][p],
                                                  'after': inventory.get(p)} for p in changes[:3]]}
        result['packages'] = cached['records']
    if not build['ok']:
        return result
    kind = 'test' if payload['action'] == 'test' else 'app'
    result['targets'] = available = targets(project, kind)
    if payload['action'] == 'build':
        result['ok'] = True
        return result
    if not available:
        result['error'] = f'This package has no {"test" if kind == "test" else "application"} targets. Try Build or supply a custom main program.'
        return result
    target = payload['target'] if payload['workflow'] == 'package' else ''
    if target and target not in available:
        result.update(error='The selected target was not found. Choose an available target.', needs_target=True)
        return result
    if kind == 'app' and not target and len(available) > 1:
        result.update(error='Choose an application target, then submit again.', needs_target=True)
        return result
    command = ['fpm', payload['action'], *flags] + (['--target', target] if target else [])
    run = stage(command, project, 30, payload['stdin'])
    result['stages'].append({'name': 'Test' if kind == 'test' else 'Run', **run})
    result.update(collect_plots(project))
    result['ok'] = run['ok']
    return result


def main():
    import resource
    if os.geteuid() == 0:
        os.setgroups([])
        os.setgid(65534)
        os.setuid(65534)
    if os.geteuid() == 0:
        raise RuntimeError('Refusing to run package code as root.')
    for limit, value in [(resource.RLIMIT_CORE, 0), (resource.RLIMIT_FSIZE, 16 * 1024 * 1024),
                         (resource.RLIMIT_NOFILE, 128), (resource.RLIMIT_NPROC, 128)]:
        resource.setrlimit(limit, (value, value))
    message = json.loads(sys.stdin.buffer.readline(24000000))
    return execute(message)


if __name__ == '__main__':
    try:
        result = main()
    except Exception as error:
        result = {'ok': False, 'error': f'{type(error).__name__}: {error}', 'stages': []}
    print(json.dumps(result), flush=True)
