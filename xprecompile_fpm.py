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


def generated_source_tag(options, spec):
    """Bind generated sources to the existing leaf manifest/cache contract."""
    import copy
    import tomllib
    from fpm_shared import digest
    manifest = tomllib.loads(spec['manifest'])
    cpp = manifest.setdefault('preprocess', {}).setdefault('cpp', {})
    cpp['macros'] = [m for m in cpp.get('macros', []) if not m.startswith('PLAYGROUND_CATALOG_')]
    return 'PLAYGROUND_CATALOG_' + digest({'adapter': options['adapter_sha256'],
        'source_package': {**copy.deepcopy(spec), 'manifest': manifest}}).upper()


def shareable_generated_source(options, spec):
    import tomllib
    try:
        macros = tomllib.loads(spec['manifest']).get('preprocess', {}).get('cpp', {}).get('macros', [])
        return bool(spec.get('generated')) and generated_source_tag(options, spec) in macros
    except (KeyError, TypeError, ValueError):
        return False


def write_build_message(writer, message):
    """Drain bounded chunks: source bundles can exceed Modal's stdin buffer."""
    data = (json.dumps(message) + '\n').encode('utf-8')
    for start in range(0, len(data), 64 * 1024):
        writer.write(data[start:start + 64 * 1024])
        writer.drain()
    writer.write_eof()
    writer.drain()


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
        if package['id'] in {'pyplot-fortran', 'forimage', 'cairo-fortran', 'fortran_stb_image', 'easy-plplot', 'ogpf'} and not result.get('plots'):
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


def build_package(app, base_image, package, recipe, *, _shared_plan=None):
    if package.get('catalog_build', {}).get('shared_dependencies') and _shared_plan is None:
        options = package['catalog_build']
        shared = {name.lower() for name in options['shared_dependencies']['repositories']}
        if (any(name.lower() in shared and not shareable_generated_source(options, spec)
                for name, spec in options.get('source_packages', {}).items())
                or (package.get('catalog_patches') and package['repository'].lower() in shared)):
            raise ValueError('Shared dependencies currently require unpatched library sources.')
        from fpm_shared_graph import graph_digest
        if options['shared_dependencies']['adapter_sha256'] == graph_digest(ROOT):
            from xshared_graph import build_graph_package
            return build_graph_package(app, base_image, package, recipe)
        from xshared_fpm import build_shared_package
        return build_shared_package(app, base_image, package, recipe)
    import modal
    from fpm_sources import Preparer
    from xfpm_modal import bundle_sources
    from fpm_catalog_build import CatalogPreparer, validate_build, build_image
    options = validate_build(package)
    # Shared coordinators already configure native libraries and flags before
    # selecting exports. Repeating apt setup would add redundant image layers.
    if _shared_plan is None:
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
        if _shared_plan:
            from fpm_shared_graph import graph_digest, rewrite_graph_sources
            from fpm_shared import rewrite_shared_sources
            rewrite = (rewrite_graph_sources if options['shared_dependencies']['adapter_sha256'] == graph_digest(ROOT)
                       else rewrite_shared_sources)
            rewrite({repo: path for (repo, _), path in preparer.repositories.items()}, _shared_plan)
        message = {**package, 'key': key, 'recipe': recipe, 'source': source, 'root': root,
                   'records': records, 'bundle': bundle_sources(temporary)}
    prebuild = '/opt/fpm/xfpm_shared_prebuild.py' if _shared_plan else '/opt/fpm/xfpm_prebuild.py'
    if options.get('source_limit'):
        if _shared_plan:
            raise ValueError('Large-source prebuilds currently require the ordinary catalog builder.')
        base_image = (base_image
            .add_local_file(ROOT/'fpm_catalog_limits.py', '/opt/fpm/fpm_catalog_limits.py', copy=True)
            .add_local_file(ROOT/'xfpm_catalog_prebuild.py', '/opt/fpm/xfpm_catalog_prebuild.py', copy=True).build(app))
        prebuild = '/opt/fpm/xfpm_catalog_prebuild.py'
    sandbox = modal.Sandbox.create('python', prebuild, app=app, image=base_image,
        runtime='gvisor', workdir='/work', timeout=4000, cpu=2, memory=4096,
        block_network=True, secrets=[], volumes={}, include_oidc_identity_token=False,
        env={'OMP_NUM_THREADS': '2', 'HOME': '/work'})
    try:
        write_build_message(sandbox.stdin, message)
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
    from fpm_cache import worker_identity
    # Later child image layers may resolve these inputs again. Keep a stable,
    # content-versioned directory rather than an already deleted temporary one.
    directory = ROOT / '.fpm-audit-cache/worker-layers' / worker_identity()
    directory.mkdir(parents=True, exist_ok=True)
    for name in ('fpm_cache.py', 'fpm_build.py', 'fpm_sources.py', 'fpm_compilers.py',
                 'xfpm_worker.py', 'fpm_targets.py', 'fortran_plot.py', 'fortran_image.py'):
        shutil.copyfile(ROOT / name, directory / name)
    shutil.copytree(ROOT / 'vendor/pyplot-fortran', directory / 'vendor/pyplot-fortran', dirs_exist_ok=True)
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
    donors = dict(previous.get('dependency_donors', {}))
    # Keep verified old donors available while selected parents are migrated.
    # They may still be serving the public API until the operator redeploys.
    for name, entry in previous.get('packages', {}).items():
        if entry.get('artifact_image') and entry.get('verification', {}).get('library_reused') is True:
            donors.setdefault(entry['key'], {**entry, 'id': entry.get('id', name)})
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
                if package.get('catalog_build', {}).get('shared_dependencies'):
                    from xshared_fpm import shared_worker_image
                    ready = shared_worker_image(app, ready)
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
        report_path.write_text(json.dumps({'base_image': base_name, 'recipe': recipe, 'packages': retained,
                                          'dependency_donors': donors, 'failures': failures}, indent=2) + '\n')
    if failures:
        raise RuntimeError('Catalog verification failed for: ' + ', '.join(failures) + '. See ' + str(report_path))
    report_path.write_text(json.dumps({'base_image': base_name, 'recipe': recipe, 'packages': retained,
                                      'dependency_donors': donors, 'failures': failures}, indent=2) + '\n')
    # A selected batch extends the deployed catalog rather than removing valid
    # images for packages outside that batch. Drop only stale/unverified entries.
    return {name: entry for name, entry in retained.items()
            if entry.get('image') and entry.get('verification', {}).get('library_reused') is True}


