import {createEditor} from './editors.mjs';
import {examples} from './examples.mjs';
import {parseCompilerErrors} from './diagnostics.mjs';
import {playgroundConfig} from './config.mjs';
import {createQuickFixControls} from './quick_fix_controls.mjs';
import {applyFormatting} from './formatting.mjs';

const get = id => document.getElementById(id);
let token = '', service = '', catalog = {}, active = null, connecting = false, revision = 0;
let filename = 'main.f90';
let features = {}, retained = null, expiryTimer = null;
let compilerVersions = {};
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
  const busy = Boolean(active);
  const interpreted = get('compiler').value === 'ofort';
  get('compile').textContent = interpreted ? 'Check syntax' : 'Compile';
  get('run').textContent = interpreted ? 'Run' : 'Compile and Run';
  quickFix.setBusy(busy);
  get('run').disabled = !token || busy || !editor.getValue().trim();
  get('compile').disabled = get('run').disabled || !features.compile_only;
  get('format').disabled = get('run').disabled || !features.format || !editor.undoableClear;
  get('check').disabled = get('run').disabled || !features.check;
  get('rerun').disabled = interpreted || !token || busy || !features.run_again || !retained || retained.expires_at * 1000 <= Date.now();
  get('build-note').textContent = !features.compile_only ? 'Compile-only and Run Again require an updated execution service.' : retained ? 'Run Again reuses this executable until it expires (up to five minutes). Editing source or options requires recompilation.' : 'Compile to enable Run Again. Each run starts a fresh process.';
  if (interpreted) get('build-note').textContent = 'ofort checks syntax or interprets standalone source. Run starts a fresh process each time; no executable or compiled helpers are used.';
  get('stop').disabled = !active || active.stopping;
  get('connect').disabled = connecting || busy;
  get('compiler').disabled = !token || busy;
  get('download').disabled = !editor.getValue().trim();
  const spec = catalog[get('compiler').value];
  for (const option of get('standard').options) option.disabled = option.value !== 'default' && !spec?.standards?.[option.value];
  if (get('standard').value !== 'default' && !spec?.standards?.[get('standard').value]) get('standard').value = 'default';
  get('standard').disabled = !token || busy || !Object.keys(spec?.standards || {}).length;
  get('standard-note').textContent = `Standard selection applies only to user code. ${spec?.standard_note || 'Standard selection is unavailable from this service.'}`;
  for (const option of get('compiler').options) option.title = compilerVersions[option.value] || 'Version unavailable';
  get('compiler-version').textContent = `${interpreted ? 'Interpreter' : 'Compiler'} version: ${compilerVersions[get('compiler').value] || 'unavailable from this service.'}`;
  for (const option of get('preset').options) option.disabled = !spec?.presets?.[option.value];
  if (!spec?.presets?.[get('preset').value]) get('preset').value = 'default';
  get('preset').disabled = interpreted || !token || busy || !spec;
  for (const [id, key] of [['warnings', 'warnings'], ['fast-math', 'fast_math']]) {
    if (!spec?.extras?.[key]) get(id).checked = false;
    get(id).disabled = !token || busy || !spec?.extras?.[key];
  }
  const flags = spec ? [...(spec.presets[get('preset').value] || []),
    ...(spec.standards?.[get('standard').value] || []),
    ...(get('warnings').checked ? spec.extras.warnings : []),
    ...(get('fast-math').checked ? spec.extras.fast_math : [])] : [];
  get('options-note').textContent = `User-code flags: ${flags.join(' ') || '(compiler default)'}. Helpers keep fixed build options.${get('fast-math').checked ? ' Fast math can change numerical results.' : ''}`;
  if (interpreted) get('options-note').textContent = 'ofort default checks are enabled, including reads of uninitialized variables. Unsupported language features may be rejected.';
}

