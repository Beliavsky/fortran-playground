"""Generate the pinned ENNUF fixed-weight demonstration with NumPy 2.2.6.

Operator-only: downloaded projects install the audited Fortran asset directly.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

REVISION = '2555a7f1560ef3cb7cf707221fa5bb1b5334ee6f'


def generate(source):
    import numpy as np
    if np.__version__ != '2.2.6':
        raise ValueError('Regeneration requires numpy==2.2.6.')
    sys.path.insert(0, str(source / 'src'))
    from ennuf.ml_model import Model, InputLayer, Dense, Activation, SupportedActivations
    model = Model('ennuf_example', ['output'], description='Fixed-weight 2-2-1 ReLU example; not a trained model.')
    inputs = InputLayer((2,), 'features', model)
    hidden = Dense('hidden', inputs, model, 2,
                   np.array([[1, -1], [2, .5]], dtype=np.float32),
                   np.array([.5, -.25], dtype=np.float32))
    relu = Activation('relu', 2, hidden, model, SupportedActivations.from_identifier('relu'))
    output = Dense('output', relu, model, 1,
                   np.array([[2], [-3]], dtype=np.float32), np.array([1], dtype=np.float32))
    model.layers = [inputs, hidden, relu, output]
    text = model.to_fortran()
    # The upstream generator collects imported layer types in a Python set.
    # Import order has no semantic effect, so sort it for reproducible output.
    text = re.sub(r'(?im)^( *USE neural_net_mod, ONLY:)([^\n]+)$',
                  lambda m: m[1] + ' ' + ', '.join(sorted(v.strip() for v in m[2].split(','))), text)
    inputs = {p.relative_to(source).as_posix(): hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
              for p in sorted((source/'src/ennuf').rglob('*')) if p.is_file() and p.suffix in {'.py', '.f90'}}
    return {'schema': 1, 'repository': 'MetOffice/ennuf', 'revision': REVISION,
            'license': 'BSD-3-Clause', 'configuration': {'numpy': '2.2.6', 'precision': 'float32',
            'model': 'fixed-weight dense(2,2), ReLU, dense(2,1)'}, 'inputs': inputs,
            'files': {'playground-generated/ennuf_example_mod.f90': text}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = (json.dumps(generate(args.source.resolve()), indent=2)+'\n').encode()
    path = Path(__file__).resolve().parent/'fpm_catalog/generated'/('ennuf-'+REVISION+'.json')
    if args.check:
        if path.read_bytes() != data:
            raise ValueError('ENNUF generated asset is out of date.')
    else:
        path.write_bytes(data)
    print('ENNUF generated asset verified:', len(data), 'bytes')


if __name__ == '__main__':
    main()
