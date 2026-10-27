"""GitHub/catalog preparation for the local FPM backend; no hosted execution."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time

from fortran_fpm import COMPILERS, execute_project
from fpm_sources import Preparer, fetch
from fpm_collections import source_preparer, validate_request


def catalog():
    return json.loads((Path(__file__).resolve().parent / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']


def validate_local_request(data):
    if not isinstance(data, dict):
        raise ValueError('Invalid FPM request')
    compiler = data.get('compiler', 'gfortran')
    if not isinstance(compiler, str) or compiler not in COMPILERS:
        raise ValueError('Choose a supported local FPM compiler')
    # Source preparation is compiler-independent; the local backend also offers
    # LFortran, which is not a compiler ID in the hosted package service.
    request = validate_request({**data, 'compiler': 'gfortran'})
    request['compiler'] = compiler
    return request


def health(server):
    available = {name: item.get('version') or name for name, item in server.compilers.items()
                 if name in COMPILERS and item.get('path')}
    error = ('FPM was not found. Install it or restart with --fpm-path PATH.' if not server.fpm_path
             else 'No local FPM compiler was found. Add one to PATH or use --compiler-path.' if not available
             else 'Install the catalog preparation dependency: python -m pip install tomli-w==1.2.0'
             if importlib.util.find_spec('tomli_w') is None else '')
    return {'ok': not error, 'error': error, 'local': True, 'fpm': 'local installation',
            'compiler': available.get('gfortran', next(iter(available.values()), 'not found')),
            'compilers': available, 'workspace': str(server.workspace), 'precompiled': {},
            'features': {'translated_r': True}}


def compact_sources(sources, repositories):
    """Keep Windows compiler/log paths short, preserving dependency references."""
    import tomllib
    import tomli_w
    mapping = {root.resolve(): sources / ('p' + str(index))
               for index, root in enumerate(dict.fromkeys(repositories))}
    for original, compact in mapping.items():
        original.rename(compact)
    for original, compact in mapping.items():
        for path in compact.rglob('fpm.toml'):
            manifest = tomllib.loads(path.read_text(encoding='utf-8'))
            tables = [manifest.get(key, {}) for key in ('dependencies', 'dev-dependencies')]
            for kind in ('test', 'executable', 'example'):
                tables.extend(item.get('dependencies', {}) for item in manifest.get(kind, []))
            old_parent = (original / path.relative_to(compact)).parent
            for table in tables:
                for spec in table.values():
                    if not isinstance(spec, dict) or 'path' not in spec:
                        continue
                    dependency = (old_parent / spec['path']).resolve()
                    container = next((root for root in mapping if dependency.is_relative_to(root)), None)
                    if container is None:
                        raise ValueError('Prepared dependency leaves its source tree')
                    destination = mapping[container] / dependency.relative_to(container)
                    spec['path'] = Path(os.path.relpath(destination, path.parent)).as_posix()
            path.write_text(tomli_w.dumps(manifest), encoding='utf-8')
    return mapping


def execute_catalog(workspace, data, *, overrides=None, fpm_path=None, cancel=None, downloader=None):
    import threading
    from fpm_catalog_build import CatalogPreparer, validate_build
    from fpm_catalog_patches import apply_patches
    request = validate_local_request(data)
    compiler = request['compiler']
    cancel = cancel or threading.Event()
    package = next((p for p in catalog() if not request.get('subdirectory') and request['url'].rstrip('/').removesuffix('.git').lower()
                    == ('https://github.com/' + p['repository']).lower()
                    and request['revision'] == p['revision']), None)
    settings = validate_build(package) if package else {}
    flags = settings.get('environment', {})
    if flags and compiler not in ('gfortran', 'gfortran17'):
        raise ValueError('This catalog package has GNU-specific build settings; choose gfortran or gfortran17. '
                         'Other packages can use your other installed compilers.')
    started = time.monotonic()

    def download(url, **kwargs):
        if cancel.is_set():
            raise InterruptedError('Source preparation cancelled')
        value = (downloader or fetch)(url, **kwargs)
        if cancel.is_set():
            raise InterruptedError('Source preparation cancelled')
        return value

    # Every submission owns a fresh source/build tree. Nothing is written to a
    # persistent compiled cache or to an existing project in the workspace.
    with tempfile.TemporaryDirectory(prefix='.lfp-', dir=workspace) as temporary:
        sources = Path(temporary) / 's'
        consumer = request['workflow'] == 'consumer'
        pins = ([{'repository': package['repository'], 'revision': package['revision'],
                  'sha256': package['archive_sha256']}, *package.get('dependencies', [])]
                if package and consumer else None)
        preparer = (CatalogPreparer(sources, options=copy.deepcopy(settings), pins=pins, downloader=download)
                    if settings else source_preparer(sources, request, pins=pins, downloader=download))
        preparer.deadline = time.monotonic() + 600
        # Compiler choice does not change the downloaded source tree.
        relative, records = preparer.prepare({**request, 'compiler': 'gfortran', 'target': ''})
        root = sources / relative
        if package:
            if records[0]['sha256'] != package['archive_sha256']:
                raise ValueError('Catalog root archive checksum mismatch')
            apply_patches(package, root)
        original = root.resolve()
        mapping = compact_sources(sources, preparer.repositories.values())
        container = next(p for p in mapping if original.is_relative_to(p))
        root = mapping[container] / original.relative_to(container)
        prepared = time.monotonic() - started
        if cancel.is_set():
            raise InterruptedError('Source preparation cancelled')
        row = execute_project(root, compiler, overrides=overrides, fpm_path=fpm_path, cancel=cancel,
            build_environment=flags, options={'action': request['action'],
                'source': request['source'] if consumer else None,
                'stdin': request['stdin'] if request['action'] != 'build' else '',
                'target': request['target'] if not consumer and request['action'] != 'build' else '',
                'compile_timeout': 0, 'run_timeout': 0})
        stages = [{**stage, 'name': 'Build' if index == 0 else request['action'].capitalize()}
                  for index, stage in enumerate(row.get('stages', []))]
        notes = ['Built from scratch with installed FPM and compilers; no hosted service or compiled package cache.',
                 *row.get('notes', [])]
        if settings.get('apt_packages'):
            notes.append('Native library requirements (install equivalents on your system): '
                         + ', '.join(settings['apt_packages']))
        return {'ok': row['ok'], 'status': row['status'], 'error': row.get('error', ''),
                'compiler': row.get('compiler_version', compiler), 'compiler_id': compiler,
                'fpm': 'local installation', 'local': True, 'build_mode': 'from-scratch',
                'packages': records, 'stages': stages, 'targets': row.get('targets', []),
                'needs_target': row.get('needs_target', False), 'notes': notes,
                'plots': row.get('plots', []), 'plot_notes': row.get('plot_notes', []),
                'prepare_seconds': prepared, 'total_seconds': time.monotonic() - started}
