"""Operator-only configuration of pinned numerical and interoperability libraries.

Visitor preparation only installs the resulting checksum-locked text assets.
Run on GNU/Linux with GNU Fortran 16, GCC, CMake, MPICH, FFTW and OpenBLAS.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

PACKAGES = {
    'paramonte': ('cdslaborg/paramonte', '93a9f4f472894115b9f15ac0c68490af719f44fb', 'MIT',
                  ['-Dlib=static', '-Dpar=serial', '-Dlang=fortran', '-Dtest=none',
                   '-Dexam=none', '-Dbench=none', '-Dbuild=debug'], {'libparamonte', 'libparamontec'}),
    'dbcsr': ('cp2k/dbcsr', 'cd6f522ec5005da8c59d2883975a89a2da607eac', 'GPL-2.0-or-later',
               ['-DUSE_MPI=OFF', '-DUSE_OPENMP=OFF', '-DUSE_LIBXS=OFF', '-DUSE_LIBXSMM=OFF',
                '-DUSE_ACCEL=none', '-DWITH_C_API=OFF', '-DWITH_EXAMPLES=OFF',
                '-DBUILD_TESTING=OFF', '-DBUILD_SHARED_LIBS=OFF'], {'dbcsr'}),
    'psblas': ('sfilippone/psblas3', '68ae08adf2f71c9db80b58569ec140b948f626bf', 'BSD-3-Clause',
               ['-DPSB_BUILD_CUDA=OFF', '-DBUILD_SHARED_LIBS=OFF',
                '-DMPI_Fortran_COMPILER=/usr/bin/mpifort.mpich',
                '-DMPI_C_COMPILER=/usr/bin/mpicc.mpich'], {'base', 'base_C', 'prec', 'linsolve'}),
    '2decomp-fft': ('2decomp-fft/2decomp-fft', '4cb38be477b9457cfa5f5624c8fe09387968b190', 'BSD-3-Clause',
                    ['-DBUILD_TARGET=mpi', '-DFFT_Choice=generic', '-DENABLE_OMP=OFF',
                     '-DBUILD_TESTING=OFF', '-DBUILD_SHARED_LIBS=OFF',
                     '-DMPI_Fortran_COMPILER=/usr/bin/mpifort.mpich'], {'decomp2d'}),
    'flibcpp': ('swig-fortran/flibcpp', '334b2250230afbb419402ca2f1c0649c3b12a693', 'MIT',
                ['-DFLIBCPP_BUILD_EXAMPLES=OFF', '-DFLIBCPP_BUILD_TESTS=OFF',
                 '-DFLIBCPP_USE_SWIG=OFF', '-DBUILD_SHARED_LIBS=OFF'],
                {'flc', 'flc_algorithm', 'flc_map', 'flc_random', 'flc_set', 'flc_string', 'flc_vector'}),
    'libmbd': ('libmbd/libmbd', '77d7ab424d21f43dea9f57734b355ce4ea4d1a42', 'MPL-2.0',
               ['-DENABLE_SCALAPACK_MPI=OFF', '-DENABLE_C_API=ON', '-DBUILD_TESTING=OFF',
                '-DBUILD_SHARED_LIBS=OFF'], {'mbd'}),
    'dtfft': ('ShatrovOA/dtFFT', 'bbfd6746be7482bd8366ccb09a73b72882573984', 'GPL-3.0-or-later',
              ['-DDTFFT_WITH_FFTW=ON', '-DDTFFT_BUILD_SHARED=OFF', '-DDTFFT_BUILD_TESTS=OFF',
               '-DDTFFT_BUILD_C_CXX_API=OFF', '-DDTFFT_BUILD_PYTHON_API=OFF',
               '-DMPI_Fortran_COMPILER=/usr/bin/mpifort.mpich',
               '-DMPI_C_COMPILER=/usr/bin/mpicc.mpich', '-DMPI_CXX_COMPILER=/usr/bin/mpicxx.mpich'], {'dtfft'}),
}


def generate(name, original):
    repository, revision, license, options, targets = PACKAGES[name]
    inputs = {p.relative_to(original).as_posix(): hashlib.sha256(p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
              for p in sorted(original.rglob('*')) if p.is_file()
              and (p.name == 'CMakeLists.txt' or p.suffix in {'.cmake', '.in'})}
    files, sources, macros = {}, [], set()
    fypp_outputs = {}
    with tempfile.TemporaryDirectory() as temporary:
        source, build = Path(temporary)/'source', Path(temporary)/'build'
        shutil.copytree(original, source)
        if name == 'libmbd':
            # Match upstream's git-describe hash fallback for an untagged tree.
            (source/'cmake/libMBDVersionTag.cmake').write_text('set(VERSION_TAG "0.0.0-'+revision[:12]+'")\n')
        query = build/'.cmake/api/v1/query'
        query.mkdir(parents=True)
        (query/'codemodel-v2').touch()
        command = ['cmake', '-S', str(source), '-B', str(build),
                   '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_Fortran_COMPILER=gfortran',
                   '-DCMAKE_C_COMPILER=gcc', '-DCMAKE_CXX_COMPILER=g++', *options]
        if name == 'paramonte':
            command.append('-Dfc=' + shutil.which('gfortran'))
        subprocess.run(command, check=True)
        if name == 'dbcsr':
            subprocess.run(['cmake', '--build', str(build), '--target', 'fypp', '-j', '2'],
                           env={**os.environ, 'PYTHONHASHSEED': '0'}, check=True)
        reply = build/'.cmake/api/v1/reply'
        index = json.loads(next(reply.glob('index-*.json')).read_text())
        model = json.loads((reply/index['reply']['codemodel-v2']['jsonFile']).read_text())
        seen = set()
        for target in model['configurations'][0]['targets']:
            if target['name'] not in targets:
                continue
            seen.add(target['name'])
            data = json.loads((reply/target['jsonFile']).read_text())
            for group in data.get('compileGroups', []):
                if group['language'] == 'Fortran':
                    macros.update(d['define'] for d in group.get('defines', []))
                    if name == 'psblas':
                        # Upstream records feature/index definitions in raw flags.
                        for fragment in group.get('compileCommandFragments', []):
                            macros.update(re.findall(r'(?:^|\s)-D([A-Za-z_]\w*(?:=[^\s]*)?)', fragment['fragment']))
            for item in data.get('sources', []):
                path = Path(item['path'])
                if path.suffix.lower() not in {'.f', '.f90', '.c', '.cxx', '.cpp', '.cc'}:
                    continue
                if not path.is_absolute():
                    path = source/path
                if path.is_relative_to(build):
                    if name == 'dbcsr' and path.suffix == '.F':
                        # Keep the original Fypp templates in the source tree;
                        # visitor rendering uses the existing locked Fypp path.
                        output = path.relative_to(build).as_posix()
                        if not (source/output).is_file():
                            raise ValueError('Generated source has no original template: '+output)
                        text = re.sub(r'(?im)^([ \t]*USE \w+, ONLY: )((?:[\w ,\t]|&\n)+)$',
                                      lambda m: m[1] + ', '.join(sorted(v.strip() for v in m[2].replace('&\n', '').split(','))), path.read_text())
                        fypp_outputs[output] = hashlib.sha256(text.encode('utf-8')).hexdigest()
                    else:
                        output = 'playground-generated/'+path.name
                        files[output] = path.read_text()
                else:
                    output = path.relative_to(source).as_posix()
                if output not in sources:
                    sources.append(output)
        if seen != targets:
            raise ValueError('Missing configured library targets: '+str(targets-seen))
        if name == 'dtfft':
            files['playground-generated/dtfft_config.h'] = (build/'dtfft_config.h').read_text()
        if name == 'paramonte':
            # Upstream creates this include in its source tree at configure time.
            output = 'src/fortran/main/pm_paramonte@version.inc.F90'
            if (original/output).exists():
                raise ValueError('ParaMonte version include must be generated, not overwritten.')
            files[output] = (source/output).read_text()
        if name == 'psblas':
            files['playground-generated/psb_config.h'] = (build/'include/psb_config.h').read_text()
        if name == 'dbcsr':
            # The template bodies are checked as well as the configure inputs.
            for path in (original/'src').rglob('*'):
                if path.is_file() and path.suffix in {'.F', '.h', '.fypp'}:
                    inputs[path.relative_to(original).as_posix()] = hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
    return {'schema': 1, 'repository': repository, 'revision': revision, 'license': license,
            'configuration': {'options': options, 'sources': sorted(sources), 'fortran_macros': sorted(macros),
                              **({'fypp_outputs': dict(sorted(fypp_outputs.items()))} if fypp_outputs else {})},
            'inputs': dict(sorted(inputs.items())), 'files': dict(sorted(files.items()))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', choices=PACKAGES)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    asset = generate(args.package, args.source.resolve())
    path = Path(__file__).resolve().parent/'fpm_catalog/generated'/(args.package+'-'+asset['revision']+'.json')
    data = (json.dumps(asset, indent=2)+'\n').encode()
    if args.check:
        if path.read_bytes() != data:
            raise ValueError('Generated CMake asset is out of date: '+args.package)
    else:
        path.write_bytes(data)
    print('GENERATED', args.package, len(asset['files']), 'files;', len(data), 'bytes')


if __name__ == '__main__':
    main()
