"""Operator-only generation of the pinned fdict sources; never run by visitors."""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys

REVISION = '6ac903d4c0c524d45b948281a18b9656936c0197'


def generate(root):
    if version('fypp') != '3.2':
        raise ValueError('Generation requires Fypp 3.2.')
    inputs = ['CMakeLists.txt', 'VERSION', 'src/CMakeLists.txt',
              'cmake/fdictOptions.cmake', 'src/fdict_common.fypp',
              'src/fdict_types.fypp', 'src/variable.fypp', 'src/dictionary.fypp']
    # Match the upstream default build: standard integer/real/complex/logical
    # kinds, ranks through five, iso_fortran_env, no optional extended kinds.
    flags = ['-DFDICT_NAME="fdict"', '-DFDICT_VERSION="0.9.1"',
             '-DFDICT_VERSION_MAJOR=0', '-DFDICT_VERSION_MINOR=9', '-DFDICT_VERSION_PATCH=1',
             '-DFDICT_WITH_ISO_ENV=1', '-DFDICT_WITH_PURE_INTERFACE=0']
    outputs = {}
    for name in ['fdict_types', 'variable', 'dictionary']:
        process = subprocess.run([sys.executable, '-m', 'fypp', *flags, name+'.fypp'],
                                 cwd=root/'src', capture_output=True, check=True)
        outputs['playground-generated/'+name+'.f90'] = process.stdout.decode().replace('\r\n', '\n')
    return {'schema': 1, 'repository': 'zerothi/fdict', 'revision': REVISION,
            'license': 'MPL-2.0', 'generator': {'fypp': '3.2', 'flags': flags},
            'inputs': {p: hashlib.sha256((root/p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                       for p in inputs}, 'files': outputs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    asset = generate(args.source.resolve())
    path = Path(__file__).resolve().parent/'fpm_catalog/generated'/('fdict-'+REVISION+'.json')
    data = (json.dumps(asset, indent=2)+'\n').encode()
    if args.check:
        if path.read_bytes() != data:
            raise ValueError('fdict generated asset is out of date.')
    else:
        path.write_bytes(data)
    print('fdict:', len(asset['files']), 'generated sources;', len(data), 'bytes')


if __name__ == '__main__':
    main()
