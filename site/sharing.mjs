const MAX_SOURCE_BYTES = 100000;

function validateSource(source) {
  if (!source.trim()) throw new Error('Shared code is empty.');
  if (new TextEncoder().encode(source).length > MAX_SOURCE_BYTES) {
    throw new Error('Shared code exceeds the 100 KB source limit.');
  }
}

export function sharedCodeFromHash(hash) {
  if (!hash.startsWith('#code=')) return null;
  const [encodedSource, ...options] = hash.slice(6).split('&');
  // One UTF-8 byte needs at most three characters in percent-encoded form.
  if (encodedSource.length > MAX_SOURCE_BYTES*3) {
    throw new Error('Shared code exceeds the 100 KB source limit.');
  }
  let source;
  let interfaceMode = 'simple';
  let preprocess = false;
  const seen = new Set();
  try {
    source = decodeURIComponent(encodedSource);
    for (const option of options) {
      const separator = option.indexOf('=');
      const key = option.slice(0, separator);
      const value = decodeURIComponent(option.slice(separator + 1));
      if (separator < 0 || seen.has(key) || !['interface', 'preprocess'].includes(key)) throw new Error('Unknown or duplicate shared-link option.');
      seen.add(key);
      if (key === 'interface') interfaceMode = value;
      else {
        if (!['0', '1'].includes(value)) throw new Error('Shared-link preprocess must be 0 or 1.');
        preprocess = value === '1';
      }
    }
  }
  catch (error) {
    if (error instanceof URIError) throw new Error('The shared-code link contains invalid URL encoding.');
    throw error;
  }
  if (!['simple', 'advanced'].includes(interfaceMode)) throw new Error('Shared-link interface must be simple or advanced.');
  if (preprocess) {
    if (seen.has('interface') && interfaceMode === 'simple') throw new Error('Preprocessing requires the Advanced interface.');
    interfaceMode = 'advanced';
  }
  validateSource(source);
  return {source, interfaceMode, preprocess};
}

export function sourceFromHash(hash) {
  return sharedCodeFromHash(hash)?.source ?? null;
}

export function createShareLink(href, source, interfaceMode = 'simple', preprocess = false) {
  validateSource(source);
  if (typeof preprocess !== 'boolean') throw new Error('Preprocessing must be a boolean.');
  if (preprocess && interfaceMode === 'simple') throw new Error('Preprocessing requires the Advanced interface.');
  if (!['simple', 'advanced'].includes(interfaceMode)) throw new Error('Shared-link interface must be simple or advanced.');
  const url = new URL(href);
  url.search = '';
  url.hash = `code=${encodeURIComponent(source)}&interface=${interfaceMode}${preprocess ? '&preprocess=1' : ''}`;
  return url.href;
}
