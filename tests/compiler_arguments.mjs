import assert from 'node:assert/strict';
import {compilerArguments, optionTokens} from '../site/compiler_arguments.mjs';

const spec = {presets: {default: [], debug: ['-O0', '-g']},
  standards: {'2018': ['-stand', 'f18']}, extras: {warnings: ['-warn', 'all']},
  additional_options: {optimization: [['-O0'], ['-O2'], ['-O3']], debug: [['-g']],
    warnings: [['-warn', 'all']]}};
assert.deepEqual(optionTokens('  -O2 \t-warn all\n'), ['-O2', '-warn', 'all']);
assert.deepEqual(optionTokens('  '), []);
assert.deepEqual(compilerArguments(spec, {standard: '2018'}, ['-O2', '-warn', 'all']),
  ['-stand', 'f18', '-O2', '-warn', 'all']);
assert.deepEqual(compilerArguments(spec, {warnings: true}, ['-warn', 'all']),
  ['-warn', 'all', '-warn', 'all']);
assert.throws(() => compilerArguments(spec, {preset: 'debug'}, ['-O2']), /Conflicting optimization/);
assert.throws(() => compilerArguments(spec, {}, ['-O2', '-O3']), /Conflicting optimization/);
for (const args of [['-warn'], ['-warn', 'none'], ['-o', 'other.exe'], ['@response'],
  ['-O2;echo bad'], [null], Array(33).fill('-g'), ['x'.repeat(129)]]) {
  assert.throws(() => compilerArguments(spec, {}, args));
}
assert.throws(() => compilerArguments({}, {}, ['-O2']), /unavailable/);
assert.deepEqual(compilerArguments({}, {}, []), []);
console.log('Compiler option token validation, multi-part flags, and conflicts passed.');
