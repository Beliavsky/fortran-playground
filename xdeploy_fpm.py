"""Build the independent FPM sandbox image, then deploy its separate API."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from urllib.request import Request, urlopen


def verify_api(url, origin):
    request = Request(url + '/api/health', headers={'Origin': origin})
    with urlopen(request, timeout=45) as response:
        data = json.loads(response.read(10000))
        if response.status != 200 or data.get('ok') is not True or data.get('fpm') != '0.12.0':
            raise ValueError('The deployed endpoint did not return a healthy FPM response.')
        if response.headers.get('Access-Control-Allow-Origin') != origin:
            raise ValueError('The deployed endpoint does not allow the configured browser origin.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner-secret', help='Optional Modal secret containing P2F_OWNER_KEY (API only).')
    parser.add_argument('--origins', help='Comma-separated allowed browser origins, for forks.')
    args = parser.parse_args()
    if args.owner_secret:
        os.environ['FPM_OWNER_SECRET'] = args.owner_secret
    if args.origins:
        os.environ['FPM_ORIGINS'] = args.origins
    import modal
    from xfpm_modal import APP_NAME, IMAGE_NAME, runtime_image
    with modal.enable_output():
        runtime_image.build(modal.App.lookup(APP_NAME, create_if_missing=True)).publish(IMAGE_NAME)
    subprocess.run([sys.executable, '-X', 'utf8', '-m', 'modal', 'deploy', 'xfpm_modal.py'],
                   cwd=Path(__file__).resolve().parent, check=True)
    url = modal.Function.from_name(APP_NAME, 'api').get_web_url()
    print('Execution API URL (use this, not the Modal dashboard URL):', url)
    print('Set site/fpm/service.json to:')
    print(json.dumps({'url': url}))
    print('Checking the deployed HTTP endpoint and browser access...', flush=True)
    origin = os.environ.get('FPM_ORIGINS', 'https://beliavsky.github.io').split(',')[0]
    try:
        verify_api(url, origin)
    except Exception as error:
        raise SystemExit(f'Deployment completed, but the API is not ready: {error}\n'
                         f'Inspect startup logs with: {sys.executable} -m modal app logs {APP_NAME}') from error
    print('HTTP health and browser access: PASS')
    print('Then commit the configuration and publish the static site.')


if __name__ == '__main__':
    main()
