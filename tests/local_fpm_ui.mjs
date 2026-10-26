import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const html = readFileSync(new URL('../local_site/fpm/index.html', import.meta.url), 'utf8');
const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(match => match[1]));
const elements = new Map();
const element = () => ({value: '', textContent: '', hidden: false, disabled: false, checked: false, options: [], listeners: {},
  appendChild(child) {this.options.push(child);}, replaceChildren(...children) {this.options = children;},
  addEventListener(name, handler) {this.listeners[name] = handler;}, focus() {}, select() {},
  setRangeText(text, start, end) {this.value = this.value.slice(0, start) + text + this.value.slice(end);}});
globalThis.document = {getElementById(id) {
  assert.ok(ids.has(id), id);
  if (!elements.has(id)) elements.set(id, element());
  return elements.get(id);
}, createElement: element};
globalThis.location = new URL('http://127.0.0.1:8766/fpm/#session=private');
globalThis.history = {replaceState() {}};
globalThis.sessionStorage = {setItem() {}, getItem() {return '';}};
let copied = '';
Object.defineProperty(globalThis, 'navigator', {configurable: true, value: {clipboard: {async writeText(text) {copied = text;}}}});
const get = id => document.getElementById(id);
for (const [id, value] of Object.entries({project: '.', workflow: 'package', action: 'run', profile: 'debug',
  interface: 'single', 'compile-timeout': '120', 'run-timeout': '30', source: 'program main\nend program\n'})) get(id).value = value;
let posts = [], polls = 0, cancels = 0, fail = false, onPoll = null;
const stage = output => ({ok: true, seconds: 0.1, command: ['fpm', 'run'], stdout: output, stderr: ''});
let rows = [{compiler: 'gfortran', status: 'PASS', ok: true, times: {total: 0.4, compile: 0.2, run: 0.1, other: 0.1},
  execution: stage('42.0\n'), stages: [stage('42.0\n')], targets: ['main']}];
globalThis.fetch = async (url, options) => {
  assert.equal(options.headers['X-Local-Token'], 'private');
  let data;
  if (url === '/api/fpm/session') data = {workspace: 'C:/test', fpm: 'fpm', projects: ['.'], compilers: {
    gfortran: {path: 'gfortran', version: 'GNU'}, flang: {path: 'flang', version: 'Flang'}}};
  else if (url === '/api/fpm/jobs') {
    if (fail) return {ok: false, async json() {return {error: 'A local job is already active'};}};
    posts.push(JSON.parse(options.body)); polls = 0; data = {id: 'job'};
  } else if (url.endsWith('/cancel')) {cancels++; data = {cancelled: true};}
  else if (url === '/api/jobs/job') {
    if (onPoll) {const handler = onPoll; onPoll = null; await handler();}
    data = {state: polls++ ? 'done' : 'running', rows};
  } else if (url === '/api/format') data = {ok: true, formatted_source: 'program main\n   print *,42\nend program\n'};
  else if (url === '/api/check') data = {ok: true, diagnostics: []};
  else throw new Error(url);
  return {ok: true, async json() {return data;}};
};
const timeout = globalThis.setTimeout;
globalThis.setTimeout = fn => {queueMicrotask(fn); return 1;};
await import('../local_site/fpm/fpm.mjs');
assert.equal(posts.length, 0);
assert.equal(get('submit').disabled, false);
assert.equal(get('source-pane').hidden, true);
assert.equal(get('compiler-ifx').disabled, true);
assert.match(get('source-link').href, /#session=private/);
get('stdin').value = '1\n';
await get('submit').onclick();
assert.equal(posts[0].project, '.');
assert.equal(posts[0].options.stdin, '1\n');
assert.equal(get('status').textContent, 'PASS');
assert.equal(get('targets').options[0].value, 'main');

get('interface').value = 'compare'; get('interface').onchange(); get('compiler-flang').checked = true;
rows.push({compiler: 'flang', status: 'PASS', ok: true, execution: stage('42.000\n'), stages: [stage('42.000\n')]});
get('workflow').value = 'consumer'; get('workflow').onchange();
assert.equal(get('source-pane').hidden, false);
assert.equal(get('test-action').disabled, true);
await get('submit').onclick();
assert.deepEqual(posts.at(-1).compilers, ['gfortran', 'flang']);
assert.match(posts.at(-1).options.source, /program main/);
const jobs = posts.length;
get('diff-enabled').checked = true; get('diff-mode').value = 'numeric'; get('diff-enabled').onchange();
assert.match(get('diff-results').textContent, /Numeric match/);
await get('copy').onclick(); assert.match(copied, /flang: PASS/); assert.match(copied, /Output comparison/);
assert.equal(posts.length, jobs);
await get('format').onclick(); assert.match(get('source').value, /print \*,42/);
await get('check').onclick(); assert.equal(get('checks').hidden, false);

get('workflow').value = 'package'; get('workflow').onchange();
get('action').value = 'build'; get('action').onchange();
await get('submit').onclick(); assert.equal(posts.at(-1).options.stdin, '');
get('action').value = 'test'; get('action').onchange();
onPoll = () => get('stop').onclick();
rows = [{compiler: 'gfortran', status: 'STOPPED', ok: false}];
await get('submit').onclick(); assert.equal(cancels, 1); assert.equal(get('status').textContent, 'Stopped');
fail = true; await get('submit').onclick();
assert.equal(get('submit').disabled, false); assert.equal(rows[0].status, 'STOPPED');
assert.match(get('status').textContent, /already active/);
globalThis.setTimeout = timeout;
console.log('Local FPM UI: package/consumer workflows, comparison, stdin, tools, copying, cancellation, and recovery passed.');
