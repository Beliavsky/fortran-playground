# Ten checked command-line, testing and workflow drivers

Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox on their first verification runs. Every run reused the existing package library and compiled only the main and executable. The [verification report](gams-workflows-ten-validation.json) preserves pins, normalized source hashes, timings and complete output. GAMS categories are not exhausted.

## Independent references and limits

The argparse consumer relaunches its own executable twelve times with generated options. Parsed integers, exact binary reals, quoted labels, absent defaults and present/absent flags are compared with the generating parameters. M_CLI converts 32 generated prototypes into native NAMELIST text; the native reader must recover all 224 values. These are bounded parser examples, not all-syntax or invalid-input conformance suites.

Veggies equality result flags follow a 17-by-17 integer truth table, and combined objects must report exact assertion/failure counts. Its test runner executes two passing specifications. Julienne independently checks 289 integer comparisons and 765 dyadic absolute-tolerance outcomes against integer inequalities, including inclusive boundaries. Intentionally failed result objects are inspected successfully rather than ignored. Arithmetic inside these consumers belongs to the examples, not the testing libraries.

Tcl finite sums are checked against n*(n+1)*(2*n+1)/6 for n=0..64; a malformed expression must fail and the interpreter must subsequently recover. Four fixed local printf pipes are checked for all 170 ordered records, end of output and close status. The Linux filesystem example checks 65 binary file lifecycles and directory/file classification. No network or host-system access is added.

The gFTL consumer checks 55,872 integer prefix values and 1,152 closed-form prefix sums. FyCollections integer list edits follow plain-array oracles; integer/string contents, exact search indices and missing searches are checked after every step. These exercise the existing audited template instantiations, not arbitrary generated types.

The history consumer records twelve commands, edits each via a scratch directive unit, then recalls each original to establish that substitutions did not overwrite history. It uses the supported 1024-character buffers and executes no recorded text as shell code. All successful sources were saved directly; this batch produced no failed service probes.

### argparse-f (N3)

Independent API consumer; pinned sources and available author examples reviewed. 12 bounded self-invocations with short/long integer option names, signed dyadic doubles, quoted labels with spaces, absent integer defaults and present/absent logical flags. 72 exact references. Invalid options, help exits, positional/named arguments and all parser syntaxes unverified.

### veggies (S3)

Independent API consumer; pinned sources and available author examples reviewed. 289 exact integer equality outcomes, 17 combined assertion/failure counts, plus two passing test-runner cases checking 64 integer sums and an exact binary real. The arithmetic examples are user calculations, not numerical algorithms supplied by Veggies. Intentionally failed result objects are inspected without running a failing suite. Filtering, generators, full diagnostics and parallelism unverified.

### m-system (N1)

Independent API consumer; pinned sources and available author examples reviewed. 65 Linux sandbox file create/read/remove traces under an owner-only directory. Generated binary contents and native directory/regular-file predicates are checked; files and directory must disappear after removal. Other system calls, permissions inspection, symlinks and Windows behavior unverified.

### fortran-tcl86 (S)

Independent API consumer; pinned sources and available author examples reviewed. Tcl computes sums of squares for n=0..64, compared with independent integer closed forms. One malformed expression must produce nonempty error text; a subsequent expression must return 56. One reused interpreter, no GUI/network. Other bindings, callbacks, arbitrary scripts and thread safety unverified.

### julienne (S3)

Independent API consumer; pinned sources and available author examples reviewed. 289 integer equality and 765 default-real absolute-tolerance outcomes, including exact boundary acceptance and zero tolerance. Inputs are exact dyadics and expected flags follow integer inequalities. One failed diagnosis retains an appended annotation. Relative/percentage tolerances, arrays, nonfinite inputs, macro termination and multi-image testing unverified.

### m-process (S)

Independent API consumer; pinned sources and available author examples reviewed. Four fixed local printf read pipes return 170 independently generated integer records; order, end of output and successful process_close status are checked. Sandbox restrictions remain in effect. Write pipes, arbitrary commands, stderr/nonzero-status handling, interactive terminals and Windows behavior unverified.

### gftl (N4)

Independent API consumer; pinned sources and available author examples reviewed. 12 vectors with 96 appends each through the existing audited integer instantiation. 55,872 reverse-order prefix values and 1,152 independent closed-form prefix sums, with append status and size checks. Other templates/types, deletion, iterators, copies, clear/reuse and memory leaks unverified.

### m_history (N3)

Independent API consumer; pinned sources and available author examples reviewed. 12 generated original history commands, each recalled and edited with a scripted numeric substitution, then recalled again to require the unchanged original. Uses supported 1024-character line buffers and scratch directive units; no shell command is executed. Short buffers, other editing directives, interactive terminals and malformed history commands unverified.

