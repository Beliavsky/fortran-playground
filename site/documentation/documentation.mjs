const get = id => document.getElementById(id);
const local = location.hostname === '127.0.0.1' || location.hostname === 'localhost';
let origin = '';
let token = '';
if (local) {
  token = new URLSearchParams(location.hash.slice(1)).get('session') || '';
  try {
    if (token) sessionStorage.setItem('local-fortran-session', token);
    else token = sessionStorage.getItem('local-fortran-session') || '';
    history.replaceState(null, '', location.pathname + location.search);
  } catch {}
}
for (const name of ['url', 'revision', 'subdirectory']) get(name).value = new URLSearchParams(location.search).get(name) || '';
async function request(path, body) {
  const response = await fetch(origin + path, {method: body ? 'POST' : 'GET',
    headers: {...(body ? {'Content-Type': 'application/json'} : {}), ...(local ? {'X-Local-Token': token} : {})},
    ...(body ? {body: JSON.stringify(body)} : {})});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || `Documentation request failed (${response.status})`);
  return result;
}
try {
  if (!local) {
    const config = await (await fetch('service.json')).json();
    if (!config.url) throw new Error('Online documentation generation has not been deployed yet. The local generator is available.');
    const url = new URL(config.url);
    if (url.protocol !== 'https:' || !url.hostname.endsWith('.modal.run') || url.pathname !== '/') throw new Error('Invalid documentation service configuration.');
    origin = url.origin;
  }
  const health = await request(local ? '/api/documentation/health' : '/api/health');
  if (!health.ok) throw new Error(health.error || 'Documentation service unavailable.');
  get('generate').disabled = false;
  get('status').textContent = `FORD ${health.ford} · Documentation service ready`;
} catch (error) {get('status').textContent = error.message;}
get('documentation-form').addEventListener('submit', async event => {
  event.preventDefault();
  get('generate').disabled = true;
  get('results').hidden = true;
  get('generation-log').hidden = true;
  get('status').textContent = 'Generating documentation. This can take a few minutes…';
  try {
    const payload = Object.fromEntries(['url', 'revision', 'subdirectory'].map(name => [name, get(name).value.trim()]));
    let result;
    if (local) result = await request('/api/documentation', payload);
    else {
      const job = await request('/api/docs', payload);
      const deadline = Date.now() + 240000;
      while (Date.now() < deadline) {
        await new Promise(resolve => setTimeout(resolve, 1500));
        const state = await request('/api/docs/' + encodeURIComponent(job.id));
        if (state.state === 'done') {result = state.result; break;}
      }
      if (!result) throw new Error('Documentation request timed out.');
    }
    if (!result.ok) throw new Error(result.error || 'Documentation generation failed.');
    if (!/^[a-f0-9]{64}$/.test(result.key)) throw new Error('Invalid documentation response.');
    const base = origin + (local ? '/documentation/view/' : '/view/') + result.key + '/';
    get('view').href = base + 'index.html';
    get('zip').href = base + 'documentation.zip';
    get('results').hidden = false;
    get('status').textContent = `${result.cached ? 'Reused cached documentation' : 'Documentation ready'} · ${result.repository} @ ${result.revision} · ${result.source_files} source files`;
    get('diagnostics').textContent = result.log || '';
    get('generation-log').hidden = !result.log;
  } catch (error) {get('status').textContent = error.message;}
  finally {get('generate').disabled = false;}
});
