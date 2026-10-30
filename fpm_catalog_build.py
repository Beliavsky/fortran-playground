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

from fpm_sources import Preparer, github_repository, extract_archive, MAX_PACKAGES, MAX_EXPANDED, validate_request

ROOT = Path(__file__).resolve().parent
LEGACY_ADAPTER_SHA256 = '2406f4594114fb2a8304dc9005cfb4e595bfcf02439ea97707e2826b89c02133'
SOURCE_ADAPTER_SHA256 = 'fd73ab30a27bb1299e6630ac45976aec59e1c123d56881471a0cb2065cc97bbc'
NAME_ADAPTER_SHA256 = 'e69f1678e4f5c0963a1794ac1fa804522972481e75f9e530400bd3eec8e92c32'
FORTRAN_SOURCE_ADAPTER_SHA256 = '073bc7a78272acc47c93133034888bc644eda85592c9af0becfe53dad87b82c8'
C_SOURCE_ADAPTER_SHA256 = '66e8249cbc0eb57ffecf9f04801ede2060312d64ba2fa2d839b07fdc746f5f8c'
MPI_ADAPTER_SHA256 = '57d6ae25c7ae46d94a499cb7947261010bb800c7c531caf90592e85a5445505d'
FYPP_ADAPTER_SHA256 = 'e27e15d511b0c7a6071e422dd426d023680f5754df7dc8f53326fdb29a4a5927'

GENERATED_SOURCE_ADAPTER_SHA256 = 'e34f911192ec7459f4becd43da08a8df4dd8a5fd89707941f2cbffc607e82c25'
CPP_SOURCE_ADAPTER_SHA256 = '63a30c28b5a3f5fc5c4e3a88bdb65c171bdde90b0999773c0d9bad5115f57d90'
UPPERCASE_FYPP_ADAPTER_SHA256 = '3bd5fbb173561ecf82a9a62c5e896c26236f10bef6d0d5ba0a9813d186fa6a30'
SOURCE_LIMIT_ADAPTER_SHA256 = '6c8aeaa3de63975428f8d302160907d0fa752820f913fc17c60cab133eaca72d'
SHORT_ROOT_ADAPTER_SHA256 = '5afc6d43de793d71797e00b1038d1cbf915f7bf3cb8a43a22b3a4d6e283974c6'
SOURCE_ALLOWANCE_ADAPTER_SHA256 = '54d4595c11c37b6d2e9435fb4746268e31610c6e8ac3367ad3538366583ac0eb'
MAX_CATALOG_SOURCES = 1000

