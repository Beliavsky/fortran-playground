import {compilerArguments, optionTokens} from './compiler_arguments.mjs';

export function comparisonPlan(compilers, catalog, options, additional = {}) {
  return compilers.map(compiler => {
    const selection = {...options, additional: optionTokens(additional[compiler] || '')};
    let reason = '';
    try {
      const spec = catalog[compiler];
      if (!spec) throw new Error('Compiler options are unavailable from this service.');
      if (selection.preset !== 'default' && !spec.presets?.[selection.preset]) throw new Error('Selected preset is unsupported.');
      if (selection.standard !== 'default' && !spec.standards?.[selection.standard]) throw new Error('Selected standard is unsupported.');
      for (const [key, label] of [['warnings', 'Extra warnings'], ['fast_math', 'Fast math'], ['preprocess', 'Preprocessing']]) {
        if (selection[key] && !spec.extras?.[key]) throw new Error(`${label} is unsupported.`);
      }
      compilerArguments(spec, selection, selection.additional);
    } catch (error) { reason = error.message; }
    return {compiler, options: selection, reason};
  });
}

export function comparisonTimes(result, total) {
  const seconds = stage => Number.isFinite(stage?.seconds) && stage.seconds >= 0 ? stage.seconds : null;
  const compile = seconds(result?.build), run = seconds(result?.execution);
  return {total, compile, run, other: Math.max(0, total - (compile ?? 0) - (run ?? 0))};
}

// The caller owns cancellation of the current remote job. The queue never
// submits another job once stop is requested, including during submission.
export async function executeComparison({plan, submit, poll, cancel, stopped,
  update, stopOnFailure = false, now = () => performance.now(),
  wait = () => new Promise(resolve => setTimeout(resolve, 500))}) {
  let halted = false;
  for (const item of plan) {
    if (halted || stopped()) { update({...item, status: 'SKIP', reason: 'Not submitted: comparison stopped.'}); continue; }
    if (item.reason) { update({...item, status: 'SKIP'}); continue; }
    const started = now();
    let id;
    update({...item, status: 'RUNNING'});
    try {
      ({id} = await submit(item));
      if (!id) throw new Error('Service did not return a job ID.');
      if (stopped()) await cancel(id);
      const deadline = now() + 300000;
      while (true) {
        const state = await poll(id);
        if (state.state === 'done') {
          if (!state.result && !stopped()) throw new Error('Service did not return a job result.');
          const status = stopped() ? 'STOPPED' : state.result.ok ? 'PASS' : 'FAIL';
          update({...item, status, result: state.result, times: comparisonTimes(state.result, (now() - started) / 1000)});
          halted = stopped() || (stopOnFailure && status === 'FAIL');
          break;
        }
        if (now() > deadline) throw new Error('Job response timed out. Try Reconnect.');
        await wait();
      }
    } catch (error) {
      if (id) { try { await cancel(id); } catch {} }
      update({...item, status: stopped() ? 'STOPPED' : 'ERROR', reason: error.message,
        times: comparisonTimes(null, (now() - started) / 1000)});
      // Authentication and quota errors need intervention, not more submissions.
      halted = stopped() || stopOnFailure || [401, 403, 429].includes(error.status);
    }
  }
}
