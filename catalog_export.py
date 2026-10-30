"""Portable, versioned Fortran software metadata; no compilation or network access."""
import copy
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
PUBLISHER = 'fortran-playground'
REPOSITORY = 'https://github.com/Beliavsky/fortran-playground'
BASE_URL = 'https://beliavsky.github.io/fortran-playground'
SCHEMA_NAME = 'catalog-v1.schema.json'
FEED_NAME = 'catalog-v1.json'
SCHEMA_URL = f'{BASE_URL}/catalog/{SCHEMA_NAME}'
ID_PATTERN = re.compile(r'github:[a-z0-9_.-]+/[a-z0-9_.-]+')


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def text_hash(path):
    return hashlib.sha256(Path(path).read_text(encoding='utf-8').encode('utf-8')).hexdigest()


def validate_owners(records):
    """Validate shared profile snapshots without requiring the refresh tool."""
    if not isinstance(records, dict):
        raise ValueError('GitHub owners must be a mapping.')
    for key, record in records.items():
        if (not isinstance(key, str) or not re.fullmatch(r'[a-z0-9_.-]+', key)
                or not isinstance(record, dict) or not isinstance(record.get('login'), str)
                or record['login'].lower() != key
                or record.get('account_type') not in ('User', 'Organization', 'Bot')
                or record.get('profile_url') != 'https://github.com/' + record['login']
                or 'display_name' not in record
                or record.get('source_url') not in ('https://api.github.com/users/' + key, record['profile_url'])):
            raise ValueError(f'{key}: invalid public GitHub owner record.')
        name = record.get('display_name')
        if name is not None and (not isinstance(name, str) or not name.strip() or len(name) > 256
                                 or name != ' '.join(name.split())):
            raise ValueError(f'{key}: invalid public display name.')
        try:
            timestamp = datetime.fromisoformat(record['retrieved_at'])
            if timestamp.tzinfo is None:
                raise ValueError()
        except (KeyError, TypeError, ValueError):
            raise ValueError(f'{key}: owner retrieval time needs a time zone.') from None
    return records


def snapshot_id(data):
    return 'sha256:' + hashlib.sha256(canonical_json({key: value for key, value in data.items()
                                                   if key != 'snapshot_id'})).hexdigest()


def owner_display_name(key, profile, manual):
    """Use the same owner-label policy in the website and combined review table."""
    if key == 'fortran-lang':
        return 'fortran-lang'
    if manual.get('status') == 'confirmed':
        return manual['name']
    return profile.get('display_name') or profile.get('login') or key


def validate_attributions(data):
    """Keep public project credits distinct from reviewed account identities."""
    if not isinstance(data, dict) or data.get('schema') != 1:
        raise ValueError('Invalid manual name attribution schema.')
    for field, pattern in [('owner_names', r'[a-z0-9_.-]+'), ('project_authors', ID_PATTERN)]:
        mapping = data.get(field)
        if not isinstance(mapping, dict):
            raise ValueError(f'{field}: expected a mapping.')
        for key, value in mapping.items():
            if not isinstance(key, str) or not re.fullmatch(pattern, key):
                raise ValueError('Invalid name attribution identity.')
            records = value if field == 'project_authors' else [value]
            if not isinstance(records, list) or not records:
                raise ValueError(f'{key}: at least one author credit is required.')
            for record in records:
                if not isinstance(record, dict) or record.get('status') not in ('confirmed', 'inferred'):
                    raise ValueError(f'{key}: attribution needs a review status.')
                for name in ('name', 'scope', 'rationale'):
                    text = record.get(name)
                    if not isinstance(text, str) or not text.strip() or text != ' '.join(text.split()):
                        raise ValueError(f'{key}: attribution needs {name}.')
                if len(record['name']) > 256:
                    raise ValueError(f'{key}: attribution name is too long.')
                try:
                    date.fromisoformat(record['reviewed_on'])
                except (KeyError, TypeError, ValueError):
                    raise ValueError(f'{key}: attribution needs a review date.') from None
                evidence = record.get('evidence')
                if not isinstance(evidence, list) or not evidence:
                    raise ValueError(f'{key}: public attribution evidence is required.')
                for item in evidence:
                    if not isinstance(item, dict) or not isinstance(item.get('url'), str):
                        raise ValueError(f'{key}: invalid attribution evidence.')
                    url = urlsplit(item['url'])
                    if (url.scheme != 'https' or not url.hostname or url.username or url.password
                            or any(c.isspace() for c in item['url'])
                            or not isinstance(item.get('description'), str) or not item['description'].strip()):
                        raise ValueError(f'{key}: attribution evidence requires an HTTPS link and description.')
    return data


