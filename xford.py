"""Generate cached FORD documentation from a local directory or public GitHub repo."""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import webbrowser
from ford_docs import generate, github_documentation


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='Local source directory or https://github.com/OWNER/REPO')
    parser.add_argument('--revision', default='')
    parser.add_argument('--subdirectory', default='')
    parser.add_argument('--cache', type=Path, default=Path('.fpm-audit-cache/ford'))
    parser.add_argument('--serve', action='store_true', help='Open documentation in your browser; Ctrl+C stops serving')
    args = parser.parse_args()
    if args.source.startswith('https://'):
        result = github_documentation(dict(url=args.source, revision=args.revision, subdirectory=args.subdirectory), args.cache)
    else:
        source = Path(args.source).resolve()
        selected = (source / args.subdirectory).resolve()
        if not selected.is_relative_to(source): parser.error('Package directory leaves source root')
        result = generate(selected, args.cache, repository=str(source), directory=args.subdirectory)
    destination = args.cache.resolve() / result['key']
    print(json.dumps(result, indent=2))
    print('Documentation:', destination / 'index.html')
    print('Download:', destination / 'documentation.zip')
    if args.serve:
        class Handler(SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header('Content-Security-Policy', "sandbox allow-scripts allow-forms; default-src 'self' 'unsafe-inline' data:; connect-src 'none'; form-action 'self'")
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('Access-Control-Allow-Origin', '*')
                super().end_headers()
        with ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(destination))) as server:
            url = f'http://127.0.0.1:{server.server_port}/'
            print(url, flush=True)
            webbrowser.open(url)
            try: server.serve_forever()
            except KeyboardInterrupt: pass


if __name__ == '__main__': main()
