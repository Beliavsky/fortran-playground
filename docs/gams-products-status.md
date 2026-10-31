# Checked scalar-product, assertion and error-status drivers

These D1, S3 and R3 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-products-status-validation.json) records source hashes, pins and actual output. GAMS categories are not exhausted.

## Exact scalar products: fordot (D1)

Lengths 1, 7, 8, 17 and 64 cover singleton, odd and even arrays. Three integer numerator patterns produce mixed signed, cancelling and zero products. Inputs are `u_i=a_i/8`, `v_i=b_i/4`; an independent int64 scalar sum supplies `sum(a_i*b_i)/32`. All products and partial sums are small exactly representable dyadic values, so finite **exact equality** is required.

For every dataset, the default call and all four methods m1..m4 are tested. Each method also uses valid distinct block counts from `[1,3,n]`, covering uneven partitions and single-element blocks. There are 231 calls. Empty inputs, invalid block counts, noncontiguous arrays, severe floating roundoff, coarray mode and performance are not verified.

## Captured comparison outcomes: fassert (S3)

Three positive assertions exercise integer arithmetic, integer arrays and an approximate real64 numerical result. Thirteen captured comparisons check matching/mismatching integer scalars and vectors; seven scalar real64 offsets `[-0.75,-0.5,-0.25,0,0.25,0.5,0.75]` with absolute tolerance 0.5; and two vector comparisons at and outside tolerance 0.25.

Native logical expressions independently determine the expected outcome. Both exact scalar tolerance boundaries must pass. Captured diagnostics must contain the supplied case label and the matching PASSED/FAILED prefix. Expected failures are returned to the caller and verified without terminating the program. Shape mismatches, NaN comparison semantics, negative tolerances, custom comparators, other ranks/types and framework integrations are outside this example. This S3 driver does not verify the separate R2 mapping.

## Recovery and copied error objects: errstat (R3)

An independently written `safe_ratio_root(a,b,status)` returns `sqrt(a/b)` for valid inputs, or zero plus a user-defined status/message for invalid inputs. Nine calls alternate successful results with positive/negative zero denominator errors (101), a negative radicand (102), and a quiet-NaN numerator (103). Exact arithmetic results, codes, flags and messages must match the specified cases. Every successful call must replace the previous error with status zero and message `ok`.

A further error with code 701 and message `original` is copied to a second status object. Appending context must produce `original - context` only in the first object. Explicit success with message `recovered` must leave the copy unchanged. Initialization must reset the first object to success with an empty message. The arithmetic function and error codes belong to the driver; errstat supplies the status-handling API. Arbitrary arithmetic overflow, omitted status arguments, message repositories, additional-task callbacks and thread safety are not verified.

## Checked links and actual output

These independent API consumers have their own MIT notice. Author examples/tests were reviewed for usage; upstream package licenses remain separate. Loading a link selects source without submitting a job.

### fordot-exact-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fordot&example=gams-fordot-exact-reference) / [Driver source](../fpm_catalog/gams-drivers/fordot-exact-reference.f90) / [Pinned procedure](https://github.com/gha3mi/fordot/blob/3966625781a9c1dffe037e3032fa4a0b6f958760/src/fordot.f90#L21) / [Author example/test](https://github.com/gha3mi/fordot/blob/3966625781a9c1dffe037e3032fa4a0b6f958760/test/test1.f90)

```text
Length=1 pattern=1 exact dot product=    -0.25000
Length=1 pattern=2 exact dot product=    -0.18750
Length=1 pattern=3 exact dot product=     0.00000
Length=7 pattern=1 exact dot product=     3.56250
Length=7 pattern=2 exact dot product=     0.00000
Length=7 pattern=3 exact dot product=     0.00000
Length=8 pattern=1 exact dot product=     3.46875
Length=8 pattern=2 exact dot product=     0.37500
Length=8 pattern=3 exact dot product=     0.00000
Length=17 pattern=1 exact dot product=     1.00000
Length=17 pattern=2 exact dot product=     0.00000
Length=17 pattern=3 exact dot product=     0.00000
Length=64 pattern=1 exact dot product=    -3.43750
Length=64 pattern=2 exact dot product=     0.18750
Length=64 pattern=3 exact dot product=     0.00000
231 exact results checked: default and m1..m4, including unequal blocks and zero products.
PASS fordot-exact-reference
```

### fassert-captured-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fassert&example=gams-fassert-captured-reference) / [Driver source](../fpm_catalog/gams-drivers/fassert-captured-reference.f90) / [Pinned procedure](https://github.com/degawa/fassert/blob/678fa217df79af318cc537d3c69eab3b7cf68cb7/src/fassert.f90#L1) / [Author example/test](https://github.com/degawa/fassert/blob/678fa217df79af318cc537d3c69eab3b7cf68cb7/example/collab/testdrive.f90)

```text
PASSED: integer arithmetic
PASSED: integer squares
PASSED: numerical assertion
Three positive assertions and 13 captured comparisons checked.
Scalar/vector mismatches and both exact tolerance boundaries were detected without stopping.
PASS fassert-captured-reference
```

### errstat-recovery-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=errstat&example=gams-errstat-recovery-reference) / [Driver source](../fpm_catalog/gams-drivers/errstat-recovery-reference.f90) / [Pinned procedure](https://github.com/degawa/errstat/blob/336ee374c82a4525d87444c767a1f23f059d5723/src/errstat.f90#L1) / [Author example/test](https://github.com/degawa/errstat/blob/336ee374c82a4525d87444c767a1f23f059d5723/example/error/err_code.f90)

```text
Call 1: status=0 message=ok
Call 2: status=101 message=zero denominator
Call 3: status=0 message=ok
Call 4: status=102 message=negative radicand
Call 5: status=0 message=ok
Call 6: status=103 message=nonfinite input
Call 7: status=0 message=ok
Call 8: status=101 message=zero denominator
Call 9: status=0 message=ok
Nine success/failure/recovery calls, copied statuses, appended context and explicit reset checked.
PASS errstat-recovery-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fordot-exact-reference fassert-captured-reference errstat-recovery-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
