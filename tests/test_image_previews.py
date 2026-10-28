import base64
from io import BytesIO
import importlib.util
from pathlib import Path
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch

import fortran_image as images
from fortran_plot import valid_png


@unittest.skipUnless(importlib.util.find_spec('PIL'), 'Pillow required for PNM previews')
class ImagePreviewTests(unittest.TestCase):
    def test_ascii_binary_pbm_pgm_ppm_and_pixel_values(self):
        from PIL import Image
        samples = [(b'P1\n2 1\n0 1\n', [(255,255,255),(0,0,0)]),
                   (b'P4\n2 1\n\x40', [(255,255,255),(0,0,0)]),
                   (b'P2\n# comment\n2 1\n255\n0 127\n', [(0,0,0),(127,127,127)]),
                   (b'P5\n2 1\n255\n\x00\x7f', [(0,0,0),(127,127,127)]),
                   (b'P3\n2 1\n255\n255 0 0 0 255 0\n', [(255,0,0),(0,255,0)]),
                   (b'P6\n2 1\n255\n\xff\x00\x00\x00\xff\x00', [(255,0,0),(0,255,0)])]
        for data, expected in samples:
            with self.subTest(magic=data[:2]):
                converted = images.pnm_to_png(data)
                self.assertTrue(valid_png(converted))
                with Image.open(BytesIO(converted)) as image:
                    self.assertEqual(image.size, (2,1))
                    self.assertEqual([image.getpixel((i,0)) for i in range(2)], expected)

    def test_changed_files_and_shared_png_pnm_limits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root/'old.ppm').write_bytes(b'P3\n1 1\n255\n255 0 0\n')
            before = images.snapshot(root)
            for i in range(5):
                (root/f'{i}.ppm').write_bytes(b'P6\n1 1\n255\n\xff\x00\x00')
            (root/'already.png').write_bytes(images.pnm_to_png(b'P3\n1 1\n255\n0 0 0\n'))
            result = images.collect_plots(root,before)
            self.assertEqual(len(result['plots']),4)
            self.assertEqual(result['plots'][0]['name'],'already.png')
            self.assertFalse(any(p['name'].startswith('old.ppm') for p in result['plots']))
            self.assertTrue(result['plot_notes'])
            self.assertTrue(all(valid_png(base64.b64decode(p['data'])) for p in result['plots']))
            with patch('fortran_plot.MAX_PNG_BYTES', 1):
                self.assertEqual(images.collect_plots(root)['plots'],[])

    def test_rejects_bad_truncated_oversized_and_non_pnm_content(self):
        for data in [b'P6\n4097 1\n255\n', b'P6\n4096 4096\n255\n',
                     b'P6\n1000000 1000000\n255\n', b'P6\n2 1\n255\n\xff',
                     b'<svg/>', b'P7\n', b'P3\n1 1\n255\nnot pixels']:
            with self.subTest(data=data[:50]):
                with self.assertRaises((ValueError,OSError,SyntaxError)):
                    images.pnm_to_png(data)
        with patch('fortran_image.MAX_PNM_BYTES', 2):
            with self.assertRaises(ValueError): images.pnm_to_png(b'P3\n')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); (root/'invalid.ppm').write_bytes(b'<svg/>')
            self.assertEqual(images.collect_plots(root)['plots'],[])
            self.assertTrue(images.collect_plots(root)['plot_notes'])

    def test_nested_files_symlinks_and_old_files_are_omitted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary); (root/'nested').mkdir()
            target=root/'nested/real.ppm';target.write_bytes(b'P3\n1 1\n255\n0 0 0\n')
            try: (root/'link.ppm').symlink_to(target)
            except OSError: pass
            self.assertEqual(images.collect_plots(root)['plots'],[])

    def test_missing_pillow_is_a_note_and_ordinary_jobs_do_not_import_it(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            with patch.dict(sys.modules, {'PIL':None}):
                self.assertEqual(images.collect_plots(root),{'plots':[],'plot_notes':[]})
                (root/'image.ppm').write_bytes(b'P3\n1 1\n255\n0 0 0\n')
                result=images.collect_plots(root)
                self.assertEqual(result['plots'],[])
                self.assertIn('install Pillow',result['plot_notes'][0])

    @unittest.skipUnless(shutil.which('gfortran'), 'GNU Fortran required')
    def test_real_local_source_and_fpm_jobs_return_pnm_previews(self):
        from xfortran_run import build_and_run
        from fortran_fpm import execute_project
        source = '''program main
implicit none
integer :: unit
open(newunit=unit,file='generated.ppm',status='replace')
write(unit,'(a)') 'P3','1 1','255','255 0 0'
close(unit)
print *, 'Generated a red pixel'
end program
'''
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            main=root/'main.f90';main.write_text(source)
            result=build_and_run([main],'gfortran',cwd=root,run_timeout=30)
            self.assertTrue(result['ok'],result)
            self.assertEqual(len(result['plots']),1)
            self.assertIn('PNG preview',result['plots'][0]['name'])
            if shutil.which('fpm'):
                (root/'fpm.toml').write_text('name="image-test"\n')
                (root/'src').mkdir()
                (root/'src/sample.f90').write_text('module sample\nend module\n')
                result=execute_project(root,'gfortran',options={'source':source})
                self.assertTrue(result['ok'],result)
                self.assertEqual(len(result['plots']),1)
                self.assertTrue(valid_png(base64.b64decode(result['plots'][0]['data'])))


if __name__=='__main__': unittest.main()
