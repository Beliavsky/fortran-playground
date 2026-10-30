"""Reviewed operator-only source allowance; public extraction stays unchanged."""
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import tarfile

from fpm_sources import MAX_ARCHIVE, MAX_EXPANDED, MAX_FILES

PARAMONTE = {
    'repository': 'cdslaborg/paramonte',
    'revision': '93a9f4f472894115b9f15ac0c68490af719f44fb',
    'archive_sha256': '7cbaacf1b28e7e65b78a46f838966d1a3e9bccd8e34c7daaa497412271c42518',
}
REVIEWED_EXPANDED = 128 * 1024 * 1024


def implementation_digest():
    root = Path(__file__).resolve().parent
    sources = {name: hashlib.sha256((root/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
               for name in ('fpm_catalog_limits.py', 'xfpm_catalog_prebuild.py')}
    return hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()


def source_limit(package):
    options = package.get('catalog_build', {})
    if 'source_limit' not in options:
        return MAX_EXPANDED
    settings = options['source_limit']
    if (settings != {'mib': 128, 'adapter_sha256': implementation_digest()}
            or any(package.get(k) != v for k, v in PARAMONTE.items())
            or package.get('id') != 'paramonte'):
        raise ValueError('Source allowance requires the reviewed ParaMonte archive and adapter.')
    return REVIEWED_EXPANDED


def preparer_limit(options, pins):
    if 'source_limit' not in options:
        return MAX_EXPANDED
    pin = next((p for p in (pins or []) if p['repository'] == PARAMONTE['repository']), {})
    return source_limit({'id': 'paramonte', 'repository': pin.get('repository'),
                         'revision': pin.get('revision'), 'archive_sha256': pin.get('sha256'),
                         'catalog_build': options})


def extract_operator_bundle(data, destination, *, package):
    """Only the pinned prebuild entry point may unpack a larger staged bundle.

    Match public archive path, type, per-file and entry checks; change only the
    aggregate expanded-byte allowance. Never used by visitor execution workers.
    """
    limit = source_limit(package)
    if limit != REVIEWED_EXPANDED:
        raise ValueError('Large bundle extraction requires an explicit source allowance.')
    if len(data) > MAX_ARCHIVE:
        raise ValueError('Package download exceeds 16 MiB.')
    with tarfile.open(fileobj=BytesIO(data), mode='r:gz') as archive:
        members, seen, roots, size = [], set(), set(), 0
        for member in archive:
            path = PurePosixPath(member.name)
            if (path.is_absolute() or '..' in path.parts or not path.parts
                    or '\\' in member.name or ':' in member.name
                    or not (member.isfile() or member.isdir())):
                raise ValueError('Package archive contains an unsafe path, link, or special file.')
            if path in seen or member.size > MAX_ARCHIVE or member.size < 0:
                raise ValueError('Package archive contains duplicate or oversized files.')
            seen.add(path)
            size += member.size
            members.append(member)
            roots.add(path.parts[0])
            if size > limit or len(members) > MAX_FILES:
                raise ValueError('Operator bundle exceeds the 128 MiB / 10000-entry limit.')
        if len(roots) != 1:
            raise ValueError('Expected one package archive root.')
        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)
        archive.extractall(destination, members=members, filter='data')
    return destination / roots.pop()
