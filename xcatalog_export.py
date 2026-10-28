"""Export reusable Fortran software metadata without running compilers or contacting GitHub."""
import argparse
from pathlib import Path

from catalog_export import ROOT, publish_export


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'catalog-export')
    args = parser.parse_args()
    try:
        data = publish_export(args.output_dir)
    except (ValueError, OSError) as error:
        parser.exit(1, f'Catalog export failed: {error}\n')
    state = data['provenance']['source_commit'] or 'local/modified inputs; see provenance'
    print(f'Exported {len(data["projects"])} projects to {args.output_dir} ({state}).')


if __name__ == '__main__':
    main()
