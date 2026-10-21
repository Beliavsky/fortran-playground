import assert from 'node:assert/strict';
import {playgroundConfig} from '../site/config.mjs';
import {examples, exampleLabels} from '../site/examples.generated.mjs';
import {createShareLink, sourceFromHash, sharedCodeFromHash} from '../site/sharing.mjs';
if (process.argv.includes('--simple-default')) playgroundConfig.interfaceMode = 'simple';
const plainVisit = process.argv.includes('--plain-default');
const advancedLink = process.argv.includes('--advanced-link');
if (advancedLink) playgroundConfig.interfaceMode = 'simple';
const elements = new Map();
const startupSource = 'program shared\nprint *, "shared + café"\nend program shared\n';
const base = 'https://example.org/fortran-playground/';
globalThis.location = new URL(plainVisit ? base : advancedLink ? createShareLink(base, startupSource, 'advanced') :
  base + '#code=' + encodeURIComponent(startupSource)); // Existing links have no interface parameter.
const pageListeners = {};
globalThis.addEventListener = (name, handler) => {pageListeners[name] = handler;};
let copiedLink = '', clipboardFails = false;
Object.defineProperty(globalThis, 'navigator', {configurable: true, value: {
  clipboard: {async writeText(text) {if (clipboardFails) throw new Error('Denied'); copiedLink = text;}},
}});
globalThis.document = {
  getElementById(id) {
    if (!elements.has(id)) elements.set(id, {value: '', textContent: '', disabled: false,
      attributes: {}, setAttribute(name, value) {this.attributes[name] = value;},
      options: [], appendChild(option) {this.options.push(option);}, listeners: {}, addEventListener(name, fn) {this.listeners[name] = fn;}, focus() {}, click() {},
      select() {this.selected = true;}, setSelectionRange(from, to) {this.selection = [from, to];}});
    return elements.get(id);
  },
  createElement() {return {click() {}};},
};
const get = id => document.getElementById(id);
get('checks-pane').hidden = true; // Initial HTML state.
get('compiler').value = 'gfortran';
get('compiler').options = ['gfortran','ifx','flang','lfortran','ofort'].map(value => ({value}));
get('preset').value = 'default';
get('standard').value = 'default';
get('standard').options = ['default', '1995', '2003', '2008', '2018', '2023'].map(value => ({value}));
get('preset').options = ['default','debug','optimized','strict'].map(value => ({value}));
let allowReplace = true, confirmations = 0;
globalThis.confirm = () => {confirmations++; return allowReplace;};
let submissions = 0, payload, state = 'done', sessionFails = false, cancelled = 0, legacy = false, expired = false, buildOK = true, buildError = '';
let checkOK = true, findings = true, checkRequestFails = false;
let serviceCompilers = ['gfortran', 'ofort'];
globalThis.fetch = async (url, options = {}) => {
  let result;
  if (url === './service.json') result = {url: 'https://execute.example.org'};
  else if (url.endsWith('/api/session')) {
    assert.equal(url, 'https://execute.example.org/api/session');
    if (sessionFails) throw new Error('Offline');
    result = {token: 'session', commit: 'abcd1234', timeout: 30, compilers: serviceCompilers,
      features: legacy ? {} : {compile_only: true, run_again: true, format: true, check: true},
      ...(legacy ? {} : {compiler_versions: {gfortran: 'GNU Fortran (GCC) 15.2.0', ifx: 'Intel Fortran 2026.0'}}),
      compiler_options: {gfortran: {presets: {default: [], debug: ['-g']}, extras: {warnings: ['-Wall']},
        ...(legacy ? {} : {standards: {'2008': ['-std=f2008'], '2018': ['-std=f2018']},
          standard_note: 'GNU rejects extensions beyond the selected standard.'})},
        ofort: {presets: {default: []}, extras: {}, standards: {}, interpreter: true}}};
  } else if (url.endsWith('/api/jobs')) {
    if (checkRequestFails && JSON.parse(options.body).mode === 'check') throw new Error('Check request offline');
    submissions++; payload = JSON.parse(options.body); result = {id: 'job'};
  } else if (url.endsWith('/cancel')) {cancelled++; state = 'done'; result = {};}
  else if (payload?.mode === 'check') result = {state, result: {ok: checkOK, findings, seconds: 0.1,
    checking: {stdout: findings ? 'input.f90:2:1: C001 implicit typing' : 'All checks passed!', stderr: ''},
    error: checkOK ? null : 'Fortitude unavailable'}};
  else result = {state, result: {ok: buildOK, compiler: payload?.compiler || 'gfortran', seconds: 0.3,
    ...(payload?.compiler === 'ofort' ? {interpreter: true} : {}),
    ...(legacy ? {} : {compiler_version: 'GNU Fortran (GCC) 15.2.0'}),
    ...(payload?.mode === 'fortran-run' ? {reused_executable: true} : payload?.compiler === 'ofort' && payload?.mode === 'fortran-edit' ? {} : {
      build: {ok: buildOK, stdout: buildOK ? 'Build: PASS' : 'Build: FAIL', stderr: buildError, seconds: 0.2},
      ...(buildOK && payload?.retain_executable && payload?.compiler !== 'ofort' ? {artifact: {id: 'private-id', expires_at: Date.now()/1000 + (expired ? -1 : 300)}} : {})}),
    ...(payload?.mode === 'fortran-compile' ? {} : {execution: {stdout: '385\n', stderr: '', seconds: 0.1}})}};
  return {ok: true, json: async () => result};
};
await import('../site/app.mjs');
const expectedInitialMode = plainVisit ? playgroundConfig.interfaceMode : advancedLink ? 'advanced' : 'simple';
assert.equal(get('interface-mode').value, expectedInitialMode);
assert.equal(get('compiler-controls').hidden, expectedInitialMode === 'simple');
if (expectedInitialMode === 'simple') {
  assert.equal(get('run').textContent, 'Run');
  assert.equal(get('compilation-pane').hidden, true);
  get('advanced-options').onclick();
  assert.equal(get('interface-mode').value, 'advanced');
}
assert.equal(submissions, 0); // Connecting/loading never executes a program.
assert.equal(get('checks-pane').hidden, true);
const firstExample = Object.keys(examples)[0];
assert.equal(get('example').value, firstExample || '');
assert.deepEqual(get('example').options.map(({value, textContent}) => [value, textContent]), Object.entries(exampleLabels));
assert.equal(get('load').disabled, !firstExample);
const loadedSource = plainVisit ? examples[firstExample] || '' : startupSource;
assert.equal(get('fortran').value, loadedSource);
assert.equal(confirmations, 0); // Initial links load without a replacement prompt.
if (!plainVisit) assert.match(get('share-status').textContent, /Code loaded from a shared link/);
await get('share').onclick();
assert.equal(sourceFromHash(new URL(copiedLink).hash), loadedSource);
assert.equal(sharedCodeFromHash(new URL(copiedLink).hash).interfaceMode, 'advanced');
assert.equal(get('share-link-field').hidden, true);
clipboardFails = true;
await get('share').onclick();
assert.equal(get('share-link-field').hidden, false);
assert.equal(get('share-link').selected, true);
assert.equal(get('share-link').value, copiedLink);
clipboardFails = false;
get('interface-mode').value = 'simple'; get('interface-mode').onchange();
await get('share').onclick();
assert.equal(sharedCodeFromHash(new URL(copiedLink).hash).interfaceMode, 'simple');
get('advanced-options').onclick();
get('fortran').value = 'my unsaved changes';
get('fortran').listeners.input();
location.hash = '#code=' + encodeURIComponent('print *, 42\nend\n');
allowReplace = false;
pageListeners.hashchange();
assert.equal(get('fortran').value, 'my unsaved changes');
assert.equal(get('interface-mode').value, 'advanced');
allowReplace = true;
pageListeners.hashchange();
assert.equal(get('fortran').value, 'print *, 42\nend\n');
assert.equal(get('interface-mode').value, 'simple');
location.hash = '#code=' + encodeURIComponent(get('fortran').value) + '&interface=advanced';
allowReplace = false;
pageListeners.hashchange();
assert.equal(get('interface-mode').value, 'simple');
allowReplace = true;
pageListeners.hashchange();
assert.equal(get('interface-mode').value, 'advanced'); // Same source can request a different interface.
location.hash = '#code=%broken';
pageListeners.hashchange();
assert.equal(get('fortran').value, 'print *, 42\nend\n');
assert.match(get('share-status').textContent, /invalid URL encoding/);
assert.equal(submissions, 0); // Sharing, loading and hash changes never submit jobs.
for (const [name, source] of Object.entries(examples)) {
  get('example').value = name;
  get('load').onclick();
  assert.equal(get('fortran').value, source);
}
// The remaining service tests use fixed input, independent of the example catalog.
get('fortran').value = 'program main\nprint *, 385\nend program main\n';
get('fortran').listeners.input();
assert.equal(get('run').disabled, false);
assert.equal(get('compile').disabled, false);
assert.equal(get('format').disabled, true); // Plain-text fallback cannot guarantee Undo.
assert.equal(get('rerun').disabled, true);
assert.equal(get('fortran-lines').textContent, '3 lines');
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
const beforeCheck = get('fortran').value;
const compilationBeforeCheck = get('diagnostics').textContent;
const firstCheck = get('check').onclick();
assert.equal(get('checks-pane').hidden, false);
assert.equal(get('check').attributes['aria-expanded'], 'true');
assert.match(get('check-status').textContent, /Checking/);
await firstCheck;
assert.equal(payload.mode, 'check');
assert.equal(payload.source, beforeCheck);
assert.equal(payload.fortran_source, undefined);
assert.equal(payload.retain_executable, undefined);
assert.equal(payload.compiler_options, undefined);
assert.equal(get('fortran').value, beforeCheck);
assert.equal(get('diagnostics').textContent, compilationBeforeCheck);
assert.equal(get('rerun').disabled, false);
assert.match(get('checks').textContent, /C001/);
assert.equal(get('check-time').textContent, '0.10 s');
assert.match(get('status').textContent, /reported issues/);
const savedChecks = get('checks').textContent;
get('hide-checks').onclick();
assert.equal(get('checks-pane').hidden, true);
assert.equal(get('check').attributes['aria-expanded'], 'false');
assert.equal(get('checks').textContent, savedChecks);
findings = false;
await get('check').onclick();
assert.equal(get('checks-pane').hidden, false);
assert.match(get('status').textContent, /check passed/);
get('hide-checks').onclick();
checkOK = false;
await get('check').onclick();
assert.equal(get('checks-pane').hidden, false);
assert.match(get('checks').textContent, /unavailable/);
assert.equal(get('fortran').value, beforeCheck);
checkOK = true;
state = 'running';
const previousChecks = get('checks').textContent;
const checking = get('check').onclick();
await new Promise(resolve => setTimeout(resolve, 10));
assert.equal(get('check').disabled, true);
get('hide-checks').onclick(); // Hiding is allowed during a pending check.
get('fortran').value = 'program changed\nend program changed\n'; get('fortran').listeners.input();
state = 'done'; await checking;
assert.match(get('status').textContent, /discarded/);
assert.equal(get('checks').textContent, previousChecks);
assert.equal(get('checks-pane').hidden, true); // Completion does not override hiding.
assert.match(get('check-status').textContent, /discarded/);
checkRequestFails = true;
await get('check').onclick();
assert.equal(get('checks-pane').hidden, false);
assert.match(get('check-status').textContent, /Check request offline/);
assert.equal(get('diagnostics').textContent, compilationBeforeCheck);
checkRequestFails = false;
await get('connect').onclick();
get('fortran').value = beforeCheck; get('fortran').listeners.input();
await get('compile').onclick(); // Restore a retained build for the following tests.
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
get('compiler').value = 'ofort'; get('compiler').onchange();
assert.equal(get('compile').textContent, 'Check syntax');
assert.equal(get('run').textContent, 'Run');
assert.equal(get('standard').disabled, true);
assert.equal(get('preset').disabled, true);
assert.equal(get('warnings').disabled, true);
assert.equal(get('fast-math').disabled, true);
await get('compile').onclick();
assert.equal(payload.mode, 'fortran-compile');
assert.equal(payload.compiler, 'ofort');
assert.equal(payload.retain_executable, undefined);
assert.equal(get('build-title').textContent, 'Syntax checking');
assert.equal(get('rerun').disabled, true);
await get('run').onclick();
assert.equal(payload.mode, 'fortran-edit');
assert.equal(payload.retain_executable, undefined);
assert.equal(get('build-title').textContent, 'Interpreter diagnostics');
assert.match(get('diagnostics').textContent, /No separate syntax check/);
assert.equal(get('build-time').textContent, '');
assert.equal(get('result-compiler-version').hidden, false);
get('compiler').value = 'gfortran'; get('compiler').onchange();
assert.equal(get('compile').textContent, 'Compile');
assert.equal(get('run').textContent, 'Compile and Run');
// Simple mode resets execution options and preserves source and old results.
expired = false;
get('compiler').value = 'ofort'; get('compiler').onchange();
get('standard').value = '2018';
get('preset').value = 'optimized';
get('warnings').checked = true;
get('fast-math').checked = true;
const modeSource = get('fortran').value, modeOutput = get('output').textContent;
const modeDiagnostics = get('diagnostics').textContent;
const beforeModeChange = submissions;
get('interface-mode').value = 'simple'; get('interface-mode').onchange();
assert.equal(submissions, beforeModeChange);
assert.equal(get('compiler').value, 'gfortran');
assert.equal(get('standard').value, 'default');
assert.equal(get('preset').value, 'default');
assert.equal(get('warnings').checked, false);
assert.equal(get('fast-math').checked, false);
assert.equal(get('run').textContent, 'Run');
for (const id of ['compiler-controls', 'option-controls', 'compile', 'rerun', 'check', 'checks-pane']) {
  assert.equal(get(id).hidden, true, id);
}
assert.equal(get('fortran').value, modeSource);
assert.equal(get('output').textContent, modeOutput);
assert.equal(get('diagnostics').textContent, modeDiagnostics);
assert.equal(get('rerun').disabled, true);
await get('run').onclick();
assert.equal(payload.compiler, 'gfortran');
assert.deepEqual(payload.compiler_options, {preset: 'default', warnings: false, fast_math: false, standard: 'default'});
assert.equal(payload.retain_executable, undefined);
assert.equal(get('compilation-pane').hidden, true);
const beforeHiddenActions = submissions;
await get('compile').onclick(); await get('rerun').onclick(); await get('check').onclick();
assert.equal(submissions, beforeHiddenActions);
buildOK = false; buildError = 'A compiler error';
await get('run').onclick();
assert.equal(get('compilation-pane').hidden, false);
assert.match(get('diagnostics').textContent, /A compiler error/);
buildOK = true; buildError = '';
await get('run').onclick();
assert.equal(get('compilation-pane').hidden, true);
state = 'running';
const simpleRun = get('run').onclick();
assert.equal(get('interface-mode').disabled, true);
const runningSource = get('fortran').value;
location.hash = '#code=end&interface=advanced';
pageListeners.hashchange();
assert.equal(get('interface-mode').value, 'simple');
assert.equal(get('fortran').value, runningSource);
assert.match(get('share-status').textContent, /current operation/);
get('advanced-options').onclick();
assert.equal(get('interface-mode').value, 'simple');
await new Promise(resolve => setTimeout(resolve, 10));
state = 'done'; await simpleRun;
get('advanced-options').onclick();
get('preset').value = 'debug'; get('preset').onchange();
await get('compile').onclick();
assert.equal(get('rerun').disabled, false);
get('interface-mode').value = 'simple'; get('interface-mode').onchange();
assert.equal(get('preset').value, 'default');
assert.equal(get('rerun').disabled, true); // Resetting actual build options invalidates reuse.
serviceCompilers = ['ofort'];
await get('connect').onclick();
assert.equal(get('run').disabled, true);
assert.equal(get('compiler').value, 'gfortran');
assert.match(get('simple-compiler').textContent, /unavailable/);
const unavailableSubmissions = submissions;
await get('run').onclick();
assert.equal(submissions, unavailableSubmissions);
get('advanced-options').onclick();
assert.equal(get('compiler-controls').hidden, false);
assert.equal(get('compilation-pane').hidden, false);
assert.equal(get('compiler').value, 'ofort');
serviceCompilers = ['gfortran', 'ofort'];
get('compiler').value = 'gfortran';
await get('connect').onclick();
legacy = true;
await get('connect').onclick();
assert.equal(get('run').disabled, false);
assert.equal(get('compile').disabled, true);
assert.equal(get('check').disabled, true);
assert.equal(get('rerun').disabled, true);
assert.match(get('build-note').textContent, /updated execution service/);
assert.equal(get('standard').disabled, true);
assert.match(get('compiler-version').textContent, /unavailable/);
await get('run').onclick();
assert.match(get('result-compiler-version').textContent, /unavailable/);
console.log('Fortran-only UI tests passed (no hosted jobs submitted).');
