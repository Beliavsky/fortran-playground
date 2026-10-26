import {renderPlots} from '../plots.mjs';
import {createEditor} from '../editors.mjs';
import {serviceOrigin} from '../service_config.mjs';

const get = id => document.getElementById(id);
const editor = createEditor(get('source'), get('line-count'));
editor.setIndentation({width: 3, automatic: true});
let origin = '', examples = [], busy = false, job = '', targetsKey = '', ready = false;
let compilerLabels = {gfortran: 'GNU Fortran 16.2.0'};
let compilerSelection = false;
let packages = [], precompiled = {};
get('compiler').value = 'gfortran';

function controls() {
  const consumer = get('workflow').value === 'consumer';
  get('test-action').disabled = consumer;
  if (consumer && get('action').value === 'test') get('action').value = 'run';
  get('source-pane').hidden = !consumer;
  get('workspace').classList.toggle('package-only', !consumer);
  get('target-controls').hidden = consumer || get('action').value === 'build';
  get('stdin-pane').hidden = get('action').value === 'build';
  get('workflow-note').textContent = consumer
    ? 'The package is built as a dependency of your main program. Examples include working main programs.'
    : 'Build the downloaded project itself. Run uses an application target; Test runs all tests unless you select one. Leave the target blank to discover available applications.';
  const labels = {run: 'Compile and Run', build: 'Build', test: 'Build and Test'};
  get('submit').textContent = labels[get('action').value];
  get('submit').disabled = busy || !ready;
  get('cancel').disabled = !busy || !job;
  for (const id of ['workflow', 'action', 'package-url', 'revision', 'target', 'example']) get(id).disabled = busy;
  get('compiler').disabled = busy || !ready || !compilerSelection;
  get('load-example').disabled = busy || !get('example').value;
  get('available-package').disabled = busy;
  get('package-search').disabled = busy;
  get('package-category').disabled = busy;
  const selected = packages.find(p => p.id === get('available-package').value);
  get('load-package').disabled = busy || !ready || !selected
    || precompiled[selected.id]?.revision !== selected.revision;
  editor.setReadOnly(busy);
  editor.refresh();
}

function renderPackages() {
  const previous = get('available-package').value;
  const query = get('package-search').value.trim().toLowerCase();
  const category = get('package-category').value;
  const visible = packages.filter(p => (!category || p.category === category)
    && `${p.id} ${p.repository} ${p.description} ${p.category}`.toLowerCase().includes(query));
  const placeholder = document.createElement('option');
  placeholder.value = ''; placeholder.textContent = 'Choose a precompiled package…';
  get('available-package').replaceChildren(placeholder);
  for (const item of visible) {
    const option = document.createElement('option');
    option.value = item.id;
    option.textContent = `${item.id} — ${item.description}`;
    option.disabled = precompiled[item.id]?.revision !== item.revision;
    get('available-package').appendChild(option);
  }
  get('available-package').value = visible.some(p => p.id === previous) ? previous : '';
  get('package-count').textContent = `${visible.length} of ${packages.length} packages`;
  controls();
}

get('package-search').addEventListener('input', renderPackages);
get('package-category').addEventListener('change', renderPackages);

function resetTargets() {
  const key = [get('package-url').value, get('revision').value, get('action').value, get('compiler').value].join('\n');
  if (targetsKey !== key) {
    targetsKey = key;
    get('target').value = '';
    get('targets').replaceChildren();
  }
}

