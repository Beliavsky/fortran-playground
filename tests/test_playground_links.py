from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

from xplayground_links import build_link_page


ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.hrefs, self.tags = [], []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == 'a':
            self.hrefs.append(dict(attrs)['href'])


class PlaygroundLinkTests(unittest.TestCase):
    def test_sources_round_trip_and_html_is_escaped(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = '! Example: <img src=x> & "title"\r\n! Unicode: caf\u00e9 \u03bb\r\nprint *, "a+b & 50% # ?"\r\nend\r\n'
            (root / 'a&b.F90').write_bytes(b'\xef\xbb\xbf' + source.encode('utf-8'))
            (root / 'ignored.txt').write_text('ignored')
            output = root / 'docs/index.html'
            count, warnings = build_link_page(root, output, title='<script>title</script>',
                playground_url='https://example.org/custom/?old=yes#old')
            self.assertEqual((count, warnings), (1, []))
            page = output.read_text(encoding='utf-8')
            links = Links(page)
            self.assertNotIn('script', links.tags)
            self.assertNotIn('img', links.tags)
            self.assertIn('a&amp;b.F90', page)
            url = urlsplit(links.hrefs[0])
            self.assertEqual((url.scheme, url.netloc, url.path, url.query), ('https', 'example.org', '/custom/', ''))
            self.assertEqual(unquote(url.fragment.removeprefix('code=')), source)
            if shutil.which('node'):
                result = subprocess.run(['node', '--input-type=module', '-e',
                    "import {sourceFromHash} from './site/sharing.mjs'; "
                    "process.stdout.write(sourceFromHash(new URL(process.argv[1]).hash));", links.hrefs[0]],
                    cwd=ROOT, capture_output=True, check=True)
                self.assertEqual(result.stdout.decode('utf-8'), source)

    def test_recursion_order_extensions_and_repeated_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'nested').mkdir()
            for filename in ['b.f95', 'a.f03', 'nested/a.F08']:
                (root / filename).write_bytes(('print *, "' + filename + '"\nend\n').encode('utf-8'))
            output = root / 'index.html'
            self.assertEqual(build_link_page(root, output)[0], 2)
            self.assertEqual(build_link_page(root, output, recursive=True)[0], 3)
            page = output.read_text()
            self.assertIn('nested/a.F08', page)
            sources = [unquote(urlsplit(href).fragment[5:]) for href in Links(page).hrefs]
            self.assertEqual(sources, [f'print *, "{name}"\nend\n' for name in ['a.f03', 'b.f95', 'nested/a.F08']])

    def test_skip_invalid_files_and_accept_utf8_byte_boundary(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'empty.f90').write_text(' \n')
            (root / 'large.f90').write_text('x'*100001)
            (root / 'bad_utf8.f90').write_bytes(b'\xff')
            (root / 'unicode_large.f90').write_bytes(('\u03bb'*50001).encode('utf-8'))
            (root / 'boundary.f90').write_bytes(('\u03bb'*50000).encode('utf-8'))
            count, warnings = build_link_page(root, root / 'index.html')
            self.assertEqual(count, 1)
            self.assertEqual(sum(message.startswith('Skipped ') for message in warnings), 4)
            self.assertTrue(any('long link' in message for message in warnings))

    def test_empty_directory_and_failures_do_not_overwrite_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / 'index.html'
            self.assertEqual(build_link_page(root, output), (0, []))
            self.assertIn('No eligible Fortran examples', output.read_text())
            source = root / 'source.f90'
            source.write_text('end\n')
            with self.assertRaisesRegex(ValueError, 'overwrite'):
                build_link_page(root, source)
            self.assertEqual(source.read_text(), 'end\n')
            for url in ['javascript:alert(1)', 'https://user:secret@example.org/']:
                with self.assertRaises(ValueError):
                    build_link_page(root, output, playground_url=url)
            with self.assertRaisesRegex(ValueError, 'Not a directory'):
                build_link_page(root / 'missing', output)

    def test_command_line(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'source.f90').write_text('print *, 42\nend\n')
            (root / 'empty.f90').write_text('')
            output = root / 'docs/index.html'
            result = subprocess.run([sys.executable, str(ROOT / 'xplayground_links.py'), str(root),
                '--recursive', '--output', str(output), '--title', 'My examples'],
                capture_output=True, text=True, check=True)
            self.assertIn('Wrote 1 playground links', result.stdout)
            self.assertIn('Skipped empty.f90', result.stderr)
            self.assertIn('<h1>My examples</h1>', output.read_text())


if __name__ == '__main__':
    unittest.main()
