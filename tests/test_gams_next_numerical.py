"""Independent constants and proof integrity for the numerical audit candidates."""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'docs/gams-next-numerical-validation.json'


class NextNumericalTests(unittest.TestCase):
    def test_six_sources_have_matching_pins_and_main_only_hosted_proofs(self):
        manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())['drivers']
        drivers = {d['id']: d for d in manifest if d.get('validation_path') == REPORT}
        proofs = json.loads((ROOT/REPORT).read_text())['drivers']
        self.assertEqual(len(drivers), 6)
        self.assertEqual(set(drivers), {p['driver_id'] for p in proofs})
        records = {r['id']: r for r in json.loads((ROOT/'fpm_catalog/gams.json').read_text())['procedure_mappings']}
        for proof in proofs:
            driver = drivers[proof['driver_id']]
            source = (ROOT/driver['path']).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertEqual(proof['source_revision'], records[driver['procedure_id']]['revision'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})

    def test_signed_cube_root_constants_match_independent_libm_values(self):
        data = json.loads((ROOT/'docs/gams-next-numerical-references.json').read_text())['drivers']
        rows = data['rpn-real-cube-roots-reference']
        self.assertEqual(len(rows), 55)
        for row in rows:
            expected = math.cbrt(float(F(row['x'])))
            self.assertLessEqual(abs(float(row['expected'])-expected),
                                 4e-15*max(abs(expected), 1e-100))

    def test_bessel_constants_match_positive_decimal_series(self):
        data = json.loads((ROOT/'docs/gams-next-numerical-references.json').read_text())['drivers']
        rows = data['rpn-bessel-i0-values-reference']
        self.assertEqual(len(rows), 29)
        with localcontext() as context:
            context.prec = 80
            for row in rows:
                x = F(row['x'])
                x = D(x.numerator)/D(x.denominator)
                term, total = D(1), D(1)
                for k in range(1, 1000):
                    term *= x*x/D(4*k*k)
                    total += term
                    if abs(term) < D('1e-70')*total:
                        break
                else:
                    self.fail('Independent I0 series did not converge')
                self.assertLess(abs(D(row['expected'])-total)/total, D('3e-17'))


if __name__ == '__main__':
    unittest.main()
