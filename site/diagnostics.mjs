// The service always compiles submitted source as input_p.f90. Never attribute
// helper-file errors to the user's editor, even if their line numbers coincide.
export function parseCompilerErrors(output, source) {
  const text = output.replace(/\x1b\[[0-?]*[ -/]*[@-~]/g, '').replace(/\r\n?/g, '\n');
  const locations = [...text.matchAll(/^\s*(?:-->\s*)?(.+?\.f90)(?::(\d+)(?::(\d+))?:?|\((\d+)(?:,(\d+))?\)\s*:)([^\n]*)$/gmi)];
  const lineCount = source.replace(/\r\n?/g, '\n').split('\n').length;
  const errors = [];
  const isError = /^\s*(?:(?:syntax|semantic|fatal)\s+)?(?:error|severe|catastrophic)\s*(?::|#)/i;
  for (let i = 0; i < locations.length; i++) {
    const match = locations[i];
    const path = match[1].trim().replace(/^['"]|['"]$/g, '');
    if (path.split(/[\\/]/).at(-1).toLowerCase() !== 'input_p.f90') continue;
    const line = Number(match[2] || match[4]);
    if (line < 1 || line > lineCount) continue;
    const end = locations[i + 1]?.index ?? text.length;
    const details = match[6] + text.slice(match.index + match[0].length, end);
    let message;
    // LFortran puts the diagnostic before its arrow-prefixed source location.
    if (/^\s*-->/.test(match[0])) {
      const preceding = text.slice(i ? locations[i - 1].index + locations[i - 1][0].length : 0, match.index);
      message = preceding.split('\n').slice(-8).reverse().find(item => isError.test(item));
    } else message = details.split('\n').find(item => isError.test(item));
    if (!message) continue; // Warnings, notes and location-free errors stay in the log.
    const column = Number(match[3] || match[5]) || null;
    message = message.trim();
    if (!errors.some(item => item.line === line && item.column === column && item.message === message)) {
      errors.push({line, column, message});
    }
  }
  return errors;
}
