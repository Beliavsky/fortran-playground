import assert from 'node:assert/strict';
import {parseURLSettings} from '../site/url_settings.mjs';

assert.deepEqual(parseURLSettings('?interface=compare').settings, {interface: 'compare'});
assert.deepEqual(parseURLSettings('?compiler=ifx&standard=2018&preprocess=1').settings,
  {compiler: 'ifx', standard: '2018', preprocess: true, interface: 'advanced'});
assert.deepEqual(parseURLSettings('?compilers=gfortran,ifx,flang&example=01_arithmetic').settings,
  {compilers: ['gfortran', 'ifx', 'flang'], example: '01_arithmetic', interface: 'compare'});
assert.deepEqual(parseURLSettings('?owner=1&utm_source=forum').settings, {});
for (const query of ['?interface=bogus', '?compiler=unknown', '?compilers=gfortran,unknown',
  '?compilers=gfortran,gfortran', '?standard=2029', '?preprocess=true', '?example=../bad',
  '?interface=compare&interface=advanced', '?compiler=', '?compilers=']) {
  assert.ok(parseURLSettings(query).warnings.length, query);
}
assert.deepEqual(parseURLSettings('?interface=simple&compiler=ifx&preprocess=1').settings, {interface: 'simple'});
assert.deepEqual(parseURLSettings('?interface=advanced&compilers=gfortran,ifx').settings, {interface: 'advanced'});
console.log('URL settings validation, mode inference, duplicates, and conflicts passed.');
