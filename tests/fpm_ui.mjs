import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {playgroundConfig} from '../site/config.mjs';
const allEnabled = process.argv.includes('--all-enabled')
  || (!process.argv.includes('--all-link') && playgroundConfig.enableAllFpmPackages === true);
playgroundConfig.enableAllFpmPackages = allEnabled;
if (process.argv.includes('--all-link')) globalThis.location = new URL('https://example.test/fpm/?collection=all');

const html = readFileSync(new URL('../site/fpm/index.html', import.meta.url), 'utf8');
const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]));
for (const id of ['subdirectory', 'subdirectory-label']) {
  assert.match(html, new RegExp(`<[^>]*id="${id}"[^>]*\\bhidden\\b`));
}
const localExecution = process.argv.includes('--local');
const preferences = new Map();
globalThis.localStorage = {getItem: key => preferences.get(key) ?? null,
  setItem: (key, value) => preferences.set(key, value)};
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
      value: '', disabled: false, hidden: false, readOnly: false, options: [], listeners: {},
      get textContent() {return this.text || '';},
      set textContent(value) {this.text = value; this.options = [];},
      classList: {toggle() {}}, addEventListener(name, fn) {this.listeners[name] = fn;},
      setAttribute(key, value) {this[key] = value;},
      appendChild(child) {this.options.push(child);}, replaceChildren(...children) {this.options = children;},
      focus() {}, select() {},
    });
    return elements.get(id);
  },
  createElement(tag) {return tag === 'a' ? {setAttribute(key, value) {this[key] = value;}, click() {downloads.push({name: this.download, blob: blobs.get(this.href)});}}
    : {listeners: {}, addEventListener(name, fn) {this.listeners[name] = fn;}};},
};
const get = id => document.getElementById(id);
get('workflow').value = 'consumer';
get('action').value = 'run';
get('compiler').options = ['gfortran', 'gfortran17', 'ifx', 'flang'].map(value => ({value}));
const legacyService = process.argv.includes('--legacy');
const examples = JSON.parse(readFileSync(new URL('../site/fpm/examples.json', import.meta.url), 'utf8'));
const packages = JSON.parse(readFileSync(new URL('../site/fpm/packages.json', import.meta.url), 'utf8'));
// Keep topic-search behavior testable if an author later edits live metadata.
const topicFixture = packages.find(p => p.id === 'dvode');
topicFixture.topics = [...new Set([...(topicFixture.topics || []), 'adams-bashforth', 'fortran'])];
const translated = JSON.parse(readFileSync(new URL('../site/fpm/translated-r.json', import.meta.url), 'utf8'));
const allPackages = JSON.parse(readFileSync(new URL('../site/fpm/all-packages.json', import.meta.url), 'utf8'));
// A retained clean-build audit must not override a selected package's cached recipe.
for (const entry of [packages[0], allPackages.find(p => p.id === packages[0].id)]) {
  entry.audit = {tested_at: '2026-10-27', revision: entry.revision, summary: 'Build passed',
    ...entry.audit, verification: {preprocess: true}};
}
let allFetches = 0;
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
  else if (url === './all-packages.json') {allFetches++; value = allPackages;}
  else if (url === './translated-r.json') {translatedFetches++; value = translated;}
  else if (url === './service.json') value = {url: unconfigured ? '' : 'https://fpm.modal.run'};
  else if (url.endsWith('/api/health')) value = {ok: true, compiler: 'GNU Fortran 16.2.0', fpm: '0.12.0',
    ...(legacyService ? {} : {features: {translated_r: true, run_examples: true, preprocess: true}}),
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
const {resultText, programOutputText} = await import('../site/fpm/fpm.mjs');
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
assert.equal(get('example-action').disabled, true);
assert.equal(get('example').options.length, 5);
assert.equal(submissions.length, 0, 'Initialization must not submit a job');
assert.equal(get('package-collection').value, 'general', 'Selected remains the default');
assert.equal(allFetches, 0, 'Selected does not download the full catalog');
assert.equal(get('package-gams').value, '');
assert.equal(get('package-gams-controls').hidden, false);
assert.equal(get('package-gams-subclass-controls').hidden, true);
const beforeGamsSearch = get('source').value;
get('package-gams').value = 'C'; get('package-gams').listeners.change();
assert.equal(get('package-gams-subclass-controls').hidden, false);
const childCodes = get('package-gams-subclass').options.map(p => p.value);
assert.ok(childCodes.indexOf('C9') < childCodes.indexOf('C10'), 'Subclasses use numerical order');
assert.ok(get('available-package').options.some(p => p.value === 'm_calculator'), 'Parents include broad-only assignments');
get('package-gams-subclass').value = 'C10'; get('package-gams-subclass').listeners.change();
assert.ok(get('available-package').options.some(p => p.value === 'specfun'));
assert.ok(!get('available-package').options.some(p => p.value === 'm_calculator'), 'A child excludes broad-only assignments');
get('package-gams-subclass').value = 'C1'; get('package-gams-subclass').listeners.change();
assert.equal(get('available-package').options.length, 1, 'C1 must not match sibling C10');
get('package-gams').value = 'L'; get('package-gams').listeners.change();
assert.equal(get('package-gams-subclass').value, '', 'Changing parents clears the old subclass');
get('package-gams-subclass').value = 'L6'; get('package-gams-subclass').listeners.change();
assert.ok(get('available-package').options.some(p => p.value === 'mersenne-twister-fortran'));
assert.ok(!get('available-package').options.some(p => p.value === 'fortsa'));
get('package-gams-subclass').value = 'L1'; get('package-gams-subclass').listeners.change();
assert.ok(!get('available-package').options.some(p => p.value === 'fortsa'), 'L1 must not match siblings L10 or L11');
get('package-gams').value = ''; get('package-gams').listeners.change();
get('package-search').value = 'GAMS: L10'; get('package-search').listeners.input();
assert.deepEqual(get('available-package').options.slice(1).map(p => p.value), ['fortsa']);
get('package-search').value = 'GAMS G1'; get('package-search').listeners.input();
assert.ok(get('available-package').options.some(p => p.value === 'minpack'));
assert.ok(!get('available-package').options.some(p => p.value === 'lbfgsb'));
get('package-search').value = ''; get('package-search').listeners.input();
get('package-gams').value = 'B'; get('package-gams').listeners.change();
assert.equal(get('package-gams-subclass-controls').hidden, true, 'Parents without published children hide the subclass control');
assert.equal(get('package-gams-subclass').disabled, true);
get('package-gams').value = 'D'; get('package-gams').listeners.change();
assert.ok(get('available-package').options.some(p => p.value === 'fortran-lapack'));
assert.ok(get('available-package').options.slice(1).every(option =>
  packages.find(p => p.id === option.value).gams.some(c => c.code === 'D')));
get('package-search').value = 'lapack'; get('package-search').listeners.input();
const lapackMatches = get('available-package').options.map(p => p.value);
get('package-topic-source').value = 'github'; get('package-topic-source').listeners.change();
assert.deepEqual(get('available-package').options.map(p => p.value), lapackMatches,
  'GAMS classification works independently of topic source');
get('package-category').value = 'Integration'; get('package-category').listeners.change();
assert.equal(get('available-package').options.length, 1, 'GAMS, category, and text filters combine');
await get('package-search-results').options.find(p => p.textContent === 'Search all categories').listeners.click();
assert.ok(get('available-package').options.length > 1);
get('available-package').value = 'fortran-lapack'; get('available-package').listeners.change();
const classLink = get('package-gams-details').options[1];
assert.equal(classLink.textContent, 'D — Linear Algebra');
assert.equal(classLink.href, 'https://gams.nist.gov/cgi-bin/serve.cgi/Class/D');
assert.equal(classLink.target, '_blank');
assert.equal(classLink.rel, 'noopener noreferrer');
get('package-search').value = 'GAMS: B'; get('package-search').listeners.input();
assert.equal(get('available-package').options.length, 1, 'Contradictory class filters give no matches');
await get('package-search-results').options.find(p => p.textContent === 'Search all GAMS classes').listeners.click();
assert.ok(get('available-package').options.some(p => p.value === 'fortran-primes'));
get('package-search').value = 'GAMS L'; get('package-search').listeners.input();
assert.ok(get('available-package').options.some(p => p.value === 'mersenne-twister-fortran'));
assert.ok(!get('available-package').options.some(p => p.value === 'fmin'));
get('package-search').value = 'GAMS O'; get('package-search').listeners.input();
assert.equal(get('available-package').options.length, 1, 'An unassigned class is a valid empty search');
await get('package-search-results').options.find(p => p.textContent === 'Clear GAMS search').listeners.click();
assert.equal(get('available-package').options.length, packages.length + 1);
for (const code of ['F', 'G', 'K']) {
  get('package-gams').value = code; get('package-gams').listeners.change();
  assert.ok(get('available-package').options.some(p => p.value === 'minpack'), 'A package may have several GAMS classes');
}
get('package-gams').value = ''; get('package-gams').listeners.change();
get('package-search').value = 'integral transforms'; get('package-search').listeners.input();
assert.ok(get('available-package').options.some(p => p.value === 'fftpack'), 'Text search includes GAMS labels');
get('package-search').value = ''; get('package-search').listeners.input();
get('package-topic-source').value = 'combined'; get('package-topic-source').listeners.change();
assert.equal(get('source').value, beforeGamsSearch);
assert.equal(submissions.length, 0, 'GAMS browsing never edits code or submits jobs');
assert.equal(get('package-topic-source').value, 'combined');
const originalTopics = packages[0].playground_topics;
packages[0].playground_topics = [...originalTopics, 'playground-only-fixture'];
const programBeforeTopicSearch = get('source').value;
get('package-search').value = 'playground only fixture'; get('package-search').listeners.input();
assert.equal(get('available-package').value, packages[0].id);
assert.ok(get('package-topics').options.some(p => p.textContent === 'Playground topics:'));
assert.ok(get('package-topics').options.some(p => p.textContent === 'GitHub topics:'));
const topicButton = get('package-topics').options.find(p => p.textContent === 'playground-only-fixture');
topicButton.listeners.click();
assert.equal(get('package-search').value, 'playground-only-fixture');
get('package-topic-source').value = 'github'; get('package-topic-source').listeners.change();
assert.equal(get('available-package').options.length, 1, 'GitHub-only mode excludes playground-only topic matches');
assert.equal(get('package-topics').hidden, true);
get('package-search').value = packages[0].repository; get('package-search').listeners.input();
assert.equal(get('available-package').value, packages[0].id, 'Repository and owner search remain available in GitHub-only mode');
assert.ok(!get('package-topics').options.some(p => p.textContent === 'Playground topics:'));
get('package-topic-source').value = 'combined'; get('package-topic-source').listeners.change();
packages[0].playground_topics = originalTopics;
get('package-search').value = ''; get('package-search').listeners.input();
assert.equal(get('source').value, programBeforeTopicSearch, 'Topic filtering does not edit the program');
assert.equal(submissions.length, 0, 'Topic filtering does not submit jobs');
assert.equal(get('package-sort').value, 'name');
const alphabetical = [...packages].sort((a, b) => (a.name || a.id).localeCompare(b.name || b.id, 'en', {sensitivity: 'base', numeric: true})
  || a.repository.localeCompare(b.repository, 'en'));
assert.deepEqual(get('available-package').options.slice(1).map(p => p.value), alphabetical.map(p => p.id));
const savedStars = packages.map(p => [p.stars, p.stars_updated_at]);
for (const p of packages) {delete p.stars; delete p.stars_updated_at;}
packages[0].stars = 500; packages[1].stars = 500; packages[2].stars = 0;
packages[0].stars_updated_at = '2026-10-28T00:00:00+00:00';
get('available-package').value = packages[1].id;
get('package-sort').value = 'stars'; get('package-sort').listeners.change();
assert.deepEqual(get('available-package').options.slice(1, 4).map(p => p.value), packages.slice(0, 3).map(p => p.id),
  'Stars sort descending, name breaks ties, zero precedes missing counts');
assert.equal(get('available-package').value, packages[1].id, 'Sorting preserves selection');
assert.match(get('available-package').options[1].textContent, /\[500 stars\]/);
assert.match(get('available-package').options[4].textContent, /stars unavailable/);
assert.match(get('package-stars-note').textContent, /Stars updated 2026-10-28/);
get('package-search').value = 'fortran'; get('package-search').listeners.input();
assert.deepEqual(get('package-search-results').options.map(p => p.textContent),
  get('available-package').options.slice(1, 21).map(p => p.textContent.replace(' [FPM unavailable]', '')),
  'Search buttons and dropdown use the same ordering and star labels');
assert.equal(submissions.length, 0, 'Sorting never submits a job');
packages.forEach((p, i) => {p.stars = savedStars[i][0]; p.stars_updated_at = savedStars[i][1];});
get('package-sort').value = 'name'; get('package-sort').listeners.change();
assert.equal(get('package-stars-note').hidden, true);
get('package-search').value = 'DVODE';
get('package-search').listeners.input();
assert.equal(get('available-package').value, 'dvode');
get('package-search').value = 'adams bashforth'; get('package-search').listeners.input();
assert.ok(get('available-package').options.some(item => item.value === 'dvode'));
get('available-package').value = 'dvode'; get('available-package').listeners.change();
assert.equal(get('package-topics').hidden, false);
const topicLabel = get('package-topics').options.find(item => item.textContent === 'adams-bashforth');
get('package-category').value = 'Interpolation';
topicLabel.listeners.click();
assert.equal(get('package-category').value, '');
assert.equal(get('package-search').value, 'adams-bashforth');
assert.ok(get('available-package').options.some(item => item.value === 'dvode'));
const labels = get('package-topics').options.map(item => item.textContent);
assert.ok(labels.indexOf('adams-bashforth') < labels.indexOf('fortran'));
get('package-search').value = 'DVODE'; get('package-search').listeners.input();
assert.ok(get('package-search-results').options.some(item => item.textContent.startsWith('dvode')));
get('package-category').value = 'Interpolation'; get('package-category').listeners.change();
assert.equal(get('available-package').options.length, 1);
await get('package-search-results').options.find(item => item.textContent === 'Search all categories').listeners.click();
assert.equal(get('available-package').value, 'dvode');
get('package-search').value = 'lapack';
get('package-search').listeners.input();
assert.ok(get('available-package').options.some(p => p.value === 'fortran-lapack'));
for (const packageEntry of packages.filter(p => p.topics?.includes('lapack'))) {
  assert.ok(get('available-package').options.some(p => p.value === packageEntry.id), 'Topic matches join description matches');
}
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
const sourceNote = get('package-note').options;
assert.equal(sourceNote[0].textContent, packages[0].repository);
assert.equal(sourceNote[0].href, `https://github.com/${packages[0].repository}`);
assert.equal(sourceNote[2].textContent, packages[0].revision.slice(0, 7));
assert.equal(sourceNote[2].title, packages[0].revision);
assert.equal(sourceNote[2].href, `https://github.com/${packages[0].repository}/tree/${packages[0].revision}`);
for (const link of [sourceNote[0], sourceNote[2]]) {
  assert.equal(link.target, '_blank');
  assert.equal(link.rel, 'noopener noreferrer');
}
if (!legacyService) {
  get('compiler').value = 'ifx';
  get('compiler').listeners.change();
  const beforeSelection = get('source').value;
  get('available-package').listeners.change();
  assert.equal(get('source').value, beforeSelection, 'Selecting a package does not load its code');
  get('available-package').listeners.dblclick();
  assert.equal(get('compiler').value, localExecution ? 'ifx' : 'gfortran');
  assert.match(get('connection').textContent, localExecution ? /Local FPM/ : /GNU Fortran 16/);
  assert.equal(get('source').value, packages[0].source);
  assert.equal(get('revision').value, packages[0].revision);
  assert.equal(get('preprocess').checked, false, 'Selected packages use their recorded build recipe');
  assert.equal(submissions.length, 0, 'Loading a cached package must not submit a job');
  get('source').value = 'edited program';
  get('load-package').listeners.click();
  assert.equal(get('source').value, packages[0].source, 'The Load package button retains the same behavior');
}
get('available-package').value = packages[1].id;
get('available-package').listeners.change();
assert.equal(get('load-package').disabled, !localExecution, 'Local packages build from source; hosted packages require verification');
if (!localExecution) {
  const before = [get('source').value, get('package-url').value, get('revision').value];
  get('available-package').listeners.dblclick();
  assert.deepEqual([get('source').value, get('package-url').value, get('revision').value], before,
    'Double-click must respect disabled loading');
  assert.equal(submissions.length, 0);
}
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
assert.equal(get('program-output-only').checked, true);
assert.equal(get('output').value, '<script>42</script>');
assert.equal(get('build-details').disabled, false);
get('build-details').listeners.click();
assert.match(get('output').value, /^PASS\nPackage: test\/package/);
assert.equal(get('build-details')['aria-expanded'], 'true');
get('build-details').listeners.click();
assert.equal(get('output').value, '<script>42</script>');
get('program-output-only').checked = false;
get('program-output-only').listeners.change();
assert.equal(preferences.get('fortran-playground-fpm-program-output-only'), 'false');
assert.match(get('output').value, /^PASS\nPackage:/);
assert.equal(get('build-details').disabled, true);
get('program-output-only').checked = true;
get('program-output-only').listeners.change();
assert.equal(preferences.get('fortran-playground-fpm-program-output-only'), 'true');
assert.equal(get('output').value, '<script>42</script>');
assert.equal(submissions.length, 1, 'Changing the output view must not submit a job');
const execution = (stdout = '', stderr = '') => ({ok: true, stages: [
  {name: 'Run', ok: true, seconds: .1, command: ['fpm', 'run'], stdout, stderr, exit_code: 0}]});
assert.equal(programOutputText(execution('  42\n', 'Project is up to date\r\nwarning\n')), '  42\nwarning\n');
assert.equal(programOutputText(execution('Project is up to date\n', 'Project is up to date\nProject is up to date\n')),
  'Project is up to date\nProject is up to date\n', 'Preserve program text matching FPM status');
assert.equal(programOutputText(execution('', 'Project is up to date\n')), 'Program completed successfully with no output.');
assert.equal(programOutputText(execution('  \n')), '  \n');
assert.equal(programOutputText({ok: true, stages: []}), 'Build completed successfully.');
for (const name of ['Build', 'Run']) {
  const failed = execution('partial output\n', 'compiler or runtime error');
  failed.ok = false; failed.stages[0].ok = false; failed.stages[0].name = name;
  failed.stages[0].exit_code = 1;
  assert.equal(programOutputText(failed), resultText(failed));
}

get('workflow').value = 'package';
get('workflow').listeners.change();
assert.equal(get('source-pane').hidden, true);
assert.equal(get('target-controls').hidden, false);
assert.equal(get('test-action').disabled, false);
assert.equal(get('example-action').disabled, false);
get('action').value = 'example'; get('action').listeners.change();
assert.equal(get('submit').textContent, 'Run examples');
await get('submit').listeners.click();
if (legacyService) {
  assert.equal(get('submit').disabled, true);
  assert.match(get('workflow-note').textContent, /Run examples/);
} else assert.equal(submissions.at(-1).action, 'example');
get('action').value = 'run'; get('action').listeners.change();
if (!legacyService) {
  get('target').value = 'old-target';
  get('compiler').value = localExecution ? 'gfortran' : 'ifx'; get('compiler').listeners.change();
  assert.equal(get('target').value, '');
  assert.match(get('connection').textContent, localExecution ? /GNU Fortran 16/ : /Intel ifx/);
}
result = {ok: false, needs_target: true, error: 'Choose an application target', targets: ['alpha', 'beta'], stages: []};
await get('submit').listeners.click();
assert.equal(get('status').textContent, 'Choose a target');
assert.match(get('output').value, /Choose an application target/);
assert.equal(get('build-details').disabled, true);
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
get('program-output-only').listeners.change();
assert.match(get('output').value, /slots are busy/, 'A view change must not restore a stale result after an error');
fail = false; transportFailure = true;
await get('submit').listeners.click();
assert.equal(cancellations, 1, 'A lost connection cancels the known job');
assert.equal(get('submit').disabled, false);
assert.match(resultText({ok: false, error: 'Timed out', stages: []}), /Timed out/);
assert.match(resultText({ok: false, stages: [{name: 'Build', ok: true, seconds: 1, command: ['fpm', 'build'], exit_code: 0}]}), /^BUILD PASS — nothing run/);
assert.match(resultText({ok: false, nothing_run: true, stages: []}), /^BUILD PASS — nothing run/);

transportFailure = false;
assert.equal(translatedFetches, 0, 'General collection does not fetch translated R metadata');
get('package-gams').value = 'D'; get('package-gams').listeners.change();
get('package-gams-subclass').value = 'D2'; get('package-gams-subclass').listeners.change();
get('package-collection').value = 'translated-r';
await get('package-collection').listeners.change();
assert.equal(get('package-gams').value, '', 'Changing collections clears the class filter');
assert.equal(get('package-gams-subclass').value, '', 'Changing collections clears the subclass filter');
assert.equal(get('package-gams-subclass-controls').hidden, true);
assert.equal(get('package-gams-controls').hidden, true, 'Unclassified translated R packages hide the GAMS filter');
assert.equal(translatedFetches, 1);
assert.equal(get('subdirectory').hidden, false);
assert.equal(get('subdirectory-label').hidden, false);
get('package-search').value = 'dvode'; get('package-search').listeners.input();
await get('package-search-results').options.find(item => item.textContent === 'Search Selected Fortran packages').listeners.click();
assert.equal(get('available-package').value, 'dvode');
get('package-collection').value = 'translated-r'; await get('package-collection').listeners.change();
assert.match(get('package-count').textContent, /596/);
assert.equal(get('package-topics').hidden, true, 'Translated packages do not inherit repository-wide topic labels');
get('package-search').value = 'Metrics'; get('package-search').listeners.input();
assert.ok(get('available-package').options.some(option => option.value === 'Metrics'));
assert.equal(get('package-sort').disabled, true, 'Translated packages share a repository and use name sorting');
get('available-package').value = 'Metrics'; get('available-package').listeners.change();
assert.equal(get('load-package').disabled, false, 'Cold builds do not require a precompiled image');
get('load-package').listeners.click();
assert.equal(get('workflow').value, 'package');
assert.equal(get('subdirectory').value, 'Metrics');
assert.match(get('package-source').href, /\/Metrics$/);
await get('submit').listeners.click();
if (legacyService) {
  assert.equal(get('submit').disabled, true);
  assert.match(get('workflow-note').textContent, /backend deployment/);
  assert.notEqual(submissions.at(-1).subdirectory, 'Metrics', 'An old API must not receive unsupported requests');
} else {
  assert.equal(submissions.at(-1).subdirectory, 'Metrics');
  assert.equal(submissions.at(-1).workflow, 'package');
}
get('workflow').value = 'consumer'; get('workflow').listeners.change();
get('source').value = 'program main\nprint *, 42\nend program';
await get('download-project').listeners.click();
const translatedZip = Buffer.from(await downloads.at(-1).blob.arrayBuffer()).toString('utf8');
assert.ok(translatedZip.includes('"subdirectory": "Metrics"'));
get('package-collection').value = 'general';
await get('package-collection').listeners.change();
assert.equal(get('subdirectory').hidden, true);
assert.equal(get('package-gams-controls').hidden, false);
assert.equal(get('subdirectory-label').hidden, true);
assert.equal(get('subdirectory').value, '', 'Changing to general clears the hidden translated directory');
get('example').value = examples[0].name; get('load-example').listeners.click();
assert.equal(get('subdirectory').value, '', 'Loading a general example clears the translated directory');
assert.equal(get('submit').disabled, false, 'General examples stay usable with an older service');
assert.equal(translatedFetches, 1);

if (allEnabled) {
  // Full discovery catalog reuses selected pins, but new entries build on demand.
  const beforeAll = submissions.length;
  get('package-collection').value = 'all';
  await get('package-collection').listeners.change();
  assert.equal(allFetches, 1);
  assert.equal(translatedFetches, 1);
  assert.equal(submissions.length, beforeAll);
  assert.equal(get('subdirectory').hidden, true);
  const cold = allPackages.find(p => p.fpm_status === 'available' && !p.source);
  get('package-search').value = cold.repository.split('/')[0];
  get('package-search').listeners.input();
  assert.ok(get('available-package').options.some(p => p.value === cold.id), 'Owner search includes full catalog entries');
  get('available-package').value = cold.id; get('available-package').listeners.change();
  assert.equal(get('load-package').disabled, false, 'No precompiled image is required for discovery entries');
  get('load-package').listeners.click();
  assert.equal(get('package-url').value, `https://github.com/${cold.repository}`);
  assert.equal(get('revision').value, '');
  assert.equal(get('workflow').value, 'package');
  assert.equal(get('package-source').href, `https://github.com/${cold.repository}`);
  assert.equal(get('action').value, 'build', 'Discovery entries start with Build, not an assumed application');
  get('action').value = 'build'; get('action').listeners.change();
  await get('submit').listeners.click();
  assert.equal(submissions.at(-1).url, `https://github.com/${cold.repository}`);
  assert.equal(submissions.at(-1).revision, '');
  assert.equal(submissions.at(-1).workflow, 'package');
  assert.equal(submissions.at(-1).action, 'build');
  assert.ok(!Object.hasOwn(submissions.at(-1), 'subdirectory'));
  get('workflow').value = 'consumer'; get('workflow').listeners.change();
  await get('download-project').listeners.click();
  const discoveryZip = Buffer.from(await downloads.at(-1).blob.arrayBuffer()).toString('utf8');
  assert.ok(!discoveryZip.includes('"package": {'), 'Unpinned discovery metadata is not an audited build recipe');
  const missing = allPackages.find(p => p.fpm_status === 'missing');
  get('package-search').value = ''; get('package-search').listeners.input();
  get('available-package').value = missing.id; get('available-package').listeners.change();
  assert.equal(get('load-package').disabled, true);
  assert.match(get('package-note').options.at(-1).textContent, /No root fpm.toml/);
  assert.equal(get('package-source').href, `https://github.com/${missing.repository}`);
  get('available-package').value = packages[0].id; get('available-package').listeners.change();
  get('load-package').listeners.click();
  assert.equal(get('revision').value, packages[0].revision, 'Selected pins survive in All');
  assert.equal(get('source').value, packages[0].source);
  assert.equal(get('preprocess').checked, false, 'Retained discovery audits must not bypass selected caches');
  get('package-collection').value = 'general'; await get('package-collection').listeners.change();
  get('package-collection').value = 'all'; await get('package-collection').listeners.change();
  assert.equal(allFetches, 1, 'Full catalog is cached for this page session');

} else {
  assert.ok(!get('package-collection').options.some(o => o.value === 'all'));
  assert.equal(allFetches, 0);
  get('package-collection').value = 'all'; await get('package-collection').listeners.change();
  assert.equal(get('package-collection').value, 'general');
  assert.equal(allFetches, 0, 'Disabled collection cannot be fetched through collection-change events');
  get('package-search').value = 'no-such-package-12345'; get('package-search').listeners.input();
  assert.ok(get('package-search-results').options.some(o => o.textContent === 'Search Translated R packages'));
  assert.ok(!get('package-search-results').options.some(o => o.textContent === 'Search All Fortran packages'));
}

// A successful build can reveal examples without running anything automatically.
get('workflow').value = 'package'; get('workflow').listeners.change();
get('action').value = 'build'; get('action').listeners.change();
result = {ok: true, build_ok: true, targets: [], target_groups: {app: [], example: ['demo_a', 'demo_b'], test: []}, stages: []};
await get('submit').listeners.click();
assert.equal(get('target-discovery').hidden, false);
assert.equal(get('use-app-targets').hidden, true);
assert.equal(get('use-example-targets').hidden, legacyService);
const beforeChoosing = submissions.length;
if (!legacyService) {
  get('use-example-targets').listeners.click();
  assert.equal(get('action').value, 'example');
  assert.equal(get('target-picker').hidden, false);
  assert.deepEqual(get('targets').options.map(o => o.value), ['demo_a', 'demo_b']);
  get('target-picker').value = 'demo_b'; get('target-picker').listeners.change();
  assert.equal(get('target').value, 'demo_b');
  assert.equal(submissions.length, beforeChoosing);
}
get('preprocess').checked = true; get('preprocess').listeners.change();
assert.equal(get('target-discovery').hidden, true, 'Changing build options invalidates target suggestions');
get('action').value = 'build'; get('action').listeners.change();
await get('submit').listeners.click();
if (legacyService) {
  assert.equal(submissions.length, beforeChoosing, 'Old services must not receive unsupported preprocessing requests');
  assert.match(get('workflow-note').textContent, /backend deployment/);
} else assert.equal(submissions.at(-1).preprocess, true);
await get('download-project').listeners.click();
const preprocessedZip = Buffer.from(await downloads.at(-1).blob.arrayBuffer()).toString('utf8');
assert.ok(preprocessedZip.includes('"preprocess": true'));
globalThis.setTimeout = originalTimeout;
console.log('FPM UI: workflows, targets, stdin, results, no automatic submissions, and error recovery passed.');
