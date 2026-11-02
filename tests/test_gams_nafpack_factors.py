"""Independent algebra and proof checks for the NAFPack factorization batch."""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def product(a, b):
    return [[sum(x*y for x, y in zip(row, column)) for column in zip(*b)] for row in a]


class NafpackFactorsTests(unittest.TestCase):
    def test_ten_exact_sources_have_main_only_hosted_proofs(self):
        manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())
        drivers = [d for d in manifest['drivers']
                   if d.get('validation_path') == 'docs/gams-nafpack-factors-ten-validation.json']
        proofs = json.loads((ROOT/'docs/gams-nafpack-factors-ten-validation.json').read_text())['drivers']
        self.assertEqual(len(drivers), 10)
        self.assertEqual({d['id'] for d in drivers}, {d['driver_id'] for d in proofs})
        self.assertEqual(sum(d['gams_code'] == 'D5' for d in drivers), 4)
        for proof in proofs:
            source = (ROOT/'fpm_catalog/gams-drivers'/(proof['driver_id']+'.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})

    def test_householder_spectrum_oracle_is_exactly_orthogonal(self):
        for n in range(2, 11):
            norm = sum(i*i for i in range(1, n+1))
            q = [[F(int(i == j))-F(2*(i+1)*(j+1), norm) for j in range(n)] for i in range(n)]
            identity = [[F(int(i == j)) for j in range(n)] for i in range(n)]
            self.assertEqual(product(q, q), identity)

    def test_characteristic_coefficients_have_known_sign_convention(self):
        roots = [F(-1), F(1, 2), F(2)]
        coefficients = [F(1)]
        for root in roots:
            next_coefficients = [F(0)]*(len(coefficients)+1)
            for i, value in enumerate(coefficients):
                next_coefficients[i] += value
                next_coefficients[i+1] -= root*value
            coefficients = next_coefficients
        self.assertEqual(coefficients, [F(1), F(-3, 2), F(-3, 2), F(1)])
        self.assertEqual(-coefficients[1], sum(roots))
        self.assertEqual(coefficients[-1], -roots[0]*roots[1]*roots[2])

    def test_unit_ldu_and_lu_oracles_agree(self):
        lower = [[F(1), F(0)], [F(1, 4), F(1)]]
        diagonal = [[F(2), F(0)], [F(0), F(3)]]
        unit_upper = [[F(1), F(-1, 8)], [F(0), F(1)]]
        upper = product(diagonal, unit_upper)
        expected = [[F(2), F(-1, 4)], [F(1, 2), F(47, 16)]]
        self.assertEqual(product(lower, upper), expected)
        self.assertEqual(product(product(lower, diagonal), unit_upper), expected)

    def test_cholesky_reconstruction_from_known_lower_entries(self):
        lower = [[F(2), F(0)], [F(1, 4), F(3)]]
        transpose = [list(row) for row in zip(*lower)]
        self.assertEqual(product(lower, transpose), [[F(4), F(1, 2)], [F(1, 2), F(145, 16)]])
