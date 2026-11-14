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

  function normalizeDeclaration(text) {
    // Work on code alone: quoted selectors and comments are not spacing targets.
    const chars = Array.from(text), pieces = normalizedPieces(text);
    let quote = '', comment = false, separator = false;
    for (let i = 0; i < chars.length; i++) {
      const c = chars[i];
      if (c === '\n' || c === '\r') {comment = false; continue;}
      if (comment) continue;
      if (quote) {
        if (c === quote) {if (chars[i + 1] === quote) {i++; continue;} quote = '';}
        continue;
      }
      if (c === "'" || c === '"') {quote = c; continue;}
      if (c === '!') {comment = true; continue;}
      if (c === ':' && chars[i + 1] === ':') {
        separator = true;
        let before = i - 1, after = i + 2;
        while (chars[before] === ' ' || chars[before] === '\t') pieces[before--] = '';
        while (chars[after] === ' ' || chars[after] === '\t') pieces[after++] = '';
        pieces[i] = ' :: '; pieces[++i] = '';
      }
    }
    let result = pieces.join('');
    // Legacy declarations omit ::. Read a balanced type/attribute selector.
    if (!separator) {
      const head = /^(\s*(?:double\s+precision|double\s+complex|integer|real|complex|logical|character|type|class|procedure|external|dimension|allocatable|pointer|optional|target|value|contiguous|intent)\b)/i.exec(result);
      if (head) {
        let i = head[0].length;
        while (/^[ \t]$/.test(result[i] || '')) i++;
        if (result[i] === '*') {
          i++;
          while (/^[ \t]$/.test(result[i] || '')) i++;
          const size = /^[a-z0-9_]+/i.exec(result.slice(i));
          if (size) i += size[0].length;
        }
        if (result[i] !== '(' && !result.slice(head[0].length, i).includes('*')) {
          const rest = result.slice(head[0].length).trimStart();
          if (/^[a-z]/i.test(rest)) return result.slice(0, head[0].length).trimEnd() + ' :: ' + rest;
        }
        if (result[i] === '(') {
          let depth = 0, quote = '';
          for (; i < result.length; i++) {
            const c = result[i];
            if (quote) {if (c === quote) {if (result[i + 1] === quote) {i++; continue;} quote = '';}}
            else if (c === "'" || c === '"') quote = c;
            else if (c === '(') depth++;
            else if (c === ')' && --depth === 0) {i++; break;}
          }
        }
        if (/^[ \t]+[a-z]/i.test(result.slice(i))) result = result.slice(0, i).trimEnd() + ' :: ' + result.slice(i).trimStart();
      }
    }
    return result;
  }

  function normalizeDescription(text, ranges) {
    const chars = Array.from(text), parts = [];
    let previous = 0;
    for (const [first, last] of ranges) {
      if (!Number.isInteger(first) || !Number.isInteger(last) || first < previous || last < first || last > chars.length) return text;
      parts.push(chars.slice(previous, first).join(''), normalizeDeclaration(chars.slice(first, last).join('')));
      previous = last;
    }
    return parts.join('') + chars.slice(previous).join('');
  }

  const fortranTypes = new Set('integer real complex logical character double precision type class'.split(' '));
  const fortranKeywords = new Set(('call use only import implicit none program module submodule subroutine function result contains end ' +
    'interface generic procedure public private pass nopass deferred extends abstract recursive pure elemental impure ' +
    'intent in out inout optional allocatable pointer target dimension codimension parameter save value contiguous external intrinsic ' +
    'kind len bind operator assignment select case default if then else elseif endif do while concurrent forall where elsewhere ' +
    'allocate deallocate nullify associate block critical return stop error cycle exit print read write format').split(' '));

  function fortranTokens(text) {
    const tokens = [];
    let i = 0;
    while (i < text.length) {
      const start = i, char = text[i];
      if (char === '!' || (char === '#' && /(?:^|\n)[ \t]*$/.test(text.slice(0, i)))) {
        while (i < text.length && text[i] !== '\n' && text[i] !== '\r') i++;
        tokens.push({start, end: i, kind: 'comment'});
        continue;
      }
      // BOZ prefixes belong to the literal; doubled quotes are Fortran escapes.
      const boz = /[boz]/i.test(char) && (text[i + 1] === "'" || text[i + 1] === '"');
      if (char === "'" || char === '"' || boz) {
        if (boz) i++;
        const quote = text[i++];
        while (i < text.length) {
          if (text[i++] === quote) {
            if (text[i] === quote) {i++; continue;}
            break;
          }
        }
        tokens.push({start, end: i, kind: 'string'});
        continue;
      }
      const logical = /^\.(?:true|false)\.(?:_(?:[a-z][a-z0-9_]*|\d+))?/i.exec(text.slice(i));
      const number = /^(?:\d+\.\d*|\.\d+|\d+)(?:[edq][+-]?\d+)?(?:_(?:[a-z][a-z0-9_]*|\d+))?/i.exec(text.slice(i));
      if (logical || number) {
        i += (logical || number)[0].length;
        tokens.push({start, end: i, kind: 'number'});
        continue;
      }
      const identifier = /^[a-z][a-z0-9_]*/i.exec(text.slice(i));
      if (identifier) {
        i += identifier[0].length;
        const word = identifier[0].toLowerCase();
        if (fortranTypes.has(word) || fortranKeywords.has(word)) {
          tokens.push({start, end: i, kind: fortranTypes.has(word) ? 'type' : 'keyword'});
        }
        continue;
      }
      i++;
    }
    return tokens;
  }

  function highlightCode(doc, roots) {
    const replacements = [];
    for (const root of roots) {
      const nodes = [], walker = doc.createTreeWalker(root, 4);
      let node;
      while ((node = walker.nextNode())) nodes.push(node);
      const tokens = fortranTokens(nodes.map(n => n.data).join(''));
      let offset = 0, firstToken = 0;
      for (const node of nodes) {
        const end = offset + node.data.length;
        while (firstToken < tokens.length && tokens[firstToken].end <= offset) firstToken++;
        const wrapper = doc.createElement('span');
        let previous = 0, colored = false;
        for (let j = firstToken; j < tokens.length && tokens[j].start < end; j++) {
          const token = tokens[j], first = Math.max(offset, token.start) - offset;
          const last = Math.min(end, token.end) - offset;
          if (first > previous) wrapper.appendChild(doc.createTextNode(node.data.slice(previous, first)));
          const span = doc.createElement('span');
          span.className = 'syntax-' + token.kind;
          span.textContent = node.data.slice(first, last);
          wrapper.appendChild(span);
          previous = last; colored = true;
        }
        if (colored) {
          if (previous < node.data.length) wrapper.appendChild(doc.createTextNode(node.data.slice(previous)));
          node.parentNode.replaceChild(wrapper, node);
          replacements.push({wrapper, node});
        }
        offset = end;
      }
    }
    // Restore the very same text nodes before formatting again. Links, argument
    // annotation elements, focus and their listeners are never replaced.
    return () => {for (const {wrapper, node} of replacements) wrapper.parentNode.replaceChild(node, wrapper);};
  }

  function initializeFormatting(doc, win) {
    const control = doc.getElementById('original-formatting');
    if (!control) return;
    const roots = Array.from(doc.querySelectorAll('.calling-sequence, .declaration-code'));
    const code = roots.map(root => {
      const nodes = [], walker = doc.createTreeWalker(root, 4); // SHOW_TEXT
      let node;
      while ((node = walker.nextNode())) nodes.push({node, original: node.data});
      const originalText = nodes.map(item => item.original).join('');
      const declaration = root.getAttribute && root.getAttribute('data-normalized-code');
      if (root.classList && root.classList.contains('declaration-code')) {
        // Declaration blocks contain plain text, so a projected declaration can
        // replace a shared source line while the exact original stays available.
        return nodes.map((item, index) => ({...item, normalized: index === 0 ? normalizeDeclaration(declaration || originalText) : ''}));
      }
      const pieces = normalizedPieces(originalText);
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
    const highlightRoots = doc.createElement ? Array.from(doc.querySelectorAll('.calling-sequence, .argument-details > pre > code')) : [];
    let removeHighlighting = () => {};
    function apply() {
      removeHighlighting();
      const original = control.checked;
      for (const nodes of code) for (const item of nodes) item.node.data = original ? item.original : item.normalized;
      for (const item of tooltips) {
        const description = original ? item.original : item.normalized;
        const name = original ? item.name : normalizeFortran(item.name);
        item.node.setAttribute('data-intent-description', description);
        item.node.setAttribute('title', name + ': ' + description);
        item.node.setAttribute('aria-label', name + ': ' + description);
      }
      removeHighlighting = highlightCode(doc, highlightRoots);
    }
    control.addEventListener('change', () => {
      try {win.localStorage.setItem(preference, String(control.checked));} catch {}
      apply();
    });
    apply();
  }

  global.FortranCatalogFormatting = {normalizeFortran, normalizeDeclaration, normalizeDescription, fortranTokens, highlightCode, initializeFormatting};
  if (typeof document !== 'undefined') initializeFormatting(document, global);
})(globalThis);
