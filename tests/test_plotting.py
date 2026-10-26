import base64
import importlib.util
import os
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import zlib

import fortran_plot as plotting

ROOT = Path(__file__).resolve().parents[1]


def png():
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(b'\0\xff\0\0')) + chunk(b'IEND', b''))


class PlotTests(unittest.TestCase):
    def test_source_pin_and_default_kind(self):
        source = plotting.module_source()
        self.assertNotIn('#ifdef', source)
        self.assertIn('pyplot_wp = real64', source)
        self.assertTrue(plotting.uses_pyplot('use, non_intrinsic :: &\n & pyplot_module'))
        self.assertFalse(plotting.uses_pyplot('! use pyplot_module\nprint *, "hello"'))
        environment = plotting.plotting_environment({'GASNET_PSHM_NODES': '2'})
        self.assertEqual(environment['GASNET_PSHM_NODES'], '2')
        self.assertTrue(environment['PATH'].endswith(os.environ.get('PATH', '')))
        self.assertEqual(environment['MPLBACKEND'], 'Agg')

    def test_png_bounds_corruption_changed_files_and_safe_download_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'old.png').write_bytes(png())
            before = plotting.snapshot(root)
            (root / 'new.png').write_bytes(png())
            (root / 'fake.png').write_text('<svg onload="alert(1)"></svg>')
            data = plotting.collect_plots(root, before)
            self.assertEqual([p['name'] for p in data['plots']], ['new.png'])
            self.assertTrue(data['plot_notes'])
            self.assertFalse(plotting.valid_png(png()[:-1]))
            self.assertFalse(plotting.valid_png(png() + b'junk'))
            animation = b'acTL' + struct.pack('>II', 10000, 0)
            animation = struct.pack('>I', 8) + animation + struct.pack('>I', zlib.crc32(animation) & 0xffffffff)
            self.assertFalse(plotting.valid_png(png()[:33] + animation + png()[33:]))
            plot = {**data['plots'][0], 'name': '../../outside.png'}
            saved = plotting.save_plots({'plots': [plot]}, root / 'download', 'gfortran')
            self.assertEqual(saved[0].parent, root / 'download/gfortran')
            self.assertEqual(saved[0].read_bytes(), png())
            for index in range(5): (root / f'{index}.png').write_bytes(png())
            result = plotting.collect_plots(root)
            self.assertEqual(len(result['plots']), 4)
            self.assertTrue(result['plot_notes'])

    def test_symlinks_and_nested_files_not_returned(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); (root / 'nested').mkdir()
            (root / 'nested/real.png').write_bytes(png())
            try: (root / 'link.png').symlink_to(root / 'nested/real.png')
            except OSError: pass
            self.assertEqual(plotting.collect_plots(root)['plots'], [])

    @unittest.skipUnless(shutil.which('gfortran') and importlib.util.find_spec('matplotlib'), 'GNU and Matplotlib required')
    def test_real_local_source_and_fpm_consumer(self):
        from xfortran_run import build_and_run
        from fortran_fpm import execute_project
        with tempfile.TemporaryDirectory(prefix='plot test ') as temporary:
            root = Path(temporary)
            result = build_and_run([ROOT / 'docs/examples/plot_trig.f90'], 'gfortran', cwd=root, run_timeout=30)
            self.assertTrue(result['ok'], result)
            self.assertEqual(len(result['plots']), 1)
            self.assertTrue(plotting.valid_png(base64.b64decode(result['plots'][0]['data'])))
            if shutil.which('fpm'):
                (root / 'fpm.toml').write_text('name="plot-package"\n')
                (root / 'src').mkdir()
                (root / 'src/sample.f90').write_text('module sample\nend module\n')
                result = execute_project(root, 'gfortran', options={'source': (ROOT / 'docs/examples/plot_trig.f90').read_text()})
                self.assertTrue(result['ok'], result)
                self.assertEqual(len(result['plots']), 1)
                self.assertFalse(list(root.glob('.fortran-fpm-*')))


if __name__ == '__main__': unittest.main()
