import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const html = readFileSync(new URL('../site/fpm/index.html', import.meta.url), 'utf8');
const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]));
const elements = new Map();
globalThis.document = {
  getElementById(id) {
    assert.ok(ids.has(id), `Missing element ${id}`);
    if (!elements.has(id)) elements.set(id, {
      value: '', disabled: false, hidden: false, textContent: '', readOnly: false, options: [], listeners: {},
      classList: {toggle() {}}, addEventListener(name, fn) {this.listeners[name] = fn;},
      appendChild(child) {this.options.push(child);}, replaceChildren(...children) {this.options = children;},
      focus() {}, select() {},
    });
    return elements.get(id);
  },
  createElement() {return {};},
};
const get = id => document.getElementById(id);
get('workflow').value = 'consumer';
get('action').value = 'run';
get('compiler').options = ['gfortran', 'gfortran17', 'ifx', 'flang'].map(value => ({value}));
const legacyService = process.argv.includes('--legacy');
const examples = JSON.parse(readFileSync(new URL('../site/fpm/examples.json', import.meta.url), 'utf8'));
const unconfigured = process.argv.includes('--unconfigured');
let submissions = [], fail = false, cancellations = 0, transportFailure = false;
let result = {ok: true, packages: [{repository: 'test/package', revision: 'a'.repeat(40)}],
  stages: [{name: 'Run', ok: true, seconds: 0.1, command: ['fpm', 'run'], stdout: '<script>42</script>', stderr: '', exit_code: 0}]};
globalThis.fetch = async (url, options = {}) => {
  let value;
  if (url === './examples.json') value = examples;
  else if (url === './service.json') value = {url: unconfigured ? '' : 'https://fpm.modal.run'};
  else if (url.endsWith('/api/health')) value = {ok: true, compiler: 'GNU Fortran 16.2.0', fpm: '0.12.0',
    ...(legacyService ? {} : {compilers: {gfortran: 'GNU Fortran 16.2.0', ifx: 'Intel ifx'}})};
  else if (url.endsWith('/cancel')) {cancellations++; value = {state: 'cancelling'};}
  else if (url.endsWith('/api/jobs')) {
    if (fail) return {ok: false, async json() {return {error: 'Both FPM job slots are busy.'};}};
    submissions.push(JSON.parse(options.body)); value = {id: 'job-123'};
  } else if (url.endsWith('/api/jobs/job-123')) {
    if (transportFailure) throw new Error('Connection lost');
    value = {state: 'done', result};
  } else throw new Error(`Unexpected URL: ${url}`);
  return {ok: true, async json() {return value;}};
};
const originalTimeout = globalThis.setTimeout;
globalThis.setTimeout = fn => {queueMicrotask(fn); return 1;};
const {resultText} = await import('../site/fpm/fpm.mjs');
if (unconfigured) {
  assert.equal(get('submit').disabled, true);
  assert.match(get('connection').textContent, /not been configured/);
  get('example').value = examples[0].name;
  get('load-example').listeners.click();
  assert.equal(get('source').value, examples[0].source, 'Examples remain usable without a service');
  assert.equal(get('source').readOnly, false);
  assert.equal(submissions.length, 0);
  console.log('Unconfigured FPM service leaves examples and editing available and submission disabled.');
  process.exit(0);
}
assert.equal(get('submit').disabled, false);
assert.equal(get('compiler').value, 'gfortran');
assert.equal(get('compiler').options.find(option => option.value === 'flang').disabled, true);
assert.equal(get('compiler').options.find(option => option.value === 'ifx').disabled, legacyService);
assert.equal(get('source-pane').hidden, false);
assert.equal(get('test-action').disabled, true);
assert.equal(get('example').options.length, 5);
assert.equal(submissions.length, 0, 'Initialization must not submit a job');

get('example').value = examples[0].name;
get('example').listeners.change();
get('load-example').listeners.click();
assert.equal(get('source').value, examples[0].source);
assert.equal(get('revision').value, examples[0].revision);
await get('submit').listeners.click();
assert.equal(submissions.length, 1);
assert.equal(submissions[0].workflow, 'consumer');
assert.equal(submissions[0].compiler, legacyService ? undefined : 'gfortran');
assert.equal(submissions[0].source, examples[0].source);
assert.match(get('output').value, /<script>42<\/script>/, 'Output is plain text, not inserted as HTML');
assert.equal(get('status').textContent, 'PASS');

get('workflow').value = 'package';
get('workflow').listeners.change();
assert.equal(get('source-pane').hidden, true);
assert.equal(get('target-controls').hidden, false);
assert.equal(get('test-action').disabled, false);
if (!legacyService) {
  get('target').value = 'old-target';
  get('compiler').value = 'ifx'; get('compiler').listeners.change();
  assert.equal(get('target').value, '');
  assert.match(get('connection').textContent, /Intel ifx/);
}
result = {ok: false, needs_target: true, error: 'Choose an application target', targets: ['alpha', 'beta'], stages: []};
await get('submit').listeners.click();
assert.equal(get('status').textContent, 'Choose a target');
assert.deepEqual(get('targets').options.map(option => option.value), ['alpha', 'beta']);
get('target').value = 'alpha';
get('stdin').value = '41\n';
result = {ok: true, stages: []};
await get('submit').listeners.click();
assert.equal(submissions.at(-1).target, 'alpha');
assert.equal(submissions.at(-1).compiler, legacyService ? undefined : 'ifx');
assert.equal(submissions.at(-1).stdin, '41\n');

get('action').value = 'test';
get('action').listeners.change();
assert.equal(get('target').value, '', 'Changing action clears stale target names');
await get('submit').listeners.click();
assert.equal(submissions.at(-1).action, 'test');
get('workflow').value = 'consumer';
get('workflow').listeners.change();
assert.equal(get('action').value, 'run');
get('action').value = 'build';
get('action').listeners.change();
assert.equal(get('stdin-pane').hidden, true);

fail = true;
await get('submit').listeners.click();
assert.equal(get('submit').disabled, false, 'Admission errors must leave the interface usable');
assert.match(get('output').value, /slots are busy/);
fail = false; transportFailure = true;
await get('submit').listeners.click();
assert.equal(cancellations, 1, 'A lost connection cancels the known job');
assert.equal(get('submit').disabled, false);
assert.match(resultText({ok: false, error: 'Timed out', stages: []}), /Timed out/);
globalThis.setTimeout = originalTimeout;
console.log('FPM UI: workflows, targets, stdin, results, no automatic submissions, and error recovery passed.');
