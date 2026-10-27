"""Hosted and local FPM command-line modes; imported only when --fpm is used."""
import argparse
import getpass
import json
import math
import os
from pathlib import Path
import sys
import threading
import time
from urllib.parse import quote

from fortran_output_diff import add_diff_arguments, validate_diff_arguments, comparison_report

ROOT = Path(__file__).resolve().parent


def hosted_row(compiler, result, elapsed):
    row = {'compiler': compiler, 'ok': result['ok'], 'status': 'PASS' if result['ok'] else 'FAIL',
           'compiler_version': result.get('compiler', ''), 'stages': result.get('stages', []),
           'error': result.get('error', ''), 'targets': result.get('targets', []), 'packages': result.get('packages', []),
           'plots': result.get('plots', []), 'plot_notes': result.get('plot_notes', [])}
    if result.get('cache'):
        cache = result['cache']
        row['notes'] = [f'Precompiled package: {cache["package"]} ({cache["compiler"]}); '
                        + ('library reused' if cache['library_reused'] else 'library required rebuilding')]
    for stage in row['stages']:
        row['build' if stage['name'] == 'Build' else 'execution'] = {**stage, 'commands': [stage['command']]}
    build = row.get('build', {}).get('seconds')
    run = row.get('execution', {}).get('seconds')
    row['times'] = {'total': elapsed, 'compile': build, 'run': run, 'other': max(0, elapsed - (build or 0) - (run or 0))}
    return row


def run_hosted_job(client, payload, timeout):
    from xplayground_run import ServiceError
    started, identifier = time.monotonic(), None

    def remaining():
        seconds = timeout - (time.monotonic() - started)
        if seconds <= 0:
            raise ServiceError(f'FPM job timed out after {timeout:g} seconds')
        return min(30, seconds)

    try:
        created = client.request('jobs', payload, timeout=remaining())
        if not isinstance(created.get('id'), str) or not created['id']:
            raise ServiceError('No FPM job ID was returned; submission was not retried')
        identifier = quote(created['id'], safe='')
        while True:
            response = client.request('jobs/' + identifier, timeout=remaining())
            if response.get('state') == 'done':
                result = response.get('result')
                if not isinstance(result, dict) or type(result.get('ok')) is not bool:
                    raise ServiceError('Invalid FPM job result')
                return hosted_row(payload.get('compiler', 'gfortran'), result, time.monotonic() - started)
            time.sleep(min(0.5, remaining()))
    except BaseException:
        if identifier:
            try:
                client.request('jobs/' + identifier + '/cancel', {}, timeout=5)
            except Exception:
                print('Could not confirm cancellation; hosted job lifetime remains bounded.', file=sys.stderr)
        raise


def print_row(row, terse=False):
    print(f'\n=== {row["compiler"]}: {row["status"]} ===', flush=True)
    if row.get('error'):
        print(row['error'])
    for note in row.get('notes', []):
        print('Note: ' + note)
    if not terse:
        if row.get('compiler_version'):
            print(row['compiler_version'])
        if row.get('project'):
            print('Project: ' + row['project'])
        if row.get('working_directory'):
            print('Working directory: ' + row['working_directory'])
        for package in row.get('packages', []):
            print(f'Package: {package["repository"]} @ {package["revision"]}')
    for stage in row.get('stages', []):
        if not terse:
            import subprocess
            print(f'{stage.get("name", "FPM")} ({stage["seconds"]:.3f} seconds): ' + subprocess.list2cmdline(stage['command']))
        # Keep build diagnostics, including warnings, in terse output as well.
        for stream in ('stdout', 'stderr'):
            if stage.get(stream):
                print(stage[stream], end='' if stage[stream].endswith('\n') else '\n')
        if stage.get('error'):
            print(stage['error'])
    if row.get('targets'):
        print('Available targets: ' + ', '.join(row['targets']))


def print_summary(rows):
    if not rows:
        return
    print('\nSummary: times in seconds\nCompiler   Result      Total   Compile       Run     Other')
    for row in rows:
        values = ['-' if row.get('times', {}).get(key) is None else f'{row["times"][key]:.3f}'
                  for key in ('total', 'compile', 'run', 'other')]
        print(f'{row["compiler"]:<10} {row["status"]:<7} ' + ' '.join(f'{value:>9}' for value in values))


def print_plots(row, directory):
    from fortran_plot import save_plots
    for path in save_plots(row, directory, row['compiler']):
        print('Plot: ' + str(path))
    for note in row.get('plot_notes', []):
        print('Plot: ' + note)


