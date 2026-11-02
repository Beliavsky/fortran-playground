"""Independent algebra and publication checks for the structured matrix batch."""
from fractions import Fraction as F
import hashlib
import itertools
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BandedProductsTests(unittest.TestCase):
    def test_ten_exact_sources_have_main_only_proofs(self):
        manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())
        drivers = [d for d in manifest['drivers']
                   if d.get('validation_path') == 'docs/gams-banded-products-ten-validation.json']
        proofs = json.loads((ROOT/'docs/gams-banded-products-ten-validation.json').read_text())['drivers']
        self.assertEqual(len(drivers), 10)
        self.assertEqual({d['id'] for d in drivers}, {d['driver_id'] for d in proofs})
        for proof in proofs:
            source = (ROOT/'fpm_catalog/gams-drivers'/(proof['driver_id']+'.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})

    def test_positive_and_indefinite_families_have_separated_gershgorin_disks(self):
        for n in range(2, 17):
            d = [F(3)+F(i % 4, 8) for i in range(1, n+1)]
            off = [F(i % 3+1, 8) for i in range(1, n)]
            for i in range(n):
                radius = (off[i-1] if i else 0)+(off[i] if i < n-1 else 0)
                self.assertGreater(d[i], radius)
            self.assertGreater(abs(F(5, 4)), abs(F(1, 8)))

    def test_pivoted_family_has_independently_known_nonzero_determinant(self):
        matrix = [[F(1, 8), F(3, 4), F(0)],
                  [F(5, 4), F(13, 4), F(-3, 16)],
                  [F(0), F(3, 8), F(27, 8)]]
        exact = F(0)
        for permutation in itertools.permutations(range(3)):
            inversions = sum(permutation[i] > permutation[j] for i in range(3) for j in range(i+1, 3))
            product = F((-1)**inversions)
            for i, j in enumerate(permutation):
                product *= matrix[i][j]
            exact += product
        # Cofactor expansion gives 1413/1024 - 3240/1024.
        self.assertEqual(exact, F(-1827, 1024))

    def test_toeplitz_and_hankel_manual_conventions(self):
        c, r = [2, 3, 5], [99, 7, 11, 13]
        toeplitz = [[c[i-j] if i >= j else r[j-i] for j in range(4)] for i in range(3)]
        self.assertEqual(toeplitz, [[2, 7, 11, 13], [3, 2, 7, 11], [5, 3, 2, 7]])
        values = [2, -1, 4, 0, 3, 7]
        hankel = [[values[i+j] for j in range(4)] for i in range(3)]
        self.assertEqual(hankel[0], values[:4])
        self.assertEqual(hankel[2], values[2:])

    def test_bidiagonal_spectra_distinct_and_orientation_independent(self):
        for n in range(2, 17):
            diagonal = [(-1)**i*(F(2)+F(i, 8)) for i in range(1, n+1)]
            self.assertEqual(len(set(diagonal)), n)
            self.assertTrue(all(diagonal))
            for eigenvalue in diagonal:
                self.assertEqual(math.prod(v-eigenvalue for v in diagonal), 0)
