"""Driver evidence must prove execution and reuse, rather than just compilation."""
import copy
import json
from pathlib import Path
import unittest

from xverify_gams_drivers import verification_record

ROOT = Path(__file__).resolve().parents[1]


class DriverVerificationTests(unittest.TestCase):
    def evidence(self):
        driver = next(d for d in json.loads((ROOT/'fpm_catalog/gams-drivers.json').read_text())['drivers']
                      if d['id'] == 'nonlin-rosenbrock-bfgs')
        row = next(r for r in json.loads((ROOT/'docs/gams-g1-validation.json').read_text())['drivers']
                   if r['driver_id'] == driver['id'])
        result = {'ok': row['ok'], 'compiler': row['compiler'], 'fpm': row['fpm'],
                  'cache': {'library_reused': row['library_reused']}, 'stages': copy.deepcopy(row['stages'])}
        return driver, row, result

    def test_saved_sandbox_run_proves_current_main_and_library_reuse(self):
        driver, saved, result = self.evidence()
        record = verification_record(driver, result)
        self.assertEqual(record['source_sha256'], saved['source_sha256'])
        self.assertEqual(record['compiled_targets'], ['main.f90', 'playground-main'])
        self.assertTrue(record['library_reused'])

    def test_rejects_build_only_success_failed_run_and_library_recompilation(self):
        driver, _, good = self.evidence()
        for failure in ['build marker', 'nonzero exit', 'no reuse', 'library rebuilt', 'wrong compiler']:
            result = copy.deepcopy(good)
            run = next(s for s in result['stages'] if s['name'] == 'Run')
            if failure == 'build marker':
                result['stages'][0]['stdout'] += run['stdout']
                run['stdout'] = ''
            elif failure == 'nonzero exit':
                run['exit_code'] = 1
            elif failure == 'no reuse':
                result['cache']['library_reused'] = False
            elif failure == 'library rebuilt':
                result['stages'][0]['stdout'] += '[100%] nonlin.f90 done.\n'
            else:
                result['compiler'] = 'GNU Fortran 12.2.0'
            with self.subTest(failure=failure), self.assertRaises(ValueError):
                verification_record(driver, result)
