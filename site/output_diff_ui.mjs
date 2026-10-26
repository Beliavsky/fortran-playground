import {comparisonReport} from './output_diff.mjs';

// Shared by the hosted and standalone local pages; settings never submit work.
export function createOutputComparison(get) {
  let rows = [];
  get('diff-enabled').checked = false;
  get('diff-mode').value = 'whitespace';
  get('diff-atol').value = get('diff-rtol').value = '0';
  function report() {
    if (!get('diff-enabled').checked) return '';
    const mode = get('diff-mode').value;
    try {return comparisonReport(rows, mode, mode === 'numeric' ? get('diff-atol').value : '0', mode === 'numeric' ? get('diff-rtol').value : '0', get('diff-reference').value);}
    catch (error) {return 'Output comparison: ' + error.message;}
  }
  function render() {
    get('diff-controls').hidden = !get('diff-enabled').checked;
    get('diff-results').hidden = !get('diff-enabled').checked;
    const numeric = get('diff-mode').value === 'numeric';
    get('diff-atol').disabled = get('diff-rtol').disabled = !numeric;
    get('diff-results').textContent = report();
  }
  for (const id of ['diff-enabled', 'diff-mode', 'diff-reference', 'diff-atol', 'diff-rtol']) get(id).onchange = render;
  for (const id of ['diff-atol', 'diff-rtol']) get(id).oninput = render;
  return {
    report,
    update(value) {
      rows = value;
      const selected = get('diff-reference').value;
      const option = (value, label) => {const node = document.createElement('option'); node.value = value; node.textContent = label; return node;};
      get('diff-reference').replaceChildren(option('', 'Automatic (first successful)'), ...rows.map(row => option(row.compiler, row.compiler)));
      get('diff-reference').value = rows.some(row => row.compiler === selected) ? selected : '';
      render();
    },
  };
}
