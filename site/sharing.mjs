const MAX_SOURCE_BYTES = 100000;

function validateSource(source) {
  if (!source.trim()) throw new Error('Shared code is empty.');
  if (new TextEncoder().encode(source).length > MAX_SOURCE_BYTES) {
    throw new Error('Shared code exceeds the 100 KB source limit.');
  }
}

export function sourceFromHash(hash) {
  if (!hash.startsWith('#code=')) return null;
  // One UTF-8 byte needs at most three characters in percent-encoded form.
  if (hash.length > 6 + MAX_SOURCE_BYTES*3) {
    throw new Error('Shared code exceeds the 100 KB source limit.');
  }
  let source;
  try { source = decodeURIComponent(hash.slice(6)); }
  catch { throw new Error('The shared-code link contains invalid URL encoding.'); }
  validateSource(source);
  return source;
}

export function createShareLink(href, source) {
  validateSource(source);
  const url = new URL(href);
  url.search = '';
  url.hash = `code=${encodeURIComponent(source)}`;
  return url.href;
}
