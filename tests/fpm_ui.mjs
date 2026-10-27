import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const html = readFileSync(new URL('../site/fpm/index.html', import.meta.url), 'utf8');
const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]));
const localExecution = process.argv.includes('--local');
if (localExecution) {
  ids.add('local-source-link'); ids.add('local-projects-link');
  globalThis.location = new URL('http://127.0.0.1:8766/fpm/#session=private');
  globalThis.sessionStorage = {getItem() {return 'private';}, setItem() {}};
  globalThis.history = {replaceState() {}};
}
const elements = new Map();
const downloads = [], blobs = new Map();
URL.createObjectURL = blob => {const url = `blob:export-${blobs.size}`; blobs.set(url, blob); return url;};
URL.revokeObjectURL = () => {};
globalThis.document = {
  documentElement: {dataset: {execution: localExecution ? 'local' : 'hosted'}},
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
  createElement(tag) {return tag === 'a' ? {click() {downloads.push({name: this.download, blob: blobs.get(this.href)});}} : {};},
};
const get = id => document.getElementById(id);
get('workflow').value = 'consumer';
get('action').value = 'run';
get('compiler').options = ['gfortran', 'gfortran17', 'ifx', 'flang'].map(value => ({value}));
const legacyService = process.argv.includes('--legacy');
const examples = JSON.parse(readFileSync(new URL('../site/fpm/examples.json', import.meta.url), 'utf8'));
const packages = JSON.parse(readFileSync(new URL('../site/fpm/packages.json', import.meta.url), 'utf8'));
const translated = JSON.parse(readFileSync(new URL('../site/fpm/translated-r.json', import.meta.url), 'utf8'));
let translatedFetches = 0;
const unconfigured = process.argv.includes('--unconfigured');
let submissions = [], fail = false, cancellations = 0, transportFailure = false;
let runtimeFailure = false, holdRuntime;
const runtime = JSON.parse(readFileSync(new URL('../site/fpm/project-runtime.json', import.meta.url), 'utf8'));
let result = {ok: true, packages: [{repository: 'test/package', revision: 'a'.repeat(40)}],
  stages: [{name: 'Run', ok: true, seconds: 0.1, command: ['fpm', 'run'], stdout: '<script>42</script>', stderr: '', exit_code: 0}]};
