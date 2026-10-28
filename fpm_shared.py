"""Immutable, operator-owned exports of compatible Fortran leaf dependencies.

This module is not used for arbitrary visitor repositories. Exported archives
are installed into images; execution sandboxes never mount the export Volume.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import subprocess
import tomllib

SHARED_FILES = ('fpm_shared.py', 'xshared_fpm.py', 'xfpm_shared_prebuild.py', 'xfpm_shared_worker.py')
PLAN = Path('/opt/fpm/shared-consumer.json')
SHARED_ROOT = PurePosixPath('/opt/fpm/shared')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def implementation_digest(root):
    return digest({name: hashlib.sha256((Path(root)/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                   for name in SHARED_FILES})


def file_hash(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def build_context(package):
    options = package.get('catalog_build', {})
    return {'environment': options.get('environment', {}),
            'apt_packages': sorted(options.get('apt_packages', []))}


def dependency_contract(pin, root, roots, context, recipe, implementation):
    manifest = tomllib.loads((Path(root)/'fpm.toml').read_text(encoding='utf-8'))
    if manifest.get('dependencies'):
        raise ValueError('Shared export currently requires a leaf dependency: ' + pin['repository'])
    # Metadata-only version/name rendering does not affect Fortran compilation.
    profile = {key: manifest.get(key, {}) for key in ('preprocess', 'fortran', 'library')}
    profile['link'] = manifest.get('build', {}).get('link', [])
    edges = set()
    for parent in roots.values():
        m = tomllib.loads((Path(parent)/'fpm.toml').read_text(encoding='utf-8'))
        for spec in m.get('dependencies', {}).values():
            if isinstance(spec, dict) and 'path' in spec and (Path(parent)/spec['path']).resolve() == Path(root).resolve():
                if spec.get('preprocess'):
                    edges.add(json.dumps(spec['preprocess'], sort_keys=True))
    return {'schema': 1, 'source': {k: pin[k] for k in ('repository', 'revision', 'sha256')},
            'recipe': recipe, 'implementation': implementation, 'context': context,
            'profile': profile, 'edge_preprocessing': sorted(edges)}


def donor_roots(project):
    cache = tomllib.loads((Path(project)/'build/cache.toml').read_text())
    return {name: (Path(project)/entry['proj-dir']).resolve() for name, entry in cache.items()
            if name != 'playground-main'}


def export_dependency(contract, destination, project=Path('/work/consumer'), *, metadata_path=None):
    """Collect one dependency's existing objects/modules, without compilation."""
    key = digest(contract)[:24]
    destination = Path(destination)/key
    if (destination/'manifest.json').exists():
        existing = json.loads((destination/'manifest.json').read_text())
        validate_export(destination, key, contract)
        return existing
    metadata = json.loads((Path(metadata_path) if metadata_path else Path(project).parent/'precompiled.json').read_text())
    pin = contract['source']
    if (metadata['recipe'] != contract['recipe'] or metadata['compiler_version'] != '16.2.0'
            or pin not in metadata['records']):
        raise ValueError('Shared export source/compiler recipe mismatch.')
    expected = contract['context']['environment']
    if any(os.environ.get(name, '') != expected.get(name, '') for name in ('FPM_FFLAGS', 'FPM_LDFLAGS')):
        raise ValueError('Shared export compiler environment mismatch.')
    for package in contract['context']['apt_packages']:
        name, version = package.split('=', 1)
        installed = subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', name], text=True).strip()
        if installed != version:
            raise ValueError('Shared export native dependency mismatch: ' + name)
    roots = donor_roots(project)
    root = next((p for p in roots.values() if p.name.endswith('-'+pin['revision'])), None)
    if root is None or dependency_contract(pin, root, roots, contract['context'], metadata['recipe'],
                                            contract['implementation']) != contract:
        raise ValueError('Shared export preprocessing/manifest mismatch.')
    commands = json.loads((Path(project)/'build/compile_commands.json').read_text())
    objects, module_dirs, modules, submodules = [], set(), set(), set()
    for command in commands:
        directory = Path(command['directory'])
        source = (directory/command['file']).resolve()
        if not source.is_relative_to(root):
            continue
        args = command['arguments']
        fortran = Path(args[0]).name == 'gfortran' and source.suffix.lower() in {'.f', '.f90', '.f95', '.for'}
        c_source = Path(args[0]).name == 'gcc' and source.suffix.lower() == '.c'
        if not (fortran or c_source):
            raise ValueError('Shared export currently supports Fortran and C sources only.')
        obj = (directory/args[args.index('-o')+1]).resolve()
        if not obj.is_relative_to(Path(project)/'build') or not obj.is_file():
            raise ValueError('Missing compiled dependency object.')
        objects.append(obj)
        if not fortran:
            continue
        for i, arg in enumerate(args):
            if arg == '-J':
                module_dirs.add((directory/args[i+1]).resolve())
            elif arg.startswith('-J'):
                module_dirs.add((directory/arg[2:]).resolve())
        text = source.read_text(errors='strict')
        modules.update(n.lower() for n in re.findall(
            r'^\s*module\s+(?!procedure\b|function\b|subroutine\b|pure\b|elemental\b|recursive\b)(\w+)', text, re.I|re.M))
        for parent, child in re.findall(r'^\s*submodule\s*\(\s*([\w:]+)\s*\)\s*(\w+)', text, re.I|re.M):
            submodules.add(parent.split(':')[0].lower()+'@'+child.lower())
    if not objects or len(set(objects)) != len(objects):
        raise ValueError('Missing or duplicate dependency compile commands.')
    temporary = destination.with_name('.tmp-'+key+'-'+str(os.getpid()))
    temporary.mkdir(parents=True, exist_ok=False)
    (temporary/'lib').mkdir(); (temporary/'include').mkdir()
    try:
        library = 'fpm_shared_'+key
        subprocess.run(['ar', 'rcsD', str(temporary/'lib'/('lib'+library+'.a')), *map(str, objects)], check=True)
        found = set()
        for directory in module_dirs:
            for p in directory.iterdir():
                if p.suffix not in {'.mod', '.smod'} or p.stem.lower() not in modules|submodules:
                    continue
                target = temporary/'include'/p.name
                if target.exists() and file_hash(target) != file_hash(p):
                    raise ValueError('Conflicting dependency module variants: ' + p.name)
                shutil.copyfile(p, target)
                if p.suffix == '.mod': found.add(p.stem.lower())
        if not found:
            raise ValueError('No compiled dependency modules found.')
        if (root/'include').is_dir():
            shutil.copytree(root/'include', temporary/'include', dirs_exist_ok=True)
        # Keep redistribution notices alongside the exported library.
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


