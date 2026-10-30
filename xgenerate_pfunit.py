"""Generate pinned serial pFUnit catalog sources on GNU/Linux (operator only).

Uses the author's CMake configuration and assertion generator. No generation or
CMake command runs in visitor jobs. Supply the four extracted, pinned trees.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PINS = {
    'pfunit': ('Goddard-Fortran-Ecosystem/pFUnit', '380524aa4ce4d97b2815a07a1bd24b660841cc6f'),
    'fargparse': ('Goddard-Fortran-Ecosystem/fArgParse', '54c6066edb5bd9c2044274e13838db287ad947a3'),
    'gftl-shared': ('Goddard-Fortran-Ecosystem/gFTL-shared', '99dec0597bbd1df3f7b3bc46df930b46090ce509'),
    'gftl': ('Goddard-Fortran-Ecosystem/gFTL', '4af86210b6cc6ac46d3298b6861571aa26bd6acc'),
}
MAX_RANK = 2  # Keep the pinned text asset below the existing 2 MiB catalog limit.
OPTIONS = ['-DSKIP_MPI=YES', '-DSKIP_OPENMP=YES', '-DSKIP_ROBUST=YES',
           '-DSKIP_FHAMCREST=YES', '-DENABLE_TESTS=NO', f'-DMAX_ASSERT_RANK={MAX_RANK}']


def generate(roots):
    inputs = {name: {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
                    for p in sorted(root.rglob('*')) if p.is_file()}
              for name, root in roots.items()}
    with tempfile.TemporaryDirectory() as temporary:
        base = Path(temporary)
        source, build = base/'source', base/'build'
        shutil.copytree(roots['pfunit'], source)
        arg = source/'extern/fArgParse'
        shared = arg/'extern/gFTL-shared'
        gftl = shared/'extern/gFTL'
        for name, destination in [('fargparse', arg), ('gftl-shared', shared), ('gftl', gftl)]:
            shutil.copytree(roots[name], destination, dirs_exist_ok=True)
        query = build/'.cmake/api/v1/query'
        query.mkdir(parents=True)
        (query/'codemodel-v2').touch()
        command = ['cmake', '-S', str(source), '-B', str(build),
                   '-DCMAKE_Fortran_COMPILER=gfortran', *OPTIONS]
        result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=240)
        if result.returncode:
            raise RuntimeError(result.stdout)
        reply = build/'.cmake/api/v1/reply'
        index = json.loads(next(reply.glob('index-*.json')).read_text())
        model = json.loads((reply/index['reply']['codemodel-v2']['jsonFile']).read_text())
        targets = {t['name']: json.loads((reply/t['jsonFile']).read_text())
                   for t in model['configurations'][0]['targets']}
        names = ['funit-core', 'asserts', 'funit-main', 'fargparse',
                 'gftl-shared-v2', 'gftl-shared-v2-as-default']
        macros = {name: sorted({d['define'] for group in targets[name].get('compileGroups', [])
                               for d in group.get('defines', [])}) for name in names}
        generated = build/'src/funit/asserts'
        definitions = ['-'+d for d in macros['asserts']]
        jobs = [(f'Assert_{kind}.tmpl', f'Assert{kind}_{rank}d.F90', rank)
                for kind in ['Logical', 'Integer', 'Real', 'Complex'] for rank in range(MAX_RANK+1)]
        jobs += [('Norms.tmpl', f'Norms_{rank}d.F90', rank) for rank in range(MAX_RANK+1)]
        jobs += [('FormatIntrinsic.tmpl', 'FormatIntrinsic.F90', MAX_RANK)]
        for template, output, rank in jobs:
            subprocess.run([sys.executable, str(source/'tools/overload_template.py'),
                            '--rank='+str(rank), '-i', str(source/'src/funit/asserts'/template),
                            '-o', str(generated/output), *definitions], check=True, timeout=30)
        files, sources = {}, []
        for name in ['funit-core', 'asserts', 'funit-main']:
            for entry in targets[name]['sources']:
                if Path(entry['path']).suffix.lower() not in {'.f90', '.c'}:
                    continue
                path = Path(entry['path'])
                if not path.is_absolute():
                    path = source/path
                path = path.resolve()
                if path.is_relative_to(build):
                    destination = 'playground-generated/'+path.name
                    files[destination] = path.read_text()
                else:
                    destination = path.relative_to(source).as_posix()
                sources.append(destination)
        shared_files = {}
        for kind in ['Integer32', 'Integer', 'Real32', 'Real', 'Real64', 'String', 'Unlimited']:
            path = build/'extern/fArgParse/extern/gFTL-shared/src/v2/vector'/(kind+'Vector.F90')
            shared_files['playground-generated/v2_'+path.name] = path.read_text()
        for relative in ['vector/StringVector_wrap.F90', 'map/StringUnlimitedMap.F90',
                         'map/StringUnlimitedMap_wrap.F90']:
            path = build/'extern/fArgParse/extern/gFTL-shared/src/v2'/relative
            shared_files['playground-generated/v2_'+path.name] = path.read_text()
        assets = {}
        for name, output in [('pfunit', files), ('gftl-shared', shared_files)]:
            repository, revision = PINS[name]
            assets[name] = {'schema': 1, 'repository': repository, 'revision': revision,
                            'license': 'Apache-2.0', 'inputs': inputs[name],
                            'files': dict(sorted(output.items()))}
        evidence = {'configuration_options': OPTIONS, 'configuration_log': result.stdout,
                    'sources': sorted(set(sources)), 'compile_definitions': macros,
                    'dependency_pins': PINS, 'input_sha256': inputs,
                    'fargparse_sources': sorted(p.relative_to(arg).as_posix()
                                               for p in (arg/'src').glob('*.F90'))}
        return assets, evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in PINS:
        parser.add_argument('--'+name+'-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('fpm_catalog/generated'))
    parser.add_argument('--evidence', type=Path, help='Optional operator configuration report')
    parser.add_argument('--check', action='store_true', help='Compare assets without overwriting them')
    args = parser.parse_args()
    roots = {name: getattr(args, name.replace('-', '_')+'_source').resolve() for name in PINS}
    assets, evidence = generate(roots)
    args.output.mkdir(parents=True, exist_ok=True)
    for name, asset in assets.items():
        suffix = '-pfunit-' if name == 'gftl-shared' else '-'
        path = args.output/(name+suffix+PINS[name][1]+'.json')
        data = (json.dumps(asset, indent=2)+'\n').encode('utf-8')
        if args.check:
            if path.read_bytes() != data:
                raise ValueError('Generated pFUnit asset is out of date: '+str(path))
        else:
            path.write_bytes(data)
        print(name, len(asset['files']), 'generated files')
    if args.evidence:
        args.evidence.write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