export function resultText(result) {
  const lines = [`${result.ok ? 'PASS' : 'FAIL'}${result.needs_target ? ' — target selection required' : ''}`];
  if (result.error) lines.push(result.error);
  for (const pkg of result.packages ?? []) lines.push(`Package: ${pkg.repository} @ ${pkg.revision}`);
  if (result.compiler) lines.push(`Compiler: ${result.compiler}; FPM ${result.fpm}`);
  if (result.cache) lines.push(`Precompiled package: ${result.cache.package} (${result.cache.compiler}); `
    + (result.cache.library_reused ? 'library reused' : 'library required rebuilding'));
  if (result.prepare_seconds !== undefined) lines.push(`Prepare: ${result.prepare_seconds.toFixed(3)} seconds`);
  for (const stage of result.stages ?? []) {
    lines.push('', `${stage.name}: ${stage.ok ? 'PASS' : 'FAIL'} (${stage.seconds.toFixed(3)} seconds)`,
      `$ ${stage.command.join(' ')}`, stage.stdout, stage.stderr);
    if (stage.error) lines.push(stage.error);
    if (stage.exit_code !== 0) lines.push(`Exit code: ${stage.exit_code}`);
  }
  if (result.targets?.length) lines.push('', `Available targets: ${result.targets.join(', ')}`);
  if (result.total_seconds !== undefined) lines.push('', `Total service time: ${result.total_seconds.toFixed(3)} seconds`);
  return lines.join('\n');
}