### m_cli (N3)

Independent API consumer; pinned sources and available author examples reviewed. 32 generated default prototypes converted to native NAMELIST text. Exact integer, dyadic real, three-element real array, alternating logical and quoted label references; 224 values. Repeated calls exercise dictionary reinitialization. Actual CLI overrides, malformed input, help paths and all quoting rules unverified.

### fycollections (N4)

Independent API consumer; pinned sources and available author examples reviewed. Eight fresh integer/string list traces of 48 steps. Plain integer-array oracles follow append/middle insertion/deletion; every integer and string element and exact lookup index is checked in reverse after each step, plus absent searches and allocatable destruction. Generated author IntList/StringList specializations only; string insert/delete, negative indexing, list copies and other types unverified.

## Provenance and actual output

Pinned APIs, implementations and available author examples were reviewed. These independent MIT consumers do not copy upstream implementation/example bodies; upstream license terms remain separate. Only each recorded class and tested scope is verified. Loading an example does not submit a job.

### argparse-options-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=argparse-f&example=gams-argparse-options-reference) / [Driver source](../fpm_catalog/gams-drivers/argparse-options-reference.f90) / [Pinned procedure](https://github.com/0382/argparse-f/blob/435cc1676d6064162a3c36b91f1aa50d926fdd45/src/argparse-f.f90#L143) / [Author test](https://github.com/0382/argparse-f/blob/435cc1676d6064162a3c36b91f1aa50d926fdd45/test/check.f90)

```text
12 child invocations; 72 typed/default/flag references, short and long option names
PASS argparse-options-reference
```

### veggies-results-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=veggies&example=gams-veggies-results-reference) / [Driver source](../fpm_catalog/gams-drivers/veggies-results-reference.f90) / [Pinned procedure](https://github.com/everythingfunctional/veggies/blob/8388f5e2633afa3d08cf5c6e7db1eeb0dcab2dc8/src/veggies/run_tests_m.f90#L13) / No pinned author example; API reviewed directly.

```text
Running Tests

Checked framework consumers
    integer references
    exact binary real

A total of 2 test cases

All Passed
Took 3.2478e-4 seconds

A total of 2 test cases containing a total of 66 assertions

289 equality outcomes and 17 mixed-result counts; two passing specification cases
PASS veggies-results-reference
```

### system-files-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=m-system&example=gams-system-files-reference) / [Driver source](../fpm_catalog/gams-drivers/system-files-reference.f90) / [Pinned procedure](https://github.com/urbanjost/M_system/blob/cb558fe8be200783e603e33a66aaba0289b6d3d1/src/M_system.F90#L1) / [Author test](https://github.com/urbanjost/M_system/blob/cb558fe8be200783e603e33a66aaba0289b6d3d1/example/demo_system_mkdir.f90)

```text
65 Linux binary file lifecycles, lengths 0..64; directory/file type checks
PASS system-files-reference
```

### tcl-sums-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-tcl86&example=gams-tcl-sums-reference) / [Driver source](../fpm_catalog/gams-drivers/tcl-sums-reference.f90) / [Pinned procedure](https://github.com/interkosmos/fortran-tcl86/blob/5d5cc9dbf39679d75d2a58d149112aedde2567d6/src/tcl.f90#L1) / [Author test](https://github.com/interkosmos/fortran-tcl86/blob/5d5cc9dbf39679d75d2a58d149112aedde2567d6/examples/eval/eval.f90)

```text
65 Tcl finite-sum references, syntax rejection and successful interpreter recovery
PASS tcl-sums-reference
```

### julienne-diagnosis-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=julienne&example=gams-julienne-diagnosis-reference) / [Driver source](../fpm_catalog/gams-drivers/julienne-diagnosis-reference.f90) / [Pinned procedure](https://github.com/BerkeleyLab/julienne/blob/b2648cc10d8cdd0549d5c286b56d023a642e2a3e/src/julienne/julienne_test_diagnosis_m.F90#L1) / [Author test](https://github.com/BerkeleyLab/julienne/blob/b2648cc10d8cdd0549d5c286b56d023a642e2a3e/test/modules/test_diagnosis_test_m.F90)

```text
Exact equality and inclusive absolute-tolerance truth-table references: 1054
PASS julienne-diagnosis-reference
```

### process-lines-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=m-process&example=gams-process-lines-reference) / [Driver source](../fpm_catalog/gams-drivers/process-lines-reference.f90) / [Pinned procedure](https://github.com/urbanjost/M_process/blob/a38afc744f991a602eded0f7782beb2eff87c8cd/src/M_process.f90#L1) / [Author test](https://github.com/urbanjost/M_process/blob/a38afc744f991a602eded0f7782beb2eff87c8cd/example/demo_process_open_read.f90)

