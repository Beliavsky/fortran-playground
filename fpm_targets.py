"""FPM target names/lists and basic globs, without shell interpretation."""
from fnmatch import fnmatchcase
import re
import shlex
import os
import tomllib


def discover_targets(project, kind, *, windows=False):
    """Use FPM's compiled target buckets, with manifest fallback for custom ones."""
    manifest = tomllib.loads((project / 'fpm.toml').read_text(encoding='utf-8-sig'))
    tables = {'app': 'executable', 'example': 'example', 'test': 'test'}
    declared = {category: {item['name'] for item in manifest.get(table, [])}
                for category, table in tables.items()}
    found = set()
    for path in (project / 'build').glob('*/*/*'):
        if not path.is_file() or not (path.suffix.lower() == '.exe' if windows else os.access(path, os.X_OK)):
            continue
        name = path.stem if windows else path.name
        bucket = path.parent.name
        if bucket == kind or (bucket not in tables and name in declared[kind]):
            found.add(name)
    return sorted(found)


def parse_targets(value):
    if not isinstance(value, str) or len(value) > 2048:
        raise ValueError('Targets must be text, at most 2048 characters.')
    try:
        words = shlex.split(value)
    except ValueError:
        raise ValueError('Close the quotes around target names or patterns.') from None
    patterns = [part for word in words for part in word.replace(',', ' ').split()]
    if len(patterns) > 32 or (value.strip() and not patterns):
        raise ValueError('Supply between 1 and 32 target names or patterns.')
    if any(not re.fullmatch(r'[A-Za-z0-9_*?][A-Za-z0-9_.*?-]{0,127}', p) for p in patterns):
        raise ValueError('Use target names or * and ? patterns, separated by spaces or commas; flags and paths are not targets.')
    return list(dict.fromkeys(patterns))


def select_targets(value, available):
    selected = []
    for pattern in parse_targets(value):
        matches = [name for name in available if fnmatchcase(name, pattern)]
        if not matches:
            raise ValueError(f'No available target matches {pattern!r}. Choose from: ' + ', '.join(available))
        selected.extend(name for name in matches if name not in selected)
    return selected
