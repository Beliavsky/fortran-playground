"""Protect the distinctions between missing procedures and cross-class claims."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from xaudit_gams_drivers import audit, INPUTS, markdown, ROOT


class GamsDriverAuditTests(unittest.TestCase):
    def test_inventory_balances_and_does_not_count_empty_driver_groups(self):
        report = audit()
        counts = report['counts']
        self.assertEqual(counts['procedures_with_drivers']+counts['procedures_without_drivers'],
                         counts['procedure_records'])
        self.assertEqual(sum(counts['unchecked_by_status'].values()), counts['procedures_without_drivers'])
        unchecked = {r['procedure_id'] for r in report['unchecked_procedures']}
        claims = {r['procedure_id'] for r in report['additional_class_claims']}
        self.assertFalse(unchecked & claims)
        self.assertIn('stdlib-pca', unchecked)
        self.assertIn('rng-uniform', claims)
        self.assertNotIn('nonlin-bfgs', claims)
        self.assertEqual({r['status'] for r in report['unchecked_procedures']
                          if r['procedure_id'] == 'stdlib-pca'}, {'sandbox-limit'})
        self.assertEqual({r['status'] for r in report['unchecked_procedures']
                          if r['procedure_id'] in {'fortran-lapack-eigh', 'fortran-lapack-svd'}},
                         {'sandbox-limit'})
        self.assertNotIn('fortran-lapack-eigh', {r['procedure_id'] for r in report['next_candidates']})

    def copy_inputs(self, destination):
        for name in INPUTS:
            target = destination/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT/name).read_bytes())
        policy = json.loads((ROOT/'fpm_catalog/gams-driver-priorities.json').read_text())
        for record in policy['unchecked_dispositions'].values():
            for name in record.get('retained_paths', []):
                target = destination/name
                if (ROOT/name).is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes((ROOT/name).read_bytes())

    def test_completed_candidate_drops_out_and_new_record_requires_triage(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            self.copy_inputs(destination)
            p = destination/'fpm_catalog/gams-drivers.json'
            manifest = json.loads(p.read_text())
            original = next(d for d in manifest['drivers'] if d['procedure_id'] == 'nonlin-bfgs-finite-differences')
            manifest['drivers'].remove(original)
            p.write_text(json.dumps(manifest))
            pending = audit(destination)
            self.assertIn(('nonlin-bfgs-finite-differences', 'G1b1a'),
                          {(r['procedure_id'], r['gams_code']) for r in pending['next_candidates']})
            manifest['drivers'].append(original)
            p.write_text(json.dumps(manifest))
            p = destination/'fpm_catalog/gams.json'
            data = json.loads(p.read_text())
            record = deepcopy(next(r for r in data['procedure_mappings'] if r['id'] == 'fortran-lapack-eigh'))
            record['id'] = 'audit-new-unchecked'
            data['procedure_mappings'].append(record)
            p.write_text(json.dumps(data))
            report = audit(destination)
            self.assertNotIn(('nonlin-bfgs-finite-differences', 'G1b1a'),
                             {(r['procedure_id'], r['gams_code']) for r in report['next_candidates']})
            new = next(r for r in report['unchecked_procedures'] if r['procedure_id'] == record['id'])
            self.assertEqual(new['status'], 'needs-triage')

    def test_published_snapshot_matches_live_metadata_and_pinned_links(self):
        report = audit()
        self.assertEqual(report, json.loads((ROOT/'docs/gams-driver-audit.json').read_text(encoding='utf-8')))
        self.assertEqual(markdown(report), (ROOT/'docs/gams-driver-audit.md').read_text(encoding='utf-8'))
        for record in report['unchecked_procedures']:
            for evidence in record['sources']+record['author_examples']:
                self.assertIn('/blob/'+record['revision']+'/', evidence['url'])

    def test_snapshot_hashes_are_independent_of_checkout_line_endings(self):
        original = audit()
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            self.copy_inputs(destination)
            for name in INPUTS:
                p = destination/name
                p.write_bytes(p.read_text(encoding='utf-8').replace('\n', '\r\n').encode('utf-8'))
            self.assertEqual(original['input_sha256'], audit(destination)['input_sha256'])


if __name__ == '__main__':
    unittest.main()
