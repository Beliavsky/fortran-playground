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
  try {
    source = decodeURIComponent(encodedSource);
    if (options.length) {
      if (options.length !== 1 || !options[0].startsWith('interface=')) {
        throw new Error('Unknown shared-link option.');
      }
      interfaceMode = decodeURIComponent(options[0].slice('interface='.length));
    }
  }
  catch (error) {
    if (error instanceof URIError) throw new Error('The shared-code link contains invalid URL encoding.');
    throw error;
  }
  if (!['simple', 'advanced'].includes(interfaceMode)) throw new Error('Shared-link interface must be simple or advanced.');
  validateSource(source);
  return {source, interfaceMode};
}

export function sourceFromHash(hash) {
  return sharedCodeFromHash(hash)?.source ?? null;
}

export function createShareLink(href, source, interfaceMode = 'simple') {
  validateSource(source);
  if (!['simple', 'advanced'].includes(interfaceMode)) throw new Error('Shared-link interface must be simple or advanced.');
  const url = new URL(href);
  url.search = '';
  url.hash = `code=${encodeURIComponent(source)}&interface=${interfaceMode}`;
  return url.href;
}
