// Local-only validation. No Modal requests; no changes to the web interface.
import assert from 'node:assert/strict';
import {mkdtempSync, readFileSync, writeFileSync, rmSync, mkdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname, join, resolve, relative, isAbsolute, sep} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {spawnSync} from 'node:child_process';
import {findQuickFix, applyQuickFix} from './site/fixes.mjs';

const root = dirname(fileURLToPath(import.meta.url));
const fixtures = join(root, 'tests', 'cases', 'quick_fixes');
const normalize = text => text.trim().replace(/\s+/g, ' ');

export function validateCases({log = console.log} = {}) {
  const started = performance.now();
  const version = spawnSync('gfortran', ['--version'], {encoding: 'utf8', timeout: 10000});
  if (version.error || version.status !== 0) throw new Error('gfortran must be installed and on PATH.');
  const directory = mkdtempSync(join(tmpdir(), 'fortran-quick-fixes-'));
  const results = [];
  const cases = JSON.parse(readFileSync(join(fixtures, 'cases.json'), 'utf8'));
  function compile(source) {
    writeFileSync(join(directory, 'input_p.f90'), source);
    const result = spawnSync('gfortran', ['-std=f2018', '-Wall', '-Wextra', '-fdiagnostics-color=never',
      '-fmax-errors=1', 'input_p.f90', '-o', 'program.exe'], {
      cwd: directory, encoding: 'utf8', timeout: 30000, maxBuffer: 1024 * 1024,
      env: {...process.env, LC_ALL: 'C', LANG: 'C'},
    });
    if (result.error) throw result.error;
    return {status: result.status, output: result.stdout + result.stderr};
  }
  try {
    for (const item of cases) {
      const source = readFileSync(join(fixtures, item.name + (item.fix ? '.bad.f90' : '.f90')), 'utf8');
      const record = {name: item.name, expectedFix: Boolean(item.fix), ok: false};
      try {
        record.before = compile(source);
        assert.equal(record.before.status === 0, Boolean(item.compiles), 'unexpected original compilation status');
        if (item.warning) assert.match(record.before.output, /Warning:/, 'expected a real compiler warning');
        const fix = findQuickFix(source, record.before.output, {enableQuickFixes: true});
        assert.equal(Boolean(fix), Boolean(item.fix), 'unexpected fix availability');
        if (fix) {
          record.rule = fix.ruleId;
          record.correctedSource = applyQuickFix(source, fix);
          const expected = readFileSync(join(fixtures, item.name + '.fixed.f90'), 'utf8');
          assert.equal(record.correctedSource, expected, 'correction differs from expected source');
          record.after = compile(record.correctedSource);
          assert.equal(record.after.status, 0, record.after.output);
          assert.equal(findQuickFix(record.correctedSource, record.after.output, {enableQuickFixes: true}), null);
          const run = spawnSync(join(directory, 'program.exe'), [], {
            cwd: directory, encoding: 'utf8', timeout: 10000, maxBuffer: 1024 * 1024,
          });
          if (run.error) throw run.error;
          assert.equal(run.status, 0, run.stderr);
          assert.equal(normalize(run.stdout), item.stdout, 'corrected program output differs');
          record.stdout = run.stdout;
        }
        record.ok = true;
        log(`PASS ${item.name}: ${fix ? 'failed -> exact correction -> compiled -> output matched' : 'no fix offered'}`);
      } catch (error) { record.error = String(error); log(`FAIL ${item.name}: ${record.error}`); }
      results.push(record);
    }
  } finally {
    // Delete only the directory returned by mkdtemp, after verifying its scope.
    const within = relative(resolve(tmpdir()), resolve(directory));
    if (!within || isAbsolute(within) || within === '..' || within.startsWith('..' + sep)
        || !within.startsWith('fortran-quick-fixes-')) throw new Error('Unsafe temporary cleanup target');
    rmSync(directory, {recursive: true, force: true});
  }
  const report = {compiler: version.stdout.split(/\r?\n/)[0], seconds: (performance.now() - started) / 1000,
    passed: results.filter(item => item.ok).length, total: results.length, cases: results};
  log(`${report.passed}/${report.total} cases passed in ${report.seconds.toFixed(2)} s (${report.compiler}).`);
  return report;
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  const args = process.argv.slice(2);
  if (args.includes('--help')) {
    console.log('Usage: node xcheck_fixes.mjs [--report FILE.json]\nCompile malformed fixtures, apply JavaScript fixes, recompile and verify output.');
  } else {
    try {
      if (args.length && (args.length !== 2 || args[0] !== '--report')) throw new Error('Usage: node xcheck_fixes.mjs [--report FILE.json]');
      const report = validateCases();
      if (args.length) {
        const path = resolve(args[1]); mkdirSync(dirname(path), {recursive: true});
        writeFileSync(path, JSON.stringify(report, null, 2) + '\n');
        console.log(`Saved ${path}`);
      }
      if (report.passed !== report.total) process.exitCode = 1;
    } catch (error) { console.error(String(error)); process.exitCode = 1; }
  }
}
