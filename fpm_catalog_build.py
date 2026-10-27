"""Operator-only adapters for pinned catalog builds; never used for visitor URLs.

The ordinary preparer and its limits remain authoritative. Explicit catalog
recipes may map registry names to locked Git sources, use audited GitHub mirrors,
enable selected compiler metapackages, and render manifest version placeholders.
"""
import hashlib
from pathlib import Path
import re
import tomllib

from fpm_sources import Preparer, github_repository

ROOT = Path(__file__).resolve().parent


def adapter_digest():
    return hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def validate_build(package):
    options = package.get('catalog_build', {})
    if not options:
        return options
    allowed = {'adapter_sha256', 'apt_packages', 'environment', 'registry', 'git_aliases',
               'metapackages', 'manifest_versions', 'source_revisions'}
    if set(options) - allowed or options.get('adapter_sha256') != adapter_digest():
        raise ValueError('Refresh the catalog build adapter checksum: ' + package['id'])
    for value in options.get('apt_packages', []):
        if not re.fullmatch(r'[a-z0-9][a-z0-9+.-]*=[A-Za-z0-9:~+.-]+', value):
            raise ValueError('Catalog system packages must have exact versions.')
    environment = options.get('environment', {})
    if set(environment) - {'FPM_FFLAGS', 'FPM_LDFLAGS'} or any(
            not isinstance(v, str) or len(v) > 1000 or '\x00' in v for v in environment.values()):
        raise ValueError('Unsupported catalog compiler environment.')
    if set(options.get('metapackages', [])) - {'openmp', 'blas', 'lapack'}:
        raise ValueError('Unsupported catalog metapackage.')
    if 'openmp' in options.get('metapackages', []) and '-fopenmp' not in environment.get('FPM_FFLAGS', '').split():
        raise ValueError('OpenMP catalog builds require -fopenmp.')
    return options


def build_image(app, image, options):
    if options.get('apt_packages'):
        image = image.apt_install(*options['apt_packages'])
    if options.get('environment'):
        image = image.env(options['environment'])
    return image.build(app) if options else image


class CatalogPreparer(Preparer):
    def __init__(self, directory, *, options, **kwargs):
        super().__init__(directory, **kwargs)
        self.options = options

    def repository(self, url, revision='', *, development=False):
        # Exact aliases only, rather than accepting arbitrary hosts or redirects.
        normalized = url.rstrip('/').removesuffix('.git')
        url = self.options.get('git_aliases', {}).get(normalized, url)
        repo = github_repository(url)
        override = self.options.get('source_revisions', {}).get(repo.lower())
        if override:
            if revision and re.fullmatch('[a-f0-9]{40}', revision) and revision != override:
                raise ValueError('Catalog source override conflicts with an explicit upstream commit.')
            revision = override
        return super().repository(url, revision, development=development)

    def manifest(self, root, *, development=False):
        root = root.resolve()
        if (root, development) in self.prepared or (root, True) in self.prepared:
            return
        path = root / 'fpm.toml'
        text = path.read_text(encoding='utf-8')
        if len(text.encode()) > 1000000:
            raise ValueError('Package manifest is too large.')
        manifest = tomllib.loads(text)
        # Placeholder versions appear in release-generation templates upstream.
        if manifest.get('version') == 'VERSION':
            containing = next((repo for (repo, _), directory in self.repositories.items()
                               if root.is_relative_to(directory)), '')
            version = self.options.get('manifest_versions', {}).get(containing)
            if not version or not re.fullmatch(r'\d+\.\d+\.\d+(?:[-+][A-Za-z0-9.-]+)?', version):
                raise ValueError('Catalog manifest VERSION placeholder needs a recorded version.')
            manifest['version'] = version
        tables = [manifest.get('dependencies', {})]
        if development:
            tables.append(manifest.get('dev-dependencies', {}))
            for kind in ('test', 'executable', 'example'):
                tables.extend(t.get('dependencies', {}) for t in manifest.get(kind, []))
        for table in tables:
            if not isinstance(table, dict):
                raise ValueError('Invalid dependency table.')
            for name, spec in list(table.items()):
                if isinstance(spec, dict) and {'git', 'path'} & spec.keys():
                    continue
                key = name.lower()
                if key in self.options.get('metapackages', []) and spec == '*':
                    link = {'openmp': 'gomp', 'blas': 'blas', 'lapack': 'lapack'}[key]
                    links = manifest.setdefault('build', {}).setdefault('link', [])
                    if link not in links:
                        links.append(link)
                    del table[name]
                elif key in self.options.get('registry', {}) and isinstance(spec, str):
                    replacement = self.options['registry'][key]
                    if set(replacement) != {'git', 'rev'} or not re.fullmatch('[a-f0-9]{40}', replacement['rev']):
                        raise ValueError('Catalog registry mappings require exact Git commits.')
                    github_repository(replacement['git'])
                    table[name] = dict(replacement)
                else:
                    raise ValueError('Unmapped catalog dependency: ' + name)
        import tomli_w
        path.write_text(tomli_w.dumps(manifest), encoding='utf-8')
        return super().manifest(root, development=development)
