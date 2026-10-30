"""Serve a local Fortran editor using installed compilers. No hosted services.

python xfortran_serve.py --workspace C:\\fortran\\test
Use an Intel developer terminal if ifx needs its compiler environment initialized.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
import re
from pathlib import Path
import secrets
import shutil
import tempfile
import threading
import time
from urllib.parse import parse_qs, urlsplit
import webbrowser

from xfortran_run import COMPILERS, SUFFIXES, UnsupportedOption, compare, discover, flags_for, run_process

ASSETS = Path(__file__).resolve().parent / 'local_site'
HOSTED_ASSETS = Path(__file__).resolve().parent / 'site'
MAX_BODY = 16 * 1024 * 1024


def catalog_page():
    """Use the hosted markup and assets, changing only local execution labels."""
    text = (HOSTED_ASSETS / 'fpm/index.html').read_text(encoding='utf-8')
    text = text.replace('<html lang="en">', '<html lang="en" data-execution="local">')
    text = text.replace('<title>FPM package playground</title>', '<title>Local FPM playground</title>')
    text = text.replace('FORTRAN PACKAGES &middot; EXPERIMENTAL', 'LOCAL FORTRAN PACKAGES')
    text = text.replace('<h1>FPM package playground</h1>', '<h1>Local FPM playground</h1>\n'
        '<p><a id="local-source-link" href="/">Local source-file playground</a> &middot; '
        '<a id="local-projects-link" href="/fpm/projects/">Local FPM projects</a></p>\n'
        '<p>Compile and run with your installed FPM and compilers. Programs run with your permissions. '
        'GitHub sources download into a fresh temporary project for each submission.</p>')
    text = text.replace('Selected packages (GNU Fortran 16)', 'Selected packages (build locally)')
    text = text.replace('Choose a precompiled package&hellip;', 'Choose a package&hellip;')
    text = text.replace('href="../gams/"', 'href="https://beliavsky.github.io/fortran-playground/gams/"')
    text = text.replace("connect-src 'self' https://*.modal.run", "connect-src 'self'")
    for name in ('style.css', 'editor-vendor/codemirror.css'):
        text = text.replace('href="../' + name + '"', 'href="ui/' + name + '"')
    text = text.replace('href="fpm.css"', 'href="ui/fpm/fpm.css"')
    text = text.replace('src="fpm.mjs"', 'src="ui/fpm/fpm.mjs"')
    return re.sub(r'<footer>.*?</footer>', '<footer><p>All compilation and execution use your computer. '
        'No hosted jobs or usage quotas apply. Each submission builds from scratch; package source files '
        'and builds in existing local projects are untouched. Install the native libraries listed in the '
        'catalog build notes when required. Use Local FPM projects to work with packages already on disk '
        'or compare installed compilers.</p></footer>', text, flags=re.S)


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, workspace, port=8766, overrides=None, fpm_path=None):
        self.workspace = Path(workspace).resolve(strict=True)
        if not self.workspace.is_dir():
            raise ValueError('Workspace must be a directory')
        self.overrides = overrides or {}
        self.compilers = discover(self.overrides)
        self.fpm_path = shutil.which(fpm_path or 'fpm')
        self.token = secrets.token_urlsafe(32)
        self.jobs = {}
        self.lock = threading.Lock()
        super().__init__(('127.0.0.1', port), Handler)
        self.origin = f'http://127.0.0.1:{self.server_port}'

    def workspace_path(self, value):
        if not isinstance(value, str) or not value or '\0' in value or ':' in value or '\\' in value:
            raise ValueError('Use a workspace-relative path with forward slashes')
        relative = Path(value)
        if relative.is_absolute() or '..' in relative.parts or relative.suffix.lower() not in SUFFIXES:
            raise ValueError('Source must be a Fortran file within the workspace')
        path = (self.workspace / relative).resolve()
        if not path.is_relative_to(self.workspace):
            raise ValueError('Source must be a Fortran file within the workspace')
        return path

    def file_list(self):
        import os
        files, visited = [], set()
        for directory, folders, names in os.walk(self.workspace, followlinks=False):
            resolved = Path(directory).resolve()
            if resolved in visited:
                folders.clear()
                continue
            visited.add(resolved)
            folders[:] = [name for name in folders if not name.startswith('.') and name not in ('node_modules', '__pycache__')
                          and not (Path(directory) / name).is_symlink()
                          and (Path(directory) / name).resolve().is_relative_to(self.workspace)]
            for name in names:
                path = Path(directory) / name
                if path.suffix.lower() in SUFFIXES and path.resolve().is_relative_to(self.workspace):
                    files.append(path.relative_to(self.workspace).as_posix())
        return sorted(files, key=str.lower)

    def submit(self, data):
        if not isinstance(data, dict) or set(data) - {'sources', 'compilers', 'settings', 'extras', 'stdin', 'compile_only', 'fail_fast', 'compile_timeout', 'run_timeout'}:
            raise ValueError('Invalid job request')
        sources, names = data.get('sources'), data.get('compilers')
        if not isinstance(sources, list) or not sources or not isinstance(names, list) or not names:
            raise ValueError('Select at least one source and compiler')
        if any(not isinstance(name, str) or name not in COMPILERS or not self.compilers[name].get('path') for name in names) or len(set(names)) != len(names):
            raise ValueError('Choose available compilers without duplicates')
        seen = set()
        for source in sources:
            if not isinstance(source, dict) or set(source) != {'path', 'source'} or not isinstance(source['source'], str) or not source['source'].strip() or '\0' in source['source']:
                raise ValueError('Each source needs a nonempty UTF-8 source string and a relative path')
            path = self.workspace_path(source['path'])
            if path in seen:
                raise ValueError('Duplicate source file')
            seen.add(path)
        settings, extras = data.get('settings', {}), data.get('extras', {})
        if not isinstance(extras, dict) or set(extras) - set(COMPILERS):
            raise ValueError('Invalid compiler options')
        for name in names:
            try:
                flags_for(name, settings, extras.get(name))
            except UnsupportedOption:
                pass
        for key in ('compile_only', 'fail_fast'):
            if type(data.get(key, False)) is not bool:
                raise ValueError(f'{key} must be a boolean')
        if not isinstance(data.get('stdin', ''), str) or (data.get('stdin') and data.get('compile_only')):
            raise ValueError('Standard input is only available when running')
        for key, default in [('compile_timeout', 120), ('run_timeout', 30)]:
            value = data.get(key, default)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError('Timeouts must be finite nonnegative seconds (0 means unlimited)')
        with self.lock:
            if any(job['state'] == 'running' for job in self.jobs.values()):
                return None
            for identifier in list(self.jobs)[:-19]:
                self.jobs.pop(identifier)
            identifier = secrets.token_urlsafe(16)
            job = {'state': 'running', 'rows': [], 'cancel': threading.Event()}
            self.jobs[identifier] = job

        def work():
            def update(row):
                with self.lock:
                    job['rows'] = [item for item in job['rows'] if item['compiler'] != row['compiler']] + [row]
            try:
                with tempfile.TemporaryDirectory(prefix='fortran_sources_') as temporary:
                    root, paths, include_dirs = Path(temporary), [], []
                    for source in sources:
                        path = root / source['path']
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(source['source'], encoding='utf-8')
                        paths.append(path)
                        include_dirs.append(self.workspace_path(source['path']).parent)
                    rows = compare(paths, names, settings=settings, extras=extras, overrides=self.overrides,
                        versions={name: item.get('version', '') for name, item in self.compilers.items()},
                        cancel=job['cancel'], fail_fast=data.get('fail_fast', False), update=update,
                        compile_only=data.get('compile_only', False), stdin=data.get('stdin', ''), cwd=self.workspace,
                        compile_timeout=data.get('compile_timeout', 120), run_timeout=data.get('run_timeout', 30),
                        include_dirs=[self.workspace, *include_dirs])
                with self.lock:
                    job['rows'] = rows
            except Exception as error:
                with self.lock:
                    job['error'] = str(error)
                    completed = {row['compiler']: row for row in job['rows'] if row['status'] not in ('QUEUED', 'RUNNING')}
                    job['rows'] = [completed.get(name) or {'compiler': name, 'status': 'ERROR', 'ok': False,
                                                         'error': str(error)} for name in names]
            finally:
                with self.lock:
                    job['state'] = 'done'

        job['thread'] = threading.Thread(target=work, daemon=True)
        job['thread'].start()
        return identifier

    def stop_jobs(self):
        with self.lock:
            jobs = list(self.jobs.values())
            for job in jobs:
                job['cancel'].set()
        for job in jobs:
            thread = job.get('thread')
            if thread and thread.is_alive():
                thread.join(timeout=8)

    def project_path(self, value):
        from fortran_fpm import project_directory
        if not isinstance(value, str) or not value or '\0' in value or ':' in value or '\\' in value:
            raise ValueError('Use a workspace-relative package directory with forward slashes')
        relative = Path(value)
        path = (self.workspace / relative).resolve()
        if relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(self.workspace):
            raise ValueError('Package directory must remain within the workspace')
        return project_directory(path)

    def project_list(self):
        import os
        projects = []
        for count, (directory, folders, files) in enumerate(os.walk(self.workspace, followlinks=False)):
            if count >= 10000 or len(projects) >= 256:
                break
            folders[:] = [name for name in folders if not name.startswith('.') and name not in ('build', 'node_modules', '__pycache__')]
            path = Path(directory).resolve()
            if not path.is_relative_to(self.workspace):
                folders.clear()
                continue
            if 'fpm.toml' in files:
                projects.append(path.relative_to(self.workspace).as_posix())
        return sorted(projects, key=str.lower)

    def submit_fpm(self, data):
        from fortran_fpm import COMPILERS as FPM_COMPILERS, compare_projects, validate_options
        if not isinstance(data, dict) or set(data) - {'project', 'compilers', 'options'}:
            raise ValueError('Invalid FPM job request')
        project = self.project_path(data.get('project'))
        names = data.get('compilers')
        if not isinstance(names, list) or not names or any(not isinstance(name, str) or name not in FPM_COMPILERS or not self.compilers[name].get('path') for name in names) or len(set(names)) != len(names):
            raise ValueError('Choose distinct available FPM compilers')
        options = validate_options(data.get('options', {}))
        if not self.fpm_path:
            raise ValueError('fpm is not on PATH; restart the server with --fpm-path PATH')
        with self.lock:
            if any(job['state'] == 'running' for job in self.jobs.values()):
                return None
            for identifier in list(self.jobs)[:-19]:
                self.jobs.pop(identifier)
            identifier = secrets.token_urlsafe(16)
            job = {'state': 'running', 'rows': [], 'cancel': threading.Event()}
            self.jobs[identifier] = job

        def work():
            def update(row):
                with self.lock:
                    job['rows'] = [item for item in job['rows'] if item['compiler'] != row['compiler']] + [row]
            try:
                rows = compare_projects(project, names, options=options, overrides=self.overrides,
                                        fpm_path=self.fpm_path, cancel=job['cancel'], update=update)
                with self.lock:
                    job['rows'] = rows
            except Exception as error:
                with self.lock:
                    job['error'] = str(error)
                    job['rows'] = [{'compiler': name, 'status': 'ERROR', 'ok': False, 'error': str(error)} for name in names]
            finally:
                with self.lock:
                    job['state'] = 'done'
        job['thread'] = threading.Thread(target=work, daemon=True)
        job['thread'].start()
        return identifier

    def source_tool(self, action, data):
        if not isinstance(data, dict) or set(data) - {'path', 'source', 'indent'}:
            raise ValueError('Invalid editor tool request')
        source = data.get('source')
        if not isinstance(source, str) or not source.strip() or '\0' in source:
            raise ValueError('Enter Fortran source first')
        path = self.workspace_path(data.get('path'))
        indent = data.get('indent', 3)
        if type(indent) is not int or indent not in (2, 3, 4):
            raise ValueError('Indentation must be 2, 3, or 4 spaces')
        name = 'fprettify' if action == 'format' else 'fortitude'
        executable = shutil.which(name)
        if not executable:
            raise ValueError(f'{name} was not found on PATH. Initialize its environment and restart the local server.')
        with tempfile.TemporaryDirectory(prefix='fortran_tools_') as temporary:
            snapshot = Path(temporary) / path.name
            snapshot.write_text(source, encoding='utf-8')
            arguments = (['-i', str(indent), '--stdout', str(snapshot)] if action == 'format' else
                         ['check', '--no-fix', '--no-fix-only', '--no-unsafe-fixes', '--output-format', 'json', str(snapshot)])
            stage = run_process([executable, *arguments], temporary, threading.Event(), timeout=30, output_limit=MAX_BODY)
        result = {'ok': False, 'seconds': stage['seconds'], 'stderr': stage['stderr']}
        if action == 'format':
            if stage['ok'] and stage['stdout'].strip() and not stage['stderr'].strip():
                result.update(ok=True, formatted_source=stage['stdout'])
            else:
                result['error'] = stage['stderr'] or 'fprettify returned no formatted source'
        else:
            try:
                findings = json.loads(stage['stdout'])
                if stage.get('exit_code') not in (0, 1) or stage.get('timed_out') or not isinstance(findings, list):
                    raise ValueError('Fortitude did not return a successful check result')
                diagnostics = [{'line': item['location']['row'], 'column': item['location']['column'],
                                'code': item['code'], 'message': item['message']} for item in findings]
                result.update(ok=True, diagnostics=diagnostics)
            except (ValueError, KeyError, TypeError):
                result['error'] = stage['stderr'] or 'Fortitude returned invalid diagnostics'
        return result

    def submit_catalog(self, data):
        from local_fpm_catalog import validate_local_request, execute_catalog
        request = validate_local_request(data)
        if not self.fpm_path or not self.compilers[request['compiler']].get('path'):
            raise ValueError('Choose an installed compiler and install FPM before submitting')
        with self.lock:
            if any(job['state'] == 'running' for job in self.jobs.values()):
                return None
            for identifier in list(self.jobs)[:-19]:
                self.jobs.pop(identifier)
            identifier = secrets.token_urlsafe(16)
            job = {'state': 'running', 'cancel': threading.Event()}
            self.jobs[identifier] = job

        def work():
            try:
                result = execute_catalog(self.workspace, request, overrides=self.overrides,
                                         fpm_path=self.fpm_path, cancel=job['cancel'])
            except Exception as error:
                result = {'ok': False, 'error': str(error), 'stages': [], 'local': True}
            with self.lock:
                job.update(result=result, state='done')
        job['thread'] = threading.Thread(target=work, daemon=True)
        job['thread'].start()
        return identifier


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, status, value, content_type='application/json; charset=utf-8'):
        body = json.dumps(value).encode('utf-8') if isinstance(value, (dict, list)) else value
        self.send_response(status)
        # CodeMirror measures and positions editor elements with inline styles.
        for key, value in {'Content-Type': content_type, 'Content-Length': str(len(body)), 'Cache-Control': 'no-store',
            'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer',
            'Content-Security-Policy': "default-src 'self'; script-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"}.items():
            self.send_header(key, value)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def allowed(self, api=False, post=False):
        if self.headers.get('Host') != self.server.origin.removeprefix('http://'):
            self.reply(403, {'error': 'Unexpected Host'}); return False
        origin = self.headers.get('Origin')
        if (origin and origin != self.server.origin) or (post and origin != self.server.origin):
            self.reply(403, {'error': 'Unrelated websites cannot access the local compiler service'}); return False
        if api and not secrets.compare_digest(self.headers.get('X-Local-Token', '').encode('utf-8'), self.server.token.encode('ascii')):
            self.reply(403, {'error': 'Open the full local URL printed by the server, including its session fragment'}); return False
        return True

    def do_GET(self):
        parsed = urlsplit(self.path)
        api = parsed.path.startswith('/api/')
        if not self.allowed(api):
            return
        try:
            if parsed.path == '/api/session':
                self.reply(200, {'workspace': str(self.server.workspace), 'compilers': self.server.compilers})
            elif parsed.path == '/api/fpm/session':
                from fortran_fpm import COMPILERS as FPM_COMPILERS
                self.reply(200, {'workspace': str(self.server.workspace), 'fpm': self.server.fpm_path,
                    'projects': self.server.project_list(),
                    'compilers': {name: value for name, value in self.server.compilers.items() if name in FPM_COMPILERS}})
            elif parsed.path == '/api/fpm/catalog/health':
                from local_fpm_catalog import health
                self.reply(200, health(self.server))
            elif parsed.path == '/api/files':
                self.reply(200, {'files': self.server.file_list()})
            elif parsed.path == '/api/source':
                path = self.server.workspace_path(parse_qs(parsed.query).get('path', [''])[0])
                if path.stat().st_size > MAX_BODY:
                    raise ValueError('Source is larger than the 16 MiB editor request limit')
                self.reply(200, {'source': path.read_text(encoding='utf-8-sig')})
            elif parsed.path.startswith(('/api/jobs/', '/api/fpm/catalog/jobs/')):
                identifier = parsed.path.rsplit('/', 1)[-1]
                with self.server.lock:
                    job = self.server.jobs.get(identifier)
                    value = {key: job[key] for key in ('state', 'rows', 'result', 'error') if key in job} if job else None
                self.reply(200 if value else 404, value or {'error': 'Unknown job'})
            elif parsed.path in ('/fpm/', '/fpm/index.html'):
                self.reply(200, catalog_page().encode('utf-8'), 'text/html; charset=utf-8')
            elif parsed.path in ('/fpm/projects/', '/fpm/projects/index.html'):
                self.reply(200, (ASSETS / 'fpm/index.html').read_bytes(), 'text/html; charset=utf-8')
            elif parsed.path in ('/fpm/projects.mjs', '/fpm/fpm.mjs'):
                self.reply(200, (ASSETS / 'fpm/fpm.mjs').read_bytes(), 'text/javascript; charset=utf-8')
            elif parsed.path in ('/fpm/examples.json', '/fpm/packages.json', '/fpm/all-packages.json', '/fpm/translated-r.json', '/fpm/project-runtime.json'):
                self.reply(200, (HOSTED_ASSETS / parsed.path[1:]).read_bytes())
            elif parsed.path.startswith('/fpm/ui/'):
                name = parsed.path.removeprefix('/fpm/ui/')
                allowed = {'style.css', 'plots.mjs', 'editors.mjs', 'indentation.mjs', 'service_config.mjs', 'config.mjs',
                           'state_links.mjs', 'external_source.mjs',
                           'fpm/fpm.mjs', 'fpm/project_export.mjs', 'fpm/gams_classes.mjs', 'fpm/fpm.css',
                           'editor-vendor/codemirror.js', 'editor-vendor/fortran.js', 'editor-vendor/codemirror.css'}
                if name not in allowed:
                    self.reply(404, {'error': 'Not found'})
                else:
                    assets = ASSETS if name.startswith('editor-vendor/') else HOSTED_ASSETS
                    self.reply(200, (assets / name).read_bytes(),
                        'text/css; charset=utf-8' if name.endswith('.css') else 'text/javascript; charset=utf-8')
            elif parsed.path in ('/', '/index.html', '/app.mjs', '/style.css', '/view_controls.css', '/view_controls.mjs', '/editors.mjs', '/indentation.mjs',
                                 '/output_diff.mjs', '/output_diff_ui.mjs', '/plots.mjs',
                                 '/editor-vendor/codemirror.js', '/editor-vendor/fortran.js',
                                 '/editor-vendor/codemirror.css', '/editor-vendor/LICENSE'):
                name = 'index.html' if parsed.path == '/' else 'fpm/index.html' if parsed.path == '/fpm/' else parsed.path[1:]
                self.reply(200, (ASSETS / name).read_bytes(), {'html': 'text/html; charset=utf-8', 'mjs': 'text/javascript; charset=utf-8',
                    'js': 'text/javascript; charset=utf-8', 'css': 'text/css; charset=utf-8'}.get(name.rsplit('.', 1)[-1], 'text/plain; charset=utf-8'))
            else:
                self.reply(404, {'error': 'Not found'})
        except (ValueError, OSError) as error:
            self.reply(400, {'error': str(error)})

    def do_POST(self):
        if not self.allowed(api=True, post=True):
            return
        try:
            if self.headers.get('Transfer-Encoding') or self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                raise ValueError('Use JSON with a Content-Length')
            length = int(self.headers.get('Content-Length', '-1'))
            if not 0 <= length <= MAX_BODY:
                raise ValueError('Request must fit the 16 MiB editor request limit')
            data = json.loads(self.rfile.read(length))
            path = urlsplit(self.path).path
            if path in ('/api/format', '/api/check'):
                self.reply(200, self.server.source_tool(path.removeprefix('/api/'), data))
            elif path == '/api/jobs':
                identifier = self.server.submit(data)
                self.reply(202 if identifier else 409, {'id': identifier} if identifier else {'error': 'A local comparison is already active'})
            elif path == '/api/fpm/jobs':
                identifier = self.server.submit_fpm(data)
                self.reply(202 if identifier else 409, {'id': identifier} if identifier else {'error': 'A local job is already active'})
            elif path == '/api/fpm/catalog/jobs':
                identifier = self.server.submit_catalog(data)
                self.reply(202 if identifier else 409, {'id': identifier} if identifier else {'error': 'A local job is already active'})
            elif path.startswith(('/api/jobs/', '/api/fpm/catalog/jobs/')) and path.endswith('/cancel'):
                identifier = path.rsplit('/', 2)[-2]
                with self.server.lock:
                    job = self.server.jobs.get(identifier)
                    if job:
                        job['cancel'].set()
                self.reply(200 if job else 404, {'cancelled': bool(job)})
            else:
                self.reply(404, {'error': 'Not found'})
        except (ValueError, OSError) as error:
            self.reply(400, {'error': str(error)})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path.cwd())
    parser.add_argument('--port', type=int, default=8766, help='Loopback port; 0 selects a free port')
    parser.add_argument('--compiler-path', action='append', default=[], metavar='COMPILER=PATH')
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--fpm', action='store_true', help='Open the local FPM package page')
    parser.add_argument('--fpm-projects', action='store_true', help='Open the directory-based Local FPM projects page')
    parser.add_argument('--fpm-path', help='FPM executable override')
    args = parser.parse_args(argv)
    overrides = {}
    for item in args.compiler_path:
        name, separator, value = item.partition('=')
        if not separator or name not in COMPILERS or not value:
            parser.error('Use --compiler-path COMPILER=PATH')
        overrides[name] = value
    try:
        server = LocalServer(args.workspace, args.port, overrides, fpm_path=args.fpm_path)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    page = '/fpm/projects/' if args.fpm_projects else '/fpm/' if args.fpm else '/'
    url = server.origin + page + '#session=' + server.token
    print(f'Local Fortran workspace: {server.workspace}\nOpen {url}\nPrograms run with your permissions. Press Ctrl+C to stop.', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stop_jobs()
        server.server_close()


if __name__ == '__main__':
    main()
