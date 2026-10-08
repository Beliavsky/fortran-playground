import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {findQuickFix, applyQuickFix} from '../site/fixes.mjs';
const source = readFileSync(new URL('./cases/quick_fixes/print_single.bad.f90', import.meta.url), 'utf8');
const expected = readFileSync(new URL('./cases/quick_fixes/print_single.fixed.f90', import.meta.url), 'utf8');
const diagnostic = 'input_p.f90:4:13:\nError: Expected comma in I/O list at (1)\n';
assert.equal(findQuickFix(source, diagnostic), null); // Off by default.
assert.equal(findQuickFix(source, diagnostic, {enableQuickFixes: false}), null);
assert.equal(findQuickFix(source, diagnostic, {enableQuickFixes: true, compiler: 'ifx'}), null);
assert.equal(findQuickFix(source, diagnostic, {enableQuickFixes: true, disabledRules: ['print-format-comma']}), null);
const enabled = {enableQuickFixes: true};
const fix = findQuickFix(source, diagnostic, enabled);
assert.equal(fix.ruleId, 'print-format-comma');
assert.equal(applyQuickFix(source, fix), expected);
assert.equal(applyQuickFix(source.replaceAll('\n', '\r\n'), findQuickFix(source.replaceAll('\n', '\r\n'), diagnostic, enabled)), expected.replaceAll('\n', '\r\n'));
assert.throws(() => applyQuickFix(source + '! changed\n', fix), /Source changed/);
assert.throws(() => applyQuickFix(source, {...fix, start: -1}), /Invalid/);
for (const output of (['', diagnostic.replace('Error:', 'Warning:'), diagnostic.replace('input_p.f90', 'python.f90'),
  diagnostic.replace('input_p.f90', '/runtime/lapack_d.f90'), diagnostic.replace('4:13', '99:13')])) {
  assert.equal(findQuickFix(source, output, enabled), null);
}
const alreadyCorrect = source.replace("'(i0)' n", "'(i0)', n n");
assert.equal(findQuickFix(alreadyCorrect, diagnostic, enabled), null);
for (const replacement of ["print '(i0)'", "print '(i0)' ! n", "print '(i0)' )", "print '(i0)' n; print *, n", "print '(i0)' &", "! print '(i0)' n", "print *, n"] ) {
  assert.equal(findQuickFix(source.replace("print '(i0)' n", replacement), diagnostic, enabled), null);
}
// Do not repair a later cascading diagnostic past an unknown first error.
assert.equal(findQuickFix(source, 'input_p.f90:2:1:\nError: Unknown first error\n' + diagnostic, enabled), null);
assert.equal(findQuickFix(source, diagnostic.replace('I/O list', 'PRINT statement'), enabled).ruleId, fix.ruleId);
assert.equal(findQuickFix(source.replace('integer :: n = 7', 'integer :: n = &'), diagnostic, enabled), null);
const continued = source.replace('integer :: n = 7', 'integer :: n = &\n! continuation comment\n');
assert.equal(findQuickFix(continued, diagnostic.replace('4:13', '6:13'), enabled), null);
const app = readFileSync(new URL('../site/app.mjs', import.meta.url), 'utf8');
assert.ok(app.includes('quick_fix_controls.mjs')); // Optional controls use the tested engine.

const endSource = readFileSync(new URL('./cases/quick_fixes/end_program.bad.f90', import.meta.url), 'utf8');
const endExpected = readFileSync(new URL('./cases/quick_fixes/end_program.fixed.f90', import.meta.url), 'utf8');
const endDiagnostic = "input_p.f90:4:17:\nError: Expected label 'demo' for END PROGRAM statement at (1)\n";
const endFix = findQuickFix(endSource, endDiagnostic, enabled);
assert.equal(endFix.ruleId, 'closing-unit-name');
assert.equal(applyQuickFix(endSource, endFix), endExpected);
assert.equal(findQuickFix(endSource, endDiagnostic), null);
assert.equal(findQuickFix(endSource, endDiagnostic, {...enabled, disabledRules: ['closing-unit-name']}), null);
assert.equal(findQuickFix(source, diagnostic, {...enabled, disabledRules: ['closing-unit-name']}).ruleId, 'print-format-comma');
assert.equal(findQuickFix(endSource, endDiagnostic, {...enabled, disabledRules: ['print-format-comma']}).ruleId, 'closing-unit-name');
assert.equal(findQuickFix(endSource, endDiagnostic.replace("'demo'", "'another'"), enabled), null);
assert.equal(findQuickFix(endSource, endDiagnostic.replace('END PROGRAM', 'END MODULE'), enabled), null);
assert.equal(findQuickFix(endSource.replace('program Demo', '! program Demo'), endDiagnostic, enabled), null);
assert.equal(findQuickFix(endSource.replace('print', 'if (.true.) then\nprint'), endDiagnostic.replace('4:17', '5:17'), enabled), null);
assert.equal(findQuickFix(endExpected, endDiagnostic, enabled), null);
assert.equal(applyQuickFix(endSource.replaceAll('\n', '\r\n'), findQuickFix(endSource.replaceAll('\n', '\r\n'), endDiagnostic, enabled)), endExpected.replaceAll('\n', '\r\n'));
assert.equal(findQuickFix(endSource, endDiagnostic.replace("'demo'", '‘demo’'), enabled).replacement, 'Demo');
assert.throws(() => applyQuickFix(endSource + '\n', endFix), /Source changed/);
const malformed = [
  'program main\nif (.true.) then\nend program wrong\n',
  'program main\ndo\nend program wrong\n',
  'program main\ninterface\nend program wrong\n',
  'program main\ncontains\nsubroutine s()\nend program wrong\n',
  'program main\nend module main\nend program wrong\n',
  'program main\nprint *, 7; print *, 8\nend program wrong\n',
  'program main\n#unsupported\nend program wrong\n',
];
for (const text of malformed) {
  const line = text.trimEnd().split('\n').length;
  const output = `input_p.f90:${line}:1:\nError: Expected label 'main' for END PROGRAM statement at (1)\n`;
  assert.equal(findQuickFix(text, output, enabled), null, text);
}
const quoted = 'program main\nprint *, "subroutine fake()"\nend program wrong\n';
assert.ok(findQuickFix(quoted, "input_p.f90:3:1:\nError: Expected label 'main' for END PROGRAM statement at (1)\n", enabled));
console.log('Quick-fix gates, source guards and conservative refusal tests passed.');
