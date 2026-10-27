"""Local runner distributed as run.py in downloaded FPM projects."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib


def prepare(project, settings, *, downloader=None):
    """Download locked sources once; preserve local edits on subsequent runs."""
    sys.path.insert(0, str(project / 'tools'))
    from fpm_collections import source_preparer
    from fpm_catalog_build import CatalogPreparer, validate_build
    from fpm_catalog_patches import apply_patches
    package = settings.get('package')
    identity = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()
    state = project / '.playground-prepared.json'
    if state.exists():
        saved = json.loads(state.read_text(encoding='utf-8'))
        if saved['identity'] != identity:
            raise ValueError('Project settings changed; extract a fresh project to prepare different dependencies.')
        root = (project / saved['root']).resolve()
        if not root.is_relative_to(project / 'dependencies') or not (root / 'fpm.toml').is_file():
            raise ValueError('Prepared dependencies are missing; extract a fresh project.')
        return root
    if (project / 'dependencies').exists():
        raise ValueError('dependencies already exists; refusing to overwrite local files.')
    options = validate_build(package) if package else {}
    pins = ([{'repository': package['repository'], 'revision': package['revision'],
              'sha256': package['archive_sha256']}, *package.get('dependencies', [])]
            if package else None)
    with tempfile.TemporaryDirectory(prefix='.prepare-', dir=project) as temporary:
        sources = Path(temporary) / 'sources'
        kwargs = {'pins': pins, **({'downloader': downloader} if downloader else {})}
        preparer = (CatalogPreparer(sources, options=options, **kwargs) if options
                    else source_preparer(sources, settings['request'], **kwargs))
        # These are local downloads, rather than a public preparation job.
        preparer.deadline = time.monotonic() + 600
        relative, records = preparer.prepare({**{k: v for k, v in settings['request'].items() if k != 'preprocess'},
                                             'source': 'program main\nend program main\n'})
        if package:
            apply_patches(package, sources / relative)
        sources.rename(project / 'dependencies')
    root = project / 'dependencies' / relative
    name = tomllib.loads((root / 'fpm.toml').read_text(encoding='utf-8'))['name']
    manifest = ('name = "playground-main"\n[build]\nauto-tests = false\nauto-examples = false\n'
                '[dependencies]\n' + json.dumps(name) + ' = { path = '
                + json.dumps(root.relative_to(project).as_posix()) + ' }\n')
    (project / 'fpm.toml').write_text(manifest, encoding='utf-8')
    from fortran_plot import uses_pyplot, provides_pyplot
    if (uses_pyplot((project / 'app/main.f90').read_text(encoding='utf-8'))
            and not provides_pyplot(project / 'dependencies')
            and not (project / 'src/pyplot_module.f90').exists()):
        (project / 'src').mkdir(exist_ok=True)
        shutil.copyfile(project / 'tools/pyplot_module.f90', project / 'src/pyplot_module.f90')
    state.write_text(json.dumps({'identity': identity, 'root': root.relative_to(project).as_posix(),
                                 'sources': records}, indent=2) + '\n', encoding='utf-8')
    return root


def run(project, args):
    settings = json.loads((project / 'playground.json').read_text(encoding='utf-8'))
    prepare(project, settings)
    # The downloaded main can be edited again after the first preparation.
    from fortran_plot import uses_pyplot, provides_pyplot
    if (uses_pyplot((project / 'app/main.f90').read_text(encoding='utf-8'))
            and not provides_pyplot(project / 'dependencies')
            and not (project / 'src/pyplot_module.f90').exists()):
        (project / 'src').mkdir(exist_ok=True)
        shutil.copyfile(project / 'tools/pyplot_module.f90', project / 'src/pyplot_module.f90')
    if args.prepare_only:
        return 0
    from fortran_plot import plotting_environment
    environment = plotting_environment(directory=project)
    options = (settings.get('package') or {}).get('catalog_build', {})
    flags = options.get('environment', {})
    if flags and not Path(args.compiler).name.lower().removesuffix('.exe').startswith('gfortran'):
        raise ValueError('This catalog recipe has GNU compiler flags. Use gfortran or adjust playground.json for your compiler.')
    for key, value in flags.items():
        environment[key] = (environment.get(key, '') + ' ' + value).strip()
    if not shutil.which('fpm'):
        raise ValueError('Install fpm and put it on PATH before running this project.')
    action = 'build' if args.build_only else 'run'
    command = ['fpm', action, '--profile', 'debug', '--compiler', args.compiler,
               '--c-compiler', 'gcc', '--cxx-compiler', 'g++', '--no-prune']
    if settings['request'].get('preprocess'):
        from fpm_compilers import preprocessing_flag
        name = Path(args.compiler).name.lower().removesuffix('.exe')
        command += ['--flag', (environment.get('FPM_FFLAGS', '') + ' ' + preprocessing_flag(name, windows=os.name == 'nt')).strip()]
    stdin = project / 'stdin.txt'
    print('Running:', ' '.join(command), flush=True)
    return subprocess.run(command, cwd=project, env=environment,
                          input=stdin.read_bytes() if stdin.exists() and action == 'run' else None).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true', help='Download/prepare sources without compiling.')
    parser.add_argument('--build-only', action='store_true', help='Compile without running.')
    parser.add_argument('--compiler', default='gfortran', help='Local Fortran compiler executable (default: gfortran).')
    args = parser.parse_args()
    try:
        return run(Path(__file__).resolve().parent, args)
    except (ValueError, OSError, ImportError) as error:
        print('Error:', error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
