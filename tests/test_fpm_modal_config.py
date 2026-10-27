"""Reimport the deployment module as its containers do, without Modal credentials."""
import os
import asyncio
from pathlib import Path
import runpy
import types
import json
import tempfile
import unittest
from unittest.mock import patch
from xdeploy_fpm import verify_api

ROOT = Path(__file__).resolve().parents[1]


class Image:
    def __init__(self):
        self.environment = {}
        self.files = []

    @classmethod
    def from_registry(cls, *args, **kwargs): return cls()
    @classmethod
    def debian_slim(cls, *args, **kwargs): return cls()
    def pip_install(self, *args, **kwargs): return self
    def run_commands(self, *args, **kwargs): return self
    def add_local_file(self, source, target, **kwargs):
        self.files.append((str(source), target))
        return self
    def add_local_dir(self, *args, **kwargs): return self
    def env(self, environment):
        self.environment.update(environment)
        return self


class App:
    def __init__(self, name): pass
    def function(self, **spec):
        def decorate(function):
            function.deployment_spec = spec
            return function
        return decorate


class ModalConfigTests(unittest.TestCase):
    def test_large_catalog_uses_image_file_and_short_environment_values(self):
        from xdeploy_fpm import configure_routing
        entries = {str(index): {'key': 'a' * 24, 'image': 'library-' + str(index), 'revision': 'b' * 40,
                                'records': [{'repository': 'owner/' + 'x' * 1000}],
                                'verification': 'private operator report'} for index in range(100)}
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ):
            path = configure_routing(entries, temporary)
            self.assertGreater(path.stat().st_size, 32767)
            self.assertNotIn('FPM_PRECOMPILED', os.environ)
            self.assertLess(len(os.environ['FPM_PRECOMPILED_FILE']), 32767)
            local = self.load(True, {'FPM_PRECOMPILED_FILE': str(path)})
            expected = json.loads(path.read_text(encoding='utf-8'))
            self.assertEqual(local['PRECOMPILED'], expected)
            self.assertNotIn('verification', expected['0'])
            for name in ('api_image', 'broker_image'):
                image = local[name]
                self.assertIn((str(path), '/root/fpm-precompiled.json'), image.files)
                self.assertNotIn('FPM_PRECOMPILED', image.environment)
                self.assertTrue(all(len(value) < 32767 for value in image.environment.values()))
                original = Path.read_text
                def read(source, *args, **kwargs):
                    if source.as_posix() == '/root/fpm-precompiled.json':
                        return json.dumps(expected)
                    return original(source, *args, **kwargs)
                with patch.object(Path, 'read_text', read):
                    remote = self.load(False, image.environment)
                self.assertEqual(remote['PRECOMPILED'], expected)
                self.assertEqual(remote['IMAGE_NAME'], local['IMAGE_NAME'])

    def load(self, local, environment):
        modal = types.SimpleNamespace(App=App, Image=Image, is_local=lambda: local,
            Dict=types.SimpleNamespace(from_name=lambda *args, **kwargs: None),
            Secret=types.SimpleNamespace(from_name=lambda name, **kwargs: name),
            concurrent=lambda **kwargs: lambda function: function,
            asgi_app=lambda **kwargs: lambda function: function)
        with patch.dict(os.environ, environment, clear=True), patch.dict('sys.modules', {'modal': modal}):
            return runpy.run_path(str(ROOT / 'xfpm_modal.py'))

    def test_owner_secret_dependencies_match_in_local_and_container_imports(self):
        for secret in ('', 'p2f-owner'):
            with self.subTest(secret=secret):
                local = self.load(True, {'FPM_OWNER_SECRET': secret, 'FPM_ENABLED_COMPILERS': '["gfortran","ifx","flang"]',
                    'FPM_PRECOMPILED': '{"fortran-lapack":{"image":"pinned-cache","revision":"abc"}}'})
                for image_name in ('api_image', 'broker_image'):
                    environment = local[image_name].environment
                    self.assertEqual(environment['FPM_OWNER_SECRET'], secret)
                    remote = self.load(False, environment)
                    self.assertEqual(remote['IMAGE_NAME'], local['IMAGE_NAME'])
                    self.assertEqual(remote['RECIPE_ID'], local['RECIPE_ID'])
                    self.assertEqual(remote['ENABLED_COMPILERS'], local['ENABLED_COMPILERS'])
                    self.assertEqual(remote['PRECOMPILED'], local['PRECOMPILED'])
                    self.assertEqual(remote['api'].deployment_spec['secrets'],
                                     local['api'].deployment_spec['secrets'])
                    self.assertEqual(remote['run_job'].deployment_spec['secrets']
                                     if 'secrets' in remote['run_job'].deployment_spec else [], [])

    def test_deployment_checks_real_http_health_and_cors(self):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"ok":true,"fpm":"0.12.0"}'
        response.headers = {'Access-Control-Allow-Origin': 'https://example.org'}
        response.__enter__.return_value = response
        with patch('xdeploy_fpm.urlopen', return_value=response) as open_url:
            verify_api('https://test.modal.run', 'https://example.org')
            with self.assertRaisesRegex(ValueError, 'older FPM API'):
                verify_api('https://test.modal.run', 'https://example.org', translated_r=True)
            response.read.return_value = b'{"ok":true,"fpm":"0.12.0","features":{"translated_r":true}}'
            verify_api('https://test.modal.run', 'https://example.org', translated_r=True)
            with self.assertRaisesRegex(ValueError, 'compiler catalog'):
                verify_api('https://test.modal.run', 'https://example.org', ['gfortran', 'ifx'])
            self.assertEqual(open_url.call_args.args[0].full_url, 'https://test.modal.run/api/health')
            response.headers = {}
            with self.assertRaisesRegex(ValueError, 'browser origin'):
                verify_api('https://test.modal.run', 'https://example.org')
            response.headers = {'Access-Control-Allow-Origin': 'https://example.org'}
            response.read.return_value = b'{"ok":false}'
            with self.assertRaisesRegex(ValueError, 'healthy FPM'):
                verify_api('https://test.modal.run', 'https://example.org')

    def test_pending_call_uses_builtin_timeout_then_returns_completed_result(self):
        from unittest.mock import AsyncMock
        module = self.load(True, {})
        getter = AsyncMock(side_effect=[TimeoutError(), {'ok': True, 'stages': []}])
        module['modal'].FunctionCall = types.SimpleNamespace(from_id=lambda identifier:
            types.SimpleNamespace(get=types.SimpleNamespace(aio=getter)))
        runner = module['Runner']()
        self.assertIsNone(asyncio.run(runner.poll('pending-call')))
        self.assertEqual(asyncio.run(runner.poll('pending-call')), {'ok': True, 'stages': []})
        getter.assert_called_with(timeout=0)

    def test_exact_cached_consumer_skips_all_downloads(self):
        import json
        from unittest.mock import MagicMock
        from fpm_cache import catalog, cache_identity
        module = self.load(True, {})
        package = catalog()[0]
        function = module['execute_job']
        entry = {'key': cache_identity(package, module['RECIPE_ID']), 'image': 'verified-image',
                 'revision': package['revision'], 'records': [{'repository': package['repository']}]}
        sandbox = MagicMock()
        sandbox.poll.return_value = 0
        sandbox.stdout.read.return_value = '{"ok":true,"stages":[]}'
        module['modal'].Sandbox = types.SimpleNamespace(create=MagicMock(return_value=sandbox))
        module['modal'].Image.from_name = MagicMock(return_value='selected-image')
        request = {'url': 'https://github.com/' + package['repository'], 'revision': package['revision'],
                   'source': 'program main\nend program'}
        with patch.dict(function.__globals__, {'PRECOMPILED': {package['id']: entry}}), \
             patch('fpm_sources.Preparer.prepare', side_effect=AssertionError('Cache hit must not download')):
            result = function('test-job', request, cancelled=lambda: False)
        self.assertTrue(result['ok'], result)
        message = json.loads(sandbox.stdin.write.call_args.args[0])
        self.assertEqual(message['cache_key'], entry['key'])
        self.assertNotIn('bundle', message)
        module['modal'].Image.from_name.assert_called_once_with('verified-image')
        sandbox.terminate.assert_called_once()

    def test_translated_sources_reach_existing_worker_protocol(self):
        import json
        from unittest.mock import MagicMock
        from fpm_collections import R_REPOSITORY
        module = self.load(True, {})
        sandbox = MagicMock()
        sandbox.poll.return_value = 0
        sandbox.stdout.read.return_value = '{"ok":true,"stages":[]}'
        module['modal'].Sandbox = types.SimpleNamespace(create=MagicMock(return_value=sandbox))
        module['modal'].Image.from_name = MagicMock(return_value='clean-image')
        request = {'url': 'https://github.com/' + R_REPOSITORY, 'revision': 'a' * 40,
                   'subdirectory': 'Metrics', 'workflow': 'package', 'action': 'run', 'target': 'demo_* other'}
        with patch('fpm_collections.TranslatedRPreparer.prepare', return_value=('r/Metrics', [])) as prepare:
            result = module['execute_job']('translated-job', request, cancelled=lambda: False)
        self.assertEqual(prepare.call_args.args[0]['target'], '')
        self.assertTrue(result['ok'], result)
        message = json.loads(sandbox.stdin.write.call_args.args[0])
        self.assertEqual(message['root'], 'r/Metrics')
        self.assertNotIn('subdirectory', message['request'])
        self.assertEqual(message['request']['target'], 'demo_* other')
        self.assertIn('bundle', message)
        self.assertNotIn('cache_key', message)


if __name__ == '__main__':
    unittest.main()