async function request(path, options = {}) {
  const response = await fetch(origin + path, {...options, signal: AbortSignal.timeout(20000)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Service returned HTTP ${response.status}`);
  return data;
}

async function submit() {
  if (busy || !ready) return;
  busy = true;
  job = '';
  controls();
  get('status').textContent = 'Submitting…';
  get('output').value = '';
  get('plot-results').replaceChildren();
  let terminal = false;
  try {
    const payload = {url: get('package-url').value.trim(), revision: get('revision').value.trim(),
      ...(compilerSelection ? {compiler: get('compiler').value} : {}),
      workflow: get('workflow').value, action: get('action').value, target: get('target').value.trim(),
      source: editor.getValue(), stdin: get('stdin').value};
    const submitted = await request('/api/jobs', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    job = submitted.id;
    controls();
    const deadline = Date.now() + 420000;
    while (Date.now() < deadline) {
      get('status').textContent = 'Preparing, building, or running…';
      await new Promise(resolve => setTimeout(resolve, 1000));
      const response = await request(`/api/jobs/${job}`);
      if (response.state !== 'done') continue;
      terminal = true;
      const result = response.result;
      get('output').value = resultText(result);
      renderPlots(get('plot-results'), result);
      get('status').textContent = result.needs_target ? 'Choose a target' : result.ok ? 'PASS' : 'FAIL';
      get('targets').replaceChildren(...(result.targets ?? []).map(name => {
        const option = document.createElement('option'); option.value = name; return option;
      }));
      return;
    }
    throw new Error('The job exceeded the service time limit.');
  } catch (error) {
    get('status').textContent = 'Error';
    get('output').value = error.message;
  } finally {
    if (job && !terminal) {
      try {await request(`/api/jobs/${job}/cancel`, {method: 'POST'});} catch { /* Sandbox lifetime remains bounded. */ }
    }
    busy = false;
    job = '';
    controls();
  }
}

get('submit').addEventListener('click', submit);
get('cancel').addEventListener('click', async () => {
  if (!job) return;
  get('cancel').disabled = true;
  get('status').textContent = 'Cancelling…';
  try {await request(`/api/jobs/${job}/cancel`, {method: 'POST'});}
  catch (error) {get('status').textContent = error.message; get('cancel').disabled = false;}
});
for (const id of ['workflow', 'action']) get(id).addEventListener('change', () => {resetTargets(); controls();});
get('compiler').addEventListener('change', () => {
  resetTargets();
  get('connection').textContent = `${compilerLabels[get('compiler').value]} · FPM 0.12.0 · Separate package service`;
  controls();
});
for (const id of ['package-url', 'revision']) get(id).addEventListener('input', resetTargets);
get('example').addEventListener('change', controls);
get('available-package').addEventListener('change', () => {
  const selected = packages.find(p => p.id === get('available-package').value);
  get('package-note').textContent = selected
    ? `${selected.description} Source: https://github.com/${selected.repository} @ ${selected.revision}. `
      + (precompiled[selected.id]?.revision === selected.revision ? 'Verified precompiled GNU 16 library.'
        : 'Precompiled build is not available on this service yet.')
    : 'Choose a package to load its pinned revision and a working main program. Loading does not run a job.';
  controls();
});
get('load-package').addEventListener('click', () => {
  const selected = packages.find(p => p.id === get('available-package').value);
  if (!selected || get('load-package').disabled) return;
  get('package-url').value = `https://github.com/${selected.repository}`;
  get('revision').value = selected.revision;
  get('compiler').value = 'gfortran';
  get('connection').textContent = `${compilerLabels.gfortran} · FPM 0.12.0 · Separate package service`;
  get('workflow').value = 'consumer';
  get('action').value = 'run';
  editor.setValue(selected.source);
  resetTargets(); controls();
});
get('load-example').addEventListener('click', () => {
  const example = examples.find(item => item.name === get('example').value);
  if (!example) return;
  get('package-url').value = `https://github.com/${example.repository}`;
  get('revision').value = example.revision;
  get('workflow').value = 'consumer';
  get('action').value = 'run';
  editor.setValue(example.source);
  resetTargets(); controls();
});
get('copy').addEventListener('click', async () => {
  try {await navigator.clipboard.writeText(get('output').value); get('status').textContent = 'Results copied';}
  catch {get('output').focus(); get('output').select(); get('status').textContent = 'Select and copy the results';}
});

async function initialize() {
  controls();
  // Independent initialization: examples and the editor remain usable offline.
  const catalog = fetch('./examples.json', {cache: 'no-store'}).then(response => {
    if (!response.ok) throw new Error('Cannot load package examples.');
    return response.json();
  }).then(data => {
    examples = data;
    for (const example of examples) {
      const option = document.createElement('option');
      option.value = example.name; option.textContent = `${example.category} — ${example.repository}`;
      get('example').appendChild(option);
    }
  }).catch(error => {get('workflow-note').textContent = error.message;});
  const available = fetch('./packages.json', {cache: 'no-store'}).then(response => {
    if (!response.ok) throw new Error('Cannot load the precompiled package catalog.');
    return response.json();
  }).then(data => {
    packages = data;
    for (const category of [...new Set(packages.map(p => p.category))].sort()) {
      const option = document.createElement('option');
      option.value = category; option.textContent = category;
      get('package-category').appendChild(option);
    }
  }).catch(error => {get('package-note').textContent = error.message;});
  try {
    const response = await fetch('./service.json', {cache: 'no-store'});
    if (!response.ok) throw new Error('Cannot load FPM service configuration.');
    const configuration = await response.json();
    if (!configuration.url) throw new Error('The FPM service has not been configured yet. See the instructions linked below.');
    origin = serviceOrigin(configuration.url);
    const health = await request('/api/health');
    if (!health.ok || typeof health.fpm !== 'string') throw new Error('FPM service unavailable or incompatible.');
    compilerSelection = Boolean(health.compilers);
    compilerLabels = health.compilers ?? {gfortran: health.compiler};
    precompiled = health.precompiled ?? {};
    for (const option of get('compiler').options) {
      option.disabled = !Object.hasOwn(compilerLabels, option.value);
      if (!option.disabled) option.textContent = compilerLabels[option.value];
    }
    ready = true;
    get('connection').textContent = `${health.compiler} · FPM ${health.fpm} · Separate package service`;
    get('status').textContent = 'Ready';
  } catch (error) {
    get('connection').textContent = error.message;
    get('status').textContent = 'Service unavailable';
  }
  await Promise.all([catalog, available]);
  renderPackages();
  get('package-note').textContent = Object.keys(precompiled).length
    ? 'Choose a package to load its pinned revision and a working main program. Loading does not run a job.'
    : 'Precompiled packages have not been deployed on this service yet. The existing examples and custom URLs remain available.';
  controls();
}

if (typeof window !== 'undefined') {
  (async () => {
    try {
      await import('../editor-vendor/codemirror.js');
      await import('../editor-vendor/fortran.js');
      editor.enhance(globalThis.CodeMirror, 'text/x-fortran', 'Fortran main program');
      editor.refresh();
    } catch { /* The textarea retains editing and automatic indentation. */ }
  })();
}
await initialize();
