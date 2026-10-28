import {renderPlots} from './plots.mjs';
import {createEditor} from './editors.mjs';
import {examples, exampleLabels} from './examples.generated.mjs';
import {parseCompilerErrors} from './diagnostics.mjs';
import {playgroundConfig} from './config.mjs';
import {createQuickFixControls} from './quick_fix_controls.mjs';
import {applyFormatting} from './formatting.mjs';
import {sharedCodeFromHash, createShareLink} from './sharing.mjs';
import {serviceOrigin} from './service_config.mjs';
import {compilerArguments, optionTokens} from './compiler_arguments.mjs';
import {sourceURL, combinedSource, mappedErrors} from './external_source.mjs';
import {comparisonPlan, executeComparison} from './comparison.mjs';
import {loadAllOutputs, saveAllOutputs, comparisonOutput, comparisonReport} from './comparison_output.mjs';
import {loadIndentation, saveIndentation} from './indentation.mjs';
import {createOutputComparison} from './output_diff_ui.mjs';
import {parseURLSettings} from './url_settings.mjs';
import {captureState, copyStateLink, stateFromHash} from './state_links.mjs';

const get = id => document.getElementById(id);
const outputComparison = createOutputComparison(get);
const ownerAccessRequested = new URLSearchParams(location.search).get('owner') === '1';
const {settings: urlSettings, warnings: urlWarnings} = parseURLSettings(location.search);
let urlSettingsPending = true, sharedLinkLoaded = false;
let preserveStateOptions = false;
function showURLWarnings() {
  get('url-settings-status').textContent = urlWarnings.join(' ');
  get('url-settings-status').hidden = !urlWarnings.length;
}
function applyURLServiceSettings() {
  if (!urlSettingsPending) return;
  urlSettingsPending = false;
  const settings = {...urlSettings};
  if (sharedLinkLoaded && Object.hasOwn(settings, 'preprocess')) {
    urlWarnings.push('The shared-code link takes precedence over query preprocessing.');
    delete settings.preprocess;
  }
  if (isSimple()) {
    for (const key of ['compiler', 'compilers', 'standard', 'preprocess']) {
      if (Object.hasOwn(settings, key)) urlWarnings.push(`URL setting ${key} is ignored in the Simple interface.`);
    }
    showURLWarnings(); return;
  }
  if (settings.compiler) {
    if (availableCompilers.includes(settings.compiler)) get('compiler').value = settings.compiler;
    else urlWarnings.push(`Requested compiler ${settings.compiler} is unavailable; the current compiler is retained.`);
  }
  if (settings.compilers) {
    if (isCompare()) {
      for (const name of compareNames) get(`compare-${name}`).checked = settings.compilers.includes(name) && availableCompilers.includes(name);
      const missing = settings.compilers.filter(name => !availableCompilers.includes(name));
      if (missing.length) urlWarnings.push(`Requested compilers unavailable: ${missing.join(', ')}.`);
      if (!selectedCompilers().length) urlWarnings.push('No requested compiler is available. Select a compiler before running.');
    } else urlWarnings.push('The shared-code interface overrides the query compiler comparison selection.');
  }
  const names = isCompare() ? selectedCompilers() : [get('compiler').value];
  if (settings.standard) {
    if (settings.standard === 'default' || names.some(name => catalog[name]?.standards?.[settings.standard])) get('standard').value = settings.standard;
    else urlWarnings.push(`Requested standard ${settings.standard} is unavailable for the selected compilers; the current standard is retained.`);
  }
  if (Object.hasOwn(settings, 'preprocess')) {
    if (!settings.preprocess || names.some(name => catalog[name]?.extras?.preprocess)) get('preprocess').checked = settings.preprocess;
    else urlWarnings.push('Requested preprocessing is unavailable for the selected compilers; the current setting is retained.');
  }
  showURLWarnings();
}
function stdinError() {
  const input = get('stdin').value;
  if (new TextEncoder().encode(input).length > Math.min(100000, features.max_stdin_bytes ?? 100000)) return 'Program input exceeds the 100 KB limit or this service\'s input limit.';
  return input && !features.stdin ? 'Standard input requires an updated execution service. Clear the input to run without it.' : '';
}
let token = '', service = '', catalog = {}, active = null, connecting = false, revision = 0;
let filename = 'main.f90';
let features = {}, retained = null, expiryTimer = null;
let externalLoading = false, externalCount = 1;
const externalRows = Array.from({length: 5}, (_, index) => {
  const element = name => get(name + (index ? `-${index}` : ''));
  return {element, source: null, message: ''};
});
const loadedSources = () => externalRows.slice(0, externalCount).map(row => row.source).filter(Boolean);
const hasExternal = () => externalRows.slice(0, externalCount).some(row => row.source || row.element('external-url').value.trim());
function externalError() {
  if (externalLoading) return 'Loading external source...';
  try {
    for (const row of externalRows.slice(0, externalCount)) {
      const url = row.element('external-url').value.trim();
      if (url && (!row.source || sourceURL(url) !== row.source.requestUrl)) return 'Load every external source URL, or remove it, before compiling.';
    }
    combinedSource(editor.getValue(), loadedSources());
    return '';
  } catch (error) { return error.message; }
}
function resetExternalRow(row) {
  row.source = null; row.message = '';
  row.element('external-url').value = ''; row.element('external-source').value = '';
  row.element('external-preview').open = false;
}
function clearExternal() {
  externalRows.forEach(resetExternalRow); externalCount = 1;
}
let compilerVersions = {};
let interfaceMode = ['simple', 'compare'].includes(playgroundConfig.interfaceMode) ? playgroundConfig.interfaceMode : 'advanced';
const compareNames = [...get('compiler').options].map(option => option.value);
get('compare-gfortran').checked = true;
let comparisonRows = [], comparisonSnapshot = null, comparisonSelected = '';
let showAllOutputs = loadAllOutputs();
get('show-all-outputs').checked = showAllOutputs;
const renderedOutputRows = new Map();
const isCompare = () => interfaceMode === 'compare';
const selectedCompilers = () => compareNames.filter(name => get(`compare-${name}`).checked && availableCompilers.includes(name));
let availableCompilers = [], compilationFailed = false;
const additionalByCompiler = {};
let additionalCompiler = 'gfortran';
function selectedOptions() {
  return {preset: get('preset').value, standard: get('standard').value,
    warnings: Boolean(get('warnings').checked), fast_math: Boolean(get('fast-math').checked),
    ...(get('preprocess').checked ? {preprocess: true} : {}),
    ...(Number(get('images').value) ? {images: Number(get('images').value)} : {}),
    ...(get('additional-options').value.trim() ? {additional: optionTokens(get('additional-options').value)} : {})};
}
const isSimple = () => interfaceMode === 'simple';
function resetSimpleSettings() {
  const changed = get('compiler').value !== 'gfortran' || get('standard').value !== 'default' ||
    get('preset').value !== 'default' || get('warnings').checked || get('fast-math').checked || get('preprocess').checked || get('additional-options').value.trim() || Number(get('images').value) || hasExternal();
  clearExternal();
  get('compiler').value = 'gfortran';
  get('standard').value = 'default';
  get('preset').value = 'default';
  get('warnings').checked = false;
  get('fast-math').checked = false;
  get('preprocess').checked = false;
  get('images').value = '0';
  get('additional-options').value = '';
  for (const name of Object.keys(additionalByCompiler)) delete additionalByCompiler[name];
  return changed;
}
function invalidateBuild() {
  retained = null;
  clearTimeout(expiryTimer);
}
const editor = createEditor(get('fortran'), get('fortran-lines'), () => {
  revision++;
  invalidateBuild();
  clearErrorInfo();
  get('freshness').textContent = 'Input changed; previous results are retained.';
  controls();
});
let indentation = loadIndentation();
get('indent-width').value = String(indentation.width);
get('auto-indent').checked = indentation.automatic;
editor.setIndentation(indentation);

