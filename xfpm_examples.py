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
    # Small local-export tools only; package archives are fetched by the user's
    # machine. This never builds libraries or contacts the execution service.
    root = audit.parents[1]
    runtime = {'run.py': (root / 'fpm_project_run.py').read_text(encoding='utf-8')}
    for name in ('fpm_sources.py', 'fpm_collections.py', 'fpm_targets.py', 'fpm_compilers.py', 'fpm_catalog_build.py',
                 'fpm_catalog_patches.py', 'fortran_plot.py'):
        runtime['tools/' + name] = (root / name).read_text(encoding='utf-8')
    from fortran_plot import module_source
    runtime['tools/pyplot_module.f90'] = module_source()
    runtime['tools/pyplot-LICENSE'] = (root / 'vendor/pyplot-fortran/LICENSE').read_text(encoding='utf-8')
    (site / 'fpm/project-runtime.json').write_text(json.dumps(runtime, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    generate_fpm_examples(Path(__file__).resolve().parent / 'site')
