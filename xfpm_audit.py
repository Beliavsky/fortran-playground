"""Prepare pinned packages and benchmark them in isolated Modal sandboxes.

This is an offline feasibility tool, not part of either playground's request path.
Run with the Python environment containing Modal: python xfpm_audit.py --prepare-only
or python xfpm_audit.py --repetitions 2
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / 'docs' / 'fpm-feasibility'
CACHE = ROOT / '.fpm-audit-cache'
GNU_IMAGE = 'gcc:16.2.0-trixie@sha256:43978d7710a803d1c3d32f4117c1528ec7285a4ce2c0a51e982ec1a6e3d87d95'
FPM_URL = 'https://github.com/fortran-lang/fpm/releases/download/v0.12.0/fpm-0.12.0-linux-x86_64-gcc-12'


def download(url, limit=16 * 1024 * 1024):
    started = time.monotonic()
    request = Request(url, headers={'User-Agent': 'Fortran-playground-FPM-feasibility-audit'})
    with urlopen(request, timeout=60) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f'Download exceeds audit limit: {url}')
    return data, time.monotonic() - started


def prepare():
    CACHE.mkdir(exist_ok=True)
    lock_path = AUDIT / 'packages.lock.json'
    packages = json.loads(lock_path.read_text(encoding='utf-8'))
    catalog, _ = download('https://raw.githubusercontent.com/Beliavsky/Fortran-packages-list/main/README.md')
    for package in packages:
        if package['listed_repository'].lower() not in catalog.decode('utf-8').lower():
            raise ValueError(f'Package is absent from the supplied list: {package["name"]}')
        if not package.get('revision'):
            data, _ = download(f'https://api.github.com/repos/{package["repository"]}/commits/HEAD')
            package['revision'] = json.loads(data)['sha']
        archive = CACHE / f'{package["name"]}-{package["revision"]}.tar.gz'
        url = f'https://codeload.github.com/{package["repository"]}/tar.gz/{package["revision"]}'
        if not archive.exists() or not package.get('sha256'):
            data, elapsed = download(url)
            digest = hashlib.sha256(data).hexdigest()
            if package.get('sha256') and package['sha256'] != digest:
                raise ValueError(f'Archive digest changed: {package["name"]}')
            archive.write_bytes(data)
            package.update(download_seconds=round(elapsed, 3), archive_bytes=len(data), sha256=digest)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != package['sha256']:
            raise ValueError(f'Archive checksum mismatch: {archive}')
        package['archive'] = archive.name
        demo_source = (AUDIT / 'demos' / f'{package["name"]}.f90').read_text(encoding='utf-8')
        package['demo_sha256'] = hashlib.sha256(demo_source.encode('utf-8')).hexdigest()
        lock_path.write_text(json.dumps(packages, indent=2) + '\n', encoding='utf-8')
        print(f'Prepared {package["name"]} {package["revision"][:12]}', flush=True)
    lock_path.write_text(json.dumps(packages, indent=2) + '\n', encoding='utf-8')
    binary = CACHE / 'fpm-linux'
    checksum_text, _ = download(FPM_URL + '.sha256')
    checksum = checksum_text.decode().split()[0]
    if not binary.exists():
        binary.write_bytes(download(FPM_URL)[0])
    if hashlib.sha256(binary.read_bytes()).hexdigest() != checksum:
        raise ValueError('FPM release binary checksum mismatch')
    metadata = {'gnu_image': GNU_IMAGE, 'fpm_url': FPM_URL, 'fpm_sha256': checksum,
                'catalog_url': 'https://raw.githubusercontent.com/Beliavsky/Fortran-packages-list/main/README.md',
                'catalog_sha256': hashlib.sha256(catalog).hexdigest(),
                'worker_sha256': hashlib.sha256((ROOT / 'xfpm_audit_worker.py').read_text(encoding='utf-8').encode('utf-8')).hexdigest(),
                'profile': 'debug', 'build_timeout': 180, 'run_timeout': 30, 'sandbox_timeout': 250,
                'cpu': [0.5, 1.0], 'memory_mib': [512, 1024], 'network': 'blocked',
                'runtime': 'gvisor', 'file_limit_bytes': 16 * 1024 * 1024,
                'output_limit_bytes_per_stage': 200000, 'packages': packages}
    (CACHE / 'config.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    # Only prepared artifacts and our own small demonstrations are uploaded.
    bundle = CACHE / 'bundle'
    bundle.mkdir(exist_ok=True)
    for package in packages:
        shutil.copyfile(CACHE / package['archive'], bundle / package['archive'])
        shutil.copyfile(AUDIT / 'demos' / f'{package["name"]}.f90', bundle / f'{package["name"]}.f90')
    shutil.copyfile(CACHE / 'config.json', bundle / 'config.json')
    return metadata


def save_results(metadata, results):
    report = {**metadata, 'runs': results}
    (AUDIT / 'results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    fields = ['package', 'repetition', 'ok', 'build_seconds', 'run_seconds', 'build_peak_rss_kib',
              'run_peak_rss_kib', 'sandbox_client_seconds', 'failure']
    with (AUDIT / 'results.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader(); writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--repetitions', type=int, default=2, choices=(1, 2, 3))
    args = parser.parse_args()
    metadata = prepare()
    metadata['repetitions'] = args.repetitions
    if args.prepare_only:
        return
    import modal
    app = modal.App('fortran-playground-fpm-feasibility-audit')
    image = (modal.Image.from_registry(GNU_IMAGE, add_python='3.12')
             .apt_install('time')
             .add_local_file(CACHE / 'fpm-linux', '/usr/local/bin/fpm', copy=True)
             .run_commands('chmod 755 /usr/local/bin/fpm', 'mkdir -p /work && chmod 1777 /work',
                           'test "$(gfortran -dumpfullversion)" = 16.2.0', 'fpm --version')
             .add_local_file(ROOT / 'xfpm_audit_worker.py', '/opt/audit/worker.py', copy=True)
             .add_local_dir(CACHE / 'bundle', '/opt/audit/bundle', copy=True))
    results = []
    with modal.enable_output(), app.run():
        for package in metadata['packages']:
            for repetition in range(1, args.repetitions + 1):
                started = time.monotonic()
                sandbox = modal.Sandbox.create('python', '/opt/audit/worker.py', package['name'], app=app,
                    image=image, runtime='gvisor', workdir='/work', timeout=250, cpu=(0.5, 1.0),
                    memory=(512, 1024), block_network=True, secrets=[], volumes={}, include_oidc_identity_token=False,
                    env={'OMP_NUM_THREADS': '1', 'HOME': '/work'})
                try:
                    sandbox.wait()
                    stdout, stderr = sandbox.stdout.read(), sandbox.stderr.read()
                    try:
                        result = json.loads(stdout)
                    except ValueError:
                        result = {'package': package['name'], 'ok': False,
                                  'failure': f'Sandbox exit {sandbox.returncode}: {stderr[-2000:]} {stdout[-2000:]}'}
                    result.update(repetition=repetition, sandbox_client_seconds=round(time.monotonic() - started, 3),
                                  sandbox_exit_code=sandbox.returncode)
                    results.append(result)
                    save_results(metadata, results)
                    print(f'{package["name"]} #{repetition}: {result.get("ok")} '
                          f'build={result.get("build_seconds")} run={result.get("run_seconds")}', flush=True)
                finally:
                    sandbox.terminate()
    passed = {name for name in {row['package'] for row in results}
              if all(row['ok'] and row['build_seconds'] < 120 and row['run_seconds'] < 20
                     for row in results if row['package'] == name)}
    print(f'{len(passed)} packages passed every repetition with headroom: {", ".join(sorted(passed))}')
    return 0 if len(passed) >= 5 else 1


if __name__ == '__main__':
    raise SystemExit(main())
