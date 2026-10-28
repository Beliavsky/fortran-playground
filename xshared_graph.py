"""Operator builds of complete shared FPM dependency graphs."""
import copy
import hashlib
import json
from pathlib import Path

from fpm_cache import cache_identity, catalog
from fpm_shared import build_context, digest, implementation_digest
from fpm_shared_graph import dependency_graph, graph_digest, install_graph_image
from xshared_fpm import (VOLUME_NAME, legacy_candidates, prepared, shared_worker_image)

ROOT = Path(__file__).resolve().parent


def helper_image(image):
    return (image.add_local_file(ROOT/'fpm_shared.py', '/root/fpm_shared.py', copy=True)
            .add_local_file(ROOT/'fpm_shared_graph.py', '/root/fpm_shared_graph.py', copy=True))


def ensure_graph_dependency(app, base_image, contract, entries, package, recipe):
    import modal
    from xprecompile_fpm import build_package, find_artifact, write_build_message
    key = digest(contract)[:24]; name = 'fortran-fpm-dependency-'+key
    try:
        image = modal.Image.from_name(name).build(app)
    except modal.exception.NotFoundError:
        image = None
    if image is not None:
        sandbox = modal.Sandbox.create('python', '-c',
            "print(open('/opt/fpm/shared/"+key+"/manifest.json').read())", app=app, image=image,
            timeout=30, block_network=True, secrets=[], volumes={})
        try:
            sandbox.wait(); manifest = json.loads(sandbox.stdout.read())
            if manifest['key'] != key or manifest['contract'] != contract:
                raise ValueError('Published shared graph identity mismatch.')
        finally:
            sandbox.terminate()
        print(contract['source']['repository']+': reusing shared archive; no compilation', flush=True)
        return manifest, image
    by_id = {p['id']: p for p in catalog()}
    donor = None
    # Prefer the parent's original image: it has precisely this resolved graph.
    candidates = sorted(entries.items(), key=lambda item: item[1].get('id', item[0]) != package['id'])
    for identifier, entry in candidates:
        candidate = by_id.get(entry.get('id', identifier))
        if (not candidate or entry.get('recipe') != recipe or not entry.get('artifact_image')
                or entry.get('verification', {}).get('library_reused') is not True
                or contract['source'] not in entry.get('records', [])
                or build_context(candidate) != contract['context']):
            continue
        if entry['key'] in {cache_identity(p, recipe) for p in legacy_candidates(candidate)}:
            donor = entry
            break
    if donor is None:
        original = list(legacy_candidates(package))
        for candidate in original:
            donor = find_artifact(app, candidate, recipe)
            if donor is not None: break
        if donor is None:
            print(package['id']+': establishing a first graph donor', flush=True)
            donor = build_package(app, base_image, original[0], recipe)
        # All remaining nodes in this build can export the same donor.
        entries[donor['key']] = {**donor, 'id': package['id']}
    print(contract['source']['repository']+': exporting existing objects; no compilation', flush=True)
    volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True, version=2)
    exporter = helper_image(modal.Image.from_name(donor['artifact_image'])).build(app)
    sandbox = modal.Sandbox.create('python', '/root/fpm_shared_graph.py', app=app, image=exporter,
        timeout=180, cpu=1, memory=1024, block_network=True, secrets=[], volumes={'/dependency-cache': volume})
    try:
        write_build_message(sandbox.stdin, {'contract': contract, 'leaf_adapter': implementation_digest(ROOT),
                                          'graph_adapter': graph_digest(ROOT)})
        sandbox.wait()
        if sandbox.returncode:
            raise ValueError('Shared graph export failed: '+sandbox.stderr.read()[-5000:])
        result = json.loads(sandbox.stdout.read()); manifest = result['manifest']
    finally:
        sandbox.terminate()
    if manifest['contract'] != contract or manifest['compiled_objects'] != 0:
        raise ValueError('Shared graph export identity mismatch.')
    image = helper_image(base_image).run_function(install_graph_image,
        volumes={'/dependency-cache': volume}, include_source=False,
        kwargs={'key': key, 'manifest_sha256': result['manifest_sha256']}).build(app)
    image.publish(name)
    return manifest, image


