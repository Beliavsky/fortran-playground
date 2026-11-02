# Ten checked grid weights, complex spectra and masked statistics drivers

Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. Existing stdlib libraries were reused; only mains and executables were compiled. The [verification report](gams-grids-spectra-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings and complete output. GAMS categories are not exhausted.

## Reusable sampled-grid quadrature weights (H2a1b2)

The two weight drivers use lengths n=0..16, three dyadic spacing patterns and ascending/descending grids. The first node is -3/4 and each subsequent increment is (1+mod(i*k,4))/8. Empty and singleton grids produce empty/zero weights. Python Fraction arithmetic integrates each local Lagrange basis polynomial exactly, by polynomial multiplication and analytic antiderivatives, rather than reproducing upstream spacing formulas. The [reference table](gams-grids-spectra-ten-references.json) saves every node and exact rational weight. The Fortran consumers compare individual weights, polynomial integrals and exact grid preservation.

- **Trapezoidal weights:** 102 grid cases, piecewise linear interpolation, exact constant and linear integrals for n>=2.
- **Simpson weights:** 306 grid/mode cases, with even=-1,0,1 and omitted-default equivalence. Two nodes use a linear panel, three nodes a quadratic panel, and four nodes a cubic panel. Larger odd grids use quadratic panels. Larger even grids place a cubic panel at the left/right end or average the two schemes. Constant, linear and (when n>=3) quadratic integrals are checked; arbitrary cubic exactness on nonuniform composite quadratic panels is not claimed.

## Complex matrix norms and eigenvectors

- **Matrix norms (D1b2):** 108 rectangular matrices of sizes 1..6 by 1..6, including zeros. Entries (3+4i)*t/8 have the exact modulus 5*abs(t)/8, which supplies independent one-, infinity- and Frobenius-norm references. Character/integer orders and rank-three batched infinity reductions with dim=[1,2] are checked. Spectral norms and extreme-range scaling are outside this example.
- **Ordinary complex eigenvectors (D4a4):** 63 dense nonnormal problems, sizes 2..8, three patterns and scales. A checked Householder factor Q and invertible shear S construct A=Q*S*D*inverse(S)*Q^H from prescribed distinct complex diagonal entries.
- **Generalized complex eigenvectors (D4b4):** 63 nonsingular matrix pairs A=Q*D*inverse(S), B=Q*inverse(S), sharing the prescribed finite spectrum. The explicit inverse shear is checked before use.

Both eigenvector consumers require one-to-one eigenvalue matching, the respective GEEV/GGEV vector normalization and the right residual A*v-lambda*B*v and left residual A^H*u-conjg(lambda)*B^H*u. Eigenvector order and phase are unrestricted. Inputs must be preserved exactly. Ordinary problems use B=I. Defective, nearly clustered, infinite or ill-conditioned spectra are excluded. The generalized COMPLEX128 path is independently checked and does not change the status of the previously retained failing generalized REAL64 eigenvector consumer.

Ordinary GEEV vectors have Euclidean norm one. Generalized GGEV vectors instead satisfy max(abs(real(v))+abs(aimag(v)))=1. The initial generalized consumer incorrectly required Euclidean unit norms and failed; its [exact source and full result](gams-candidates/stdlib-complex-ggev/README.md) are retained. Correcting only those two assertions passed all prescribed eigenvalue, left/right residual and input-preservation checks. This was a consumer error, not an established numerical library failure or sandbox limit.

## Discrete uniform probabilities (L5a1u)

Two integer32 drivers enumerate the inclusive support loc..loc+scale: loc=-8..8, scale=1..16, and queries from loc-2 through loc+scale+2 (3672 queries per driver). PMF references count equal support points; CDF references count points <=x, divided by scale+1. PMF normalization and the CDF upper endpoint are checked. These integer overloads return default REAL32, so the explicit absolute tolerance is 2e-7. Zero/negative scale and integer overflow are excluded. No random-number sampling is involved.

## Masked medians, moments and pairwise deletion

REAL64 median/moment data use n=3..12, patterns k=1..3 and three variables j=1..3. Values are (mod(i*i+3*j*i+2*k*j,17)-8)/8; each variable excludes its own mod(i+j+k,4)=0 observations. The reference table saves selected indices, 90 exact rational medians and 1080 exact moments. Python rational order statistics supply medians; an exact binomial expansion of raw powers supplies moments of orders 2..5 about the default selected mean, zero, or supplied center j/8. Rank-one and rank-two dim=1/2 calls are checked. The median driver also replaces excluded values with a finite sentinel and requires unchanged results.

The combined COMPLEX128 covariance/correlation driver uses n=8..12, patterns k=1..3, the same real components/masks and imaginary components (mod(2*i*i+j*i+k*(j+1),19)-9)/8. Each of the 135 variable pairs uses its own mask intersection and pair-specific means/variances. Python Fraction exact raw cross-moments provide population covariance; sample correction uses that pair's N/(N-1). Correlation normalization uses mpmath 1.3.0 at 80 digits, confirmed at 120 digits within 1e-65. Constants retain 18 significant digits. Column observations conjugate the first variable; transposed row observations produce the conjugate matrix. Population/sample covariance, correlation, transpose orientation and replacement of excluded finite values are checked across 15 datasets. Pairwise deletion is not claimed to preserve positive semidefiniteness.

## Limits, provenance and maintenance

Unless stated otherwise, real/imaginary components must be finite and agree within 2e-10*max(1,abs(reference component)); preservation and integer checks are exact. Repeated grid nodes, nonfinite data, empty selected statistics, constant-variable correlations, singular generalized B and extreme-range inputs are outside these bounded demonstrations. They are not precision or performance benchmarks.

Pinned public APIs, implementations and linked author examples were reviewed. These are independent MIT consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source was patched. The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies the classifications, including complex general generalized eigenproblems D4b4. Loading an example does not submit a job. The [coverage report](gams-coverage.md) records remaining work.

## Driver details

### stdlib-trapz-grid-weights-reference (H2a1b2)

Independent API consumer; pinned sources reviewed. 102 REAL64 irregular-grid weight cases; n=0..16, three dyadic spacing patterns and both directions. Exact rational integrals of local Lagrange basis polynomials supply individual weights; polynomial integrals and input preservation checked. Linear exactness checked. Repeated nodes and nonfinite inputs excluded.

### stdlib-simps-grid-weights-reference (H2a1b2)

Independent API consumer; pinned sources reviewed. 306 REAL64 irregular-grid weight cases; n=0..16, three dyadic spacing patterns and both directions. Exact rational integrals of local Lagrange basis polynomials supply individual weights; polynomial integrals and input preservation checked. All even=-1/0/1 modes and omitted default checked; quadratic exactness only when n>=3. Repeated nodes and nonfinite inputs excluded.

### stdlib-complex-matrix-norms-reference (D1b2)

Independent API consumer; pinned sources reviewed. 108 COMPLEX128 rectangular matrices with entries (3+4i)*integer/8; exact modulus 5*abs(integer)/8 supplies one/infinity/Frobenius references. Rank-three batched dim=[1,2] calls, integer and character orders, zero matrices and input preservation. Spectral norm and extreme-range scaling excluded.

### stdlib-complex-eigenvectors-reference (D4a4)

Independent API consumer; pinned sources reviewed. 63 COMPLEX128 dense nonnormal matrix eigenproblems of sizes 2..8, three patterns/scales. Explicit invertible shear and checked Householder factors prescribe distinct finite complex spectra. One-to-one eigenvalue matching, normalized left/right eigenvectors, both residual equations and exact input preservation. Eigenvector phases/order unrestricted; defective, clustered and infinite spectra excluded.

### stdlib-complex-generalized-eigenvectors-reference (D4b4)

Independent API consumer; pinned sources reviewed. 63 COMPLEX128 general nonsingular matrix-pair eigenproblems of sizes 2..8, three patterns/scales. Explicit invertible shear and checked Householder factors prescribe distinct finite complex spectra. One-to-one eigenvalue matching, GGEV-scaled left/right eigenvectors, both residual equations and exact input preservation. Eigenvector phases/order unrestricted; defective, clustered and infinite spectra excluded.

### stdlib-integer-uniform-pmf-reference (L5a1u)

Independent API consumer; pinned sources reviewed. 3672 integer32 support queries: loc=-8..8, positive scale=1..16, x=loc-2..loc+scale+2. Exact enumeration of inclusive support loc..loc+scale supplies masses and normalization. Integer overload returns default REAL32, so absolute tolerance is 2e-7. Zero/negative scale and overflow excluded.

### stdlib-integer-uniform-cdf-reference (L5a1u)

Independent API consumer; pinned sources reviewed. 3672 integer32 support queries: loc=-8..8, positive scale=1..16, x=loc-2..loc+scale+2. Exact enumeration of inclusive support loc..loc+scale supplies cumulative counts and endpoint checks. Integer overload returns default REAL32, so absolute tolerance is 2e-7. Zero/negative scale and overflow excluded.

### stdlib-masked-real-medians-reference (L1a1a)

Independent API consumer; pinned sources reviewed. 90 variable-specific REAL64 masked median selections, n=3..12 and three dyadic-data patterns. Python exact rational order statistics, ties and odd/even sample counts; rank-one and rank-two dim=1/2 reductions and ignored-value replacement. Empty masks and nonfinite data excluded.

### stdlib-masked-real-moments-reference (L1a1c)

Independent API consumer; pinned sources reviewed. 1080 REAL64 masked moment references: orders 2..5, n=3..12, three patterns, variable-specific masks and default mean/zero/supplied dyadic centers. Exact rational binomial expansion of raw powers; rank-one and dim=1/2 calls. No empty masks, nonfinite or high-order stability claim.

### stdlib-complex-pairwise-missingness-reference (L1c1b)

Independent API consumer; pinned sources reviewed. 15 three-variable COMPLEX128 datasets with different observation masks per variable; 135 pairwise intersections each containing at least three observations. Exact rational cross-moments and 80/120-digit normalization, population/sample covariance, correlation and transpose conjugacy. Excluded finite sentinels must be ignored. Pairwise deletion is not claimed to preserve positive semidefiniteness; empty/constant pairs excluded.

## Provenance and actual output

### stdlib-trapz-grid-weights-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-trapz-grid-weights-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-trapz-grid-weights-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L46) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_trapz_weights.f90)

```text
Irregular-grid weight cases and exact polynomial integrals: 102
PASS stdlib-trapz-grid-weights-reference
```

### stdlib-simps-grid-weights-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-simps-grid-weights-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-simps-grid-weights-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L95) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_simps_weights.f90)

```text
Irregular-grid weight cases and exact polynomial integrals: 306
PASS stdlib-simps-grid-weights-reference
```

### stdlib-complex-matrix-norms-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-matrix-norms-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-matrix-norms-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L6082) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_mnorm.f90)

```text
Complex rectangular one/infinity/Frobenius norm matrices: 108
PASS stdlib-complex-matrix-norms-reference
```

### stdlib-complex-eigenvectors-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-eigenvectors-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-eigenvectors-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3469) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_eig.f90)

```text
Distinct prescribed spectra and left/right residuals: 63
PASS stdlib-complex-eigenvectors-reference
```

### stdlib-complex-generalized-eigenvectors-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-generalized-eigenvectors-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-generalized-eigenvectors-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3505) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_eig_generalized.f90)

```text
Distinct prescribed spectra and left/right residuals: 63
PASS stdlib-complex-generalized-eigenvectors-reference
```

### stdlib-integer-uniform-pmf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-integer-uniform-pmf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-integer-uniform-pmf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_uniform.f90#L57) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_uniform_pdf.f90)

```text
Inclusive integer uniform support-count comparisons: 3672
PASS stdlib-integer-uniform-pmf-reference
```

### stdlib-integer-uniform-cdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-integer-uniform-cdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-integer-uniform-cdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_uniform.f90#L76) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_uniform_cdf.f90)

```text
Inclusive integer uniform support-count comparisons: 3672
PASS stdlib-integer-uniform-cdf-reference
```

### stdlib-masked-real-medians-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-masked-real-medians-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-masked-real-medians-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L1230) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_median.f90)

```text
Masked reductions against exact rational references: 90
PASS stdlib-masked-real-medians-reference
```

### stdlib-masked-real-moments-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-masked-real-moments-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-masked-real-moments-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L2647) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_moment.f90)

```text
Masked reductions against exact rational references: 1080
PASS stdlib-masked-real-moments-reference
```

### stdlib-complex-pairwise-missingness-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-pairwise-missingness-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-pairwise-missingness-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L450) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_cov.f90)

```text
Variable-specific missingness datasets and pairwise deletion references: 15
PASS stdlib-complex-pairwise-missingness-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-trapz-grid-weights-reference stdlib-simps-grid-weights-reference stdlib-complex-matrix-norms-reference stdlib-complex-eigenvectors-reference stdlib-complex-generalized-eigenvectors-reference stdlib-integer-uniform-pmf-reference stdlib-integer-uniform-cdf-reference stdlib-masked-real-medians-reference stdlib-masked-real-moments-reference stdlib-complex-pairwise-missingness-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
