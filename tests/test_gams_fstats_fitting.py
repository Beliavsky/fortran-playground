"""Independent probability definitions, reference algebra and retained probe evidence."""
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'docs/gams-fstats-fitting-ten-validation.json'


class FstatsFittingTests(unittest.TestCase):
    def rows(self, short):
        table = json.loads((ROOT/'docs/gams-fstats-fitting-ten-references.json').read_text())
        return table['drivers']['fstats-'+short+'-reference']

    def reference(self, row, pdf, cdf, survival):
        for key, expected in [('pdf', pdf), ('cdf', cdf), ('survival', survival)]:
            self.assertLessEqual(abs(float(row[key])-expected),
                                 5e-12*max(abs(expected), 1e-30))

    def test_ten_sources_have_matching_successful_main_only_proofs(self):
        manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())
        drivers = [d for d in manifest['drivers'] if d.get('validation_path') == REPORT]
        proofs = json.loads((ROOT/REPORT).read_text())['drivers']
        self.assertEqual(len(drivers), 10)
        self.assertEqual({d['id'] for d in drivers}, {p['driver_id'] for p in proofs})
        for proof in proofs:
            source = (ROOT/'fpm_catalog/gams-drivers'/(proof['driver_id']+'.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})

    def test_chi_squared_integrals_match_integer_half_integer_recurrences(self):
        self.assertEqual(len(self.rows('chi-squared-positive-tails')), 30)
        for row in self.rows('chi-squared-positive-tails'):
            v, x = int(F(row['a'])), float(F(row['x']))
            z = x/2
            # Start with Gamma(1) or Gamma(1/2) survival; recur upward in shape.
            shape = 1 if v % 2 == 0 else 0.5
            survival = math.exp(-z) if shape == 1 else math.erfc(math.sqrt(z))
            while shape < v/2:
                survival += z**shape*math.exp(-z)/math.gamma(shape+1)
                shape += 1
            pdf = x**(v/2-1)*math.exp(-x/2)/(2**(v/2)*math.gamma(v/2))
            # Lower-tail subtraction loses digits for tiny CDFs; use an absolute
            # comparison there, while retaining a relative upper-tail check.
            self.assertAlmostEqual(float(row['cdf']), 1-survival, delta=3e-15)
            self.assertAlmostEqual(float(row['pdf']), pdf, delta=3e-13*pdf)
            self.assertAlmostEqual(float(row['survival']), survival, delta=3e-13*survival)

    def test_f_density_and_two_closed_form_cdfs(self):
        self.assertEqual(len(self.rows('f-positive-tails')), 20)
        checked = 0
        for row in self.rows('f-positive-tails'):
            a, b, x = (float(F(row[k])) for k in ['a', 'b', 'x'])
            beta = math.gamma(a/2)*math.gamma(b/2)/math.gamma((a+b)/2)
            pdf = (a/b)**(a/2)*x**(a/2-1)/(beta*(1+a*x/b)**((a+b)/2))
            self.assertAlmostEqual(float(row['pdf']), pdf, delta=3e-13*pdf)
            if (a, b) == (1, 1):
                cdf = 2*math.atan(math.sqrt(x))/math.pi
                survival = 2*math.atan(1/math.sqrt(x))/math.pi
            elif (a, b) == (2, 4):
                survival = (1+x/2)**(-2)
                cdf = x*(x+4)/(x+2)**2
            else:
                continue
            self.reference(row, pdf, cdf, survival)
            checked += 1
        self.assertEqual(checked, 10)

    def test_lognormal_tables_use_observation_space(self):
        self.assertEqual(len(self.rows('lognormal-observation-scale')), 42)
        for row in self.rows('lognormal-observation-scale'):
            mu, sigma, x = (float(F(row[k])) for k in ['a', 'b', 'x'])
            if x <= 0:
                self.reference(row, 0, 0, 1)
                continue
            z = (math.log(x)-mu)/sigma
            self.reference(row, math.exp(-z*z/2)/(x*sigma*math.sqrt(2*math.pi)),
                           math.erfc(-z/math.sqrt(2))/2, math.erfc(z/math.sqrt(2))/2)

    def test_quadratic_projection_oracle_satisfies_exact_normal_equations(self):
        for n in range(5, 14, 2):
            x = [F(i-(n+1)//2, 4) for i in range(1, n+1)]
            s2, s4, s6 = (sum(v**k for v in x) for k in [2, 4, 6])
            determinant = n*s4-s2*s2
            self.assertGreater(determinant, 0)
            for variant in range(1, 4):
                a, b, c, eta = F(variant, 4), F(-3, 4), F(1, 2), F(variant, 64)
                fitted = [a+eta*(s4*s4-s2*s6)/determinant, b,
                          c+eta*(n*s6-s2*s4)/determinant]
                residual = [fitted[0]+fitted[1]*v+fitted[2]*v*v
                            -(a+b*v+c*v*v+eta*v**4) for v in x]
                for power in range(3):
                    self.assertEqual(sum(v**power*r for v, r in zip(x, residual)), 0)

    def test_failed_interpolation_probes_keep_exact_evidence(self):
        directory = ROOT/'docs/gams-candidates/fstats-interpolation'
        for stem in ['fstats-clamped-cubic-spline-values-reference',
                     'fstats-hermite-values-derivatives-reference']:
            record = json.loads((directory/(stem+'-result.json')).read_text())
            source = (directory/(stem+'.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), record['source_sha256'])
            self.assertFalse(record['result']['ok'])
            self.assertTrue(record['result']['cache']['library_reused'])
            self.assertTrue(record['result']['stages'][0]['ok'])
            self.assertFalse(record['result']['stages'][1]['ok'])
        proofs = json.loads((ROOT/REPORT).read_text())['drivers']
        self.assertNotIn('fstats-clamped-cubic-spline-values-reference',
                         {p['driver_id'] for p in proofs})


if __name__ == '__main__':
    unittest.main()
