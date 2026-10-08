import {parseCompilerErrors} from './diagnostics.mjs';

const PRINT_COMMA = 'print-format-comma';
const END_NAME = 'closing-unit-name';

// Inspect a single physical statement, respecting doubled quotes and comments.
// Continuations, preprocessor lines and multiple statements are deliberately
// outside this initial rule's scope.
function codePart(line) {
  let quote = null;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (quote) {
      if (ch === quote) {
        if (line[i + 1] === quote) i++;
        else quote = null;
      }
    } else if (ch === '"' || ch === "'") quote = ch;
    else if (ch === '!') return line.slice(0, i);
    else if (ch === '&' || ch === ';' || ch === '#') return null;
  }
  return quote ? null : line;
}

function printComma(source, error) {
  if (!/^Error:\s*Expected comma in (?:I\/O list|PRINT statement)\b/i.test(error.message)) return null;
  const lines = [...source.matchAll(/[^\r\n]*(?:\r\n|\r|\n|$)/g)];
  const physical = lines[error.line - 1];
  if (!physical) return null;
  // Refuse a line continued from an earlier statement, including continuation
  // followed by comment-only or blank physical lines.
  for (let previous = error.line - 2; previous >= 0; previous--) {
    const preceding = lines[previous][0].trim();
    if (!preceding || preceding.startsWith('!')) continue;
    if (codePart(preceding) === null) return null;
    break;
  }
  const line = codePart(physical[0].replace(/[\r\n]+$/, ''));
  if (line === null) return null;
  const header = /^\s*(?:\d+\s+)?print\s+(['"])/i.exec(line);
  if (!header) return null;
  const opening = header[0].length - 1, quote = header[1];
  let closing = opening + 1;
  while (closing < line.length) {
    if (line[closing] !== quote) closing++;
    else if (line[closing + 1] === quote) closing += 2;
    else break;
  }
  if (closing >= line.length) return null;
  const format = line.slice(opening + 1, closing).trim();
  if (!format.startsWith('(') || !format.endsWith(')')) return null;
  const rest = line.slice(closing + 1).trimStart();
  // A comma already present means the error is elsewhere in the I/O list.
  // Require an actual item, not an empty statement or a stray closing delimiter.
  if (!rest || !/^[a-z\d_'".+-]/i.test(rest)) return null;
  const start = physical.index + closing + 1;
  return Object.freeze({ruleId: PRINT_COMMA, description: 'Insert a comma after the PRINT format.',
    start, end: start, replacement: ',', originalSource: source, line: error.line});
}

function closingName(source, error) {
  const diagnostic = /^Error:\s+Expected (?:label|name)\s+['‘“"]([a-z]\w*)['’”"]\s+for\s+END\s+(PROGRAM|MODULE|SUBROUTINE|FUNCTION)\s+statement\b/i.exec(error.message);
  if (!diagnostic) return null;
  const expected = diagnostic[1].toLowerCase(), kind = diagnostic[2].toLowerCase();
  const lines = [...source.matchAll(/[^\r\n]*(?:\r\n|\r|\n|$)/g)];
  const stack = [];
  for (let i = 0; i < error.line; i++) {
    if (!lines[i]) return null;
    const code = codePart(lines[i][0].replace(/[\r\n]+$/, ''));
    if (code === null) return null;
    const line = code.replace(/^\s*\d+\s+/, '').trim();
    if (!line) continue;
    const closing = /^end\s*(program|module|subroutine|function)\s+([a-z]\w*)\s*$/i.exec(line);
    if (i === error.line - 1) {
      const top = stack.at(-1);
      if (!closing || !top || top.kind !== kind || closing[1].toLowerCase() !== kind
          || top.name?.toLowerCase() !== expected || closing[2].toLowerCase() === expected) return null;
      const start = lines[i].index + code.lastIndexOf(closing[2]);
      return Object.freeze({ruleId: END_NAME, description: `Change the END ${kind.toUpperCase()} name to ${top.name}.`,
        start, end: start + closing[2].length, replacement: top.name, originalSource: source, line: error.line});
    }
    if (closing || /^end\s*$/i.test(line)) {
      const top = stack.at(-1);
      if (!top?.name || (closing && (top.kind !== closing[1].toLowerCase() || top.name.toLowerCase() !== closing[2].toLowerCase()))) return null;
      stack.pop(); continue;
    }
    const ending = /^end\s*(if|do)(?:\s+([a-z]\w*))?\s*$/i.exec(line);
    if (ending) {
      const top = stack.at(-1);
      if (top?.kind !== ending[1].toLowerCase() || (ending[2]?.toLowerCase() || null) !== (top.label?.toLowerCase() || null)) return null;
      stack.pop(); continue;
    }
    if (/^contains\s*$/i.test(line)) {
      const top = stack.at(-1);
      if (!top?.name || top.contains) return null;
      top.contains = true; continue;
    }
    let opening = /^(program|module)\s+([a-z]\w*)\s*$/i.exec(line);
    if (opening) {
      if (stack.length) return null;
      stack.push({kind: opening[1].toLowerCase(), name: opening[2]}); continue;
    }
    // Deliberately accept only simple, complete procedure headers; BIND,
    // derived-type results and continued headers need a fuller parser.
    opening = /^(?:(?:pure|impure|elemental|recursive|non_recursive)\s+)*(?:(?:integer|real|logical|complex|character)(?:\s*\([^()]*\)|\s*\*\s*\d+)?\s+|double\s+precision\s+)?(subroutine|function)\s+([a-z]\w*)\s*\([^()]*\)\s*(?:result\s*\(\s*[a-z]\w*\s*\))?\s*$/i.exec(line);
    if (opening) {
      const parent = stack.at(-1);
      if (parent && (!parent.contains || !['program', 'module'].includes(parent.kind))) return null;
      stack.push({kind: opening[1].toLowerCase(), name: opening[2]}); continue;
    }
    const construct = /^(?:([a-z]\w*)\s*:\s*)?(if\s*\(.*\)\s*then|do(?:\s+while\s*\(.*\)|\s+[a-z]\w*\s*=.+)?)\s*$/i.exec(line);
    if (construct) {
      if (!stack.at(-1)?.name && !['if', 'do'].includes(stack.at(-1)?.kind)) return null;
      stack.push({kind: /^if/i.test(construct[2]) ? 'if' : 'do', label: construct[1] || null}); continue;
    }
    // Refuse unrecognised structural statements rather than guessing scope.
    // This also rules out interface bodies, module procedures and old labelled DO.
    const structural = line.replace(/'(?:''|[^'])*'|"(?:""|[^"])*"/g, ' ');
    if (/^(?:[a-z]\w*\s*:\s*)?(?:end\b|end(?:if|do|select|type|interface|associate|block|forall|where)\b|program\b|module\b|submodule\b|subroutine\b|function\b|do\b|select\b|block\b|associate\b|interface\b|abstract\s+interface\b|enum\b|type(?:\s|,|::)|where\b|forall\b)/i.test(structural)
        || /\b(?:subroutine|function)\s+[a-z]\w*\s*\(/i.test(structural)) return null;
  }
  return null;
}

// Off by default for callers; the web interface explicitly uses its configuration. Individual rules can
// also be disabled without changing diagnostics, compilation or execution.
export function findQuickFix(source, output, {enableQuickFixes = false, compiler = 'gfortran', disabledRules = []} = {}) {
  if (!enableQuickFixes || compiler !== 'gfortran') return null;
  const error = parseCompilerErrors(output, source)[0];
  if (!error) return null;
  return (!disabledRules.includes(PRINT_COMMA) ? printComma(source, error) : null)
    || (!disabledRules.includes(END_NAME) ? closingName(source, error) : null);
}

export function applyQuickFix(source, fix) {
  if (!fix || source !== fix.originalSource) throw new Error('Source changed; compile again before applying a fix.');
  if (!Number.isInteger(fix.start) || !Number.isInteger(fix.end) || fix.start < 0 || fix.end < fix.start || fix.end > source.length) {
    throw new Error('Invalid quick-fix range.');
  }
  return source.slice(0, fix.start) + fix.replacement + source.slice(fix.end);
}
