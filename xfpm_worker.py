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
from fpm_targets import parse_targets, select_targets, discover_targets
from fpm_compilers import COMPILERS, compiler_flags, preprocessing_flag
from fpm_cache import consumer_project, cached_request_matches, library_inventory
from fortran_plot import uses_pyplot, install_module, plotting_environment, provides_pyplot
from fortran_image import collect_plots


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
    return discover_targets(project, kind)


def execute(message):
    os.environ.update(plotting_environment())
    target_text = message['request'].get('target', '')
    parse_targets(target_text)
    action = message['request'].get('action', 'run')
    preprocess = message['request'].get('preprocess', False)
    if type(preprocess) is not bool:
        raise ValueError('Preprocess must be a boolean.')
    if action == 'example' and message['request'].get('workflow', 'consumer') != 'package':
        raise ValueError('Run examples requires the package workflow.')
    payload = validate_request({**{k: v for k, v in message['request'].items() if k != 'preprocess'}, 'target': '',
                                **({'action': 'run'} if action == 'example' else {})})
    payload['target'] = target_text
    payload['action'] = action
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
    if preprocess:
        flags += ['--flag', preprocessing_flag(compiler)]
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
    result['build_ok'] = True
    result['target_groups'] = {kind: targets(project, kind) for kind in ('app', 'example', 'test')}
    kind = {'test': 'test', 'example': 'example'}.get(payload['action'], 'app')
    result['targets'] = available = result['target_groups'][kind]
    if payload['action'] == 'build':
        result['ok'] = True
        return result
    if not available:
        result.update(status='NOT_RUN', nothing_run=True,
                      error=f'This package has no {kind} targets. Choose Run examples, Test, Build, or supply a custom main program.')
        return result
    target = payload['target'] if payload['workflow'] == 'package' else ''
    if kind in ('app', 'example') and not target.strip() and len(available) > 1:
        result.update(error=f'Choose {kind} targets, then submit again.', needs_target=True,
                      status='NOT_RUN', nothing_run=True)
        return result
    try:
        selected = select_targets(target, available)
    except ValueError as error:
        result.update(error=str(error), needs_target=True, status='NOT_RUN', nothing_run=True)
        return result
    command = ['fpm', 'run' if kind == 'example' else payload['action'], *flags,
               *(['--example'] if kind == 'example' else []), *(['--target', *selected] if selected else [])]
    run = stage(command, project, 30, payload['stdin'])
    result['stages'].append({'name': {'test': 'Test', 'example': 'Examples'}.get(kind, 'Run'), **run})
    if run['ok'] and '<INFO> No executables to run' in run['stderr']:
        result.update(status='NOT_RUN', nothing_run=True, error='FPM found no runnable targets. Choose another action or target.')
        return result
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