def main(argv, *, hosted):
    names = ('gfortran', 'gfortran17', 'ifx', 'flang') if hosted else ('gfortran', 'gfortran17', 'ifx', 'flang', 'lfortran')
    parser = argparse.ArgumentParser(description=('Hosted' if hosted else 'Local') + ' FPM package operations')
    parser.add_argument('--fpm', required=True, metavar='GITHUB_URL' if hosted else 'DIRECTORY')
    parser.add_argument('--action', choices=('build', 'run', 'test'), default='run')
    parser.add_argument('--compile-only', action='store_true', help='Alias for --action build')
    parser.add_argument('--target', default='', help='Names or * and ? patterns, separated by spaces/commas; quote lists in the shell')
    parser.add_argument('--main', type=Path, help='Local UTF-8 main program using the package; Build or Run only')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--compiler', choices=names)
    group.add_argument('--compilers', nargs='+', choices=names)
    parser.add_argument('--stdin-file', type=Path)
    parser.add_argument('--fail-fast', action='store_true')
    parser.add_argument('--terse', action='store_true')
    parser.add_argument('--list', action='store_true', help='List the custom main program, when supplied')
    parser.add_argument('--plot-dir', type=Path, default=Path('playground-plots'), help='Save returned PNGs under DIR/COMPILER (default: playground-plots)')
    if hosted:
        parser.add_argument('--revision', default='')
        parser.add_argument('--subdirectory', default='', help='Top-level package directory in the translated R collection')
        parser.add_argument('--service-url', help='Defaults to site/fpm/service.json')
        parser.add_argument('--origin', default='https://beliavsky.github.io')
        parser.add_argument('--owner', action='store_true')
        parser.add_argument('--timeout', type=float, default=450)
    else:
        parser.add_argument('--profile', choices=('debug', 'release'), default='debug')
        parser.add_argument('--fpm-path', help='FPM executable override')
        parser.add_argument('--compiler-path', action='append', default=[], metavar='COMPILER=PATH')
        parser.add_argument('--compile-timeout', type=float, default=120)
        parser.add_argument('--run-timeout', type=float, default=30)
        parser.add_argument('--max-output-mb', type=int, default=4)
    add_diff_arguments(parser)
    args = parser.parse_args(argv)
    rows, cancel = [], threading.Event()
    try:
        selected = args.compilers or [args.compiler or 'gfortran']
        if len(set(selected)) != len(selected):
            raise ValueError('List each compiler only once')
        validate_diff_arguments(args, selected)
        if args.compile_only and args.action not in ('run', 'build'):
            raise ValueError('--compile-only conflicts with --action test')
        action = 'build' if args.compile_only else args.action
        source = args.main.read_text(encoding='utf-8-sig') if args.main else None
        stdin = args.stdin_file.read_text(encoding='utf-8-sig') if args.stdin_file else ''
        if action == 'build' and (args.stdin_file or args.target):
            raise ValueError('--stdin-file and --target require Run or Test')
        if source is not None and action == 'test':
            raise ValueError('--main cannot be used with --action test')
        if source is not None and args.target:
            raise ValueError('--target selects a package target; remove it when using --main')
        if args.list:
            if source is None:
                raise ValueError('--list requires --main; package sources are not listed by this option')
            print('=== Main program ===\n' + source + '\n=== End main program ===')
        if hosted:
            from xplayground_run import PlaygroundClient, ServiceError
            from fpm_collections import validate_request
            if not math.isfinite(args.timeout) or args.timeout <= 0:
                raise ValueError('--timeout must be positive finite seconds')
            url = args.service_url or json.loads((ROOT / 'site/fpm/service.json').read_text(encoding='utf-8'))['url']
            owner_key = (os.environ.get('P2F_OWNER_KEY') or getpass.getpass('Owner key: ')) if args.owner else ''
            client = PlaygroundClient(url, args.origin, owner_key=owner_key)
            payload = validate_request({'url': args.fpm, 'revision': args.revision, 'subdirectory': args.subdirectory, 'action': action,
                'target': args.target, 'source': source or '', 'workflow': 'consumer' if source is not None else 'package', 'stdin': stdin})
            health = client.request('health')
            available = health.get('compilers', {'gfortran': health.get('compiler')})
            missing = [name for name in selected if name not in available]
            if missing:
                raise ValueError('FPM compilers unavailable on this service: ' + ', '.join(missing))
            if not args.terse:
                print('FPM service: ' + client.service_url)
            for name in selected:
                submitted = {**payload, 'compiler': name}
                if 'compilers' not in health:
                    submitted.pop('compiler')  # Compatible with the original GNU-only API.
                row = run_hosted_job(client, submitted, args.timeout)
                rows.append(row); print_row(row, args.terse); print_plots(row, args.plot_dir)
                if args.fail_fast and not row['ok']:
                    break
        else:
            from fortran_fpm import compare_projects
            overrides = {}
            for value in args.compiler_path:
                name, separator, path = value.partition('=')
                if not separator or name not in names or not path:
                    raise ValueError('Use --compiler-path COMPILER=PATH')
                overrides[name] = path
            options = {'action': action, 'target': args.target, 'source': source, 'stdin': stdin,
                       'profile': args.profile, 'compile_timeout': args.compile_timeout, 'run_timeout': args.run_timeout,
                       'output_limit': args.max_output_mb * 1024 * 1024, 'fail_fast': args.fail_fast}
            def update(row):
                if row['status'] != 'RUNNING':
                    print_row(row, args.terse)
                    print_plots(row, args.plot_dir)
            rows = compare_projects(args.fpm, selected, options=options, overrides=overrides, cancel=cancel,
                fpm_path=args.fpm_path, update=update)
        print_summary(rows)
        if args.diff:
            print('\n' + comparison_report(rows, args.diff, args.diff_atol, args.diff_rtol, args.diff_reference))
        return 0 if rows and all(row['ok'] for row in rows) else 1
    except KeyboardInterrupt:
        cancel.set()
        print('\nInterrupted; any known hosted job was sent a cancellation request.', file=sys.stderr)
        return 130
    except Exception as error:
        print_summary(rows)
        print('Error: ' + str(error), file=sys.stderr)
        return 2