def input_provenance(root, paths):
    records = [{'path': path, 'sha256': text_hash(root / path)} for path in sorted(paths)]
    commit = None
    modified = None
    try:
        commit = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], check=True,
                                capture_output=True, text=True).stdout.strip()
        status = subprocess.run(['git', '-C', str(root), 'status', '--porcelain=v1',
                                 '--untracked-files=all', '--', *paths], check=True,
                                capture_output=True, text=True).stdout
        modified = bool(status.strip())
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return {'repository': REPOSITORY, 'source_commit': commit if modified is False else None,
            'base_commit': commit, 'inputs_modified': modified, 'hash_normalization': 'utf-8-lf',
            'inputs': records}


def build_export(root=ROOT):
    # Import tools need only this module and the standard library; the source
    # catalog and its authoring helpers are needed solely when exporting.
    from xpackage_gams import gams_data, package_classes, class_tree, procedure_records, driver_data, numerical_review
    from xpackage_topics import playground_topics
    from xgithub_owners import load_owners
    from xpackage_attributions import load_attributions

    root = Path(root)
    packages = json.loads((root / 'fpm_catalog.json').read_text(encoding='utf-8'))['packages']
    github = json.loads((root / 'fpm_catalog/topics.json').read_text(encoding='utf-8'))
    curated = playground_topics(root)
    owner_records = load_owners(root)
    attributions = load_attributions(root)
    gams = gams_data(root)
    drivers = driver_data(root, gams)
    review = numerical_review(root, gams)
    inputs = ['fpm_catalog.json', 'fpm_catalog/topics.json', 'fpm_catalog/playground-topics.json',
              'fpm_catalog/gams.json', 'catalog_export.py', 'xpackage_topics.py', 'xpackage_gams.py',
                   f'catalog/{SCHEMA_NAME}']
    if (root / 'fpm_catalog/owners.json').exists():
        inputs.append('fpm_catalog/owners.json')
    if (root / 'fpm_catalog/name-attributions.json').exists():
        inputs.append('fpm_catalog/name-attributions.json')
    inputs.extend(['fpm_catalog/gams-drivers.json', 'docs/gams-g1-validation.json',
                   'fpm_catalog/gams-numerical-review.json'])
    inputs.extend(sorted({p for d in drivers for p in [d['path'], *d['license_files']]}))
    projects = []
    for package in sorted(packages, key=lambda p: p['repository'].lower()):
        owner, name = package['repository'].split('/')
        metadata = github['repositories'].get(package['repository'].lower(), {})
        example = f'fpm_catalog/demos/{package["id"]}.f90'
        inputs.append(example)
        projects.append({
            'id': 'github:' + package['repository'].lower(),
            'name': package['id'],
            'repository': {'host': 'github', 'owner': owner, 'name': name,
                           'url': f'https://github.com/{owner}/{name}'},
            'description': package['description'], 'languages': ['Fortran'], 'build_systems': ['fpm'],
            'categories': [package['category']],
            'license': {'label': package.get('license') or None, 'spdx_expression': None},
            'github': {'topics': metadata.get('topics', []), 'topics_updated_at': github['retrieved_at'],
                       'stars': metadata.get('stars'), 'stars_updated_at': metadata.get('stars_updated_at')},
            'curation': {'topics': curated[package['id']],
                         'gams_codes': [c['code'] for c in package_classes(gams, package['id'])],
                         'gams_review_level': 'discovery',
                         'gams_notes': gams.get('review_notes', {}).get(package['id'], ''),
                         'reviewed_revision': package['revision']},
            'playground': {'package_id': package['id'], 'catalog_status': 'selected',
                           'url': f'{BASE_URL}/fpm/?package={package["id"]}',
                           'package_revision': package['revision'], 'live_service_checked': False,
                           'example': {'path': example, 'sha256': text_hash(root / example)}},
        })
        procedures = procedure_records(gams, package['id'])
        if procedures:
            projects[-1]['curation']['procedures'] = procedures
        if package['id'] in review['packages']:
            projects[-1]['curation']['numerical_review'] = review['packages'][package['id']]
    provenance = input_provenance(root, inputs)
    export = {'$schema': SCHEMA_URL, 'schema_version': 1, 'publisher': PUBLISHER,
              'provenance': provenance,
              'taxonomies': {'gams': {'source': gams['source'],
                  'retrieved_on': gams['taxonomy_retrieved_on'],
                  'classes': class_tree(gams),
                  'detailed_taxonomy_source': gams.get('detailed_taxonomy_source')}},
              'demonstrations': [{**d, 'source_sha256': text_hash(root / d['path']),
                  'url': f'{BASE_URL}/fpm/?package={d["package_id"]}&example={d["name"]}',
                  'validation_path': 'docs/gams-g1-validation.json'} for d in drivers],
              'projects': projects}
    selected_owners = {p['repository']['owner'].lower() for p in projects}
    export['owners'] = {key: value for key, value in owner_records.items() if key in selected_owners}
    export['attributions'] = {'schema': 1,
        'owner_names': {key: value for key, value in attributions['owner_names'].items() if key in selected_owners},
        'project_authors': {key: value for key, value in attributions['project_authors'].items()
                            if key in {project['id'] for project in projects}}}
    export['snapshot_id'] = snapshot_id(export)
    validate_export(export)
    return export


