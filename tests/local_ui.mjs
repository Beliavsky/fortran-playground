import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

class Element {
  constructor() {this.children = []; this._value = ''; this.textContent = ''; this.checked = false; this.selectedOptions = [];}
  set value(value) {this._value = String(value);}
  get value() {return this._value || this.children[0]?.value || '';}
  append(child) {this.children.push(child);}
  replaceChildren(...children) {this.children = children;}
  select() {this.selected = true;}
  addEventListener(name, handler) {this[name] = handler;}
  setAttribute(name, value) {this[name] = value;}
}
const html = readFileSync(new URL('../local_site/index.html', import.meta.url), 'utf8');
const ids = new Map([...html.matchAll(/\bid="([^"]+)"/g)].map(match => [match[1], new Element()]));
const get = id => ids.get(id) || null;
assert.match(html, /id="checks-pane"[^>]*hidden/);
get('checks-pane').hidden = true;
globalThis.document = {getElementById: get, createElement: () => new Element()};
let editorOptions, editorChange;
const editor = {
  value: '', wrapper: {setAttribute() {}},
  getWrapperElement() {return this.wrapper;},
  getInputField() {return this.wrapper;},
  on(event, listener) {if (event === 'change') editorChange = listener;},
  setValue(value) {this.value = value; editorChange();},
  getValue() {return this.value;},
  getLine(line) {return this.value.split('\n')[line];},
  getDoc() {return {changeGeneration() {}};},
  posFromIndex(offset) {const lines = this.value.slice(0, offset).split('\n'); return {line: lines.length - 1, ch: lines.at(-1).length};},
  replaceRange(text) {this.setValue(text);},
  addLineClass(line) {return line;}, removeLineClass() {}, setGutterMarker() {},
  markText() {return {clear() {}};}, scrollIntoView() {},
  setCursor(cursor) {this.cursor = cursor;}, focus() {},
  save() {get('editor').value = this.value;},
  setOption(key, value) {this[key] = value;},
};
globalThis.CodeMirror = {fromTextArea(textarea, options) {
  assert.equal(textarea, get('editor')); editorOptions = options; return editor;
}};
assert.match(html, /editor-vendor\/codemirror\.js/);
assert.match(html, /editor-vendor\/fortran\.js/);
globalThis.location = new URL('http://127.0.0.1:8766/#session=test-session');
let stripped = false;
globalThis.history = {replaceState() {stripped = true;}};
const session = new Map();
globalThis.sessionStorage = {getItem: key => session.get(key), setItem: (key, value) => session.set(key, value)};
let clipboard = '', clipboardFails = false;
Object.defineProperty(globalThis, 'navigator', {value: {clipboard: {async writeText(text) {if (clipboardFails) throw new Error(); clipboard = text;}}}, configurable: true});
get('interface').value = 'single'; get('preset').value = get('standard').value = 'default';
get('compile-timeout').value = '120'; get('run-timeout').value = '30';
const compilerNames = ['gfortran', 'gfortran17', 'ifx', 'flang', 'lfortran', 'ofort'];
for (const name of compilerNames) get(name + '-options').value = '[]';
const module = 'module m\nend module\n', main = 'program p\nuse m\nend program\n';
let submissions = [], current, onPost = null, cancelled = 0, failure = '', pollCount = 0;
let toolRequest, toolFails = false;
globalThis.fetch = async (url, options) => {
  assert.ok(url.startsWith('/api/')); assert.equal(options.headers['X-Local-Token'], 'test-session');
  let result;
  if (url === '/api/session') result = {workspace: 'workspace', compilers: Object.fromEntries(compilerNames.map(name => [name, {path: name, version: name + ' test'}]))};
  else if (url === '/api/files') result = {files: ['module.f90', 'main.f90']};
  else if (url.startsWith('/api/source?')) result = {source: url.includes('module') ? module : main};
  else if (url === '/api/format' || url === '/api/check') {
    toolRequest = JSON.parse(options.body);
    assert.equal(editor.readOnly, true);
    if (toolFails) result = {ok: false, error: 'Tool not found on PATH'};
    else result = url === '/api/format' ? {ok: true, formatted_source: toolRequest.source + '! formatted\n'} :
      {ok: true, diagnostics: [{line: 1, column: 1, code: 'T001', message: 'Missing implicit none'}]};
  }
  else if (url === '/api/jobs') {
    current = JSON.parse(options.body); submissions.push(current);
    pollCount = 0;
    if (failure === 'submit') return {ok: false, json: async () => ({error: 'Source must not be empty'})};
    if (onPost) await onPost(); result = {id: 'job'};
  } else if (url.endsWith('/cancel')) {cancelled++; result = {cancelled: true};}
  else if (failure === 'poll') throw new Error('Connection lost');
  else if (failure === 'worker') result = {state: 'done', rows: [], error: 'Cannot create temporary source'};
  else if (++pollCount === 1) {
    assert.equal(editor.readOnly, true);
    result = {state: 'running', rows: [{compiler: current.compilers[0], status: 'RUNNING'}]};
  }
  else result = {state: 'done', rows: current.compilers.map(compiler => ({compiler, status: 'PASS', compiler_version: compiler + ' version',
    times: {total: 1, compile: 0.6, run: current.compile_only ? null : 0.1, other: 0.3},
    build: {ok: true, commands: [['compile', 'module.f90']], stdout: '', stderr: ''},
    ...(current.compile_only ? {} : {execution: {stdout: '42\n', stderr: ''}})}))};
  return {ok: true, json: async () => result};
};
await import('../local_site/app.mjs');
assert.equal(stripped, true); assert.equal(submissions.length, 0);
assert.equal(session.get('local-fortran-session'), 'test-session');
assert.equal(get('run').disabled, true); assert.equal(get('files').children.length, 2);
assert.equal(editorOptions.mode, 'text/x-fortran'); assert.equal(editorOptions.lineNumbers, true);
assert.equal(editorOptions.indentUnit, 3); assert.equal(get('auto-indent').checked, true);
assert.equal(get('checks-pane').hidden, true);
for (const name of ['editors.mjs', 'indentation.mjs', 'output_diff.mjs', 'output_diff_ui.mjs']) {
  assert.equal(readFileSync(new URL('../local_site/' + name, import.meta.url), 'utf8'), readFileSync(new URL('../site/' + name, import.meta.url), 'utf8'));
}
assert.equal(editor.readOnly, false);
assert.equal(get('editor').disabled, false);
// Typing directly into the initially empty editor creates a source without New program.
editor.setValue('program typed\nend program typed\n');
assert.equal(get('sources').children.length, 1);
assert.equal(get('source-title').textContent, 'main.f90');
assert.equal(get('run').disabled, false);
await get('run').onclick();
assert.equal(current.sources[0].source, 'program typed\nend program typed\n');
get('interface').value = 'compare'; get('interface').onchange();
await get('run').onclick();
assert.equal(current.sources[0].path, 'main.f90');
get('remove').onclick();
assert.equal(get('sources').children.length, 0);
assert.equal(editor.readOnly, false);
assert.equal(get('run').disabled, true);
get('interface').value = 'single'; get('interface').onchange();
get('files').selectedOptions = get('files').children;
await get('add').onclick(); assert.equal(get('sources').children.length, 2);
assert.equal(get('editor').value, main);
assert.equal(editor.value, main); assert.equal(editor.readOnly, false);
get('up').onclick(); assert.match(get('sources').children[0].textContent, /main.f90/);
get('down').onclick(); assert.match(get('sources').children[0].textContent, /module.f90/);
editor.setValue(main + '! edited\n');
await get('run').onclick();
assert.deepEqual(current.compilers, ['gfortran']);
assert.equal(get('summary').children[0].children[1].textContent, 'PASS');
get('interface').value = 'compare'; get('interface').onchange(); get('ifx').checked = true; get('ifx').onchange();
get('stdin').value = '7 8\n'; get('optimization').value = '3';
get('gfortran-options').value = '["-Wall"]';
await get('run').onclick();
assert.deepEqual(current.compilers, ['gfortran', 'ifx']);
assert.deepEqual(current.sources.map(source => source.path), ['module.f90', 'main.f90']);
assert.ok(current.sources[1].source.endsWith('! edited\n'));
assert.equal(current.stdin, '7 8\n'); assert.equal(current.settings.optimization, 3);
assert.deepEqual(current.extras.gfortran, ['-Wall']);
assert.equal(get('summary').children.length, 2); assert.equal(get('results').children.length, 2);
await get('copy').onclick(); assert.match(clipboard, /=== gfortran: PASS/); assert.match(clipboard, /=== ifx: PASS/);
clipboardFails = true; await get('copy').onclick(); assert.equal(get('copy-text').selected, true);
await get('compile').onclick(); assert.equal(current.compile_only, true); assert.equal(current.stdin, '');
onPost = () => get('stop').onclick();
await get('run').onclick(); onPost = null;
assert.equal(cancelled, 1); assert.match(get('status').textContent, /Stopped/);
const beforeBadOption = submissions.length;
get('gfortran-options').value = 'invalid JSON'; await get('run').onclick();
assert.equal(submissions.length, beforeBadOption);
assert.equal(get('run').disabled, false);
get('gfortran-options').value = '[]';
for (const mode of ['single', 'compare']) {
  get('interface').value = mode;
  for (failure of ['submit', 'worker', 'poll']) {
    await get('run').onclick();
    for (const tr of get('summary').children) assert.equal(tr.children[1].textContent, 'ERROR');
    assert.equal(editor.readOnly, false);
    assert.equal(get('run').disabled, false);
    assert.match(get('status').textContent, /Source must not be empty|Cannot create temporary source|Connection lost/);
  }
}
for (const mode of ['single', 'compare']) {
  get('interface').value = mode;
  get('indent-width').value = '4'; get('indent-width').onchange();
  assert.equal(editor.indentUnit, 4);
  const original = editor.value;
  await get('format').onclick();
  assert.equal(toolRequest.indent, 4);
  assert.equal(editor.value, original + '! formatted\n');
  assert.match(get('status').textContent, /Ctrl\+Z/);
  await get('check').onclick();
  assert.equal(get('checks-pane').hidden, false);
  assert.equal(get('check-results').children.length, 1);
  get('check-results').children[0].onclick();
  assert.deepEqual(editor.cursor, {line: 0, ch: 0});
  editor.setValue(editor.value + '! edited again\n');
  assert.equal(get('checks-pane').hidden, true);
  toolFails = true;
  const beforeFailure = editor.value;
  await get('format').onclick();
  assert.equal(editor.value, beforeFailure);
  assert.match(get('status').textContent, /PATH/);
  await get('check').onclick();
  assert.match(get('check-status').textContent, /PATH/);
  assert.equal(editor.readOnly, false);
  toolFails = false;
}
failure = '';
for (const name of compilerNames) {
  get('interface').value = 'single'; get('compiler').value = name;
  await get('run').onclick(); assert.deepEqual(current.compilers, [name]);
}
get('interface').value = 'compare';
for (const name of compilerNames) get(name).checked = true;
await get('run').onclick(); assert.deepEqual(current.compilers, compilerNames);
assert.equal(get('summary').children.length, 6); assert.equal(get('results').children.length, 6);
assert.equal(get('diff-enabled').checked, false);
const beforeDiff = submissions.length;
get('diff-enabled').checked = true; get('diff-enabled').onchange();
assert.match(get('diff-results').textContent, /Reference: gfortran/);
assert.match(get('diff-results').textContent, /ifx: Exact match/);
get('diff-mode').value = 'numeric'; get('diff-mode').onchange();
get('diff-reference').value = 'ifx'; get('diff-reference').onchange();
assert.match(get('diff-results').textContent, /Reference: ifx/);
get('diff-rtol').value = '-1'; get('diff-rtol').oninput();
assert.match(get('diff-results').textContent, /nonnegative/);
get('diff-rtol').value = '0'; get('diff-rtol').oninput();
await get('copy').onclick(); assert.match(get('copy-text').value, /Output comparison: numeric/);
assert.equal(submissions.length, beforeDiff);
get('diff-enabled').checked = false; get('diff-enabled').onchange();
assert.equal(get('diff-results').hidden, true);
get('clear').onclick(); assert.equal(editor.value, '');
assert.equal(get('format').disabled, true);
console.log('Local editor file ordering, snapshots, comparison, copying, and cancellation passed.');
