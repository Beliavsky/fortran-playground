"""Pinned dependency graphs and immutable per-library archive exports."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tomllib

from fpm_shared import (dependency_contract, digest, file_hash, implementation_digest,
                        validate_export as validate_leaf_export)

GRAPH_FILES = ('fpm_shared_graph.py', 'xshared_graph.py')


def graph_digest(root):
    root = Path(root)
    return digest({'leaf': implementation_digest(root), 'graph': {
        name: file_hash_normalized(root/name) for name in GRAPH_FILES}})


def file_hash_normalized(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def dependency_graph(records, roots, context, recipe, leaf_adapter, graph_adapter):
    """Return dependencies before dependents; reject cycles and unresolved paths."""
    roots = {name.lower(): Path(path).resolve() for name, path in roots.items()}
    pins = {pin['repository'].lower(): pin for pin in records}
    by_path = {path: name for name, path in roots.items()}
    if set(roots) != set(pins) or len(by_path) != len(roots):
        raise ValueError('Shared graph roots do not match pinned sources.')
    manifests = {name: tomllib.loads((path/'fpm.toml').read_text(encoding='utf-8'))
                 for name, path in roots.items()}
    edges = {}
    for name, manifest in manifests.items():
        children = set()
        for spec in manifest.get('dependencies', {}).values():
            if not isinstance(spec, dict) or 'path' not in spec:
                raise ValueError('Shared graph requires resolved, pinned dependency paths: '+name)
            child = by_path.get((roots[name]/spec['path']).resolve())
            if child is None:
                raise ValueError('Shared graph dependency is outside the pinned graph: '+name)
            children.add(child)
        edges[name] = sorted(children)
    contracts, visiting = {}, set()
    def visit(name):
        if name in visiting:
            raise ValueError('Cycle in shared dependency graph: '+name)
        if name in contracts:
            return
        visiting.add(name)
        for child in edges[name]:
            visit(child)
        manifest = manifests[name]
        if not edges[name]:
            # Existing leaf exports, including stdlib, keep their exact keys.
            contract = dependency_contract(pins[name], roots[name], roots, context, recipe, leaf_adapter)
        else:
            profile = {key: manifest.get(key, {}) for key in ('preprocess', 'fortran', 'library')}
            profile['link'] = manifest.get('build', {}).get('link', [])
            profile['external-modules'] = manifest.get('build', {}).get('external-modules', [])
            preprocessing = set()
            for parent, m in manifests.items():
                for spec in m.get('dependencies', {}).values():
                    if (roots[parent]/spec['path']).resolve() == roots[name] and spec.get('preprocess'):
                        preprocessing.add(json.dumps(spec['preprocess'], sort_keys=True))
            sources = {p.relative_to(roots[name]).as_posix(): file_hash_normalized(p)
                       for p in roots[name].rglob('*') if p.is_file() and p.suffix.lower() in
                       {'.f', '.f90', '.f95', '.for', '.c', '.h', '.inc', '.fypp'}}
            contract = {'schema': 2, 'source': pins[name], 'recipe': recipe,
                'implementation': graph_adapter, 'context': context, 'profile': profile,
                'edge_preprocessing': sorted(preprocessing), 'sources': digest(sources),
                'dependencies': [{'repository': child, 'key': digest(contracts[child])[:24]}
                                 for child in edges[name]]}
        contracts[name] = contract
        visiting.remove(name)
    for name in sorted(roots):
        visit(name)
    return contracts


def export_graph_dependency(message, destination, project=Path('/work/consumer'), *, metadata_path=None):
    """Export only this node's already compiled objects; never compile children."""
    from fpm_shared import donor_roots
    contract = message['contract']; key = digest(contract)[:24]
    destination = Path(destination)/key
    if (destination/'manifest.json').exists():
        return validate_graph_export(destination, key, contract)
    metadata = json.loads((Path(metadata_path) if metadata_path else Path(project).parent/'precompiled.json').read_text())
    if (metadata['recipe'] != contract['recipe'] or metadata['compiler_version'] != '16.2.0'
            or contract['source'] not in metadata['records']):
        raise ValueError('Shared graph donor source/compiler mismatch.')
    expected = contract['context']['environment']
    if any(os.environ.get(name, '') != expected.get(name, '') for name in ('FPM_FFLAGS', 'FPM_LDFLAGS')):
        raise ValueError('Shared graph donor flags mismatch.')
    for package in contract['context']['apt_packages']:
        name, version = package.split('=', 1)
        if subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', name], text=True).strip() != version:
            raise ValueError('Shared graph native dependency mismatch: '+name)
    candidates = set(donor_roots(project).values()); roots = {}
    for pin in metadata['records']:
        matches = [p for p in candidates if p.name.endswith('-'+pin['revision'])]
        if len(matches) != 1:
            raise ValueError('Ambiguous or missing shared graph donor root.')
        roots[pin['repository'].lower()] = matches[0]
    contracts = dependency_graph(metadata['records'], roots, contract['context'], contract['recipe'],
                                 message['leaf_adapter'], message['graph_adapter'])
    repository = contract['source']['repository'].lower()
    if contracts[repository] != contract:
        raise ValueError('Shared graph donor manifest/source/dependency mismatch.')
    root = roots[repository]
    objects, module_dirs, modules, submodules = [], set(), set(), set()
    for command in json.loads((Path(project)/'build/compile_commands.json').read_text()):
        directory = Path(command['directory']); source = (directory/command['file']).resolve()
        if not source.is_relative_to(root):
            continue
        args = command['arguments']; compiler = Path(args[0]).name
        fortran = compiler == 'gfortran' and source.suffix.lower() in {'.f', '.f90', '.f95', '.for'}
        if not (fortran or (compiler == 'gcc' and source.suffix.lower() == '.c')):
            raise ValueError('Shared graph supports Fortran and C objects only.')
        obj = (directory/args[args.index('-o')+1]).resolve()
        if not obj.is_relative_to(Path(project)/'build') or not obj.is_file():
            raise ValueError('Missing shared graph object.')
        objects.append(obj)
        if not fortran:
            continue
        for i, arg in enumerate(args):
            if arg == '-J': module_dirs.add((directory/args[i+1]).resolve())
            elif arg.startswith('-J'): module_dirs.add((directory/arg[2:]).resolve())
        text = source.read_text(encoding='utf-8')
        modules.update(n.lower() for n in re.findall(
            r'^\s*module\s+(?!procedure\b|function\b|subroutine\b|pure\b|elemental\b|recursive\b)(\w+)', text, re.I|re.M))
        for parent, child in re.findall(r'^\s*submodule\s*\(\s*([\w:]+)\s*\)\s*(\w+)', text, re.I|re.M):
            submodules.add(parent.split(':')[0].lower()+'@'+child.lower())
    if not objects or len(set(objects)) != len(objects):
        raise ValueError('Missing or duplicate shared graph objects.')
    temporary = destination.with_name('.tmp-'+key+'-'+str(os.getpid()))
    temporary.mkdir(parents=True, exist_ok=False)
    try:
        (temporary/'include').mkdir(); (temporary/'lib').mkdir()
        library = 'fpm_shared_'+key
        subprocess.run(['ar', 'rcsD', str(temporary/'lib'/('lib'+library+'.a')), *map(str, objects)], check=True)
        found = set()
        for directory in module_dirs:
            for p in directory.iterdir():
                if p.suffix not in {'.mod', '.smod'} or p.stem.lower() not in modules|submodules:
                    continue
                target = temporary/'include'/p.name
                if target.exists() and file_hash(target) != file_hash(p):
                    raise ValueError('Conflicting shared graph module: '+p.name)
                shutil.copyfile(p, target)
                if p.suffix == '.mod': found.add(p.stem.lower())
        if (root/'include').is_dir():
            for p in (root/'include').rglob('*'):
                if p.is_file():
                    target = temporary/'include'/p.relative_to(root/'include')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if target.exists() and file_hash(target) != file_hash(p):
                        raise ValueError('Conflicting shared graph header: '+p.name)
                    shutil.copyfile(p, target)
        for p in root.iterdir():
            if p.is_file() and re.match(r'(?i)(licen[cs]e|copying|notice)', p.name):
                shutil.copyfile(p, temporary/p.name)
        files = {p.relative_to(temporary).as_posix(): {'sha256': file_hash(p), 'bytes': p.stat().st_size}
                 for p in temporary.rglob('*') if p.is_file()}
        manifest = {'key': key, 'contract': contract, 'modules': sorted(found), 'library': library,
            'files': files, 'artifact_bytes': sum(v['bytes'] for v in files.values()),
            'exported_objects': len(objects), 'compiled_objects': 0}
        (temporary/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        temporary.rename(destination)
        return manifest
    except BaseException:
        shutil.rmtree(temporary)
        raise


def validate_graph_export(directory, key, contract=None):
    """Use the leaf format/checks; also permit libraries without Fortran modules."""
    from pathlib import PurePosixPath
    directory = Path(directory); manifest = json.loads((directory/'manifest.json').read_text())
    if manifest.get('modules'):
        return validate_leaf_export(directory, key, contract)
    if (not re.fullmatch('[a-f0-9]{24}', key) or manifest['key'] != key
            or digest(manifest['contract'])[:24] != key or (contract is not None and manifest['contract'] != contract)
            or manifest.get('library') != 'fpm_shared_'+key or manifest.get('modules') != []):
        raise ValueError('Shared graph identity mismatch.')
    actual = set()
    for p in directory.rglob('*'):
        if p.is_symlink(): raise ValueError('Shared graph contains a symlink.')
        if p.is_file(): actual.add(p.relative_to(directory).as_posix())
    if actual != set(manifest['files'])|{'manifest.json'}:
        raise ValueError('Shared graph file list mismatch.')
    for name, item in manifest['files'].items():
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
            raise ValueError('Unsafe shared graph path.')
        p = directory/name
        if not p.is_file() or p.stat().st_size != item['bytes'] or file_hash(p) != item['sha256']:
            raise ValueError('Shared graph checksum mismatch.')
    return manifest


def install_graph_image(key, manifest_sha256):
    import fpm_shared_graph
    source = Path('/dependency-cache')/key
    if file_hash(source/'manifest.json') != manifest_sha256:
        raise ValueError('Shared graph manifest changed.')
    fpm_shared_graph.validate_graph_export(source, key)
    target = Path('/opt/fpm/shared')/key
    shutil.copytree(source, target)
    for p in [target, *target.rglob('*')]:
        p.chmod(0o755 if p.is_dir() else 0o444)


def rewrite_graph_sources(roots, plans):
    """Flatten only the hosted build copies; link dependents before dependencies."""
    import tomli_w
    originals = {p['repository'].lower(): tomllib.loads(
        (Path(roots[p['repository'].lower()])/'fpm.toml').read_text(encoding='utf-8')) for p in plans}
    native_links = []
    for plan in plans:
        link = originals[plan['repository'].lower()].get('build', {}).get('link', [])
        if isinstance(link, str): link = [link]
        native_links.extend(name for name in link if name not in native_links)
    for plan in plans:
        root = Path(roots[plan['repository'].lower()])
        original = originals[plan['repository'].lower()]
        stub = root/'playground-shared'; stub.mkdir(exist_ok=False)
        (stub/'stub.f90').write_text('module playground_shared_'+plan['key']+'\nend module\n')
        replacement = {'name': original['name'], 'version': '0.0.0',
            'build': {'auto-executables': False, 'auto-tests': False, 'auto-examples': False,
                'external-modules': sorted({m for p in plans for m in p['modules']}),
                'link': [p['library'] for p in plans]+native_links},
            'library': {'source-dir': 'playground-shared'}}
        (root/'fpm.toml').write_text(tomli_w.dumps(replacement), encoding='utf-8')


if __name__ == '__main__':
    import sys
    message = json.load(sys.stdin)
    manifest = export_graph_dependency(message, '/dependency-cache')
    subprocess.run(['sync', '/dependency-cache'], check=True)
    print(json.dumps({'manifest': manifest, 'manifest_sha256': file_hash(
        Path('/dependency-cache')/manifest['key']/'manifest.json')}))
