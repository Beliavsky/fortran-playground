import {renderPlots} from '../plots.mjs';
import {createEditor} from '../editors.mjs';
import {loadIndentation, saveIndentation} from '../indentation.mjs';
import {createOutputComparison} from '../output_diff_ui.mjs';

const get = id => document.getElementById(id);
let token = new URLSearchParams(location.hash.slice(1)).get('session') || '';
try {
  if (token) sessionStorage.setItem('local-fortran-session', token);
  else token = sessionStorage.getItem('local-fortran-session') || '';
  history.replaceState(null, '', location.pathname);
} catch {}
get('source-link').href = '/#session=' + encodeURIComponent(token);
get('catalog-link').href = '/fpm/#session=' + encodeURIComponent(token);
const names = ['gfortran', 'gfortran17', 'ifx', 'flang', 'lfortran'];
let catalog = {}, fpm = '', busy = false, loading = false, stopping = false, job = '', rows = [];
const comparison = createOutputComparison(get);
let indentation = loadIndentation();
const editor = createEditor(get('source'), get('line-count'), () => {get('checks').hidden = true;});
editor.setIndentation(indentation);
if (globalThis.CodeMirror) editor.enhance(globalThis.CodeMirror, 'text/x-fortran', 'Fortran main program');
get('indent-width').value = String(indentation.width); get('auto-indent').checked = indentation.automatic;
const status = text => {get('status').textContent = text;};
const resultLabel = row => row.nothing_run ? 'BUILD PASS — nothing run' : row.status;

