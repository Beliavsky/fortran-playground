# Ten checked structured-data and interoperability drivers

Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Every run reused the existing package library and compiled only the main and executable. The [verification report](gams-interop-ten-validation.json) preserves pins, normalized source hashes, timings and complete output. GAMS categories are not exhausted.

## Independent references and limits

JSON and YAML values are compared with the parameters used to generate their inputs; the JSON values must match both before and after serialization. The NPY consumer uses native stream I/O rather than a package reader, checking header shape/type/order and every payload value. Native stream integer/REAL64 representation is scoped to the little-endian GNU/Linux sandbox.

Container states are compared with plain indexed arrays after every operation. Error lists are checked against independently numbered diagnostics and parity categories, including snapshots from before each append. File drivers compare expected byte lengths and content through the native runtime and test disappearance after deletion. These are Linux filesystem checks, not portability claims.

Lua integer polynomials, dyadic affine arithmetic and finite sums use direct closed-form Fortran references; the low-level binding also checks stack depth and one syntax error. Embedded NumPy reductions use scalar-loop sum/max/sum-of-squares references. Sum/max are exact for the selected dyadic inputs and Frobenius norms allow relative error 1e-13. Scalar reductions do not establish array-axis or memory-layout correctness.

The [two retained initial probes](gams-candidates/interop-ten-first-probes/README.md) are consumer corrections: erloff category tags require message_type_t, and valid NPY shape tuples permit a trailing comma. Exact failed sources, hashes, pins and full service results remain available; neither is classified as an upstream defect.

### rojff (N3)

Independent API consumer; pinned sources and available author examples reviewed. 49 signed integer/dyadic REAL64/ASCII string objects checked before and after compact serialization against independent formulas; absent keys and two malformed inputs. Unicode, escaping, arrays and arbitrary malformed input unverified.

### erloff (R)

Independent API consumer; pinned sources and available author examples reviewed. 48 append steps with exact diagnostic membership and parity category counts. Previous copied snapshots retain their size and exclude each newly added message. Other filters, severity classes and memory behavior unverified.

### npy-for-fortran (N1)

Independent API consumer; pinned sources and available author examples reviewed. 35 REAL64 matrix NPY files independently read using native stream I/O: magic/version, little-endian dtype, Fortran order, exact shape, byte size and 420 payload values. Scope is little-endian GNU/Linux; empty arrays, other kinds, NPZ and external NumPy loading unverified.

### ftl (N4)

Independent API consumer; pinned sources and available author examples reviewed. Eight 128-step traces compare all dynamic-array values and 17 map membership/value slots against plain-array oracles. Growth, LIFO pops, replacement, conditional deletion, final drain and explicit destruction. Iterators, object copies, missing-key Get, clear/reuse and thread safety unverified.

### fortran-unix (N1)

Independent API consumer; pinned sources and available author examples reviewed. 129 Linux POSIX file lifecycles with generated binary bytes: c_stat sizes versus expected lengths and INQUIRE, byte content, c_unlink disappearance and failed stat afterward. Permissions, symlinks, errno, directories and non-Linux platforms unverified.

### stdlib-os (N1)

Independent API consumer; pinned sources and available author examples reviewed. 33 Linux file create/rename/read/unlink lifecycles with exact sizes and contents, relative/absolute normalization fixtures, basename/dirname, nested mkdir/rmdir. Windows paths, symlinks, exceptional I/O and recursive operations unverified.

### fortran-lua53 (S)

Independent API consumer; pinned sources and available author examples reviewed. 129 Lua calls check integer polynomial and dyadic affine values against independent formulas, two-result stack depth and cleanup, plus one rejected syntax error. General Lua applications, callbacks, runtime-error recovery and other platforms unverified.

### forpy (S)

Independent API consumer; pinned sources and available author examples reviewed. 35 asymmetric REAL64 arrays passed into embedded NumPy. Sum/max match independent scalar loops exactly; Frobenius norm matches the scalar sum-of-squares reference within 1e-13. Array axis/layout observability, mutability, exceptions and general numerical NumPy routines unverified.

### yafyaml (N3)

Independent API consumer; pinned sources and available author examples reviewed. 32 fresh core-schema YAML files with signed integer, alternating logical, quoted ASCII text and integer sequences of lengths 1..8. 240 independent value references and absent keys. Malformed inputs, anchors, nested mappings, duplicate keys and repeated loads into the same parser unverified.

### flook (S)

Independent API consumer; pinned sources and available author examples reviewed. 153 Lua table set/execute/get traces with signed dyadic parameters and n=0..16. Exact affine arithmetic and triangular-sum references with explicit table/state closure. General scripts, callbacks, table nesting, error recovery and memory leaks unverified.

## Provenance and actual output

Pinned APIs, implementations and available author examples were reviewed. These are independent MIT consumers; upstream implementation/example bodies were not copied and upstream licenses remain separate. A checked driver demonstrates only its recorded class and scope; it does not verify other package classifications. Loading an example does not submit a job.

### rojff-json-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rojff&example=gams-rojff-json-reference) / [Driver source](../fpm_catalog/gams-drivers/rojff-json-reference.f90) / [Pinned procedure](https://github.com/everythingfunctional/rojff/blob/9f68e5aa4c12b32720d4224f1ac279bfd7d77b93/src/rojff/parser/parser_m.f90#L18) / [Author test](https://github.com/everythingfunctional/rojff/blob/9f68e5aa4c12b32720d4224f1ac279bfd7d77b93/example/get_value/main.f90)

```text
49 objects; 294 independent typed references; two malformed inputs rejected
PASS rojff-json-reference
```

