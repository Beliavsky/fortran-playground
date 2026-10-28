import {sourceURL, combinedSource} from './external_source.mjs';

const bytes = value => new TextEncoder().encode(value).length;
const compilers = ['gfortran', 'gfortran17', 'ifx', 'ifort', 'flang', 'lfortran', 'ofort'];
const generalValues = {
  'interface-mode': ['simple', 'advanced', 'compare'], compiler: compilers,
  standard: ['default', '1995', '2003', '2008', '2018', '2023'],
  preset: ['default', 'debug', 'optimized', 'strict'], images: ['0', '1', '2', '4'],
  example: 128, 'indent-width': ['1', '2', '3', '4', '5', '6', '7', '8'],
  'diff-mode': ['whitespace', 'exact', 'numeric'], 'diff-atol': 100, 'diff-rtol': 100,
};
const fpmValues = {
  compiler: compilers, 'package-collection': ['general', 'translated-r', 'all'],
  'package-search': 120, 'package-category': 200, 'package-sort': ['name', 'stars'],
  'package-topic-source': ['combined', 'github'], 'package-gams': 24, 'package-gams-subclass': 24,
  'available-package': 200, 'package-url': 2048, revision: 200, subdirectory: 200,
  workflow: ['consumer', 'package'], action: ['run', 'example', 'build', 'test'], target: 2048, example: 200,
};
export const stateFields = {
  fortran: {values: generalValues, checks: ['warnings', 'fast-math', 'preprocess', 'auto-indent',
    'compare-stop-failure', 'show-all-outputs', 'diff-enabled', ...compilers.filter(c => c !== 'ifort').map(c => `compare-${c}`)]},
  fpm: {values: fpmValues, checks: ['preprocess', 'program-output-only']},
};
function object(value) {return value && typeof value === 'object' && !Array.isArray(value);}
function text(value, limit) {return typeof value === 'string' && bytes(value) <= limit;}

export function validateState(state, kind) {
  if (!object(state) || state.version !== 1 || !Object.hasOwn(stateFields, state.kind) || (kind && state.kind !== kind)) {
    throw new Error('Unsupported playground state type or version.');
  }
  const allowed = ['version', 'kind', 'source', 'stdin', 'values', 'checks', 'compilerOptions', 'external'];
  if (Object.keys(state).some(k => !allowed.includes(k)) || !text(state.source, 100000) || !text(state.stdin, 100000)) {
    throw new Error('Invalid state fields, or code/input exceeds 100 KB.');
  }
  const fields = stateFields[state.kind];
  if (!object(state.values) || !object(state.checks)) throw new Error('Invalid state settings.');
  for (const [key, value] of Object.entries(state.values)) {
    const rule = fields.values[key];
    if (!rule || (Array.isArray(rule) ? !rule.includes(value) : !text(value, rule))) throw new Error(`Invalid state setting: ${key}.`);
  }
  for (const [key, value] of Object.entries(state.checks)) {
    if (!fields.checks.includes(key) || typeof value !== 'boolean') throw new Error(`Invalid state checkbox: ${key}.`);
  }
  if (state.kind === 'fortran') {
    if (!object(state.compilerOptions) || Object.entries(state.compilerOptions).some(([c, v]) => !compilers.includes(c) || !text(v, 2048))) {
      throw new Error('Invalid shared compiler options.');
    }
    if (!Array.isArray(state.external) || state.external.length > 5) throw new Error('Invalid external source list.');
    for (const row of state.external) {
      if (!object(row) || Object.keys(row).some(k => !['url', 'source'].includes(k)) || !text(row.url, 2048)) throw new Error('Invalid external source row.');
      if (row.url) sourceURL(row.url);
      if (row.source !== null) {
        const s = row.source;
        if (!object(s) || Object.keys(s).some(k => !['source', 'filename', 'url', 'requestUrl', 'sha256'].includes(k))
            || !text(s.source, 100000) || !text(s.filename, 256) || !text(s.url, 2048)
            || !text(s.requestUrl, 2048) || !/^[a-f0-9]{64}$/.test(s.sha256)
            || sourceURL(row.url) !== sourceURL(s.requestUrl)) throw new Error('Invalid shared external source snapshot.');
        sourceURL(s.url);
      }
    }
    combinedSource(state.source, state.external.map(row => row.source));
  } else if ('external' in state || 'compilerOptions' in state) throw new Error('Unexpected FPM state fields.');
  if (bytes(JSON.stringify(state)) > 1000000) throw new Error('Playground state is too large for a link.');
  return state;
}

export function captureState(kind, get, source, extra = {}) {
  const fields = stateFields[kind];
  return validateState({version: 1, kind, source, stdin: get('stdin').value,
    values: Object.fromEntries(Object.keys(fields.values).map(id => [id, get(id).value])),
    checks: Object.fromEntries(fields.checks.map(id => [id, Boolean(get(id).checked)])), ...extra}, kind);
}

export function createStateLink(href, state) {
  validateState(state);
  const data = new TextEncoder().encode(JSON.stringify(state));
  let binary = '';
  for (let i = 0; i < data.length; i += 8192) binary += String.fromCharCode(...data.subarray(i, i + 8192));
  const url = new URL(href);
  url.search = ''; url.username = ''; url.password = '';
  url.hash = 'state=v1.' + btoa(binary).replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, '');
  return url.href;
}

export function stateFromHash(hash, kind) {
  if (!hash.startsWith('#state=')) return null;
  if (!hash.startsWith('#state=v1.')) throw new Error('Unsupported playground state version.');
  const encoded = hash.slice(10);
  if (encoded.length > 1333336 || !/^[A-Za-z0-9_-]+$/.test(encoded)) throw new Error('Invalid or oversized playground state link.');
  try {
    const binary = atob(encoded.replaceAll('-', '+').replaceAll('_', '/'));
    const state = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(Uint8Array.from(binary, c => c.charCodeAt(0))));
    return validateState(state, kind);
  } catch (error) {throw new Error('Cannot restore playground state: ' + error.message);}
}

export async function copyStateLink(href, state, get) {
  get('share-state-field').hidden = true;
  try {
    const link = createStateLink(href, state);
    get('share-state-link').value = link;
    try {
      await navigator.clipboard.writeText(link);
      get('share-state-status').textContent = 'State link copied. It includes code and standard input; opening it does not run a job.';
    } catch {
      get('share-state-field').hidden = false;
      get('share-state-link').focus(); get('share-state-link').select();
      get('share-state-status').textContent = 'Copy the selected state link. It includes code and standard input; opening it does not run a job.';
    }
    if (link.length > 8000) get('share-state-status').textContent += ' This long link may be truncated by some sites.';
  } catch (error) {get('share-state-status').textContent = error.message;}
}
