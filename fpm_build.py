"""Consumer build layout and artifact inventory, shared by prebuilds and workers."""
import json
import os
from pathlib import Path
import re


def consumer_project(package, source):
    """Use identical paths, manifest and flags during prebuilds and submissions."""
    import tomllib
    from fortran_plot import uses_pyplot, provides_pyplot, install_module
    project = Path('/work/consumer')
    (project / 'app').mkdir(parents=True, exist_ok=True)
    main = project / 'app/main.f90'
    # Do not invalidate FPM's timestamp cache when nothing changed.
    if not main.exists() or main.read_text(encoding='utf-8') != source:
        main.write_text(source, encoding='utf-8')
    if uses_pyplot(source) and not provides_pyplot(Path('/work/sources')):
        if not (project / 'src/pyplot_module.f90').exists():
            install_module(project / 'src')
    name = tomllib.loads((package / 'fpm.toml').read_text(encoding='utf-8'))['name']
    relative = Path(os.path.relpath(package, project)).as_posix()
    manifest = ('name = "playground-main"\n[build]\nauto-tests = false\n'
                'auto-examples = false\n[dependencies]\n' + json.dumps(name)
                + ' = { path = ' + json.dumps(relative) + ' }\n')
    path = project / 'fpm.toml'
    if not path.exists() or path.read_text(encoding='utf-8') != manifest:
        path.write_text(manifest, encoding='utf-8')
    return project


def consumer_modules(project):
    main = project / 'app/main.f90'
    names = set(re.findall(r'^\s*module\s+(?!procedure\b|function\b|subroutine\b)(\w+)',
        main.read_text(encoding='utf-8') if main.exists() else '', re.I | re.M))
    return {name.lower() for name in names}


def library_inventory(project=Path('/work/consumer'), *, main_modules=()):
    """Exclude modules from both the prebuild main and the visitor's new main."""
    excluded = consumer_modules(project) | set(main_modules)
    files = {}
    for path in (project / 'build').rglob('*'):
        if path.suffix.lower() not in {'.o', '.a', '.mod', '.smod'} or not path.is_file():
            continue
        relative = path.relative_to(project).as_posix()
        if path.suffix == '.o' and path.name == 'app_main.f90.o':
            continue
        if path.suffix.lower() in {'.mod', '.smod'} and path.stem.lower().split('@')[0] in excluded:
            continue
        stat = path.stat()
        # Filesystem snapshots preserve second-resolution mtimes, not nanoseconds.
        # FPM uses these same source/object timestamps to decide what to rebuild.
        files[relative] = [stat.st_size, int(stat.st_mtime)]
    return files


