"""Audit up to 20 discovery packages with temporary hosted GNU 16 build jobs."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

from fpm_runner import run_hosted_job
from xplayground_run import PlaygroundClient

ROOT = Path(__file__).resolve().parent
SAMPLE = [
    'awvwgk/blas-interface', 'gha3mi/forblas', 'HugoMVale/odrpack95', 'sebastiandyrda/lib_statistics',
    'jacobwilliams/odepack', 'princemahajan/FLINT', 'arjenmarkus/pointsets', 'wcota/rndgen-fortran',
    'everythingfunctional/strff', 'Carltoffel/Fortran-String-to-Real', '0382/argparse-f',
    'davidpfister/subprocess.f', 'lauvergn/AD_dnSVM', 'zoziha/Auto-Diff', 'jacobwilliams/kronrod',
    'Euler-37/integrate_fortran', 'geospace-code/h5fortran', 'freevryheid/flibcsv',
    'furstj/interpolation', 'vmagnin/formidi',
]


def classify(row):
    if row.get('ok'):
        return 'build_pass'
    text = (row.get('error', '') + ' ' + ' '.join(
        s.get('stdout', '') + ' ' + s.get('stderr', '') + ' ' + s.get('error', '') for s in row.get('stages', []))).lower()
    if 'registry dependencies and metapackages' in text:
        return 'unsupported_dependency'
    if 'preprocessor directive' in text:
        return 'preprocessing_required'
    if 'werror=implicit-interface' in text:
        return 'implicit_interface_error'
    if 'could not be found, check if the file exists' in text:
        return 'missing_source'
    if 'fatal error:' in text and 'include' in text and '\\' in text:
        return 'platform_specific_source'
    if any(s in text for s in ('limit', 'timed out', 'timeout', 'too many')):
        return 'service_limit'
    if not row.get('stages'):
        return 'preparation_failure'
    if any(s in text for s in ('cannot find -l', 'undefined reference', 'cannot open module file')):
        return 'missing_library_or_module'
    return 'build_failure'


def audit(output, limit=20):
    catalog = json.loads((ROOT / 'site/fpm/all-packages.json').read_text(encoding='utf-8'))
    selected = {p['repository'].lower(): p for p in catalog}
    service = json.loads((ROOT / 'site/fpm/service.json').read_text())['url']
    client = PlaygroundClient(service)
    health = client.request('health')
    if not health.get('ok'):
        raise ValueError('FPM service is unavailable')
    report = {'schema': 1, 'tested_at': datetime.now(timezone.utc).isoformat(),
              'environment': 'Hosted Linux sandbox, GNU Fortran 16.2.0, FPM 0.12.0',
              'action': 'build', 'selection': 'Twenty non-precompiled packages across numerical, string, I/O, and utility categories; not a random estimate of the whole catalog.',
              'service': service, 'packages': []}
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    for repo in SAMPLE[:limit]:
        entry = selected[repo.lower()]
        if entry.get('source'):
            raise ValueError('Audit sample must exclude precompiled packages: ' + repo)
        request = Request(f'https://api.github.com/repos/{repo}/commits/HEAD',
                          headers={'User-Agent': 'Fortran-playground-discovery-audit'})
        with urlopen(request, timeout=30) as response:
            revision = json.load(response)['sha']
        print(f'Building {repo} @ {revision[:7]}', flush=True)
        try:
            row = run_hosted_job(client, {'url': f'https://github.com/{repo}', 'revision': revision,
                'workflow': 'package', 'action': 'build', 'compiler': 'gfortran'}, 420)
        except Exception as error:
            # Do not retry submissions or continue through admission/quota errors.
            print(f'Audit stopped: {error}', flush=True)
            break
        result = {'repository': repo, 'revision': revision, 'category': entry['category'],
                  'outcome': classify(row), 'build_ok': row.get('build_ok', row['ok']),
                  'application_targets': row.get('targets', []), 'error': row.get('error', ''),
                  'compiler': row.get('compiler_version', ''), 'times': row['times'],
                  'stages': [{k: v for k, v in stage.items() if k not in ('stdout', 'stderr')}
                             | {'stdout_tail': stage.get('stdout', '')[-2000:], 'stderr_tail': stage.get('stderr', '')[-4000:]}
                             for stage in row.get('stages', [])]}
        report['packages'].append(result)
        output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(f'{repo}: {result["outcome"]}; {result["error"][:200]}', flush=True)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/fpm-discovery-audit.json')
    parser.add_argument('--limit', type=int, choices=range(1, 21), default=20)
    args = parser.parse_args()
    audit(args.output, args.limit)
