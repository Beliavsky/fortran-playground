"""Small deterministic FPM deployment checks, with no source downloads."""
import base64
from io import BytesIO
import json
import tarfile


def probe_message(compiler, action):
    files = {
        'fpm.toml': 'name="fpm-smoke"\n',
        'src/math.f90': 'module smoke_math\nuse iso_c_binding\ninterface\ninteger(c_int) function c_answer() bind(C)\nimport c_int\nend function\nend interface\nend module\n',
        'src/answer.c': 'int c_answer(void) { return 42; }\n',
        'app/main.f90': 'program main\nuse smoke_math\ninteger n\nread(*,*) n\nif(n+c_answer()/=43) error stop\nprint *, "FPM RUN PASS"\nend program\n',
        'test/check.f90': 'program check\nuse smoke_math\nif(c_answer()/=42) error stop\nprint *, "FPM TEST PASS"\nend program\n',
    }
    buffer = BytesIO()
    with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
        for name, text in files.items():
            member = tarfile.TarInfo('bundle/package/' + name)
            data = text.encode()
            member.size = len(data)
            member.mode = 0o644
            archive.addfile(member, BytesIO(data))
    return {'root': 'package', 'bundle': base64.b64encode(buffer.getvalue()).decode(),
            'request': {'url': 'https://github.com/example/probe', 'workflow': 'package',
                        'compiler': compiler, 'action': action, 'stdin': '1\n'}}


def verify_image(app, image, compiler):
    import modal
    for action in ('build', 'run', 'test'):
        sandbox = modal.Sandbox.create('python', '/opt/fpm/xfpm_worker.py', app=app, image=image,
            runtime='gvisor', workdir='/work', timeout=250, cpu=(0.5, 1.0), memory=(512, 1024),
            block_network=True, secrets=[], volumes={}, include_oidc_identity_token=False,
            env={'OMP_NUM_THREADS': '1', 'HOME': '/work'})
        try:
            sandbox.stdin.write((json.dumps(probe_message(compiler, action)) + '\n').encode())
            sandbox.stdin.write_eof()
            sandbox.stdin.drain()
            sandbox.wait()
            result = json.loads(sandbox.stdout.read())
            marker = 'FPM RUN PASS' if action == 'run' else 'FPM TEST PASS'
            if not result.get('ok') or result.get('compiler_id') != compiler or (action != 'build' and marker not in json.dumps(result)):
                raise ValueError(f'{compiler} {action} verification failed: {json.dumps(result)[-6000:]}')
            print(f'{compiler}: sandbox {action} verified', flush=True)
        finally:
            sandbox.terminate()
