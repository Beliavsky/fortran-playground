"""Build the FPM page's starter catalog from the audited source programs."""
import json
from pathlib import Path


def generate_fpm_examples(site):
    audit = Path(__file__).resolve().parent / 'docs/fpm-feasibility'
    packages = json.loads((audit / 'packages.lock.json').read_text(encoding='utf-8'))
    examples = [{key: package[key] for key in ('name', 'repository', 'revision', 'category')} |
                {'source': (audit / 'demos' / (package['name'] + '.f90')).read_text(encoding='utf-8')}
                for package in packages]
    path = site / 'fpm/examples.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(examples, indent=2) + '\n', encoding='utf-8')
    from fpm_cache import catalog
    packages = [{**package, 'source': (audit.parents[1] / 'fpm_catalog/demos' /
                 (package['id'] + '.f90')).read_text(encoding='utf-8')} for package in catalog()]
    (site / 'fpm/packages.json').write_text(json.dumps(packages, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    generate_fpm_examples(Path(__file__).resolve().parent / 'site')
