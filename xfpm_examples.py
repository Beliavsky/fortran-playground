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
    topics_path = audit.parents[1] / 'fpm_catalog/topics.json'
    topics = json.loads(topics_path.read_text(encoding='utf-8'))['repositories'] if topics_path.exists() else {}
    from xpackage_topics import playground_topics
    curated = playground_topics(audit.parents[1])
    from xpackage_gams import gams_data, package_classes, subclass_module
    gams = gams_data(audit.parents[1])
    (site / 'fpm/gams_classes.mjs').write_text(subclass_module(gams), encoding='utf-8')
    packages = [{**package, 'source': (audit.parents[1] / 'fpm_catalog/demos' /
                 (package['id'] + '.f90')).read_text(encoding='utf-8'),
                 'topics': topics.get(package['repository'].lower(), {}).get('topics', []),
                 'playground_topics': curated[package['id']],
                 'gams': package_classes(gams, package['id']),
                 **{key: value for key, value in topics.get(package['repository'].lower(), {}).items()
                    if key in ('stars', 'stars_updated_at')}} for package in catalog()]
    (site / 'fpm/packages.json').write_text(json.dumps(packages, indent=2) + '\n', encoding='utf-8')
    # Discovery metadata is refreshed explicitly, never during builds/deploys.
    discovery = json.loads((audit.parents[1] / 'fpm_catalog/all-packages.json').read_text(encoding='utf-8'))
    selected = {p['repository'].lower(): p for p in packages}
    combined = {}
    for entry in discovery['packages']:
        key = entry['repository'].lower()
        pinned = selected.get(key, {})
        combined[key] = {**entry, **pinned, 'fpm_status': 'available' if pinned else entry['fpm_status'],
                         'categories': sorted(set(entry['categories'] + ([pinned['category']] if pinned else [])))}
    for key, entry in selected.items():
        combined.setdefault(key, {**entry, 'fpm_status': 'available', 'categories': [entry['category']]})
    audit_path = audit.parents[1] / 'docs/fpm-discovery-audit.json'
    if audit_path.exists():
        report = json.loads(audit_path.read_text(encoding='utf-8'))
        labels = {'build_pass': 'build passed', 'missing_library_or_module': 'missing external library or module',
                  'preprocessing_required': 'preprocessing required', 'implicit_interface_error': 'implicit-interface compilation error',
                  'platform_specific_source': 'platform-specific source error', 'missing_source': 'missing source file',
                  'unsupported_dependency': 'unsupported dependency', 'preparation_failure': 'source preparation failed',
                  'service_limit': 'service limit exceeded', 'build_failure': 'compilation failed'}
        for result in report['packages']:
            entry = combined.get(result['repository'].lower())
            if entry is not None:
                entry['audit'] = {'revision': result['revision'], 'tested_at': report['tested_at'],
                                  'outcome': result['outcome'], 'summary': labels[result['outcome']]}
        for verification in report.get('fix_verifications', []):
            entry = combined.get(verification['repository'].lower())
            if entry is not None and entry.get('audit'):
                entry['audit']['verification'] = verification
    (site / 'fpm/all-packages.json').write_text(json.dumps(
        sorted(combined.values(), key=lambda p: p['repository'].lower()), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
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
