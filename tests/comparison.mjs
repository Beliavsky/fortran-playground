import assert from 'node:assert/strict';
import {comparisonPlan, comparisonTimes, executeComparison} from '../site/comparison.mjs';

const spec = {presets: {default: [], debug: ['-g']}, standards: {'2018': ['-std=f2018']},
  extras: {preprocess: ['-cpp'], warnings: ['-Wall']}, coarray_images: {'2': ['-fcoarray=lib']},
  additional_options: {optimization: [['-O2'], ['-O3']]}};
const options = {preset: 'default', standard: 'default', warnings: false, fast_math: false};
const catalog = {gnu: spec, other: {presets: {default: []}, extras: {}}};
assert.equal(comparisonPlan(['gnu', 'other'], catalog, options).filter(item => !item.reason).length, 2);
for (const request of [{standard: '2018'}, {preset: 'debug'}, {preprocess: true}, {warnings: true}, {images: 2}]) {
  const plan = comparisonPlan(['gnu', 'other'], catalog, {...options, ...request});
  assert.equal(plan[0].reason, ''); assert.ok(plan[1].reason);
}
const additional = comparisonPlan(['gnu', 'other'], catalog, options, {gnu: '-O2'});
assert.deepEqual(additional[0].options.additional, ['-O2']);
assert.deepEqual(additional[1].options.additional, []);
assert.match(comparisonPlan(['gnu'], catalog, options, {gnu: '-O2 -O3'})[0].reason, /Conflicting/);
assert.ok(comparisonPlan(['missing'], catalog, options)[0].reason);
assert.deepEqual(comparisonTimes({execution: {seconds: 2}}, 5), {total: 5, compile: null, run: 2, other: 3});
assert.deepEqual(comparisonTimes({build: {seconds: 1}, execution: {seconds: 2}}, 5), {total: 5, compile: 1, run: 2, other: 2});

async function scenario({stopOnFailure = false, stopDuringSubmit = false, throwStatus, invalidResult = false} = {}) {
  const events = [], submitted = [], cancelled = [], results = [];
  let stop = false, clock = 0, inFlight = false;
  const plan = [{compiler: 'bad'}, {compiler: 'skip', reason: 'Unsupported'}, {compiler: 'good'}];
  await executeComparison({plan, stopOnFailure, stopped: () => stop, now: () => clock,
    wait: async () => {throw new Error('Unexpected wait');},
    submit: async item => {
      assert.equal(inFlight, false); inFlight = true;
      submitted.push(item.compiler); events.push(`submit ${item.compiler}`); clock += 1000;
      if (stopDuringSubmit) stop = true;
      if (throwStatus) {inFlight = false; throw Object.assign(new Error('Request rejected'), {status: throwStatus});}
      return {id: item.compiler};
    },
    poll: async id => {
      events.push(`poll ${id}`); clock += 2000; inFlight = false;
      return {state: 'done', ...(invalidResult ? {} : {result: {ok: id === 'good', build: {seconds: 0.5}}})};
    },
    cancel: async id => {cancelled.push(id);}, update: row => results.push(row),
  });
  return {submitted, cancelled, results: results.filter(row => row.status !== 'RUNNING'), events};
}
let run = await scenario();
assert.deepEqual(run.submitted, ['bad', 'good']);
assert.deepEqual(run.events, ['submit bad', 'poll bad', 'submit good', 'poll good']);
assert.deepEqual(run.results.map(row => row.status), ['FAIL', 'SKIP', 'PASS']);
assert.deepEqual(run.results[0].times, {total: 3, compile: 0.5, run: null, other: 2.5});
run = await scenario({stopOnFailure: true});
assert.deepEqual(run.submitted, ['bad']);
assert.deepEqual(run.results.map(row => row.status), ['FAIL', 'SKIP', 'SKIP']);
run = await scenario({stopDuringSubmit: true});
assert.deepEqual(run.submitted, ['bad']); assert.deepEqual(run.cancelled, ['bad']);
assert.equal(run.results[0].status, 'STOPPED');
run = await scenario({throwStatus: 400}); assert.deepEqual(run.submitted, ['bad', 'good']);
for (const status of [401, 403, 429]) {
  run = await scenario({throwStatus: status}); assert.deepEqual(run.submitted, ['bad']);
}
run = await scenario({invalidResult: true}); assert.equal(run.results[0].status, 'ERROR');
assert.deepEqual(run.cancelled, ['bad', 'good']);
console.log('Comparison settings, sequential execution, timing, failures, and cancellation passed.');
