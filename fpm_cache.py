"""Pinned GNU 16 consumer catalog and private, immutable build-cache helpers."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE_SCHEMA = 1
from fpm_build import consumer_project, library_inventory

BUILD_FILES = ('xfpm_prebuild.py', 'fpm_build.py', 'fpm_sources.py', 'fortran_plot.py',
               'vendor/pyplot-fortran/src/pyplot_module.F90', 'vendor/pyplot-fortran/upstream.json')
WORKER_FILES = ('xfpm_worker.py', 'fpm_cache.py', 'fpm_build.py', 'fpm_sources.py', 'fpm_compilers.py',
                'fortran_plot.py', 'vendor/pyplot-fortran/src/pyplot_module.F90', 'vendor/pyplot-fortran/upstream.json')


def worker_identity(root=ROOT):
    digest = hashlib.sha256()
    for name in WORKER_FILES:
        digest.update(name.encode())
        digest.update((root / name).read_text(encoding='utf-8').encode())
    return digest.hexdigest()[:16]


def recipe_identity(root=ROOT):
    from fpm_compilers import compiler_flags, COMPILERS
    recipe = json.loads((root / 'fpm_build_recipe.json').read_text(encoding='utf-8'))
    recipe['flags'] = compiler_flags('gfortran')
    recipe['compiler'] = {k: COMPILERS['gfortran'][k] for k in ('command', 'version')}
    recipe['sources'] = {name: hashlib.sha256((root / name).read_text(encoding='utf-8').encode()).hexdigest()
                         for name in BUILD_FILES}
    return hashlib.sha256(json.dumps(recipe, sort_keys=True).encode()).hexdigest()[:24]


def catalog():
    return json.loads((ROOT / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']


def match_package(payload, packages=None):
    if payload.get('compiler', 'gfortran') != 'gfortran' or payload.get('workflow', 'consumer') != 'consumer':
        return None
    url = payload['url'].rstrip('/').removesuffix('.git').lower()
    return next((p for p in (catalog() if packages is None else packages)
                 if url == ('https://github.com/' + p['repository']).lower()
                 and payload.get('revision') == p['revision']), None)


def cached_request_matches(payload, metadata):
    """The broker chooses catalog entries; workers validate their immutable pin."""
    return (payload.get('compiler', 'gfortran') == 'gfortran'
            and payload.get('workflow', 'consumer') == 'consumer'
            and metadata.get('schema') == CACHE_SCHEMA
            and payload['url'].rstrip('/').removesuffix('.git').lower()
                == ('https://github.com/' + metadata['repository']).lower()
            and payload.get('revision') == metadata['revision'])


def cache_identity(package, recipe):
    """Metadata, other catalog entries and service code cannot invalidate a library."""
    pin = {k: package[k] for k in ('id', 'repository', 'revision', 'archive_sha256')}
    dependencies = [{k: p[k] for k in ('repository', 'revision', 'sha256')}
                    for p in package.get('dependencies', [])]
    identity = {'schema': CACHE_SCHEMA, 'package': pin, 'recipe': recipe,
                'dependencies': sorted(dependencies, key=lambda p: (p['repository'].lower(), p['revision']))}
    # Preserve all existing keys; only packages opting into an operator build
    # recipe depend on native libraries, compiler environment and adapters.
    if package.get('catalog_build'):
        identity['catalog_build'] = package['catalog_build']
    if package.get('catalog_patches'):
        identity['catalog_patches'] = package['catalog_patches']
    data = json.dumps(identity, sort_keys=True)
    return hashlib.sha256(data.encode()).hexdigest()[:24]
