"""Build and verify immutable GNU 16 FPM consumer images; does not deploy the API."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
import tempfile
import time

from fpm_cache import catalog, cache_identity

ROOT = Path(__file__).resolve().parent
DEFAULT_REPORT = ROOT / '.fpm-audit-cache/precompiled.json'


def verify_cached(app, image, package, key):
    """Test a different main in a fresh, ordinary restricted execution sandbox."""
    import modal
    source = (ROOT / 'fpm_catalog/demos' / (package['id'] + '.f90')).read_text(encoding='utf-8')
    demo_sha256 = hashlib.sha256(source.encode()).hexdigest()
    marker = 'PASS ' + package['id']
    # Actual changed Fortran, not just a comment or a replay of the prebuilt executable.
    source = source.replace(marker, marker + ' CHANGED MAIN')
    message = {'cache_key': key, 'request': {'url': 'https://github.com/' + package['repository'],
               'revision': package['revision'], 'compiler': 'gfortran', 'workflow': 'consumer',
               'action': 'run', 'source': source}}
    sandbox = modal.Sandbox.create('python', '/opt/fpm/xfpm_worker.py', app=app, image=image,
        runtime='gvisor', workdir='/work', timeout=250, cpu=(0.5, 1), memory=(512, 1024),
        block_network=True, secrets=[], volumes={}, include_oidc_identity_token=False,
        env={'OMP_NUM_THREADS': '1', 'HOME': '/work'})
    started = time.monotonic()
    try:
        sandbox.stdin.write((json.dumps(message) + '\n').encode())
        sandbox.stdin.write_eof()
        sandbox.stdin.drain()
        sandbox.wait()
        result = json.loads(sandbox.stdout.read())
        # The marker in build diagnostics is not evidence that the program ran.
        output = '\n'.join(s.get('stdout', '') for s in result.get('stages', []) if s['name'] == 'Run')
        if not result.get('ok') or marker + ' CHANGED MAIN' not in output or not result.get('cache', {}).get('library_reused'):
            summary = {k: v for k, v in result.items() if k != 'plots'}
            raise ValueError('Cached consumer verification failed: ' + json.dumps(summary)[-12000:])
        compiled = re.findall(r'\]\s+(.+?)\s+done\.', result['stages'][0].get('stdout', ''))
        if any(name not in {'main.f90', 'playground-main'} for name in compiled):
            raise ValueError('FPM rebuilt library targets: ' + ', '.join(compiled))
        if package['id'] in {'pyplot-fortran', 'forimage', 'cairo-fortran', 'fortran_stb_image'} and not result.get('plots'):
            raise ValueError('Plotting verification returned no PNG.')
        preview_check = {}
        if package['id'] == 'forimage':
            import base64
            if len(result['plots']) != 2:
                raise ValueError('ForImage must return both original and negative image previews.')
            directory = ROOT / '.fpm-audit-cache/forimage-previews'
            directory.mkdir(exist_ok=True, parents=True)
            for index, plot in enumerate(result['plots'], 1):
                (directory / f'{index}.png').write_bytes(base64.b64decode(plot['data'], validate=True))
            preview_check = {'preview_count': 2, 'preview_names': [p['name'] for p in result['plots']]}
        if package['id'] in {'cairo-fortran', 'fortran_stb_image'}:
            import base64
            if len(result['plots']) != 1:
                raise ValueError('Image example must return exactly one PNG preview.')
            directory = ROOT / ('.fpm-audit-cache/' + package['id'] + '-previews')
            directory.mkdir(exist_ok=True, parents=True)
            (directory / '1.png').write_bytes(base64.b64decode(result['plots'][0]['data'], validate=True))
            preview_check = {'preview_count': 1, 'preview_names': [result['plots'][0]['name']]}
        return {'seconds': round(time.monotonic() - started, 3),
                'build_seconds': result['stages'][0]['seconds'], 'library_reused': True,
                'demo_sha256': demo_sha256,
                'compiled_targets': compiled, **preview_check}
    finally:
        sandbox.terminate()


def build_package(app, base_image, package, recipe):
    import modal
    from fpm_sources import Preparer
    from xfpm_modal import bundle_sources
    from fpm_catalog_build import CatalogPreparer, validate_build, build_image
    options = validate_build(package)
    base_image = build_image(app, base_image, options)
    key = cache_identity(package, recipe)
    name = 'fortran-fpm-lib-' + key
    source = (ROOT / 'fpm_catalog/demos' / (package['id'] + '.f90')).read_text(encoding='utf-8')
    with tempfile.TemporaryDirectory() as temporary:
        pins = [{'repository': package['repository'], 'revision': package['revision'], 'sha256': package['archive_sha256']},
                *package.get('dependencies', [])]
        preparer = CatalogPreparer(temporary, pins=pins, options=options) if options else Preparer(temporary, pins=pins)
        root, records = preparer.prepare({'url': 'https://github.com/' + package['repository'],
                                                    'revision': package['revision'], 'source': source})
        if records[0]['sha256'] != package['archive_sha256']:
            raise ValueError('Pinned package archive checksum mismatch.')
        if package.get('catalog_patches'):
            from fpm_catalog_patches import apply_patches
            apply_patches(package, Path(temporary) / root)
        message = {**package, 'key': key, 'recipe': recipe, 'source': source, 'root': root,
                   'records': records, 'bundle': bundle_sources(temporary)}
    sandbox = modal.Sandbox.create('python', '/opt/fpm/xfpm_prebuild.py', app=app, image=base_image,
        runtime='gvisor', workdir='/work', timeout=4000, cpu=2, memory=4096,
        block_network=True, secrets=[], volumes={}, include_oidc_identity_token=False,
        env={'OMP_NUM_THREADS': '2', 'HOME': '/work'})
    try:
        sandbox.stdin.write((json.dumps(message) + '\n').encode())
        sandbox.stdin.write_eof()
        sandbox.stdin.drain()
        # Builder emits one JSON line and stays alive until the filesystem is snapshotted.
        output = ''
        for chunk in sandbox.stdout:
            output += chunk
            if '\n' in output:
                break
            if len(output) > 1000000:
                raise ValueError('Prebuild metadata exceeded its limit.')
        metadata = json.loads(output.split('\n', 1)[0])
        if not metadata.get('ok'):
            raise ValueError(metadata.get('error', 'Prebuild failed.'))
        # Failed verification must not retain an unpublished snapshot forever.
        snapshot = sandbox.snapshot_filesystem(timeout=55, ttl=86400)
        verification = verify_cached(app, snapshot, package, key)
        # The original builder is idle; retain its identical filesystem only
        # after the disposable verification clone passes.
        snapshot = sandbox.snapshot_filesystem(timeout=55, ttl=None)
        snapshot.publish(name)
        return {**metadata, 'artifact_image': name, 'verification': verification}
    finally:
        sandbox.terminate()


def refresh_worker(app, image):
    """Replace worker code/catalog in one layer; retain the compiled /work tree."""
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        for name in ('fpm_cache.py', 'fpm_build.py', 'fpm_sources.py', 'fpm_compilers.py',
                     'xfpm_worker.py', 'fpm_targets.py', 'fortran_plot.py', 'fortran_image.py'):
            shutil.copyfile(ROOT / name, directory / name)
        shutil.copytree(ROOT / 'vendor/pyplot-fortran', directory / 'vendor/pyplot-fortran')
        return image.add_local_dir(directory, '/opt/fpm', copy=True).env({'FPM_COMPILER': 'gfortran'}).build(app)


def find_artifact(app, package, recipe):
    """Recover a published library even after a fresh checkout loses its report."""
    import modal
    key = cache_identity(package, recipe)
    name = 'fortran-fpm-lib-' + key
    image = modal.Image.from_name(name)
    try:
        # Named Images resolve through build(); Image.hydrate() is unsupported
        # by Modal even though other object types expose that operation.
        image = image.build(app)
    except modal.exception.NotFoundError:
        return None
    code = ("import json,os; os.setgroups([]); os.setgid(65534); os.setuid(65534); "
            "d=json.loads(open('/work/precompiled.json').read(2000000)); "
            "d.pop('inventory',None); print(json.dumps(d))")
    sandbox = modal.Sandbox.create('python', '-c', code, app=app, image=image, runtime='gvisor',
        timeout=30, cpu=0.125, memory=128, block_network=True, secrets=[], volumes={},
        include_oidc_identity_token=False)
    try:
        sandbox.wait()
        text = sandbox.stdout.read()
        if len(text) > 1000000:
            raise ValueError('Stored library metadata exceeded its limit.')
        metadata = json.loads(text)
        if (metadata.get('key') != key or metadata.get('recipe') != recipe
                or metadata.get('revision') != package['revision']
                or metadata.get('repository') != package['repository']
                or metadata['records'][0]['sha256'] != package['archive_sha256']):
            raise ValueError('Published library metadata does not match its pinned identity.')
        print('Recovered published library:', package['id'], flush=True)
        return {**metadata, 'artifact_image': name}
    finally:
        sandbox.terminate()


def build_catalog(app, image, base_name, names=None, report_path=DEFAULT_REPORT, *, reverify=False, rebuild=False):
    import modal
    from fpm_cache import recipe_identity, worker_identity
    recipe = recipe_identity()
    worker = worker_identity()
    packages = [p for p in catalog() if names is None or p['id'] in names]
    previous = json.loads(report_path.read_text()) if report_path.exists() else {}
    retained = {p['id']: previous.get('packages', {}).get(p['id']) for p in catalog()}
    retained = {name: entry for name, entry in retained.items() if entry
                and entry.get('key') == cache_identity(next(p for p in catalog() if p['id'] == name), recipe)}
    failures = {}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    for package in packages:
        name = package['id']
        try:
            if package.get('catalog_build'):
                from fpm_catalog_build import validate_build
                validate_build(package)
            if package.get('catalog_patches'):
                from fpm_catalog_patches import validate_patches
                validate_patches(package)
            old = previous.get('packages', {}).get(name)
            runner_name = 'fpm-run-' + worker + '-' + cache_identity(package, recipe)
            if (not rebuild and not reverify and old and old.get('key') == cache_identity(package, recipe)
                    and old.get('artifact_image') and old.get('image') == runner_name
                    and old.get('verification', {}).get('library_reused') is True
                    and old['verification'].get('demo_sha256') == hashlib.sha256(
                        (ROOT / 'fpm_catalog/demos' / (name + '.f90')).read_text(encoding='utf-8').encode()).hexdigest()):
                print(f'{name}: reusing verified published image; no compilation or verification job', flush=True)
                continue
            if not rebuild and old and old.get('key') == cache_identity(package, recipe) and old.get('artifact_image'):
                print(f'{name}: reusing compiled library', flush=True)
                entry = old
            else:
                entry = None if rebuild else find_artifact(app, package, recipe)
                if entry is None:
                    print(f'{name}: compiling library ({"forced rebuild" if rebuild else "no matching published artifact"})', flush=True)
                    entry = build_package(app, image, package, recipe)
            runner_name = 'fpm-run-' + worker + '-' + entry['key']
            if entry.get('image') == runner_name:
                ready = modal.Image.from_name(runner_name)
            else:
                print(f'{name}: refreshing worker layer; keeping compiled library', flush=True)
                ready = refresh_worker(app, modal.Image.from_name(entry['artifact_image']))
            print(f'{name}: verifying changed main; keeping compiled library', flush=True)
            verification = verify_cached(app, ready, package, entry['key'])
            ready.publish(runner_name)
            entry = {**entry, 'image': runner_name, 'verification': verification}
            retained[name] = entry
            print(f"{name}: verified; {entry['artifact_bytes']/1048576:.1f} MiB artifacts; "
                  f"changed main build {entry['verification']['build_seconds']:.3f} seconds", flush=True)
        except Exception as error:
            retained.pop(name, None)
            failures[name] = str(error)
            print(f'{name}: FAILED: {error}', flush=True)
        report_path.write_text(json.dumps({'base_image': base_name, 'recipe': recipe, 'packages': retained, 'failures': failures}, indent=2) + '\n')
    if failures:
        raise RuntimeError('Catalog verification failed for: ' + ', '.join(failures) + '. See ' + str(report_path))
    report_path.write_text(json.dumps({'base_image': base_name, 'recipe': recipe, 'packages': retained,
                                      'failures': failures}, indent=2) + '\n')
    # A selected batch extends the deployed catalog rather than removing valid
    # images for packages outside that batch. Drop only stale/unverified entries.
    return {name: entry for name, entry in retained.items()
            if entry.get('image') and entry.get('verification', {}).get('library_reused') is True}


def write_validation_report(entries, path):
    """Export reproducible public evidence without operator routing details."""
    from datetime import datetime, timezone
    from fpm_cache import recipe_identity, worker_identity
    packages = catalog()
    if set(entries) != {p['id'] for p in packages}:
        raise ValueError('A validation report requires verifying the complete catalog; omit --packages.')
    for package in packages:
        source = (ROOT / 'fpm_catalog/demos' / (package['id'] + '.f90')).read_text(encoding='utf-8')
        if entries[package['id']]['verification'].get('demo_sha256') != hashlib.sha256(source.encode()).hexdigest():
            raise ValueError('Example changed since verification: ' + package['id'])
    recipe = json.loads((ROOT / 'fpm_build_recipe.json').read_text(encoding='utf-8'))
    report = {'verified_at': datetime.now(timezone.utc).isoformat(), 'compiler': 'GNU Fortran 16.2.0',
        'fpm': '0.12.0', 'compiler_image': recipe['compiler_image'],
        'recipe': recipe_identity(), 'worker': worker_identity(),
        'sandbox': {'runtime': 'gvisor', 'cpu': [0.5, 1], 'memory_mib': [512, 1024],
                    'network': False, 'secrets': False, 'build_limit_seconds': 180,
                    'run_limit_seconds': 30, 'new_file_limit_mib': 16},
        'check': 'Each edited main ran successfully; library artifacts were unchanged and FPM rebuilt only the main and executable. Plotting returned a PNG.',
        'artifact_size_note': 'Logical object/module/archive bytes including FPM flag variants; excludes compiler images, native system libraries, sources, main executables. Not compressed storage or billing.',
        'total_artifact_bytes': sum(e['artifact_bytes'] for e in entries.values()),
        'packages': [{**{k: entries[p['id']][k] for k in ('id', 'repository', 'revision', 'records',
                     'prebuild_seconds', 'artifact_bytes', 'verification')},
                     **({key: p[key] for key in ('catalog_build', 'catalog_patches') if p.get(key)})} for p in packages]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packages', nargs='+', choices=[p['id'] for p in catalog()])
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--validation-report', type=Path, help='Write public measurements after verifying the complete catalog.')
    parser.add_argument('--reverify', action='store_true', help='Re-run changed-main verification, retaining compiled libraries.')
    parser.add_argument('--rebuild', action='store_true', help='Force rebuilding selected libraries; default: reuse matching published builds.')
    args = parser.parse_args()
    if args.validation_report and args.packages:
        parser.error('--validation-report requires checking the complete catalog; omit --packages.')
    import modal
    from xfpm_modal import APP_NAME, runtime_image, IMAGE_NAME
    app = modal.App.lookup(APP_NAME, create_if_missing=True)
    with modal.enable_output():
        image = runtime_image.build(app)
        entries = build_catalog(app, image, IMAGE_NAME, args.packages, args.report,
                                reverify=args.reverify or bool(args.validation_report), rebuild=args.rebuild)
        if args.validation_report:
            write_validation_report(entries, args.validation_report)


if __name__ == '__main__':
    main()
