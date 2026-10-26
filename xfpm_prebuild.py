"""Offline catalog builder, executed only in a network-blocked build sandbox."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from fpm_cache import consumer_project, library_inventory, CACHE_SCHEMA
from fpm_build import consumer_modules
from fpm_compilers import compiler_flags
from fpm_sources import extract_archive
from fortran_plot import plotting_environment, provides_pyplot, install_module


def build(message):
    bundle = extract_archive(base64.b64decode(message['bundle'], validate=True), Path('/work/sources'),
                             require_manifest=False)
    package = (bundle / message['root']).resolve()
    if not package.is_relative_to(bundle.resolve()) or not (package / 'fpm.toml').is_file():
        raise ValueError('Invalid prebuild root.')
    # Snapshot storage rounds fractional mtimes. Give staged sources an exact,
    # old timestamp so restored objects cannot appear older than their sources.
    for path in bundle.rglob('*'):
        if path.is_file():
            os.utime(path, (1700000000, 1700000000))
    project = consumer_project(package, message['source'])
    # Cache the optional plotting helper too, so adding a plot to a main does
    # not require regenerating a large dependency archive during a visitor job.
    if not provides_pyplot(bundle):
        install_module(project / 'src')
    os.environ.update(plotting_environment(directory=project))
    version = subprocess.check_output(['gfortran', '-dumpfullversion'], text=True).strip()
    if version != '16.2.0':
        raise ValueError('Catalog requires GNU Fortran 16.2.0.')
    started = time.monotonic()
    with Path('/work/prebuild.log').open('w') as log:
        # FPM's first dependency resolution uses ././ prefixes in include paths;
        # loading its dependency cache normalizes them and changes flag hashes.
        # Populate that second, stable set of targets ahead of visitor jobs too.
        for _ in range(2):
            remaining = max(1, 3600 - (time.monotonic() - started))
            process = subprocess.run(['fpm', 'build', *compiler_flags('gfortran')], cwd=project,
                                     stdout=log, stderr=subprocess.STDOUT, timeout=remaining)
            if process.returncode:
                log.flush()
                raise ValueError(Path('/work/prebuild.log').read_text(errors='replace')[-12000:])
    # Debug info in LAPACK alone can make a linked executable exceed the public
    # 16 MiB file limit. Keep runtime checks and compiler flags, but omit debug
    # symbols from cached dependency objects/archives (the user's main keeps them).
    objects = [str(path) for path in (project / 'build').rglob('*')
               if path.suffix in {'.o', '.a'} and path.is_file() and path.name != 'app_main.f90.o']
    subprocess.run(['strip', '--strip-debug', *objects], check=True, timeout=120)
    for path in project.rglob('*'):
        if path.is_file():
            stamp = round(path.stat().st_mtime)
            os.utime(path, (stamp, stamp))
    inventory = library_inventory()
    if not inventory:
        raise ValueError('No library artifacts were built.')
    metadata = {'schema': CACHE_SCHEMA, 'id': message['id'], 'key': message['key'], 'recipe': message['recipe'],
                'repository': message['repository'], 'revision': message['revision'],
                'root': message['root'], 'records': message['records'],
                'compiler_version': version, 'inventory': inventory,
                'main_modules': sorted(consumer_modules(project)),
                'prebuild_seconds': round(time.monotonic() - started, 3),
                'artifact_bytes': sum(value[0] for value in inventory.values())}
    Path('/work/precompiled.json').write_text(json.dumps(metadata))
    return {key: value for key, value in metadata.items() if key != 'inventory'}


if __name__ == '__main__':
    message = json.loads(sys.stdin.buffer.readline(24000000))
    # No build hook or compiler runs with root privileges, credentials or network access.
    os.setgroups([])
    os.setgid(65534)
    os.setuid(65534)
    try:
        print(json.dumps({'ok': True, **build(message)}), flush=True)
    except Exception as error:
        print(json.dumps({'ok': False, 'error': str(error)}), flush=True)
    # Remain alive until the coordinator snapshots/terminates the filesystem.
    time.sleep(3600)
