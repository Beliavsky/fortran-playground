import {renderPlots} from '../plots.mjs';
import {createEditor} from '../editors.mjs';
import {serviceOrigin} from '../service_config.mjs';
import {githubRepository, pinnedSource, projectFiles, zipFiles, download} from './project_export.mjs';

const get = id => document.getElementById(id);
const localExecution = document.documentElement?.dataset?.execution === 'local';
let localToken = '';
if (localExecution) {
  localToken = new URLSearchParams(location.hash.slice(1)).get('session') || '';
  try {
    if (localToken) sessionStorage.setItem('local-fortran-session', localToken);
    else localToken = sessionStorage.getItem('local-fortran-session') || '';
    history.replaceState(null, '', location.pathname + location.search);
  } catch {}
  for (const [id, path] of [['local-source-link', '/'], ['local-projects-link', '/fpm/projects/']]) {
    get(id).href = path + '#session=' + encodeURIComponent(localToken);
  }
}
const editor = createEditor(get('source'), get('line-count'));
editor.setIndentation({width: 3, automatic: true});
let origin = '', examples = [], busy = false, job = '', targetsKey = '', ready = false;
let compilerLabels = {gfortran: 'GNU Fortran 16.2.0'};
let compilerSelection = false;
let translatedSupported = false;
let examplesSupported = false;
const examplesUnavailable = () => get('action').value === 'example' && !examplesSupported;
const translatedUnavailable = () => Boolean(get('subdirectory').value.trim()) && !translatedSupported;
let packages = [], generalPackages = [], translatedPackages, precompiled = {};
let collectionLoading = false, collectionGeneration = 0;
let searchButtons = [];
let topicButtons = [];
const genericTopics = new Set(['fortran', 'modern-fortran', 'fortran-package-manager', 'fpm']);
const translatedCollection = () => get('package-collection').value === 'translated-r';
const packageCategories = p => p.categories?.length ? p.categories : [p.category];
let exporting = false, exportRuntime;
get('compiler').value = 'gfortran';

function controls() {
  const consumer = get('workflow').value === 'consumer';
  get('test-action').disabled = consumer;
  get('example-action').disabled = consumer;
  if (consumer && ['test', 'example'].includes(get('action').value)) get('action').value = 'run';
  get('source-pane').hidden = !consumer;
  get('workspace').classList.toggle('package-only', !consumer);
  get('target-controls').hidden = consumer || get('action').value === 'build';
  get('stdin-pane').hidden = get('action').value === 'build';
  get('workflow-note').textContent = consumer
    ? 'The package is built as a dependency of your main program. Examples include working main programs.'
    : 'Compile and Run selects applications; Run examples selects FPM example targets; Test selects tests. Targets accept names or * and ? patterns, separated by spaces or commas. Leave blank to discover applications/examples or run all tests. Programs share the run/test time limit.';
  const labels = {run: 'Compile and Run', example: 'Run examples', build: 'Build', test: 'Build and Test'};
  get('submit').textContent = labels[get('action').value];
  if (ready && translatedUnavailable()) get('workflow-note').textContent = localExecution
    ? 'Restart the local server with the updated code to enable translated R packages.'
    : 'The connected FPM service does not yet support translated R packages. Complete the updated FPM backend deployment, then reload this page. General packages remain available.';
  if (ready && examplesUnavailable()) get('workflow-note').textContent = localExecution
    ? 'Restart the local server with the updated code to enable Run examples.'
    : 'The connected FPM service needs an update to support Run examples. Complete the backend deployment, then reload this page.';
  get('submit').disabled = busy || !ready || translatedUnavailable() || examplesUnavailable();
  get('cancel').disabled = !busy || !job;
  for (const id of ['workflow', 'action', 'package-url', 'revision', 'subdirectory', 'target', 'example', 'package-collection']) get(id).disabled = busy;
  get('compiler').disabled = busy || !ready || !compilerSelection;
  get('load-example').disabled = busy || !get('example').value;
  get('available-package').disabled = busy;
  get('package-search').disabled = busy || collectionLoading;
  get('package-category').disabled = busy || collectionLoading;
  for (const button of searchButtons) button.disabled = busy;
  for (const button of topicButtons) button.disabled = busy;
  const selected = packages.find(p => p.id === get('available-package').value);
  get('load-package').disabled = busy || collectionLoading || !selected || (!localExecution && !translatedCollection() && (!ready
    || precompiled[selected.id]?.revision !== selected.revision));
  get('download-main').disabled = busy;
  get('download-project').disabled = busy || exporting;
  editor.setReadOnly(busy);
  editor.refresh();
}

