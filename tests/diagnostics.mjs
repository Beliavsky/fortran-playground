import assert from 'node:assert/strict';
import {mkdtempSync, writeFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {parseCompilerErrors} from '../site/diagnostics.mjs';
import {createEditor} from '../site/editors.mjs';

const source = 'program main\ninteger :: n = 3\nprint "(i0)" n\nend program\n';
const gnu = 'input_p.f90:3:13:\n\n  3 | print "(i0)" n\n    |             1\nError: Expected comma in PRINT statement at (1)\n';
assert.deepEqual(parseCompilerErrors(gnu, source), [{line: 3, column: 13, message: 'Error: Expected comma in PRINT statement at (1)'}]);
assert.equal(parseCompilerErrors('/opt/p2f/runtime/python.f90:3:13:\nError: Wrong helper\n', source).length, 0);
assert.equal(parseCompilerErrors('input_p.f90:3:13:\nWarning: Unused variable\n', source).length, 0);
assert.equal(parseCompilerErrors('input_p.f90:999:13:\nError: Out of range\n', source).length, 0);
assert.equal(parseCompilerErrors('Error: No source location\n', source).length, 0);
assert.equal(parseCompilerErrors('input_p.f90:3:1:\n  3 | print *, "Error: not a diagnostic"\nWarning: Unused\n', source).length, 0);
assert.equal(parseCompilerErrors('C:\\work\\input_p.f90(3): error #5082: Syntax error\r\n', source)[0].line, 3);
assert.equal(parseCompilerErrors('./input_p.f90:3:13: error: expected comma\n', source)[0].column, 13);
assert.equal(parseCompilerErrors('\x1b[31msyntax error: expected comma\x1b[0m\n --> /work/input_p.f90:3:13\n', source)[0].line, 3);
const arrows = 'warning: unused\n --> input_p.f90:2:1\n  2 | integer :: n\nsyntax error: expected comma\n --> input_p.f90:3:13\n';
assert.deepEqual(parseCompilerErrors(arrows, source).map(item => item.line), [3]);
const multi = gnu + 'python.f90:2:1:\nError: helper\ninput_p.f90:4:1:\nError: Second source error\n';
assert.deepEqual(parseCompilerErrors(multi, source).map(item => item.line), [3, 4]);

// Test editor decoration, navigation, cleanup and delayed enhancement without a browser.
globalThis.document = {createElement() { return {setAttribute(key, value) {this[key] = value;}}; }};
const textarea = {value: source, labels: [], focus() {this.focused = true;},
  addEventListener(name, fn) {this[name] = fn;}, setSelectionRange(from, to) {this.selection = [from, to];}};
const editor = createEditor(textarea, {});
editor.setDiagnostics(parseCompilerErrors(gnu, source));
editor.goToDiagnostic();
assert.equal(textarea.value.slice(...textarea.selection), 'print "(i0)" n');
const lines = new Map(), gutters = new Map(), marks = [];
let options;
const cm = {
  getValue: () => textarea.value, getLine: index => textarea.value.split('\n')[index],
  getInputField: () => ({setAttribute() {}}), on(name, fn) {this[name] = fn;},
  addLineClass(index, where, cls) {lines.set(index, cls); return index;},
  removeLineClass(index) {lines.delete(index);},
  setGutterMarker(index, gutter, marker) {if (marker) gutters.set(index, marker); else gutters.delete(index);},
  markText(from, to, opts) {const mark = {from, to, opts, clear() {this.cleared = true;}}; marks.push(mark); return mark;},
  scrollIntoView(pos) {this.scrolled = pos;}, setCursor(pos) {this.cursor = pos;}, focus() {this.focused = true;},
};
editor.enhance({fromTextArea(_textarea, settings) {options = settings; return cm;}}, 'text/x-fortran', 'Fortran');
assert.ok(options.gutters.includes('p2f-errors'));
assert.equal(lines.get(2), 'p2f-error-line');
assert.match(gutters.get(2).title, /Expected comma/);
assert.ok(marks.some(mark => mark.from.ch === 12 && mark.opts.className === 'p2f-error-column'));
gutters.get(2).onclick();
assert.deepEqual(cm.cursor, {line: 2, ch: 12});
cm.change();
assert.equal(lines.size, 0);
assert.equal(gutters.size, 0);
assert.ok(marks.every(mark => mark.cleared));
editor.setDiagnostics(parseCompilerErrors(gnu, source));
editor.setDiagnostics([]);
assert.equal(lines.size, 0);
assert.equal(gutters.size, 0);

// Compare against a real GNU diagnostic when the compiler is installed.
if (spawnSync('gfortran', ['--version']).status === 0) {
  const directory = mkdtempSync(join(tmpdir(), 'fortran-diagnostic-'));
  try {
    writeFileSync(join(directory, 'input_p.f90'), source);
    const result = spawnSync('gfortran', ['-fsyntax-only', 'input_p.f90'], {cwd: directory, encoding: 'utf8'});
    assert.notEqual(result.status, 0);
    assert.equal(parseCompilerErrors(result.stdout + result.stderr, source)[0].line, 3);
  } finally {rmSync(directory, {recursive: true, force: true});}
}
console.log('Compiler diagnostic parsing and editor markers passed.');
