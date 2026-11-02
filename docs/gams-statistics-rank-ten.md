# Ten checked complex statistics and rank-sensitive linear algebra drivers

Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. Existing stdlib libraries were reused; only mains and executables were compiled. The [verification report](gams-statistics-rank-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings and complete output. GAMS categories are not exhausted.

## Complex statistics: exact references and conventions

Five drivers use 32 bounded three-variable datasets: observation counts n=4..11 and patterns k=1..4, each with all observations and a shared row mask excluding mod(i+k,3)=0. This gives 64 selections, each retaining at least two observations and strictly positive component variances. For variable j=1..3, real parts are (mod(i*i+3*j*i+2*k*j,17)-8)/8 and imaginary parts are (mod(2*i*i+j*i+k*(j+1),19)-9)/8. These inputs are exactly representable dyadics. The [reference table](gams-statistics-rank-ten-references.json) records selected indices and exact rational real/imaginary components.

Python Fraction arithmetic supplies exact means, pairwise-difference covariance and analytic central powers from a binomial expansion of raw powers. The population column-observation covariance is sum(conjg(z_i(a)-z_i(b))*(z_j(a)-z_j(b)))/(2*N*N), summed over ordered observation pairs a,b. Sample correction multiplies by N/(N-1). Correlation normalizers use mpmath 1.3.0 at 80 digits and are confirmed at 120 digits to absolute difference below 1e-65. Fortran constants retain 18 significant digits; the rational references remain available in full.

- **Complex means (L1a1a):** masked scalar, rank-two whole-array and dim=1/2 reductions, plus unmasked dim=1 calls, against 192 exact complex component means.
- **Complex variances (L1a1b):** 192 population references and sample correction, using rank-one and dim=1/2 masked reductions. The result is real E(abs(Z-mean)**2), not the analytic second central power.
- **Complex covariance (L1c1b):** 576 complex population entries, population/sample corrections, shared masks and unmasked paths (384 calls). Column observations dim=1 conjugate the first variable. Row observations obtained by transposing the data and using dim=2 give the conjugate matrix; both documented source conventions are checked explicitly.
- **Complex correlation (L1c1b):** 576 independently normalized complex entries, 192 masked/unmasked dim=1/2 calls, unit diagonal and Hermitian structure. The same orientation convention applies.
- **Complex central powers (L1a1c):** 768 exact references of orders 2..5 from E((Z-mean)**p). Packed selected-vector calls and unmasked dim=1/2 reductions are checked. These complex powers differ from magnitude moments and do not estimate variance when p=2.

## Pivoted QR, minimum norm and reused factors

- **REAL64 pivoted QR (D5):** 180 full/reduced factorizations from 30 tall/square/wide shapes and three scaled triangular templates. Pivot indices must be a permutation; reconstruction uses A(:,pivots). Orthonormal columns, triangular zeros and preservation are checked. At least one nonidentity permutation must occur, without prescribing a pivot order or factor signs.
- **COMPLEX128 pivoted QR (D5):** the same 180-case shape/mode coverage with genuinely complex entries, unitary Gram checks and unrestricted phases.
- **Complex rank-deficient least squares (D9a1):** 45 overdetermined rank-(n-1) cases with a nonzero orthogonal residual. Checked unitary factors and prescribed singular values define the minimum-norm solution; returned rank, solution, stationarity and null-space orthogonality are checked with cond=1e-12.
- **Complex underdetermined minimum norm via PINV (D9a1):** 45 full-row-rank consistent systems. A known solution in the row space supplies the independent oracle; PINV(A)*b must match it and remain orthogonal to every explicit null-space vector. rtol=1e-12. This does not verify the failing LSTSQ consumer described below.
- **Complex factored positive-definite solves (D2d1b):** 288 vector/multiple-RHS lower/upper solves on 72 explicitly manufactured factors, with known solutions, residuals and exact factor/RHS preservation. The solve calls do not factorize the matrix.

The linear algebra examples construct unitary matrices locally with Householder formulas and check the unitary Gram matrices before using them. Rank-sensitive references use prescribed nonzero singular values j+1 and exact zero singular values, so these are separated-rank examples. No claim is made for near-cutoff rank decisions or ill-conditioned problems.

## Retained failed LSTSQ probe

The complex underdetermined LSTSQ consumer compiled but returned an invalid-problem-size API error on its first 2x4 matrix. The exact [original/diagnostic sources and full results](gams-candidates/stdlib-underdetermined/README.md) are retained with pins and hashes. The diagnostic adds only shape and error-state printing. The pinned routine passes ldb=m to GELSD where LAPACK requires at least max(1,m,n), a source-level explanation consistent with the failure. No numerical answer was produced; this was not a sandbox time or executable-size limit. Successful PINV solves do not promote the separate source-supported LSTSQ procedure.

## Limits, provenance and maintenance

Real and imaginary components must be finite and agree to scaled absolute tolerance 2e-10*max(1,abs(reference component)); integer/permutation and preservation checks are exact. Empty or all-false masks, singleton variance, nonfinite observations, variable-specific missingness, constant-variable correlation, user-supplied moment centers, approximate rank thresholds, invalid factors and poisoned unused triangles are outside these drivers. These bounded tests are not a precision or performance benchmark.

Pinned public APIs, implementations and linked author examples were reviewed. These are independent MIT consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source was patched. The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies the existing L1a1a/L1a1b/L1a1c/L1c1b statistics classes, D5 QR, D9a1 least squares and D2d1b positive-definite complex systems. The PINV application is classified by the demonstrated minimum-norm problem; it does not claim a different fitting algorithm. Loading an example does not submit a job. The [coverage report](gams-coverage.md) records remaining work.

## Driver details

### stdlib-complex-means-reference (L1a1a)

Independent API consumer; pinned sources reviewed. 64 COMPLEX128 three-variable data selections (32 datasets, all/row masks), exact Fraction means; rank-one, rank-two whole-array and dimension-1/2 masked reductions, plus unmasked reductions. No empty/all-false masks, missing values or high-rank arrays claimed.

### stdlib-complex-variances-reference (L1a1b)

Independent API consumer; pinned sources reviewed. 64 COMPLEX128 data selections, population/sample variance with REAL64 nonnegative results. Exact pairwise squared-distance references; scalar masked and dimension-1/2 reductions. This is E(abs(Z-mean)**2), not the analytic second central power. Empty/singleton and nonfinite cases excluded.

### stdlib-complex-covariances-reference (L1c1b)

Independent API consumer; pinned sources reviewed. 64 COMPLEX128 three-variable selections, both population/sample corrections and masked/unmasked paths. Exact pairwise-difference covariance oracle. Column observations dim=1 conjugate the first variable; transpose to row observations dim=2 gives the conjugate covariance matrix. Only common row masks, not variable-specific missingness, claimed.

### stdlib-complex-correlations-reference (L1c1b)

Independent API consumer; pinned sources reviewed. 64 COMPLEX128 selections with strictly positive component variances. Correlations from exact rational pairwise covariance and independently evaluated square roots (80/120 digits); masked/unmasked and dim=1/2 conjugation conventions, unit diagonal and Hermitian structure. Constant-variable and nonfinite cases excluded.

### stdlib-complex-central-powers-reference (L1a1c)

Independent API consumer; pinned sources reviewed. 768 exact rational analytic central-power references of orders 2..5 for 64 selections and three complex variables. Independent binomial expansion of raw powers; packed selected-vector and unmasked dimension-1/2 APIs. E((Z-mean)**p) is complex and differs from magnitude moments/variance. User centers, bias corrections and nonfinite cases excluded.

### stdlib-real-pivoted-qr-reference (D5)

Independent API consumer; pinned sources reviewed. REAL64 pivoted QR: 180 full/reduced factorizations of 30 tall/square/wide shapes with three scaled triangular templates. Pivot permutations, reconstruction of A(:,pivots), orthonormal columns, triangular zeros and preservation; at least one nonidentity pivot required. No fixed phases, prescribed pivot order or rank cutoff claimed.

### stdlib-complex-pivoted-qr-reference (D5)

Independent API consumer; pinned sources reviewed. COMPLEX128 pivoted QR: 180 full/reduced factorizations of 30 tall/square/wide shapes with three scaled triangular templates. Pivot permutations, reconstruction of A(:,pivots), orthonormal columns, triangular zeros and preservation; at least one nonidentity pivot required. No fixed phases, prescribed pivot order or rank cutoff claimed.

### stdlib-complex-rank-deficient-fits-reference (D9a1)

Independent API consumer; pinned sources reviewed. 45 COMPLEX128 rank-(n-1) overdetermined with nonzero orthogonal residual least-squares problems, built with checked unitary factors and prescribed singular values. Known minimum-norm solution, returned rank, residual, stationarity and null-space orthogonality; cond=1e-12. Near-cutoff or ill-conditioned rank decisions excluded.

### stdlib-complex-minimum-norm-pinv-reference (D9a1)

Independent API consumer; pinned sources reviewed. 45 full-row-rank COMPLEX128 underdetermined systems solved using the Moore-Penrose inverse. Checked unitary factors prescribe the unique minimum-norm solution; consistency, stationarity and explicit null-space orthogonality verified, rtol=1e-12. This does not promote the retained failing LSTSQ consumer.

### stdlib-complex-factored-positive-systems-reference (D2d1b)

Independent API consumer; pinned sources reviewed. 288 COMPLEX128 vector/multiple-RHS solves using explicitly supplied lower/upper Cholesky factors of 72 positive-definite matrices. Sizes 1..8, three patterns/scales; known coefficients, residuals and exact factor/RHS preservation. Factors are manufactured directly; no factorization is performed in these calls. Invalid factors and unused-triangle poisoning excluded.

## Provenance and actual output

### stdlib-complex-means-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-means-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-means-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L494) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_mean.f90)

```text
Independent exact-reference complex data selections: 64
PASS stdlib-complex-means-reference
```

### stdlib-complex-variances-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-variances-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-variances-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L1782) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_var.f90)

```text
Independent exact-reference complex data selections: 64
PASS stdlib-complex-variances-reference
```

### stdlib-complex-covariances-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-covariances-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-covariances-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L239) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_cov.f90)

```text
Independent exact-reference complex data selections: 64
PASS stdlib-complex-covariances-reference
```

### stdlib-complex-correlations-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-correlations-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-correlations-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L15) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_corr.f90)

```text
Independent exact-reference complex data selections: 64
PASS stdlib-complex-correlations-reference
```

### stdlib-complex-central-powers-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-central-powers-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-central-powers-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L2647) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_moment.f90)

```text
Independent exact-reference complex data selections: 64
PASS stdlib-complex-central-powers-reference
```

### stdlib-real-pivoted-qr-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-real-pivoted-qr-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-real-pivoted-qr-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2216) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_pivoting_qr.f90)

```text
Pivoted QR factorizations: 180; nonidentity permutations: 180
PASS stdlib-real-pivoted-qr-reference
```

### stdlib-complex-pivoted-qr-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-pivoted-qr-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-pivoted-qr-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2216) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_pivoting_qr.f90)

```text
Pivoted QR factorizations: 180; nonidentity permutations: 180
PASS stdlib-complex-pivoted-qr-reference
```

### stdlib-complex-rank-deficient-fits-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-rank-deficient-fits-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-rank-deficient-fits-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1457) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_lstsq1.f90)

```text
Known minimum-norm solutions, stationarity and null-space orthogonality: 45
PASS stdlib-complex-rank-deficient-fits-reference
```

### stdlib-complex-minimum-norm-pinv-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-minimum-norm-pinv-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-minimum-norm-pinv-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3013) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_pseudoinverse.f90)

```text
Known minimum-norm solutions, stationarity and null-space orthogonality: 45
PASS stdlib-complex-minimum-norm-pinv-reference
```

### stdlib-complex-factored-positive-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-factored-positive-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-factored-positive-systems-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1189) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_solve_lower_chol.f90)

```text
Known-factor complex lower/upper vector and multiple-RHS solves: 288
PASS stdlib-complex-factored-positive-systems-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-complex-means-reference stdlib-complex-variances-reference stdlib-complex-covariances-reference stdlib-complex-correlations-reference stdlib-complex-central-powers-reference stdlib-real-pivoted-qr-reference stdlib-complex-pivoted-qr-reference stdlib-complex-rank-deficient-fits-reference stdlib-complex-minimum-norm-pinv-reference stdlib-complex-factored-positive-systems-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
