# Ten checked statistical, matrix, quadrature and service drivers

Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Seven newly reviewed stdlib procedures and three existing service records have dedicated drivers. Every successful run reused the existing package library and compiled only the main and executable. The [verification report](gams-statistics-services-ten-validation.json) preserves pins, source hashes, timings and full output. GAMS categories are not exhausted.

## Independent numerical references

Median references come from nine-bin integer histogram ordering, not another sorting or selection routine. Covariance references use pairwise differences: the sum over k<l of (x[k,i]-x[l,i])*(x[k,j]-x[l,j]), divided by n*(n-c), where c is 1 for sample or 0 for population covariance. Correlations normalize these pairwise sums. Both axis conventions are checked without using package mean, variance or covariance routines to produce the references.

Third/fourth moment references use exact INT64 arithmetic. With x[i]=q[i]/8 and S=sum(q), the central moment numerator is sum((n*q[i]-S)**p), with denominator n**(p+1)*8**p. Explicit zero-center references instead use sum(q[i]**p)/(n*8**p). All integer operations stay within INT64 range; final rational conversion is REAL64.

Determinants of 96 nonsingular 3x3 matrices are checked with the independent six-term polynomial. Inverses of 128 nonsymmetric matrices A=D*(I+u*v**T)*E are compared with E**(-1)*(I-u*v**T/(1+v**T*u))*D**(-1), plus left/right identity residuals. Default calls must preserve input matrices. These are bounded matrix families, not a certification for arbitrary conditioning, sizes or singular cases.

Trapezoidal integration checks 864 affine antiderivatives over nonuniform, reversed and constant-spacing grids. Selected inputs/results are exact binary values; no reference is produced by summing another trapezoidal rule. Nonlinear integration errors and adaptivity remain outside this driver.

## Service references and scope

Timer results, multiplied by nloops, must lie between independently sampled inner and outer native clock intervals. Four SYSTEM_CLOCK ticks and 2 microseconds CPU resolution slack are allowed. Sixteen reused timer pairs also check exact work sums. No performance or minimum-duration claim is made.

Assertions are tested through 65 passing pure-contract calls and one deliberately false assertion in a self-invoked child. The parent requires nonzero exit and the specified diagnostic; the expected failure is checked rather than ignored. MPI wrappers run on exactly one process and check 1,408 identity values/statuses across 64 traces. This does not verify communication between processes or speedup.

## Retained random-array bounds failure

The [requested-bounds probe](gams-candidates/test-helper-bounds/README.md) for fortran_test_helper compiles with cached-library reuse but returns a maximum 1.944083652 for requested [0,1] bounds. The public source transforms intrinsic draws with 0.99*(low+(high+1-low)*draw), explaining the excess. Its exact source, normalized hash, package pin and full failed result are retained. That record receives no checked driver and no source patch.

## Classification and provenance

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies explicit parents for covariance/correlation (L1c1b), shape moments (L1a1c), real general determinants (D3a1) and nonautomatic sampled-grid quadrature (H2a1b2). Only these reviewed scopes are promoted; adjacent statistical/solver capabilities and the retained bounds failure remain separate.

### stdlib-median-reference (L1a1a)

Independent API consumer; pinned sources and available author examples reviewed. 768 REAL64 vector medians for lengths 1..64 against an independent nine-bin histogram ordering, with odd/even sizes, ties, signed dyadics and input preservation. Empty input returns NaN. Masks, nonfinite data and other ranks/kinds unverified.

### stdlib-covariance-reference (L1c1b)

Independent API consumer; pinned sources and available author examples reviewed. 29 three-variable REAL64 datasets with 4..32 observations; sample/population matrices and both axis conventions. All 1,044 entries match independent pairwise-difference sums without package mean/variance/covariance calls or MATMUL. Scaled absolute tolerance 2e-12. Missing data, masks, degeneracy, complex values and all numerical conditioning unverified.

### stdlib-correlation-reference (L1c1b)

Independent API consumer; pinned sources and available author examples reviewed. 29 nonconstant three-variable REAL64 datasets; 522 Pearson matrix entries for both axis conventions against normalized pairwise-difference sums, absolute tolerance 2e-12. No package covariance, variance or mean supplies the reference. Constant columns, missing data, masks, complex values and general correlation analysis unverified.

### stdlib-moments-reference (L1a1c)

Independent API consumer; pinned sources and available author examples reviewed. 1,152 third/fourth REAL64 moment values about the automatic mean or explicit zero for 32 lengths and nine shifts. Exact INT64 numerators and rational denominators supply independent references; scaled absolute tolerance 2e-12. Standardized skewness/kurtosis, masks, other orders/kinds, nonfinite inputs and stability for extreme data unverified.

### stdlib-determinant-reference (D3a1)

Independent API consumer; pinned sources and available author examples reviewed. 96 nonsingular REAL64 3x3 matrices generated from triangular factors and parity-changing row swaps. Determinants checked against an independent six-term polynomial, relative tolerance 1e-11, and inputs unchanged. Singular matrices, other sizes/kinds, overflow and ill-conditioning unverified.

### stdlib-inverse-reference (D2a1)

Independent API consumer; pinned sources and available author examples reviewed. 128 nonsymmetric REAL64 3x3 matrices from diagonally scaled rank-one updates. Sherman-Morrison closed form supplies 1,152 entries; left/right identity residuals supply 2,304 checks, absolute tolerance 2e-12. Inputs unchanged. Singular matrices, general conditioning, other sizes/kinds and full inverse error handling unverified.

### stdlib-trapezoid-reference (H2a1b2)

