"""Independent definitions and provenance for the gamma/relative-function batch."""
from decimal import Decimal as D, localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'specfunc-fullerton-'


class GammaRelativeTests(unittest.TestCase):
    def rows(self, short):
        data = json.loads((ROOT/'docs/gams-gamma-relative-ten-references.json').read_text())
        return data['drivers'][PREFIX+short+'-reference']

    def close_reference(self, row, value):
        self.assertLessEqual(abs(float(row['reference'])-float(value)),
                             3e-12*max(abs(float(value)), 1e-30))

    def test_ten_exact_sources_have_main_only_proofs(self):
        manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())
        drivers = [d for d in manifest['drivers']
                   if d.get('validation_path') == 'docs/gams-gamma-relative-ten-validation.json']
        proofs = json.loads((ROOT/'docs/gams-gamma-relative-ten-validation.json').read_text())['drivers']
        self.assertEqual(len(drivers), 10)
        self.assertEqual({d['id'] for d in drivers}, {d['driver_id'] for d in proofs})
        for proof in proofs:
            source = (ROOT/'fpm_catalog/gams-drivers'/(proof['driver_id']+'.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})

    def test_integer_shape_gamma_integrals_and_scaling(self):
        for short in ['lower-incomplete-gamma', 'upper-gamma-positive-x', 'tricomi-incomplete-gamma']:
            with localcontext() as context:
                context.prec = 80
                for row in self.rows(short):
                    a, x = Fraction(row['a']), Fraction(row['x'])
                    if a.denominator != 1 or a <= 0:
                        continue
                    n = int(a)
                    z = D(x.numerator)/D(x.denominator)
                    upper = D(math.factorial(n-1))*(-z).exp()*sum(
                        (z**k/D(math.factorial(k)) for k in range(n)), D(0)) if z else D(math.factorial(n-1))
                    lower = D(math.factorial(n-1))-upper
                    if short == 'upper-gamma-positive-x':
                        expected = upper
                    elif short == 'lower-incomplete-gamma':
                        expected = lower
                    else:
                        expected = lower/(D(math.factorial(n-1))*z**n) if z else D(1)/D(math.factorial(n))
                    self.close_reference(row, expected)

    def test_factorials_and_integer_pochhammer_products(self):
        for row in self.rows('factorials-real32'):
            self.close_reference(row, math.factorial(row['n']))
        for row in self.rows('pochhammer-ratios'):
            a, x = Fraction(row['a']), Fraction(row['x'])
            if x.denominator == 1 and x >= 0:
                expected = math.prod(a+k for k in range(int(x)))
                self.close_reference(row, expected)

    def test_reciprocal_gamma_pole_zeros_and_half_integer_recurrence(self):
        for row in self.rows('reciprocal-gamma-pole-zeros'):
            x = Fraction(row['x'])
            if x.denominator == 1:
                self.assertEqual(float(row['reference']), 0)
            else:
                value, position = math.sqrt(math.pi), Fraction(1, 2)
                while position < x:
                    value *= float(position)
                    position += 1
                while position > x:
                    position -= 1
                    value /= float(position)
                self.close_reference(row, 1/value)

    def test_cube_roots_and_cin_power_series(self):
        for row in self.rows('signed-cube-roots'):
            x, value = float(Fraction(row['x'])), float(row['reference'])
            self.assertLessEqual(abs(value**3-x), 2e-14*max(abs(x), 1e-30))
        for row in self.rows('entire-cosine-integral'):
            x = float(Fraction(row['x']))
            if x > 4:
                continue
            value = sum((-1)**(k+1)*x**(2*k)/(2*k*math.factorial(2*k)) for k in range(1, 50))
            self.close_reference(row, value)

    def test_failed_domains_preserved_and_excluded(self):
        folder = ROOT/'docs/gams-candidates/fullerton-gamma-cinh'
        records = list(folder.glob('*-result.json'))
        self.assertEqual(len(records), 2)
        for path in records:
            record = json.loads(path.read_text())
            source = path.with_name(path.name.replace('-result.json', '.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), record['source_sha256'])
            self.assertFalse(record['result']['ok'])
            self.assertTrue(record['result']['stages'][0]['ok'])
        data = json.loads((ROOT/'fpm_catalog/gams.json').read_text())
        for ident in ['upper-incomplete-gamma', 'entire-hyperbolic-integral']:
            record = next(r for r in data['procedure_mappings'] if r['id'] == PREFIX+ident)
            self.assertNotIn('driver_id', record)
        self.assertTrue(all(Fraction(r['x']) > 0 for r in self.rows('upper-gamma-positive-x')))
