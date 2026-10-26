export const defaultIndentation = {width: 3, automatic: true};
const storageKey = 'fortran-playground.indentation';

export function indentationSettings(value) {
  return {width: [2, 3, 4].includes(value?.width) ? value.width : 3,
    automatic: typeof value?.automatic === 'boolean' ? value.automatic : true};
}
export function loadIndentation(storage) {
  try { return indentationSettings(JSON.parse((storage || globalThis.localStorage).getItem(storageKey))); }
  catch { return {...defaultIndentation}; }
}
export function saveIndentation(storage, value) {
  try { (storage || globalThis.localStorage).setItem(storageKey, JSON.stringify(indentationSettings(value))); } catch {}
}

function leading(line, width = 3) {
  let column = 0;
  for (const char of /^\s*/.exec(line)[0]) column += char === '\t' ? width - column % width : 1;
  return column;
}
// Mask strings and comments, retaining quote state across continued literals.
function codeLine(line, quote = '') {
  let code = '', last = '';
  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (!quote && char === '!') break;
    if (char.trim()) last = char;
    if (quote) {
      code += ' ';
      if (char === quote) {
        if (line[i + 1] === quote) {code += ' '; i++;}
        else quote = '';
      }
    } else if (char === "'" || char === '"') {quote = char; code += ' ';}
    else code += char;
  }
  return {code: code.trim().toLowerCase(), continued: last === '&', quote};
}
function kindOf(code) {
  code = code.replace(/^[a-z]\w*\s*:(?!:)\s*/, '');
  const close = /^end\s*(program|module|submodule|subroutine|function|if|do|select|type|interface|associate|block|critical|where|forall|team)\b/.exec(code);
  if (close) return {close: close[1]};
  if (code === 'end') return {close: 'unit'};
  if (/^else\s*where\b/.test(code)) return {branch: 'where'};
  if (/^else(?:\s*if\b|\s*$|\s+[a-z]\w*$)/.test(code)) return {branch: 'if'};
  if (/^(?:case\s*(?:\(|default\b)|(?:type|class)\s+is\s*\(|class\s+default\b|rank\s*(?:\(|default\b))/.test(code)) return {branch: 'select'};
  if (/^contains$/.test(code)) return {branch: 'contains'};
  if (/^if\s*\(.*\)\s*then\s*$/.test(code)) return {open: 'if'};
  if (/^do(?:\s*$|\s+(?:while\s*\(|concurrent\s*\(|[a-z]\w*\s*=))/.test(code)) return {open: 'do'};
  if (/^select\s*(?:case|type|rank)\s*\(/.test(code)) return {open: 'select'};
  if (/^(?:abstract\s+)?interface\b/.test(code)) return {open: 'interface'};
  if (/^type\s*(?:,.*)?::\s*[a-z]\w*\s*(?:\([^)]*\))?$/.test(code) || /^type\s+[a-z]\w*$/.test(code)) return {open: 'type'};
  if (/^(associate\s*\(|block\s*$|critical\s*$|change\s+team\s*\()/.test(code)) return {open: code.startsWith('change') ? 'team' : code.split(/[\s(]/)[0]};
  if (/^(?:where|forall)\s*\(.*\)\s*$/.test(code)) return {open: code.startsWith('where') ? 'where' : 'forall'};
  if (/^(?:(?:module|pure|impure|elemental|recursive|non_recursive)\s+)*(?:(?:integer|real|complex|logical|character|double\s+precision|type|class)(?:\s*\([^)]*\)|\s*\*\d+)?\s+)?(?:subroutine|function)\s+[a-z]\w*\s*(?:\(|$)/.test(code)) return {open: /\bsubroutine\b/.test(code) ? 'subroutine' : 'function'};
  const unit = /^(program|module|submodule)\s+(?!procedure\b|function\b|subroutine\b)(?:\([^)]*\)\s*)?[a-z]\w*\s*$/.exec(code);
  return unit ? {open: unit[1]} : {};
}
const units = ['program', 'module', 'submodule', 'subroutine', 'function'];

// Use actual opening-line indentation. Ambiguous statements reset context;
// indentation assistance must not rewrite pasted code or guess at old DO labels.
export function indentationForLine(lines, index, width = 3, allowBareEnd = true) {
  const stack = [];
  let pending = null, quote = '';
  let answer = {current: null, next: leading(lines[index] || '', width)};
  for (let i = 0; i <= index; i++) {
    const line = lines[i] || '', indent = leading(line, width);
    if (/^\s*#/.test(line)) {stack.length = 0; pending = null; quote = ''; continue;}
    if (!line.trim() || /^\s*!/.test(line)) {
      if (i === index && pending) answer.next = pending.indent + width;
      continue;
    }
    const parsed = codeLine(line, quote);
    quote = parsed.continued ? parsed.quote : '';
    if (!parsed.code && !parsed.continued && !pending) continue;
    const continuedBefore = Boolean(pending);
    const base = pending?.indent ?? indent;
    const code = (pending?.code || '') + ' ' + parsed.code.replace(/^&/, '').replace(/&$/, '');
    if (parsed.continued) {
      pending = {code, indent: base};
      if (i === index) answer.next = base + width;
      continue;
    }
    pending = null;
    const clean = code.trim();
    if (clean.includes(';') || /^\d+\s|^do\s+\d+\b/.test(clean) || parsed.quote) {
      stack.length = 0; continue;
    }
    const kind = kindOf(clean), top = stack.at(-1);
    let current = null, next = continuedBefore ? base : indent;
    if (kind.close && top && (kind.close === top.kind || (kind.close === 'unit' && units.includes(top.kind) && (i !== index || allowBareEnd)))) {
      current = top.indent; next = current; stack.pop();
    } else if (kind.branch && top && (kind.branch === top.kind || (kind.branch === 'contains' && [...units, 'type'].includes(top.kind)))) {
      current = top.indent + (kind.branch === 'select' ? width : 0);
      next = current + width;
    } else if (kind.open) {
      stack.push({kind: kind.open, indent: base}); next = base + width;
    }
    if (i === index) answer = {current: continuedBefore ? null : current, next};
  }
  return answer;
}