def validate_export(data):
    """Validate the v1 contract and cross-record identity/class references offline."""
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError('Unsupported catalog schema_version; expected 1.')
    if data.get('publisher') != PUBLISHER:
        raise ValueError('Unexpected catalog publisher.')
    if 'owners' in data:
        validate_owners(data['owners'])
    if 'attributions' in data:
        validate_attributions(data['attributions'])
    if data.get('$schema') != SCHEMA_URL:
        raise ValueError('Unexpected catalog schema reference.')
    if not _matches(r'sha256:[0-9a-f]{64}', data.get('snapshot_id')):
        raise ValueError('Invalid snapshot_id.')
    provenance = data.get('provenance')
    if not isinstance(provenance, dict) or provenance.get('repository') != REPOSITORY:
        raise ValueError('Invalid catalog provenance.')
    _require(provenance, ('repository', 'source_commit', 'base_commit', 'inputs_modified', 'hash_normalization', 'inputs'), 'provenance')
    for field in ('source_commit', 'base_commit'):
        value = provenance.get(field)
        if not _commit(value):
            raise ValueError(f'Invalid provenance {field}.')
    if provenance.get('inputs_modified') is not None and type(provenance['inputs_modified']) is not bool:
        raise ValueError('inputs_modified must be boolean or null.')
    if provenance.get('inputs_modified') is not False and provenance.get('source_commit') is not None:
        raise ValueError('Modified or unknown inputs cannot claim a source commit.')
    if provenance.get('source_commit') is not None and provenance['source_commit'] != provenance.get('base_commit'):
        raise ValueError('Source and base commits disagree.')
    if provenance.get('hash_normalization') != 'utf-8-lf':
        raise ValueError('Unsupported source hash normalization.')
    inputs = provenance.get('inputs')
    if not isinstance(inputs, list) or not inputs or any(not isinstance(item, dict)
            or not isinstance(item.get('path'), str) or not item['path']
            or not _matches(r'[0-9a-f]{64}', item.get('sha256')) for item in inputs):
        raise ValueError('Invalid source input hashes.')
    if len({item['path'] for item in inputs}) != len(inputs):
        raise ValueError('Duplicate source input paths.')
    if data['snapshot_id'] != snapshot_id(data):
        raise ValueError('snapshot_id does not match the export contents.')
    _object(data.get('taxonomies'), 'taxonomies')
    gams = data['taxonomies'].get('gams')
    _object(gams, 'taxonomies.gams')
    if gams.get('source') != 'https://gams.nist.gov/cgi-bin/serve.cgi':
        raise ValueError('Unknown GAMS taxonomy source.')
    try:
        date.fromisoformat(gams['retrieved_on'])
    except (KeyError, TypeError, ValueError):
        raise ValueError('Invalid GAMS retrieval date.') from None
    taxonomy = gams.get('classes')
    if not isinstance(taxonomy, dict) or not set('ABCDEFGHIJKLMNOPQRSZ').issubset(taxonomy):
        raise ValueError('Missing GAMS taxonomy.')
    for code, info in taxonomy.items():
        if (not _matches(r'[A-SZ][a-z0-9]*', code) or not isinstance(info, dict)
                or not isinstance(info.get('label'), str) or not info['label']):
            raise ValueError(f'Invalid GAMS class {code}.')
        _require(info, ('label', 'parent'), f'GAMS {code}')
    for code, info in taxonomy.items():
        parent = info.get('parent')
        if parent is not None and (not isinstance(parent, str) or parent not in taxonomy):
            raise ValueError(f'Invalid GAMS parent for {code}.')
        if (len(code) == 1 and parent is not None) or (len(code) > 1 and (
                parent is None or parent[0] != code[0])):
            raise ValueError(f'GAMS parent does not belong to class {code}.')
        visited = {code}
        while parent is not None:
            if parent in visited:
                raise ValueError(f'Cycle in GAMS hierarchy at {code}.')
            visited.add(parent)
            parent = taxonomy[parent].get('parent')
            if parent is not None and (not isinstance(parent, str) or parent not in taxonomy):
                raise ValueError(f'Invalid GAMS ancestor for {code}.')
    projects = data.get('projects')
    if not isinstance(projects, list):
        raise ValueError('Catalog projects must be a list.')
    seen = set()
    procedures = {}
    for project in projects:
        if not isinstance(project, dict) or not _matches(ID_PATTERN, project.get('id')):
            raise ValueError('Invalid project identity.')
        identity = project['id']
        if identity in seen:
            raise ValueError(f'Duplicate project {identity}.')
        seen.add(identity)
        repo = project.get('repository', {})
        _object(repo, f'{identity}.repository')
        _require(repo, ('host', 'owner', 'name', 'url'), f'{identity}.repository')
        if any(not isinstance(repo[field], str) or not repo[field] for field in ('owner', 'name', 'url')):
            raise ValueError(f'{identity}: repository fields must be nonempty strings.')
        slug = identity.removeprefix('github:')
        if (repo.get('host') != 'github' or f'{repo.get("owner")}/{repo.get("name")}'.lower() != slug
                or not isinstance(repo.get('url'), str) or repo['url'].lower() != f'https://github.com/{slug}'):
            raise ValueError(f'{identity}: repository and ID disagree.')
        if not isinstance(project.get('description'), str) or not isinstance(project.get('name'), str) or not project['name']:
            raise ValueError(f'{identity}: missing description or name.')
        for key in ('languages', 'build_systems', 'categories'):
            _strings(project.get(key), f'{identity}.{key}')
        author = project.get('github', {})
        _object(author, f'{identity}.github')
        _require(author, ('topics', 'topics_updated_at', 'stars', 'stars_updated_at'), f'{identity}.github')
        _strings(author.get('topics'), f'{identity}.github.topics')
        stars = author.get('stars')
        if stars is not None and (type(stars) is not int or stars < 0):
            raise ValueError(f'{identity}: invalid GitHub stars.')
        for field in ('topics_updated_at', 'stars_updated_at'):
            if field not in author:
                raise ValueError(f'{identity}: missing {field}.')
            _timestamp(author[field], f'{identity}.{field}')
        license_data = project.get('license')
        _object(license_data, f'{identity}.license')
        if any(field not in license_data or (license_data[field] is not None and not isinstance(license_data[field], str))
               for field in ('label', 'spdx_expression')):
            raise ValueError(f'{identity}: invalid license metadata.')
        curation = project.get('curation', {})
        _object(curation, f'{identity}.curation')
        _strings(curation.get('topics'), f'{identity}.curation.topics')
        codes = curation.get('gams_codes')
        _strings(codes, f'{identity}.curation.gams_codes')
        if any(code not in taxonomy for code in codes):
            raise ValueError(f'{identity}: unknown GAMS class.')
        if any(taxonomy[code]['parent'] and taxonomy[code]['parent'] not in codes for code in codes):
            raise ValueError(f'{identity}: GAMS subclass lacks its parent.')
        if (curation.get('gams_review_level') not in ('discovery', 'source-reviewed', 'driver-verified')
                or not isinstance(curation.get('gams_notes'), str)
                or 'reviewed_revision' not in curation or not _commit(curation['reviewed_revision'])):
            raise ValueError(f'{identity}: invalid classification review metadata.')
        records = curation.get('procedures', [])
        if not isinstance(records, list):
            raise ValueError(f'{identity}: procedures must be a list.')
        for record in records:
            if (not isinstance(record, dict) or not _matches(r'[a-z0-9]+(?:-[a-z0-9]+)*', record.get('id'))
                    or record['id'] in procedures or record.get('revision') != curation['reviewed_revision']
                    or record.get('review_level') != 'source-reviewed'
                    or any(not isinstance(record.get(k), str) or not record[k]
                           for k in ('module', 'procedure', 'derivatives'))):
                raise ValueError(f'{identity}: invalid procedure mapping.')
            _strings(record.get('gams_codes'), 'procedure.gams_codes')
            if not record['gams_codes'] or not set(record['gams_codes']).issubset(codes):
                raise ValueError(f'{identity}: procedure classification lacks package assignment.')
            procedures[record['id']] = record
        if 'numerical_review' in curation:
            review = curation['numerical_review']
            if (not isinstance(review, dict) or review.get('revision') != curation['reviewed_revision']
                    or not _matches(r'[0-9a-f]{64}', review.get('archive_sha256'))
                    or review.get('status') not in ('procedure-reviewed', 'support-only')
                    or review.get('procedure_ids') != [r['id'] for r in records]
                    or not isinstance(review.get('notes'), str) or not review['notes']
                    or bool(records) != (review['status'] == 'procedure-reviewed')):
                raise ValueError(f'{identity}: inconsistent numerical review coverage.')
        if project.get('playground') is not None:
            playground = project['playground']
            if not isinstance(playground, dict) or playground.get('live_service_checked') is not False:
                raise ValueError(f'{identity}: exported availability is catalog membership, not a live service check.')
            package_id = playground.get('package_id')
            if (not _matches(r'[a-zA-Z0-9_.-]+', package_id) or playground.get('catalog_status') != 'selected'
                    or playground.get('url') != f'{BASE_URL}/fpm/?package={package_id}'
                    or 'package_revision' not in playground or not _commit(playground['package_revision'])):
                raise ValueError(f'{identity}: invalid playground link or revision.')
            example = playground.get('example')
            if (not isinstance(example, dict) or not isinstance(example.get('path'), str)
                    or not example['path'] or not _matches(r'[0-9a-f]{64}', example.get('sha256'))):
                raise ValueError(f'{identity}: invalid example reference.')
    demonstrations = data.get('demonstrations', [])
    if not isinstance(demonstrations, list):
        raise ValueError('Demonstrations must be a list.')
    driver_ids = set()
    for driver in demonstrations:
        if not isinstance(driver, dict):
            raise ValueError('Invalid demonstration.')
        record = procedures.get(driver.get('procedure_id'), {})
        if (not _matches(r'[a-z0-9]+(?:-[a-z0-9]+)*', driver.get('id')) or driver['id'] in driver_ids
                or record.get('driver_id') != driver['id'] or driver.get('revision') != record.get('revision')
                or driver.get('package_id') != record.get('package_id')
                or driver.get('gams_code') not in record.get('gams_codes', [])
                or not _matches(r'[0-9a-f]{64}', driver.get('source_sha256'))):
            raise ValueError('Demonstration and procedure mapping disagree.')
        driver_ids.add(driver['id'])
    return data


