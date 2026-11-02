"""Independent mathematical and publication checks for the root/matrix batch."""
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPORT = 'docs/gams-roots-structured-ten-validation.json'


class RootsStructuredTests(unittest.TestCase):
    def test_all_ten_have_successful_main_only_proofs(self):
        manifest = json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())
        drivers = [d for d in manifest['drivers'] if d.get('validation_path') == REPORT]
        proofs = json.loads((ROOT/REPORT).read_text())['drivers']
        self.assertEqual(len(drivers), 10)
        inverse = next(d for d in drivers if d['id'] == 'specialmatrices-circulant-inverses-reference')
        self.assertEqual(inverse['gams_code'], 'D2a1')
        self.assertEqual({d['id'] for d in drivers}, {p['driver_id'] for p in proofs})
        for proof in proofs:
            source = (ROOT/'fpm_catalog/gams-drivers'/(proof['driver_id']+'.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), proof['source_sha256'])
            self.assertTrue(proof['ok'] and proof['library_reused'])
            self.assertEqual(set(proof['compiled_targets']), {'main.f90', 'playground-main'})

    def test_manufactured_families_have_unique_bracketed_roots(self):
        functions = [lambda z: z*(1+z*z), lambda z: math.expm1(z), math.sin,
                     math.log1p, lambda z: z/(2+z*z)]
        for fun in functions:
            self.assertEqual(fun(0), 0)
            self.assertLess(fun(-0.75), 0)
            self.assertGreater(fun(1.25), 0)
            for k in range(1, 100):
                z = -0.75+2*k/100
                if abs(z) > 1e-12:
                    self.assertGreater(fun(z)*z, 0)

    def test_poisson_spectrum_matches_stencil_trace(self):
        for nx in range(2, 6):
            for ny in range(2, 5):
                hx, hy = 2/(nx+1), 3/(ny+1)
                spectrum = [-4*(math.sin(math.pi*i/(2*(nx+1)))/hx)**2
                            -4*(math.sin(math.pi*j/(2*(ny+1)))/hy)**2
                            for j in range(1, ny+1) for i in range(1, nx+1)]
                self.assertTrue(all(x < 0 for x in spectrum))
                self.assertAlmostEqual(sum(spectrum), nx*ny*(-2/hx**2-2/hy**2), places=10)

    def test_circulant_dft_convention_and_dominance(self):
        import cmath
        for n in range(3, 18):
            c = [((3*i) % 7-3)/16 for i in range(1, n+1)]
            c[0] = 4+sum(abs(x) for x in c)
            self.assertGreater(c[0], sum(abs(x) for x in c[1:]))
            for j in range(n):
                value = sum(c[k]*cmath.exp(-2j*math.pi*j*k/n) for k in range(n))
                v = [cmath.exp(2j*math.pi*j*i/n) for i in range(n)]
                for i in range(n):
                    product = sum(c[(i-k) % n]*v[k] for k in range(n))
                    self.assertLess(abs(product-value*v[i]), 1e-11)

    def test_retained_probes_are_reproducible_and_not_successes(self):
        folder = ROOT/'docs/gams-candidates/roots-structured-api'
        results = list(folder.glob('*-result.json'))
        self.assertEqual(len(results), 8)
        for path in results:
            record = json.loads(path.read_text())
            source = path.with_name(path.name.replace('-result.json', '.f90')).read_text()
            self.assertEqual(hashlib.sha256(source.encode()).hexdigest(), record['source_sha256'])
            self.assertFalse(record['result']['ok'])
            self.assertTrue(record['result']['stages'][0]['ok'])
            self.assertFalse(record['result']['stages'][1]['ok'])
