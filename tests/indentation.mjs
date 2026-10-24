import assert from 'node:assert/strict';
import {indentationForLine, loadIndentation, saveIndentation} from '../site/indentation.mjs';
import {createEditor} from '../site/editors.mjs';

const hint = (source, width = 3) => {
  const lines = source.split('\n'); return indentationForLine(lines, lines.length - 1, width);
};
for (const width of [2, 3, 4]) {
  assert.equal(hint('program demo', width).next, width);
  assert.equal(hint('module demo\ncontains\nsubroutine work()', width).next, width);
  assert.equal(hint('do i = 1, 10', width).next, width);
  assert.equal(hint('outer: do concurrent (i = 1:10)', width).next, width);
  assert.equal(hint('if (x > 0) then', width).next, width);
  assert.deepEqual(hint('if (x > 0) then\n      else', width), {current: 0, next: width});
  assert.deepEqual(hint('if (x > 0) then\n      else if (x < 0) then', width), {current: 0, next: width});
  assert.deepEqual(hint('do i=1,10\n      end do', width), {current: 0, next: 0});
  assert.deepEqual(hint('select case (i)\n       case (1)', width), {current: width, next: 2 * width});
  assert.equal(hint('   value = func(a, &', width).next, 3 + width);
  assert.equal(hint('   value = func(a, &\n          b, &', width).next, 3 + width);
  assert.equal(hint('   value = func(a, &\n          b)', width).next, 3);
  assert.equal(hint('if (a > 0 .and. &\n & b > 0) then', width).next, width);
}
for (const source of ['if (x) print *, x', '   ! do i=1,10', '   print *, "if (x) then !"', '   do 100 i=1,10', '   x=1; if (x>0) then']) {
  assert.equal(hint(source).next, source.startsWith('   ') ? 3 : 0);
}
assert.deepEqual(hint('   do i=1,10\n      if (i>1) then\n         end if'), {current: 6, next: 6});
assert.deepEqual(hint('program p\n   do i=1,10\n      end program p'), {current: null, next: 6});
assert.deepEqual(hint('program p\n   contains'), {current: 0, next: 3});
assert.equal(hint("   print *, 'ab&\n        &cd'").next, 3);
assert.equal(hint("   print *, 'ab&\n! comment\n        &cd'").next, 3);
assert.equal(hint('   x = f(a, &\n! comment\n & b)').next, 3);
assert.equal(hint('type :: item').next, 3);
assert.equal(hint('real(kind=8) function square(x)').next, 3);
assert.equal(hint('module subroutine work()').next, 3);
assert.equal(hint('subroutine work').next, 3);
assert.equal(hint('call function(x)').next, 0);
assert.equal(hint('\tdo i=1,10', 4).next, 8);
assert.deepEqual(hint('where (x>0)\n   elsewhere'), {current: 0, next: 3});
const storage = {text: null, getItem() {return this.text;}, setItem(key, value) {this.text = value;}};
assert.deepEqual(loadIndentation(storage), {width: 3, automatic: true});
saveIndentation(storage, {width: 4, automatic: false});
assert.deepEqual(loadIndentation(storage), {width: 4, automatic: false});
storage.text = '{invalid'; assert.equal(loadIndentation(storage).width, 3);
storage.text = '{"width":99}'; assert.equal(loadIndentation(storage).width, 3);
assert.equal(loadIndentation({getItem() {throw new Error('blocked');}}).width, 3);

const listeners = {};
const textarea = {value: 'do i=1,10', selectionStart: 9, selectionEnd: 9, labels: [],
  addEventListener(name, handler) {listeners[name] = handler;},
  setSelectionRange(start, end) {this.selectionStart = start; this.selectionEnd = end;},
  setRangeText(text, start, end) {this.value = this.value.slice(0, start) + text + this.value.slice(end); this.selectionStart = this.selectionEnd = start + text.length;}};
const editor = createEditor(textarea, {});
let prevented = false;
listeners.keydown({key: 'Enter', preventDefault() {prevented = true;}});
assert.equal(prevented, true); assert.equal(textarea.value, 'do i=1,10\n   ');
// Loading and pasting retain indentation.
editor.setValue('program p\n        print *, 1\nend');
assert.ok(editor.getValue().includes('        print'));
listeners.input({inputType: 'insertFromPaste'});
assert.ok(editor.getValue().includes('        print'));

let options, cursor;
const events = {};
function position(index) {const lines = textarea.value.slice(0, index).split('\n'); return {line: lines.length - 1, ch: lines.at(-1).length};}
function index(pos) {return textarea.value.split('\n').slice(0, pos.line).reduce((sum, line) => sum + line.length + 1, 0) + pos.ch;}
const cm = {getValue: () => textarea.value, getCursor: () => cursor, getLine: line => textarea.value.split('\n')[line],
  getOption: name => options[name], setOption: (name, value) => {options[name] = value;},
  getInputField: () => ({setAttribute() {}}), on: (name, handler) => {events[name] = handler;},
  somethingSelected: () => false, listSelections: () => [{}], indexFromPos: index,
  operation: fn => fn(),
  replaceRange(text, from, to) {
    const start = index(from), end = index(to), offset = index(cursor);
    textarea.value = textarea.value.slice(0, start) + text + textarea.value.slice(end);
    cursor = position(offset + text.length - (end - start)); events.change();
  },
  replaceSelection(text) {this.replaceRange(text, cursor, cursor);},
};
editor.enhance({fromTextArea(element, config) {options = config; return cm;}}, 'text/x-fortran', 'Fortran');
assert.equal(options.indentUnit, 3); assert.equal(options.tabSize, 3);
textarea.value = 'if (x) then'; cursor = position(textarea.value.length);
options.extraKeys.Enter(cm); assert.equal(textarea.value, 'if (x) then\n   ');
textarea.value = 'if (x) then\n   end if'; cursor = position(textarea.value.length);
events.inputRead(cm, {origin: '+input', text: ['f']});
assert.equal(textarea.value, 'if (x) then\nend if');
options.extraKeys.Enter(cm); assert.equal(textarea.value, 'if (x) then\nend if\n');
textarea.value = 'do i=1,10\n   enddo'; cursor = position(textarea.value.length);
events.inputRead(cm, {origin: '+input', text: ['o']});
assert.equal(textarea.value, 'do i=1,10\nenddo');
editor.setIndentation({width: 2, automatic: false});
assert.equal(options.indentUnit, 2);
textarea.value = 'do i=1,10'; cursor = position(textarea.value.length);
options.extraKeys.Enter(cm); assert.equal(textarea.value, 'do i=1,10\n');
options.extraKeys.Tab(cm); assert.equal(textarea.value, 'do i=1,10\n  ');
console.log('Fortran block indentation, continuations, preferences, and editor key bindings passed.');
