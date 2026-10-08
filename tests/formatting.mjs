import assert from 'node:assert/strict';
import {applyFormatting} from '../site/formatting.mjs';
import {createEditor} from '../site/editors.mjs';
const source = 'program main\nprint*,1\nend\n';
const formatted = 'program main\n   print *, 1\nend\n';
const textarea = {value: source, labels: [], addEventListener() {}};
const history = [], generations = [];
const cm = {
  getValue: () => textarea.value,
  getInputField: () => ({setAttribute() {}}),
  on(name, fn) {this[name] = fn;},
  getDoc: () => ({changeGeneration(value) {generations.push(value);}}),
  posFromIndex: index => index,
  replaceRange(value) {history.push(textarea.value); textarea.value = value; this.change();},
};
const editor = createEditor(textarea, {});
assert.throws(() => applyFormatting(editor, source, {ok: true, formatted_source: formatted}), /enhanced/);
editor.enhance({fromTextArea: () => cm}, 'text/x-fortran', 'Fortran');
assert.equal(applyFormatting(editor, source, {ok: true, formatted_source: formatted}), true);
assert.equal(editor.getValue(), formatted);
assert.equal(history.length, 1);
assert.deepEqual(generations, [true, true]);
textarea.value = history.pop(); cm.change(); // One Undo restores the whole source.
assert.equal(editor.getValue(), source);
assert.equal(applyFormatting(editor, source, {ok: true, formatted_source: source}), false);
for (const result of [{ok: false, error: 'Cancelled'}, {ok: true}, {ok: true, formatted_source: ''}, {ok: true, formatted_source: 'x'.repeat(100001)}]) {
  assert.throws(() => applyFormatting(editor, source, result));
  assert.equal(editor.getValue(), source);
}
textarea.value = 'new source';
assert.throws(() => applyFormatting(editor, source, {ok: true, formatted_source: formatted}), /discarded/);
assert.equal(editor.getValue(), 'new source');
assert.equal(history.length, 0);
console.log('Formatting result guards and single-step Undo passed.');