def validate_export(directory, key, contract=None):
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text())
    if (not re.fullmatch('[a-f0-9]{24}', key) or manifest['key'] != key
            or digest(manifest['contract'])[:24] != key or (contract is not None and manifest['contract'] != contract)):
        raise ValueError('Shared dependency identity mismatch.')
    if (manifest.get('library') != 'fpm_shared_'+key or not manifest.get('modules')
            or any(not re.fullmatch(r'[a-z][a-z0-9_]{0,62}', m) for m in manifest['modules'])):
        raise ValueError('Invalid shared dependency modules/library.')
    actual = set()
    for p in directory.rglob('*'):
        if p.is_symlink():
            raise ValueError('Shared dependency contains a symlink.')
        if p.is_file(): actual.add(p.relative_to(directory).as_posix())
    if actual != set(manifest['files'])|{'manifest.json'}:
        raise ValueError('Shared dependency file list mismatch.')
    for name, item in manifest['files'].items():
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
            raise ValueError('Unsafe shared dependency path.')
        p = directory/name
        if p.is_symlink() or not p.is_file() or p.stat().st_size != item['bytes'] or file_hash(p) != item['sha256']:
            raise ValueError('Shared dependency checksum mismatch: ' + name)
    return manifest


def install_shared_image(key, manifest_sha256):
    """Modal build step: copy verified exports; the resulting image has no mount."""
    from pathlib import Path
    import shutil
    import fpm_shared
    source = Path('/dependency-cache')/key
    if fpm_shared.file_hash(source/'manifest.json') != manifest_sha256:
        raise ValueError('Shared export manifest changed.')
    manifest = fpm_shared.validate_export(source, key)
    target = Path('/opt/fpm/shared')/key
    shutil.copytree(source, target)
    for p in [target, *target.rglob('*')]:
        p.chmod(0o755 if p.is_dir() else 0o444)


def rewrite_shared_sources(roots, plans):
    """Replace only selected prepared build copies; downloads retain originals."""
    import tomli_w
    for plan in plans:
        root = Path(roots[plan['repository'].lower()])
        original = tomllib.loads((root/'fpm.toml').read_text())
        if original.get('dependencies'):
            raise ValueError('Shared export is not a leaf dependency.')
        key = plan['key']
        stub = root/'playground-shared'
        stub.mkdir(exist_ok=False)
        (stub/'stub.f90').write_text('module playground_shared_'+key+'\nend module\n')
        link = original.get('build', {}).get('link', [])
        if isinstance(link, str): link = [link]
        replacement = {'name': original['name'], 'version': '0.0.0',
            'build': {'auto-executables': False, 'auto-tests': False, 'auto-examples': False,
                      'external-modules': plan['modules'], 'link': [plan['library'], *link]},
            'library': {'source-dir': 'playground-shared'}}
        (root/'fpm.toml').write_text(tomli_w.dumps(replacement))


def enable_shared_consumer():
    """Add external modules/flags when legacy prebuild/worker creates its project."""
    if not PLAN.is_file():
        raise ValueError('Missing shared dependency plan.')
    plan = json.loads(PLAN.read_text())
    import fpm_cache
    original = fpm_cache.consumer_project
    def consumer(package, source):
        project = original(package, source)
        import tomli_w
        manifest = tomllib.loads((project/'fpm.toml').read_text())
        manifest['build']['external-modules'] = sorted({m for p in plan for m in p['modules']})
        manifest['build']['link'] = [p['library'] for p in plan]
        (project/'fpm.toml').write_text(tomli_w.dumps(manifest))
        return project
    fpm_cache.consumer_project = consumer
    for name, options in [('FPM_FFLAGS', ['-I'+str(SHARED_ROOT/p['key']/'include') for p in plan]),
                          ('FPM_LDFLAGS', ['-L'+str(SHARED_ROOT/p['key']/'lib') for p in plan])]:
        flags = shlex.split(os.environ.get(name, ''))
        os.environ[name] = shlex.join(flags+[o for o in options if o not in flags])


if __name__ == '__main__':
    import sys
    contract = json.load(sys.stdin)
    manifest = export_dependency(contract, '/dependency-cache')
    subprocess.run(['sync', '/dependency-cache'], check=True)
    print(json.dumps({'key': manifest['key'], 'manifest_sha256': file_hash(
        Path('/dependency-cache')/manifest['key']/'manifest.json'), 'manifest': manifest}))