Independent API consumer; pinned sources and available author examples reviewed. 864 exact affine-integral references for nine slopes and 32 grid lengths: nonuniform explicit grids, reversed grids and constant-spacing overload. Reference is an analytic antiderivative, not another trapezoidal sum. Nonlinear error estimates, adaptive integration, malformed/empty grids and other kinds unverified.

### timer-brackets-reference (R)

Independent API consumer; pinned sources and available author examples reviewed. 16 reused wall/CPU timer pairs, nloops averaging and exact integer work checksums. Reported durations multiplied by nloops must fall between native inner/outer SYSTEM_CLOCK or CPU_TIME brackets, allowing four wall ticks or 2 microseconds CPU resolution slack. No latency or speed benchmark claim. Pause/resume, wrapping, invalid calls, MPI/OpenMP timers and other platforms unverified.

### assert-enforcement-reference (S3)

Independent API consumer; pinned sources and available author examples reviewed. 65 bounded square evaluations inside pure pre/postcondition assertions, plus one deliberately false assertion in a self-invoked child. Parent requires nonzero exit and the specified diagnostic, proving enforcement in the existing enabled library. Child failure is expected and checked. Other macros, callbacks, multi-image behavior and disabled builds unverified. Upstream custom license terms remain unchanged.

### mpifx-identity-reference (R)

Independent API consumer; pinned sources and available author examples reviewed. 64 exactly one-process typed collective traces: broadcast, real-vector SUM allreduce, in-place MAX and integer SUM allreduce; all 1,408 values and API statuses checked exactly. Communicator rank/size checked. This verifies wrapper identities, not communication between processes, parallel execution or speedup. Other wrappers/types and multi-process behavior unverified.

## Provenance and actual output

Pinned APIs, implementations and available author examples were reviewed. These independent MIT consumers do not copy upstream implementation/example bodies; upstream license terms remain separate, including the custom assertion-library terms. Only each recorded class and tested scope is verified. Loading an example does not submit a job.

### stdlib-median-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-median-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-median-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L1230) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_median.f90)

```text
768 finite medians from independent histograms; odd/even lengths, ties, negative values; empty NaN
PASS stdlib-median-reference
```

### stdlib-covariance-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-covariance-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-covariance-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L239) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_cov.f90)

```text
29 datasets; sample/population covariance and both axis conventions; entries: 1044
PASS stdlib-covariance-reference
```

### stdlib-correlation-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-correlation-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-correlation-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L15) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_corr.f90)

```text
29 datasets; Pearson matrices against pairwise differences, both axes; entries: 522
PASS stdlib-correlation-reference
```

### stdlib-moments-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-moments-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-moments-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L2647) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_moment.f90)

```text
Third/fourth moments about mean and zero versus exact integer rational references: 1152
PASS stdlib-moments-reference
```

### stdlib-determinant-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-determinant-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-determinant-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2666) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_determinant.f90)

```text
96 nonsingular real 3x3 determinants; positive/negative parity, six-term oracle, input preservation
PASS stdlib-determinant-reference
```

### stdlib-inverse-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-inverse-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-inverse-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2812) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_inverse.f90)

```text
128 scaled nonsymmetric rank-one inverses; 1,152 exact-form references and two-sided residuals
PASS stdlib-inverse-reference
```

### stdlib-trapezoid-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-trapezoid-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-trapezoid-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L18) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_trapz.f90)

```text
Affine antiderivatives on nonuniform, reversed and constant-spacing grids: 864
PASS stdlib-trapezoid-reference
```

### timer-brackets-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortime&example=gams-timer-brackets-reference) / [Driver source](../fpm_catalog/gams-drivers/timer-brackets-reference.f90) / [Pinned procedure](https://github.com/gha3mi/fortime/blob/5a31be5a47bf2c0bf49c4d0fb7b67415ccc0a1e7/src/fortime.F90#L1) / [Author test](https://github.com/gha3mi/fortime/blob/5a31be5a47bf2c0bf49c4d0fb7b67415ccc0a1e7/example/example1.f90)

```text
16 reused wall/CPU timer pairs; averaging, native inner/outer brackets and exact work checksums
PASS timer-brackets-reference
```

### assert-enforcement-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=berkeley-assert&example=gams-assert-enforcement-reference) / [Driver source](../fpm_catalog/gams-drivers/assert-enforcement-reference.f90) / [Pinned procedure](https://github.com/BerkeleyLab/assert/blob/eda03ce48da96c3118ec98d4498f4bd47c0b60ab/src/assert_m.F90#L1) / [Author test](https://github.com/BerkeleyLab/assert/blob/eda03ce48da96c3118ec98d4498f4bd47c0b60ab/example/simple-assertions.f90)

```text
65 pure-contract calls; false assertion terminates a child with the required diagnostic
PASS assert-enforcement-reference
```

### mpifx-identity-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=mpifx&example=gams-mpifx-identity-reference) / [Driver source](../fpm_catalog/gams-drivers/mpifx-identity-reference.f90) / [Pinned procedure](https://github.com/dftbplus/mpifx/blob/1223bd515bf2ccf39f5575d628ab2867a3d8e155/lib/mpifx_bcast.fpp#L1) / [Author test](https://github.com/dftbplus/mpifx/blob/1223bd515bf2ccf39f5575d628ab2867a3d8e155/test/test_allreduce.f90)

```text
[1793552330.296071] [modal:39   :0]       tcp_iface.c:912  UCX  ERROR scandir(/sys/class/net) failed: No such file or directory
64 one-process broadcast/reduction traces; 1,408 exact value references
PASS mpifx-identity-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-median-reference stdlib-covariance-reference stdlib-correlation-reference stdlib-moments-reference stdlib-determinant-reference stdlib-inverse-reference stdlib-trapezoid-reference timer-brackets-reference assert-enforcement-reference mpifx-identity-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