def adapter_digest():
    return hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def validate_build(package):
    options = package.get('catalog_build', {})
    if not options:
        return options
    allowed = {'adapter_sha256', 'apt_packages', 'environment', 'registry', 'git_aliases',
               'metapackages', 'manifest_versions', 'manifest_names', 'source_revisions', 'source_packages', 'shared_dependencies', 'source_limit'}
    if (set(options) - allowed or options.get('adapter_sha256') not in {adapter_digest(), LEGACY_ADAPTER_SHA256, SOURCE_ADAPTER_SHA256, NAME_ADAPTER_SHA256, FORTRAN_SOURCE_ADAPTER_SHA256, C_SOURCE_ADAPTER_SHA256, MPI_ADAPTER_SHA256, FYPP_ADAPTER_SHA256, GENERATED_SOURCE_ADAPTER_SHA256, CPP_SOURCE_ADAPTER_SHA256, UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256}
            or (options.get('source_packages') and options.get('adapter_sha256') == LEGACY_ADAPTER_SHA256)
            or (options.get('manifest_names') and options.get('adapter_sha256') not in {adapter_digest(), NAME_ADAPTER_SHA256, FORTRAN_SOURCE_ADAPTER_SHA256, C_SOURCE_ADAPTER_SHA256, MPI_ADAPTER_SHA256, FYPP_ADAPTER_SHA256, GENERATED_SOURCE_ADAPTER_SHA256, CPP_SOURCE_ADAPTER_SHA256, UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256})):
        raise ValueError('Refresh the catalog build adapter checksum: ' + package['id'])
    if 'source_limit' in options:
        from fpm_catalog_limits import source_limit
        if options['adapter_sha256'] not in {adapter_digest(), SOURCE_ALLOWANCE_ADAPTER_SHA256}:
            raise ValueError('Source allowance requires the current catalog adapter.')
        source_limit(package)
    shared = options.get('shared_dependencies')
    if shared:
        if (options.get('adapter_sha256') not in {adapter_digest(), FORTRAN_SOURCE_ADAPTER_SHA256, C_SOURCE_ADAPTER_SHA256, MPI_ADAPTER_SHA256, FYPP_ADAPTER_SHA256, GENERATED_SOURCE_ADAPTER_SHA256, CPP_SOURCE_ADAPTER_SHA256, UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256}
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
        # Existing recipes retain their original validation policy and cache keys.
        source_limit = MAX_CATALOG_SOURCES if options['adapter_sha256'] in {adapter_digest(), SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256} else 500
        if (set(spec) - {'manifest', 'sources', 'fypp', 'generated', 'short_root'} or not {'manifest', 'sources'} <= set(spec) or not isinstance(spec['manifest'], str)
                or len(spec['manifest'].encode()) > 16000 or not isinstance(spec['sources'], list)
                or not 1 <= len(spec['sources']) <= source_limit):
            raise ValueError('Invalid catalog source package.')
        if 'short_root' in spec and (options['adapter_sha256'] not in {adapter_digest(), SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256}
                                     or not isinstance(spec['short_root'], bool)):
            raise ValueError('Short catalog paths require the current operator adapter.')
        from pathlib import PurePosixPath
        names = set()
        suffixes = {'.f', '.f90', '.f95', '.for'}
        if options.get('adapter_sha256') in {adapter_digest(), C_SOURCE_ADAPTER_SHA256, MPI_ADAPTER_SHA256, FYPP_ADAPTER_SHA256, GENERATED_SOURCE_ADAPTER_SHA256, CPP_SOURCE_ADAPTER_SHA256, UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256}:
            suffixes.add('.c')
        if options.get('adapter_sha256') in {adapter_digest(), CPP_SOURCE_ADAPTER_SHA256, UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256}:
            suffixes.update({'.cc', '.cpp', '.cxx'})
        generated = spec.get('generated')
        if generated is not None:
            if (options.get('adapter_sha256') not in {adapter_digest(), GENERATED_SOURCE_ADAPTER_SHA256, CPP_SOURCE_ADAPTER_SHA256, UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256} or not isinstance(generated, dict)
                    or set(generated) != {'asset', 'sha256'}
                    or not re.fullmatch(r'[a-z0-9-]+\.json', generated.get('asset', ''))
                    or not re.fullmatch('[a-f0-9]{64}', generated.get('sha256', ''))):
                raise ValueError('Catalog generated files require a locked operator asset.')
        generator = spec.get('fypp')
        if generator is not None:
            if (options.get('adapter_sha256') not in {adapter_digest(), FYPP_ADAPTER_SHA256, GENERATED_SOURCE_ADAPTER_SHA256, CPP_SOURCE_ADAPTER_SHA256, UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256} or not isinstance(generator, dict)
                    or set(generator) != {'version', 'outputs'} or generator['version'] != '3.2'
                    or not isinstance(generator['outputs'], dict)
                    or set(generator['outputs']) != {s for s in spec['sources'] if s.endswith('.fpp') or (options.get('adapter_sha256') in {adapter_digest(), UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256} and s.endswith('.F'))}
                    or not generator['outputs']
                    or any(not isinstance(v, str) or not re.fullmatch('[a-f0-9]{64}', v)
                           for v in generator['outputs'].values())):
                raise ValueError('Catalog Fypp sources require version 3.2 and exact output checksums.')
            suffixes.add('.fpp')
        for source in spec['sources']:
            path = PurePosixPath(source)
            target = (path.with_suffix('.f90').name if source in spec.get('fypp', {}).get('outputs', {}) else
                      path.with_suffix('.cpp').name if path.suffix.lower() in {'.cc', '.cxx'} else path.name)
            if (path.is_absolute() or '..' in path.parts or '\\' in source or ':' in source
                    or path.suffix.lower() not in suffixes or target in names):
                raise ValueError('Catalog library sources must be distinct relative Fortran or supported C files.')
            names.add(target)
        manifest = tomllib.loads(spec['manifest'])
        if manifest.get('library', {}).get('source-dir') != 'playground-library':
            raise ValueError('Catalog source package must use playground-library.')
    for value in options.get('apt_packages', []):
        if not re.fullmatch(r'[a-z0-9][a-z0-9+.-]*=[A-Za-z0-9:~+.-]+', value):
            raise ValueError('Catalog system packages must have exact versions.')
    environment = options.get('environment', {})
    if 'FPM_CXXFLAGS' in environment and (options['adapter_sha256'] != adapter_digest()
            or not options.get('source_packages') or options.get('shared_dependencies')):
        raise ValueError('C++ flags require a current, unshared catalog source package.')
    if set(environment) - {'FPM_FFLAGS', 'FPM_LDFLAGS', 'FPM_CXXFLAGS', 'UCX_TLS'} or any(
            not isinstance(v, str) or len(v) > 1000 or '\x00' in v for v in environment.values()):
        raise ValueError('Unsupported catalog compiler environment.')
    # Operator-owned MPI images may use only local UCX transports. Keep this
    # opt-in scoped to new recipes; public requests cannot set image variables.
    if 'UCX_TLS' in environment and (options.get('adapter_sha256') not in {adapter_digest(), MPI_ADAPTER_SHA256, FYPP_ADAPTER_SHA256, GENERATED_SOURCE_ADAPTER_SHA256, CPP_SOURCE_ADAPTER_SHA256, UPPERCASE_FYPP_ADAPTER_SHA256, SOURCE_LIMIT_ADAPTER_SHA256, SHORT_ROOT_ADAPTER_SHA256, SOURCE_ALLOWANCE_ADAPTER_SHA256}
                                    or environment['UCX_TLS'] != 'self,sm'):
        raise ValueError('Catalog UCX transport must be self,sm under the current adapter.')
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


def install_generated(spec, root, repository, revision):
    """Copy audited generated text; never execute a source repository's build."""
    import json
    from pathlib import PurePosixPath
    settings = spec.get('generated')
    if not settings:
        return
    data = (ROOT/'fpm_catalog/generated'/settings['asset']).read_bytes()
    if len(data) > 2*1024*1024 or hashlib.sha256(data).hexdigest() != settings['sha256']:
        raise ValueError('Catalog generated asset checksum mismatch.')
    asset = json.loads(data)
    if (asset.get('schema') != 1 or asset.get('repository', '').lower() != repository.lower()
            or asset.get('revision') != revision or not 1 <= len(asset.get('files', {})) <= 500):
        raise ValueError('Catalog generated asset does not match its source lock.')
    def path_for(name):
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
            raise ValueError('Generated asset path leaves its source tree.')
        target = (root/name).resolve()
        if not target.is_relative_to(root.resolve()):
            raise ValueError('Generated asset path leaves its source tree.')
        return target
    for name, digest in asset.get('inputs', {}).items():
        data = path_for(name).read_bytes().replace(b'\r\n', b'\n')
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('Generated asset input checksum mismatch: '+name)
    for name, text in asset['files'].items():
        target = path_for(name)
        if target.suffix.lower() not in {'.inc', '.f90', '.h', '.cc', '.cpp', '.cxx'} or not isinstance(text, str):
            raise ValueError('Generated assets must be supported sources or include files.')
        data = text.encode('utf-8')
        if len(data) > 1024*1024 or target.exists():
            raise ValueError('Generated asset must not overwrite upstream files.')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


class CatalogPreparer(Preparer):
    def __init__(self, directory, *, options, **kwargs):
        super().__init__(directory, **kwargs)
        self.options = options
        from fpm_catalog_limits import preparer_limit
        self.max_expanded = preparer_limit(options, self.pins.values() if self.pins is not None else None)

    def prepare(self, payload):
        if self.max_expanded == MAX_EXPANDED:
            return super().prepare(payload)
        payload = validate_request(payload)
        root = self.repository(payload['url'], payload['revision'], development=payload['workflow'] == 'package')
        self.check_source_size()
        return root.relative_to(self.directory).as_posix(), self.records

    def check_source_size(self):
        paths = list(self.directory.rglob('*'))
        if len(paths) > 20000 or sum(p.stat().st_size for p in paths if p.is_file()) > self.max_expanded:
            raise ValueError(f'Combined dependency sources exceed {self.max_expanded // (1024*1024)} MiB / 20000 entries.')

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
        if spec.get('short_root') and root.name != 'p':
            # FPM flattens source paths into object names. Large libraries can
            # exceed Linux's single-argument limit when ar runs via /bin/sh -c.
            # Only the extracted container directory changes, never its contents.
            short = (root.parent / 'p').resolve()
            area = self.directory.resolve()
            if not root.is_relative_to(area) or not short.is_relative_to(area) or short.exists():
                raise ValueError('Short catalog source path must stay inside its staging area.')
            root = root.rename(short)
        install_generated(spec, root, repo, pin['revision'])
        library = root / 'playground-library'
        library.mkdir()
        for source in spec['sources']:
            path = (root / source).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError('Missing catalog library source: ' + source)
            if source in spec.get('fypp', {}).get('outputs', {}):
                # Only checksum-locked, operator-reviewed recipes reach this
                # generator. Public repository preparation never invokes Fypp.
                import importlib.metadata
                try:
                    version = importlib.metadata.version('fypp')
                except importlib.metadata.PackageNotFoundError:
                    raise ValueError('Install the catalog generator: python -m pip install fypp==3.2') from None
                if version != spec['fypp']['version']:
                    raise ValueError('Catalog generation requires fypp==3.2.')
                import fypp
                target = library / path.with_suffix('.f90').name
                fypp.Fypp().process_file(str(path), str(target))
                text = target.read_text(encoding='utf-8')
                if source.endswith('.F'):
                    # Canonicalize simple USE lists emitted from unordered Fypp sets.
                    text = re.sub(r'(?im)^([ \t]*USE \w+, ONLY: )((?:[\w ,\t]|&\n)+)$',
                                  lambda m: m[1] + ', '.join(sorted(v.strip() for v in m[2].replace('&\n', '').split(','))), text)
                target.write_bytes(text.encode('utf-8'))
                if hashlib.sha256(target.read_bytes()).hexdigest() != spec['fypp']['outputs'][source]:
                    raise ValueError('Catalog generated source checksum mismatch: ' + source)
            else:
                # FPM 0.12 discovers .cpp but ignores .cc/.cxx. Preserve the
                # original source tree and stage C++ wrappers under .cpp names.
                target = path.with_suffix('.cpp').name if path.suffix.lower() in {'.cc', '.cxx'} else path.name
                shutil.copyfile(path, library / target)
        (root / 'fpm.toml').write_text(spec['manifest'], encoding='utf-8')
        self.check_source_size()
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
