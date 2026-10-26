"""Reimport the deployment module as its containers do, without Modal credentials."""
import os
from pathlib import Path
import runpy
import types
import unittest
from unittest.mock import patch
from xdeploy_fpm import verify_api

ROOT = Path(__file__).resolve().parents[1]


class Image:
    def __init__(self):
        self.environment = {}

    @classmethod
    def from_registry(cls, *args, **kwargs): return cls()
    @classmethod
    def debian_slim(cls, *args, **kwargs): return cls()
    def pip_install(self, *args, **kwargs): return self
    def run_commands(self, *args, **kwargs): return self
    def add_local_file(self, *args, **kwargs): return self
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
                local = self.load(True, {'FPM_OWNER_SECRET': secret})
                for image_name in ('api_image', 'broker_image'):
                    environment = local[image_name].environment
                    self.assertEqual(environment['FPM_OWNER_SECRET'], secret)
                    remote = self.load(False, environment)
                    self.assertEqual(remote['IMAGE_NAME'], local['IMAGE_NAME'])
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
            self.assertEqual(open_url.call_args.args[0].full_url, 'https://test.modal.run/api/health')
            response.headers = {}
            with self.assertRaisesRegex(ValueError, 'browser origin'):
                verify_api('https://test.modal.run', 'https://example.org')
            response.headers = {'Access-Control-Allow-Origin': 'https://example.org'}
            response.read.return_value = b'{"ok":false}'
            with self.assertRaisesRegex(ValueError, 'healthy FPM'):
                verify_api('https://test.modal.run', 'https://example.org')


if __name__ == '__main__':
    unittest.main()
