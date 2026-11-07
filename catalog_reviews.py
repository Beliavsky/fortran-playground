"""Revision-matched independent reviews; offline snapshots, never execution claims."""
import copy
from datetime import date
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit

PUBLISHER = 'fortran-gams-catalog-independent-reviews'
FEED_URL = 'https://beliavsky.github.io/fortran-gams-catalog/reviewed-metadata.json'
ROOT = Path(__file__).resolve().parent
SNAPSHOT = 'fpm_catalog/catalog-reviews.json'
OVERRIDES = 'fpm_catalog/catalog-review-overrides.json'


def digest(data):
    payload = {k: v for k, v in data.items() if k != 'snapshot_id'}
    return 'sha256:' + hashlib.sha256(json.dumps(
        payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 1024 * 1024:
        raise ValueError('Review text must be a nonempty string.')


def source_path(value):
    text(value)
    if '\\' in value or ':' in value or PurePosixPath(value).is_absolute() or '..' in PurePosixPath(value).parts:
        raise ValueError('Review source paths must be relative.')


def evidence(record, repository, revision):
    records = record.get('evidence')
    if not isinstance(records, list) or not records:
        raise ValueError('Review evidence is required.')
    for item in records:
        source_path(item['path'])
        url = urlsplit(item['url'])
        prefix = repository['url'] + '/blob/' + revision + '/'
        if (url.scheme != 'https' or url.netloc != 'github.com'
                or not item['url'].startswith(prefix) or any(ord(c) < 32 for c in item['url'])
                or not re.fullmatch(r'[0-9a-f]{64}', item.get('sha256', ''))):
            raise ValueError('Evidence needs a pinned repository URL and SHA-256.')
    return {item['path'] for item in records}


def review_header(record):
    if not re.fullmatch(r'[0-9a-f]{40}', record.get('revision', '')):
        raise ValueError('Reviews need full commit revisions.')
    date.fromisoformat(record['reviewed_on'])
    text(record['notes'])


def validate_project(project):
    identity = project['id']
    if not re.fullmatch(r'github:[a-z0-9_.-]+/[a-z0-9_.-]+', identity):
        raise ValueError('Invalid reviewed repository identity.')
    repository = project['repository']
    if ('github:' + repository['owner'].lower() + '/' + repository['name'].lower() != identity
            or repository['url'] != 'https://github.com/' + repository['owner'] + '/' + repository['name']):
        raise ValueError('Repository and review identity disagree.')
    license_data = project.get('license')
    if license_data is not None:
        review_header(license_data)
        text(license_data['label'])
        if license_data.get('spdx_expression') is not None:
            text(license_data['spdx_expression'])
        evidence(license_data, repository, license_data['revision'])
    if not isinstance(project['classifications'], list):
        raise ValueError('Expected a list of reviewed classifications.')
    for claim in project['classifications']:
        review_header(claim)
        if claim['level'] != 'source-reviewed' or not re.fullmatch(r'[A-Z][A-Za-z0-9]*', claim['code']):
            raise ValueError('Only explicit source-reviewed classifications may be imported.')
        paths = evidence(claim, repository, claim['revision'])
        if not isinstance(claim['procedures'], list):
            raise ValueError('Expected a list of reviewed procedures.')
        for procedure in claim['procedures']:
            if (procedure.get('role') != 'public-entry-point' or 'local_driver' in procedure
                    or 'driver_id' in procedure):
                raise ValueError('Only public interfaces, without execution claims, may be imported.')
            text(procedure['procedure'])
            for field in ('module', 'derived_type', 'summary', 'signature'):
                if field in procedure:
                    text(procedure[field])
            for reference in [procedure, *procedure.get('declarations', [])]:
                if (reference['path'] not in paths
                        or type(reference['line_start']) is not int or type(reference['line_end']) is not int
                        or not 1 <= reference['line_start'] <= reference['line_end']):
                    raise ValueError('Procedure ranges must refer to pinned evidence.')
            if procedure.get('signature') and not procedure.get('declarations'):
                raise ValueError('Signatures need argument declarations.')
            if 'usage' in procedure:
                text(procedure['usage'])
                if procedure.get('usage_kind') != 'calling-sketch':
                    raise ValueError('Imported usage is an unchecked calling sketch.')
    return project


def validate_feed(data):
    if (not isinstance(data, dict) or data.get('schema_version') != 1 or data.get('publisher') != PUBLISHER
            or data.get('source_repository') != 'https://github.com/Beliavsky/fortran-gams-catalog'
            or data.get('snapshot_id') != digest(data) or not isinstance(data.get('projects'), list)):
        raise ValueError('Invalid independent-review feed or snapshot hash.')
    seen = set()
    for project in data['projects']:
        validate_project(project)
        if project['id'] in seen:
            raise ValueError('Duplicate reviewed repository.')
        seen.add(project['id'])
    return data


def select_reviews(feed, packages):
    """Match exact repository + commit, retaining explicit mismatch reports."""
    validate_feed(feed)
    by_id = {p['id']: p for p in feed['projects']}
    selected = {}
    report = {'matched': [], 'revision_mismatches': [], 'no_independent_review': []}
    for package in packages:
        identity = 'github:' + package['repository'].lower()
        original = by_id.get(identity)
        if original is None:
            report['no_independent_review'].append(package['id'])
            continue
        project = copy.deepcopy(original)
        pin = package['revision']
        revisions = {c['revision'] for c in original['classifications']} | (
            {original['license']['revision']} if original.get('license') else set())
        if revisions - {pin}:
            report['revision_mismatches'].append({'package_id': package['id'], 'repository': identity,
                'package_revision': pin, 'reviewed_revisions': sorted(revisions - {pin})})
        project['classifications'] = [c for c in project['classifications'] if c['revision'] == pin]
        if project.get('license') and project['license']['revision'] != pin:
            project['license'] = None
        if not project['classifications'] and project['license'] is None:
            continue
        selected[package['id']] = project
        report['matched'].append(package['id'])
    return {'schema_version': 1, 'publisher': PUBLISHER, 'source_url': FEED_URL,
            'source_snapshot_id': feed['snapshot_id'], 'packages': selected, 'report': report}


def load_reviews(root=ROOT):
    """Load cached records and optional whole-package local replacements offline."""
    root = Path(root)
    path = root / SNAPSHOT
    result = {}
    if path.exists():
        data = json.loads(path.read_text(encoding='utf-8'))
        if (data.get('schema_version') != 1 or data.get('publisher') != PUBLISHER
                or not re.fullmatch(r'sha256:[0-9a-f]{64}', data.get('source_snapshot_id', ''))):
            raise ValueError('Invalid saved independent reviews.')
        result = data['packages']
        if not isinstance(result, dict):
            raise ValueError('Saved reviews need a package mapping.')
    override = root / OVERRIDES
    if override.exists():
        data = json.loads(override.read_text(encoding='utf-8'))
        if data.get('schema_version') != 1 or not isinstance(data.get('packages'), dict):
            raise ValueError('Invalid local review overrides.')
        result = {**result, **data['packages']}
    for value in result.values():
        if value is not None:
            validate_project(value)
    return {key: value for key, value in result.items() if value is not None}


def matching_review(project, reviews):
    """Recheck pins at build time, so changing a package never reuses stale APIs."""
    package = project.get('playground', {}).get('package_id')
    review = reviews.get(package)
    if not review or review['id'] != project['id']:
        return None
    result = copy.deepcopy(review)
    revision = project['playground']['package_revision']
    result['classifications'] = [c for c in result['classifications'] if c['revision'] == revision]
    if result.get('license') and result['license']['revision'] != revision:
        result['license'] = None
    return result if result['classifications'] or result.get('license') else None
