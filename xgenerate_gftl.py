"""Regenerate audited gFTL header assets; not run by visitors or deployments.

Supply extracted source trees from the revisions below. Only the explicitly
listed upstream m4/configure operations run; no CMake projects are executed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

PINS = {'gftl': ('Goddard-Fortran-Ecosystem/gFTL', '4af86210b6cc6ac46d3298b6861571aa26bd6acc'),
        'gftl-shared': ('Goddard-Fortran-Ecosystem/gFTL-shared', '8009755e846560fbb389c01d76e013ddf14a7f98')}


def generate(gftl, shared, m4='m4'):
    inputs = {}

    def read(root, name):
        data = (root / name).read_bytes().replace(b'\r\n', b'\n')
        inputs[(str(root), name)] = hashlib.sha256(data).hexdigest()
        return data.decode('utf-8')

    def expand(name, definitions):
        path = Path(name)
        text = read(gftl, name)
        # CMake uses -s for diagnostic line markers. Omitting those markers
        # avoids recording machine-specific paths; macro expansion is identical.
        result = subprocess.run([m4, *['-D'+k+'='+v for k, v in definitions.items()],
                                 '-I'+str((gftl/'include/v1/templates').resolve())],
                                input=text.encode(), cwd=gftl/path.parent,
                                capture_output=True, timeout=15, check=True)
        return result.stdout.replace(b'\r\n', b'\n').decode('utf-8')

    files = {}
    for folder in ('templates', 'types'):
        base = 'include/v1/'+folder
        cm = read(gftl, base+'/CMakeLists.txt')
        names = re.search(r'set\s*\(\s*macro_files\s+(.*?)\)', cm, re.S)[1].split()
        for name in names:
            for param in ('type', 'key', 'value'):
                target = name if folder == 'types' and param == 'type' else param+'_'+name
                files[base+'/'+target+'.inc'] = expand(base+'/'+name+'.m4', {'param': param})
    base = 'include/v2/parameters'
    cm = read(gftl, base+'/CMakeLists.txt')
    for kind, args in re.findall(r'^\s*(process_m4|cpp_copy_parameter)\s*\(([^)]+)\)', cm, re.M):
        params = args.split()
        for parameter in (('T', 'Key', 'T1', 'T2') if '${parameter}' in args else ('',)):
            values = [v.replace('${parameter}', parameter) for v in params]
            if kind == 'process_m4':
                macro, source, target = values
                definitions = {'_T': macro}
            else:
                first, second, target = values
                source = 'cpp_copy.m4'
                definitions = {'_T_in': first, '_T_out': second}
            files[base+'/'+target] = expand(base+'/'+source, definitions)

    # The immutable dependency exporter exposes one include root. The v1 and
    # v2 include namespaces are disjoint, so stage both beneath that root.
    files = {name.replace('include/v1/', 'include/').replace('include/v2/', 'include/'): text
             for name, text in files.items()}
    for version in ('v1', 'v2'):
        base = gftl/'include'/version
        for path in sorted(base.rglob('*.inc')):
            target = 'include/'+path.relative_to(base).as_posix()
            if target in files:
                raise ValueError('Conflicting flattened include file: '+target)
            files[target] = read(gftl, path.relative_to(gftl).as_posix())

    # A concrete instantiation makes the header-only library explorable through
    # the same consumer workflow. This wrapper adds no container implementation.
    files['playground-generated/integer_vector.F90'] = (
        '! gFTL integer-vector instantiation; template implementation remains upstream.\n'
        'module playground_gftl\n#define T integer\n#define Vector IntegerVector\n'
        '#define VectorIterator IntegerVectorIterator\n#include "vector/template.inc"\n'
        '#undef VectorIterator\n#undef Vector\n#undef T\nend module playground_gftl\n')
    assets = {'gftl': files}
    outputs = {}
    for typename in ('Integer32', 'Real64', 'String', 'Unlimited'):
        source = 'src/v2/vector-like/'+typename+'Generic.F90.in'
        text = read(shared, source).replace('@Container@', 'Vector').replace('@container@', 'vector')
        if re.search(r'@\w+@', text):
            raise ValueError('Unresolved configure substitution: '+source)
        outputs['playground-generated/v2_'+typename+'Vector.F90'] = text
    assets['gftl-shared'] = outputs
    result = {}
    for name, generated in assets.items():
        repo, revision = PINS[name]
        root = gftl if name == 'gftl' else shared
        # Record every m4 input as well: includes may be read internally by m4.
        for path in root.rglob('*.m4'):
            read(root, path.relative_to(root).as_posix())
        evidence = {path: sha for (tree, path), sha in inputs.items() if tree == str(root)}
        result[name] = {'schema': 1, 'repository': repo, 'revision': revision,
                        'license': 'Apache-2.0', 'inputs': dict(sorted(evidence.items())),
                        'files': dict(sorted(generated.items()))}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gftl-source', type=Path, required=True)
    parser.add_argument('--shared-source', type=Path, required=True)
    parser.add_argument('--m4', default='m4')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--pflogger', action='store_true', help='Also generate the separate pFlogger map variant')
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent/'fpm_catalog/generated'
    folder.mkdir(exist_ok=True)
    for name, asset in generate(args.gftl_source.resolve(), args.shared_source.resolve(), args.m4).items():
        path = folder/(name+'-'+PINS[name][1]+'.json')
        data = (json.dumps(asset, indent=2, ensure_ascii=False)+'\n').encode()
        if args.check:
            if path.read_bytes() != data:
                raise ValueError('Generated asset is out of date: '+str(path))
        else:
            path.write_bytes(data)
        print(name, len(asset['files']), 'generated files;', len(data), 'bytes')
    if args.pflogger:
        # Keep the existing vector-only asset byte-for-byte unchanged.
        base = folder/('gftl-shared-'+PINS['gftl-shared'][1]+'.json')
        asset = json.loads(base.read_text(encoding='utf-8'))
        template = args.shared_source/'src/v2/map-like/Generic.F90.in'
        data = template.read_bytes().replace(b'\r\n', b'\n')
        asset['inputs']['src/v2/map-like/Generic.F90.in'] = hashlib.sha256(data).hexdigest()
        kinds = {'Integer': '__INTEGER', 'String': '__CHARACTER_DEFERRED',
                 'Unlimited': '__UNLIMITED_POLYMORPHIC'}
        for key, value in [('Integer','String'), ('String','Integer'), ('String','Unlimited')]:
            text = data.decode('utf-8')
            for name, replacement in {'Key_T': key+value, 'Container': 'Map', 'container': 'map',
                                       'KEY_TYPE': kinds[key], 'T_TYPE': kinds[value]}.items():
                text = text.replace('@'+name+'@', replacement)
            if re.search(r'@\w+@', text):
                raise ValueError('Unresolved map substitution.')
            asset['files']['playground-generated/v2_'+key+value+'Map.F90'] = text
        asset['inputs'] = dict(sorted(asset['inputs'].items()))
        asset['files'] = dict(sorted(asset['files'].items()))
        path = folder/('gftl-shared-pflogger-'+PINS['gftl-shared'][1]+'.json')
        data = (json.dumps(asset, indent=2, ensure_ascii=False)+'\n').encode()
        if args.check:
            if path.read_bytes() != data:
                raise ValueError('Generated pFlogger asset is out of date.')
        else:
            path.write_bytes(data)
        print('gftl-shared-pflogger',len(asset['files']),'generated files;',len(data),'bytes')


if __name__ == '__main__':
    main()
