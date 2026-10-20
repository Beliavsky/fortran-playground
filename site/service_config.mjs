export function serviceOrigin(value) {
  let url;
  try { url = new URL(value); } catch { /* Report all invalid configurations consistently. */ }
  if (typeof value !== 'string' || !url || url.protocol !== 'https:' ||
      url.username || url.password || url.search || url.hash || url.pathname !== '/') {
    throw new Error('Expected the HTTPS origin of the execution service (no path, credentials, query, or fragment).');
  }
  return url.origin;
}
