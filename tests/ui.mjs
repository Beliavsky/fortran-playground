import assert from 'node:assert/strict';
import {playgroundConfig} from '../site/config.mjs';
const elements = new Map();
globalThis.document = {
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, {value: '', textContent: '', disabled: false,
      options: [], listeners: {}, addEventListener(name, fn) {this.listeners[name] = fn;}, focus() {}, click() {},
      setSelectionRange(from, to) {this.selection = [from, to];}});
    return elements.get(id);
  },
  createElement() {return {click() {}};},
};
const get = id => document.getElementById(id);
get('compiler').value = 'gfortran';
get('compiler').options = ['gfortran','ifx','flang','lfortran'].map(value => ({value}));
get('preset').value = 'default';
get('standard').value = 'default';
get('standard').options = ['default', '1995', '2003', '2008', '2018', '2023'].map(value => ({value}));
get('preset').options = ['default','debug','optimized','strict'].map(value => ({value}));
get('example').value = 'sum';
globalThis.confirm = () => true;
let submissions = 0, payload, state = 'done', sessionFails = false, cancelled = 0, legacy = false, expired = false, buildOK = true, buildError = '';
globalThis.fetch = async (url, options = {}) => {
  let result;
  if (url === './service.json') result = {url: 'https://test.modal.run'};
  else if (url.endsWith('/api/session')) {
    if (sessionFails) throw new Error('Offline');
    result = {token: 'session', commit: 'abcd1234', timeout: 30, compilers: ['gfortran'],
      features: legacy ? {} : {compile_only: true, run_again: true},
      ...(legacy ? {} : {compiler_versions: {gfortran: 'GNU Fortran (GCC) 15.2.0', ifx: 'Intel Fortran 2026.0'}}),
      compiler_options: {gfortran: {presets: {default: [], debug: ['-g']}, extras: {warnings: ['-Wall']},
        ...(legacy ? {} : {standards: {'2008': ['-std=f2008'], '2018': ['-std=f2018']},
          standard_note: 'GNU rejects extensions beyond the selected standard.'})}}};
  } else if (url.endsWith('/api/jobs')) {
    submissions++; payload = JSON.parse(options.body); result = {id: 'job'};
  } else if (url.endsWith('/cancel')) {cancelled++; state = 'done'; result = {};}
  else result = {state, result: {ok: buildOK, compiler: 'gfortran', seconds: 0.3,
    ...(legacy ? {} : {compiler_version: 'GNU Fortran (GCC) 15.2.0'}),
    ...(payload?.mode === 'fortran-run' ? {reused_executable: true} : {
      build: {ok: buildOK, stdout: buildOK ? 'Build: PASS' : 'Build: FAIL', stderr: buildError, seconds: 0.2},
      ...(buildOK ? {artifact: {id: 'private-id', expires_at: Date.now()/1000 + (expired ? -1 : 300)}} : {})}),
    ...(payload?.mode === 'fortran-compile' ? {} : {execution: {stdout: '385\n', stderr: '', seconds: 0.1}})}};
  return {ok: true, json: async () => result};
};
await import('../site/app.mjs');
assert.equal(submissions, 0); // Connecting/loading never executes a program.
assert.equal(get('run').disabled, false);
assert.equal(get('compile').disabled, false);
assert.equal(get('rerun').disabled, true);
assert.equal(get('fortran-lines').textContent, '9 lines');
assert.equal(get('first-error').hidden, true);
assert.equal(get('compiler').options[1].disabled, true);
assert.match(get('compiler-version').textContent, /GNU Fortran \(GCC\) 15.2.0/);
assert.equal(get('compiler').options[0].title, 'GNU Fortran (GCC) 15.2.0');
assert.equal(get('preset').options[2].disabled, true);
assert.equal(get('fast-math').disabled, true);
assert.equal(get('standard').disabled, false);
assert.equal(get('standard').options[3].disabled, false);
assert.equal(get('standard').options[5].disabled, true);
get('standard').value = '2008'; get('standard').onchange();
assert.match(get('options-note').textContent, /-std=f2008/);
assert.match(get('standard-note').textContent, /GNU rejects extensions/);
get('preset').value = 'debug'; get('preset').onchange();
await get('run').onclick();
assert.equal(payload.source, '');
assert.equal(payload.mode, 'fortran-edit');
assert.match(payload.fortran_source, /program main/);
assert.equal(payload.compiler_options.preset, 'debug');
assert.equal(payload.compiler_options.standard, '2008');
assert.equal(get('output').textContent, '385\n');
assert.equal(get('build-time').textContent, '0.20 s');
assert.equal(get('run-time').textContent, '0.10 s');
assert.match(get('status').textContent, /0.30 s total/);
assert.equal(get('result-compiler-version').hidden, false);
assert.match(get('result-compiler-version').textContent, /GNU Fortran \(GCC\) 15.2.0/);
const compiledVersion = get('result-compiler-version').textContent;
get('compiler').value = 'ifx'; get('compiler').onchange();
assert.equal(get('standard').disabled, true);
assert.equal(get('standard').value, 'default');
assert.match(get('compiler-version').textContent, /Intel Fortran 2026.0/);
assert.equal(get('result-compiler-version').textContent, compiledVersion);
get('compiler').value = 'gfortran'; get('compiler').onchange();
await get('compile').onclick(); // Compiler changes invalidated the retained build.
assert.equal(payload.retain_executable, true);
assert.equal(get('rerun').disabled, false);
await get('rerun').onclick();
assert.equal(payload.mode, 'fortran-run');
assert.equal(payload.artifact_id, 'private-id');
assert.equal(payload.fortran_source, undefined);
assert.match(get('diagnostics').textContent, /Compilation skipped/);
await get('compile').onclick();
assert.equal(payload.mode, 'fortran-compile');
assert.equal(get('run-time').textContent, '');
assert.match(get('output').textContent, /Not run/);
assert.equal(get('rerun').disabled, false);
for (const id of ['compiler', 'standard', 'preset', 'warnings', 'fast-math']) {
  get(id).onchange();
  assert.equal(get('rerun').disabled, true);
  await get('compile').onclick();
}
const beforeClear = submissions;
get('clear').onclick();
assert.equal(get('rerun').disabled, true);
assert.equal(get('fortran').value, '');
assert.equal(get('fortran-lines').textContent, '0 lines');
assert.equal(get('run').disabled, true);
get('file').files = [{name: 'custom.f90', size: 30, text: async () => 'program custom\nend program\n'}];
await get('file').onchange();
assert.equal(get('fortran-lines').textContent, '2 lines');
assert.match(get('file-status').textContent, /loaded locally/);
assert.equal(submissions, beforeClear);
get('file').files = [{name: 'big.f90', size: 100001}];
await get('file').onchange();
assert.match(get('file-status').textContent, /exceeds/);
assert.match(get('fortran').value, /program custom/);
get('fortran').value = 'x'.repeat(100001); get('fortran').listeners.input();
await get('run').onclick();
assert.equal(submissions, beforeClear);
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
await get('compile').onclick();
assert.equal(get('rerun').disabled, false);
buildOK = false;
buildError = 'input_p.f90:2:5:\nError: Expected comma\n';
await get('compile').onclick();
assert.equal(get('rerun').disabled, true);
assert.match(get('diagnostics').textContent, /Build: FAIL/);
assert.equal(get('first-error').disabled, false);
assert.equal(get('first-error').hidden, false);
assert.equal(get('error-note').hidden, false);
assert.match(get('error-note').textContent, /line 2: Error: Expected comma/);
get('first-error').onclick();
assert.equal(get('fortran').value.slice(...get('fortran').selection), 'end program');
get('fortran').listeners.input();
assert.equal(get('first-error').disabled, true);
assert.equal(get('first-error').hidden, true);
assert.equal(get('error-note').hidden, true);
assert.equal(get('error-note').textContent, '');
await get('compile').onclick();
assert.equal(get('first-error').disabled, false);
get('preset').onchange();
assert.equal(get('first-error').disabled, true);
buildOK = true;
buildError = '';
expired = true;
// Feature-off leaves compile/error navigation intact and never offers an edit.
playgroundConfig.enableQuickFixes = false;
get('fortran').value = 'program main\nprint "(i0)" 7\nend program main\n';
get('fortran').listeners.input();
buildOK = false;
buildError = 'input_p.f90:2:14:\nError: Expected comma in PRINT statement at (1)\n';
await get('compile').onclick();
assert.equal(get('first-error').hidden, false);
assert.equal(get('fix-error').hidden, true);
assert.equal(get('fix-note').hidden, true);
const unchanged = get('fortran').value, beforeFix = submissions;
get('fix-error').onclick();
assert.equal(get('fortran').value, unchanged);
assert.equal(submissions, beforeFix);
playgroundConfig.enableQuickFixes = true;
buildOK = true; buildError = '';
await get('compile').onclick();
assert.equal(get('rerun').disabled, true);
const beforeExpiredRun = submissions;
await get('rerun').onclick();
assert.equal(submissions, beforeExpiredRun);
legacy = true;
await get('connect').onclick();
assert.equal(get('run').disabled, false);
assert.equal(get('compile').disabled, true);
assert.equal(get('rerun').disabled, true);
assert.match(get('build-note').textContent, /updated execution service/);
assert.equal(get('standard').disabled, true);
assert.match(get('compiler-version').textContent, /unavailable/);
await get('run').onclick();
assert.match(get('result-compiler-version').textContent, /unavailable/);
console.log('Fortran-only UI tests passed (no hosted jobs submitted).');
