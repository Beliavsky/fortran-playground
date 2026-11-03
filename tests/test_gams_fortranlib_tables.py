"""Hosted proof integrity and exact scientific-table fixture conventions."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'docs/gams-fortranlib-tables-validation.json'


class FortranlibTablesTests(unittest.TestCase):
    def test_five_pinned_sources_have_main_only_hosted_proofs(self):
        drivers = {d['id']: d for d in json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())['drivers']
                   if d.get('validation_path') == REPORT}
        proofs = json.loads((ROOT/REPORT).read_text())['drivers']
        self.assertEqual(len(drivers), 5)
        self.assertEqual(set(drivers), {p['driver_id'] for p in proofs})
        records = {r['id']: r for r in json.loads((ROOT/'fpm_catalog/gams.json').read_text())['procedure_mappings']}
        for proof in proofs:
            d = drivers[proof['driver_id']]
            source = (ROOT/d['path']).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertEqual(d['revision'], proof['source_revision'])
            self.assertEqual(records[d['procedure_id']]['driver_id'], d['id'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})

    def test_hosted_outputs_retain_the_advertised_problem_counts(self):
        records = json.loads((ROOT/REPORT).read_text())['drivers']
        outputs = {r['driver_id']: next(s['stdout'] for s in r['stages'] if s['name'] == 'Run')
                   for r in records}
        for short, pattern in [
            ('logarithmic-interpolation', r'query pairs checked:\s+715'),
            ('logarithmic-areas', r'subset areas checked:\s+726'),
            ('conservative-rebinning', r'cell means checked:\s+84'),
            ('bilinear-surfaces', r'including boundaries:\s+1875'),
            ('masked-histograms', r'6 one-dimensional histograms and 3 two-dimensional histograms')]:
            self.assertRegex(outputs['fortranlib-'+short+'-reference'], pattern)
        self.assertIn('55 cumulative-prefix', outputs['fortranlib-logarithmic-areas-reference'])
        self.assertIn('14 total-area conservation', outputs['fortranlib-conservative-rebinning-reference'])

    def test_histogram_boundary_fixture_has_exact_counts_and_weight_sums(self):
        samples = [F(i-6, 4) for i in range(1, 12)]
        weights = [1+F(i, 4) for i in range(1, 12)]
        # Reference half-open intervals, with a closed final upper endpoint.
        groups = [[i for i, value in enumerate(samples)
                   if F(j-2, 2) <= value < F(j-1, 2) or j == 3 and value == 1]
                  for j in range(4)]
        self.assertEqual([len(group) for group in groups], [2, 2, 2, 3])
        self.assertEqual([sum(weights[i] for i in group) for group in groups],
                         [F(13, 4), F(17, 4), F(21, 4), F(39, 4)])
        self.assertEqual(sum(len(a)*len(b) for a in groups for b in groups), 81)


if __name__ == '__main__':
    unittest.main()
