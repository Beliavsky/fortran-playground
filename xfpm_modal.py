"""Separate FPM service. Build and deploy with python xdeploy_fpm.py."""
import base64
from io import BytesIO
import hashlib
import json
import os
from pathlib import Path
import tarfile
import tempfile
import time

import modal
from fpm_compilers import COMPILERS

ROOT = Path(__file__).resolve().parent
APP_NAME = 'fortran-playground-fpm'
app = modal.App(APP_NAME)
state = modal.Dict.from_name(APP_NAME + '-state', create_if_missing=True)
GNU_IMAGE = 'gcc:16.2.0-trixie@sha256:43978d7710a803d1c3d32f4117c1528ec7285a4ce2c0a51e982ec1a6e3d87d95'
FPM_URL = 'https://github.com/fortran-lang/fpm/releases/download/v0.12.0/fpm-0.12.0-linux-x86_64-gcc-12'
FPM_SHA256 = '576fc54fb829263b32d0e288535a2a3edc9d0478dffec84ba70445446f6d6abf'
OWNER_SECRET_NAME = os.environ.get('FPM_OWNER_SECRET', '')
ENABLED_COMPILERS = tuple(json.loads(os.environ.get('FPM_ENABLED_COMPILERS', '["gfortran"]')))
if modal.is_local():
    digest = hashlib.sha256()
    for filename in ('xfpm_modal.py', 'xfpm_worker.py', 'fpm_sources.py', 'fpm_compilers.py',
                     'fpm_toolchains/xinstall_gnu17.sh', 'fpm_toolchains/xinstall_intel.sh', 'fpm_toolchains/xinstall_flang.sh'):
        digest.update((ROOT / filename).read_bytes())
    IMAGE_NAME = 'fortran-fpm-' + digest.hexdigest()[:20]
else:
    IMAGE_NAME = os.environ['FPM_IMAGE_NAME']

def image_name(compiler):
    return IMAGE_NAME if compiler == 'gfortran' else IMAGE_NAME + '-' + compiler


def with_fpm(base, compiler):
    return (base
    .run_commands(
        "python -c \"import urllib.request,hashlib,pathlib; b=urllib.request.urlopen('" + FPM_URL + "').read(); "
        "assert hashlib.sha256(b).hexdigest() == '" + FPM_SHA256 + "'; pathlib.Path('/usr/local/bin/fpm').write_bytes(b)\"",
        'chmod 755 /usr/local/bin/fpm', 'mkdir -p /work && chmod 1777 /work',
        COMPILERS[compiler]['command'] + ' --version', 'fpm --version')
    .env({'FPM_COMPILER': compiler})
    .add_local_file(ROOT / 'fpm_sources.py', '/opt/fpm/fpm_sources.py', copy=True)
    .add_local_file(ROOT / 'fpm_compilers.py', '/opt/fpm/fpm_compilers.py', copy=True)
    .add_local_file(ROOT / 'xfpm_worker.py', '/opt/fpm/xfpm_worker.py', copy=True))

runtime_image = with_fpm(modal.Image.from_registry(GNU_IMAGE, add_python='3.12')
                         .run_commands('test "$(gfortran -dumpfullversion)" = 16.2.0'), 'gfortran')


def runtime_images(compilers):
    """Build optional toolchains independently; all installer sources are in this repo."""
    images = {'gfortran': runtime_image}
    for compiler in compilers:
        if compiler == 'gfortran':
            continue
        if compiler == 'gfortran17':
            base = (modal.Image.from_registry(GNU_IMAGE, add_python='3.12')
                .run_commands('test "$(gfortran -dumpfullversion)" = 16.2.0')
                .apt_install('curl', 'ca-certificates', 'build-essential', 'libgmp-dev', 'libmpfr-dev', 'libmpc-dev', 'libisl-dev', 'flex', 'bison', 'texinfo', 'xz-utils')
                .add_local_file(ROOT / 'fpm_toolchains/xinstall_gnu17.sh', '/opt/p2f/xinstall_gnu17.sh', copy=True)
                .run_commands('bash /opt/p2f/xinstall_gnu17.sh')
                .run_commands('mkdir -p /opt/fpm/bin && ln -s /opt/gcc17/bin/gfortran /opt/fpm/bin/gfortran'))
        else:
            script = 'xinstall_intel.sh' if compiler == 'ifx' else 'xinstall_flang.sh'
            base = (modal.Image.debian_slim(python_version='3.12').apt_install('gfortran')
                .apt_install('curl', 'gnupg', 'build-essential', 'ca-certificates')
                .pip_install('certifi==2026.2.25')
                .add_local_file(ROOT / 'fpm_toolchains' / script, '/opt/p2f/' + script, copy=True)
                .run_commands('bash /opt/p2f/' + script))
            if compiler == 'ifx':
                base = base.run_commands('mkdir -p /opt/fpm/bin && ln -s /usr/local/bin/p2f-ifx /opt/fpm/bin/ifx')
            else:
                base = base.run_commands('mkdir -p /opt/fpm/bin && ln -s /usr/bin/flang-23 /opt/fpm/bin/flang-new')
        images[compiler] = with_fpm(base, compiler)
    return {compiler: images[compiler] for compiler in compilers}

