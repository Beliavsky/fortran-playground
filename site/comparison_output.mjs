const preferenceKey = 'fortran-playground.show-all-outputs';
export function loadAllOutputs(storage) {
  try {return (storage || globalThis.localStorage).getItem(preferenceKey) === 'true';} catch {return false;}
}
export function saveAllOutputs(value, storage) {
  try {(storage || globalThis.localStorage).setItem(preferenceKey, String(Boolean(value)));} catch {}
}

export function comparisonOutput(row, mode) {
  const result = row.result || {}, execution = result.execution;
  let missing = 'Not run.';
  if (row.status === 'QUEUED' || row.status === 'RUNNING') missing = 'Waiting for result.';
  else if (row.status === 'SKIP') missing = 'Not submitted.';
  else if (result.build?.ok === false) missing = 'Not run because compilation failed.';
  else if (mode === 'fortran-compile') missing = 'Not run (compile-only comparison).';
  else if (row.status === 'ERROR') missing = 'No program result received.';
  return {
    title: `${row.compiler}: ${row.status}`,
    version: result.compiler_version || row.version || 'Version unavailable',
    stdout: execution ? execution.stdout || (execution.stderr ? '(No standard output)' : '(No output)') : missing,
    stderr: execution?.stderr || '',
    build: result.build?.stdout || (result.build ? '(No build output)' : result.interpreter ? 'No separate compilation stage (interpreter).' : 'No compilation result received.'),
    buildError: result.build?.stderr || '',
    reason: [row.reason, result.error].filter(Boolean).join('\n'),
    failed: ['FAIL', 'ERROR', 'STOPPED'].includes(row.status),
  };
}

// Preserve stream text, including leading/trailing whitespace. Separators are
// outside the streams, and no HTML or terminal escape interpretation is used.
export function comparisonReport(rows, snapshot, stale = false) {
  const lines = ['Fortran playground compiler comparison',
    `Operation: ${snapshot.mode === 'fortran-compile' ? 'Compile only' : 'Compile and Run'}`,
    'Times in seconds. Other = Total - Compile - Run.',
    ...(stale ? ['Source or settings have changed; these results use the earlier snapshot.'] : [])];
  for (const row of rows) {
    const view = comparisonOutput(row, snapshot.mode);
    lines.push('', `=== ${view.title} ===`, view.version,
      `Settings: ${JSON.stringify(row.options || {})}`,
      `Flags: ${row.flags?.join(' ') || '(compiler default or unavailable)'}`,
      ['total', 'compile', 'run', 'other'].map(key => `${key}: ${Number.isFinite(row.times?.[key]) ? row.times[key].toFixed(3) : '-'}`).join('  '));
    if (view.reason) lines.push(view.reason);
    for (const [label, stage] of [['Compilation', row.result?.build], ['Program', row.result?.execution]]) {
      if (!stage) {lines.push(`${label}: ${label === 'Program' ? view.stdout : view.build}`); continue;}
      for (const stream of ['stdout', 'stderr']) {
        lines.push(`--- ${label} ${stream} ---`, stage[stream] || '', `--- End ${label} ${stream} ---`);
      }
    }
  }
  return lines.join('\n') + '\n';
}