def artifact_totals(entries):
    """Count each immutable shared export once, regardless of its consumers."""
    shared = {}
    for name, entry in entries.items():
        for dependency in entry.get('shared_dependencies', []):
            key = dependency['key']
            if key in shared and shared[key]['dependency'] != dependency:
                raise ValueError('Conflicting shared dependency measurements: ' + key)
            shared.setdefault(key, {'dependency': dependency, 'users': []})['users'].append(name)
    owned = sum(e['artifact_bytes'] for e in entries.values())
    shared_bytes = sum(e['dependency']['artifact_bytes'] for e in shared.values())
    return {'owned_artifact_bytes': owned, 'shared_artifact_bytes': shared_bytes,
            'total_artifact_bytes': owned + shared_bytes,
            'shared_dependencies': [{**entry['dependency'], 'users': sorted(entry['users'])}
                                    for _, entry in sorted(shared.items())]}


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
        'artifact_size_note': 'Logical package-owned object/module/archive bytes plus each immutable shared dependency export once. Legacy package measurements include their dependency objects and FPM flag variants. Excludes compiler images, native system libraries, sources and main executables; not compressed storage or billing. Retired rollout images and the operator export Volume are not counted.',
        **artifact_totals(entries),
        'packages': [{**{k: entries[p['id']][k] for k in ('id', 'repository', 'revision', 'records',
                     'prebuild_seconds', 'artifact_bytes', 'verification')},
                     **({key: p[key] for key in ('catalog_build', 'catalog_patches') if p.get(key)}),
                     **({'shared_dependencies': entries[p['id']]['shared_dependencies']}
                        if entries[p['id']].get('shared_dependencies') else {})} for p in packages]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


def enable_shared_catalog(names=None):
    """Explicitly opt a batch into graph sharing; preserve unsupported recipes."""
    from xshared_graph import enable_packages
    path = ROOT/'fpm_catalog.json'
    document = json.loads(path.read_text(encoding='utf-8'))
    eligible = set()
    for package in document['packages']:
        if names is not None and package['id'] not in names:
            continue
        if package.get('catalog_patches') or package.get('catalog_build', {}).get('source_packages'):
            print(package['id']+': retaining existing cache recipe (patched or repackaged sources)', flush=True)
        else:
            eligible.add(package['id'])
    updated = enable_packages(document, eligible, ROOT)
    if updated != document:
        path.write_text(json.dumps(updated, indent=2)+'\n', encoding='utf-8')
    return eligible


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packages', nargs='+', choices=[p['id'] for p in catalog()])
    parser.add_argument('--report', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--validation-report', type=Path, help='Write public measurements after verifying the complete catalog.')
    parser.add_argument('--reverify', action='store_true', help='Re-run changed-main verification, retaining compiled libraries.')
    parser.add_argument('--rebuild', action='store_true', help='Force rebuilding selected libraries; default: reuse matching published builds.')
    parser.add_argument('--share-dependencies', action='store_true',
                        help='Enable complete dependency graphs for eligible selected packages (all if --packages is omitted); updates fpm_catalog.json.')
    args = parser.parse_args()
    if args.validation_report and args.packages:
        parser.error('--validation-report requires checking the complete catalog; omit --packages.')
    if args.share_dependencies:
        enable_shared_catalog(args.packages)
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
