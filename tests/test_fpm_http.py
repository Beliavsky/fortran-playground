"""Optional HTTP adapter checks when FastAPI and its test client are installed."""
import importlib.util
import unittest

from fpm_api import Service, create_api


@unittest.skipUnless(importlib.util.find_spec('fastapi') and importlib.util.find_spec('httpx'),
                     'FastAPI and httpx required for HTTP adapter tests')
class HttpTests(unittest.TestCase):
    def test_origins_payloads_polling_and_cancellation(self):
        from fastapi.testclient import TestClient
        from test_fpm_service import MemoryStore, Runner, PAYLOAD

        store, runner = MemoryStore(), Runner()
        with TestClient(create_api(Service(store, runner), ['https://play.example'])) as client:
            self.assertEqual(client.get('/api/health').json()['fpm'], '0.12.0')
            self.assertEqual(client.post('/api/jobs', json=PAYLOAD).status_code, 403)
            headers = {'Origin': 'https://play.example'}
            preflight = client.options('/api/jobs', headers={**headers, 'Access-Control-Request-Method': 'POST',
                                                            'Access-Control-Request-Headers': 'Content-Type'})
            self.assertEqual(preflight.status_code, 200)
            self.assertEqual(client.post('/api/jobs', content='bad', headers=headers).status_code, 415)
            json_headers = {**headers, 'Content-Type': 'application/json'}
            self.assertEqual(client.post('/api/jobs', content='{', headers=json_headers).status_code, 400)
            self.assertEqual(client.post('/api/jobs', content='[' + ' ' * 1250000, headers=json_headers).status_code, 413)
            response = client.post('/api/jobs', json=PAYLOAD, headers=headers)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.headers['access-control-allow-origin'], headers['Origin'])
            self.assertEqual(response.headers['cache-control'], 'no-store')
            identifier = response.json()['id']
            self.assertEqual(client.get('/api/jobs/' + identifier, headers=headers).json()['state'], 'running')
            self.assertEqual(client.post('/api/jobs/' + identifier + '/cancel', headers=headers).status_code, 200)
            self.assertTrue(store.data['cancel:' + identifier])
            self.assertEqual(client.get('/api/jobs/' + 'x' * 43, headers=headers).status_code, 404)
            runner.result = {'ok': True, 'stages': []}
            self.assertTrue(client.get('/api/jobs/' + identifier, headers=headers).json()['result']['ok'])


if __name__ == '__main__':
    unittest.main()
