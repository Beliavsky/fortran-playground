import assert from 'node:assert/strict';
import {sourceFromHash, sharedCodeFromHash, createShareLink} from '../site/sharing.mjs';

const base = 'https://beliavsky.github.io/fortran-playground/';
for (const source of [
  'program main\n   print *, "Hello!"\nend program main\n',
  '! Unicode: café λ 🌍\r\nprint *, "a+b & 50% # ? ="\r\nend\r\n',
  'print *, "</script><img src=x onerror=alert(1)>"\nend\n',
  'x'.repeat(100000),
  'λ'.repeat(50000),
]) {
  const link = createShareLink(base + '?old=value#old', source);
  assert.equal(new URL(link).search, '');
  assert.equal(sourceFromHash(new URL(link).hash), source);
}
assert.equal(sourceFromHash(''), null);
assert.equal(sourceFromHash('#some-section'), null);
assert.deepEqual(sharedCodeFromHash('#code=print%20*%2C42'), {source: 'print *,42', interfaceMode: 'simple'});
for (const interfaceMode of ['simple', 'advanced']) {
  const source = '! Literal text: &interface=advanced + 50%\nend\n';
  const link = createShareLink(base, source, interfaceMode);
  assert.deepEqual(sharedCodeFromHash(new URL(link).hash), {source, interfaceMode});
}
for (const options of ['&interface=unknown', '&interface=', '&interface=%GG',
  '&interface=advanced&interface=simple', '&other=value']) {
  assert.throws(() => sharedCodeFromHash('#code=end' + options));
}
assert.throws(() => createShareLink(base, 'end', 'unknown'), /interface/);
assert.equal(sourceFromHash('#code=print%20*%2C%20%22a+b%22'), 'print *, "a+b"');
for (const hash of ['#code=%', '#code=%GG', '#code=%C3%28']) {
  assert.throws(() => sourceFromHash(hash), /invalid URL encoding/);
}
for (const hash of ['#code=', '#code=%20%0A']) assert.throws(() => sourceFromHash(hash), /empty/);
assert.throws(() => sourceFromHash('#code=' + 'x'.repeat(100001)), /100 KB/);
assert.throws(() => sourceFromHash('#code=' + encodeURIComponent('λ'.repeat(50001))), /100 KB/);
assert.throws(() => createShareLink(base, 'λ'.repeat(50001)), /100 KB/);
assert.throws(() => createShareLink(base, ' '), /empty/);
console.log('Shared-code URL round trips, Unicode, malformed input and size limits passed.');