function renderTopics(packageEntry) {
  const container = get('package-topics');
  const topics = [...new Set(packageEntry?.topics || [])].sort((a, b) =>
    Number(genericTopics.has(a)) - Number(genericTopics.has(b)) || a.localeCompare(b));
  container.replaceChildren();
  topicButtons = [];
  container.hidden = !topics.length;
  if (!topics.length) return;
  const label = document.createElement('span'); label.textContent = 'GitHub topics:'; container.appendChild(label);
  for (const topic of topics) {
    const button = document.createElement('button'); button.type = 'button'; button.textContent = topic;
    button.disabled = busy;
    button.addEventListener('click', () => {
      get('package-search').value = topic;
      get('package-category').value = '';
      renderPackages();
    });
    topicButtons.push(button); container.appendChild(button);
  }
}

function renderPackages() {
  const previous = get('available-package').value;
  const query = get('package-search').value.trim().toLowerCase();
  const category = get('package-category').value;
  const visible = packages.filter(p => {
    const text = `${p.id} ${p.repository} ${p.description} ${p.category} ${(p.keywords || []).join(' ')} ${(p.topics || []).join(' ')}`.toLowerCase();
    return (!category || packageCategories(p).includes(category)) && (text.includes(query)
      || text.replace(/[-_]+/g, ' ').includes(query.replace(/[-_]+/g, ' ')));
  });
  const placeholder = document.createElement('option');
  placeholder.value = ''; placeholder.textContent = localExecution || translatedCollection() ? 'Choose a package…' : 'Choose a precompiled package…';
  get('available-package').replaceChildren(placeholder);
  for (const item of visible) {
    const option = document.createElement('option');
    option.value = item.id;
    option.textContent = `${item.id} — ${item.description}`;
    option.disabled = !localExecution && !translatedCollection() && precompiled[item.id]?.revision !== item.revision;
    get('available-package').appendChild(option);
  }
  get('available-package').value = query && visible.length === 1 ? visible[0].id
    : visible.some(p => p.id === previous) ? previous : '';
  get('package-count').textContent = `${visible.length} of ${packages.length} packages`;
  renderTopics(packages.find(p => p.id === get('available-package').value));
  const matches = get('package-search-results');
  matches.replaceChildren();
  searchButtons = [];
  matches.hidden = !query;
  if (query) {
    for (const item of visible.slice(0, 20)) {
      const button = document.createElement('button');
      button.type = 'button'; button.disabled = busy;
      button.textContent = `${item.id} — ${item.description}`;
      button.addEventListener('click', () => {get('available-package').value = item.id; selectPackage();});
      searchButtons.push(button);
      matches.appendChild(button);
    }
    if (!visible.length) {
      const message = document.createElement('span');
      message.textContent = `No matches in ${translatedCollection() ? 'Translated R packages' : 'General Fortran packages'}${category ? ' / ' + category : ''}.`;
      matches.appendChild(message);
      const button = document.createElement('button'); button.type = 'button'; button.disabled = busy;
      button.textContent = category ? 'Search all categories' : translatedCollection() ? 'Search General Fortran packages' : 'Search Translated R packages';
      button.addEventListener('click', async () => {
        if (category) get('package-category').value = '';
        else {
          get('package-collection').value = translatedCollection() ? 'general' : 'translated-r';
          await selectCollection();
          get('package-search').value = query;
        }
        renderPackages();
      });
      matches.appendChild(button);
      searchButtons.push(button);
    }
    if (visible.length === 1) selectPackage();
  }
  controls();
}

get('package-search').addEventListener('input', renderPackages);
get('package-category').addEventListener('change', renderPackages);

