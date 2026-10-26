import hashlib
from io import BytesIO
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from xfpm_audit_worker import extract_package

ROOT = Path(__file__).resolve().parents[1]


class FpmAuditTests(unittest.TestCase):
    def make_archive(self, path, name, *, link=False):
        with tarfile.open(path, 'w:gz') as stream:
            member = tarfile.TarInfo(name)
            if link:
                member.type = tarfile.SYMTYPE
                member.linkname = '../../outside'
                stream.addfile(member)
            else:
                content = b'name = "example"\n'
                member.size = len(content)
                stream.addfile(member, BytesIO(content))

    def test_archive_accepts_root_manifest_and_rejects_traversal_links_and_missing_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / 'package.tar.gz'
            self.make_archive(archive, 'package/fpm.toml')
            source = extract_package(archive, root / 'valid')
            self.assertEqual((source / 'fpm.toml').read_text(), 'name = "example"\n')
            for name, link in [('../escape', False), ('/absolute', False), ('package/link', True), ('package/README', False)]:
                self.make_archive(archive, name, link=link)
                with self.subTest(name=name), self.assertRaises(ValueError):
                    extract_package(archive, root / 'invalid')
            self.assertFalse((root / 'escape').exists())

    def test_five_pinned_revisions_and_demonstration_hashes(self):
        directory = ROOT / 'docs' / 'fpm-feasibility'
        packages = json.loads((directory / 'packages.lock.json').read_text())
        self.assertEqual(len(packages), 5)
        self.assertEqual(len({package['repository'] for package in packages}), 5)
        for package in packages:
            self.assertRegex(package['revision'], r'^[a-f0-9]{40}$')
            self.assertRegex(package['sha256'], r'^[a-f0-9]{64}$')
            demo = directory / 'demos' / (package['name'] + '.f90')
            self.assertEqual(hashlib.sha256(demo.read_text(encoding='utf-8').encode('utf-8')).hexdigest(), package['demo_sha256'])
            self.assertIn('error stop', demo.read_text())

    def test_recorded_results_match_inputs_and_meet_five_package_threshold(self):
        directory = ROOT / 'docs' / 'fpm-feasibility'
        report = json.loads((directory / 'results.json').read_text())
        self.assertEqual(report['packages'], json.loads((directory / 'packages.lock.json').read_text()))
        worker_source = (ROOT / 'xfpm_audit_worker.py').read_text(encoding='utf-8').encode('utf-8')
        self.assertEqual(hashlib.sha256(worker_source).hexdigest(), report['worker_sha256'])
        self.assertEqual(report['network'], 'blocked')
        self.assertEqual(report['runtime'], 'gvisor')
        for package in report['packages']:
            rows = [row for row in report['runs'] if row['package'] == package['name']]
            self.assertEqual(len(rows), 2)
            for row in rows:
                self.assertTrue(row['ok'])
                self.assertEqual(row['uid'], 65534)
                self.assertEqual(row['sandbox_exit_code'], 0)
                self.assertLess(row['build_seconds'], 120)
                self.assertLess(row['run_seconds'], 20)
                self.assertIn('16.2.0', row['compiler'])


if __name__ == '__main__':
    unittest.main()
