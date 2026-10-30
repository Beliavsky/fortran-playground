from io import BytesIO
import copy
import hashlib
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from fpm_catalog_build import CatalogPreparer, adapter_digest, validate_build, SHORT_ROOT_ADAPTER_SHA256
from fpm_catalog_limits import (PARAMONTE, source_limit, implementation_digest,
                                preparer_limit, extract_operator_bundle)
from fpm_sources import extract_archive, validate_request, MAX_EXPANDED


class CatalogLimitTests(unittest.TestCase):
    def package(self):
        return {'id': 'paramonte', **PARAMONTE, 'catalog_build': {
            'adapter_sha256': adapter_digest(),
            'source_limit': {'mib': 128, 'adapter_sha256': implementation_digest()}}}

    def test_allowance_requires_exact_pin_and_current_adapters(self):
        package = self.package()
        validate_build(package)
        self.assertEqual(source_limit(package), 128*1024*1024)
        self.assertEqual(source_limit({}), MAX_EXPANDED)
        for key in ('id', 'repository', 'revision', 'archive_sha256'):
            changed = copy.deepcopy(package); changed[key] = 'wrong'
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate_build(changed)
        for settings in ({'mib': 256, 'adapter_sha256': implementation_digest()},
                         {'mib': 128, 'adapter_sha256': '0'*64}, True, 128, {}, None):
            changed = copy.deepcopy(package);changed['catalog_build']['source_limit'] = settings
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                validate_build(changed)
        package['catalog_build']['adapter_sha256'] = SHORT_ROOT_ADAPTER_SHA256
        with self.assertRaises(ValueError):validate_build(package)

    def test_preparer_requires_locked_archive_and_public_rejects_option(self):
        package = self.package();options=package['catalog_build']
        pins = [{'repository':PARAMONTE['repository'], 'revision':PARAMONTE['revision'],
                 'sha256':PARAMONTE['archive_sha256']}]
        self.assertEqual(preparer_limit(options,pins),128*1024*1024)
        with self.assertRaises(ValueError):preparer_limit(options,[])
        pins[0]['sha256']='0'*64
        with self.assertRaises(ValueError):preparer_limit(options,pins)
        with self.assertRaisesRegex(ValueError,'Invalid FPM request'):
            validate_request({'url':'https://github.com/cdslaborg/paramonte',
                              'source_limit': options['source_limit']})

    def test_only_operator_bundle_accepts_more_than_64_mib(self):
        buffer=BytesIO()
        with tarfile.open(fileobj=buffer,mode='w:gz') as archive:
            for i in range(9):
                data=b'x'*(8*1024*1024);info=tarfile.TarInfo('bundle/part'+str(i));info.size=len(data)
                archive.addfile(info,BytesIO(data))
        data=buffer.getvalue()
        with tempfile.TemporaryDirectory() as temporary:
            dest=Path(temporary)/'public'
            with self.assertRaisesRegex(ValueError,'64 MiB'):extract_archive(data,dest,require_manifest=False)
            self.assertFalse(dest.exists())
            root=extract_operator_bundle(data,Path(temporary)/'operator',package=self.package())
            self.assertEqual(sum(p.stat().st_size for p in root.iterdir()),72*1024*1024)
            with patch('fpm_catalog_limits.REVIEWED_EXPANDED',64*1024*1024):
                with self.assertRaisesRegex(ValueError,'128 MiB'):
                    extract_operator_bundle(data,Path(temporary)/'bounded',package=self.package())
            self.assertFalse((Path(temporary)/'bounded').exists())

    def test_operator_extraction_retains_path_link_and_file_limits(self):
        for name,kind,size in [('bundle/../escape',tarfile.REGTYPE,0),
                                ('bundle/link',tarfile.SYMTYPE,0),
                                ('bundle/huge',tarfile.REGTYPE,17*1024*1024)]:
            buffer=BytesIO()
            with tarfile.open(fileobj=buffer,mode='w:gz') as archive:
                info=tarfile.TarInfo(name);info.type=kind;info.linkname='outside' if kind==tarfile.SYMTYPE else '';info.size=size
                archive.addfile(info,BytesIO(b'x'*size) if size else None)
            with tempfile.TemporaryDirectory() as temporary, self.assertRaises(ValueError):
                extract_operator_bundle(buffer.getvalue(),Path(temporary)/'sources',package=self.package())

    def test_combined_staging_uses_exception_without_changing_archive_limits(self):
        buffer=BytesIO();block=b'x'*(12*1024*1024)
        with tarfile.open(fileobj=buffer,mode='w:gz') as archive:
            for i in range(3):
                info=tarfile.TarInfo(f'package/src/code{i}.f90');info.size=len(block)
                archive.addfile(info,BytesIO(block))
        data=buffer.getvalue();pin={**PARAMONTE,'archive_sha256':hashlib.sha256(data).hexdigest()}
        package=self.package();package['archive_sha256']=pin['archive_sha256']
        options=package['catalog_build']
        options['source_packages']={pin['repository']:{'manifest':
            'name="paramonte"\n[library]\nsource-dir="playground-library"\n',
            'sources':[f'src/code{i}.f90' for i in range(3)]}}
        pins=[{'repository':pin['repository'],'revision':pin['revision'],'sha256':pin['archive_sha256']}]
        payload={'url':'https://github.com/'+pin['repository'],'revision':pin['revision'],
                 'source':'program main\nend program\n'}
        with patch.dict('fpm_catalog_limits.PARAMONTE',pin,clear=True):
            validate_build(package)
            with tempfile.TemporaryDirectory() as temporary:
                preparer=CatalogPreparer(temporary,options=options,pins=pins,downloader=lambda *a,**kw:data)
                relative,records=preparer.prepare(payload)
                self.assertTrue((Path(temporary)/relative/'fpm.toml').is_file())
                self.assertEqual(len(records),1)
            ordinary=copy.deepcopy(options);ordinary.pop('source_limit')
            with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(ValueError,'64 MiB'):
                CatalogPreparer(temporary,options=ordinary,pins=pins,downloader=lambda *a,**kw:data).prepare(payload)