async function selectCollection() {
  const generation = ++collectionGeneration;
  const translated = translatedCollection();
  collectionLoading = true;
  packages = [];
  renderPackages();
  get('package-note').textContent = 'Loading collection…';
  try {
    if (translated && !translatedPackages) {
      const response = await fetch('./translated-r.json', {cache: 'no-store'});
      if (!response.ok) throw new Error('Cannot load the translated R catalog. Please retry.');
      translatedPackages = await response.json();
    }
    if (generation !== collectionGeneration) return;
    packages = translated ? translatedPackages : generalPackages;
    get('package-list-label').textContent = translated ? 'Translated R packages (build from scratch)'
      : localExecution ? 'Packages (build locally)' : 'Available packages (GNU Fortran 16)';
    get('package-search').value = '';
    get('package-category').replaceChildren(...['', ...new Set(packages.flatMap(packageCategories))].sort().map(value => {
      const option = document.createElement('option'); option.value = value; option.textContent = value || 'All categories'; return option;
    }));
    get('package-category').value = '';
    get('available-package').value = '';
    get('package-note').textContent = translated
      ? 'Experimental R translations. Select a package to build or run its own programs, or write your own main. Sources and sibling dependencies download at the pinned revision. Every job builds from scratch; these packages have not been verified in this playground and may exceed online limits.'
      : 'Choose a package to load its pinned revision and example main.';
  } catch (error) {
    if (generation === collectionGeneration) get('package-note').textContent = error.message;
  } finally {
    if (generation === collectionGeneration) {collectionLoading = false; renderPackages();}
  }
}
get('package-collection').value = 'general';
get('package-collection').addEventListener('change', selectCollection);

function sourceLinks(packageEntry) {
  const url = pinnedSource(packageEntry);
  get('package-source-links').hidden = !url;
  get('package-source').href = url || '';
}

get('download-main').addEventListener('click', () => {
  download(new Blob([editor.getValue()], {type: 'text/plain;charset=utf-8'}), 'main.f90');
});
get('download-project').addEventListener('click', async () => {
  // Snapshot everything before fetching tools, so edits during the download
  // cannot mix different main programs, inputs or dependency selections.
  const snapshot = {source: editor.getValue(), stdin: get('stdin').value,
    url: get('package-url').value.trim(), revision: get('revision').value.trim(),
    subdirectory: get('subdirectory').value.trim(), packages};
  exporting = true; controls();
  try {
    if (!exportRuntime) {
      const response = await fetch('./project-runtime.json', {cache: 'no-store'});
      if (!response.ok) throw new Error('Could not load the project download tools. Please retry.');
      exportRuntime = await response.json();
    }
    const files = projectFiles({...snapshot, runtime: exportRuntime});
    const name = githubRepository(snapshot.url).split('/').at(-1);
    download(zipFiles(files), `${name}-playground.zip`);
    get('download-note').textContent = 'Project downloaded. Extract it and follow README.md to build locally; no playground job was submitted.';
  } catch (error) {get('download-note').textContent = error.message;}
  finally {exporting = false; controls();}
});

function resetTargets() {
  const key = [get('package-url').value, get('revision').value, get('subdirectory').value, get('action').value, get('compiler').value].join('\n');
  if (targetsKey !== key) {
    targetsKey = key;
    get('target').value = '';
    get('targets').replaceChildren();
  }
}

export function resultText(result) {
  const lines = [nothingRun(result) ? 'BUILD PASS — nothing run'
    : `${result.ok ? 'PASS' : 'FAIL'}${result.needs_target ? ' — target selection required' : ''}`];
  if (result.error) lines.push(result.error);
  for (const note of result.notes ?? []) lines.push('Note: ' + note);
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
  if (result.total_seconds !== undefined) lines.push('', `Total ${result.local ? 'local' : 'service'} time: ${result.total_seconds.toFixed(3)} seconds`);
  return lines.join('\n');
}

function nothingRun(result) {
  return result.nothing_run || (!result.ok && result.stages?.some(s => s.name === 'Build' && s.ok)
    && !result.stages.some(s => s.name !== 'Build'));
}