container_settings = {'FPM_IMAGE_NAME': IMAGE_NAME, 'FPM_OWNER_SECRET': OWNER_SECRET_NAME,
                      'FPM_ENABLED_COMPILERS': json.dumps(ENABLED_COMPILERS)}
broker_image = (modal.Image.debian_slim(python_version='3.12').pip_install('tomli-w==1.2.0')
    .env(container_settings)
    .add_local_file(ROOT / 'fpm_compilers.py', '/root/fpm_compilers.py', copy=True)
    .add_local_file(ROOT / 'fpm_sources.py', '/root/fpm_sources.py', copy=True))
api_image = (modal.Image.debian_slim(python_version='3.12').pip_install('fastapi==0.142.2')
    .env({**container_settings,
          'FPM_ORIGINS': os.environ.get('FPM_ORIGINS',
          'https://beliavsky.github.io,http://127.0.0.1:8766,http://localhost:8766')})
    .add_local_file(ROOT / 'fpm_sources.py', '/root/fpm_sources.py', copy=True)
    .add_local_file(ROOT / 'fpm_compilers.py', '/root/fpm_compilers.py', copy=True)
    .add_local_file(ROOT / 'fpm_api.py', '/root/fpm_api.py', copy=True))


def bundle_sources(directory):
    buffer = BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
        archive.add(directory, arcname='bundle')
    data = buffer.getvalue()
    if len(data) > 16 * 1024 * 1024:
        raise ValueError('Prepared dependency bundle exceeds 16 MiB compressed.')
    return base64.b64encode(data).decode('ascii')


def execute_job(identifier, payload, *, sandbox_image=None, sandbox_app=None, cancelled=None):
    from fpm_sources import Preparer
    from fpm_sources import validate_request
    sandbox = None
    cancelled = cancelled or (lambda: state.get('cancel:' + identifier, False))
    started = time.monotonic()
    try:
        payload = validate_request(payload)
        if payload['compiler'] not in ENABLED_COMPILERS and sandbox_image is None:
            raise ValueError('Requested FPM compiler is not enabled.')
        with tempfile.TemporaryDirectory() as temporary:
            root, records = Preparer(temporary).prepare(payload)
            message = {'request': payload, 'root': root, 'bundle': bundle_sources(temporary)}
        prepare_seconds = time.monotonic() - started
        if cancelled():
            return {'ok': False, 'error': 'Cancelled.', 'stages': []}
        sandbox = modal.Sandbox.create('python', '/opt/fpm/xfpm_worker.py', app=sandbox_app or app,
            image=sandbox_image or modal.Image.from_name(image_name(payload['compiler'])), runtime='gvisor', workdir='/work', timeout=250,
            cpu=(0.5, 1.0), memory=(512, 1024), block_network=True, secrets=[], volumes={},
            include_oidc_identity_token=False, env={'OMP_NUM_THREADS': '1', 'HOME': '/work'})
        sandbox.stdin.write((json.dumps(message) + '\n').encode())
        sandbox.stdin.write_eof()
        sandbox.stdin.drain()
        while sandbox.poll() is None:
            if cancelled():
                return {'ok': False, 'error': 'Cancelled.', 'stages': []}
            time.sleep(1)
        output = sandbox.stdout.read()
        if len(output) > 2500000:
            raise ValueError('FPM result exceeded its size limit.')
        result = json.loads(output)
        if not isinstance(result, dict) or not isinstance(result.get('ok'), bool):
            raise ValueError('Invalid FPM sandbox result.')
        result.update(packages=records, prepare_seconds=round(prepare_seconds, 3),
                      total_seconds=round(time.monotonic() - started, 3))
        return result
    except Exception as error:
        return {'ok': False, 'error': f'{type(error).__name__}: {error}', 'stages': []}
    finally:
        if sandbox is not None:
            sandbox.terminate()


@app.function(image=broker_image, max_containers=2, timeout=360, cpu=(0.125, 0.5), memory=(256, 1024))
def run_job(identifier, payload):
    return execute_job(identifier, payload)


class Store:
    async def get(self, key, default):
        return await state.get.aio(key, default)

    async def put(self, key, value):
        await state.put.aio(key, value)

    async def pop(self, key):
        await state.pop.aio(key, None)


class Runner:
    async def start(self, identifier, payload):
        call = await run_job.spawn.aio(identifier, payload)
        return call.object_id

    async def poll(self, identifier):
        try:
            return await modal.FunctionCall.from_id(identifier).get.aio(timeout=0)
        except TimeoutError:
            return None
        except Exception:
            return {'ok': False, 'error': 'FPM preparation or execution stopped at a service limit.', 'stages': []}


@app.function(image=api_image, max_containers=1, cpu=(0.125, 0.5), memory=(256, 512), timeout=60,
    secrets=[modal.Secret.from_name(OWNER_SECRET_NAME, required_keys=['P2F_OWNER_KEY'])]
    if OWNER_SECRET_NAME else [])
@modal.concurrent(max_inputs=16)
@modal.asgi_app()
def api():
    from fpm_api import Service, create_api
    return create_api(Service(Store(), Runner(), owner_key=os.environ.get('P2F_OWNER_KEY', ''), compilers=ENABLED_COMPILERS),
                      os.environ['FPM_ORIGINS'].split(','))
