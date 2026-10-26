"""Local FPM operations shared by the command-line runner and loopback server."""
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
import tomllib
import sys

COMPILERS = ('gfortran', 'gfortran17', 'ifx', 'flang', 'lfortran')


def project_directory(value):
    root = Path(value).resolve(strict=True)
    if not root.is_dir() or not (root / 'fpm.toml').is_file():
        raise ValueError('Choose a local project directory containing fpm.toml')
    return root


def validate_options(options):
    if not isinstance(options, dict) or set(options) - {
        'action', 'target', 'source', 'stdin', 'profile', 'compile_timeout', 'run_timeout', 'output_limit', 'fail_fast'}:
        raise ValueError('Invalid local FPM options')
    defaults = {'action': 'run', 'target': '', 'source': None, 'stdin': '', 'profile': 'debug',
                'compile_timeout': 120, 'run_timeout': 30, 'output_limit': 4 * 1024 * 1024, 'fail_fast': False}
    result = {**defaults, **options}
    if result['action'] not in ('build', 'run', 'test') or result['profile'] not in ('debug', 'release'):
        raise ValueError('Choose Build, Run, or Test and a debug or release profile')
    import re
    if not isinstance(result['target'], str) or (result['target'] and not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}', result['target'])):
        raise ValueError('Supply one target name, without flags or wildcards')
    for key in ('compile_timeout', 'run_timeout'):
        if type(result[key]) not in (float, int) or not math.isfinite(result[key]) or result[key] < 0:
            raise ValueError('Timeouts must be finite nonnegative seconds; 0 means unlimited')
    if type(result['output_limit']) is not int or not 1 <= result['output_limit'] <= 64 * 1024 * 1024:
        raise ValueError('Output limit must be between 1 byte and 64 MiB per stream')
    if type(result['fail_fast']) is not bool:
        raise ValueError('fail_fast must be a boolean')
    if not isinstance(result['stdin'], str) or '\0' in result['stdin']:
        raise ValueError('Standard input must be text without NUL characters')
    if result['source'] is not None:
        if not isinstance(result['source'], str) or not result['source'].strip() or '\0' in result['source']:
            raise ValueError('Enter a nonempty Fortran main program')
        if result['action'] == 'test':
            raise ValueError('Test applies to the package, not a custom main program')
        if result['target']:
            raise ValueError('Target selection applies to the package, not a custom main program')
    if result['action'] == 'build' and (result['stdin'] or result['target']):
        raise ValueError('Standard input and targets require Run or Test')
    return result


def target_names(project, kind):
    names = set()
    for path in (project / 'build').glob(f'*/{kind}/*'):
        if path.is_file() and (path.suffix.lower() == '.exe' if os.name == 'nt' else os.access(path, os.X_OK)):
            names.add(path.stem if os.name == 'nt' else path.name)
    return sorted(names)


def compiler_shim(executable, name, directory):
    """Give FPM 0.12 an unambiguous compiler basename, especially LLVM Flang."""
    basename = {'flang': 'flang-new'}.get(name, name)
    environment = os.environ.copy()
    environment['PATH'] = str(Path(executable).parent) + os.pathsep + environment.get('PATH', '')
    destination = directory / (basename + ('.cmd' if os.name == 'nt' else ''))
    if os.name == 'nt':
        # Keep compiler binaries in their installation directories so drivers
        # can locate DLLs, runtime libraries, and compiler subprocesses.
        executable_path = str(executable).replace('%', '%%')
        invocation = '"' + executable_path + '" %*'
        if name == 'flang':
            # FPM 0.12 adds -fPIC even for the Windows MSVC target. Modern
            # Flang rejects it; PE/COFF compilation has no matching option.
            driver = directory / 'flang_driver.py'
            driver.write_text('import subprocess,sys\nargs=[a for a in sys.argv[2:] if a not in ("-fPIC","-fpic")]\n'
                              'raise SystemExit(subprocess.call([sys.argv[1],*args]))\n', encoding='utf-8')
            invocation = '"' + str(sys.executable).replace('%', '%%') + '" "' + str(driver).replace('%', '%%') + '" "' + executable_path + '" %*'
        destination.write_text('@echo off\nsetlocal DisableDelayedExpansion\n' + invocation + '\nexit /b %errorlevel%\n', encoding='utf-8')
    else:
        destination.symlink_to(executable)
    # FPM 0.12 derives build directory names from this argument. A bare name
    # avoids embedded spaces/quotes, and separates GNU 16/17 cache entries.
    environment['PATH'] = str(directory) + os.pathsep + environment['PATH']
    return destination.name, environment


