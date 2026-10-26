"""Run ordered local Fortran files with installed compilers; no network or Modal.

Examples:
  python xfortran_run.py module.f90 main.f90 --compilers gfortran ifx --O 3
  python xfortran_run.py main.f90 --stdin-file input.txt --list --terse
"""
import argparse
import json
import math
import os
import re
from pathlib import Path
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from fortran_output_diff import add_diff_arguments, validate_diff_arguments, comparison_report

COMPILERS = ('gfortran', 'gfortran17', 'ifx', 'flang', 'lfortran', 'ofort')
ALIASES = {'gfortran17': ('gfortran17', 'gfortran-17', 'gfortran'),
           'flang': ('flang', 'flang-new', 'flang-23', 'flang-22', 'flang-21')}
SUFFIXES = {'.f90', '.f95', '.f03', '.f08', '.f', '.for', '.ftn'}


def stop_process(process):
    if os.name == 'nt':
        killer = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/taskkill.exe'
        try:
            subprocess.run([str(killer), '/PID', str(process.pid), '/T', '/F'],
                           capture_output=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
        except (OSError, subprocess.TimeoutExpired):
            pass
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if process.poll() is None:
        try:
            process.kill()
        except OSError:
            pass


def run_process(command, cwd, cancel, timeout=30, stdin='', output_limit=4 * 1024 * 1024):
    started = time.perf_counter()
    stage = {'ok': False, 'command': [str(arg) for arg in command], 'stdout': '', 'stderr': '', 'seconds': 0}
    if cancel.is_set():
        return {**stage, 'cancelled': True, 'stderr': 'Cancelled before launch.'}
    try:
        process = subprocess.Popen(stage['command'], cwd=cwd, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=os.name != 'nt',
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    except OSError as error:
        return {**stage, 'stderr': str(error), 'seconds': time.perf_counter() - started}
    buffers = [bytearray(), bytearray()]
    truncated = [False, False]

    def drain(stream, index):
        try:
            while chunk := stream.read(8192):
                room = max(0, output_limit - len(buffers[index]))
                buffers[index].extend(chunk[:room])
                truncated[index] |= len(chunk) > room
        except (OSError, ValueError):
            pass
        finally:
            stream.close()

    def feed():
        try:
            process.stdin.write(stdin.encode('utf-8'))
        except (OSError, ValueError):
            pass
        finally:
            try:
                process.stdin.close()
            except OSError:
                pass

    readers = [threading.Thread(target=drain, args=(stream, index), daemon=True)
               for index, stream in enumerate((process.stdout, process.stderr))]
    for reader in readers:
        reader.start()
    threading.Thread(target=feed, daemon=True).start()
    reason = ''
    try:
        while process.poll() is None:
            if cancel.is_set():
                reason = 'Cancelled.'; stage['cancelled'] = True; break
            if timeout and time.perf_counter() - started >= timeout:
                reason = f'Timed out after {timeout:g} seconds.'; stage['timed_out'] = True; break
            cancel.wait(0.05)
    except BaseException:
        stop_process(process)
        process.wait(timeout=5)
        raise
    if reason:
        stop_process(process)
    process.wait(timeout=5)
    for reader in readers:
        reader.join(timeout=1)
    stage.update(exit_code=process.returncode, ok=process.returncode == 0 and not reason,
                 stdout=buffers[0].decode('utf-8', errors='replace'),
                 stderr=buffers[1].decode('utf-8', errors='replace'),
                 seconds=time.perf_counter() - started)
    if reason or process.returncode:
        stage['stderr'] += ('\n' if stage['stderr'] else '') + (reason or f'Process exit code {process.returncode}.')
    if any(truncated):
        stage['truncated'] = True
        stage['stderr'] += '\nOutput was truncated at the configured per-stream limit.'
    return stage


def compiler_executable(name, overrides=None):
    if name not in COMPILERS:
        raise ValueError(f'Unknown compiler: {name}')
    value = (overrides or {}).get(name)
    candidates = [value] if value else ALIASES.get(name, (name,))
    executable = None
    for candidate in candidates:
        executable = shutil.which(candidate)
        if executable and name == 'gfortran17':
            probe = run_process([executable, '--version'], Path.cwd(), threading.Event(), 10)
            if not re.search(r'GNU Fortran[^\n]*\b17\.\d', probe['stdout'] + probe['stderr']):
                executable = None
        if executable:
            break
    if not executable:
        requirement = ' (GNU version 17 required)' if name == 'gfortran17' else ''
        raise ValueError(f'{name}: executable not found{requirement}: {value or ", ".join(candidates)}. '
                         f'Add it to PATH or use --compiler-path {name}=PATH')
    return executable


def discover(overrides=None):
    found = {}
    for name in COMPILERS:
        try:
            executable = compiler_executable(name, overrides)
            probe = run_process([executable, '/QV' if name == 'ifx' and os.name == 'nt' else '--version'],
                                Path.cwd(), threading.Event(), 10)
            version = (probe['stdout'] + probe['stderr']).strip().splitlines()
            found[name] = {'path': executable, 'version': version[0] if version else 'Version unavailable'}
        except ValueError as error:
            found[name] = {'path': None, 'error': str(error)}
    return found


def option_tokens(text):
    # POSIX shlex would eat backslashes in Windows paths. In Windows mode,
    # remove surrounding quotes while retaining their contents verbatim.
    return [part[1:-1] if len(part) >= 2 and part[0] == part[-1] and part[0] in '\"\'' else part
            for part in shlex.split(text, posix=os.name != 'nt')]


class UnsupportedOption(ValueError):
    pass


def option_notes(name, settings):
    notes = []
    if name in ('lfortran', 'ofort') and ((settings.get('optimization') or 0) > 0 or settings.get('preset') == 'optimized'):
        notes.append(f'{name}: positive optimization levels use --fast; numbered levels are unavailable.')
    if name == 'ofort':
        notes.append('ofort is an interpreter. Compile performs a syntax check; Run time includes parsing and execution.')
    if name == 'flang' and settings.get('preset') == 'debug':
        notes.append('flang: Debug adds symbols; it does not enable runtime bounds checks.')
    return notes


def flags_for(name, settings, extra=None):
    if name not in COMPILERS:
        raise ValueError(f'Unknown compiler: {name}')
    if not isinstance(settings, dict) or set(settings) - {'preset', 'optimization', 'standard', 'warnings', 'bounds_check', 'backtrace', 'preprocess', 'fast_math'}:
        raise ValueError('Unknown common compiler setting')
    if any(key in settings and type(settings[key]) is not bool for key in ['warnings', 'bounds_check', 'backtrace', 'preprocess', 'fast_math']):
        raise ValueError('Compiler switches must be booleans')
    windows = name == 'ifx' and os.name == 'nt'
    gnu = name in ('gfortran', 'gfortran17')
    flags = []
    preset = settings.get('preset', 'default')
    if preset not in ('default', 'debug', 'optimized', 'strict'):
        raise ValueError('Unknown compiler preset')
    if preset == 'debug':
        flags += (['-O0', '-g', '-fcheck=all', '-fbacktrace'] if gnu else
                  ['/Od', '/debug:full', '/check:all', '/traceback'] if windows else
                  ['-O0', '-g', '-check', 'all', '-traceback'] if name == 'ifx' else
                  ['-O0', '-g'] if name == 'flang' else ['-g', '--array-bounds-checking'] if name == 'lfortran' else ['--check-uninitialized'])
    if preset == 'strict':
        flags += (['-pedantic', '-Wall', '-Wextra'] if gnu else ['/warn:all'] if windows else
                  ['-warn', 'all'] if name == 'ifx' else ['-pedantic'] if name == 'flang' else
                  ['--disable-implicit-typing'] if name == 'lfortran' else ['--std=f2023'])
    level = settings.get('optimization')
    if level is None and preset == 'optimized':
        level = 3
    if level is not None:
        if type(level) is not int or level not in range(4):
            raise ValueError('Optimization must be 0, 1, 2, or 3')
        flags = [flag for flag in flags if flag not in ('-O0', '-O3', '/Od', '/O3')]
        flags += (['--fast'] if level else []) if name in ('lfortran', 'ofort') else [('/O' if windows else '-O') + str(level)]
    standard = settings.get('standard', 'default')
    years = {'1995': '95', '2003': '03', '2008': '08', '2018': '18', '2023': '23'}
    if standard != 'default':
        if not isinstance(standard, str) or standard not in years:
            raise ValueError('Unknown language standard')
        if gnu:
            flags += ['-std=f' + ('95' if standard == '1995' else standard)]
        elif name == 'ifx':
            flags += ['/stand:f' + years[standard]] if windows else ['-stand', 'f' + years[standard]]
        elif name == 'flang' and standard == '2018':
            flags += ['-std=f2018']
        elif name == 'flang':
            raise UnsupportedOption(f'flang: only standard 2018 has a verified local mapping; use Compiler default for other code.')
        elif standard == '2023':
            flags += ['--std=f2023' if name == 'ofort' else '--std=f23']
        else:
            raise UnsupportedOption(f'{name}: standard {standard} has no verified local mapping. Use Compiler default or native extra arguments.')
    switches = ({'warnings': ['-Wall', '-Wextra'], 'bounds_check': ['-fcheck=bounds'], 'backtrace': ['-fbacktrace'],
                 'preprocess': ['-cpp'], 'fast_math': ['-ffast-math']} if gnu else
                {'warnings': ['/warn:all'], 'bounds_check': ['/check:bounds'], 'backtrace': ['/traceback'],
                 'preprocess': ['/fpp'], 'fast_math': ['/fp:fast']} if windows else
                {'warnings': ['-warn', 'all'], 'bounds_check': ['-check', 'bounds'], 'backtrace': ['-traceback'],
                 'preprocess': ['-fpp'], 'fast_math': ['-fp-model', 'fast']} if name == 'ifx' else
                {'warnings': ['-pedantic'], 'preprocess': ['-cpp'], 'fast_math': ['-ffast-math']} if name == 'flang' else
                {'warnings': ['--style-suggestions'], 'bounds_check': ['--array-bounds-checking'],
                 'preprocess': ['--cpp'], 'fast_math': ['--fast']} if name == 'lfortran' else
                {'warnings': ['--warn-unused']})
    for key in ['warnings', 'bounds_check', 'backtrace', 'preprocess', 'fast_math']:
        if settings.get(key):
            if key not in switches:
                raise UnsupportedOption(f'{name}: {key} has no supported local mapping. Disable it or supply native extra arguments.')
            flags += switches[key]
    extra = extra or []
    if isinstance(extra, list):
        compile_extra = link_extra = extra
    elif isinstance(extra, dict) and not set(extra) - {'compile', 'link'}:
        compile_extra, link_extra = extra.get('compile', []), extra.get('link', [])
    else:
        raise ValueError(f'{name}: options must be an argument list or an object with compile/link lists')
    for arguments in (compile_extra, link_extra):
        if not isinstance(arguments, list) or any(not isinstance(arg, str) or '\0' in arg for arg in arguments):
            raise ValueError(f'{name}: each compiler option must be a string')
        if any(arg in ('-o', '-c', '/c', '-module', '-module-dir', '-J') or arg.startswith(('-J', '-module-dir=')) or arg.lower().startswith(('/object:', '/exe:', '/module:', '@')) for arg in arguments):
            raise ValueError('Output paths, compile-only switches, and response files are managed by the runner')
    return flags + compile_extra, flags + link_extra


def source_paths(files):
    paths = []
    for value in files:
        if '://' in str(value):
            raise ValueError('The local runner accepts local source files only')
        path = Path(value).resolve(strict=True)
        if not path.is_file():
            raise ValueError(f'Not a source file: {path}')
        if path in paths:
            raise ValueError(f'Source supplied more than once: {path}')
        paths.append(path)
    if not paths:
        raise ValueError('Supply at least one source file')
    return paths


def build_and_run(files, name, settings=None, extra=None, *, overrides=None, cancel=None,
                  compile_only=False, stdin='', cwd=None, compile_timeout=120, run_timeout=30,
                  output_limit=4 * 1024 * 1024, version='', include_dirs=None):
    cancel = cancel or threading.Event()
    started = time.perf_counter()
    result = {'compiler': name, 'compiler_version': version, 'ok': False, 'status': 'FAIL'}
    try:
        paths = source_paths(files)
        executable = compiler_executable(name, overrides)
        compile_flags, link_flags = flags_for(name, settings or {}, extra)
        result['notes'] = option_notes(name, settings or {})
        if name == 'lfortran':
            compile_flags = ['--no-color', '--no-style-suggestions', '--implicit-interface', '--separate-compilation', *compile_flags]
        result['compile_flags'], result['link_flags'] = compile_flags, link_flags
        if name == 'ofort':
            if isinstance(extra, dict) and extra.get('link'):
                raise UnsupportedOption('ofort is an interpreter and does not accept separate linker arguments.')
            result['interpreter'] = True
            with tempfile.TemporaryDirectory(prefix='fortran_ofort_') as temporary:
                inputs = paths
                if compile_only and len(paths) > 1:
                    fixed = [path.suffix.lower() in ('.f', '.for', '.ftn') for path in paths]
                    if any(fixed) and not all(fixed):
                        raise UnsupportedOption('ofort syntax checking cannot combine fixed-form and free-form sources.')
                    combined = Path(temporary) / ('combined.f' if all(fixed) else 'combined.f90')
                    combined.write_text('\n'.join(path.read_text(encoding='utf-8-sig').rstrip() + '\n' for path in paths), encoding='utf-8')
                    inputs = [combined]
                    result['notes'].append('ofort --check uses combined source in the supplied order; its line numbers refer to combined source.')
                stage = run_process([executable, *compile_flags, *(['--check'] if compile_only else []), *map(str, inputs)],
                                    cwd or Path.cwd(), cancel, compile_timeout if compile_only else run_timeout,
                                    '' if compile_only else stdin, output_limit)
            if compile_only:
                result['build'] = {**stage, 'commands': [stage['command']]}
            else:
                result['execution'] = stage
            result.update(ok=stage['ok'], status='STOPPED' if cancel.is_set() else 'PASS' if stage['ok'] else 'FAIL')
            return finish_result(result, started)
        build = result['build'] = {'ok': True, 'stdout': '', 'stderr': '', 'seconds': 0, 'commands': []}
        windows = name == 'ifx' and os.name == 'nt'
        with tempfile.TemporaryDirectory(prefix=f'fortran_{name}_') as temporary:
            directory = Path(temporary)
            objects = []
            include_flags = [argument for parent in dict.fromkeys([directory, *(path.parent for path in paths), *(include_dirs or [])])
                             for argument in (['/I' + str(parent)] if windows else ['-I', str(parent)])]
            for index, source in enumerate(paths):
                obj = directory / f'{index:04d}{".obj" if windows else ".o"}'
                command = ([executable, *compile_flags, *include_flags, '/module:' + str(directory), '/c', str(source), '/object:' + str(obj)] if windows else
                           [executable, *compile_flags, *include_flags, '-J' + str(directory)] + ['-c', str(source), '-o', str(obj)] if name in ('gfortran', 'gfortran17', 'lfortran') else
                           [executable, *compile_flags, *include_flags, '-module-dir', str(directory), '-c', str(source), '-o', str(obj)] if name == 'flang' else
                           [executable, *compile_flags, *include_flags, '-module', str(directory), '-c', str(source), '-o', str(obj)])
                remaining = max(0.001, compile_timeout - build['seconds']) if compile_timeout else 0
                stage = run_process(command, directory, cancel, remaining, output_limit=output_limit)
                build['commands'].append(stage['command'])
                for stream in ['stdout', 'stderr']:
                    build[stream] += stage[stream]
                build['seconds'] += stage['seconds']
                build['ok'] = stage['ok']
                if not stage['ok']:
                    break
                objects.append(str(obj))
            if build['ok']:
                program = directory / ('program.exe' if os.name == 'nt' else 'program')
                command = [executable, *objects, *link_flags, *(['/exe:' + str(program)] if windows else ['-o', str(program)])]
                stage = run_process(command, directory, cancel,
                    max(0.001, compile_timeout - build['seconds']) if compile_timeout else 0, output_limit=output_limit)
                build['commands'].append(stage['command'])
                for stream in ['stdout', 'stderr']:
                    build[stream] += stage[stream]
                build['seconds'] += stage['seconds']; build['ok'] = stage['ok']
                if stage['ok'] and not compile_only:
                    result['execution'] = run_process([str(program)], cwd or Path.cwd(), cancel, run_timeout, stdin, output_limit)
            result['ok'] = build['ok'] and (compile_only or result.get('execution', {}).get('ok', False))
            result['status'] = 'STOPPED' if cancel.is_set() else 'PASS' if result['ok'] else 'FAIL'
    except (OSError, ValueError) as error:
        result.update(status='ERROR', error=str(error))
    return finish_result(result, started)


def finish_result(result, started):
    total = time.perf_counter() - started
    compile_seconds = result.get('build', {}).get('seconds')
    run_seconds = result.get('execution', {}).get('seconds')
    result['times'] = {'total': total, 'compile': compile_seconds, 'run': run_seconds,
                       'other': max(0, total - (compile_seconds or 0) - (run_seconds or 0))}
    return result


def compare(files, names, *, update=None, fail_fast=False, versions=None, extras=None, cancel=None, **kwargs):
    cancel = cancel or threading.Event()
    rows, halted = [], False
    for name in names:
        if cancel.is_set() or halted:
            row = {'compiler': name, 'ok': False, 'status': 'SKIP', 'error': 'Not submitted: comparison stopped.'}
        else:
            if update:
                update({'compiler': name, 'status': 'RUNNING'})
            row = build_and_run(files, name, extra=(extras or {}).get(name), version=(versions or {}).get(name, ''), cancel=cancel, **kwargs)
            halted = fail_fast and not row['ok']
        rows.append(row)
        if update:
            update(row)
    return rows


def print_result(row, terse=False):
    print(f'\n=== {row["compiler"]}: {row["status"]} ===')
    if not terse:
        print(row.get('compiler_version') or 'Version unavailable')
    if row.get('error'):
        print(row['error'])
    for note in row.get('notes', []):
        print('Note: ' + note)
    for key, title in [('build', 'Compilation'), ('execution', 'Program output')]:
        stage = row.get(key)
        if not stage:
            continue
        if not terse:
            print(f'{title} ({stage["seconds"]:.3f}):')
            for command in stage.get('commands', []):
                print('Build: ' + subprocess.list2cmdline(command))
        for stream in ['stdout', 'stderr']:
            if stage.get(stream):
                print(stage[stream], end='' if stage[stream].endswith('\n') else '\n')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('files', nargs='+', help='Local source files in compilation order')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--compiler', choices=COMPILERS)
    group.add_argument('--compilers', choices=COMPILERS, nargs='+')
    parser.add_argument('--compiler-path', action='append', default=[], metavar='COMPILER=PATH')
    parser.add_argument('--compile-only', action='store_true', help='Compile and link without running')
    parser.add_argument('--stdin-file', type=Path)
    parser.add_argument('--cwd', type=Path, default=Path.cwd(), help='Program working directory (default: current directory)')
    parser.add_argument('--options-file', type=Path, help='JSON common settings and compiler argument lists or compile/link objects')
    parser.add_argument('--optimization', '--O', '-O', type=int, choices=range(4))
    parser.add_argument('--standard', choices=['default', '1995', '2003', '2008', '2018', '2023'])
    parser.add_argument('--preset', choices=['default', 'debug', 'optimized', 'strict'])
    for option in ['warnings', 'bounds-check', 'backtrace', 'preprocess', 'fast-math']:
        parser.add_argument('--' + option, action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument('--compile-timeout', type=float, default=120, help='Seconds for all compilation/linking; 0 means unlimited')
    parser.add_argument('--run-timeout', type=float, default=30, help='Seconds for execution; 0 means unlimited')
    parser.add_argument('--max-output-mb', type=int, default=4, help='Captured bytes per stream in MiB')
    parser.add_argument('--fail-fast', action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--terse', action='store_true')
    add_diff_arguments(parser)
    args = parser.parse_args(argv)
    cancel = threading.Event()
    try:
        paths = source_paths(args.files)
        if any(not math.isfinite(value) or value < 0 for value in [args.compile_timeout, args.run_timeout]) or args.max_output_mb < 1:
            raise ValueError('Timeouts must be nonnegative; output limit must be positive')
        if args.stdin_file and args.compile_only:
            raise ValueError('--stdin-file requires execution')
        overrides = {}
        for item in args.compiler_path:
            name, separator, value = item.partition('=')
            if not separator or name not in COMPILERS or not value:
                raise ValueError('Use --compiler-path COMPILER=PATH')
            overrides[name] = value
        config = json.loads(args.options_file.read_text(encoding='utf-8')) if args.options_file else {}
        if not isinstance(config, dict) or set(config) - {'common', *COMPILERS} or not isinstance(config.get('common', {}), dict):
            raise ValueError('Options file must contain common settings and/or compiler entries')
        settings = dict(config.get('common', {}))
        for key in ['optimization', 'standard', 'preset', 'warnings', 'bounds_check', 'backtrace', 'preprocess', 'fast_math']:
            if getattr(args, key) is not None:
                settings[key] = getattr(args, key)
        names = args.compilers or [args.compiler or 'gfortran']
        validate_diff_arguments(args, names)
        if len(set(names)) != len(names):
            raise ValueError('List each compiler only once')
        for name in names:
            try:
                flags_for(name, settings, config.get(name))
            except UnsupportedOption:
                pass  # Report this compiler's failure while trying the others.
        catalog = discover(overrides)
        if args.list:
            for path in paths:
                print(f'\n=== Source: {path} ===')
                source = path.read_text(encoding='utf-8-sig')
                print(source, end='' if source.endswith('\n') else '\n')
        rows = compare(paths, names, settings=settings, extras=config, overrides=overrides, cancel=cancel,
            versions={name: item.get('version', '') for name, item in catalog.items()},
            compile_only=args.compile_only, stdin=args.stdin_file.read_text(encoding='utf-8-sig') if args.stdin_file else '',
            cwd=args.cwd.resolve(strict=True), compile_timeout=args.compile_timeout, run_timeout=args.run_timeout,
            output_limit=args.max_output_mb * 1024 * 1024,
            fail_fast=args.fail_fast, update=lambda row: print_result(row, args.terse) if row['status'] != 'RUNNING' else None)
        print('\nSummary: times in seconds\nCompiler   Result      Total   Compile       Run     Other')
        for row in rows:
            times = ['-' if row.get('times', {}).get(key) is None else f'{row["times"][key]:.3f}' for key in ['total', 'compile', 'run', 'other']]
            print(f'{row["compiler"]:<10} {row["status"]:<7} ' + ' '.join(f'{value:>9}' for value in times))
        if args.diff:
            print('\n' + comparison_report(rows, args.diff, args.diff_atol, args.diff_rtol, args.diff_reference))
        return 0 if all(row['ok'] for row in rows) else 1
    except KeyboardInterrupt:
        cancel.set(); print('\nInterrupted.', file=sys.stderr); return 130
    except (OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr); return 2


if __name__ == '__main__':
    sys.exit(main())
