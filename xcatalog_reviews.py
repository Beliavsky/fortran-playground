"""Refresh the saved independent reviews for selected FPM packages."""
import argparse
import json
from pathlib import Path
from urllib.request import HTTPRedirectHandler, Request, build_opener

from catalog_export import write_json
from catalog_reviews import FEED_URL, ROOT, SNAPSHOT, select_reviews

MAX_BYTES = 32 * 1024 * 1024


class HTTPSOnly(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        if not newurl.startswith('https://'):
            raise ValueError('Review feed redirects must use HTTPS.')
        return super().redirect_request(request, fp, code, message, headers, newurl)


def refresh(source, destination, packages):
    if source.startswith('https://'):
        with build_opener(HTTPSOnly()).open(Request(source, headers={
                'User-Agent': 'fortran-playground-catalog-reviews/1'}), timeout=30) as response:
            raw = response.read(MAX_BYTES + 1)
    elif '://' in source:
        raise ValueError('Use a local file or an HTTPS feed URL.')
    else:
        with Path(source).open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Independent-review feed exceeds 32 MiB.')
    result = select_reviews(json.loads(raw), packages)
    write_json(destination, result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feed', default=FEED_URL, help='Published HTTPS feed or local reviewed-metadata.json')
    parser.add_argument('--output', type=Path, default=ROOT / SNAPSHOT)
    args = parser.parse_args()
    try:
        packages = json.loads((ROOT / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
        result = refresh(args.feed, args.output, packages)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Review refresh failed; existing snapshot preserved: {error}\n')
    report = result['report']
    print(f"Matched {len(report['matched'])} packages; "
          f"{len(report['revision_mismatches'])} revision mismatches; "
          f"{len(report['no_independent_review'])} without independent reviews.")
    print('Saved', args.output)


if __name__ == '__main__':
    main()
