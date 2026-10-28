"""Operator-only adapters for pinned catalog builds; never used for visitor URLs.

The ordinary preparer and its limits remain authoritative. Explicit catalog
recipes may map registry names to locked Git sources, use audited GitHub mirrors,
enable selected compiler metapackages, and render manifest version placeholders.
"""
import hashlib
from pathlib import Path
import re
import shutil
import tomllib

from fpm_sources import Preparer, github_repository, extract_archive, MAX_PACKAGES, MAX_EXPANDED

ROOT = Path(__file__).resolve().parent
LEGACY_ADAPTER_SHA256 = '2406f4594114fb2a8304dc9005cfb4e595bfcf02439ea97707e2826b89c02133'
SOURCE_ADAPTER_SHA256 = 'fd73ab30a27bb1299e6630ac45976aec59e1c123d56881471a0cb2065cc97bbc'
NAME_ADAPTER_SHA256 = 'e69f1678e4f5c0963a1794ac1fa804522972481e75f9e530400bd3eec8e92c32'


def adapter_digest():
    return hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def validate_build(package):
    options = package.get('catalog_build', {})
    if not options:
        return options
    allowed = {'adapter_sha256', 'apt_packages', 'environment', 'registry', 'git_aliases',
               'metapackages', 'manifest_versions', 'manifest_names', 'source_revisions', 'source_packages', 'shared_dependencies'}
    if (set(options) - allowed or options.get('adapter_sha256') not in {adapter_digest(), LEGACY_ADAPTER_SHA256, SOURCE_ADAPTER_SHA256, NAME_ADAPTER_SHA256}
            or (options.get('source_packages') and options.get('adapter_sha256') == LEGACY_ADAPTER_SHA256)
            or (options.get('manifest_names') and options.get('adapter_sha256') not in {adapter_digest(), NAME_ADAPTER_SHA256})):
        raise ValueError('Refresh the catalog build adapter checksum: ' + package['id'])
    shared = options.get('shared_dependencies')
    if shared:
        if (options.get('adapter_sha256') != adapter_digest()
                or set(shared) != {'adapter_sha256', 'repositories'}
                or not re.fullmatch('[a-f0-9]{64}', shared.get('adapter_sha256', ''))
                or not isinstance(shared['repositories'], list) or not 1 <= len(shared['repositories']) <= 12
                or len(set(shared['repositories'])) != len(shared['repositories'])):
            raise ValueError('Invalid shared dependency recipe.')
        for repo in shared['repositories']:
            github_repository('https://github.com/' + repo)
    for repo, name in options.get('manifest_names', {}).items():
        github_repository('https://github.com/' + repo)
        if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_-]*', name):
            raise ValueError('Invalid catalog manifest name.')
    for repo, spec in options.get('source_packages', {}).items():
        github_repository('https://github.com/' + repo)
        if (set(spec) != {'manifest', 'sources'} or not isinstance(spec['manifest'], str)
                or len(spec['manifest'].encode()) > 16000 or not isinstance(spec['sources'], list)
                or not 1 <= len(spec['sources']) <= 500):
            raise ValueError('Invalid catalog source package.')
        from pathlib import PurePosixPath
        names = set()
        for source in spec['sources']:
            path = PurePosixPath(source)
            if (path.is_absolute() or '..' in path.parts or '\\' in source or ':' in source
                    or path.suffix.lower() not in {'.f', '.f90', '.f95', '.for'} or path.name in names):
                raise ValueError('Catalog library sources must be distinct relative Fortran files.')
            names.add(path.name)
        manifest = tomllib.loads(spec['manifest'])
        if manifest.get('library', {}).get('source-dir') != 'playground-library':
            raise ValueError('Catalog source package must use playground-library.')
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
        source_package = self.options.get('source_packages', {}).get(repo.lower())
        if source_package:
            return self.source_package(repo, revision, source_package, development=development)
        return super().repository(url, revision, development=development)

    def source_package(self, repo, revision, spec, *, development=False):
        """Wrap an explicitly locked non-FPM repository without changing its sources.

        This operator-only path retains the ordinary downloader/archive/graph limits.
        Only listed files enter the library; upstream programs and objects stay out.
        """
        pin = self.pins.get(repo.lower()) if self.pins is not None else None
        if not pin or not re.fullmatch('[a-f0-9]{40}', pin['revision']):
            raise ValueError('Catalog source packages require an exact archive lock.')
        if re.fullmatch('[a-f0-9]{40}', revision) and revision != pin['revision']:
            raise ValueError('Catalog source package revision conflicts with its lock.')
        key = (repo.lower(), pin['revision'])
        if key in self.repositories:
            root = self.repositories[key]
            self.manifest(root, development=development)
            return root
        if len(self.records) >= MAX_PACKAGES:
            raise ValueError('Dependency graph exceeds 12 repositories.')
        data = self.download(f"https://codeload.github.com/{repo}/tar.gz/{pin['revision']}")
        digest = hashlib.sha256(data).hexdigest()
        if digest != pin['sha256']:
            raise ValueError('Catalog source package archive checksum mismatch.')
        root = extract_archive(data, self.directory / 'packages' / str(len(self.records)),
                               require_manifest=False).resolve()
        if (root / 'fpm.toml').exists() or (root / 'playground-library').exists():
            raise ValueError('Catalog source package must not overwrite upstream files.')
        library = root / 'playground-library'
        library.mkdir()
        for source in spec['sources']:
            path = (root / source).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError('Missing catalog library source: ' + source)
            shutil.copyfile(path, library / path.name)
        (root / 'fpm.toml').write_text(spec['manifest'], encoding='utf-8')
        paths = list(self.directory.rglob('*'))
        if len(paths) > 20000 or sum(p.stat().st_size for p in paths if p.is_file()) > MAX_EXPANDED:
            raise ValueError('Combined dependency sources exceed 64 MiB / 20000 entries.')
        self.repositories[key] = root
        self.records.append({'repository': repo, 'revision': pin['revision'], 'sha256': digest})
        shutil.rmtree(root / 'build', ignore_errors=True)
        (root / 'fpm.lock').unlink(missing_ok=True)
        self.manifest(root, development=development)
        return root

    def manifest(self, root, *, development=False):
        root = root.resolve()
        if (root, development) in self.prepared or (root, True) in self.prepared:
            return
        path = root / 'fpm.toml'
        text = path.read_text(encoding='utf-8')
        if len(text.encode()) > 1000000:
            raise ValueError('Package manifest is too large.')
        manifest = tomllib.loads(text)
        containing = next((repo for (repo, _), directory in self.repositories.items()
                           if root == directory), '')
        name = self.options.get('manifest_names', {}).get(containing)
        if name:
            # Operator-owned setting for a pinned root manifest only. Public
            # requests retain ordinary package-name validation.
            manifest['name'] = name
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
