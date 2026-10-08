import assert from 'node:assert/strict';
const elements = new Map();
globalThis.document = {
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, {value: '', textContent: '', disabled: false,
      options: [], listeners: {}, addEventListener(name, fn) {this.listeners[name] = fn;}, focus() {}, click() {}});
    return elements.get(id);
  },
  createElement() {return {click() {}};},
};
const get = id => document.getElementById(id);
get('compiler').value = 'gfortran';
get('compiler').options = ['gfortran','ifx','flang','lfortran'].map(value => ({value}));
get('preset').value = 'default';
get('preset').options = ['default','debug','optimized','strict'].map(value => ({value}));
get('example').value = 'sum';
globalThis.confirm = () => true;
let submissions = 0, payload, state = 'done', sessionFails = false, cancelled = 0;
globalThis.fetch = async (url, options = {}) => {
  let result;
  if (url === './service.json') result = {url: 'https://test.modal.run'};
  else if (url.endsWith('/api/session')) {
    if (sessionFails) throw new Error('Offline');
    result = {token: 'session', commit: 'abcd1234', timeout: 30, compilers: ['gfortran'],
      compiler_options: {gfortran: {presets: {default: [], debug: ['-g']}, extras: {warnings: ['-Wall']}}}};
  } else if (url.endsWith('/api/jobs')) {
    submissions++; payload = JSON.parse(options.body); result = {id: 'job'};
  } else if (url.endsWith('/cancel')) {cancelled++; state = 'done'; result = {};}
  else result = {state, result: {ok: true, compiler: 'gfortran', seconds: 0.3,
    build: {stdout: 'Build: PASS', stderr: '', seconds: 0.2},
    execution: {stdout: '385\n', stderr: '', seconds: 0.1}}};
  return {ok: true, json: async () => result};
};
await import('../site/app.mjs');
assert.equal(submissions, 0); // Connecting/loading never executes a program.
assert.equal(get('run').disabled, false);
assert.equal(get('fortran-lines').textContent, '9 lines');
assert.equal(get('compiler').options[1].disabled, true);
assert.equal(get('preset').options[2].disabled, true);
assert.equal(get('fast-math').disabled, true);
get('preset').value = 'debug'; get('preset').onchange();
await get('run').onclick();
assert.equal(payload.source, '');
assert.equal(payload.mode, 'fortran-edit');
assert.match(payload.fortran_source, /program main/);
assert.equal(payload.compiler_options.preset, 'debug');
assert.equal(get('output').textContent, '385\n');
assert.equal(get('build-time').textContent, '0.20 s');
assert.equal(get('run-time').textContent, '0.10 s');
assert.match(get('status').textContent, /0.30 s total/);
get('clear').onclick();
assert.equal(get('fortran').value, '');
assert.equal(get('fortran-lines').textContent, '0 lines');
assert.equal(get('run').disabled, true);
get('file').files = [{name: 'custom.f90', size: 30, text: async () => 'program custom\nend program\n'}];
await get('file').onchange();
assert.equal(get('fortran-lines').textContent, '2 lines');
assert.match(get('file-status').textContent, /loaded locally/);
assert.equal(submissions, 1);
get('file').files = [{name: 'big.f90', size: 100001}];
await get('file').onchange();
assert.match(get('file-status').textContent, /exceeds/);
assert.match(get('fortran').value, /program custom/);
get('fortran').value = 'x'.repeat(100001); get('fortran').listeners.input();
await get('run').onclick();
assert.equal(submissions, 1);
assert.match(get('status').textContent, /100 KB/);
get('load').onclick();
state = 'running';
const running = get('run').onclick();
await new Promise(resolve => setTimeout(resolve, 10));
assert.equal(get('run').disabled, true);
get('fortran').value = 'program changed\nend program\n'; get('fortran').listeners.input();
state = 'done'; await running;
assert.match(get('status').textContent, /discarded/);
state = 'running';
const stopping = get('run').onclick();
await new Promise(resolve => setTimeout(resolve, 10));
await get('stop').onclick(); await stopping;
assert.ok(cancelled > 0);
assert.equal(get('status').textContent, 'Stopped');
sessionFails = true;
await get('connect').onclick();
assert.equal(get('run').disabled, true);
assert.equal(get('download').disabled, false);
assert.match(get('connection').textContent, /unavailable/);
sessionFails = false;
await get('connect').onclick();
assert.equal(get('run').disabled, false);
console.log('Fortran-only UI tests passed (no hosted jobs submitted).');
