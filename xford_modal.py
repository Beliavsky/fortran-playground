"""Independent on-demand FORD pilot: modal deploy xford_modal.py.

Does not import or rebuild compiler/package images.
"""
import asyncio
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import secrets
import time

import modal

ROOT = Path(__file__).resolve().parent
APP_NAME = 'fortran-playground-docs'
app = modal.App(APP_NAME)
cache = modal.Volume.from_name(APP_NAME + '-cache', create_if_missing=True)
state = modal.Dict.from_name(APP_NAME + '-state', create_if_missing=True)
image = (modal.Image.debian_slim(python_version='3.12')
         .pip_install('ford==7.0.13', 'fastapi==0.115.12')
         .add_local_file(ROOT / 'ford_docs.py', '/root/ford_docs.py', copy=True)
         .add_local_file(ROOT / 'fpm_sources.py', '/root/fpm_sources.py', copy=True)
         .add_local_file(ROOT / 'fpm_compilers.py', '/root/fpm_compilers.py', copy=True)
         .add_local_dir(ROOT / 'vendor/ford', '/root/vendor/ford', copy=True))


@app.function(image=image, volumes={'/cache': cache}, timeout=180, memory=1024, max_containers=2)
def generate(payload):
    from ford_docs import github_documentation
    try:
        cache.reload()
        result = github_documentation(payload, '/cache')
        cache.commit()
        return {'ok': True, **result}
    except Exception as error:
        return {'ok': False, 'error': str(error)[:16000]}


@app.function(image=image, volumes={'/cache': cache}, max_containers=1,
              env={'DOCS_ORIGINS': os.environ.get('DOCS_ORIGINS', 'https://beliavsky.github.io')})
@modal.concurrent(max_inputs=20)
@modal.asgi_app()
def api():
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import Response, JSONResponse
    from ford_docs import artifact, validate_request
    web = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    origins = os.environ['DOCS_ORIGINS'].split(',')
    web.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET', 'POST'],
                       allow_headers=['Content-Type'])
    lock = asyncio.Lock()

    @web.get('/api/health')
    def health():
        return {'ok': True, 'ford': '7.0.13', 'pilot': True}

    @web.post('/api/docs')
    async def submit(request: Request):
        if request.headers.get('origin') not in origins:
            return JSONResponse({'error': 'Use the documentation page on an allowed site.'}, status_code=403)
        if len(body := await request.body()) > 4096:
            return JSONResponse({'error': 'Request too large.'}, status_code=400)
        try: payload = validate_request(json.loads(body))
        except (ValueError, TypeError) as error:
            return JSONResponse({'error': str(error)}, status_code=400)
        async with lock:
            now = time.time()
            board = await state.get.aio('board', None) or {'salt': secrets.token_hex(32), 'day': '', 'daily': 0, 'rates': {}, 'jobs': {}}
            day = time.strftime('%Y-%m-%d', time.gmtime(now))
            if board['day'] != day: board.update(day=day, daily=0)
            board['jobs'] = {k: v for k, v in board['jobs'].items() if now - v['created'] < 1800}
            board['rates'] = {k: [t for t in v if now-t < 600] for k, v in board['rates'].items() if v and now-v[-1] < 600}
            address = hashlib.sha256((board['salt'] + request.client.host).encode()).hexdigest()
            if board['daily'] >= 100 or len(board['rates'].get(address, [])) >= 30:
                return JSONResponse({'error': 'Documentation limit: 30 requests per address per ten minutes; 100 per day.'}, status_code=429)
            if sum(not j.get('finished') and now-j['created'] < 210 for j in board['jobs'].values()) >= 2:
                return JSONResponse({'error': 'Both documentation slots are busy. Try again shortly.'}, status_code=429)
            identifier = secrets.token_urlsafe(32)
            call = await generate.spawn.aio(payload)
            board['jobs'][identifier] = {'call': call.object_id, 'created': now}
            board['rates'].setdefault(address, []).append(now)
            board['daily'] += 1
            await state.put.aio('board', board)
            return {'id': identifier}

    @web.get('/api/docs/{identifier}')
    async def poll(identifier: str):
        async with lock:
            board = await state.get.aio('board', None) or {'jobs': {}}
            job = board['jobs'].get(identifier)
            if not job or time.time()-job['created'] >= 1800:
                return JSONResponse({'error': 'Documentation job expired.'}, status_code=404)
            if 'result' not in job:
                try:
                    job['result'] = await modal.FunctionCall.from_id(job['call']).get.aio(timeout=0)
                except TimeoutError:
                    if time.time()-job['created'] < 210: return {'state': 'running'}
                    job['result'] = {'ok': False, 'error': 'Documentation job exceeded its service limit.'}
                except Exception:
                    job['result'] = {'ok': False, 'error': 'Documentation worker failed. Try the local generator for diagnostics.'}
                job['finished'] = True
                await state.put.aio('board', board)
            return {'state': 'done', 'result': job['result']}

    @web.get('/view/{key}/{name:path}')
    async def view(key: str, name: str):
        try:
            cache.reload()
            path = artifact('/cache', key, name)
            content = path.read_bytes()
        except (ValueError, OSError):
            return JSONResponse({'error': 'Documentation not found.'}, status_code=404)
        return Response(content, media_type=mimetypes.guess_type(path.name)[0] or 'application/octet-stream',
            headers={**({'Content-Disposition': 'attachment; filename=documentation.zip'} if path.suffix == '.zip' else {}),'Content-Security-Policy': "sandbox allow-scripts allow-forms; default-src 'self' 'unsafe-inline' data:; connect-src 'none'; form-action 'self'",
                     'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer', 'Access-Control-Allow-Origin': '*'})
    return web