async function request(path, options = {}) {
  if (localExecution) {
    path = '/api/fpm/catalog' + path.slice('/api'.length);
    options = {...options, headers: {...options.headers, 'X-Local-Token': localToken,
      ...(options.method === 'POST' ? {'Content-Type': 'application/json'} : {})},
      ...(options.method === 'POST' ? {body: options.body || '{}'} : {})};
  }
  const response = await fetch(origin + path, {...options, signal: AbortSignal.timeout(20000)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Service returned HTTP ${response.status}`);
  return data;
}

async function submit() {
  if (busy || !ready || translatedUnavailable() || examplesUnavailable()) return;
  busy = true;
  job = '';
  controls();
  get('status').textContent = 'Submitting…';
  get('output').value = '';
  get('plot-results').replaceChildren();
  let terminal = false;
  try {
    const payload = {url: get('package-url').value.trim(), revision: get('revision').value.trim(),
      ...(get('subdirectory').value.trim() ? {subdirectory: get('subdirectory').value.trim()} : {}),
      ...(compilerSelection ? {compiler: get('compiler').value} : {}),
      workflow: get('workflow').value, action: get('action').value, target: get('target').value.trim(),
      source: editor.getValue(), stdin: get('stdin').value};
    const submitted = await request('/api/jobs', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
    job = submitted.id;
    controls();
    const deadline = localExecution ? Infinity : Date.now() + 420000;
    while (Date.now() < deadline) {
      get('status').textContent = 'Preparing, building, or running…';
      await new Promise(resolve => setTimeout(resolve, 1000));
      const response = await request(`/api/jobs/${job}`);
      if (response.state !== 'done') continue;
      terminal = true;
      const result = response.result;
      get('output').value = resultText(result);
      renderPlots(get('plot-results'), result);
      get('status').textContent = nothingRun(result) ? 'BUILD PASS — nothing run'
        : result.needs_target ? 'Choose a target' : result.ok ? 'PASS' : 'FAIL';
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
  get('connection').textContent = localExecution
    ? `${compilerLabels[get('compiler').value]} · Local FPM · Builds from scratch`
    : `${compilerLabels[get('compiler').value]} · FPM 0.12.0 · Separate package service`;
  controls();
});
for (const id of ['package-url', 'revision', 'subdirectory']) get(id).addEventListener('input', () => {
  resetTargets();
  sourceLinks({repository: githubRepository(get('package-url').value.trim()),
    revision: get('revision').value.trim(), subdirectory: get('subdirectory').value.trim()});
  controls();
});
get('example').addEventListener('change', controls);
function selectPackage() {
  const selected = packages.find(p => p.id === get('available-package').value);
  renderTopics(selected);
  sourceLinks(selected);
  const note = get('package-note');
  note.textContent = selected
    ? `${selected.description} Source: `
    : 'Choose a package to load its pinned revision and a working main program. Loading does not run a job.';
  if (selected) {
    const source = pinnedSource(selected);
    const repository = document.createElement(source ? 'a' : 'span');
    repository.textContent = selected.repository;
    const separator = document.createElement('span'); separator.textContent = ' @ ';
    const revision = document.createElement(source ? 'a' : 'span');
    revision.textContent = selected.revision.slice(0, 7);
    revision.title = selected.revision;
    if (source) {
      repository.href = `https://github.com/${selected.repository}`;
      revision.href = source;
      for (const link of [repository, revision]) {
        link.target = '_blank'; link.rel = 'noopener noreferrer';
      }
      revision.setAttribute('aria-label', `Browse source at commit ${selected.revision}`);
    }
    const detail = document.createElement('span');
    detail.textContent = '. ' + (selected.subdirectory ? 'Experimental R translation; not verified in this playground. Each submission builds from scratch. See the pinned source for documentation, examples, coverage and licensing.'
        : localExecution ? 'Sources download and build locally when you submit a job.'
        : precompiled[selected.id]?.revision === selected.revision ? 'Verified precompiled GNU 16 library.'
        : 'Precompiled build is not available on this service yet.');
    for (const child of [repository, separator, revision, detail]) note.appendChild(child);
  }
  controls();
}
get('available-package').addEventListener('change', selectPackage);
get('load-package').addEventListener('click', () => {
  const selected = packages.find(p => p.id === get('available-package').value);
  if (!selected || get('load-package').disabled) return;
  get('package-url').value = `https://github.com/${selected.repository}`;
  get('revision').value = selected.revision;
  get('subdirectory').value = selected.subdirectory || '';
  if (!localExecution && !selected.subdirectory) get('compiler').value = 'gfortran';
  get('connection').textContent = localExecution
    ? `${compilerLabels[get('compiler').value] || 'No compiler found'} · Local FPM · Builds from scratch`
    : `${compilerLabels[get('compiler').value]} · FPM 0.12.0 · Separate package service`;
  get('workflow').value = selected.subdirectory ? 'package' : 'consumer';
  get('action').value = 'run';
  if (selected.source) editor.setValue(selected.source);
  sourceLinks(selected);
  resetTargets(); controls();
});
get('load-example').addEventListener('click', () => {
  const example = examples.find(item => item.name === get('example').value);
  if (!example) return;
  get('package-url').value = `https://github.com/${example.repository}`;
  get('revision').value = example.revision;
  get('subdirectory').value = '';
  get('workflow').value = 'consumer';
  get('action').value = 'run';
  editor.setValue(example.source);
  sourceLinks({repository: example.repository, revision: example.revision});
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
    generalPackages = data;
    packages = data;
    for (const category of [...new Set(packages.map(p => p.category))].sort()) {
      const option = document.createElement('option');
      option.value = category; option.textContent = category;
      get('package-category').appendChild(option);
    }
  }).catch(error => {get('package-note').textContent = error.message;});
  try {
    if (!localExecution) {
      const response = await fetch('./service.json', {cache: 'no-store'});
      if (!response.ok) throw new Error('Cannot load FPM service configuration.');
      const configuration = await response.json();
      if (!configuration.url) throw new Error('The FPM service has not been configured yet. See the instructions linked below.');
      origin = serviceOrigin(configuration.url);
    }
    const health = await request('/api/health');
    if (!health.ok || typeof health.fpm !== 'string') throw new Error(health.error || 'FPM service unavailable or incompatible.');
    compilerSelection = Boolean(health.compilers);
    compilerLabels = health.compilers ?? {gfortran: health.compiler};
    precompiled = health.precompiled ?? {};
    translatedSupported = health.features?.translated_r === true;
    examplesSupported = health.features?.run_examples === true;
    if (localExecution) {
      get('compiler').replaceChildren(...Object.entries(compilerLabels).map(([value, textContent]) => {
        const option = document.createElement('option'); Object.assign(option, {value, textContent}); return option;
      }));
      get('compiler').value = Object.hasOwn(compilerLabels, 'gfortran') ? 'gfortran' : Object.keys(compilerLabels)[0] || '';
    }
    for (const option of get('compiler').options) {
      option.disabled = !Object.hasOwn(compilerLabels, option.value);
      if (!option.disabled) option.textContent = compilerLabels[option.value];
    }
    ready = true;
    get('connection').textContent = localExecution
      ? `${health.workspace} · ${compilerLabels[get('compiler').value]} · Local FPM · Builds from scratch`
      : `${health.compiler} · FPM ${health.fpm} · Separate package service`;
    get('status').textContent = 'Ready';
  } catch (error) {
    get('connection').textContent = error.message;
    get('status').textContent = localExecution ? 'Local setup incomplete' : 'Service unavailable';
  }
  await Promise.all([catalog, available]);
  renderPackages();
  get('package-note').textContent = localExecution
    ? 'Choose a package to load its pinned revision and example main. Each submission downloads sources and builds locally from scratch.'
    : Object.keys(precompiled).length
    ? 'Choose a package to load its pinned revision and a working main program. Loading does not run a job.'
    : 'Precompiled packages have not been deployed on this service yet. The existing examples and custom URLs remain available.';
  controls();
  if (typeof location !== 'undefined' && new URLSearchParams(location.search).get('collection') === 'translated-r') {
    get('package-collection').value = 'translated-r';
    await selectCollection();
  }
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
