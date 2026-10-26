import {createEditor} from './editors.mjs';
import {loadIndentation, saveIndentation} from './indentation.mjs';
import {createOutputComparison} from './output_diff_ui.mjs';

const get = id => document.getElementById(id);
const outputComparison = createOutputComparison(get);
const compilers = ['gfortran', 'gfortran17', 'ifx', 'flang', 'lfortran', 'ofort'];
let token = new URLSearchParams(location.hash.slice(1)).get('session') || '';
try {
  if (token) sessionStorage.setItem('local-fortran-session', token);
  else token = sessionStorage.getItem('local-fortran-session') || '';
  history.replaceState(null, '', location.pathname);
} catch {} // With blocked storage, retain the fragment so reloading still works.
get('fpm-link').href = '/fpm/#session=' + encodeURIComponent(token);
let sources = [], index = -1, catalog = {}, busy = false, loading = false, stopping = false, jobId = '', rows = [], names = [], report = '';
const cards = new Map();
let indentation = loadIndentation();
const editor = createEditor(get('editor'), get('line-count'), sourceChanged);
editor.setIndentation(indentation);
if (globalThis.CodeMirror) editor.enhance(globalThis.CodeMirror, 'text/x-fortran', 'Fortran source');
get('indent-width').value = String(indentation.width);
get('auto-indent').checked = indentation.automatic;
for (const id of ['indent-width', 'auto-indent']) get(id).onchange = () => {
  indentation = {width: Number(get('indent-width').value), automatic: get('auto-indent').checked};
  editor.setIndentation(indentation); saveIndentation(undefined, indentation);
};
const status = text => {get('status').textContent = text;};
async function api(path, data, timeout = 15000) {
  const response = await fetch('/api/' + path, {cache: 'no-store', signal: AbortSignal.timeout(timeout),
    method: data === undefined ? 'GET' : 'POST', headers: {'X-Local-Token': token, ...(data === undefined ? {} : {'Content-Type': 'application/json'})},
    ...(data === undefined ? {} : {body: JSON.stringify(data)})});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || `HTTP ${response.status}`);
  return result;
}
function controls() {
  const comparison = get('interface').value === 'compare';
  get('single-compiler').hidden = comparison; get('compiler-choices').hidden = !comparison;
  const selected = comparison ? Object.keys(catalog).filter(name => get(name).checked && catalog[name].path) : [get('compiler').value].filter(Boolean);
  for (const id of ['compile', 'run']) get(id).disabled = busy || loading || !sources.length || !selected.length;
  for (const id of ['format', 'check', 'clear']) get(id).disabled = busy || loading || !editor.getValue().trim();
  get('stop').disabled = !busy || stopping;
  for (const id of ['interface', 'compiler', 'files', 'sources', 'add', 'remove', 'up', 'down', 'new', 'refresh', 'editor', 'stdin', 'stdin-file',
    'preset', 'standard', 'optimization', 'warnings', 'bounds_check', 'backtrace', 'preprocess', 'fast_math', 'compile-timeout', 'run-timeout', 'fail-fast', 'indent-width', 'auto-indent']) get(id).disabled = busy || loading;
  for (const name of compilers) {
    get(name).disabled = busy || loading || !catalog[name]?.path;
    get(name + '-options').disabled = busy || loading || !catalog[name]?.path;
  }
  get('download').disabled = index < 0; get('copy').disabled = !rows.length;
  editor.setReadOnly(busy || loading);
  return selected;
}
function sourceList() {
  get('sources').replaceChildren(...sources.map((source, i) => {
    const option = document.createElement('option'); option.value = i; option.textContent = `${i + 1}. ${source.path}`; return option;
  }));
  get('sources').value = String(index);
  get('source-title').textContent = index < 0 ? 'Fortran input' : sources[index].path;
}
function selectSource(next) {
  index = next;
  sourceList();
  editor.setValue(sources[index]?.source || '');
  controls();
}
function sourceChanged() {
  get('checks-pane').hidden = true;
  const source = get('editor').value;
  if (index >= 0) sources[index].source = source;
  else if (source) {
    sources.push({path: 'main.f90', source});
    index = sources.length - 1;
    sourceList();
  }
  controls();
}
get('clear').onclick = () => editor.setValue('', true);
async function sourceTool(action) {
  if (busy || loading || index < 0 || !editor.getValue().trim()) return;
  const selected = sources[index], source = editor.getValue();
  loading = true; controls(); status(action === 'format' ? 'Formatting with local fprettify...' : 'Checking with local Fortitude...');
  if (action === 'check') {
    editor.clearDiagnostics(); get('checks-pane').hidden = false;
    get('check-status').textContent = 'Checking...'; get('check-results').replaceChildren();
  }
  try {
    const result = await api(action, {path: selected.path, source, indent: indentation.width}, 45000);
    if (sources[index] !== selected || editor.getValue() !== source) throw new Error('Source changed; tool result discarded.');
    if (!result.ok) throw new Error(result.error || 'Local editor tool failed.');
    if (action === 'format') {
      if (typeof result.formatted_source !== 'string' || !result.formatted_source.trim()) throw new Error('No formatted source returned.');
      if (result.formatted_source !== source) editor.setValue(result.formatted_source, true);
      status('Formatted with local fprettify. Ctrl+Z to undo.');
    } else {
      const items = result.diagnostics.map(item => ({...item, message: `${item.code}: ${item.message}`}));
      editor.setDiagnostics(items);
      get('check-status').textContent = items.length ? `${items.length} finding(s) in ${selected.path}. Select a finding to visit its line.` : 'No Fortitude findings.';
      for (const item of items) {
        const button = element('button', `${selected.path}:${item.line}:${item.column} ${item.message}`, get('check-results'));
        button.className = 'diagnostic'; button.onclick = () => editor.goToDiagnostic(item);
      }
      status('Local Fortitude check finished.');
    }
  } catch (error) {
    status(error.message);
    if (action === 'check') get('check-status').textContent = error.message;
  } finally {loading = false; controls();}
}
get('format').onclick = () => sourceTool('format');
get('check').onclick = () => sourceTool('check');
get('sources').onchange = () => selectSource(Number(get('sources').value));
get('interface').onchange = controls;
for (const name of compilers) get(name).onchange = controls;
get('compiler').onchange = controls;
get('new').onclick = () => {
  let path = 'main.f90', suffix = 2;
  while (sources.some(source => source.path === path)) path = `main${suffix++}.f90`;
  sources.push({path, source: 'program main\n   implicit none\n   print *, "Hello, Fortran!"\nend program main\n'});
  selectSource(sources.length - 1);
};
get('remove').onclick = () => {if (index >= 0) sources.splice(index, 1); selectSource(Math.min(index, sources.length - 1));};
for (const [id, delta] of [['up', -1], ['down', 1]]) get(id).onclick = () => {
  const next = index + delta;
  if (index < 0 || next < 0 || next >= sources.length) return;
  [sources[index], sources[next]] = [sources[next], sources[index]]; selectSource(next);
};
async function refresh() {
  const result = await api('files');
  get('files').replaceChildren(...result.files.map(path => {const option = document.createElement('option'); option.value = option.textContent = path; return option;}));
}
get('refresh').onclick = () => refresh().catch(error => status(error.message));
get('add').onclick = async () => {
  if (busy || loading) return;
  loading = true; controls();
  try {
    for (const option of get('files').selectedOptions) {
      if (sources.some(source => source.path === option.value)) continue;
      const result = await api('source?path=' + encodeURIComponent(option.value));
      sources.push({path: option.value, source: result.source});
    }
  } catch (error) {status(error.message);}
  finally {loading = false; selectSource(sources.length - 1);}
};
get('stdin-file').onchange = async () => {
  const file = get('stdin-file').files[0];
  if (file) get('stdin').value = await file.text();
};
get('download').onclick = () => {
  if (index < 0) return;
  const url = URL.createObjectURL(new Blob([sources[index].source], {type: 'text/plain;charset=utf-8'}));
  const link = document.createElement('a'); link.href = url; link.download = sources[index].path.split('/').at(-1); link.click(); setTimeout(() => URL.revokeObjectURL(url), 0);
};
function element(tag, text, parent) {
  const node = document.createElement(tag); if (text !== undefined) node.textContent = text;
  if (parent) parent.append(node); return node;
}
function render() {
  const ordered = names.map(name => rows.find(row => row.compiler === name) || {compiler: name, status: 'QUEUED'});
  outputComparison.update(ordered);
  const body = get('summary'); body.replaceChildren();
  const reports = ['Local Fortran comparison\nTimes in seconds.'];
  for (const row of ordered) {
    const tr = element('tr', undefined, body); element('td', row.compiler, tr); element('td', row.status, tr);
    for (const key of ['total', 'compile', 'run', 'other']) element('td', Number.isFinite(row.times?.[key]) ? row.times[key].toFixed(3) : '-', tr);
    const serialized = JSON.stringify(row);
    if (cards.get(row.compiler)?.serialized !== serialized) {
      const section = element('section'); section.className = 'result';
      element('h3', `${row.compiler}: ${row.status}`, section);
      element('p', row.compiler_version || catalog[row.compiler]?.version || '', section);
      for (const note of row.notes || []) element('p', note, section);
      if (row.error) element('pre', row.error, section);
      element('h4', 'Program output', section);
      element('pre', row.execution ? row.execution.stdout || '(No standard output)' : row.build?.ok === false ? 'Not run because compilation failed.' : row.status === 'ERROR' ? 'No execution result received.' : 'Not run.', section);
      if (row.execution?.stderr) {element('h4', 'Program standard error', section); element('pre', row.execution.stderr, section);}
      const details = element('details', undefined, section); details.open = ['FAIL', 'ERROR'].includes(row.status);
      element('summary', 'Compilation log', details);
      for (const command of row.build?.commands || []) element('pre', command.map(arg => JSON.stringify(arg)).join(' '), details);
      element('pre', row.build?.stdout || '(No compilation output)', details);
      if (row.build?.stderr) element('pre', row.build.stderr, details);
      cards.set(row.compiler, {serialized, section});
    }
    reports.push(`\n=== ${row.compiler}: ${row.status} ===\n${row.compiler_version || ''}`,
      `Times: ${JSON.stringify(row.times || {})}`, `Compile flags: ${JSON.stringify(row.compile_flags || [])}`, `Link flags: ${JSON.stringify(row.link_flags || [])}`);
    if (row.error) reports.push(row.error);
    for (const note of row.notes || []) reports.push('Note: ' + note);
    for (const key of ['build', 'execution']) if (row[key]) {
      reports.push(`${key} commands: ${JSON.stringify(row[key].commands || row[key].command || [])}`);
      for (const stream of ['stdout', 'stderr']) reports.push(`--- ${key} ${stream} ---\n${row[key][stream] || ''}\n--- End ---`);
    }
  }
  get('results').replaceChildren(...ordered.map(row => cards.get(row.compiler).section));
  report = reports.join('\n'); controls();
}
async function run(compileOnly) {
  if (busy || loading) return;
  names = controls();
  if (!sources.length || !names.length) return;
  try {
    const settings = {preset: get('preset').value, standard: get('standard').value};
    if (get('optimization').value !== '') settings.optimization = Number(get('optimization').value);
    for (const key of ['warnings', 'bounds_check', 'backtrace', 'preprocess', 'fast_math']) settings[key] = get(key).checked;
    const extras = Object.fromEntries(names.map(name => [name, JSON.parse(get(name + '-options').value)]));
    const request = {sources: sources.map(source => ({...source})), compilers: names, settings, extras,
      stdin: compileOnly ? '' : get('stdin').value, compile_only: compileOnly, fail_fast: get('fail-fast').checked,
      compile_timeout: Number(get('compile-timeout').value), run_timeout: Number(get('run-timeout').value)};
    busy = true; stopping = false; jobId = ''; rows = []; cards.clear(); render(); status('Running locally...');
    const created = await api('jobs', request); jobId = created.id;
    if (stopping) await api(`jobs/${jobId}/cancel`, {});
    while (true) {
      const result = await api(`jobs/${jobId}`); rows = result.rows;
      if (result.state === 'done') finishPending(result.error || 'Server finished without a compiler result.');
      render();
      if (result.state === 'done') {status(result.error || (stopping ? 'Stopped.' : 'Finished. Results use the source snapshot captured at submission.')); break;}
      await new Promise(resolve => setTimeout(resolve, 300));
    }
  } catch (error) {
    status(error.message);
    if (busy) {finishPending(error.message); render();}
    if (jobId) {try {await api(`jobs/${jobId}/cancel`, {});} catch {}}
  } finally {busy = false; controls();}
}
function finishPending(message) {
  rows = names.map(name => {
    const row = rows.find(item => item.compiler === name);
    return row && !['QUEUED', 'RUNNING'].includes(row.status) ? row :
      {...row, compiler: name, status: 'ERROR', error: message};
  });
}
get('compile').onclick = () => run(true); get('run').onclick = () => run(false);
get('stop').onclick = async () => {stopping = true; controls(); status('Stopping...'); try {if (jobId) await api(`jobs/${jobId}/cancel`, {});} catch (error) {status(error.message);}};
get('copy').onclick = async () => {
  const text = report + (outputComparison.report() ? '\n' + outputComparison.report() : '');
  try {await navigator.clipboard.writeText(text); get('copy-status').textContent = 'Results copied.'; get('copy-text').hidden = true;}
  catch {get('copy-text').hidden = false; get('copy-text').value = text; get('copy-text').select(); get('copy-status').textContent = 'Copy the selected results.';}
};
try {
  const session = await api('session'); catalog = session.compilers;
  get('workspace').textContent = 'Workspace and program working directory: ' + session.workspace;
  get('versions').textContent = Object.entries(catalog).map(([name, item]) => `${name}: ${item.version || item.error}`).join(' | ');
  for (const [name, item] of Object.entries(catalog)) {
    if (item.path) {const option = element('option', name, get('compiler')); option.value = name;}
  }
  const first = Object.keys(catalog).find(name => catalog[name].path); if (first) get(first).checked = true;
  await refresh(); status(first ? 'Ready. Type or paste Fortran code, or add workspace files.' : 'No compiler found. Restart from a compiler terminal or supply --compiler-path.');
} catch (error) {status(error.message);}
controls();
