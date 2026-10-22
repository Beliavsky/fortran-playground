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
assert.deepEqual(sharedCodeFromHash('#code=print%20*%2C42'), {source: 'print *,42', interfaceMode: 'simple', preprocess: false});
for (const interfaceMode of ['simple', 'advanced']) {
  const source = '! Literal text: &interface=advanced + 50%\nend\n';
  const link = createShareLink(base, source, interfaceMode);
  assert.deepEqual(sharedCodeFromHash(new URL(link).hash), {source, interfaceMode, preprocess: false});
}
for (const options of ['&interface=unknown', '&interface=', '&interface=%GG',
  '&interface=advanced&interface=simple', '&other=value']) {
  assert.throws(() => sharedCodeFromHash('#code=end' + options));
}
assert.throws(() => createShareLink(base, 'end', 'unknown'), /interface/);
assert.deepEqual(sharedCodeFromHash('#code=end&preprocess=1'), {source: 'end', interfaceMode: 'advanced', preprocess: true});
assert.deepEqual(sharedCodeFromHash('#code=end&preprocess=0'), {source: 'end', interfaceMode: 'simple', preprocess: false});
assert.deepEqual(sharedCodeFromHash(new URL(createShareLink(base, 'end', 'advanced', true)).hash),
  {source: 'end', interfaceMode: 'advanced', preprocess: true});
for (const options of ['&preprocess=yes', '&preprocess=2', '&preprocess=1&preprocess=0', '&preprocess=1&interface=simple']) {
  assert.throws(() => sharedCodeFromHash('#code=end' + options));
}
assert.throws(() => createShareLink(base, 'end', 'simple', true), /Advanced/);
assert.throws(() => createShareLink(base, 'end', 'advanced', 1), /boolean/);
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
for (const images of [1, 2, 4]) {
  assert.deepEqual(sharedCodeFromHash(new URL(createShareLink(base, 'end', 'advanced', false, images)).hash),
    {source: 'end', interfaceMode: 'advanced', preprocess: false, images});
  assert.equal(sharedCodeFromHash(`#code=end&images=${images}`).interfaceMode, 'advanced');
}
for (const suffix of ['&images=3', '&images=true', '&images=2&images=4', '&images=2&interface=simple']) {
  assert.throws(() => sharedCodeFromHash('#code=end' + suffix));
}
assert.throws(() => createShareLink(base, 'end', 'simple', false, 2), /Advanced/);