const quickFix = createQuickFixControls({editor, button: get('fix-error'),
  note: get('fix-note'), config: playgroundConfig,
  onApplied(fix) { get('status').textContent = `Fixed: ${fix.description} Compile when ready.`; },
});

function clearErrorInfo() {
  quickFix.clear();
  editor.clearDiagnostics();
  get('first-error').disabled = true;
  get('first-error').hidden = true;
  get('error-note').textContent = '';
  get('error-note').hidden = true;
}

function controls() {
  if (isSimple()) resetSimpleSettings();
  if (additionalCompiler !== get('compiler').value) {
    additionalCompiler = get('compiler').value;
    get('additional-options').value = additionalByCompiler[additionalCompiler] || '';
  }
  const busy = Boolean(active) || externalLoading;
  get('external-controls').hidden = isSimple();
  externalRows.forEach((row, index) => {
    const element = row.element;
    element('external-row').hidden = index >= externalCount;
    element('external-url').disabled = busy || connecting;
    element('load-external').disabled = busy || connecting || !token || !features.external_source || !element('external-url').value.trim();
    element('remove-external').disabled = busy || connecting || (externalCount === 1 && !(row.source || element('external-url').value));
    element('add-external').hidden = index !== externalCount - 1;
    element('add-external').disabled = busy || connecting || externalCount >= 5;
    element('external-preview').hidden = !row.source;
    element('external-status').textContent = row.message || (row.source ?
      `${row.source.filename} loaded from ${row.source.url}; SHA-256 ${row.source.sha256}. Load refreshes this snapshot.` :
      features.external_source ? '' : 'External source loading requires an updated execution service.');
  });
  get('external-summary').textContent = externalError();
  const interpreted = !isCompare() && get('compiler').value === 'ofort';
  get('compile').textContent = interpreted ? 'Check syntax' : 'Compile';
  get('run').textContent = isSimple() || interpreted ? 'Run' : 'Compile and Run';
  quickFix.setBusy(busy);
  const preprocessingUnavailable = get('preprocess').checked && !catalog[get('compiler').value]?.extras?.preprocess;
  get('run').disabled = !token || busy || !editor.getValue().trim() || (isCompare() ? !selectedCompilers().length : !availableCompilers.includes(get('compiler').value) || preprocessingUnavailable);
  get('interface-mode').value = interfaceMode;
  get('interface-mode').disabled = busy || connecting;
  get('advanced-options').disabled = busy || connecting;
  for (const id of ['compiler-controls', 'option-controls', 'compiler-version', 'standard-note',
    'options-note', 'additional-options-help', 'coarray-note', 'build-note', 'connection', 'check', 'compile', 'rerun', 'quick-fix-controls', 'quick-fix-details', 'advanced-help']) {
    get(id).hidden = isSimple();
  }
  for (const id of ['simple-compiler', 'advanced-options', 'simple-help']) get(id).hidden = !isSimple();
  get('simple-compiler').textContent = token && !availableCompilers.includes('gfortran') ?
    'GNU Fortran unavailable. Choose Advanced options to select another compiler.' : 'GNU Fortran';
  get('compilation-pane').hidden = isSimple() && !compilationFailed;
  get('compile').disabled = get('run').disabled || !features.compile_only;
  const sourceToolsUnavailable = isCompare() ? !token || busy || !editor.getValue().trim() : get('run').disabled;
  get('format').disabled = sourceToolsUnavailable || !features.format || !editor.undoableClear;
  const formatWidthSupported = indentation.width === 3 || features.format_indents?.includes(indentation.width);
  if (!formatWidthSupported) get('format').disabled = true;
  get('indent-note').textContent = formatWidthSupported ? 'Preferences are saved in this browser. Format uses the selected width.' : 'Auto-indent works with this width. Format requires an updated service to use it.';
  get('indent-width').disabled = busy || connecting;
  get('auto-indent').disabled = busy || connecting;
  get('check').disabled = sourceToolsUnavailable || !features.check;
  get('rerun').hidden = isSimple() || isCompare();
  get('rerun').disabled = isCompare() || interpreted || !token || busy || !features.run_again || !retained || retained.expires_at * 1000 <= Date.now();
  get('build-note').textContent = !features.compile_only ? 'Compile-only and Run Again require an updated execution service.' : retained ? 'Run Again reuses this executable until it expires (up to five minutes). Editing source or options requires recompilation.' : 'Compile to enable Run Again. Each run starts a fresh process.';
  if (interpreted) get('build-note').textContent = 'ofort checks syntax or interprets standalone source. Run starts a fresh process each time; no executable or compiled helpers are used.';
  get('stop').disabled = !active || active.stopping;
  for (const id of ['stdin', 'load-stdin', 'stdin-file']) get(id).disabled = busy || connecting;
  const inputError = stdinError();
  get('stdin-status').textContent = inputError || 'Changing input keeps the compiled program available for Run Again.';
  if (inputError) for (const id of ['run', 'rerun']) get(id).disabled = true;
  get('connect').disabled = connecting || busy;
  get('compiler').disabled = !token || busy;
  get('download').disabled = !editor.getValue().trim();
  get('share').disabled = !editor.getValue().trim();
  get('share-state').disabled = busy || connecting;
  const spec = catalog[get('compiler').value];
  const specs = isCompare() ? availableCompilers.map(name => catalog[name]).filter(Boolean) : [spec];
  const supports = predicate => specs.some(item => item && predicate(item));
  for (const option of get('standard').options) option.disabled = option.value !== 'default' && !supports(item => item.standards?.[option.value]);
  if (!preserveStateOptions && get('standard').value !== 'default' && !supports(item => item.standards?.[get('standard').value])) get('standard').value = 'default';
  get('standard').disabled = !token || busy || (!supports(item => Object.keys(item.standards || {}).length)
    && !(preserveStateOptions && get('standard').value !== 'default'));
  get('standard-note').textContent = `Standard selection applies only to user code. ${spec?.standard_note || 'Standard selection is unavailable from this service.'}`;
  for (const option of get('compiler').options) option.title = compilerVersions[option.value] || 'Version unavailable';
  get('compiler-version').textContent = `${interpreted ? 'Interpreter' : 'Compiler'} version: ${compilerVersions[get('compiler').value] || 'unavailable from this service.'}`;
  for (const option of get('preset').options) option.disabled = !supports(item => item.presets?.[option.value]);
  if (!preserveStateOptions && !supports(item => item.presets?.[get('preset').value])) get('preset').value = 'default';
  get('preset').disabled = interpreted || !token || busy || !spec;
  for (const [id, key] of [['warnings', 'warnings'], ['fast-math', 'fast_math']]) {
    if (!preserveStateOptions && !supports(item => item.extras?.[key])) get(id).checked = false;
    get(id).disabled = !token || busy || (!supports(item => item.extras?.[key]) && !(preserveStateOptions && get(id).checked));
  }
  // A shared link's request must not be silently ignored by an older service.
  get('preprocess').disabled = !token || busy || (!supports(item => item.extras?.preprocess) && !get('preprocess').checked);
  for (const option of get('images').options) option.disabled = option.value !== '0' && !supports(item => item.coarray_images?.[option.value]);
  get('images').disabled = !token || busy || (!supports(item => Object.keys(item.coarray_images || {}).length) && !Number(get('images').value));
  get('coarray-note').textContent = (spec?.coarray_note || 'Only sandbox-verified coarray image counts are offered.') +
    ' All images run in one sandbox and count as one job. Output order may vary; CPU limits still apply.';
  const choices = Object.values(spec?.additional_options || {}).flat();
  get('additional-options').disabled = !token || busy || get('compiler').value === 'ofort' || (!choices.length && !get('additional-options').value.trim());
  get('additional-options-help').textContent = choices.length ?
    `Supported additional options (separate arguments with spaces): ${choices.map(args => args.join(' ')).join('; ')}. Conflicting settings are rejected.` :
    'Additional options are unavailable for this compiler/service.';
  let flags = [], optionError = '';
  try { flags = compilerArguments(spec, selectedOptions(), optionTokens(get('additional-options').value)); }
  catch (error) { optionError = error.message; }
  get('options-error').textContent = optionError;
  get('options-error').hidden = isSimple() || !optionError;
  if (optionError && !isCompare()) {
    get('run').disabled = true;
    get('compile').disabled = true;
    get('rerun').disabled = true;
  }
  const fastMath = flags.includes('-ffast-math') || flags.includes('--fast') ||
    flags.some((arg, index) => arg === '-fp-model' && flags[index + 1] === 'fast');
  get('options-note').textContent = optionError ? 'Resolve compiler options before compiling.' :
    `User-code flags: ${flags.join(' ') || '(compiler default)'}. Helpers keep fixed build options.${fastMath ? ' Fast math can change numerical results.' : ''}`;
  if (interpreted) get('options-note').textContent = 'ofort default checks are enabled, including reads of uninitialized variables. Unsupported language features may be rejected.';
  if (preprocessingUnavailable) get('options-note').textContent += ' Preprocessing is requested but unavailable for this compiler/service. Choose a supported compiler or turn preprocessing off.';
  const ownerKey = get('owner-key').value;
  const ownerError = ownerKey && (!features.owner_access ? 'Owner access is not configured on this service. Clear the key to use public access.' :
    !/^[A-Za-z0-9_-]{32,256}$/.test(ownerKey) ? 'Enter the complete owner key (32 to 256 letters, digits, underscores, or hyphens), or clear it to use public access.' : '');
  get('owner-access').hidden = !ownerAccessRequested || (!features.owner_access && !ownerKey);
  get('owner-key').disabled = busy || connecting;
  get('clear-owner-key').disabled = busy || connecting || !ownerKey;
  get('owner-status').textContent = ownerError || (ownerKey ?
    'Owner key will be verified when you submit a job. Valid owner requests bypass daily and address quotas; concurrency limits still apply.' :
    'Optional owner access. The key is kept only in this page and is not included in share links.');
  if (ownerError) for (const id of ['run', 'compile', 'rerun', 'format', 'check']) get(id).disabled = true;
  comparisonControls(busy);
  if (externalError()) for (const id of ['run', 'compile', 'rerun', 'share', 'download']) get(id).disabled = true;
}