def execute_project(project, name, *, options=None, overrides=None, cancel=None, fpm_path=None):
    from xfortran_run import compiler_executable, run_process, finish_result
    started = time.perf_counter()
    row = {'compiler': name, 'ok': False, 'status': 'ERROR', 'stages': [], 'project': str(project),
           'notes': []}
    cancel = cancel or threading.Event()
    try:
        options = validate_options(options or {})
        root = project_directory(project)
        if name not in COMPILERS:
            raise ValueError(f'{name} is not supported for local FPM operations')
        executable = compiler_executable(name, overrides)
        if os.name == 'nt' and name == 'flang':
            row['notes'].append('The Windows Flang adapter removes FPM 0.12\'s unsupported -fPIC flag; other compiler arguments are preserved.')
        fpm = shutil.which(fpm_path or 'fpm')
        if not fpm:
            raise ValueError('fpm executable not found; add it to PATH or use --fpm-path')
        probe = run_process([executable, '/QV' if name == 'ifx' and os.name == 'nt' else '--version'],
                            root, cancel, timeout=10)
        lines = (probe['stdout'] + probe['stderr']).strip().splitlines()
        row['compiler_version'] = lines[0] if lines else name
        # The consumer and shim live outside src/app/test and are removed after
        # each compiler. Keeping them on this drive allows relative dependencies.
        with tempfile.TemporaryDirectory(prefix='.fortran-fpm-', dir=root) as temporary:
            scratch = Path(temporary)
            command, environment = compiler_shim(executable, name, scratch)
            workdir = root
            if options['source'] is not None:
                workdir = scratch / 'consumer'
                (workdir / 'app').mkdir(parents=True)
                manifest = tomllib.loads((root / 'fpm.toml').read_text(encoding='utf-8-sig'))
                dependency = manifest.get('name')
                if not isinstance(dependency, str) or not dependency.strip():
                    raise ValueError('Package manifest must contain a name')
                (workdir / 'fpm.toml').write_text('name="local-playground-main"\n[build]\nauto-tests=false\nauto-examples=false\n'
                    '[dependencies]\n' + json.dumps(dependency) + '={path="../.."}\n', encoding='utf-8')
                (workdir / 'app/main.f90').write_text(options['source'], encoding='utf-8')
                from fortran_plot import uses_pyplot, install_module, provides_pyplot
                if uses_pyplot(options['source']) and not provides_pyplot(root):
                    install_module(workdir / 'src')
            from fortran_plot import plotting_environment, snapshot, collect_plots
            environment = plotting_environment(environment)
            row['working_directory'] = str(workdir)
            flags = ['--profile', options['profile'], '--compiler', command, '--no-prune']

            def stage(args, timeout, stdin=''):
                value = run_process([fpm, *args], workdir, cancel, timeout=timeout, stdin=stdin,
                                    output_limit=options['output_limit'], env=environment)
                row['stages'].append(value)
                return value

            build = stage(['build', *flags, *(['--tests'] if options['action'] == 'test' else [])], options['compile_timeout'])
            row['build'] = {**build, 'commands': [build['command']]}
            if not build['ok']:
                row['status'] = 'STOPPED' if build.get('cancelled') else 'FAIL'
                return finish_result(row, started)
            kind = 'test' if options['action'] == 'test' else 'app'
            row['targets'] = names = target_names(workdir, kind)
            if options['action'] == 'build':
                row.update(ok=True, status='PASS')
                return finish_result(row, started)
            target = options['target'] if options['source'] is None else ''
            if not names or (target and target not in names) or (kind == 'app' and not target and len(names) > 1):
                row.update(status='FAIL', needs_target=True,
                           error='Choose an available target: ' + ', '.join(names) if names else
                                 'No application/test targets found. Use Build or supply a main program.')
                return finish_result(row, started)
            before = snapshot(workdir)
            run = stage([options['action'], *flags, *(['--target', target] if target else [])],
                        options['run_timeout'], options['stdin'])
            row.update(collect_plots(workdir, before))
            row['execution'] = run
            row.update(ok=run['ok'], status='PASS' if run['ok'] else 'STOPPED' if run.get('cancelled') else 'FAIL')
    except (ValueError, OSError) as error:
        row['error'] = str(error)
    return finish_result(row, started)


def compare_projects(project, names, *, options=None, update=None, cancel=None, **kwargs):
    if not names or len(set(names)) != len(names) or any(name not in COMPILERS for name in names):
        raise ValueError('Choose distinct local FPM compilers; ofort is not supported')
    options = validate_options(options or {})
    project = project_directory(project)
    cancel = cancel or threading.Event()
    rows, stopped = [], False
    for name in names:
        if stopped or cancel.is_set():
            row = {'compiler': name, 'status': 'SKIP', 'ok': False, 'error': 'Not submitted: comparison stopped.'}
        else:
            if update:
                update({'compiler': name, 'status': 'RUNNING'})
            row = execute_project(project, name, options=options, cancel=cancel, **kwargs)
            stopped = options['fail_fast'] and not row['ok']
        rows.append(row)
        if update:
            update(row)
    return rows