```text
Four fixed local printf pipes; exact ordered records with EOF/status checks: 170
PASS process-lines-reference
```

### gftl-prefix-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=gftl&example=gams-gftl-prefix-reference) / [Driver source](../fpm_catalog/gams-drivers/gftl-prefix-reference.f90) / [Pinned procedure](https://github.com/Goddard-Fortran-Ecosystem/gFTL/blob/4af86210b6cc6ac46d3298b6861571aa26bd6acc/include/v2/vector/template.inc#L1) / [Author test](https://github.com/Goddard-Fortran-Ecosystem/gFTL/blob/4af86210b6cc6ac46d3298b6861571aa26bd6acc/examples/v2/Vector/VecIntAndReal.F90)

```text
12 vectors of 96 integers; 55,872 exact prefix values and 1,152 closed-form sums
PASS gftl-prefix-reference
```

### history-edit-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=m_history&example=gams-history-edit-reference) / [Driver source](../fpm_catalog/gams-drivers/history-edit-reference.f90) / [Pinned procedure](https://github.com/urbanjost/M_history/blob/fe7dd940a5d15792653233962d8df9cb3b5443f6/src/M_history.f90#L1) / [Author test](https://github.com/urbanjost/M_history/blob/fe7dd940a5d15792653233962d8df9cb3b5443f6/app/redo.f90)

```text
!parameter_12 = 1012
!parameter_01 = 1001
!parameter_01 = 2001
!parameter_01 = 2001
!parameter_01 = 1001
!parameter_01 = 1001
!parameter_02 = 1002
!parameter_02 = 2002
!parameter_02 = 2002
!parameter_02 = 1002
!parameter_02 = 1002
!parameter_03 = 1003
!parameter_03 = 2003
!parameter_03 = 2003
!parameter_03 = 1003
!parameter_03 = 1003
!parameter_04 = 1004
!parameter_04 = 2004
!parameter_04 = 2004
!parameter_04 = 1004
!parameter_04 = 1004
!parameter_05 = 1005
!parameter_05 = 2005
!parameter_05 = 2005
!parameter_05 = 1005
!parameter_05 = 1005
!parameter_06 = 1006
!parameter_06 = 2006
!parameter_06 = 2006
!parameter_06 = 1006
!parameter_06 = 1006
!parameter_07 = 1007
!parameter_07 = 2007
!parameter_07 = 2007
!parameter_07 = 1007
!parameter_07 = 1007
!parameter_08 = 1008
!parameter_08 = 2008
!parameter_08 = 2008
!parameter_08 = 1008
!parameter_08 = 1008
!parameter_09 = 1009
!parameter_09 = 2009
!parameter_09 = 2009
!parameter_09 = 1009
!parameter_09 = 1009
!parameter_10 = 1010
!parameter_10 = 2010
!parameter_10 = 2010
!parameter_10 = 1010
!parameter_10 = 1010
!parameter_11 = 1011
!parameter_11 = 2011
!parameter_11 = 2011
!parameter_11 = 1011
!parameter_11 = 1011
!parameter_12 = 1012
!parameter_12 = 2012
!parameter_12 = 2012
!parameter_12 = 1012
12 recorded commands; exact edited recalls and unchanged originals using 1024-character buffers
PASS history-edit-reference
```

### cli-namelist-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=m_cli&example=gams-cli-namelist-reference) / [Driver source](../fpm_catalog/gams-drivers/cli-namelist-reference.f90) / [Pinned procedure](https://github.com/urbanjost/M_CLI/blob/45a7cbcdc12b71b828c482fb4c33498db7fb5618/src/M_CLI.f90#L1) / [Author test](https://github.com/urbanjost/M_CLI/blob/45a7cbcdc12b71b828c482fb4c33498db7fb5618/example/demo3.f90)

```text
32 NAMELIST prototypes; 224 exact integer/real/array/logical/quoted-string references
PASS cli-namelist-reference
```

### fy-list-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fycollections&example=gams-fy-list-reference) / [Driver source](../fpm_catalog/gams-drivers/fy-list-reference.f90) / [Pinned procedure](https://github.com/aradi/fycollections/blob/f67b874669e63834f30cd83f2b96889072b4eec7/include/fycollections.fypp#L1) / [Author test](https://github.com/aradi/fycollections/blob/f67b874669e63834f30cd83f2b96889072b4eec7/examples/list/intlist_example.fpp)

```text
Eight integer/string list traces: append, middle insert/delete, lookup and absent search
PASS fy-list-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers argparse-options-reference veggies-results-reference system-files-reference tcl-sums-reference julienne-diagnosis-reference process-lines-reference gftl-prefix-reference history-edit-reference cli-namelist-reference fy-list-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
