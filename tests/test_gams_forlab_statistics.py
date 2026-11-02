"""Independent definitions and provenance for Forlab's native-precision consumers."""
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ForlabStatisticsTests(unittest.TestCase):
    def test_ten_exact_sources_have_main_only_hosted_proofs(self):
        manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())
        drivers = [d for d in manifest['drivers']
                   if d.get('validation_path') == 'docs/gams-forlab-statistics-ten-validation.json']
        proofs = json.loads((ROOT/'docs/gams-forlab-statistics-ten-validation.json').read_text())['drivers']
        self.assertEqual(len(drivers), 10)
        self.assertEqual({d['id'] for d in drivers}, {d['driver_id'] for d in proofs})
        for proof in proofs:
            source = (ROOT/'fpm_catalog/gams-drivers'/(proof['driver_id']+'.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})
            if 'polynomial-differences' not in proof['driver_id']:
                self.assertRegex(proof['stages'][1]['stdout'], r'Forlab real storage bits:\s+32')

    def test_population_moments_and_normalization(self):
        data = [F(-2), F(-1), F(0), F(1), F(2)]
        second = sum(x*x for x in data)/len(data)
        fourth = sum(x**4 for x in data)/len(data)
        self.assertEqual(second, 2)
        self.assertEqual(sum(x**3 for x in data), 0)
        self.assertEqual(fourth/second**2, F(17, 10))
        self.assertEqual(sum(x*x for x in data)/(len(data)-1), F(5, 2))

    def test_even_chi_square_formulas_are_distribution_consistent(self):
        for k in range(1, 5):
            previous = 0
            for x in [0.125, 0.5, 1, 2, 4, 8]:
                t = x/2
                cdf = 1-math.exp(-t)*sum(t**j/math.factorial(j) for j in range(k))
                pdf = t**(k-1)*math.exp(-t)/(2*math.factorial(k-1))
                self.assertGreater(pdf, 0)
                self.assertGreater(cdf, previous)
                self.assertLess(cdf, 1)
                previous = cdf
        self.assertAlmostEqual(1-math.exp(-1), 0.6321205588285577)

    def test_cubic_forward_differences_exact(self):
        def polynomial(t):
            return t**3+2*t*t-3*t+1
        for h in [F(1, 8), F(1, 4), F(1, 2)]:
            for t in [F(-1), F(0), F(3, 2)]:
                values = [polynomial(t+i*h) for i in range(4)]
                first = (values[1]-values[0])/h
                second = (values[2]-2*values[1]+values[0])/h**2
                third = (values[3]-3*values[2]+3*values[1]-values[0])/h**3
                self.assertEqual(first, 3*t*t+4*t-3+(3*t+2)*h+h*h)
                self.assertEqual(second, 6*(t+h)+4)
                self.assertEqual(third, 6)

    def test_retained_failures_and_unpublished_api_records(self):
        folder = ROOT/'docs/gams-candidates/forlab-statistics'
        results = list(folder.glob('*-result.json'))
        self.assertEqual(len(results), 3)
        for path in results:
            record = json.loads(path.read_text())
            source = path.with_name(path.name.replace('-result.json', '.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), record['source_sha256'])
            self.assertFalse(record['result']['ok'])
        data = json.loads((ROOT/'fpm_catalog/gams.json').read_text())
        for ident in ['forlab-median-percentiles', 'forlab-difference-cumsum']:
            record = next(r for r in data['procedure_mappings'] if r['id'] == ident)
            self.assertNotIn('driver_id', record)
