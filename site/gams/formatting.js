/* Display formatting only. Metadata, source URLs and runnable examples are untouched. */
(function (global) {
  'use strict';
  const preference = 'fortran-catalog-original-formatting';

  function normalizedPieces(text) {
    const chars = Array.from(text), pieces = chars.slice();
    let quote = '', comment = false, lineStart = true;
    for (let i = 0; i < chars.length; i++) {
      const char = chars[i];
      if (char === '\n' || char === '\r') {comment = false; lineStart = true; continue;}
      if (comment) continue;
      if (quote) {
        if (char === quote) {
          if (chars[i + 1] === quote) {i++; continue;}
          quote = '';
        }
        continue;
      }
      if (lineStart && (char === ' ' || char === '\t')) continue;
      if (lineStart && char === '#') {comment = true; continue;}
      lineStart = false;
      if (char === '!') {comment = true; continue;}
      if (char === "'" || char === '"') {quote = char; continue;}
      if (char >= 'A' && char <= 'Z') pieces[i] = char.toLowerCase();
      if (char === ',') {
        let next = i + 1;
        while (chars[next] === ' ' || chars[next] === '\t') next++;
        if (chars[next] !== '\n' && chars[next] !== '\r') {
          pieces[i] = ', ';
          for (let j = i + 1; j < next; j++) pieces[j] = '';
        }
      }
    }
    return pieces;
  }

  function normalizeFortran(text) {return normalizedPieces(text).join('');}

  function normalizeDescription(text, ranges) {
    const chars = Array.from(text), parts = [];
    let previous = 0;
    for (const [first, last] of ranges) {
      if (!Number.isInteger(first) || !Number.isInteger(last) || first < previous || last < first || last > chars.length) return text;
      parts.push(chars.slice(previous, first).join(''), normalizeFortran(chars.slice(first, last).join('')));
      previous = last;
    }
    return parts.join('') + chars.slice(previous).join('');
  }

  function initializeFormatting(doc, win) {
    const control = doc.getElementById('original-formatting');
    if (!control) return;
    const roots = Array.from(doc.querySelectorAll('.calling-sequence, .declaration-code'));
    const code = roots.map(root => {
      const nodes = [], walker = doc.createTreeWalker(root, 4); // SHOW_TEXT
      let node;
      while ((node = walker.nextNode())) nodes.push({node, original: node.data});
      const pieces = normalizedPieces(nodes.map(item => item.original).join(''));
      let position = 0;
      for (const item of nodes) {
        const length = Array.from(item.original).length;
        item.normalized = pieces.slice(position, position + length).join('');
        position += length;
      }
      return nodes;
    });
    const tooltips = Array.from(doc.querySelectorAll('.argument-intent')).map(node => {
      const original = node.getAttribute('data-intent-description') || '';
      const name = node.getAttribute('data-argument-label') || '';
      let ranges = [];
      try {ranges = JSON.parse(node.getAttribute('data-code-ranges') || '[]');} catch {}
      return {node, original, normalized: normalizeDescription(original, ranges), name};
    });
    try {control.checked = win.localStorage.getItem(preference) === 'true';} catch {control.checked = false;}
    function apply() {
      const original = control.checked;
      for (const nodes of code) for (const item of nodes) item.node.data = original ? item.original : item.normalized;
      for (const item of tooltips) {
        const description = original ? item.original : item.normalized;
        const name = original ? item.name : normalizeFortran(item.name);
        item.node.setAttribute('data-intent-description', description);
        item.node.setAttribute('title', name + ': ' + description);
        item.node.setAttribute('aria-label', name + ': ' + description);
      }
    }
    control.addEventListener('change', () => {
      try {win.localStorage.setItem(preference, String(control.checked));} catch {}
      apply();
    });
    apply();
  }

  global.FortranCatalogFormatting = {normalizeFortran, normalizeDescription, initializeFormatting};
  if (typeof document !== 'undefined') initializeFormatting(document, global);
})(globalThis);
