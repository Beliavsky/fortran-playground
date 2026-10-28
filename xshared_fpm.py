"""Operator orchestration for immutable, compatible dependency images."""
import copy
import json
from pathlib import Path
import tempfile

from fpm_cache import cache_identity, catalog
from fpm_shared import (SHARED_FILES, build_context, dependency_contract, digest,
                        implementation_digest, install_shared_image)

ROOT = Path(__file__).resolve().parent
VOLUME_NAME = 'fortran-fpm-shared-libraries'


def legacy_candidates(package):
    """Recognize old artifacts without changing their keys or build records."""
    from fpm_catalog_build import (LEGACY_ADAPTER_SHA256, SOURCE_ADAPTER_SHA256,
                                   NAME_ADAPTER_SHA256, adapter_digest)
    p = copy.deepcopy(package)
    options = p.get('catalog_build', {})
    options.pop('shared_dependencies', None)
    if not (set(options)-{'adapter_sha256'}):
        bare = copy.deepcopy(p)
        bare.pop('catalog_build', None)
        yield bare
    if options:
        for adapter in (adapter_digest(), NAME_ADAPTER_SHA256, SOURCE_ADAPTER_SHA256, LEGACY_ADAPTER_SHA256):
            candidate = copy.deepcopy(p)
            candidate['catalog_build']['adapter_sha256'] = adapter
            yield candidate
    else:
        yield p


def prepared(package):
    """Caller owns the temporary directory; no compiled cache paths enter sources."""
    from fpm_sources import Preparer
    from fpm_catalog_build import CatalogPreparer, validate_build
    from fpm_catalog_patches import apply_patches
    directory = tempfile.TemporaryDirectory()
    pins = [{'repository': package['repository'], 'revision': package['revision'], 'sha256': package['archive_sha256']},
            *package.get('dependencies', [])]
    options = validate_build(package)
    preparer = CatalogPreparer(directory.name, pins=pins, options=options) if options else Preparer(directory.name, pins=pins)
    try:
        root, records = preparer.prepare({'url': 'https://github.com/'+package['repository'],
            'revision': package['revision'], 'source': 'program main\nend program\n'})
        if package.get('catalog_patches'): apply_patches(package, Path(directory.name)/root)
        roots = {repo: path for (repo, _), path in preparer.repositories.items()}
        return directory, records, roots
    except BaseException:
        directory.cleanup()
        raise


def shared_worker_image(app, image):
    """Keep the legacy worker verbatim; hook only opted-in immutable images."""
    return (image.pip_install('tomli-w==1.2.0')
        .add_local_file(ROOT/'fpm_shared.py', '/opt/fpm/fpm_shared.py', copy=True)
        .add_local_file(ROOT/'xfpm_shared_prebuild.py', '/opt/fpm/xfpm_shared_prebuild.py', copy=True)
        .add_local_file(ROOT/'xfpm_worker.py', '/opt/fpm/xfpm_legacy_worker.py', copy=True)
        .add_local_file(ROOT/'xfpm_shared_worker.py', '/opt/fpm/xfpm_worker.py', copy=True).build(app))


def ensure_dependency(app, base_image, contract, entries, package, recipe):
    import modal
    from xprecompile_fpm import build_package, find_artifact
    key = digest(contract)[:24]
    name = 'fortran-fpm-dependency-'+key
    # Named images are immutable to consumers. Recover without mounting a Volume.
    try:
        image = modal.Image.from_name(name).build(app)
    except modal.exception.NotFoundError:
        image = None
    if image is not None:
        sandbox = modal.Sandbox.create('python', '-c',
            "print(open('/opt/fpm/shared/"+key+"/manifest.json').read())", app=app, image=image,
            timeout=30, block_network=True, secrets=[], volumes={})
        try:
            sandbox.wait()
            manifest = json.loads(sandbox.stdout.read())
            if manifest['contract'] != contract or manifest['key'] != key:
                raise ValueError('Published shared dependency identity mismatch.')
        finally:
            sandbox.terminate()
        print(contract['source']['repository']+': reusing shared dependency image; no compilation', flush=True)
        return image, manifest
    pin = contract['source']
    by_id = {p['id']: p for p in catalog()}
    donor = None
    for identifier, entry in entries.items():
        candidate = by_id.get(entry.get('id', identifier))
        if (not candidate or entry.get('recipe') != recipe or not entry.get('artifact_image')
                or entry.get('verification', {}).get('library_reused') is not True
                or pin not in entry.get('records', []) or build_context(candidate) != contract['context']):
            continue
        if entry['key'] in {cache_identity(p, recipe) for p in legacy_candidates(candidate)}:
            donor = entry
            break
    if donor is None:
        # Cold fork/new variant: normal bounded preparation and a single full
        # build establish a trusted donor. Later parents skip this path entirely.
        candidates = list(legacy_candidates(package))
        for candidate in candidates:
            donor = find_artifact(app, candidate, recipe)
            if donor is not None: break
        if donor is None:
            print(pin['repository']+': building first compatible dependency variant', flush=True)
            donor = build_package(app, base_image, candidates[0], recipe)
    print(pin['repository']+': exporting existing compiled dependency; no compiler invoked', flush=True)
    volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True, version=2)
    exporter = (modal.Image.from_name(donor['artifact_image'])
        .add_local_file(ROOT/'fpm_shared.py', '/opt/fpm/fpm_shared.py', copy=True).build(app))
    sandbox = modal.Sandbox.create('python', '/opt/fpm/fpm_shared.py', app=app, image=exporter,
        timeout=180, cpu=1, memory=1024, block_network=True, secrets=[], volumes={'/dependency-cache': volume})
    try:
        from xprecompile_fpm import write_build_message
        write_build_message(sandbox.stdin, contract)
        sandbox.wait()
        text = sandbox.stdout.read()
        if sandbox.returncode:
            raise ValueError('Dependency export failed: '+sandbox.stderr.read()[-5000:])
        result = json.loads(text)
    finally:
        sandbox.terminate()
    manifest = result['manifest']
    if manifest['contract'] != contract or manifest['compiled_objects'] != 0:
        raise ValueError('Dependency export identity mismatch.')
    # Export files are verified once while baking the image. The Volume is an
    # operator transfer/cache only; neither prebuilds nor visitor workers mount it.
    image = (base_image.add_local_file(ROOT/'fpm_shared.py', '/root/fpm_shared.py', copy=True)
        .run_function(install_shared_image, volumes={'/dependency-cache': volume}, include_source=False,
            kwargs={'key': key, 'manifest_sha256': result['manifest_sha256']}).build(app))
    image.publish(name)
    return image, manifest


