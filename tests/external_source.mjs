import assert from 'node:assert/strict';
import {sourceURL, combinedSource, mappedErrors} from '../site/external_source.mjs';
const external = {filename: 'sample.f90', url: 'https://example.org/sample.f90', sha256: 'a'.repeat(64),
  source: 'module sample\r\nend module\r\n'};
const main = 'program main\nuse sample\nend program\n';
const combined = combinedSource(main, external);
assert.equal(combined.source.split('\n')[combined.mainOffset], 'program main');
assert.equal(combined.source.split('\n')[combined.externalOffset], 'module sample');
assert.ok(combined.source.indexOf('end module') < combined.source.indexOf('program main'));
assert.equal(combinedSource(main, null).source, main);
assert.deepEqual(mappedErrors([{line: 4, message: 'external error'},
  {line: combined.mainOffset + 2, message: 'main error'}], combined), {
  main: [{line: 2, message: 'main error'}], external: [{line: 1, message: 'external error'}]});
assert.throws(() => combinedSource('x'.repeat(100000), external), /100 KB/);
assert.equal(sourceURL('https://example.org/module.f90'), 'https://example.org/module.f90');
for (const value of ['http://example.org/x', 'file:///x', 'https://user:pass@example.org/x',
  'https://example.org:9000/x', 'https://example.org/x#part', 'not a URL']) assert.throws(() => sourceURL(value));
console.log('External source ordering, size limits, URL validation, and diagnostic mappings passed.');
