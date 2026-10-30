"""Verify selected GAMS drivers against existing compiled GNU 16 package images."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def verification_record(driver, result):
    """Accept only a successful execution of the requested main with library reuse."""
    stages = result.get('stages', [])
    builds = [s for s in stages if s.get('name') == 'Build']
    runs = [s for s in stages if s.get('name') == 'Run']
    marker = 'PASS '+driver['id']
    if (not result.get('ok') or len(builds) != 1 or len(runs) != 1
            or not builds[0].get('ok') or not runs[0].get('ok')
            or runs[0].get('exit_code') != 0
            or marker not in runs[0].get('stdout', '').splitlines()
            or not result.get('cache', {}).get('library_reused')
            or not re.search(r'GNU Fortran.*16\.', result.get('compiler', ''))):
        raise ValueError(driver['id']+': requires a successful GNU 16 run and cached-library reuse.')
    compiled = re.findall(r'\]\s+(.+?)\s+done\.', builds[0].get('stdout', ''))
    if set(compiled) != {'main.f90', 'playground-main'}:
        raise ValueError(driver['id']+': expected compilation of only the driver and executable.')
    source = (ROOT/driver['path']).read_text(encoding='utf-8')
    return {'driver_id': driver['id'], 'source_revision': driver['revision'],
            'source_sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
            'ok': True, 'compiler': result['compiler'], 'fpm': result['fpm'],
            'library_reused': True, 'compiled_targets': compiled,
            'validated_at': datetime.now(timezone.utc).isoformat(),
            'stages': [{k: s[k] for k in ('name', 'ok', 'stdout', 'stderr', 'seconds', 'exit_code')}
                       for s in stages]}


def main():
    manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text(encoding='utf-8'))
    drivers = {d['id']: d for d in manifest['drivers']}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--drivers', nargs='+', choices=sorted(drivers), required=True)
    parser.add_argument('--build-report', type=Path, default=ROOT/'.fpm-audit-cache/precompiled.json')
    parser.add_argument('--results-dir', type=Path, default=ROOT/'.fpm-audit-cache/gams-driver-verification')
    args = parser.parse_args()
    from fpm_cache import catalog, cache_identity, recipe_identity
    from xpackage_gams import gams_data, safe_path, driver_validation_path
    gams_data(ROOT)
    packages = {p['id']: p for p in catalog()}
    builds = json.loads(args.build_report.read_text(encoding='utf-8'))['packages']
    import modal
    app = modal.App.lookup('fortran-playground-fpm', create_if_missing=False)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    for identity in args.drivers:
        driver = drivers[identity]
        report_path = ROOT/driver_validation_path(driver)
        report = (json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {
            'schema': 1, 'environment': 'Hosted FPM playground sandbox',
            'hash_normalization': 'utf-8-lf', 'drivers': []})
        records = {r['driver_id']: r for r in report['drivers']}
        for record in records.values():
            record.setdefault('validated_at', report['validated_at'])
        package = packages[driver['package_id']]
        entry = builds[package['id']]
        if (driver['revision'] != package['revision']
                or entry['key'] != cache_identity(package, recipe_identity())
                or not safe_path(driver['path'])):
            raise ValueError(identity+': stale package image or invalid driver path.')
        source = (ROOT/driver['path']).read_text(encoding='utf-8')
        request = {'cache_key': entry['key'], 'request': {
            'url': 'https://github.com/'+package['repository'], 'revision': package['revision'],
            'compiler': 'gfortran', 'workflow': 'consumer', 'action': 'run', 'source': source}}
        print(identity+': compile driver and run; reuse package library', flush=True)
        sandbox = modal.Sandbox.create('python', '/opt/fpm/xfpm_worker.py', app=app,
            image=modal.Image.from_name(entry['image']), runtime='gvisor', workdir='/work',
            timeout=250, cpu=(0.5, 1), memory=(512, 1024), block_network=True,
            secrets=[], volumes={}, include_oidc_identity_token=False,
            env={'OMP_NUM_THREADS': '1', 'HOME': '/work'})
        try:
            sandbox.stdin.write((json.dumps(request)+'\n').encode('utf-8'))
            sandbox.stdin.write_eof()
            sandbox.stdin.drain()
            sandbox.wait()
            result = json.loads(sandbox.stdout.read())
            (args.results_dir/(identity+'.json')).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
            if result.get('cache', {}).get('key') != entry['key']:
                raise ValueError(identity+': response does not identify the requested package cache.')
            records[identity] = verification_record(driver, result)
        finally:
            sandbox.terminate()
        report.update(validated_at=datetime.now(timezone.utc).isoformat(), drivers=list(records.values()))
        report_path.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        print(identity+': PASS; library reused', flush=True)


if __name__ == '__main__':
    main()