def build_graph_package(app, base_image, package, recipe):
    import modal
    from fpm_catalog_build import build_image, validate_build
    from xprecompile_fpm import DEFAULT_REPORT, build_package
    options = validate_build(package)
    if options['shared_dependencies']['adapter_sha256'] != graph_digest(ROOT):
        raise ValueError('Refresh the shared graph implementation checksum.')
    report = json.loads(DEFAULT_REPORT.read_text()) if DEFAULT_REPORT.exists() else {}
    entries = {**report.get('dependency_donors', {}), **report.get('packages', {})}
    base_image = build_image(app, base_image, options)
    temporary, records, roots = prepared(package)
    try:
        contracts = dependency_graph(records, roots, build_context(package), recipe,
                                     implementation_digest(ROOT), graph_digest(ROOT))
        selected = {name.lower() for name in options['shared_dependencies']['repositories']}
        if not selected <= set(contracts):
            raise ValueError('Shared graph selection is not in the pinned graph.')
        # Include the whole descendant closure of every selected library.
        closure = set()
        def include(name):
            if name in closure: return
            closure.add(name)
            for child in contracts[name].get('dependencies', []): include(child['repository'])
        for name in sorted(selected): include(name)
        plans, images = [], {}
        for name, contract in contracts.items():
            if name not in closure: continue
            manifest, image = ensure_graph_dependency(app, base_image, contract, entries, package, recipe)
            images[manifest['key']] = image
            plans.append({'repository': contract['source']['repository'], 'key': manifest['key'],
                'modules': manifest['modules'], 'library': manifest['library'],
                'artifact_bytes': manifest['artifact_bytes'], 'manifest_sha256': hashlib.sha256(
                    (json.dumps(manifest, indent=2)+'\n').encode()).hexdigest()})
    finally:
        temporary.cleanup()
    # Starting with a published shared image permits recovery after loss of the
    # operator Volume. Copy other immutable exports into layers; never compile.
    image = helper_image(base_image).build(app)
    for plan in plans:
        donor = images[plan['key']]
        # A volume is a transfer mechanism only. Rehydrate a missing export from
        # its verified published image before installing the common layer.
        volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True, version=2)
        code = ("import pathlib,shutil,subprocess; k="+repr(plan['key'])+"; "
            "s=pathlib.Path('/opt/fpm/shared')/k; d=pathlib.Path('/dependency-cache')/k; "
            "shutil.copytree(s,d) if not d.exists() else None; subprocess.run(['sync','/dependency-cache'],check=True)")
        sandbox = modal.Sandbox.create('python', '-c', code, app=app, image=donor,
            timeout=90, block_network=True, secrets=[], volumes={'/dependency-cache': volume})
        try:
            sandbox.wait()
            if sandbox.returncode: raise ValueError('Shared graph transfer failed: '+sandbox.stderr.read()[-2000:])
        finally:
            sandbox.terminate()
        image = image.run_function(install_graph_image, volumes={'/dependency-cache': volume}, include_source=False,
            kwargs={'key': plan['key'], 'manifest_sha256': plan['manifest_sha256']}).build(app)
    # Static archives must appear before the archives that satisfy their references.
    plans.reverse()
    path = ROOT/'.fpm-audit-cache/dependency-plans'/(digest(plans)+'.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plans)+'\n', encoding='utf-8')
    image = image.add_local_file(path, '/opt/fpm/shared-consumer.json', copy=True).build(app)
    image = shared_worker_image(app, image)
    return build_package(app, image, package, recipe, _shared_plan=plans)


def enable_packages(document, identifiers, root):
    from fpm_catalog_build import adapter_digest, validate_build
    result = copy.deepcopy(document)
    for package in result['packages']:
        if package['id'] not in identifiers: continue
        options = package.setdefault('catalog_build', {})
        if package.get('catalog_patches') or options.get('source_packages'):
            raise ValueError('Shared graphs currently require unpatched library sources: '+package['id'])
        repositories = [p['repository'].lower() for p in [package, *package.get('dependencies', [])]]
        if len(set(repositories)) != len(repositories):
            raise ValueError('Duplicate shared graph repositories: '+package['id'])
        options['adapter_sha256'] = adapter_digest()
        options['shared_dependencies'] = {'adapter_sha256': graph_digest(root), 'repositories': repositories}
        validate_build(package)
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--enable', nargs='+', required=True, choices=[p['id'] for p in catalog()])
    args = parser.parse_args()
    path = ROOT/'fpm_catalog.json'
    document = enable_packages(json.loads(path.read_text(encoding='utf-8')), set(args.enable), ROOT)
    path.write_text(json.dumps(document, indent=2)+'\n', encoding='utf-8')
    print('Enabled complete shared dependency graphs: '+', '.join(args.enable))


if __name__ == '__main__':
    main()