function currentComparisonPlan() {
  return comparisonPlan(selectedCompilers(), catalog, selectedOptions(), additionalByCompiler);
}

function comparisonControls(busy) {
  get('comparison-controls').hidden = !isCompare();
  get('comparison-results').hidden = !isCompare() || !comparisonSnapshot;
  get('compiler-label').textContent = isCompare() ? 'Options for' : 'Compiler';
  get('compare-all').disabled = busy || connecting || !token;
  get('compare-stop-failure').disabled = busy || connecting;
  const plan = isCompare() ? currentComparisonPlan() : [];
  for (const name of compareNames) {
    get(`compare-${name}`).disabled = busy || connecting || !token || !availableCompilers.includes(name);
    get(`compare-note-${name}`).textContent = !availableCompilers.includes(name) ? 'Unavailable on this service.' :
      plan.find(item => item.compiler === name)?.reason || compilerVersions[name] || '';
  }
  const jobs = plan.filter(item => !item.reason).length;
  get('compare-job-count').textContent = `${jobs} compiler job${jobs === 1 ? '' : 's'} will be submitted${plan.length > jobs ? `; ${plan.length - jobs} skipped for unsupported settings` : ''}.`;
  get('compare-action-count').hidden = !isCompare();
  get('compare-action-count').textContent = `${jobs} compiler job${jobs === 1 ? '' : 's'}`;
  if (isCompare()) {
    get('standard-note').textContent = 'Shared standard and preset selections apply to all checked compilers. Unsupported settings skip that compiler; defaults are never substituted silently.';
    get('build-note').textContent = 'Compile and Compile and Run compare the checked compilers sequentially. Run Again is available in Advanced mode.';
    get('options-note').textContent = 'Common settings apply to all checked compilers; additional options apply only to Options for. See each compiler above for incompatible settings.';
    if (comparisonSnapshot && comparisonSnapshot.revision !== revision) {
      get('comparison-detail').textContent = 'Source or settings have changed since this comparison; the table and logs retain earlier results.';
    }
  }
  comparisonLayout();
}

function comparisonLayout() {
  const all = isCompare() && showAllOutputs && Boolean(comparisonSnapshot);
  get('all-comparison-outputs').hidden = !all;
  get('program-output-pane').hidden = all;
  get('plot-results').hidden = all;
  get('compilation-pane').hidden = all || (isSimple() && !compilationFailed);
  const fullEditor = all && get('checks-pane').hidden;
  get('results-pane').hidden = fullEditor;
  get('workspace').setAttribute('class', fullEditor ? 'workspace comparison-full-editor' : 'workspace');
  get('copy-comparison').disabled = !comparisonSnapshot || !comparisonRows.some(row => !['QUEUED', 'RUNNING'].includes(row.status));
}

