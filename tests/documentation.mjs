import assert from 'node:assert/strict';
const realTimeout = globalThis.setTimeout;
for (const mode of ['online', 'local', 'unconfigured', 'failure']) {
  const elements = new Map();
  const get = id => {
    if (!elements.has(id)) elements.set(id, {value:'', disabled:true, hidden:true, textContent:'', listeners:{},
      addEventListener(name, fn) {this.listeners[name] = fn;}});
    return elements.get(id);
  };
  globalThis.document = {getElementById:get};
  globalThis.location = new URL((mode === 'local' ? 'http://127.0.0.1:8766' : 'https://example.test') +
    '/documentation/?url=https%3A%2F%2Fgithub.com%2Fa%2Fb&revision=abc&subdirectory=packages%2Fone');
  globalThis.sessionStorage = {getItem() {return 'private';}};
  const calls = [];
  globalThis.fetch = async (url, options = {}) => {
    calls.push({url,options});
    if (url === 'service.json') return {json:async()=>({url:mode === 'unconfigured' ? '' : 'https://test.modal.run'})};
    if (mode === 'local') assert.equal(options.headers['X-Local-Token'],'private');
    if (url.endsWith('/health')) return {ok:true,json:async()=>({ok:true,ford:'7.0.13'})};
    if (mode === 'failure') return {ok:false,status:429,json:async()=>({error:'Both documentation slots are busy.'})};
    const result = {ok:true,key:'a'.repeat(64),repository:'a/b',revision:'b'.repeat(40),source_files:1,cached:true};
    return {ok:true,json:async()=>mode === 'local' ? result : url.endsWith('/api/docs') ? {id:'job'} : {state:'done',result}};
  };
  globalThis.setTimeout = fn => realTimeout(fn,0);
  await import(`../site/documentation/documentation.mjs?case=${mode}`);
  assert.equal(get('url').value,'https://github.com/a/b');
  if (mode === 'unconfigured') {
    assert.equal(get('generate').disabled,true);assert.match(get('status').textContent,/not been deployed/);continue;
  }
  assert.equal(get('generate').disabled,false);
  await get('documentation-form').listeners.submit({preventDefault(){}});
  if (mode === 'failure') assert.match(get('status').textContent,/slots are busy/);
  else {
    const submitted = calls.find(c=>c.options.method === 'POST');
    assert.deepEqual(JSON.parse(submitted.options.body),{url:'https://github.com/a/b',revision:'abc',subdirectory:'packages/one'});
    assert.equal(get('results').hidden,false);assert.match(get('view').href,/index.html$/);assert.match(get('zip').href,/documentation.zip$/);
  }
  assert.equal(get('generate').disabled,false);
}
globalThis.setTimeout = realTimeout;
console.log('Documentation UI: online/local generation, deep links, errors and disabled service passed.');
