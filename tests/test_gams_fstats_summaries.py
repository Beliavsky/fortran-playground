"""Independent mathematical definitions and proof checks for the Fstats batch."""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import itertools
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FstatsSummariesTests(unittest.TestCase):
    def rows(self, short):
        data = json.loads((ROOT/'docs/gams-fstats-summaries-ten-references.json').read_text())
        return data['drivers']['fstats-'+short+'-reference']

    def check_reference(self, row, pdf, cdf, survival):
        for key, expected in [('pdf', pdf), ('cdf', cdf), ('survival', survival)]:
            self.assertLessEqual(abs(float(row[key])-float(expected)),
                                 3e-13*max(abs(float(expected)), 1e-30))

    def test_ten_exact_sources_have_main_only_hosted_proofs(self):
        manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())
        drivers = [d for d in manifest['drivers']
                   if d.get('validation_path') == 'docs/gams-fstats-summaries-ten-validation.json']
        proofs = json.loads((ROOT/'docs/gams-fstats-summaries-ten-validation.json').read_text())['drivers']
        self.assertEqual(len(drivers), 10)
        self.assertEqual({d['id'] for d in drivers}, {d['driver_id'] for d in proofs})
        for proof in proofs:
            source = (ROOT/'fpm_catalog/gams-drivers'/(proof['driver_id']+'.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})

    def test_binomial_tables_match_exact_rational_sums(self):
        self.assertEqual(len(self.rows('binomial-boundaries')), 165)
        for row in self.rows('binomial-boundaries'):
            n, p, k = int(F(row['a'])), F(row['b']), int(F(row['x']))
            terms = [F(math.comb(n, j))*p**j*(1-p)**(n-j) for j in range(n+1)]
            split = max(0, min(n+1, k+1))
            self.check_reference(row, terms[k] if 0 <= k <= n else 0,
                                 sum(terms[:split]), sum(terms[split:]))

    def test_poisson_tables_keep_small_upper_tails(self):
        with localcontext() as context:
            context.prec = 80
            for row in self.rows('poisson-tail-functions'):
                rate = F(row['a'])
                z = D(rate.numerator)/D(rate.denominator)
                k = int(F(row['x']))
                if z == 0:
                    pdf = D(int(k == 0))
                    cdf = D(int(k >= 0))
                elif k < 0:
                    pdf, cdf = D(0), D(0)
                else:
                    pdf = (-z).exp()*z**k/D(math.factorial(k))
                    cdf = (-z).exp()*sum((z**j/D(math.factorial(j)) for j in range(k+1)), D(0))
                self.check_reference(row, pdf, cdf, 1-cdf)

    def test_normal_and_low_degree_t_closed_forms(self):
        for row in self.rows('normal-tail-functions'):
            mu, sigma, x = (float(F(row[k])) for k in ['a', 'b', 'x'])
            z = (x-mu)/sigma
            self.check_reference(row, math.exp(-z*z/2)/(sigma*math.sqrt(2*math.pi)),
                                 math.erfc(-z/math.sqrt(2))/2, math.erfc(z/math.sqrt(2))/2)
        for row in self.rows('student-t-finite-values'):
            v, x = int(F(row['a'])), float(F(row['x']))
            if v == 1:
                pdf, cdf = 1/(math.pi*(1+x*x)), 0.5+math.atan(x)/math.pi
            elif v == 2:
                pdf, cdf = (2+x*x)**(-1.5), 0.5+x/(2*math.sqrt(2+x*x))
            else:
                continue
            self.check_reference(row, pdf, cdf, 1-cdf)

    def test_summary_conventions_have_exact_examples(self):
        x = [F(0), F(1), F(2), F(3), F(4), F(5), F(6), F(100)]
        self.assertEqual(sum(x[1:-1])/6, F(7, 2))
        self.assertEqual((1-F(1, 4))*x[1]+F(1, 4)*x[2], F(5, 4))
        self.assertEqual(((3-1)*F(1)+(5-1)*F(4))/((3-1)+(5-1)), 3)
        data = [1, 1, 2, 2, 4, 6, 9]
        deviations = sorted(abs(x-2) for x in data)
        self.assertEqual(deviations[len(data)//2], 1)

    def test_full_factorial_mixed_radix_keys_cover_product(self):
        for factors in range(1, 5):
            for variant in range(3):
                levels = [1+(variant+i) % 4 for i in range(1, factors+1)]
                keys = []
                for combination in itertools.product(*(range(n) for n in levels)):
                    key, stride = 0, 1
                    for value, count in zip(combination, levels):
                        key += value*stride
                        stride *= count
                    keys.append(key)
                self.assertEqual(sorted(keys), list(range(math.prod(levels))))
