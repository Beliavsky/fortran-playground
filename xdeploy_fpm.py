"""Build the independent FPM sandbox image, then deploy its separate API."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.request import Request, urlopen


def configure_routing(entries, directory=None):
    """Pass large private routing tables as an image file, not Windows env text."""
    routing = {name: {k: entry[k] for k in ('key', 'image', 'revision', 'records')}
               for name, entry in entries.items()}
    directory = Path(directory) if directory is not None else Path(__file__).resolve().parent / '.fpm-audit-cache'
    directory.mkdir(parents=True, exist_ok=True)
    path = (directory / 'deploy-routing.json').resolve()
    path.write_text(json.dumps(routing) + '\n', encoding='utf-8')
    os.environ.pop('FPM_PRECOMPILED', None)
    os.environ['FPM_PRECOMPILED_FILE'] = str(path)
    return path


def verify_api(url, origin, compilers=None, precompiled=None, *, translated_r=False, run_examples=False):
    request = Request(url + '/api/health', headers={'Origin': origin})
    with urlopen(request, timeout=45) as response:
        data = json.loads(response.read(65536))
        if response.status != 200 or data.get('ok') is not True or data.get('fpm') != '0.12.0':
            raise ValueError('The deployed endpoint did not return a healthy FPM response.')
        if response.headers.get('Access-Control-Allow-Origin') != origin:
            raise ValueError('The deployed endpoint does not allow the configured browser origin.')
        if compilers is not None and set(data.get('compilers', {})) != set(compilers):
            raise ValueError('The deployed compiler catalog does not match the verified images.')
        if precompiled is not None:
            expected = {name: {'revision': entry['revision'], 'compiler': 'gfortran'}
                        for name, entry in precompiled.items()}
            if data.get('precompiled', {}) != expected:
                raise ValueError('The deployed precompiled catalog does not match the verified images.')
        if translated_r and data.get('features', {}).get('translated_r') is not True:
            raise ValueError('The endpoint is still serving an older FPM API without translated R package support.')
        if run_examples and data.get('features', {}).get('run_examples') is not True:
            raise ValueError('The endpoint is still serving an older FPM API without Run examples support.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner-secret', help='Optional Modal secret containing P2F_OWNER_KEY (API only).')
    parser.add_argument('--origins', help='Comma-separated allowed browser origins, for forks.')
    parser.add_argument('--without-precompiled', action='store_true', help='Deploy only clean package builds.')
    from fpm_cache import catalog
    parser.add_argument('--packages', nargs='+', choices=[p['id'] for p in catalog()],
                        help='Process these IDs, retaining other verified packages; default: all. Matching builds are reused.')
    parser.add_argument('--reverify', action='store_true', help='Re-run changed-main checks, retaining compiled package libraries.')
    parser.add_argument('--rebuild', action='store_true', help='Force recompiling selected package libraries.')
    parser.add_argument('--compilers', nargs='+', choices=['gfortran', 'gfortran17', 'ifx', 'flang'],
                        default=['gfortran', 'gfortran17', 'ifx', 'flang'],
                        help='Toolchains to build and verify; GNU 16 is always included.')
    args = parser.parse_args()
    if args.owner_secret:
        os.environ['FPM_OWNER_SECRET'] = args.owner_secret
    if args.origins:
        os.environ['FPM_ORIGINS'] = args.origins
    import modal
    from xfpm_modal import APP_NAME, IMAGE_NAME, image_name, runtime_images
    from fpm_probe import verify_image
    compilers = list(dict.fromkeys(['gfortran', *args.compilers]))
    images = runtime_images(compilers)
    enabled = []
    build_app = modal.App.lookup(APP_NAME, create_if_missing=True)
    with modal.enable_output():
        for compiler in compilers:
            try:
                image = images[compiler].build(build_app)
                verify_image(build_app, image, compiler)
                image.publish(image_name(compiler))
                enabled.append(compiler)
                if compiler == 'gfortran' and not args.without_precompiled:
                    from xprecompile_fpm import build_catalog
                    precompiled = build_catalog(build_app, image, IMAGE_NAME, args.packages,
                                                reverify=args.reverify, rebuild=args.rebuild)
            except Exception as error:
                if compiler == 'gfortran':
                    raise
                print(f'WARNING: {compiler} remains unavailable: {error}', flush=True)
    os.environ['FPM_ENABLED_COMPILERS'] = json.dumps(enabled)
    configure_routing(precompiled if not args.without_precompiled else {})
    subprocess.run([sys.executable, '-X', 'utf8', '-m', 'modal', 'deploy', 'xfpm_modal.py'],
                   cwd=Path(__file__).resolve().parent, check=True)
    url = modal.Function.from_name(APP_NAME, 'api').get_web_url()
    print('Execution API URL (use this, not the Modal dashboard URL):', url)
    print('Set site/fpm/service.json to:')
    print(json.dumps({'url': url}))
    print('Checking the deployed HTTP endpoint and browser access...', flush=True)
    origin = os.environ.get('FPM_ORIGINS', 'https://beliavsky.github.io').split(',')[0]
    try:
        verify_api(url, origin, enabled, precompiled if not args.without_precompiled else {}, translated_r=True, run_examples=True)
    except Exception as error:
        raise SystemExit(f'Deployment completed, but the API is not ready: {error}\n'
                         f'Inspect startup logs with: {sys.executable} -m modal app logs {APP_NAME}') from error
    print('HTTP health and browser access: PASS')
    print('Verified FPM compilers:', ', '.join(enabled))
    print('Then commit the configuration and publish the static site.')


if __name__ == '__main__':
    main()
