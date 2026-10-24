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

export function combinedSource(main, external) {
  if (!external) return {source: main, mainOffset: 0, externalOffset: 0, externalLines: 0};
  const text = external.source.replace(/\r\n?/g, '\n');
  const prefix = `! External source: ${external.filename}\n! URL: ${external.url}\n! SHA-256: ${external.sha256}\n`;
  const beforeMain = prefix + text + (text.endsWith('\n') ? '' : '\n') + '\n! Editor source: main.f90\n';
  const source = beforeMain + main;
  if (new TextEncoder().encode(source).length > 100000) {
    throw new Error('External source and editor code together exceed the 100 KB source limit.');
  }
  return {source, mainOffset: beforeMain.split('\n').length - 1,
    externalOffset: 3, externalLines: text.split('\n').length - (text.endsWith('\n') ? 1 : 0),
    filename: external.filename};
}

export function mappedErrors(errors, compilation) {
  const main = [], external = [];
  for (const error of errors) {
    if (error.line > compilation.mainOffset) main.push({...error, line: error.line - compilation.mainOffset});
    else if (error.line > compilation.externalOffset && error.line <= compilation.externalOffset + compilation.externalLines) {
      external.push({...error, line: error.line - compilation.externalOffset});
    }
  }
  return {main, external};
}