function renderComparison() {
  outputComparison.update(comparisonRows);
  get('comparison-results').hidden = !isCompare() || !comparisonSnapshot;
  for (const name of compareNames) {
    const row = comparisonRows.find(item => item.compiler === name);
    get(`compare-row-${name}`).hidden = !row;
    get(`compare-view-${name}`).disabled = !row || ['QUEUED', 'RUNNING'].includes(row.status);
    get(`compare-view-${name}`).setAttribute('aria-pressed', String(name === comparisonSelected));
    get(`compare-output-${name}`).hidden = !row;
    if (!row) renderedOutputRows.delete(name);
    if (!row) continue;
    get(`compare-result-${name}`).textContent = row.status;
    for (const field of ['total', 'compile', 'run', 'other']) {
      const seconds = row.times?.[field];
      get(`compare-${field}-${name}`).textContent = Number.isFinite(seconds) ? seconds.toFixed(3) : '-';
    }
    get(`compare-reason-${name}`).textContent = row.reason || '';
    if (renderedOutputRows.get(name) !== row) {
      const output = comparisonOutput(row, comparisonSnapshot.mode);
      for (const field of ['title', 'version', 'reason', 'stdout', 'stderr', 'build']) {
        get(`compare-output-${field}-${name}`).textContent = output[field];
      }
      get(`compare-output-stderr-section-${name}`).hidden = !output.stderr;
      get(`compare-output-build-error-${name}`).textContent = output.buildError;
      get(`compare-output-build-error-section-${name}`).hidden = !output.buildError;
      get(`compare-output-build-details-${name}`).open = output.failed;
      const plots = get(`compare-output-plots-${name}`);
      plots.replaceChildren(); renderPlots(plots, row.result);
      renderedOutputRows.set(name, row);
    }
  }
  comparisonLayout();
}

function viewComparison(name) {
  const row = comparisonRows.find(item => item.compiler === name);
  if (!row || ['QUEUED', 'RUNNING'].includes(row.status)) return;
  comparisonSelected = name;
  const current = comparisonSnapshot.revision === revision;
  if (row.result) show(row.result, comparisonSnapshot.compilation, false, current);
  else {
    clearErrorInfo();
    get('diagnostics').textContent = row.reason || row.status;
    get('output').textContent = 'Not run.';
    for (const id of ['build-time', 'run-time', 'result-compiler-version']) get(id).textContent = '';
  }
  invalidateBuild();
  get('comparison-detail').textContent = `Showing ${name}: ${row.status}.${current ? '' : ' Source or settings have changed since this comparison; these are earlier results.'}`;
  get('freshness').textContent = current ? 'Comparison results for the submitted source snapshot and settings.' : 'Comparison results are retained from an earlier source snapshot or settings.';
  renderComparison();
}

async function runComparison(mode) {
  if (!isCompare() || !token || active || connecting || externalLoading || !selectedCompilers().length) return;
  if (mode === 'fortran-compile' && !features.compile_only) return;
  if (externalError()) { get('status').textContent = externalError(); return; }
  if (mode === 'fortran-edit' && stdinError()) { get('status').textContent = stdinError(); return; }
  const ownerKey = get('owner-key').value;
  if (ownerKey && (!features.owner_access || !/^[A-Za-z0-9_-]{32,256}$/.test(ownerKey))) {
    get('status').textContent = 'Enter a valid owner key for this service, or clear it to use public access.'; return;
  }
  if (!editor.getValue().trim()) return;
  let compilation;
  try { compilation = combinedSource(editor.getValue(), loadedSources()); }
  catch (error) { get('status').textContent = error.message; return; }
  const plan = currentComparisonPlan().map(item => ({...item, version: compilerVersions[item.compiler],
    flags: item.reason ? [] : compilerArguments(catalog[item.compiler], item.options, item.options.additional)}));
  const stdin = get('stdin').value;
  const stopOnFailure = Boolean(get('compare-stop-failure').checked);
  const batch = active = {id: null, stopping: false, cancelled: new Set()};
  batch.cancel = async id => {
    if (!batch.cancelled.has(id)) {
      batch.cancelled.add(id);
      try { await api(`jobs/${id}/cancel`, 'POST', {}); }
      catch (error) { batch.cancelled.delete(id); throw error; }
    }
  };
  comparisonSnapshot = {compilation, revision, mode}; comparisonSelected = '';
  comparisonRows = plan.map(item => ({...item, status: 'QUEUED'}));
  invalidateBuild(); clearErrorInfo();
  get('comparison-detail').textContent = '';
  get('comparison-copy-field').hidden = true;
  get('comparison-copy-text').value = '';
  get('comparison-copy-status').textContent = '';
  get('comparison-status').textContent = 'Comparing compilers...';
  renderComparison(); controls();
  try {
    await executeComparison({plan, stopOnFailure, stopped: () => batch.stopping,
      cancel: batch.cancel,
      submit: async item => {
        batch.id = null;
        const created = await api('jobs', 'POST', {source: '', mode, automatic: false,
          fortran_source: compilation.source, compiler: item.compiler, compiler_options: item.options,
          ...(mode === 'fortran-edit' && stdin ? {stdin} : {})});
        batch.id = created.id;
        return created;
      },
      poll: id => api(`jobs/${id}`),
      update: row => {
        comparisonRows[comparisonRows.findIndex(item => item.compiler === row.compiler)] = row;
        if (row.status === 'RUNNING') get('status').textContent = `Comparing: ${row.compiler}...`;
        if (row.result && !comparisonSelected) viewComparison(row.compiler);
        renderComparison();
      },
    });
  } finally {
    active = null; invalidateBuild();
    const counts = ['PASS', 'FAIL', 'ERROR', 'STOPPED', 'SKIP'].map(status => {
      const count = comparisonRows.filter(row => row.status === status).length;
      return count ? `${count} ${status}` : '';
    }).filter(Boolean).join(', ');
    get('status').textContent = batch.stopping ? 'Comparison stopped' : 'Comparison finished';
    get('comparison-status').textContent = counts + '. Results use the source and settings captured when the comparison started.';
    controls(); renderComparison();
  }
}

async function api(path, method = 'GET', payload) {
  const response = await fetch(`${service}/api/${path}`, {
    method, cache: 'no-store', signal: AbortSignal.timeout(30000),
    headers: {'X-P2F-Token': token, ...(payload === undefined ? {} : {'Content-Type': 'application/json'}),
      ...(path === 'jobs' && method === 'POST' && get('owner-key').value ? {'X-P2F-Owner-Key': get('owner-key').value} : {})},
    ...(payload === undefined ? {} : {body: JSON.stringify(payload)}),
  });
  const result = await response.json();
  if (!response.ok) {
    const error = new Error(result.error || `Service returned ${response.status}`);
    error.status = response.status;
    throw error;
  }
  return result;
}

async function connect() {
  if (active || connecting) return;
  connecting = true; token = ''; features = {}; compilerVersions = {}; invalidateBuild(); quickFix.clear(); controls();
  try {
    const response = await fetch('./service.json', {cache: 'no-store'});
    if (!response.ok) throw new Error('Execution service configuration is unavailable.');
    const config = await response.json();
    service = serviceOrigin(config.url);
    const session = await api('session');
    if (!session.token) throw new Error('The service did not provide a session token.');
    const compilers = session.compilers || ['gfortran'];
    for (const option of get('compiler').options) option.disabled = !compilers.includes(option.value);
    availableCompilers = compilers;
    if (!isSimple() && !compilers.includes(get('compiler').value)) {
      const supported = [...get('compiler').options].find(option => !option.disabled);
      if (!supported) throw new Error('No supported compiler is available.');
      get('compiler').value = supported.value;
    }
    token = session.token;
    catalog = session.compiler_options || {};
    compilerVersions = session.compiler_versions || {};
    features = session.features || {};
    applyURLServiceSettings();
    get('connection').textContent = `Connected · ${compilers.join(' / ')} · ${session.timeout ?? '?'} s run limit · runtime ${(session.commit || '').slice(0,7)}`;
    get('status').textContent = 'Ready';
    // No transpiler pin is needed: this site submits only edited Fortran.
  } catch (error) {
    compilationFailed = true;
    get('connection').textContent = 'Execution service unavailable. Editing and downloading still work; try Reconnect.';
    get('diagnostics').textContent = String(error);
    get('status').textContent = 'Not connected';
  } finally { connecting = false; controls(); }
}

