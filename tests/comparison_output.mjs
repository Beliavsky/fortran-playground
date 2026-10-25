import assert from 'node:assert/strict';
import {comparisonOutput, comparisonReport, loadAllOutputs, saveAllOutputs} from '../site/comparison_output.mjs';

const row = {compiler: 'gfortran', status: 'PASS', version: 'Captured GNU version',
  options: {preset: 'default', additional: ['-O2']}, flags: ['-O2'],
  times: {total: 2, compile: 0.5, run: 0.1, other: 1.4},
  result: {ok: true, compiler_version: 'Actual GNU version',
    build: {ok: true, stdout: '  build\n', stderr: 'warning\n'},
    execution: {stdout: '  one\n\n two  \n', stderr: '  stderr\n'}}};
let view = comparisonOutput(row, 'fortran-edit');
assert.equal(view.version, 'Actual GNU version');
assert.equal(view.stdout, row.result.execution.stdout);
assert.equal(view.stderr, row.result.execution.stderr);
assert.equal(view.buildError, 'warning\n');
assert.equal(view.failed, false);
const failed = {...row, status: 'FAIL', result: {build: {ok: false, stderr: 'bad syntax'}}};
view = comparisonOutput(failed, 'fortran-edit');
assert.equal(view.stdout, 'Not run because compilation failed.');
assert.equal(view.failed, true);
assert.equal(view.version, row.version);
assert.equal(comparisonOutput({...row, result: {execution: {stdout: '', stderr: ''}}}, 'fortran-edit').stdout, '(No output)');
assert.equal(comparisonOutput({...row, result: {execution: {stdout: '', stderr: 'error'}}}, 'fortran-edit').stdout, '(No standard output)');
assert.equal(comparisonOutput({...row, result: {build: {ok: true}}}, 'fortran-compile').stdout, 'Not run (compile-only comparison).');
assert.equal(comparisonOutput({...row, status: 'SKIP', result: null}, 'fortran-edit').stdout, 'Not submitted.');
assert.equal(comparisonOutput({...row, status: 'RUNNING', result: null}, 'fortran-edit').stdout, 'Waiting for result.');
const interpreter = {...row, compiler: 'ofort', result: {interpreter: true, execution: {stdout: '42\n'}}};
assert.match(comparisonOutput(interpreter, 'fortran-edit').build, /No separate compilation/);

const report = comparisonReport([row, failed, interpreter], {mode: 'fortran-edit', ownerKey: 'never-copy-this'}, true);
assert.match(report, /Source or settings have changed/);
assert.match(report, /Settings: .*"additional":\["-O2"\]/);
assert.match(report, /Flags: -O2/);
assert.match(report, /total: 2.000  compile: 0.500  run: 0.100  other: 1.400/);
assert.ok(report.includes('--- Program stdout ---\n' + row.result.execution.stdout + '\n--- End Program stdout ---'));
assert.ok(report.includes('--- Program stderr ---\n' + row.result.execution.stderr + '\n--- End Program stderr ---'));
assert.match(report, /bad syntax/);
assert.match(report, /=== ofort: PASS ===/);
assert.ok(!report.includes('never-copy-this'));
assert.ok(report.indexOf('=== gfortran: PASS') < report.indexOf('=== ofort: PASS'));

const storage = {value: null, getItem() {return this.value;}, setItem(key, value) {this.value = value;}};
assert.equal(loadAllOutputs(storage), false);
saveAllOutputs(true, storage); assert.equal(loadAllOutputs(storage), true);
saveAllOutputs(false, storage); assert.equal(loadAllOutputs(storage), false);
const blocked = {getItem() {throw new Error('Denied');}, setItem() {throw new Error('Denied');}};
assert.equal(loadAllOutputs(blocked), false);
assert.doesNotThrow(() => saveAllOutputs(true, blocked));
console.log('All-output views, exact streams, reports, statuses, and saved preferences passed.');