async function api(path, payload) {
  const response = await fetch('/api/' + path, {cache: 'no-store', signal: AbortSignal.timeout(45000),
    method: payload === undefined ? 'GET' : 'POST',
    headers: {'X-Local-Token': token, ...(payload === undefined ? {} : {'Content-Type': 'application/json'})},
    ...(payload === undefined ? {} : {body: JSON.stringify(payload)})});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

function selected() {
  return get('interface').value === 'compare'
    ? names.filter(name => get('compiler-' + name).checked && catalog[name]?.path)
    : [get('compiler').value].filter(name => catalog[name]?.path);
}

function controls() {
  const consumer = get('workflow').value === 'consumer', compare = get('interface').value === 'compare';
  get('test-action').disabled = consumer;
  get('example-action').disabled = consumer;
  if (consumer && ['test', 'example'].includes(get('action').value)) get('action').value = 'run';
  get('source-pane').hidden = !consumer;
  get('single-compiler').hidden = compare; get('compiler-choices').hidden = !compare;
  get('target-controls').hidden = consumer || get('action').value === 'build';
  get('stdin-pane').hidden = get('action').value === 'build';
  get('submit').textContent = {build: 'Build', run: 'Compile and Run', example: 'Run examples', test: 'Build and Test'}[get('action').value];
  get('submit').disabled = busy || loading || !fpm || !selected().length || !get('project').value.trim();
  get('stop').disabled = !busy || stopping || !job;
  for (const id of ['project', 'refresh', 'workflow', 'action', 'profile', 'interface', 'compiler', 'target', 'stdin', 'stdin-file',
    'main-file', 'indent-width', 'auto-indent', 'compile-timeout', 'run-timeout', 'fail-fast']) get(id).disabled = busy || loading;
  for (const name of names) get('compiler-' + name).disabled = busy || loading || !catalog[name]?.path;
  for (const id of ['format', 'check']) get(id).disabled = busy || loading || !editor.getValue().trim();
  get('copy').disabled = !rows.length;
  editor.setReadOnly(busy || loading);
  editor.refresh();
}

function report() {
  return rows.map(row => {
    const lines = [`=== ${row.compiler}: ${resultLabel(row)} ===`, row.compiler_version || '',
      row.project ? 'Project: ' + row.project : '', row.working_directory ? 'Working directory: ' + row.working_directory : '', row.error || ''];
    lines.push(...(row.notes || []).map(note => 'Note: ' + note));
    if (row.times) lines.push('Times in seconds: ' + Object.entries(row.times).map(([key, value]) => `${key}=${value == null ? '-' : value.toFixed(3)}`).join(' '));
    for (const stage of row.stages ?? []) lines.push('$ ' + stage.command.join(' '), stage.stdout, stage.stderr);
    if (row.targets?.length) lines.push('Available targets: ' + row.targets.join(', '));
    return lines.filter(Boolean).join('\n');
  }).join('\n\n') + (comparison.report() ? '\n\n' + comparison.report() : '');
}

function render() {
  get('summary').replaceChildren(); get('results').replaceChildren();
  const targets = new Set();
  for (const row of rows) {
    const tr = document.createElement('tr');
    const values = [row.compiler, resultLabel(row), ...['total', 'compile', 'run', 'other'].map(key => row.times?.[key] == null ? '-' : row.times[key].toFixed(3))];
    for (const value of values) {const td = document.createElement('td'); td.textContent = value; tr.appendChild(td);}
    get('summary').appendChild(tr);
    const section = document.createElement('section'); section.className = 'result';
    const pre = document.createElement('pre');
    pre.textContent = [row.compiler + ': ' + resultLabel(row), row.compiler_version || '', row.error || '', ...(row.notes || []).map(note => 'Note: ' + note),
      ...((row.stages ?? []).flatMap(stage => ['$ ' + stage.command.join(' '), stage.stdout || '', stage.stderr || '']))].filter(Boolean).join('\n');
    section.appendChild(pre); renderPlots(section, row); get('results').appendChild(section);
    for (const name of row.targets ?? []) targets.add(name);
  }
  get('targets').replaceChildren(...[...targets].map(value => {const option = document.createElement('option'); option.value = value; return option;}));
  comparison.update(rows); controls();
}

async function refresh() {
  loading = true; controls();
  try {
    const session = await api('fpm/session'); catalog = session.compilers; fpm = session.fpm;
    get('workspace').textContent = 'Workspace: ' + session.workspace + ' · FPM: ' + (fpm || 'not found');
    const previous = get('compiler').value;
    get('compiler').replaceChildren(...names.filter(name => catalog[name]?.path).map(name => {
      const option = document.createElement('option'); option.value = name; option.textContent = name; return option;
    }));
    const first = names.find(name => catalog[name]?.path);
    get('compiler').value = catalog[previous]?.path ? previous : first || '';
    if (!names.some(name => get('compiler-' + name).checked) && first) get('compiler-' + first).checked = true;
    get('projects').replaceChildren(...session.projects.map(value => {const option = document.createElement('option'); option.value = value; return option;}));
    if (get('project').value === '.' && !session.projects.includes('.') && session.projects.length) get('project').value = session.projects[0];
    get('versions').textContent = names.filter(name => catalog[name]?.path).map(name => `${name}: ${catalog[name].version || catalog[name].path}`).join(' · ');
    status(fpm ? 'Ready' : 'FPM not found. Install it or restart with --fpm-path PATH.');
  } catch (error) {status(error.message);}
  finally {loading = false; controls();}
}

async function submit() {
  if (busy || loading) return;
  const compilers = selected();
  busy = true; stopping = false; job = ''; rows = compilers.map(compiler => ({compiler, status: 'QUEUED'})); render();
  let completed = false;
  try {
    const action = get('action').value;
    const data = {project: get('project').value.trim(), compilers, options: {action,
      source: get('workflow').value === 'consumer' ? editor.getValue() : null,
      target: get('workflow').value === 'package' && action !== 'build' ? get('target').value.trim() : '',
      stdin: action === 'build' ? '' : get('stdin').value, profile: get('profile').value,
      compile_timeout: Number(get('compile-timeout').value), run_timeout: Number(get('run-timeout').value), fail_fast: get('fail-fast').checked}};
    job = (await api('fpm/jobs', data)).id;
    if (!job) throw new Error('The server did not return a job ID');
    if (stopping) await api('jobs/' + job + '/cancel', {});
    controls();
    while (true) {
      const result = await api('jobs/' + job); rows = result.rows || []; render();
      if (result.state === 'done') {
        completed = true;
        status(result.error || (stopping ? 'Stopped' : rows.every(row => row.ok) ? 'PASS'
          : rows.some(row => row.nothing_run) && rows.every(row => row.ok || row.nothing_run)
            ? 'BUILD PASS — nothing run for some compilers; see results.' : 'Some operations failed; see results and available targets.'));
        break;
      }
      status(stopping ? 'Stopping…' : 'Building or running with local FPM…');
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  } catch (error) {
    rows = rows.map(row => ['QUEUED', 'RUNNING'].includes(row.status) ? {...row, status: 'ERROR', ok: false, error: error.message} : row);
    render(); status(error.message);
  } finally {
    if (job && !completed) {try {await api('jobs/' + job + '/cancel', {});} catch {}}
    busy = false; job = ''; controls();
  }
}

get('submit').onclick = submit;
get('stop').onclick = async () => {stopping = true; controls(); if (job) {try {await api('jobs/' + job + '/cancel', {});} catch (error) {status(error.message);}}};
get('refresh').onclick = refresh;
for (const id of ['workflow', 'action', 'interface', 'compiler', 'profile']) get(id).onchange = controls;
get('project').oninput = () => {get('target').value = ''; get('targets').replaceChildren(); controls();};
for (const name of names) get('compiler-' + name).onchange = controls;
for (const id of ['indent-width', 'auto-indent']) get(id).onchange = () => {
  indentation = {width: Number(get('indent-width').value), automatic: get('auto-indent').checked};
  saveIndentation(undefined, indentation); editor.setIndentation(indentation);
};
for (const [id, target] of [['main-file', 'source'], ['stdin-file', 'stdin']]) get(id).onchange = async () => {
  try {const file = get(id).files[0]; if (!file) return; const text = await file.text(); if (target === 'source') editor.setValue(text, true); else get(target).value = text;}
  catch (error) {status(error.message);}
};
for (const action of ['format', 'check']) get(action).onclick = async () => {
  loading = true; controls();
  try {
    const result = await api(action, {path: 'main.f90', source: editor.getValue(), indent: indentation.width});
    if (!result.ok) throw new Error(result.error || result.stderr || 'Editor tool failed');
    if (action === 'format') editor.setValue(result.formatted_source, true);
    else {editor.setDiagnostics(result.diagnostics || []); get('checks').textContent = JSON.stringify(result.diagnostics || [], null, 2); get('checks').hidden = false;}
    status(action === 'format' ? 'Formatted' : 'Check complete');
  } catch (error) {status(error.message);}
  finally {loading = false; controls();}
};
get('copy').onclick = async () => {
  try {await navigator.clipboard.writeText(report()); status('Results copied');}
  catch {get('copy-text').hidden = false; get('copy-text').value = report(); get('copy-text').focus(); get('copy-text').select(); status('Copy the selected results');}
};
await refresh();
