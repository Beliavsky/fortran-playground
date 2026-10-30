"""Generate the pinned FyCollections library and two author list specializations."""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys

REVISION = 'f67b874669e63834f30cd83f2b96889072b4eec7'
SOURCES = ['lib/common.fpp', 'lib/interfaces.fpp', 'lib/ptrlist.fpp',
           'lib/module.fpp', 'examples/list/type_intlist.fpp',
           'examples/list/type_stringlist.fpp']


def generate(root):
    if version('fypp') != '3.2':
        raise ValueError('Generation requires Fypp 3.2.')
    outputs = {}
    for source in SOURCES:
        process = subprocess.run([sys.executable, '-m', 'fypp', '-Iinclude', source],
                                 cwd=root, capture_output=True, check=True)
        outputs['playground-generated/'+Path(source).with_suffix('.f90').name] = (
            process.stdout.decode('utf-8').replace('\r\n', '\n'))
    inputs = [*SOURCES, 'include/fycollections.fypp', 'LICENSE.rst']
    return {'schema': 1, 'repository': 'aradi/fycollections', 'revision': REVISION,
            'license': 'BSD-2-Clause',
            'generator': {'fypp': '3.2', 'flags': ['-Iinclude'],
                          'specializations': ['IntList', 'StringList']},
            'inputs': {p: hashlib.sha256((root/p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                       for p in inputs}, 'files': outputs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    asset = generate(args.source.resolve())
    path = Path(__file__).resolve().parent/'fpm_catalog/generated'/('fycollections-'+REVISION+'.json')
    data = (json.dumps(asset, indent=2)+'\n').encode('utf-8')
    if args.check:
        if path.read_bytes() != data:
            raise ValueError('FyCollections generated asset is out of date.')
    else:
        path.write_bytes(data)
    print('FyCollections:', len(asset['files']), 'generated sources;', len(data), 'bytes')


if __name__ == '__main__':
    main()
