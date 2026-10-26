"""Compiler IDs and FPM-compatible executable names; no Modal dependency."""
COMPILERS = {
    'gfortran': {'label': 'GNU Fortran 16.2.0', 'command': 'gfortran', 'version': '16.2.0'},
    'gfortran17': {'label': 'GNU Fortran 17 (experimental)',
                   'command': '/opt/fpm/bin/gfortran', 'version': '17.0.0'},
    'ifx': {'label': 'Intel ifx', 'command': '/opt/fpm/bin/ifx', 'version': '2025.3.3'},
    'flang': {'label': 'LLVM Flang', 'command': '/opt/fpm/bin/flang-new', 'version': '23.1.5'},
}


def compiler_flags(compiler):
    return ['--profile', 'debug', '--compiler', COMPILERS[compiler]['command'],
            '--c-compiler', 'gcc', '--cxx-compiler', 'g++', '--no-prune']
