"""Prebuild only package-owned targets against immutable shared dependencies."""
import json
import os
from pathlib import Path
import sys
import time
from fpm_shared import enable_shared_consumer, PLAN

enable_shared_consumer()
from xfpm_prebuild import build

if __name__ == '__main__':
    message = json.loads(sys.stdin.buffer.readline(24000000))
    os.setgroups([])
    os.setgid(65534)
    os.setuid(65534)
    try:
        result = build(message)
        path = Path('/work/precompiled.json')
        metadata = json.loads(path.read_text())
        metadata['shared_dependencies'] = [{k: p[k] for k in
            ('repository', 'key', 'artifact_bytes', 'manifest_sha256')} for p in json.loads(PLAN.read_text())]
        path.write_text(json.dumps(metadata))
        result['shared_dependencies'] = metadata['shared_dependencies']
        print(json.dumps({'ok': True, **result}), flush=True)
    except Exception as error:
        print(json.dumps({'ok': False, 'error': str(error)}), flush=True)
    time.sleep(3600)