async function api(path, method = 'GET', payload) {
  const response = await fetch(`${service}/api/${path}`, {
    method, cache: 'no-store', signal: AbortSignal.timeout(30000),
    headers: {'X-P2F-Token': token, ...(payload === undefined ? {} : {'Content-Type': 'application/json'})},
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
    const url = new URL(config.url);
    if (url.protocol !== 'https:' || !url.hostname.endsWith('.modal.run') || url.username || url.password || url.search || url.hash || url.pathname !== '/') {
      throw new Error('Expected the HTTPS origin of the deployed Modal service.');
    }
    service = url.origin;
    const session = await api('session');
    if (!session.token) throw new Error('The service did not provide a session token.');
    const compilers = session.compilers || ['gfortran'];
    for (const option of get('compiler').options) option.disabled = !compilers.includes(option.value);
    if (!compilers.includes(get('compiler').value)) {
      const supported = [...get('compiler').options].find(option => !option.disabled);
      if (!supported) throw new Error('No supported compiler is available.');
      get('compiler').value = supported.value;
    }
    token = session.token;
    catalog = session.compiler_options || {};
    compilerVersions = session.compiler_versions || {};
    features = session.features || {};
    get('connection').textContent = `Connected · ${compilers.join(' / ')} · ${session.timeout ?? '?'} s run limit · runtime ${(session.commit || '').slice(0,7)}`;
    get('status').textContent = 'Ready';
    // No transpiler pin is needed: this site submits only edited Fortran.
  } catch (error) {
    get('connection').textContent = 'Execution service unavailable. Editing and downloading still work; try Reconnect.';
    get('diagnostics').textContent = String(error);
    get('status').textContent = 'Not connected';
  } finally { connecting = false; controls(); }
}

function show(result) {
  get('build-title').textContent = result.interpreter ? (result.build ? 'Syntax checking' : 'Interpreter diagnostics') : 'Compilation';
  const version = result.compiler_version;
  get('result-compiler-version').hidden = !(result.build || result.reused_executable || (result.interpreter && result.execution));
  get('result-compiler-version').textContent = `${result.interpreter ? 'Interpreter' : 'Compiler'} version: ${version || 'unavailable from this service.'}`;
  const diagnosticStage = result.build || (result.interpreter ? result.execution : null);
  if (diagnosticStage) {
    const errors = parseCompilerErrors(`${diagnosticStage.stdout || ''}\n${diagnosticStage.stderr || ''}`, editor.getValue());
    clearErrorInfo();
    editor.setDiagnostics(errors);
    get('first-error').disabled = !errors.length;
    get('first-error').hidden = !errors.length;
    get('error-note').hidden = !errors.length;
    get('error-note').textContent = errors.length ? `${errors.length} source error${errors.length === 1 ? '' : 's'}; first at line ${errors[0].line}: ${errors[0].message}` : '';
    quickFix.update(editor.getValue(), `${diagnosticStage.stdout || ''}\n${diagnosticStage.stderr || ''}`,
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
  if (!token || active) return;
  if (mode === 'fortran-compile' && !features.compile_only) return;
  if (mode === 'format' && (!features.format || !editor.undoableClear)) return;
  if (mode === 'check' && !features.check) return;
  if (mode === 'fortran-run' && (!features.run_again || !retained || retained.expires_at * 1000 <= Date.now())) { invalidateBuild(); controls(); return; }
  const source = editor.getValue();
  if (!source.trim() || new TextEncoder().encode(source).length > 100000) {
    get('status').textContent = 'Enter between 1 byte and 100 KB of Fortran.'; return;
  }
  const job = active = {id: null, revision, stopping: false};
  const artifactId = retained?.id;
  if (!['fortran-run', 'check'].includes(mode)) { invalidateBuild(); clearErrorInfo(); }
  controls(); get('status').textContent = mode === 'check' ? 'Checking with Fortitude…' : mode === 'format' ? 'Formatting…' : mode === 'fortran-run' ? 'Running retained build…' : mode === 'fortran-compile' ? 'Compiling…' : 'Compiling and running…';
  if (get('compiler').value === 'ofort' && !['format', 'check'].includes(mode)) {
    get('status').textContent = mode === 'fortran-compile' ? 'Checking syntax…' : 'Interpreting…';
  }
  try {
    const created = await api('jobs', 'POST', {
      source: ['format', 'check'].includes(mode) ? source : '', mode, automatic: false,
      ...(['format', 'check'].includes(mode) ? {} : mode === 'fortran-run' ? {artifact_id: artifactId} : {fortran_source: source, ...(features.run_again && get('compiler').value !== 'ofort' ? {retain_executable: true} : {})}),
      compiler: ['format', 'check'].includes(mode) ? 'gfortran' : get('compiler').value,
      ...(!['format', 'check'].includes(mode) && catalog[get('compiler').value] ? {compiler_options: {
        preset: get('preset').value, warnings: Boolean(get('warnings').checked), fast_math: Boolean(get('fast-math').checked),
        ...(catalog[get('compiler').value]?.standards ? {standard: get('standard').value} : {}),
      }} : {}),
    });
    job.id = created.id;
    if (job.stopping) await api(`jobs/${job.id}/cancel`, 'POST', {});
    const deadline = Date.now() + 300000;
    while (active === job) {
      const state = await api(`jobs/${job.id}`);
      if (state.state === 'done') {
        if (job.stopping) get('status').textContent = 'Stopped';
        else if (revision === job.revision && mode === 'check') {
          const result = state.result;
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
            get('status').textContent = 'Formatting failed; source unchanged';
            get('diagnostics').textContent = String(error);
          }
        }
        else if (revision === job.revision) show(state.result);
        else get('status').textContent = 'Previous result discarded — source or options changed';
        break;
      }
      if (Date.now() > deadline) throw new Error('Job response timed out. Try Reconnect.');
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  } catch (error) {
    if (mode === 'fortran-run' && error.status === 404) invalidateBuild();
    if (job.id) api(`jobs/${job.id}/cancel`, 'POST', {}).catch(() => {});
    get('diagnostics').textContent = String(error);
    get('status').textContent = 'Execution request failed';
    if (!error.status || error.status === 401 || error.status === 403) token = '';
  } finally { active = null; controls(); }
}

get('run').onclick = () => run();
get('compile').onclick = () => run('fortran-compile');
get('format').onclick = () => run('format');
get('check').onclick = () => run('check');
get('rerun').onclick = () => run('fortran-run');
get('first-error').onclick = () => editor.goToDiagnostic();
get('connect').onclick = connect;
get('stop').onclick = async () => {
  if (!active) return;
  active.stopping = true; controls(); get('status').textContent = 'Stopping…';
  try { if (active.id) await api(`jobs/${active.id}/cancel`, 'POST', {}); }
  catch (error) { get('diagnostics').textContent = String(error); }
};
get('load').onclick = () => {
  if (editor.getValue().trim() && !confirm('Replace the Fortran input with this example?')) return;
  editor.setValue(examples[get('example').value], true); filename = 'main.f90'; editor.focus();
};
get('clear').onclick = () => {
  if (editor.getValue() && !editor.undoableClear && !confirm('Clear the Fortran input?')) return;
  editor.setValue('', true); editor.focus();
  for (const id of ['output', 'diagnostics', 'run-time', 'build-time', 'checks', 'check-time']) get(id).textContent = '';
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
  const url = URL.createObjectURL(new Blob([editor.getValue()], {type: 'text/plain;charset=utf-8'}));
  const link = document.createElement('a');
  link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
for (const id of ['compiler', 'standard', 'preset', 'warnings', 'fast-math']) get(id).onchange = () => {
  clearErrorInfo();
  invalidateBuild();
  revision++; controls(); get('freshness').textContent = 'Options changed; previous results are retained.';
};
editor.setValue(examples.sum);
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
