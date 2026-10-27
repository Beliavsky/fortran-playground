"""Catalog adapters must stay explicit, locked and isolated from public requests."""
import hashlib
import json
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest.mock import Mock

from fpm_cache import cache_identity
from fpm_catalog_build import CatalogPreparer, adapter_digest, validate_build, build_image
from fpm_sources import Preparer, validate_request
from test_fpm_service import archive, PAYLOAD


class CatalogBuildTests(unittest.TestCase):
    def options(self, **values):
        return {'adapter_sha256': adapter_digest(), **values}

    def test_environment_and_adapter_only_invalidate_opted_in_package(self):
        package = {'id': 'x', 'repository': 'owner/x', 'revision': 'a'*40, 'archive_sha256': 'b'*64}
        old = cache_identity(package, 'recipe')
        self.assertEqual(old, cache_identity({**package, 'catalog_build': {}}, 'recipe'))
        selected = {**package, 'catalog_build': self.options(apt_packages=['libblas-dev=3.12.1-6'])}
        self.assertNotEqual(old, cache_identity(selected, 'recipe'))
        selected['catalog_build']['apt_packages'] = ['libblas-dev=3.12.1-7']
        self.assertNotEqual(cache_identity(selected, 'recipe'), cache_identity(
            {**package, 'catalog_build': self.options(apt_packages=['libblas-dev=3.12.1-6'])}, 'recipe'))

    def test_system_dependencies_are_exact_and_environment_is_restricted(self):
        for options in (self.options(apt_packages=['libblas-dev']),
                        self.options(environment={'PATH': '/attacker'}),
                        self.options(metapackages=['openmp']),
                        {'adapter_sha256': 'outdated'}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                validate_build({'id': 'x', 'catalog_build': options})
        options = self.options(apt_packages=['libblas-dev=3.12.1-6'],
                               metapackages=['openmp'], environment={'FPM_FFLAGS': '-fopenmp'})
        validate_build({'id': 'x', 'catalog_build': options})
        image = Mock()
        image.apt_install.return_value = image
        image.env.return_value = image
        build_image('app', image, options)
        image.apt_install.assert_called_once_with('libblas-dev=3.12.1-6')
        image.env.assert_called_once_with({'FPM_FFLAGS': '-fopenmp'})

    def test_registry_mapping_and_openmp_are_resolved_before_offline_build(self):
        root = archive({'fpm.toml': 'name="library"\n[dependencies]\nhelper="*"\nopenmp="*"\n'})
        helper = archive({'fpm.toml': 'name="helper"'})
        pins = [{'repository': 'example/library', 'revision': 'a'*40, 'sha256': hashlib.sha256(root).hexdigest()},
                {'repository': 'example/helper', 'revision': 'b'*40, 'sha256': hashlib.sha256(helper).hexdigest()}]
        options = self.options(registry={'helper': {'git': 'https://github.com/example/helper', 'rev': 'b'*40}},
                               metapackages=['openmp'], environment={'FPM_FFLAGS': '-fopenmp'})
        urls = []
        def download(url, **kwargs):
            urls.append(url)
            return helper if '/example/helper/' in url else root
        with tempfile.TemporaryDirectory() as temporary:
            path, records = CatalogPreparer(temporary, pins=pins, options=options, downloader=download).prepare(PAYLOAD)
            manifest = tomllib.loads((Path(temporary)/path/'fpm.toml').read_text())
            self.assertNotIn('openmp', manifest['dependencies'])
            self.assertEqual(manifest['build']['link'], ['gomp'])
            self.assertEqual(set(manifest['dependencies']['helper']), {'path'})
            self.assertEqual([p['revision'] for p in records], ['a'*40, 'b'*40])
            self.assertFalse(any('/commits/' in url for url in urls))
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError, 'registry'):
            Preparer(temporary, downloader=download).prepare({**PAYLOAD, 'revision': 'a'*40})
        with self.assertRaisesRegex(ValueError, 'Invalid FPM request'):
            validate_request({**PAYLOAD, 'catalog_build': options})

    def test_gitlab_mirror_is_explicit_and_pinned(self):
        root = archive({'fpm.toml': 'name="library"\n[dependencies]\nhelper={git="https://gitlab.com/example/helper.git",tag="v1"}'})
        helper = archive({'fpm.toml': 'name="helper"\nversion="VERSION"'})
        pins = [{'repository': 'example/library', 'revision': 'a'*40, 'sha256': hashlib.sha256(root).hexdigest()},
                {'repository': 'example/helper', 'revision': 'b'*40, 'sha256': hashlib.sha256(helper).hexdigest()}]
        options = self.options(git_aliases={'https://gitlab.com/example/helper':'https://github.com/example/helper'},
                               manifest_versions={'example/helper':'0.0.0'})
        def download(url, **kwargs):
            self.assertNotIn('gitlab.com', url)
            return helper if '/example/helper/' in url else root
        with tempfile.TemporaryDirectory() as temporary:
            _, records = CatalogPreparer(temporary, options=options, pins=pins, downloader=download).prepare(PAYLOAD)
            self.assertEqual(records[-1]['repository'], 'example/helper')
            manifests = [tomllib.loads(p.read_text()) for p in Path(temporary).rglob('fpm.toml')]
            self.assertEqual(next(m for m in manifests if m['name'] == 'helper')['version'], '0.0.0')
        with tempfile.TemporaryDirectory() as temporary, self.assertRaises(ValueError):
            CatalogPreparer(temporary, options={}, pins=pins, downloader=download).prepare(PAYLOAD)


class CatalogPatchTests(unittest.TestCase):
    def package(self, data=b'old source\n', before='old', after='new', path='src/code.f90'):
        from fpm_catalog_patches import patch_digest
        return {'id': 'patched', 'catalog_patches': {'adapter_sha256': patch_digest(),
            'edits': [{'path': path, 'sha256': hashlib.sha256(data).hexdigest(),
                       'before': before, 'after': after}]}}

    def test_checksum_guarded_patch_and_cache_isolation(self):
        from fpm_catalog_patches import apply_patches
        package = self.package()
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)/'src/code.f90'
            source.parent.mkdir()
            source.write_bytes(b'old source\n')
            apply_patches(package, temporary)
            self.assertEqual(source.read_bytes(), b'new source\n')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                apply_patches(package, temporary)
        base = {'id': 'x', 'repository': 'owner/x', 'revision': 'a'*40, 'archive_sha256': 'b'*64}
        self.assertEqual(cache_identity(base, 'recipe'), cache_identity({**base, 'catalog_patches': {}}, 'recipe'))
        self.assertNotEqual(cache_identity(base, 'recipe'), cache_identity({**base, **package}, 'recipe'))
        changed = self.package(after='different')
        self.assertNotEqual(cache_identity({**base, **package}, 'recipe'), cache_identity({**base, **changed}, 'recipe'))

    def test_patch_rejects_escape_and_ambiguous_matches(self):
        from fpm_catalog_patches import apply_patches, validate_patches
        for path in ('../code.f90', '/code.f90', 'C:/code.f90', 'src\\code.f90'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_patches(self.package(path=path))
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)/'src/code.f90'
            source.parent.mkdir()
            for data, before in ((b'old old', 'old'), (b'something else', 'old')):
                source.write_bytes(data)
                with self.assertRaisesRegex(ValueError, 'exactly once'):
                    apply_patches(self.package(data=data, before=before), temporary)
