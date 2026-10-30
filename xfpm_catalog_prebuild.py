"""Isolated, pinned large-source prebuild. Never installed in public workers."""
import json
import os
from pathlib import Path
import sys
import time

import xfpm_prebuild as legacy
from fpm_catalog_limits import extract_operator_bundle, source_limit


def build(message):
    source_limit(message)  # Fail before changing this process's extraction hook.
    original = legacy.extract_archive
    def extract(data, destination, *, require_manifest=False):
        if require_manifest:
            raise ValueError('Operator prebuild expects a prepared source bundle.')
        return extract_operator_bundle(data, destination, package=message)
    legacy.extract_archive = extract
    try:
        return legacy.build(message)
    finally:
        legacy.extract_archive = original


if __name__ == '__main__':
    message = json.loads(sys.stdin.buffer.readline(24000000))
    os.setgroups([])
    os.setgid(65534)
    os.setuid(65534)
    try:
        print(json.dumps({'ok': True, **build(message)}), flush=True)
    except Exception as error:
        print(json.dumps({'ok': False, 'error': str(error)}), flush=True)
    time.sleep(3600)
