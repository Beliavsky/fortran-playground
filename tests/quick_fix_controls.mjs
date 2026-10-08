import assert from 'node:assert/strict';
import {createQuickFixControls} from '../site/quick_fix_controls.mjs';
import {findQuickFix} from '../site/fixes.mjs';

const original = 'program main\nprint "(i0)" 7\nend program main\n';
const diagnostic = 'input_p.f90:2:14:\nError: Expected comma in PRINT statement at (1)\n';
let source = original, calls = 0, edits = 0, applied = 0, history = [];
const config = {enableQuickFixes: true, disabledQuickFixRules: []};
const button = {}, note = {};
const editor = {
  undoableClear: true,
  getValue: () => source,
  applyEdit(start, end, replacement) {
    history.push(source); edits++;
    source = source.slice(0, start) + replacement + source.slice(end);
    controls.clear(); // Same source-change callback as the app.
  },
  focus() {},
};
const controls = createQuickFixControls({editor, button, note, config,
  detect(...args) { calls++; return findQuickFix(...args); },
  onApplied() { applied++; },
});
assert.equal(button.hidden, true);
controls.update(source, diagnostic, 'gfortran', true);
assert.equal(button.hidden, false);
assert.match(button.title, /comma/i);
assert.match(note.textContent, /does not compile or run/);
controls.setBusy(true);
button.onclick(); assert.equal(edits, 0);
controls.setBusy(false);
button.onclick();
assert.equal(source, original.replace('" 7', '", 7'));
assert.equal(edits, 1); assert.equal(applied, 1);
assert.equal(button.hidden, true); assert.equal(note.hidden, true);
button.onclick(); assert.equal(edits, 1);
source = history.pop(); assert.equal(source, original);

// Exact snapshot check even if the normal edit callback did not clear the proposal.
controls.update(source, diagnostic, 'gfortran', true);
source += '! edited\n'; button.onclick();
assert.equal(edits, 1); assert.equal(button.hidden, true);
source = original;
for (const [compiler, failed] of [['ifx', true], ['gfortran', false]]) {
  controls.update(source, diagnostic, compiler, failed);
  assert.equal(button.hidden, true);
}
config.disabledQuickFixRules = ['print-format-comma'];
controls.update(source, diagnostic, 'gfortran', true);
assert.equal(button.hidden, true);
config.disabledQuickFixRules = [];
editor.undoableClear = false;
controls.update(source, diagnostic, 'gfortran', true);
assert.equal(button.hidden, true); // Plain-text fallback cannot guarantee undo.
editor.undoableClear = true; controls.refresh();
assert.equal(button.hidden, false);

config.enableQuickFixes = false;
const before = calls;
controls.update(source, diagnostic, 'gfortran', true);
assert.equal(calls, before); // Disabled means no detection, not merely hidden UI.
assert.equal(button.hidden, true); assert.equal(note.hidden, true);
button.onclick(); assert.equal(edits, 1);
assert.equal(source, original);
config.enableQuickFixes = true;
source = 'program main\nprint *, 7\nend program wrong\n';
controls.update(source, "input_p.f90:3:1:\nError: Expected label 'main' for END PROGRAM statement at (1)\n", 'gfortran', true);
assert.equal(button.hidden, false);
button.onclick();
assert.equal(source, 'program main\nprint *, 7\nend program main\n');
assert.equal(edits, 2); assert.equal(applied, 2);
assert.equal(button.hidden, true);
console.log('Optional quick-fix controls, stale-source guards and disabling passed.');