function show(result, compilation = combinedSource(editor.getValue(), null), allowFix = true, sourceCurrent = true) {
  get('plot-results').replaceChildren(); renderPlots(get('plot-results'), result);
  compilationFailed = result.build?.ok === false || result.ok === false || Boolean(result.error);
  get('build-title').textContent = result.interpreter ? (result.build ? 'Syntax checking' : 'Interpreter diagnostics') : 'Compilation';
  const version = result.compiler_version;
  get('result-compiler-version').hidden = !(result.build || result.reused_executable || (result.interpreter && result.execution));
  get('result-compiler-version').textContent = `${result.interpreter ? 'Interpreter' : 'Compiler'} version: ${version || 'unavailable from this service.'}`;
  const diagnosticStage = result.build || (result.interpreter ? result.execution : null);
  if (diagnosticStage) {
    const parsed = parseCompilerErrors(`${diagnosticStage.stdout || ''}\n${diagnosticStage.stderr || ''}`, compilation.source);
    const {main: errors, external: externalErrors} = mappedErrors(parsed, compilation);
    clearErrorInfo();
    editor.setDiagnostics(sourceCurrent ? errors : []);
    get('first-error').disabled = !sourceCurrent || !errors.length;
    get('first-error').hidden = !sourceCurrent || !errors.length;
    get('error-note').hidden = !(errors.length || externalErrors.length);
    get('error-note').textContent = externalErrors.length ? `External source ${externalErrors[0].filename}, line ${externalErrors[0].line}: ${externalErrors[0].message}` :
      errors.length ? `${errors.length} source error${errors.length === 1 ? '' : 's'}; first at line ${errors[0].line}: ${errors[0].message}` : '';
    if (allowFix && !compilation.mainOffset) quickFix.update(editor.getValue(), `${diagnosticStage.stdout || ''}\n${diagnosticStage.stderr || ''}`,
      result.compiler || get('compiler').value, diagnosticStage.ok === false);
  }
  for (const [key, outputId, timeId] of [['build', 'diagnostics', 'build-time'], ['execution', 'output', 'run-time']]) {
    const stage = result[key];
    get(outputId).textContent = stage ? `${stage.stdout || ''}${stage.stderr ? '\n' + stage.stderr : ''}` || '(No output)' : 'Not run for this operation.';
    get(timeId).textContent = stage ? `${Number(stage.seconds || 0).toFixed(2)} s` : '';
  }
  if (result.interpreter && !result.build && result.execution) {
    get('diagnostics').textContent = result.execution.stderr || 'No separate syntax check: ofort parses and runs source directly with --fast.';
  }
  if (result.error) get('diagnostics').textContent = result.error;
  if (compilation.mainOffset && diagnosticStage) {
    const mapped = mappedErrors(parseCompilerErrors(`${diagnosticStage.stdout || ''}\n${diagnosticStage.stderr || ''}`, compilation.source), compilation);
    for (const error of mapped.main) get('diagnostics').textContent += `\nSource location: editor main.f90:${error.line}`;
    for (const error of mapped.external) get('diagnostics').textContent += `\nSource location: ${error.filename}:${error.line} (${error.url})`;
  }
  if (result.reused_executable) get('diagnostics').textContent = 'Compilation skipped — reused the retained executable.';
  if (result.artifact_note) get('diagnostics').textContent += '\n' + result.artifact_note;
  if (result.artifact) {
    retained = result.artifact;
    clearTimeout(expiryTimer);
    expiryTimer = setTimeout(() => { invalidateBuild(); controls(); }, Math.max(0, retained.expires_at * 1000 - Date.now()));
    expiryTimer.unref?.();
  }
  get('status').textContent = `${result.ok ? 'Completed' : 'Failed'} · ${result.compiler || get('compiler').value} · ${Number(result.seconds || 0).toFixed(2)} s total`;
  get('freshness').textContent = 'Results for the submitted source and options. Program time includes process startup; compilation is shown separately.';
}

