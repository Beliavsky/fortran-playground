export function sourceURL(value) {
  const text = value.trim();
  let url;
  try { url = new URL(text); }
  catch { throw new Error('Enter a complete HTTPS URL for a raw Fortran source file.'); }
  if (text.length > 2048 || url.protocol !== 'https:' || url.username || url.password ||
      url.hash || (url.port && url.port !== '443')) {
    throw new Error('Use a public HTTPS URL without credentials, a fragment, or a custom port.');
  }
  return url.href;
}

export function combinedSource(main, externals) {
  const files = (Array.isArray(externals) ? externals : externals ? [externals] : []).filter(Boolean);
  if (files.length > 5) throw new Error('At most five external source files are supported.');
  let beforeMain = '';
  const ranges = [];
  for (const external of files) {
    const text = external.source.replace(/\r\n?/g, '\n');
    const prefix = `! External source: ${external.filename}\n! URL: ${external.url}\n! SHA-256: ${external.sha256}\n`;
    const offset = beforeMain.split('\n').length - 1 + 3;
    ranges.push({offset, lines: text.split('\n').length - (text.endsWith('\n') ? 1 : 0), filename: external.filename, url: external.url});
    beforeMain += prefix + text + (text.endsWith('\n') ? '' : '\n') + '\n';
  }
  if (files.length) beforeMain += '! Editor source: main.f90\n';
  const source = beforeMain + main;
  if (new TextEncoder().encode(source).length > 100000) {
    throw new Error('External sources and editor code together exceed the 100 KB source limit.');
  }
  return {source, mainOffset: beforeMain.split('\n').length - 1, ranges};
}

export function mappedErrors(errors, compilation) {
  const main = [], external = [];
  for (const error of errors) {
    if (error.line > compilation.mainOffset) main.push({...error, line: error.line - compilation.mainOffset});
    else {
      const range = compilation.ranges.find(range => error.line > range.offset && error.line <= range.offset + range.lines);
      if (range) external.push({...error, line: error.line - range.offset, filename: range.filename, url: range.url});
    }
  }
  return {main, external};
}
