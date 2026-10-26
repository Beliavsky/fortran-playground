// Numeric-aware stdout comparison. Decimal integer arithmetic preserves large integers.
const tokenPattern = /('(?:[^']|'')*'|"(?:[^"]|"")*"|\*{2,}|\.(?:true|false)\.|[\p{L}\p{Nl}\p{No}_][\p{L}\p{N}_]*(?:\.[\p{L}\p{N}_]+)*|[+-]?(?:infinity|inf|nan)\b|[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?|[^\s])/giu;
const numberPattern = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?$/;
const specialPattern = /^[+-]?(?:infinity|inf|nan)$|^\*{2,}$/i;
const normalized = text => text.replace(/\r\n?/g, '\n');
const whitespace = text => text.trim().split(/\s+/).filter(Boolean).join(' ');
function decimal(value) {
  const text = String(value);
  if (text.length > 2200 || !numberPattern.test(text)) throw new Error('Use finite nonnegative decimal tolerances; numeric tokens must have bounded length.');
  const parts = text.split(/[eEdD]/), exponent = parts.length === 2 ? Number(parts[1]) : 0;
  if (!Number.isFinite(exponent) || Math.abs(exponent) > 2000) throw new Error('Numeric exponent exceeds comparison limit (2000).');
  const digits = parts[0].replace('.', '');
  if (digits.replace(/^[+-]/, '').length > 2000) throw new Error('Numeric token exceeds comparison limit (2000 digits).');
  return [BigInt(digits), exponent - (parts[0].split('.')[1]?.length || 0)];
}
function aligned(a, b) {
  const exponent = Math.min(a[1], b[1]);
  return [a[0] * 10n ** BigInt(a[1] - exponent), b[0] * 10n ** BigInt(b[1] - exponent), exponent];
}
function cmp(a, b) {const [x, y] = aligned(a, b); return x > y ? 1 : x < y ? -1 : 0;}
const abs = value => value < 0n ? -value : value;
export function tolerances(atol = '0', rtol = '0') {
  const values = [decimal(atol), decimal(rtol)];
  if (values.some(value => value[0] < 0n)) throw new Error('Tolerances must be finite and nonnegative.');
  return values;
}
function close(a, b, absolute, relative) {
  const [x, y, exponent] = aligned(a, b), difference = [abs(x - y), exponent];
  const aa = [abs(a[0]), a[1]], bb = [abs(b[0]), b[1]], scale = cmp(aa, bb) >= 0 ? aa : bb;
  let bound = [relative[0] * scale[0], relative[1] + scale[1]];
  if (cmp(absolute, bound) >= 0) bound = absolute;
  return cmp(difference, bound) <= 0;
}
export function compareOutput(left, right, mode = 'whitespace', atol = '0', rtol = '0') {
  const [absolute, relative] = tolerances(atol, rtol);
  if (!['whitespace', 'exact', 'numeric'].includes(mode)) throw new Error('Unknown output comparison mode');
  const unavailable = detail => ({status: 'Not comparable', detail});
  if (left.length > 1000000 || right.length > 1000000) return unavailable('Output exceeds the 1,000,000-character comparison limit.');
  const a = normalized(left), b = normalized(right);
  let detail = '';
  if (mode === 'numeric') {
    const ta = a.match(tokenPattern) || [], tb = b.match(tokenPattern) || [];
    if (Math.max(ta.length, tb.length) > 20000) return unavailable('More than 20,000 output tokens.');
    if ([...ta, ...tb].some(token => specialPattern.test(token))) return unavailable('NaN, infinity, or overflow fields present; inspect raw output.');
    if (ta.length !== tb.length) detail = `Token counts differ: reference ${ta.length}, output ${tb.length}.`;
    let tolerant = false;
    try {
      for (let i = 0; !detail && i < ta.length; i++) {
        const x = ta[i], y = tb[i];
        if (x === y) continue;
        let same;
        if (/^(t|f|\.true\.|\.false\.)$/i.test(x) && /^(t|f|\.true\.|\.false\.)$/i.test(y)) same = /^(t|\.true\.)$/i.test(x) === /^(t|\.true\.)$/i.test(y);
        else if (numberPattern.test(x) && numberPattern.test(y)) {
          const dx = decimal(x), dy = decimal(y), equal = cmp(dx, dy) === 0;
          const integers = /^[+-]?\d+$/.test(x) && /^[+-]?\d+$/.test(y);
          same = equal || (!integers && close(dx, dy, absolute, relative));
          tolerant ||= same && !equal;
        } else same = false;
        if (!same) detail = `Token ${i + 1}: reference ${JSON.stringify(x.slice(0, 160))}, output ${JSON.stringify(y.slice(0, 160))}.`;
      }
    } catch (error) {return unavailable(error.message);}
    if (!detail) return {status: a === b ? 'Exact match' : whitespace(a) === whitespace(b) ? 'Formatting only' : tolerant ? 'Within tolerance' : 'Numeric match', detail: ''};
  } else if (a === b) return {status: 'Exact match', detail: ''};
  else if (mode === 'whitespace' && whitespace(a) === whitespace(b)) return {status: 'Formatting only', detail: ''};
  if (!detail) {
    const aa = mode === 'whitespace' ? a.trim().split(/\s+/).filter(Boolean) : a.split('\n');
    const bb = mode === 'whitespace' ? b.trim().split(/\s+/).filter(Boolean) : b.split('\n');
    let i = 0; while (i < Math.max(aa.length, bb.length) && aa[i] === bb[i]) i++;
    detail = `${mode === 'whitespace' ? 'Token' : 'Line'} ${i + 1}: reference ${JSON.stringify((aa[i] ?? '<end>').slice(0, 160))}, output ${JSON.stringify((bb[i] ?? '<end>').slice(0, 160))}.`;
  }
  return {status: 'Different', detail};
}
export function comparable(row) {
  const result = row.result || row, execution = result.execution;
  if ((row.status || 'PASS') !== 'PASS' || result.ok === false || !execution) return false;
  if (execution.ok === false || (execution.exit_code ?? 0) !== 0 || execution.timed_out || execution.cancelled) return false;
  return !execution.truncated && !execution.stdout_truncated && !/Output was truncated at the configured per-stream limit\.|Output limit exceeded\./i.test(execution.stderr || '');
}
export function comparisonReport(rows, mode = 'whitespace', atol = '0', rtol = '0', reference = '') {
  tolerances(atol, rtol);
  const baseline = rows.find(row => comparable(row) && (!reference || row.compiler === reference));
  const lines = [`Output comparison: ${mode}; stdout only; atol=${atol}, rtol=${rtol}`,
    `Reference: ${baseline?.compiler || 'unavailable (no successful complete run)'}`];
  for (const row of rows) {
    let outcome = !baseline || !comparable(row) ? {status: 'Not comparable', detail: 'Requires a successful, complete execution and reference.'} :
      compareOutput((baseline.result || baseline).execution.stdout || '', (row.result || row).execution.stdout || '', mode, atol, rtol);
    if (row === baseline && outcome.status !== 'Not comparable') outcome = {status: 'Reference', detail: ''};
    lines.push(`${row.compiler}: ${outcome.status}${outcome.detail ? ' — ' + outcome.detail : ''}`);
  }
  return lines.join('\n');
}
