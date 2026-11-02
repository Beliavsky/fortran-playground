"""Independent oracle and provenance checks for the ordering/ODE batch."""
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'docs/gams-ordering-runge-ten-validation.json'


class OrderingRungeTests(unittest.TestCase):
    def test_ten_exact_sources_have_main_only_hosted_proofs(self):
        manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())
        drivers = [d for d in manifest['drivers'] if d.get('validation_path') == REPORT]
        proofs = json.loads((ROOT/REPORT).read_text())['drivers']
        self.assertEqual(len(drivers), 10)
        self.assertEqual({d['id'] for d in drivers}, {d['driver_id'] for d in proofs})
        self.assertEqual(sum(d['package_id'] == 'orderpack' for d in drivers), 6)
        for proof in proofs:
            source = (ROOT/'fpm_catalog/gams-drivers'/(proof['driver_id']+'.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})
            self.assertLessEqual(max(map(len, source.splitlines())), 132)

    def test_even_median_conventions_differ(self):
        values = sorted([1.25, -2.0, 3.5, 0.0])
        self.assertEqual(values[1], 0.0)
        self.assertEqual((values[1]+values[2])/2, 0.625)
        source = (ROOT/'fpm_catalog/gams-drivers/orderpack-median-conventions-reference.f90').read_text()
        self.assertIn('sorted((n+1)/2)+sorted(n/2+1)', source)
        self.assertIn('expected=sorted((n+1)/2)', source)

    def test_stable_unique_and_multiplicity_oracles(self):
        data = [2, -1, 2, 0, -1, 2, 4, 0]
        firsts = [v for i, v in enumerate(data) if v not in data[:i]]
        self.assertEqual(firsts, [2, -1, 0, 4])
        counts = [sum(v == w for w in data) for v in data]
        self.assertEqual(counts, [3, 2, 3, 2, 2, 3, 1, 2])

    def test_distinct_pattern_is_distinct_for_all_sizes(self):
        for n in range(1, 66):
            values = [((37*(i-1)) % 67-33)/4 for i in range(1, n+1)]
            self.assertEqual(len(set(values)), n)

    def test_closed_form_system_satisfies_equations(self):
        for i in range(21):
            t = i/10
            y = [math.exp(-t), math.cos(t), -math.sin(t), 1/(1+math.exp(-t)), t*t+0.25]
            derivative = [-math.exp(-t), -math.sin(t), -math.cos(t),
                          math.exp(-t)/(1+math.exp(-t))**2, 2*t]
            rhs = [-y[0], y[2], -y[1], y[3]*(1-y[3]), 2*t]
            for actual, expected in zip(rhs, derivative):
                self.assertAlmostEqual(actual, expected, places=14)

    def test_failed_order_statistics_are_preserved_and_not_published(self):
        folder = ROOT/'docs/gams-candidates/orderpack-statistics'
        records = list(folder.glob('*-result.json'))
        self.assertEqual(len(records), 3)
        for path in records:
            record = json.loads(path.read_text())
            source = path.with_name(path.name.replace('-result.json', '.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), record['source_sha256'])
            self.assertFalse(record['result']['ok'])
        data = json.loads((ROOT/'fpm_catalog/gams.json').read_text())
        record = next(r for r in data['procedure_mappings'] if r['id'] == 'orderpack-order-statistics')
        self.assertNotIn('driver_id', record)
        self.assertEqual(sorted([-1.25, -2.75, 1.5, 0.0])[2], 0.0)
