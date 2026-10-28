"""Shared-library variant of the existing restricted execution worker."""
import runpy
from fpm_shared import enable_shared_consumer

enable_shared_consumer()
runpy.run_path('/opt/fpm/xfpm_legacy_worker.py', run_name='__main__')
