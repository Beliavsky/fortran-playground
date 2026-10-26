"""One pinned FPM consumer build/run inside a disposable, network-blocked sandbox."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tarfile
import time


def extract_package(archive, destination):
    with tarfile.open(archive) as stream:
        members = stream.getmembers()
        if sum(member.size for member in members) > 64 * 1024 * 1024:
            raise ValueError('Archive exceeds 64 MiB uncompressed audit bound')
        roots = set()
        for member in members:
            relative = Path(member.name)
            if relative.is_absolute() or '..' in relative.parts or not relative.parts:
                raise ValueError('Unsafe archive path')
            if not (member.isfile() or member.isdir()) or member.size > 16 * 1024 * 1024:
                raise ValueError('Archive contains a link, special file, or oversized member')
            roots.add(relative.parts[0])
        if len(roots) != 1:
            raise ValueError('Expected one archive root')
        stream.extractall(destination, filter='data')
    root = destination / roots.pop()
    if not (root / 'fpm.toml').is_file():
        raise ValueError('Missing root fpm.toml')
    return root


def stage(command, directory, timeout, label):
    started = time.monotonic()
    peak = directory / f'{label}-peak.txt'
    process = subprocess.Popen(['/usr/bin/time', '-f', '%M', '-o', str(peak), *command], cwd=directory,
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    buffers = {'stdout': bytearray(), 'stderr': bytearray()}
    reason = ''
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ, 'stdout')
        selector.register(process.stderr, selectors.EVENT_READ, 'stderr')
        while selector.get_map():
            if time.monotonic() - started > timeout:
                reason = f'Timed out after {timeout} seconds'
            if reason:
                os.killpg(process.pid, signal.SIGKILL)
                break
            for key, _ in selector.select(timeout=0.05):
                chunk = key.fileobj.read1(4096)
                if not chunk:
                    selector.unregister(key.fileobj); continue
                available = 200000 - sum(map(len, buffers.values()))
                buffers[key.data].extend(chunk[:max(0, available)])
                if len(chunk) > available:
                    reason = 'Output exceeds 200000-byte audit bound'
    process.wait(timeout=5)
    process.stdout.close(); process.stderr.close()
    peaks = peak.read_text().splitlines() if peak.exists() else []
    return {'command': command, 'seconds': round(time.monotonic() - started, 3),
            'ok': process.returncode == 0 and not reason, 'exit_code': process.returncode, 'error': reason,
            'peak_rss_kib': int(peaks[-1]) if peaks and peaks[-1].isdigit() else None,
            **{key: value.decode('utf-8', errors='replace') for key, value in buffers.items()}}


def main(name):
    import resource  # Linux-only worker; archive/manifest helpers remain testable on Windows.
    if os.geteuid() == 0:
        os.setgroups([]); os.setgid(65534); os.setuid(65534)
    if os.geteuid() == 0:
        raise RuntimeError('Refusing to execute package code as root')
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
    resource.setrlimit(resource.RLIMIT_NPROC, (128, 128))
    bundle = Path('/opt/audit/bundle')
    config = json.loads((bundle / 'config.json').read_text())
    package = next(item for item in config['packages'] if item['name'] == name)
    started = time.monotonic()
    result = {'package': name, 'revision': package['revision'], 'ok': False,
              'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'uid': os.geteuid(),
              'compiler': subprocess.check_output(['gfortran', '--version'], text=True).splitlines()[0],
              'fpm_version': subprocess.check_output(['fpm', '--version'], text=True).strip()}
    archive = bundle / package['archive']
    if hashlib.sha256(archive.read_bytes()).hexdigest() != package['sha256']:
        raise ValueError('Archive checksum mismatch')
    source = extract_package(archive, Path('/work') / 'sources')
    project = Path('/work') / 'consumer'
    (project / 'app').mkdir(parents=True)
    (project / 'app' / 'main.f90').write_text((bundle / f'{name}.f90').read_text(), encoding='utf-8')
    (project / 'fpm.toml').write_text('name = "audit-demo"\n[build]\nauto-tests = false\nauto-examples = false\n'
        '[dependencies]\n' + json.dumps(package['dependency_name']) + ' = { path = ' +
        json.dumps(Path(os.path.relpath(source, project)).as_posix()) + ' }\n')
    result['prepare_seconds'] = round(time.monotonic() - started, 3)
    result['source_bytes'] = sum(path.stat().st_size for path in source.rglob('*') if path.is_file())
    flags = ['--profile', 'debug', '--compiler', 'gfortran', '--no-prune']
    result['build'] = build = stage(['fpm', 'build', *flags], project, 180, 'build')
    result.update(build_seconds=build['seconds'], build_peak_rss_kib=build['peak_rss_kib'])
    if build['ok']:
        result['run'] = run = stage(['fpm', 'run', *flags], project, 30, 'run')
        result.update(run_seconds=run['seconds'], run_peak_rss_kib=run['peak_rss_kib'])
        result['ok'] = run['ok'] and f'PASS {name}' in run['stdout']
        if not result['ok']: result['failure'] = 'Run failed or demonstration assertion/PASS marker was missing'
    else:
        result['failure'] = 'Build failed: ' + (build['error'] or build['stderr'][-1500:])
    files = [path for path in Path('/work').rglob('*') if path.is_file()]
    result['work_bytes'] = sum(path.stat().st_size for path in files)
    result['largest_file_bytes'] = max((path.stat().st_size for path in files), default=0)
    result['worker_seconds'] = round(time.monotonic() - started, 3)
    return result


if __name__ == '__main__':
    try:
        result = main(sys.argv[1])
    except Exception as error:
        result = {'package': sys.argv[1], 'ok': False, 'failure': f'{type(error).__name__}: {error}'}
    print(json.dumps(result), flush=True)
