"""Client-side source downloads never require or forward service credentials."""
from contextlib import redirect_stdout, redirect_stderr
import hashlib
from io import BytesIO, StringIO
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

import xplayground_run as runner

URL = 'https://example.org/module.f90'
MODULE = 'module sample\ncontains\ninteger function answer()\nanswer=42\nend function\nend module\n'
MAIN = 'program main\nuse sample\nprint *, answer()\nend program\n'


class Response(BytesIO):
    def __init__(self, body=b'', status=200, **headers):
        super().__init__(body)
        self.status, self.headers = status, headers

    def getheader(self, key, default=None):
        return self.headers.get(key, default)


class DownloadTests(unittest.TestCase):
    def connection(self, response):
        connection = Mock()
        connection.getresponse.return_value = response
        return connection

    def test_normalized_snapshot_and_anonymous_headers(self):
        response = Response(b'\xef\xbb\xbf' + MODULE.replace('\n', '\r\n').encode())
        connection = self.connection(response)
        with patch.object(runner, 'SourceConnection', return_value=connection) as factory:
            source, final, digest = runner.download_source(URL)
        self.assertEqual(source, MODULE)
        self.assertEqual(final, URL)
        self.assertEqual(digest, hashlib.sha256(MODULE.encode()).hexdigest())
        self.assertEqual(factory.call_args.args, ('example.org',))
        self.assertEqual(factory.call_args.kwargs['port'], 443)
        headers = connection.request.call_args.kwargs['headers']
        self.assertEqual(set(headers), {'Accept', 'Accept-Encoding', 'User-Agent'})
        connection.close.assert_called_once()
        self.assertTrue(response.closed)

    def test_invalid_urls_are_rejected_before_connecting(self):
        for value in ['http://example.org/x', 'ftp://example.org/x', 'file:///x', 'https:missing',
                      'https://user:secret@example.org/x', URL + '#part', 'https://example.org:8443/x',
                      'https://example.org:bad/x', 'https://example.org/a b', URL + '\n', URL + '\0',
                      'https://example.org/\u03bb', URL + '?' + 'x' * 2048]:
            with self.subTest(url=value), patch.object(runner, 'SourceConnection') as connection:
                with self.assertRaises(ValueError):
                    runner.download_source(value)
                connection.assert_not_called()

    def test_relative_redirect_and_query(self):
        connections = [self.connection(Response(status=302, Location='../raw.f90?version=1')),
                       self.connection(Response(MODULE.encode()))]
        with patch.object(runner, 'SourceConnection', side_effect=connections):
            _, final, _ = runner.download_source('https://example.org/files/view')
        self.assertEqual(final, 'https://example.org/raw.f90?version=1')
        self.assertEqual(connections[1].request.call_args.args, ('GET', '/raw.f90?version=1'))
        for connection in connections:
            connection.close.assert_called_once()

    def test_redirect_validation_and_finite_hops(self):
        for location in ['http://example.org/plain', 'https://user:secret@example.org/x', 'file:///x']:
            connection = self.connection(Response(status=301, Location=location))
            with patch.object(runner, 'SourceConnection', return_value=connection) as factory:
                with self.assertRaises(ValueError):
                    runner.download_source(URL)
                self.assertEqual(factory.call_count, 1)
        with patch.object(runner, 'SourceConnection', side_effect=lambda *a, **k: self.connection(Response(status=302, Location=URL))) as factory:
            with self.assertRaisesRegex(ValueError, 'too many redirects'):
                runner.download_source(URL)
            self.assertEqual(factory.call_count, 6)

    def test_invalid_responses_are_rejected(self):
        cases = [Response(status=404), Response(status=302),
                 Response(b'<html>page</html>', **{'Content-Type': 'text/html'}),
                 Response(b'<!doctype html><html>page', **{'Content-Type': 'text/plain'}),
                 Response(b'compressed', **{'Content-Encoding': 'gzip'}),
                 Response(b'end', **{'Content-Length': 'invalid'}),
                 Response(b'end', **{'Content-Length': '-1'}),
                 Response(b'end', **{'Content-Length': '100004'}),
                 Response(b'end', **{'Content-Length': '99'}),
                 Response(b'x' * 100004), Response(b'\xff'), Response(b' \n'), Response(b'\0end')]
        for response in cases:
            connection = self.connection(response)
            with self.subTest(headers=response.headers, status=response.status), patch.object(runner, 'SourceConnection', return_value=connection):
                with self.assertRaises(ValueError):
                    runner.download_source(URL)
                connection.close.assert_called_once()

    def test_timeout_and_network_errors(self):
        with patch.object(runner, 'SourceConnection', return_value=self.connection(Response(b'end'))), \
                patch.object(runner.time, 'monotonic', side_effect=[0, 0, 16]):
            with self.assertRaisesRegex(ValueError, 'timed out'):
                runner.download_source(URL)
        connection = self.connection(Response())
        connection.request.side_effect = TimeoutError()
        with patch.object(runner, 'SourceConnection', return_value=connection):
            with self.assertRaisesRegex(ValueError, 'HTTPS download failed'):
                runner.download_source(URL)
            connection.close.assert_called_once()


