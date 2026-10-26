"""Verify compiler selection, pending polling, and results via an ephemeral HTTP API."""
import json
import os
from pathlib import Path
import time
from urllib.request import Request, urlopen


def main():
    # No owner secret is needed; exercise public admission with four small jobs.
    names = ['gfortran', 'gfortran17', 'ifx', 'flang']
    os.environ['FPM_ENABLED_COMPILERS'] = json.dumps(names)
    import modal
    from xfpm_modal import app, api, runtime_images, image_name
    from fpm_probe import verify_image
    images = runtime_images(names)
    records = []
    with modal.enable_output(), app.run():
        for name in names:
            image = images[name].build(app)
            verify_image(app, image, name)
            image.publish(image_name(name))
        url = api.get_web_url()

        def request(path, payload=None):
            body = None if payload is None else json.dumps(payload).encode()
            req = Request(url + path, data=body, headers={
                'Origin': 'https://beliavsky.github.io', 'Content-Type': 'application/json'})
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read())

        health = request('/api/health')
        assert set(health['compilers']) == set(names), health
        example = json.loads(Path('site/fpm/examples.json').read_text())[0]
        for name in names:
            job = request('/api/jobs', {'compiler': name, 'url': 'https://github.com/' + example['repository'],
                'revision': example['revision'], 'source': example['source']})
            pending = 0
            deadline = time.monotonic() + 400
            while time.monotonic() < deadline:
                response = request('/api/jobs/' + job['id'])
                if response['state'] == 'done':
                    result = response['result']
                    assert result.get('ok') and result.get('compiler_id') == name, result
                    assert 'PASS quadrature' in json.dumps(result), result
                    records.append({'compiler': name, 'pending_polls': pending, 'result': result})
                    print(f'{name}: HTTP submission/poll/result PASS; pending polls: {pending}', flush=True)
                    break
                pending += 1
                time.sleep(1)
            else:
                request('/api/jobs/' + job['id'] + '/cancel', {})
                raise TimeoutError('HTTP verification did not finish.')
    Path('docs/fpm-http-validation.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