def build_shared_package(app, base_image, package, recipe):
    import modal
    from fpm_catalog_build import build_image, validate_build
    from xprecompile_fpm import build_package, DEFAULT_REPORT
    from fpm_shared import file_hash
    options = validate_build(package)
    setting = options['shared_dependencies']
    implementation = implementation_digest(ROOT)
    if setting['adapter_sha256'] != implementation:
        raise ValueError('Refresh the shared dependency implementation checksum.')
    report = json.loads(DEFAULT_REPORT.read_text()) if DEFAULT_REPORT.exists() else {}
    entries = {**report.get('dependency_donors', {}), **report.get('packages', {})}
    base_image = build_image(app, base_image, options)
    directory, records, roots = prepared(package)
    plans = []
    try:
        for repository in setting['repositories']:
            pin = next((p for p in records if p['repository'].lower() == repository.lower()), None)
            if pin is None:
                raise ValueError('Shared dependency is not in the pinned graph: '+repository)
            contract = dependency_contract(pin, roots[repository.lower()], roots, build_context(package), recipe, implementation)
            image, manifest = ensure_dependency(app, base_image, contract, entries, package, recipe)
            # The stable manifest hash participates in the image-layer cache.
            import hashlib
            manifest_sha = hashlib.sha256((json.dumps(manifest, indent=2)+'\n').encode()).hexdigest()
            plans.append({'repository': pin['repository'], 'key': manifest['key'], 'modules': manifest['modules'],
                          'library': manifest['library'], 'artifact_bytes': manifest['artifact_bytes'],
                          'manifest_sha256': manifest_sha, 'image': image})
    finally:
        directory.cleanup()
    # For one dependency retain its shared parent layer directly. Multiple leaves
    # are copied from the operator Volume into successive immutable image layers.
    if len(plans) == 1:
        image = plans[0]['image']
    else:
        volume = modal.Volume.from_name(VOLUME_NAME, version=2)
        image = base_image.add_local_file(ROOT/'fpm_shared.py', '/root/fpm_shared.py', copy=True)
        for plan in plans:
            image = image.run_function(install_shared_image, volumes={'/dependency-cache': volume}, include_source=False,
                kwargs={'key': plan['key'], 'manifest_sha256': plan['manifest_sha256']})
        image = image.build(app)
    public_plans = [{k: v for k, v in p.items() if k != 'image'} for p in plans]
    # Modal may re-evaluate parent image definitions in later build steps, so
    # local image inputs must survive beyond this function's temporary scopes.
    path = ROOT/'.fpm-audit-cache/dependency-plans'/(digest(public_plans)+'.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(public_plans)+'\n', encoding='utf-8')
    image = image.add_local_file(path, '/opt/fpm/shared-consumer.json', copy=True).build(app)
    image = shared_worker_image(app, image)
    return build_package(app, image, package, recipe, _shared_plan=public_plans)


def main():
    import argparse
    from fpm_catalog_build import adapter_digest, validate_build
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enable', nargs='+', required=True, choices=[p['id'] for p in catalog()],
                        help='Opt selected packages into shared dependencies; does not build or deploy.')
    parser.add_argument('--dependencies', nargs='+', default=['fortran-lang/stdlib'])
    args = parser.parse_args()
    path = ROOT/'fpm_catalog.json'
    document = json.loads(path.read_text(encoding='utf-8'))
    packages = document['packages']
    for p in packages:
        if p['id'] not in args.enable: continue
        available = {r['repository'].lower() for r in [p, *p.get('dependencies', [])]}
        if any(r.lower() not in available for r in args.dependencies):
            parser.error(p['id']+': dependency is absent from the pinned source graph')
        options = p.setdefault('catalog_build', {})
        options['adapter_sha256'] = adapter_digest()
        options['shared_dependencies'] = {'adapter_sha256': implementation_digest(ROOT),
                                          'repositories': [r.lower() for r in args.dependencies]}
        validate_build(p)
    path.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')
    print('Enabled shared dependency builds for: '+', '.join(args.enable))


if __name__ == '__main__':
    main()
