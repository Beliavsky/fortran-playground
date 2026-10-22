"""Compile and run ordered Fortran source files through the hosted playground API."""
import argparse
import getpass
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
MAX_SOURCE_BYTES = 100000
DEFAULT_ORIGIN = 'https://beliavsky.github.io'
COMPILERS = ('gfortran', 'gfortran17', 'ifx', 'flang', 'lfortran', 'ofort')


@dataclass(frozen=True)
class SourceSection:
    filename: str
    first_line: int
    last_line: int


def combine_sources(paths):
    """Preserve argument order; map combined source lines back to each input."""
    chunks, sections, seen = [], [], set()
    line, size = 1, 0
    for path in paths:
        path = Path(path)
        if path.resolve() in seen:
            raise ValueError(f'Source file supplied more than once: {path}')
        seen.add(path.resolve())
        if path.stat().st_size > MAX_SOURCE_BYTES + 3:
            raise ValueError(f'{path}: source exceeds the 100 KB limit')
        try:
            source = path.read_bytes().decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
        except UnicodeError as error:
            raise ValueError(f'{path}: expected UTF-8 source') from error
        if not source.strip():
            raise ValueError(f'{path}: source is empty')
        if not source.endswith('\n'):
            source += '\n'
        filename = str(path).replace('\n', ' ').replace('\r', ' ')
        if len(paths) > 1:
            header = f'! --- Source: {filename} ---\n'
            chunks.append(header)
            size += len(header.encode('utf-8'))
            line += 1
        sections.append(SourceSection(filename, line, line + source.count('\n') - 1))
        chunks.append(source)
        size += len(source.encode('utf-8'))
        if size > MAX_SOURCE_BYTES:
            raise ValueError('Combined source, including separator comments, exceeds the 100 KB limit')
        line += source.count('\n')
    if not chunks:
        raise ValueError('Supply at least one source file')
    return ''.join(chunks), sections


def diagnostic_locations(text, sections):
    """Annotate recognized locations without rewriting the original diagnostics."""
    locations = []
    for match in re.finditer(r'\binput_p\.f90(?::|\()(\d+)', text):
        line = int(match.group(1))
        for section in sections:
            if section.first_line <= line <= section.last_line:
                location = f'input_p.f90:{line} -> {section.filename}:{line-section.first_line+1}'
                if location not in locations:
                    locations.append(location)
                break
    return locations


def origin_url(value, *, https_only=True):
    try:
        url = urlsplit(value)
        url.port  # Validate an optional port before constructing requests.
        valid = (url.scheme in ({'https'} if https_only else {'https', 'http'}) and url.hostname
                 and not (url.username or url.password or url.query or url.fragment)
                 and url.path in ('', '/'))
    except (ValueError, TypeError):
        valid = False
    if not valid:
        raise ValueError('Expected an ' + ('HTTPS' if https_only else 'HTTP(S)') +
                         ' origin without a path, credentials, query, or fragment')
    return f'{url.scheme}://{url.netloc}'


class ServiceError(Exception):
    pass


