"""Import a playground feed into a separate catalog, preserving catalog-owned fields."""
import argparse
import json
from pathlib import Path
from urllib.request import urlopen

from catalog_export import merge_catalog, write_json


def read_feed(source):
    if source.startswith('https://'):
        with urlopen(source, timeout=30) as response:
            content = response.read(16 * 1024 * 1024 + 1)
        if len(content) > 16 * 1024 * 1024:
            raise ValueError('Catalog feed exceeds 16 MiB.')
        return json.loads(content.decode('utf-8'))
    if '://' in source:
        raise ValueError('Use an HTTPS feed URL or a local JSON file.')
    return json.loads(Path(source).read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feed', required=True, help='HTTPS export URL or local catalog-v1.json')
    parser.add_argument('--catalog', type=Path, required=True, help='Existing layered catalog, or path to create')
    parser.add_argument('--output', type=Path, help='Defaults to updating --catalog atomically')
    args = parser.parse_args()
    try:
        feed = read_feed(args.feed)
        catalog = json.loads(args.catalog.read_text(encoding='utf-8')) if args.catalog.exists() else {
            'schema_version': 1, 'sources': {}, 'projects': []}
        merged = merge_catalog(catalog, feed)
        write_json(args.output or args.catalog, merged)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Catalog import failed; existing catalog preserved: {error}\n')
    print(f'Imported {len(feed["projects"])} projects; catalog now has {len(merged["projects"])} projects.')


if __name__ == '__main__':
    main()