### erloff-filter-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=erloff&example=gams-erloff-filter-reference) / [Driver source](../fpm_catalog/gams-drivers/erloff-filter-reference.f90) / [Pinned procedure](https://github.com/everythingfunctional/erloff/blob/73dfdbf54dafadb42e4705c45824b93917a20965/src/erloff/error_list_m.f90#L1) / No pinned author example; API reviewed directly.

```text
48 immutable append steps; exact parity-filter membership and snapshot preservation
PASS erloff-filter-reference
```

### npy-payload-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=npy-for-fortran&example=gams-npy-payload-reference) / [Driver source](../fpm_catalog/gams-drivers/npy-payload-reference.f90) / [Pinned procedure](https://github.com/MRedies/NPY-for-Fortran/blob/b76d22c6ece4e820d31d71825b2f774d060cd288/src/npy.f90#L1) / [Author test](https://github.com/MRedies/NPY-for-Fortran/blob/b76d22c6ece4e820d31d71825b2f774d060cd288/src/example.f90)

```text
35 NPY headers and independently read REAL64 payload values: 420
PASS npy-payload-reference
```

### ftl-state-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=ftl&example=gams-ftl-state-reference) / [Driver source](../fpm_catalog/gams-drivers/ftl-state-reference.f90) / [Pinned procedure](https://github.com/SCM-NV/ftl/blob/e6598dae7db68f68544dc1ca0e64f5bce3744c42/src/ftlDynArray.F90_template#L1) / [Author test](https://github.com/SCM-NV/ftl/blob/e6598dae7db68f68544dc1ca0e64f5bce3744c42/tests/ftlDynArrayTests.F90)

```text
Independent array/map state checkpoints: 1024
PASS ftl-state-reference
```

### unix-files-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-unix&example=gams-unix-files-reference) / [Driver source](../fpm_catalog/gams-drivers/unix-files-reference.f90) / [Pinned procedure](https://github.com/interkosmos/fortran-unix/blob/50dc6df511c1cf5a245a4ab14cd4f705d4e66c2f/src/unix_stat.F90#L1) / [Author test](https://github.com/interkosmos/fortran-unix/blob/50dc6df511c1cf5a245a4ab14cd4f705d4e66c2f/examples/stat/stat.f90)

```text
129 Linux POSIX file lifecycles, lengths 0..128 including arbitrary bytes
PASS unix-files-reference
```

### os-path-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib-os&example=gams-os-path-reference) / [Driver source](../fpm_catalog/gams-drivers/os-path-reference.f90) / [Pinned procedure](https://github.com/MarDiehl/stdlib_os/blob/60768243de9325d9b57b2e825e7312d70b1e538a/src/os.F90#L1) / [Author test](https://github.com/MarDiehl/stdlib_os/blob/60768243de9325d9b57b2e825e7312d70b1e538a/test/stdlib_test.f90)

```text
33 Linux file lifecycle traces and exact path normalization/parts
PASS os-path-reference
```

### lua53-stack-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lua53&example=gams-lua53-stack-reference) / [Driver source](../fpm_catalog/gams-drivers/lua53-stack-reference.f90) / [Pinned procedure](https://github.com/interkosmos/fortran-lua53/blob/d0d684978e922bbc8c2f7e4be0cc901f80c29de6/src/lua.f90#L1) / [Author test](https://github.com/interkosmos/fortran-lua53/blob/d0d684978e922bbc8c2f7e4be0cc901f80c29de6/examples/fibonacci/fibonacci.f90)

```text
129 Lua calls; 258 exact numeric references, stack balance and syntax rejection
PASS lua53-stack-reference
```

### forpy-numpy-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forpy&example=gams-forpy-numpy-reference) / [Driver source](../fpm_catalog/gams-drivers/forpy-numpy-reference.f90) / [Pinned procedure](https://github.com/ylikx/forpy/blob/b4fc550c7282ed0751d6559c4d867a60af3718a7/forpy_mod.F90#L1) / [Author test](https://github.com/ylikx/forpy/blob/b4fc550c7282ed0751d6559c4d867a60af3718a7/README.md)

```text
35 embedded NumPy arrays; scalar-loop sum/max/Frobenius references: 105
PASS forpy-numpy-reference
```

### yaml-values-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=yafyaml&example=gams-yaml-values-reference) / [Driver source](../fpm_catalog/gams-drivers/yaml-values-reference.f90) / [Pinned procedure](https://github.com/Goddard-Fortran-Ecosystem/yaFyaml/blob/d6005c9f635c02d7be54d09b205b6f16c54f46b5/src/Parser.F90#L1) / [Author test](https://github.com/Goddard-Fortran-Ecosystem/yaFyaml/blob/d6005c9f635c02d7be54d09b205b6f16c54f46b5/Examples/Simple/simple.F90)

```text
32 fresh YAML files; 240 exact scalar/sequence references and absent keys
PASS yaml-values-reference
```

### flook-table-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=flook&example=gams-flook-table-reference) / [Driver source](../fpm_catalog/gams-drivers/flook-table-reference.f90) / [Pinned procedure](https://github.com/ElectronicStructureLibrary/flook/blob/7b644a2ace47e43772006764a58166b6635e8941/src/flook.F90#L1) / [Author test](https://github.com/ElectronicStructureLibrary/flook/blob/7b644a2ace47e43772006764a58166b6635e8941/src/test/tst_tbl.f90)

```text
153 Lua table traces; exact affine and triangular-sum references: 306
PASS flook-table-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers rojff-json-reference erloff-filter-reference npy-payload-reference ftl-state-reference unix-files-reference os-path-reference lua53-stack-reference forpy-numpy-reference yaml-values-reference flook-table-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