def _strings(value, label):
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f'{label}: expected a list of nonempty strings.')
    if len(value) != len(set(value)):
        raise ValueError(f'{label}: duplicate entries.')


def _object(value, label):
    if not isinstance(value, dict):
        raise ValueError(f'{label}: expected an object.')


def _require(value, keys, label):
    if any(key not in value for key in keys):
        raise ValueError(f'{label}: missing required fields.')


def _matches(pattern, value):
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def _commit(value):
    return value is None or _matches(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', value)


def _timestamp(value, label):
    if value is None:
        return
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError(f'{label}: expected a timestamp with time zone or null.') from None


def merge_catalog(catalog, feed):
    """Replace this publisher's import layer; retain local records and other sources."""
    validate_export(feed)
    if (not isinstance(catalog, dict) or type(catalog.get('schema_version')) is not int
            or catalog['schema_version'] != 1 or not isinstance(catalog.get('projects'), list)):
        raise ValueError('Expected a version 1 layered catalog.')
    result = copy.deepcopy(catalog)
    publisher = feed['publisher']
    projects = {}
    for project in result['projects']:
        if not isinstance(project, dict) or not _matches(ID_PATTERN, project.get('id')):
            raise ValueError('Invalid local project identity.')
        identity = project['id']
        if identity in projects:
            raise ValueError(f'Duplicate local project {identity}.')
        if not isinstance(project.get('local', {}), dict) or not isinstance(project.get('imports', {}), dict):
            raise ValueError(f'{identity}: local and imports must be objects.')
        project.setdefault('local', {})
        project.setdefault('imports', {}).pop(publisher, None)
        projects[identity] = project
    for incoming in feed['projects']:
        project = projects.setdefault(incoming['id'], {'id': incoming['id'], 'local': {}, 'imports': {}})
        project['imports'][publisher] = copy.deepcopy(incoming)
    result['projects'] = sorted((p for p in projects.values() if p['local'] or p['imports']
                                or set(p) - {'id', 'local', 'imports'}), key=lambda p: p['id'])
    sources = result.setdefault('sources', {})
    if not isinstance(sources, dict):
        raise ValueError('Catalog sources must be an object.')
    sources[publisher] = {key: copy.deepcopy(feed[key]) for key in ('schema_version', 'snapshot_id', 'provenance', 'taxonomies')}
    if 'demonstrations' in feed:
        sources[publisher]['demonstrations'] = copy.deepcopy(feed['demonstrations'])
    if 'owners' in feed:
        sources[publisher]['owners'] = copy.deepcopy(feed['owners'])
    if 'attributions' in feed:
        sources[publisher]['attributions'] = copy.deepcopy(feed['attributions'])
    return result


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def publish_export(destination, root=ROOT):
    destination = Path(destination)
    data = build_export(root)
    write_json(destination / FEED_NAME, data)
    (destination / SCHEMA_NAME).write_text((Path(root) / 'catalog' / SCHEMA_NAME).read_text(encoding='utf-8'), encoding='utf-8')
    return data
