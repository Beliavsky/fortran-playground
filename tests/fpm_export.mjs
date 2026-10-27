import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {githubRepository, pinnedSource, projectFiles, zipFiles} from '../site/fpm/project_export.mjs';

const packages = JSON.parse(readFileSync(new URL('../site/fpm/packages.json', import.meta.url), 'utf8'));
const runtime = JSON.parse(readFileSync(new URL('../site/fpm/project-runtime.json', import.meta.url), 'utf8'));
const source = 'program main\n! edited main: \u03c0\nprint *, 42\nend program\n';
for (const packageEntry of packages) {
  assert.equal(pinnedSource(packageEntry), `https://github.com/${packageEntry.repository}/tree/${packageEntry.revision}`);
  const files = projectFiles({source, stdin: '2\n3\n', url: `https://github.com/${packageEntry.repository}.git`,
    revision: packageEntry.revision, packages, runtime});
  assert.equal(files['app/main.f90'], source);
  assert.equal(files['stdin.txt'], '2\n3\n');
  const {source: example, ...settings} = packageEntry;
  assert.deepEqual(JSON.parse(files['playground.json']).package, settings, 'All dependency locks, flags and patches survive export');
  assert.equal(files['run.py'], runtime['run.py']);
}
for (const value of ['file:///C:/code', 'https://evil.com/o/r', 'https://github.com/o/r/tree/main',
  'https://u:p@github.com/o/r', 'https://github.com/o/r?x=1']) assert.equal(githubRepository(value), '');
assert.equal(pinnedSource({...packages[0], revision: 'main'}), '');
assert.throws(() => projectFiles({source: '', url: 'https://github.com/o/r', revision: '', packages, runtime}), /main program/);
assert.throws(() => projectFiles({source, url: 'https://github.com/o/r', revision: 'bad\nrev', packages, runtime}), /revision/);
const files = projectFiles({source, url: 'https://github.com/custom/library', revision: 'main', packages, runtime});
assert.equal(JSON.parse(files['playground.json']).package, undefined);
assert.equal(files['stdin.txt'], undefined);
assert.match(files['README.md'], /not an offline source bundle/);
const zip = zipFiles(files);
// An independent ZIP reader checks CRCs, entry paths, byte encoding and payload.
execFileSync(process.env.PYTHON || 'python', ['-c',
  'import sys,io,zipfile; z=zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read())); assert z.testzip() is None; '
  + 'assert "tools/fpm_sources.py" in z.namelist(); assert "π" in z.read("app/main.f90").decode("utf-8"); '
  + 'assert z.read("playground.json").decode("utf-8").find("custom/library")>=0'],
  {input: Buffer.from(await zip.arrayBuffer())});
assert.throws(() => zipFiles({'../escape': 'bad'}), /ZIP path/);
console.log('FPM project exports preserve edited code, stdin, dependency pins, patches and build settings; ZIP CRCs and UTF-8 passed.');
