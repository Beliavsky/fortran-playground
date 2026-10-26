"""FPM-only API and durable admission limits; no package commands run here."""
import asyncio
import hashlib
import hmac
import json
import secrets
import time

from fpm_sources import validate_request


class ServiceError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


class Service:
    def __init__(self, store, runner, *, clock=time.time, owner_key=''):
        self.store, self.runner, self.clock, self.owner_key = store, runner, clock, owner_key
        self.lock = asyncio.Lock()

    async def board(self):
        now = self.clock()
        board = await self.store.get('board', None) or {
            'secret': secrets.token_hex(32), 'day': '', 'daily': 0, 'rates': {}, 'jobs': {}}
        day = time.strftime('%Y-%m-%d', time.gmtime(now))
        if board['day'] != day:
            board['day'], board['daily'] = day, 0
        board['rates'] = {key: [t for t in values if t > now - 600] for key, values in board['rates'].items()
                          if values and values[-1] > now - 600}
        for identifier, job in list(board['jobs'].items()):
            if job['expires'] <= now:
                await self.store.pop('result:' + identifier)
                await self.store.pop('cancel:' + identifier)
                del board['jobs'][identifier]
            elif job['state'] == 'running':
                result = await self.runner.poll(job['call'])
                if result is None and job['deadline'] <= now:
                    result = {'ok': False, 'error': 'The FPM job reached its service time limit.', 'stages': []}
                if result is not None:
                    await self.store.put('result:' + identifier, result)
                    job['state'] = 'done'
        return board

    async def submit(self, address, payload, owner_key=''):
        try:
            payload = validate_request(payload)
        except (ValueError, UnicodeError) as error:
            raise ServiceError(400, str(error)) from error
        async with self.lock:
            board = await self.board()
            exempt = bool(self.owner_key and hmac.compare_digest(owner_key.encode(), self.owner_key.encode()))
            address = hmac.new(bytes.fromhex(board['secret']), address.encode(), hashlib.sha256).hexdigest()
            recent = board['rates'].get(address, [])
            if not exempt and (len(recent) >= 30 or board['daily'] >= 100):
                raise ServiceError(429, 'FPM usage limit reached: 30 jobs per address per ten minutes; 100 public jobs per day.')
            if sum(job['state'] == 'running' for job in board['jobs'].values()) >= 2:
                raise ServiceError(429, 'Both FPM job slots are busy. Please try again shortly.')
            if len(board['jobs']) >= 256:
                raise ServiceError(429, 'FPM job storage is full. Please try again later.')
            identifier = secrets.token_urlsafe(32)
            call = await self.runner.start(identifier, payload)
            now = self.clock()
            board['jobs'][identifier] = {'call': call, 'state': 'running', 'deadline': now + 400, 'expires': now + 1800}
            if not exempt:
                board['rates'][address] = [*recent, now]
                board['daily'] += 1
            await self.store.put('board', board)
            return {'id': identifier}

    async def job(self, identifier, *, cancel=False):
        if not isinstance(identifier, str) or len(identifier) != 43:
            raise ServiceError(404, 'FPM job not found or expired.')
        async with self.lock:
            board = await self.board()
            job = board['jobs'].get(identifier)
            if job is None:
                raise ServiceError(404, 'FPM job not found or expired.')
            if cancel and job['state'] == 'running':
                await self.store.put('cancel:' + identifier, True)
            await self.store.put('board', board)
            if job['state'] == 'done':
                return {'state': 'done', 'result': await self.store.get('result:' + identifier, None)}
            return {'state': 'cancelling' if cancel else 'running'}


def create_api(service, origins):
    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse

    api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @api.exception_handler(ServiceError)
    async def error(_request, exception):
        return JSONResponse({'error': exception.message}, status_code=exception.status)

    @api.middleware('http')
    async def headers(request, call_next):
        if request.url.path != '/api/health' and request.headers.get('origin') not in origins:
            return JSONResponse({'error': 'Open the FPM playground to use this service.'}, status_code=403)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    api.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=['GET', 'POST'],
                       allow_headers=['Content-Type', 'X-P2F-Owner-Key'])

    @api.get('/api/health')
    async def health():
        return {'ok': True, 'compiler': 'GNU Fortran 16.2.0', 'fpm': '0.12.0', 'clean_builds': True}

    @api.post('/api/jobs')
    async def submit(request: Request):
        if request.headers.get('content-type') != 'application/json':
            raise ServiceError(415, 'Expected application/json.')
        content = bytearray()
        async for chunk in request.stream():
            content.extend(chunk)
            if len(content) > 1250000:
                raise ServiceError(413, 'FPM request is too large.')
        try:
            payload = json.loads(content)
        except (ValueError, UnicodeError):
            raise ServiceError(400, 'Invalid JSON.') from None
        return await service.submit(request.client.host if request.client else 'unknown', payload,
                                    request.headers.get('x-p2f-owner-key', ''))

    @api.get('/api/jobs/{identifier}')
    async def poll(identifier: str):
        return await service.job(identifier)

    @api.post('/api/jobs/{identifier}/cancel')
    async def cancel(identifier: str):
        return await service.job(identifier, cancel=True)

    return api