globalThis.fetch = async (url, options = {}) => {
  if (localExecution && url.startsWith('/api/')) {
    assert.equal(options.headers['X-Local-Token'], 'private');
    assert.ok(url.startsWith('/api/fpm/catalog/'));
    url = '/api/' + url.slice('/api/fpm/catalog/'.length);
  } else if (localExecution) assert.ok(!url.includes('modal.run') && url !== './service.json');
  let value;
  if (url === './examples.json') value = examples;
  else if (url === './project-runtime.json') {
    if (holdRuntime) await holdRuntime;
    if (runtimeFailure) return {ok: false};
    value = runtime;
  }
  else if (url === './packages.json') value = packages;
  else if (url === './translated-r.json') {translatedFetches++; value = translated;}
  else if (url === './service.json') value = {url: unconfigured ? '' : 'https://fpm.modal.run'};
  else if (url.endsWith('/api/health')) value = {ok: true, compiler: 'GNU Fortran 16.2.0', fpm: '0.12.0',
    ...(legacyService ? {} : {compilers: {gfortran: 'GNU Fortran 16.2.0', ifx: 'Intel ifx',
      ...(localExecution ? {lfortran: 'LFortran local'} : {})},
      precompiled: localExecution ? {} : {[packages[0].id]: {revision: packages[0].revision, compiler: 'gfortran'}}}),
    ...(localExecution ? {local: true, workspace: 'C:/test'} : {})};
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
// Downloads do not depend on API health and must not submit jobs.
get('package-url').value = `https://github.com/${packages[0].repository}`;
get('revision').value = packages[0].revision;
get('package-url').listeners.input();
assert.equal(get('package-source-links').hidden, false);
assert.equal(get('package-source').href, `https://github.com/${packages[0].repository}/tree/${packages[0].revision}`);
get('source').value = 'program main\n! edited snapshot\nend program\n';
get('stdin').value = 'saved input\n';
get('download-main').listeners.click();
assert.equal(downloads.at(-1).name, 'main.f90');
assert.equal(await downloads.at(-1).blob.text(), get('source').value);
runtimeFailure = true;
await get('download-project').listeners.click();
assert.match(get('download-note').textContent, /retry/);
assert.equal(get('download-project').disabled, false);
runtimeFailure = false;
let releaseRuntime;
holdRuntime = new Promise(resolve => {releaseRuntime = resolve;});
const saving = get('download-project').listeners.click();
assert.equal(get('download-project').disabled, true);
get('source').value = 'changed while fetching';
get('revision').value = 'main';
releaseRuntime();
await saving;
const saved = Buffer.from(await downloads.at(-1).blob.arrayBuffer()).toString('utf8');
assert.match(saved, /edited snapshot/);
assert.ok(!saved.includes('changed while fetching'));
assert.ok(saved.includes(packages[0].revision));
assert.equal(get('download-project').disabled, false);
assert.equal(submissions.length, 0);
get('revision').value = 'main'; get('revision').listeners.input();
assert.equal(get('package-source-links').hidden, true);
get('stdin').value = '';
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
if (!localExecution) assert.equal(get('compiler').options.find(option => option.value === 'flang').disabled, true);
else {
  assert.ok(get('compiler').options.some(option => option.value === 'lfortran'));
  assert.match(get('local-projects-link').href, /\/fpm\/projects\/#session=private/);
}
assert.equal(get('compiler').options.find(option => option.value === 'ifx').disabled, legacyService);
assert.equal(get('source-pane').hidden, false);
assert.equal(get('test-action').disabled, true);
assert.equal(get('example').options.length, 5);
assert.equal(submissions.length, 0, 'Initialization must not submit a job');
get('package-search').value = 'lapack';
get('package-search').listeners.input();
assert.deepEqual(get('available-package').options.map(p => p.value), ['', 'fortran-lapack']);
get('package-search').value = '';
get('package-search').listeners.input();
get('package-category').value = 'Interpolation';
get('package-category').listeners.change();
assert.ok(get('available-package').options.length > 1);
assert.ok(get('available-package').options.slice(1).every(option =>
  packages.find(p => p.id === option.value).category === 'Interpolation'));
get('package-category').value = '';
get('package-category').listeners.change();
assert.equal(submissions.length, 0, 'Filtering must not submit jobs or edit the program');
get('available-package').value = packages[0].id;
get('available-package').listeners.change();
assert.equal(get('load-package').disabled, legacyService);
assert.match(get('package-note').textContent, /linear algebra/);
if (!legacyService) {
  get('compiler').value = 'ifx';
  get('compiler').listeners.change();
  get('load-package').listeners.click();
  assert.equal(get('compiler').value, localExecution ? 'ifx' : 'gfortran');
  assert.match(get('connection').textContent, localExecution ? /Local FPM/ : /GNU Fortran 16/);
  assert.equal(get('source').value, packages[0].source);
  assert.equal(get('revision').value, packages[0].revision);
  assert.equal(submissions.length, 0, 'Loading a cached package must not submit a job');
}
get('available-package').value = packages[1].id;
get('available-package').listeners.change();
assert.equal(get('load-package').disabled, !localExecution, 'Local packages build from source; hosted packages require verification');
assert.match(resultText({ok: true, cache: {package: 'fortran-lapack', compiler: 'GNU 16', library_reused: true}}), /library reused/);

get('example').value = examples[0].name;
get('example').listeners.change();
get('load-example').listeners.click();
assert.equal(get('source').value, examples[0].source);
assert.equal(get('revision').value, examples[0].revision);
await get('submit').listeners.click();
assert.equal(submissions.length, 1);
assert.equal(submissions[0].workflow, 'consumer');
assert.equal(submissions[0].compiler, legacyService ? undefined : localExecution ? 'ifx' : 'gfortran');
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
  get('compiler').value = localExecution ? 'gfortran' : 'ifx'; get('compiler').listeners.change();
  assert.equal(get('target').value, '');
  assert.match(get('connection').textContent, localExecution ? /GNU Fortran 16/ : /Intel ifx/);
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
assert.equal(submissions.at(-1).compiler, legacyService ? undefined : localExecution ? 'gfortran' : 'ifx');
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

transportFailure = false;
assert.equal(translatedFetches, 0, 'General collection does not fetch translated R metadata');
get('package-collection').value = 'translated-r';
await get('package-collection').listeners.change();
assert.equal(translatedFetches, 1);
assert.match(get('package-count').textContent, /596/);
get('package-search').value = 'Metrics'; get('package-search').listeners.input();
assert.ok(get('available-package').options.some(option => option.value === 'Metrics'));
get('available-package').value = 'Metrics'; get('available-package').listeners.change();
assert.equal(get('load-package').disabled, false, 'Cold builds do not require a precompiled image');
get('load-package').listeners.click();
assert.equal(get('workflow').value, 'package');
assert.equal(get('subdirectory').value, 'Metrics');
assert.match(get('package-source').href, /\/Metrics$/);
await get('submit').listeners.click();
assert.equal(submissions.at(-1).subdirectory, 'Metrics');
assert.equal(submissions.at(-1).workflow, 'package');
get('workflow').value = 'consumer'; get('workflow').listeners.change();
get('source').value = 'program main\nprint *, 42\nend program';
await get('download-project').listeners.click();
const translatedZip = Buffer.from(await downloads.at(-1).blob.arrayBuffer()).toString('utf8');
assert.ok(translatedZip.includes('"subdirectory": "Metrics"'));
get('package-collection').value = 'general';
await get('package-collection').listeners.change();
get('example').value = examples[0].name; get('load-example').listeners.click();
assert.equal(get('subdirectory').value, '', 'Loading a general example clears the translated directory');
assert.equal(translatedFetches, 1);
globalThis.setTimeout = originalTimeout;
console.log('FPM UI: workflows, targets, stdin, results, no automatic submissions, and error recovery passed.');
