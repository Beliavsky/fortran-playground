"""Checksum-guarded, operator-owned source workarounds for catalog builds."""
import hashlib
from pathlib import Path, PurePosixPath
import re

# Existing recipes keep their strict byte checks and cache identities.
LEGACY_ADAPTER_SHA256 = '86ce9e8662821f1a01dbc6be505d9b18aec81bac32d625ae6f37e85932e464a5'


def patch_digest():
    return hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def validate_patches(package):
    options = package.get('catalog_patches', {})
    if not options:
        return options
    if (set(options) != {'adapter_sha256', 'edits'}
            or options['adapter_sha256'] not in {LEGACY_ADAPTER_SHA256, patch_digest()}):
        raise ValueError('Refresh the catalog source patch checksum: ' + package['id'])
    for edit in options['edits']:
        if set(edit) != {'path', 'sha256', 'before', 'after'}:
            raise ValueError('Invalid catalog source edit.')
        path = PurePosixPath(edit['path'])
        if path.is_absolute() or '..' in path.parts or '\\' in edit['path'] or ':' in edit['path']:
            raise ValueError('Catalog edit must stay inside its root repository.')
        if not re.fullmatch('[a-f0-9]{64}', edit['sha256']) or not edit['before']:
            raise ValueError('Catalog edits require an exact original checksum and nonempty match.')
    return options


def apply_patches(package, root):
    options = validate_patches(package)
    root = Path(root).resolve()
    for edit in options.get('edits', []):
        path = (root / edit['path']).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Catalog edit leaves its repository.')
        data = path.read_bytes()
        # New recipes hash normalized text so manifests rewritten by the
        # preparer can be patched on both Windows and Unix. Legacy recipes
        # retain the exact byte semantics under which they were verified.
        if options['adapter_sha256'] != LEGACY_ADAPTER_SHA256:
            data = data.replace(b'\r\n', b'\n')
        if hashlib.sha256(data).hexdigest() != edit['sha256']:
            raise ValueError('Catalog edit source checksum mismatch: ' + edit['path'])
        source = data.decode('utf-8')
        if source.count(edit['before']) != 1:
            raise ValueError('Catalog edit must match exactly once: ' + edit['path'])
        path.write_bytes(source.replace(edit['before'], edit['after'], 1).encode('utf-8'))
