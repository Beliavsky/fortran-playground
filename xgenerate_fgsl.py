"""Operator-only Autoconf configuration for pinned FGSL on GNU/Linux LP64."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

REVISION = '27a3e7cc0809623bcfde680c39a6fdcf0f590c4c'


def generate(root):
    gsl = subprocess.check_output(['pkg-config', '--modversion', 'gsl'], text=True).strip()
    if gsl != '2.8':
        raise ValueError('Generation requires GSL 2.8.')
    with tempfile.TemporaryDirectory() as temporary:
        source = Path(temporary)/'source'
        shutil.copytree(root, source)
        for command in [['autoreconf', '-fi'], ['./configure', 'CC=gcc', 'FC=gfortran']]:
            subprocess.run(command, cwd=source, check=True)
        config = (source/'config.h').read_text()
    if '#define SIZEOF_LONG 8' not in config or '#define SIZEOF_SIZE_T 8' not in config:
        raise ValueError('The catalog configuration requires an LP64 host.')
    inputs = ['configure.ac', 'Makefile.am', 'fgsl.F90', 'fgsl_utils.c']
    inputs += sorted(p.relative_to(root).as_posix() for p in (root/'m4').rglob('*') if p.is_file())
    return {'schema': 1, 'repository': 'reinh-bader/fgsl', 'revision': REVISION,
            'license': 'GPL-2.0-or-later',
            'configuration': 'Upstream Autoconf probes on GNU/Linux LP64 with GSL 2.8; C and Fortran include the same generated configuration.',
            'inputs': {p: hashlib.sha256((root/p).read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                       for p in inputs},
            'files': {'playground-generated/config.inc': config}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    asset = generate(args.source.resolve())
    path = Path(__file__).resolve().parent/'fpm_catalog/generated'/('fgsl-'+REVISION+'.json')
    data = (json.dumps(asset, indent=2)+'\n').encode()
    if args.check:
        if path.read_bytes() != data:
            raise ValueError('FGSL generated configuration is out of date.')
    else:
        path.write_bytes(data)
    print('fgsl:', len(data), 'asset bytes')


if __name__ == '__main__':
    main()
