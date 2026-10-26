"""Build the independent FPM sandbox image, then deploy its separate API."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


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
    print('Set the deployed API URL in site/fpm/service.json, then publish the static site.')


if __name__ == '__main__':
    main()