class PlaygroundClient:
    def __init__(self, service_url, origin=DEFAULT_ORIGIN, *, owner_key=''):
        self.service_url = origin_url(service_url)
        self.origin = origin_url(origin, https_only=False)
        self.token = ''
        if owner_key and not re.fullmatch(r'[A-Za-z0-9_-]{32,256}', owner_key):
            raise ValueError('Owner key must contain 32 to 256 letters, digits, underscores, or hyphens')
        self.owner_key = owner_key

    def request(self, path, payload=None, *, timeout=30):
        headers = {'Origin': self.origin, 'User-Agent': 'fortran-playground-python-client'}
        if self.token:
            headers['X-P2F-Token'] = self.token
        if path == 'jobs' and payload is not None and self.owner_key:
            headers['X-P2F-Owner-Key'] = self.owner_key
        data = None
        if payload is not None:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(payload).encode('utf-8')
        request = Request(self.service_url + '/api/' + path, data=data, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                result = json.load(response)
        except HTTPError as error:
            text = error.read().decode('utf-8', errors='replace')
            try:
                parsed = json.loads(text)
                text = parsed.get('error') or parsed.get('detail') or text
            except (ValueError, AttributeError):
                pass
            raise ServiceError(f'HTTP {error.code}: {str(text)[:1000]}') from error
        except (URLError, OSError, ValueError) as error:
            raise ServiceError(f'Execution service request failed: {error}') from error
        if not isinstance(result, dict):
            raise ServiceError('The execution service returned an invalid response')
        return result

    def connect(self):
        session = self.request('session')
        if not isinstance(session.get('token'), str) or not session['token']:
            raise ServiceError('The execution service did not provide a session token')
        self.token = session['token']
        return session

    def run_job(self, source, compiler, options, *, compile_only=False, timeout=300):
        started = time.monotonic()
        deadline = started + timeout
        identifier = None
        payload = {'source': '', 'fortran_source': source,
                   'mode': 'fortran-compile' if compile_only else 'fortran-edit',
                   'compiler': compiler, 'automatic': False}
        if options:
            payload['compiler_options'] = options

        def remaining():
            seconds = deadline - time.monotonic()
            if seconds <= 0:
                raise ServiceError(f'{compiler}: timed out after {timeout:g} seconds')
            return min(30, seconds)

        try:
            created = self.request('jobs', payload, timeout=remaining())
            if not isinstance(created.get('id'), str) or not created['id']:
                raise ServiceError('The service did not return a job ID; submission was not retried')
            identifier = quote(created['id'], safe='')
            while True:
                job = self.request('jobs/' + identifier, timeout=remaining())
                if job.get('state') == 'done':
                    result = job.get('result')
                    if not isinstance(result, dict) or not isinstance(result.get('ok'), bool):
                        raise ServiceError('The service returned an invalid job result')
                    return result, time.monotonic() - started
                time.sleep(min(0.5, remaining()))
        except BaseException:
            if identifier:
                try:
                    self.request('jobs/' + identifier + '/cancel', {}, timeout=5)
                except Exception as error:
                    print(f'Could not confirm cancellation: {error}', file=sys.stderr)
            # Never retry a submission: it may have been accepted before a network error.
            raise


def additional_flags(spec, flags, additional):
    """Validate bounded token lists against the same catalog advertised to clients."""
    if (not isinstance(additional, list) or len(additional) > 32 or
            any(not isinstance(arg, str) or not arg or len(arg) > 128 for arg in additional)):
        raise ValueError('Additional options must be a list of at most 32 short argument strings.')
    if not additional:
        return flags
    groups = spec.get('additional_options', {})
    if not groups:
        raise ValueError('Additional options are unavailable for this compiler/service.')
    choices = [(group, choice) for group, values in groups.items() for choice in values]
    seen = {}
    for arguments, strict in [(flags, False), (additional, True)]:
        index = 0
        while index < len(arguments):
            match = next(((group, choice) for group, choice in choices
                          if arguments[index:index + len(choice)] == choice), None)
            if match is None:
                if strict:
                    raise ValueError(f'Unsupported additional option: {arguments[index]}. Choose an advertised option.')
                index += 1
                continue
            group, choice = match
            if group in seen and seen[group] != choice:
                raise ValueError(f'Conflicting {group} options: {" ".join(seen[group])} and {" ".join(choice)}.')
            seen[group] = choice
            index += len(choice)
    return flags + additional


def portable_arguments(spec, common, compiler, notes=None):
    """Translate intentions using service-owned mappings, without compiler probes."""
    arguments = []
    for key, value in common.items():
        if value is False:
            continue
        choice = str(value).lower()
        flags = spec.get('portable_options', {}).get(key, {}).get(choice)
        if flags is None:
            raise ValueError(f'{compiler} does not support portable option {key}={choice} on this service')
        arguments.extend(flags)
        note = spec.get('portable_option_notes', {}).get(key, {}).get(choice)
        if note and notes is not None:
            notes.append(f'Note: {compiler}: {note}')
    return arguments


def selections(session, compilers, args, notes=None):
    """Validate every compiler before spending any job allowance."""
    if len(set(compilers)) != len(compilers):
        raise ValueError('List each compiler only once')
    if args.compile_only and not session.get('features', {}).get('compile_only'):
        raise ValueError('This service does not advertise compile-only jobs')
    if args.owner and not session.get('features', {}).get('owner_access'):
        raise ValueError('Owner access is not configured on this service')
    configured = {}
    if args.options_file:
        if args.options_file.stat().st_size > 65536:
            raise ValueError('Options file exceeds the 64 KB limit')
        configured = json.loads(args.options_file.read_text(encoding='utf-8-sig'))
        if not isinstance(configured, dict) or set(configured) - (set(COMPILERS) | {'common'}):
            raise ValueError('Options file must map compiler names to argument lists, with an optional common object')
    common = configured.pop('common', {})
    if not isinstance(common, dict) or set(common) - {'optimization', 'bounds_check', 'backtrace', 'images'}:
        raise ValueError('common must be an object with optimization, bounds_check, backtrace, and/or images settings')
    if 'images' in common and (type(common['images']) is not int or common['images'] not in (1, 2, 4)):
        raise ValueError('common.images must be 1, 2, or 4')
    if args.images is not None:
        common['images'] = args.images
    images = common.pop('images', None)
    if 'optimization' in common and (type(common['optimization']) is not int or common['optimization'] not in range(4)):
        raise ValueError('common.optimization must be an integer from 0 through 3')
    for key in ('bounds_check', 'backtrace'):
        if key in common and type(common[key]) is not bool:
            raise ValueError(f'common.{key} must be a boolean')
    for key in ('optimization', 'bounds_check', 'backtrace'):
        value = getattr(args, key)
        if value is not None:
            common[key] = value
    if args.options_file:
        for compiler, arguments in configured.items():
            if (not isinstance(arguments, list) or len(arguments) > 32 or
                    any(not isinstance(arg, str) or not arg or len(arg) > 128 for arg in arguments)):
                raise ValueError(f'{compiler}: options file entries must be lists of at most 32 short argument strings')
    result = {}
    for compiler in compilers:
        if compiler not in session.get('compilers', ['gfortran']):
            raise ValueError(f'{compiler} is unavailable on this service')
        spec = session.get('compiler_options', {}).get(compiler, {})
        if args.preset != 'default' and args.preset not in spec.get('presets', {}):
            raise ValueError(f'{compiler} does not support preset {args.preset}')
        if args.standard != 'default' and args.standard not in spec.get('standards', {}):
            raise ValueError(f'{compiler} does not support standard {args.standard}')
        options = {'preset': args.preset} if spec else {}
        if args.standard != 'default':
            options['standard'] = args.standard
        if images is not None:
            if str(images) not in spec.get('coarray_images', {}):
                raise ValueError(f'{compiler} does not support {images} coarray images on this service')
            options['images'] = images
            if spec.get('coarray_note') and notes is not None:
                notes.append(f'Note: {compiler}: {spec["coarray_note"]}')
        for key in ('warnings', 'fast_math', 'preprocess'):
            if getattr(args, key):
                if key not in spec.get('extras', {}):
                    raise ValueError(f'{compiler} does not support {key}')
                options[key] = True
        extra = portable_arguments(spec, common, compiler, notes) + configured.get(compiler, [])
        try:
            flags = effective_flags(spec, options, extra)
            levels = spec.get('portable_options', {}).get('optimization', {})
            if common.get('optimization') == 0 and levels.get('0') == []:
                for choice in levels.values():
                    if choice and any(flags[index:index + len(choice)] == choice for index in range(len(flags))):
                        raise ValueError('Conflicting optimization options: default mode and ' + ' '.join(choice))
        except ValueError as error:
            raise ValueError(f'{compiler}: {error}') from error
        if extra:
            options['additional'] = extra
        result[compiler] = options
    return result


def effective_flags(spec, options, additional=None):
    flags = list(spec.get('presets', {}).get(options.get('preset', 'default'), []))
    flags += spec.get('standards', {}).get(options.get('standard', 'default'), [])
    if 'images' in options:
        flags += spec.get('coarray_images', {}).get(str(options['images']), [])
    for key in ('warnings', 'fast_math', 'preprocess'):
        if options.get(key):
            flags += spec.get('extras', {}).get(key, [])
    return additional_flags(spec, flags, options.get('additional', []) if additional is None else additional)


def print_result(compiler, result, sections, elapsed, *, terse=False):
    print(f'\n=== {compiler}: {"PASS" if result["ok"] else "FAIL"} ===', flush=True)
    if not terse and result.get('compiler_version'):
        print(result['compiler_version'], flush=True)
    for key, title in [('build', 'Syntax check' if result.get('interpreter') else 'Compilation'),
                       ('execution', 'Program output')]:
        stage = result.get(key)
        if not stage:
            continue
        seconds = stage.get('seconds')
        timing = f'{seconds:.3f}' if seconds is not None else '-'
        if not terse:
            print(f'{title} ({timing}):', flush=True)
        for stream in ('stdout', 'stderr'):
            text = stage.get(stream, '')
            if terse and key == 'build' and stage.get('ok') and stream == 'stdout':
                # Suppress wrapper build chatter; preserve compiler diagnostics, including warnings.
                text = ''.join(line for line in text.splitlines(keepends=True)
                               if not line.startswith('Build:'))
            if text:
                print(text, end='' if text.endswith('\n') else '\n',
                      file=sys.stderr if stream == 'stderr' else sys.stdout, flush=True)
        if key == 'build':
            for location in diagnostic_locations(stage.get('stdout', '') + '\n' + stage.get('stderr', ''), sections):
                print('Source location: ' + location, flush=True)
    if result.get('error'):
        print('Error: ' + str(result['error']), file=sys.stderr, flush=True)
    if not terse:
        print(f'Total client time: {elapsed:.3f}', flush=True)


def positive_seconds(value):
    number = float(value)
    if not 0 < number <= 3600:
        raise argparse.ArgumentTypeError('Use a timeout greater than zero and at most 3600 seconds')
    return number


def print_summary(rows):
    if rows:
        print('\nSummary: times in seconds')
        print(f'  {"Compiler":10} {"Result":6} {"Total":>9} {"Compile":>9} {"Run":>9} {"Other":>9}')
        for compiler, ok, elapsed, compile_seconds, run_seconds, other_seconds in rows:
            compile_time = f'{compile_seconds:.3f}' if compile_seconds is not None else '-'
            run_time = f'{run_seconds:.3f}' if run_seconds is not None else '-'
            other_time = f'{other_seconds:.3f}' if other_seconds is not None else '-'
            print(f'  {compiler:10} {"PASS" if ok else "FAIL":6} {elapsed:9.3f} '
                  f'{compile_time:>9} {run_time:>9} {other_time:>9}')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', type=Path, nargs='+', help='UTF-8 free-form sources, in compilation order')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--compiler', choices=COMPILERS, help='Compiler (default: gfortran)')
    group.add_argument('--compilers', choices=COMPILERS, nargs='+', help='Compilers to invoke sequentially')
    parser.add_argument('--compile-only', action='store_true', help='Compile without execution (syntax check for ofort)')
    parser.add_argument('--fail-fast', action='store_true', help='Stop after the first compilation or execution failure')
    parser.add_argument('--terse', action='store_true', help='Show program output, diagnostics, and the final summary only')
    parser.add_argument('--list', action='store_true', help='Print the exact submitted source once, including with --terse')
    parser.add_argument('--owner', action='store_true', help='Use private owner access; read P2F_OWNER_KEY or prompt without echo')
    parser.add_argument('--images', type=int, choices=(1, 2, 4), help='Enable coarrays with an image count verified by the service')
    parser.add_argument('--options-file', type=Path, help='JSON file mapping compiler names to additional argument lists')
    parser.add_argument('--optimization', '--O', '-O', type=int, choices=range(4), default=None,
                        help='Portable optimization level (0-3); overrides common.optimization in the options file')
    parser.add_argument('--bounds-check', action=argparse.BooleanOptionalAction, default=None,
                        help='Request bounds checks using the selected compilers\' advertised flags')
    parser.add_argument('--backtrace', action=argparse.BooleanOptionalAction, default=None,
                        help='Request runtime backtraces using the selected compilers\' advertised flags')
    parser.add_argument('--standard', default='default', help='Language standard year, or default')
    parser.add_argument('--preset', default='default', choices=('default', 'debug', 'optimized', 'strict'))
    parser.add_argument('--warnings', action='store_true')
    parser.add_argument('--fast-math', action='store_true')
    parser.add_argument('--preprocess', action='store_true', help='Enable preprocessing for the combined source')
    parser.add_argument('--service-url', help='HTTPS service origin; defaults to site/service.json beside this script')
    parser.add_argument('--origin', default=DEFAULT_ORIGIN, help='Frontend origin permitted by your service')
    parser.add_argument('--timeout', type=positive_seconds, default=300, help='Total seconds per compiler, including polling')
    args = parser.parse_args(argv)
    rows = []
    try:
        source, sections = combine_sources(args.files)
        service_url = args.service_url or json.loads((ROOT / 'site/service.json').read_text(encoding='utf-8'))['url']
        owner_key = ''
        if args.owner:
            try:
                owner_key = os.environ.get('P2F_OWNER_KEY') or getpass.getpass('Owner key: ')
            except EOFError as error:
                raise ValueError('Owner key input unavailable; set P2F_OWNER_KEY in your environment') from error
            if not 32 <= len(owner_key) <= 256:
                raise ValueError('Owner key must contain 32 to 256 characters')
        client = PlaygroundClient(service_url, args.origin, owner_key=owner_key)
        compilers = args.compilers or [args.compiler or 'gfortran']
        session = client.connect()
        notes = []
        options = selections(session, compilers, args, notes)
        if not args.terse:
            print(f'Service: {client.service_url}\nCombined source: {len(source.encode("utf-8"))} bytes', flush=True)
            if len(sections) > 1:
                for section in sections:
                    print(f'  input_p.f90 lines {section.first_line}-{section.last_line}: {section.filename}', flush=True)
            print('Times in seconds.', flush=True)
        if args.list:
            print('\n=== Submitted source ===', flush=True)
            print(source, end='', flush=True)
            print('=== End submitted source ===', flush=True)
        for note in notes:
            print(note, flush=True)
        for compiler in compilers:
            if not args.terse:
                version = session.get('compiler_versions', {}).get(compiler) or 'version unavailable'
                print(f'\nSubmitting {compiler} ({version})...', flush=True)
                flags = effective_flags(session.get('compiler_options', {}).get(compiler, {}), options[compiler])
                print('User-code options: ' + (' '.join(flags) or '(compiler default)'), flush=True)
            result, elapsed = client.run_job(source, compiler, options[compiler],
                                             compile_only=args.compile_only, timeout=args.timeout)
            print_result(compiler, result, sections, elapsed, terse=args.terse)
            build = result.get('build') or {}
            execution = result.get('execution') or {}
            compile_seconds = build.get('seconds')
            run_seconds = execution.get('seconds')
            compile_skipped = compiler == 'ofort' and not args.compile_only and not build
            run_skipped = not execution and (args.compile_only or build.get('ok') is False)
            other_seconds = None
            if (compile_seconds is not None or compile_skipped) and (run_seconds is not None or run_skipped):
                other_seconds = elapsed - (compile_seconds or 0) - (run_seconds or 0)
            rows.append((compiler, result['ok'], elapsed, compile_seconds, run_seconds, other_seconds))
            if args.fail_fast and not result['ok']:
                print('Stopping after failure (--fail-fast); remaining compilers were not submitted.', flush=True)
                break
    except KeyboardInterrupt:
        print('\nInterrupted; cancellation requested for any known pending job.', file=sys.stderr)
        print_summary(rows)
        return 130
    except (OSError, ValueError, KeyError, ServiceError) as error:
        print(f'Error: {error}\nStopping; remaining compilers were not submitted.', file=sys.stderr)
        print_summary(rows)
        return 2
    print_summary(rows)
    return 0 if all(row[1] for row in rows) else 1


if __name__ == '__main__':
    sys.exit(main())
