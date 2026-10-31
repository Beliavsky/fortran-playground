# Checked numeric file I/O and bounds validation

These N1 and R2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-io-bounds-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Independent numeric-file fixtures: IO-Fortran-Library (N1)

Real64 matrices with shapes 1x1, 2x3, 4x2 and 3x4 are written with comma and semicolon delimiters, giving eight file fixtures. Values are `(10*i-7*j)/8`, with the first entry replaced by zero. The library writes exponential-format data. An independent native Fortran reader checks the exact row count, delimiter count per row, column order and values. Separators are replaced with spaces before native list-directed numeric parsing.

The library then reads each file and must reproduce the original shape and values. To check its reader without relying on its own writer, the driver also creates a four-row, three-column CSV from literal text using native Fortran and checks the result against an explicit matrix. All loaded values must be finite, with elementwise error divided by max(1,abs(reference)) at most 5e-14. These references can detect compensating reader/writer layout errors that a library-only round trip might miss.

Every successful library operation must return status zero. A file not created in the fresh sandbox must return nonzero status and a nonempty diagnostic. Temporary files are deleted after their checks. The author file tests were reviewed for API usage; all fixture data are independently specified. Headers, locale options, complex/integer arrays, other ranks, nonfinite values and output modes beyond exponential formatting are outside this example.

## Inclusive typed bounds: fortran-error-handler (R2)

Integer values -4..4 and real32/real64 values -3..3 test the inclusive interval [-2,2], lower-only and upper-only bounds. For each real kind, NEAREST supplies the immediately adjacent representable values inside and outside both endpoints. A further three values per type test equal lower/upper bounds [0,0], using +/-epsilon for reals. There are 102 calls in total.

Independent native comparisons determine acceptance. Each accepted value must yield isError() false and code zero. All 30 expected rejections must yield isError() true, code 105, a message beginning with the supplied text and exactly one supplied application trace entry. Interleaved successes and failures ensure that each returned object reflects the current input. No errors are triggered or suppressed to allow continuation; the API returns diagnostics for the caller to inspect.

The author validation example and criteria implementations were reviewed for usage. This checks limit(), including exact endpoint inclusion, rather than the other criteria or their tolerance settings. Reversed bounds, omitted bounds, NaNs, critical-error termination and the separate R3 error-handling mapping are not verified.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### io-numeric-file-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=io-fortran-library&example=gams-io-numeric-file-reference) / [Driver source](../fpm_catalog/gams-drivers/io-numeric-file-reference.f90) / [Pinned procedure](https://github.com/acbbullock/IO-Fortran-Library/blob/15bc3557c36adc174abbd9a077e0686dc11cc4af/src/modules/io_fortran_lib_mod.f90#L982) / [Author example/test](https://github.com/acbbullock/IO-Fortran-Library/blob/15bc3557c36adc174abbd9a077e0686dc11cc4af/test/units/file-test-c.f90)

```text
8 real64 matrix files: four shapes, comma/semicolon delimiters, independent native parsing.
Hand-written CSV, row/column layout, library round trips and missing-file diagnostics checked.
Maximum normalized numeric file error:   0.0000E+00
PASS io-numeric-file-reference
```

### error-bounds-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-error-handler&example=gams-error-bounds-reference) / [Driver source](../fpm_catalog/gams-drivers/error-bounds-reference.f90) / [Pinned procedure](https://github.com/samharrison7/fortran-error-handler/blob/ab840882bb5036de00de8b2580e745fa5314d6fd/src/ErrorCriteria.f90#L1) / [Author example/test](https://github.com/samharrison7/fortran-error-handler/blob/ab840882bb5036de00de8b2580e745fa5314d6fd/example/example_usage.f90)

```text
102 integer/real32/real64 bounds checks; 30 expected rejections.
Inclusive endpoints, nearest inside/outside floats, one-sided and equal bounds checked.
Expected failures retain code 105, the custom message and one application trace.
PASS error-bounds-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers io-numeric-file-reference error-bounds-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
