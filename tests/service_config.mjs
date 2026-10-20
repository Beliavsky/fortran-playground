import assert from 'node:assert/strict';
import {serviceOrigin} from '../site/service_config.mjs';

for (const origin of ['https://test.modal.run', 'https://execute.example.org', 'https://execute.example.org:8443']) {
  assert.equal(serviceOrigin(origin + '/'), origin);
}
for (const value of [undefined, null, {}, '', '/api', 'not a URL',
  'http://execute.example.org', 'javascript:alert(1)', 'file:///tmp/service',
  'https://user:secret@example.org', 'https://example.org/api',
  'https://example.org/?token=secret', 'https://example.org/#fragment']) {
  assert.throws(() => serviceOrigin(value), /HTTPS origin/);
}
console.log('Execution service origins support HTTPS hosts and reject unsafe configurations.');