class URLSourceTests(unittest.TestCase):
    def snapshot(self, source=MODULE, url=URL):
        return source, url, hashlib.sha256(source.encode()).hexdigest()

    def test_mixed_order_provenance_and_line_mapping(self):
        with tempfile.TemporaryDirectory() as temporary:
            main = Path(temporary) / 'main.f90'
            main.write_text(MAIN)
            with patch.object(runner, 'download_source', return_value=self.snapshot()) as download:
                combined, sections = runner.combine_sources([URL, str(main)])
            download.assert_called_once_with(URL)
        self.assertLess(combined.index(MODULE), combined.index(MAIN))
        self.assertIn('! SHA-256: ' + sections[0].sha256, combined)
        self.assertEqual(sections[0].first_line, 3)
        self.assertEqual(sections[0].url, URL)
        self.assertEqual(runner.diagnostic_locations('input_p.f90:4:1: error', sections),
                         [f'input_p.f90:4 -> {URL}:2'])

    def test_single_remote_source_has_provenance_and_duplicate_is_not_refetched(self):
        with patch.object(runner, 'download_source', return_value=self.snapshot()) as download:
            source, _ = runner.combine_sources([URL])
            self.assertTrue(source.startswith('! --- Source: https://'))
        with patch.object(runner, 'download_source', return_value=self.snapshot()) as download:
            with self.assertRaisesRegex(ValueError, 'more than once'):
                runner.combine_sources([URL, URL])
            download.assert_called_once()
        alias = 'https://example.org/redirect'
        with patch.object(runner, 'download_source', return_value=self.snapshot()) as download:
            with self.assertRaisesRegex(ValueError, 'more than once'):
                runner.combine_sources([alias, URL])
            download.assert_called_once()

    def test_combined_limit_includes_remote_headers(self):
        with patch.object(runner, 'download_source', return_value=self.snapshot('x' * 100000)):
            with self.assertRaisesRegex(ValueError, 'Combined source'):
                runner.combine_sources([URL])

    def test_main_reuses_snapshot_for_all_compilers_and_list(self):
        session = {'token': 'private', 'compilers': ['gfortran', 'ifx'],
                   'compiler_options': {name: {'presets': {'default': []}, 'standards': {}, 'extras': {}}
                                        for name in ['gfortran', 'ifx']}}
        client = Mock(service_url='https://execute.example.org')
        client.connect.return_value = session
        client.run_job.return_value = ({'ok': True, 'execution': {'stdout': '42\n'}}, 1)
        for terse in [False, True]:
            client.run_job.reset_mock()
            output, errors = StringIO(), StringIO()
            with tempfile.TemporaryDirectory() as temporary:
                main = Path(temporary) / 'main.f90'
                main.write_text(MAIN)
                with patch.object(runner, 'download_source', return_value=self.snapshot()) as download, \
                        patch.object(runner, 'PlaygroundClient', return_value=client), redirect_stdout(output), redirect_stderr(errors):
                    status = runner.main([URL, str(main), '--compilers', 'gfortran', 'ifx', '--list', *(['--terse'] if terse else [])])
            self.assertEqual(status, 0, errors.getvalue())
            download.assert_called_once_with(URL)
            calls = client.run_job.call_args_list
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0].args[0], calls[1].args[0])
            self.assertEqual(output.getvalue().count(MODULE), 1)
            self.assertIn(URL, output.getvalue())
            self.assertIn(hashlib.sha256(MODULE.encode()).hexdigest(), output.getvalue())

    def test_bad_download_does_not_contact_execution_service(self):
        with patch.object(runner, 'download_source', side_effect=ValueError('HTML; use raw source')), \
                patch.object(runner, 'PlaygroundClient') as client, redirect_stderr(StringIO()):
            self.assertEqual(runner.main([URL]), 2)
            client.assert_not_called()

    @unittest.skipUnless(shutil.which('gfortran'), 'gfortran required')
    def test_downloaded_module_and_local_main_compile(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            main = root / 'main.f90'
            main.write_text(MAIN)
            with patch.object(runner, 'download_source', return_value=self.snapshot()):
                source, _ = runner.combine_sources([URL, main])
            (root / 'combined.f90').write_text(source)
            executable = root / 'program.exe'
            build = subprocess.run(['gfortran', '-std=f2018', 'combined.f90', '-o', str(executable)],
                                   cwd=root, capture_output=True, text=True, timeout=30)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(executable)], capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout.strip(), '42')


if __name__ == '__main__':
    unittest.main()