async function run(mode = 'fortran-edit') {
  if (!token || active || externalLoading) return;
  if (get('owner-key').value && (!features.owner_access || !/^[A-Za-z0-9_-]{32,256}$/.test(get('owner-key').value))) {
    get('status').textContent = 'Enter a valid owner key for this service, or clear it to use public access.';
    return;
  }
  if (isSimple()) {
    resetSimpleSettings();
    if (!availableCompilers.includes('gfortran') || !['fortran-edit', 'format'].includes(mode)) return;
  }
  if (!['format', 'check'].includes(mode) && !availableCompilers.includes(get('compiler').value)) return;
  if (!['format', 'check'].includes(mode) && get('preprocess').checked && !catalog[get('compiler').value]?.extras?.preprocess) return;
  if (!['format', 'check'].includes(mode)) {
    try { compilerArguments(catalog[get('compiler').value], selectedOptions(), optionTokens(get('additional-options').value)); }
    catch (error) { get('status').textContent = error.message; return; }
  }
  if (mode === 'fortran-compile' && !features.compile_only) return;
  if (mode === 'format' && (!features.format || !editor.undoableClear)) return;
  if (mode === 'format' && indentation.width !== 3 && !features.format_indents?.includes(indentation.width)) return;
  if (mode === 'check' && !features.check) return;
  if (mode === 'fortran-run' && (!features.run_again || !retained || retained.expires_at * 1000 <= Date.now())) { invalidateBuild(); controls(); return; }
  const source = editor.getValue();
  if (!['format', 'check'].includes(mode) && externalError()) { get('status').textContent = externalError(); return; }
  let compilation;
  try { compilation = combinedSource(source, loadedSources()); }
  catch (error) {
    if (!['format', 'check'].includes(mode)) { get('status').textContent = error.message; return; }
  }
  const executes = ['fortran-edit', 'fortran-run'].includes(mode);
  if (executes && stdinError()) { get('status').textContent = stdinError(); return; }
  if (!source.trim() || new TextEncoder().encode(source).length > 100000) {
    get('status').textContent = 'Enter between 1 byte and 100 KB of Fortran.'; return;
  }
  const job = active = {id: null, revision, stopping: false, compilation};
  if (mode === 'check') {
    get('checks-pane').hidden = false;
    get('check').setAttribute('aria-expanded', 'true');
    get('check-status').textContent = 'Checking with Fortitude…';
  }
  const artifactId = retained?.id;
  if (!['fortran-run', 'check'].includes(mode)) { invalidateBuild(); clearErrorInfo(); }
  controls(); get('status').textContent = mode === 'check' ? 'Checking with Fortitude…' : mode === 'format' ? 'Formatting…' : mode === 'fortran-run' ? 'Running retained build…' : mode === 'fortran-compile' ? 'Compiling…' : 'Compiling and running…';
  if (get('compiler').value === 'ofort' && !['format', 'check'].includes(mode)) {
    get('status').textContent = mode === 'fortran-compile' ? 'Checking syntax…' : 'Interpreting…';
  }
  try {
    const created = await api('jobs', 'POST', {
      source: ['format', 'check'].includes(mode) ? source : '', mode, automatic: false,
      ...(mode === 'format' && features.format_indents?.includes(indentation.width) ? {format_indent: indentation.width} : {}),
      ...(executes && get('stdin').value ? {stdin: get('stdin').value} : {}),
      ...(['format', 'check'].includes(mode) ? {} : mode === 'fortran-run' ? {artifact_id: artifactId} : {fortran_source: compilation.source, ...(features.run_again && !isSimple() && get('compiler').value !== 'ofort' ? {retain_executable: true} : {})}),
      compiler: ['format', 'check'].includes(mode) ? 'gfortran' : get('compiler').value,
      ...(!['format', 'check'].includes(mode) && catalog[get('compiler').value] ? {compiler_options: {
        preset: get('preset').value, warnings: Boolean(get('warnings').checked), fast_math: Boolean(get('fast-math').checked),
        ...(get('preprocess').checked ? {preprocess: true} : {}),
        ...(Number(get('images').value) ? {images: Number(get('images').value)} : {}),
        ...(get('additional-options').value.trim() ? {additional: optionTokens(get('additional-options').value)} : {}),
        ...(catalog[get('compiler').value]?.standards ? {standard: get('standard').value} : {}),
      }} : {}),
    });
    job.id = created.id;
    if (job.stopping) await api(`jobs/${job.id}/cancel`, 'POST', {});
    const deadline = Date.now() + 300000;
    while (active === job) {
      const state = await api(`jobs/${job.id}`);
      if (state.state === 'done') {
        if (job.stopping) {
          get('status').textContent = 'Stopped';
          if (mode === 'check') get('check-status').textContent = 'Check stopped; previous results are retained.';
        }
        else if (revision === job.revision && mode === 'check') {
          const result = state.result;
          get('check-status').textContent = '';
          get('checks').textContent = result.error || `${result.checking?.stdout || ''}${result.checking?.stderr || ''}` || 'No findings.';
          get('check-time').textContent = `${Number(result.seconds || 0).toFixed(2)} s`;
          get('status').textContent = !result.ok ? 'Fortitude check failed; source unchanged' : result.findings ? 'Fortitude reported issues; source unchanged' : 'Fortitude check passed; source unchanged';
          get('freshness').textContent = 'Fortitude results for the submitted source. Compilation and program output are retained.';
        }
        else if (revision === job.revision && mode === 'format') {
          const result = state.result;
          try {
            const changed = applyFormatting(editor, source, result);
            get('status').textContent = `Formatted with fprettify · ${Number(result.seconds || 0).toFixed(2)} s. Ctrl+Z to undo.`;
            if (!changed) get('status').textContent = 'Already formatted; source unchanged.';
          } catch (error) {
            compilationFailed = true;
            get('status').textContent = 'Formatting failed; source unchanged';
            get('diagnostics').textContent = String(error);
          }
        }
        else if (revision === job.revision) show(state.result, job.compilation);
        else {
          get('status').textContent = 'Previous result discarded — source or options changed';
          if (mode === 'check') get('check-status').textContent = 'Check result discarded because source or options changed; previous results are retained.';
        }
        break;
      }
      if (Date.now() > deadline) throw new Error('Job response timed out. Try Reconnect.');
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  } catch (error) {
    if (mode !== 'check') compilationFailed = true;
    if (mode === 'fortran-run' && error.status === 404) invalidateBuild();
    if (job.id) api(`jobs/${job.id}/cancel`, 'POST', {}).catch(() => {});
    if (mode === 'check') get('check-status').textContent = `Fortitude check failed: ${error}`;
    else get('diagnostics').textContent = String(error);
    get('status').textContent = 'Execution request failed';
    if (!error.status || error.status === 401 || error.status === 403) token = '';
  } finally { active = null; controls(); }
}

function changeInterface(mode) {
  if (active || connecting || externalLoading) { get('interface-mode').value = interfaceMode; return; }
  interfaceMode = ['simple', 'compare'].includes(mode) ? mode : 'advanced';
  invalidateBuild(); clearErrorInfo();
  let settingsChanged = false;
  if (isSimple()) {
    settingsChanged = resetSimpleSettings();
    get('checks-pane').hidden = true;
    get('check').setAttribute('aria-expanded', 'false');
  } else if (token && availableCompilers.length && !availableCompilers.includes(get('compiler').value)) {
    get('compiler').value = availableCompilers[0];
    settingsChanged = true;
  }
  if (settingsChanged) {
    invalidateBuild();
    clearErrorInfo();
    revision++;
  }
  controls();
  editor.refresh();
  get('interface-mode').focus();
}
get('interface-mode').onchange = () => changeInterface(get('interface-mode').value);
get('advanced-options').onclick = () => changeInterface('advanced');
get('run').onclick = () => isCompare() ? runComparison('fortran-edit') : run();
for (const name of compareNames) {
  get(`compare-${name}`).onchange = controls;
  get(`compare-view-${name}`).onclick = () => viewComparison(name);
}
get('compare-all').onclick = () => {
  if (active || connecting || externalLoading) return;
  for (const name of compareNames) get(`compare-${name}`).checked = availableCompilers.includes(name);
  controls();
};
get('show-all-outputs').onchange = () => {
  showAllOutputs = Boolean(get('show-all-outputs').checked);
  saveAllOutputs(showAllOutputs);
  renderComparison();
};
get('copy-comparison').onclick = async () => {
  if (!comparisonSnapshot) return;
  const report = comparisonReport(comparisonRows, comparisonSnapshot, comparisonSnapshot.revision !== revision) + outputComparison.report();
  get('comparison-copy-field').hidden = true;
  get('comparison-copy-text').value = report;
  try {
    await navigator.clipboard.writeText(report);
    get('comparison-copy-status').textContent = 'Comparison results copied.';
  } catch {
    get('comparison-copy-field').hidden = false;
    get('comparison-copy-text').focus();
    get('comparison-copy-text').select();
    get('comparison-copy-status').textContent = 'Copy the selected comparison results.';
  }
};
get('compile').onclick = () => isCompare() ? runComparison('fortran-compile') : run('fortran-compile');
get('format').onclick = () => run('format');
for (const id of ['indent-width', 'auto-indent']) get(id).onchange = () => {
  indentation = {width: Number(get('indent-width').value), automatic: Boolean(get('auto-indent').checked)};
  editor.setIndentation(indentation);
  saveIndentation(undefined, indentation);
  controls();
};
get('check').onclick = () => run('check');
get('hide-checks').onclick = () => {
  get('checks-pane').hidden = true;
  get('check').setAttribute('aria-expanded', 'false');
  if (get('check').disabled) editor.focus();
  else get('check').focus();
  controls();
};
get('rerun').onclick = () => run('fortran-run');
get('first-error').onclick = () => editor.goToDiagnostic();
get('connect').onclick = connect;
get('owner-key').oninput = controls;
function externalChanged() {
  invalidateBuild(); clearErrorInfo(); revision++; controls();
}
externalRows.forEach((row, index) => {
  const element = row.element;
  element('external-url').oninput = () => {
    row.source = null; row.message = ''; element('external-source').value = '';
    externalChanged();
  };
  element('add-external').onclick = () => {
    if (active || connecting || externalLoading || externalCount >= 5) return;
    externalCount++; controls();
    externalRows[externalCount - 1].element('external-url').focus();
  };
  element('remove-external').onclick = () => {
    if (active || connecting || externalLoading) return;
    for (let i = index; i < externalCount - 1; i++) {
      const target = externalRows[i], next = externalRows[i + 1];
      target.source = next.source; target.message = next.message;
      target.element('external-url').value = next.element('external-url').value;
      target.element('external-source').value = next.element('external-source').value;
      target.element('external-preview').open = false;
    }
    resetExternalRow(externalRows[externalCount - 1]);
    externalCount = Math.max(1, externalCount - 1);
    externalChanged();
  };
  element('load-external').onclick = async () => {
    if (active || connecting || externalLoading || !token || !features.external_source) return;
    let requested;
    try { requested = sourceURL(element('external-url').value); }
    catch (error) { row.message = error.message; controls(); return; }
    row.source = null; element('external-source').value = '';
    invalidateBuild(); clearErrorInfo(); revision++;
    externalLoading = true; row.message = 'Loading external source...'; controls();
    try {
      const loaded = await api('external-source', 'POST', {url: requested});
      if (typeof loaded.source !== 'string' || !loaded.source.trim() ||
          new TextEncoder().encode(loaded.source).length > 100000 ||
          typeof loaded.filename !== 'string' || !/^[A-Za-z0-9_.-]{1,100}$/.test(loaded.filename) ||
          typeof loaded.sha256 !== 'string' || !/^[a-f0-9]{64}$/.test(loaded.sha256)) throw new Error('The service returned invalid external source metadata.');
      sourceURL(loaded.url);
      if (isSimple() || sourceURL(element('external-url').value) !== requested) throw new Error('The URL changed while loading; load it again.');
      row.source = {...loaded, requestUrl: requested};
      element('external-source').value = loaded.source;
      row.message = ''; invalidateBuild(); clearErrorInfo(); revision++;
      get('status').textContent = `${loaded.filename} loaded. Compile when ready.`;
    } catch (error) { row.message = error.message; }
    finally { externalLoading = false; controls(); }
  };
});
get('stdin').oninput = () => {
  revision++;
  get('freshness').textContent = 'Program input changed; previous results are retained.';
  controls();
};
get('load-stdin').onclick = () => get('stdin-file').click();
get('stdin-file').onchange = async () => {
  const file = get('stdin-file').files?.[0];
  if (!file || active) return;
  const initialInput = get('stdin').value;
  try {
    if (file.size > 100003) throw new Error('Input file exceeds the 100 KB limit.');
    const bytes = await file.arrayBuffer();
    const text = new TextDecoder('utf-8', {fatal: true}).decode(bytes).replace(/\r\n?/g, '\n');
    if (new TextEncoder().encode(text).length > 100000) throw new Error('Program input exceeds the 100 KB limit.');
    if (active || ((initialInput || get('stdin').value !== initialInput) && !confirm('Replace the current program input with this file?'))) return;
    get('stdin').value = text;
    get('stdin').oninput();
  } catch (error) { get('stdin-status').textContent = String(error); }
  finally { get('stdin-file').value = ''; }
};
get('clear-owner-key').onclick = () => { get('owner-key').value = ''; controls(); };
get('stop').onclick = async () => {
  if (!active) return;
  active.stopping = true; controls(); get('status').textContent = 'Stopping…';
  try { if (active.id) await (active.cancel ? active.cancel(active.id) : api(`jobs/${active.id}/cancel`, 'POST', {})); }
  catch (error) { get('diagnostics').textContent = String(error); }
};
get('load').onclick = () => {
  if (!Object.hasOwn(examples, get('example').value)) return;
  if (editor.getValue().trim() && !confirm('Replace the Fortran input with this example?')) return;
  editor.setValue(examples[get('example').value], true); filename = 'main.f90'; editor.focus();
  const coarrays = examples[get('example').value].match(/^!\s*Coarray images:\s*([124])\s*$/m);
  if (coarrays) {
    changeInterface('advanced');
    get('compiler').value = 'gfortran';
    get('images').value = coarrays[1];
    invalidateBuild(); revision++; controls();
    get('status').textContent = 'Coarray example loaded. Select a verified image count and run when ready.';
  }
};
get('clear').onclick = () => {
  if (editor.getValue() && !editor.undoableClear && !confirm('Clear the Fortran input?')) return;
  editor.setValue('', true); editor.focus();
  for (const id of ['output', 'diagnostics', 'run-time', 'build-time', 'checks', 'check-time']) get(id).textContent = '';
  get('plot-results').replaceChildren();
  compilationFailed = false;
  controls();
  get('result-compiler-version').textContent = ''; get('result-compiler-version').hidden = true;
};
get('load-file').onclick = () => get('file').click();
get('file').onchange = async () => {
  const file = get('file').files?.[0];
  if (!file) return;
  const initialRevision = revision;
  try {
    if (file.size > 100000) throw new Error('File exceeds the 100 KB source limit.');
    const text = await file.text();
    if (new TextEncoder().encode(text).length > 100000) throw new Error('File exceeds the 100 KB source limit.');
    if (initialRevision !== revision || editor.getValue().trim()) {
      if (!confirm('Replace the current Fortran input with this file?')) return;
    }
    editor.setValue(text, true); filename = file.name; editor.focus();
    get('file-status').textContent = `${file.name} loaded locally. Loading does not execute code.`;
  } catch (error) { get('file-status').textContent = String(error); }
  finally { get('file').value = ''; }
};
get('download').onclick = () => {
  if (!editor.getValue().trim()) return;
  let source;
  try {
    if (externalError()) throw new Error(externalError());
    source = combinedSource(editor.getValue(), loadedSources()).source;
  } catch (error) { get('file-status').textContent = error.message; return; }
  const url = URL.createObjectURL(new Blob([source], {type: 'text/plain;charset=utf-8'}));
  const link = document.createElement('a');
  link.href = url; link.download = loadedSources().length ? 'playground_combined.f90' : filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
get('share').onclick = async () => {
  get('share-link-field').hidden = true;
  try {
    if (externalError()) throw new Error(externalError());
    const link = createShareLink(location.href, combinedSource(editor.getValue(), loadedSources()).source, interfaceMode, Boolean(get('preprocess').checked), Number(get('images').value));
    get('share-link').value = link;
    try {
      await navigator.clipboard.writeText(link);
      get('share-status').textContent = 'Share link copied. Anyone with the link can read the code; opening it does not run it.';
    } catch {
      get('share-link-field').hidden = false;
      get('share-link').focus();
      get('share-link').select();
      get('share-status').textContent = 'Copy the selected link. Anyone with the link can read the code; opening it does not run it.';
    }
    if (link.length > 8000) get('share-status').textContent += ' This long link may be truncated by some sites.';
  } catch (error) { get('share-status').textContent = String(error); }
};

get('share-state').onclick = async () => {
  get('share-state-field').hidden = true;
  try {
    const compilerOptions = {...additionalByCompiler, [get('compiler').value]: get('additional-options').value};
    const external = externalRows.slice(0, externalCount).map(row => ({url: row.element('external-url').value.trim(), source: row.source
      ? Object.fromEntries(['source', 'filename', 'url', 'requestUrl', 'sha256'].map(key => [key, row.source[key]])) : null}));
    await copyStateLink(location.href, captureState('fortran', get, editor.getValue(), {compilerOptions, external}), get);
  } catch (error) {get('share-state-status').textContent = error.message;}
};

function loadSharedState(initial = false) {
  try {
    const state = stateFromHash(location.hash, 'fortran');
    if (!state) return;
    if (active || connecting || externalLoading) throw new Error('Wait for the current operation to finish before restoring state.');
    if (!initial && !confirm('Replace the current playground code and settings with this state link?')) return;
    // A state snapshot takes precedence over settings-only query parameters.
    urlSettingsPending = false; sharedLinkLoaded = true; preserveStateOptions = true;
    clearExternal(); invalidateBuild(); clearErrorInfo();
    interfaceMode = state.values['interface-mode'] || 'advanced';
    const savedCompiler = state.values.compiler;
    if (savedCompiler && ![...get('compiler').options].some(o => o.value === savedCompiler)) {
      const option = document.createElement('option'); option.value = savedCompiler;
      option.textContent = `${savedCompiler} (unavailable)`; option.disabled = true; get('compiler').appendChild(option);
    }
    for (const [id, value] of Object.entries(state.values)) get(id).value = value;
    for (const [id, value] of Object.entries(state.checks)) get(id).checked = value;
    for (const name of Object.keys(additionalByCompiler)) delete additionalByCompiler[name];
    Object.assign(additionalByCompiler, state.compilerOptions);
    additionalCompiler = get('compiler').value;
    get('additional-options').value = additionalByCompiler[additionalCompiler] || '';
    externalCount = Math.max(1, state.external.length);
    state.external.forEach((row, i) => {
      externalRows[i].element('external-url').value = row.url;
      externalRows[i].source = row.source;
      externalRows[i].message = row.source ? 'Snapshot restored from the state link; the URL was not downloaded again.' : '';
      externalRows[i].element('external-source').value = row.source?.source || '';
    });
    get('stdin').value = state.stdin;
    indentation = {width: Number(get('indent-width').value), automatic: Boolean(get('auto-indent').checked)};
    editor.setIndentation(indentation);
    showAllOutputs = Boolean(get('show-all-outputs').checked);
    comparisonRows = []; comparisonSnapshot = null; outputComparison.update([]);
    editor.setValue(state.source, !initial); filename = 'main.f90'; revision++; controls();
    const unavailable = !isSimple() && !availableCompilers.includes(get('compiler').value);
    const missing = compareNames.filter(name => state.checks[`compare-${name}`] && !availableCompilers.includes(name));
    const adjusted = ['warnings', 'fast-math'].filter(id => state.checks[id] && !get(id).checked);
    get('share-state-status').textContent = 'Playground state restored, including standard input. Choose Compile or Run when ready.'
      + (unavailable ? ' The saved compiler is unavailable on this service.' : '')
      + (isCompare() && missing.length ? ` Saved comparison compilers unavailable: ${missing.join(', ')}.` : '')
      + (adjusted.length ? ` Saved options unavailable: ${adjusted.join(', ')}.` : '');
  } catch (error) {get('share-state-status').textContent = error.message;}
}

function loadSharedCode(initial = false) {
  try {
    const shared = sharedCodeFromHash(location.hash);
    if (shared === null) return;
    const {source, interfaceMode: sharedMode, preprocess, images = 0} = shared;
    if (!hasExternal() && source === editor.getValue() && sharedMode === interfaceMode && preprocess === Boolean(get('preprocess').checked) && images === Number(get('images').value)) {
      sharedLinkLoaded = true; return;
    }
    if (active || connecting || externalLoading) throw new Error('Wait for the current operation to finish before opening shared code.');
    if (!initial && editor.getValue().trim() && !confirm('Replace the Fortran input with code from this shared link?')) {
      get('share-status').textContent = 'Shared code was not loaded; your input is unchanged.';
      return;
    }
    preserveStateOptions = false;
    changeInterface(sharedMode);
    if (hasExternal()) {
      clearExternal(); invalidateBuild(); clearErrorInfo(); revision++; controls();
    }
    if (images !== Number(get('images').value)) {
      get('images').value = String(images);
      if (images) get('compiler').value = 'gfortran';
      invalidateBuild(); clearErrorInfo(); revision++; controls();
    }
    if (preprocess !== Boolean(get('preprocess').checked)) {
      get('preprocess').checked = preprocess;
      invalidateBuild(); clearErrorInfo(); revision++;
      controls();
    }
    if (source !== editor.getValue()) editor.setValue(source, !initial);
    filename = 'main.f90';
    sharedLinkLoaded = true;
    get('share-status').textContent = `Code loaded from a shared link. Choose ${isSimple() ? 'Run' : 'Compile or Compile and Run'} when ready.`;
  } catch (error) { get('share-status').textContent = String(error); }
}
for (const id of ['compiler', 'standard', 'preset', 'warnings', 'fast-math', 'preprocess', 'images']) get(id).onchange = () => {
  preserveStateOptions = false;
  if (id === 'compiler') get('additional-options').value = additionalByCompiler[get('compiler').value] || '';
  clearErrorInfo();
  invalidateBuild();
  revision++; controls(); get('freshness').textContent = 'Options changed; previous results are retained.';
};
get('additional-options').oninput = () => {
  additionalByCompiler[get('compiler').value] = get('additional-options').value;
  clearErrorInfo(); invalidateBuild(); revision++; controls();
  get('freshness').textContent = 'Options changed; previous results are retained.';
};
for (const [value, label] of Object.entries(exampleLabels)) {
  const option = document.createElement('option');
  option.value = value;
  option.textContent = label;
  get('example').appendChild(option);
}
const firstExample = Object.keys(examples)[0];
get('example').disabled = !firstExample;
get('load').disabled = !firstExample;
get('example').value = firstExample || '';
editor.setValue(firstExample ? examples[firstExample] : '');
if (urlSettings.interface) interfaceMode = urlSettings.interface;
if (urlSettings.example) {
  if (Object.hasOwn(examples, urlSettings.example)) {
    get('example').value = urlSettings.example;
    editor.setValue(examples[urlSettings.example]);
  } else urlWarnings.push(`Requested example ${urlSettings.example} was not found; the current example is retained.`);
}
showURLWarnings();
if (typeof location !== 'undefined') {
  loadSharedCode(true);
  globalThis.addEventListener?.('hashchange', () => {
    if (location.hash.startsWith('#state=')) loadSharedState(); else loadSharedCode();
  });
}
if (typeof window !== 'undefined') {
  (async () => {
    await import('./editor-vendor/codemirror.js');
    await import('./editor-vendor/fortran.js');
    editor.enhance(globalThis.CodeMirror, 'text/x-fortran', 'Fortran input');
    editor.refresh();
    quickFix.refresh();
    controls();
    get('editor-note').textContent = 'Syntax coloring enabled · Tab: indentation · Ctrl+Z: undo · Esc: leave editor.';
  })().catch(() => { get('editor-note').textContent = 'Plain-text editor available.'; });
}
await connect();
loadSharedState(true);
