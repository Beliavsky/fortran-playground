import assert from 'node:assert/strict';
import {createStateLink, stateFromHash, validateState} from '../site/state_links.mjs';

const general = {version: 1, kind: 'fortran', source: 'print *, "café λ + & #"\nend\n', stdin: '2 3\n',
  values: {'interface-mode': 'compare', compiler: 'gfortran', standard: '2018', preset: 'debug', images: '2'},
  checks: {'compare-gfortran': true, 'compare-ifx': true, preprocess: true}, compilerOptions: {gfortran: '-O2', ifx: '-O3'},
  external: [{url: 'https://example.test/mod.f90', source: {source: 'module m\nend module\n',
    filename: 'mod.f90', url: 'https://example.test/mod.f90', requestUrl: 'https://example.test/mod.f90', sha256: 'a'.repeat(64)}}]};
const fpm = {version: 1, kind: 'fpm', source: 'program p\nend\n', stdin: 'hello\n',
  values: {'package-collection': 'translated-r', 'package-search': 'garch', 'package-url': 'https://github.com/owner/repo',
    revision: 'a'.repeat(40), subdirectory: 'packages/foo', workflow: 'package', action: 'example',
    target: 'demo_* test?', compiler: 'gfortran', 'package-gams': 'I', 'package-gams-subclass': 'I1a2'},
  checks: {preprocess: false, 'program-output-only': true}};
for (const state of [general, fpm]) {
  const url = new URL(createStateLink('https://example.test/?owner=1#session=SECRET', state));
  assert.equal(url.search, ''); assert.ok(!url.hash.includes('SECRET'));
  assert.deepEqual(stateFromHash(url.hash, state.kind), state);
  assert.throws(() => stateFromHash(url.hash, state.kind === 'fpm' ? 'fortran' : 'fpm'), /type/);
}
assert.equal(stateFromHash('#code=end'), null);
assert.equal(stateFromHash('#some-section'), null);
for (const hash of ['#state=v9.abc', '#state=v1.%', '#state=v1.!!!!', '#state=v1.a', '#state=v1.' + 'a'.repeat(1333337)]) {
  assert.throws(() => stateFromHash(hash));
}
for (const mutate of [
  s => s.version = 2, s => s.kind = 'constructor', s => s.ownerKey = 'private',
  s => s.values['owner-key'] = 'private', s => s.checks.preprocess = 'yes',
  s => s.values.compiler = 'arbitrary', s => s.stdin = 'x'.repeat(100001),
  s => s.compilerOptions['__proto__x'] = '-O3', s => s.external[0].url = 'file:///C:/secret.f90',
  s => s.external[0].source.requestUrl = 'https://other.test/file',
  s => s.source = 'x'.repeat(100001),
]) {
  const state = structuredClone(general); mutate(state);
  assert.throws(() => validateState(state));
}
const empty = {...fpm, source: '', stdin: '', values: {}, checks: {}};
assert.deepEqual(stateFromHash(new URL(createStateLink('https://example.test/', empty)).hash), empty);
console.log('Versioned playground state round trips, Unicode, snapshots, limits, field allowlists and token exclusion passed.');
