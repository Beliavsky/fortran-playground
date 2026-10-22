"""Compile and run ordered Fortran source files through the hosted playground API."""
import argparse
from dataclasses import dataclass
import json
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
COMPILERS = ('gfortran', 'ifx', 'flang', 'lfortran', 'ofort')


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
    def __init__(self, service_url, origin=DEFAULT_ORIGIN):
        self.service_url = origin_url(service_url)
        self.origin = origin_url(origin, https_only=False)
        self.token = ''

    def request(self, path, payload=None, *, timeout=30):
        headers = {'Origin': self.origin, 'User-Agent': 'fortran-playground-python-client'}
        if self.token:
            headers['X-P2F-Token'] = self.token
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


def selections(session, compilers, args):
    """Validate every compiler before spending any job allowance."""
    if len(set(compilers)) != len(compilers):
        raise ValueError('List each compiler only once')
    if args.compile_only and not session.get('features', {}).get('compile_only'):
        raise ValueError('This service does not advertise compile-only jobs')
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
        for key in ('warnings', 'fast_math', 'preprocess'):
            if getattr(args, key):
                if key not in spec.get('extras', {}):
                    raise ValueError(f'{compiler} does not support {key}')
                options[key] = True
        result[compiler] = options
    return result


def print_result(compiler, result, sections, elapsed):
    print(f'\n=== {compiler}: {"PASS" if result["ok"] else "FAIL"} ===', flush=True)
    if result.get('compiler_version'):
        print(result['compiler_version'], flush=True)
    for key, title in [('build', 'Syntax check' if result.get('interpreter') else 'Compilation'),
                       ('execution', 'Program output')]:
        stage = result.get(key)
        if not stage:
            continue
        print(f'{title} ({stage.get("seconds", 0):.3f} s):', flush=True)
        for stream in ('stdout', 'stderr'):
            text = stage.get(stream, '')
            if text:
                print(text, end='' if text.endswith('\n') else '\n',
                      file=sys.stderr if stream == 'stderr' else sys.stdout, flush=True)
        if key == 'build':
            for location in diagnostic_locations(stage.get('stdout', '') + '\n' + stage.get('stderr', ''), sections):
                print('Source location: ' + location, flush=True)
    if result.get('error'):
        print('Error: ' + str(result['error']), file=sys.stderr, flush=True)
    print(f'Total client time: {elapsed:.3f} s', flush=True)


def positive_seconds(value):
    number = float(value)
    if not 0 < number <= 3600:
        raise argparse.ArgumentTypeError('Use a timeout greater than zero and at most 3600 seconds')
    return number


def print_summary(rows):
    if rows:
        print('\nSummary:')
        for compiler, ok, elapsed in rows:
            print(f'  {compiler:10} {"PASS" if ok else "FAIL":4} {elapsed:.3f} s')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', type=Path, nargs='+', help='UTF-8 free-form sources, in compilation order')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--compiler', choices=COMPILERS, help='Compiler (default: gfortran)')
    group.add_argument('--compilers', choices=COMPILERS, nargs='+', help='Compilers to invoke sequentially')
    parser.add_argument('--compile-only', action='store_true', help='Compile without execution (syntax check for ofort)')
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
        client = PlaygroundClient(service_url, args.origin)
        compilers = args.compilers or [args.compiler or 'gfortran']
        session = client.connect()
        options = selections(session, compilers, args)
        print(f'Service: {client.service_url}\nCombined source: {len(source.encode("utf-8"))} bytes', flush=True)
        if len(sections) > 1:
            for section in sections:
                print(f'  input_p.f90 lines {section.first_line}-{section.last_line}: {section.filename}', flush=True)
        for compiler in compilers:
            version = session.get('compiler_versions', {}).get(compiler) or 'version unavailable'
            print(f'\nSubmitting {compiler} ({version})...', flush=True)
            result, elapsed = client.run_job(source, compiler, options[compiler],
                                             compile_only=args.compile_only, timeout=args.timeout)
            print_result(compiler, result, sections, elapsed)
            rows.append((compiler, result['ok'], elapsed))
    except KeyboardInterrupt:
        print('\nInterrupted; cancellation requested for any known pending job.', file=sys.stderr)
        print_summary(rows)
        return 130
    except (OSError, ValueError, KeyError, ServiceError) as error:
        print(f'Error: {error}\nStopping; remaining compilers were not submitted.', file=sys.stderr)
        print_summary(rows)
        return 2
    print_summary(rows)
    return 0 if all(ok for _, ok, _ in rows) else 1


if __name__ == '__main__':
    sys.exit(main())
