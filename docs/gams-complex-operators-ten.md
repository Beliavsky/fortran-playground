# Ten checked complex matrix operator and fitting drivers

Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. Existing stdlib libraries were reused; only mains and executables were compiled. The [verification report](gams-complex-operators-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings and complete output. GAMS categories are not exhausted.

## Independent references and scope

All ten drivers exercise COMPLEX128 APIs. Independent mathematical constructions define expected answers, with residuals and structural identities as additional checks. The pinned public API declarations, implementations and linked author examples were reviewed. The examples are independent MIT consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source was patched.

- **Determinants (D3c1):** 72 matrices of sizes 1..8, three diagonal spectra and three dyadic scales. Unitary similarity preserves the known product of diagonal entries; a cyclic row permutation adds an independently known sign. This checks nonzero complex determinants and exact input preservation.
- **Inverses (D2c1):** 72 matrices with independent reciprocal-diagonal inverses under checked unitary similarity. Both left and right identity residuals and input preservation are checked.
- **Pseudoinverses (D9c):** 150 tall/square/wide cases from 25 shapes, full-rank and one-zero-singular-value patterns, and three scales. Reciprocal nonzero singular values supply the expected pseudoinverse. All four Moore-Penrose identities and input preservation are checked with explicit rtol=1e-12.
- **QR (D5):** 150 full/reduced factorizations across 25 tall/square/wide shapes and three upper-trapezoidal templates. Reconstruction, orthonormal columns, upper-trapezoidal zeros and prescribed diagonal magnitudes are checked without imposing factor phases.
- **Schur (D4a4):** 63 nonnormal matrices from known complex upper-triangular templates under unitary similarity. Eigenvalues are matched one-to-one without assuming order. Unitary Schur vectors, triangularity, reconstruction and preservation are checked.
- **Matrix exponential (D):** 180 evaluations for sizes 2..7, three superdiagonal templates, five scales and default/order-12 Pade. For A=lambda*I+N with nilpotent N, the independent answer is exp(lambda) times the finite sum of N^j/j! for j=0..n-1. The next nilpotent term is explicitly checked as zero.
- **General linear systems (D2c1):** 144 vector/multiple-RHS calls with known complex coefficients in row-reversed diagonally dominant matrices of sizes 1..8. Residuals and preservation are checked.
- **Positive-definite systems (D2d1b):** 288 vector/multiple-RHS calls on 72 known-factor matrices with lower/upper factorizations. Coefficients, residuals and preservation are checked. Both triangles are populated.
- **Weighted least squares (D9a1):** 45 overdetermined full-column-rank fits with weights 1, 4 and 16. Known coefficients and a nonzero weighted-orthogonal residual provide independent references; weighted stationarity, rank and preservation are checked.
- **Equality-constrained least squares (D9b1):** 72 fits with one complex equality and a full-column-rank cost. A closed-form complex diagonal-Hessian KKT correction supplies the minimizer. Coefficients, equality feasibility, stationarity and preservation of A, b, C and d are checked.

## Mathematical constructions

The drivers construct Q=I-2*v*v^H/(v^H*v) locally and check Q^H*Q before using Q. Determinant/inverse examples use Q*diag(z)*Q^H with nonzero prescribed z. Pseudoinverses use A=Q*Sigma*P^H and A+=P*Sigma+*Q^H. QR uses Q times a known upper trapezoid; Schur uses Q*T*Q^H with known nonnormal triangular T. No library factorization is used to manufacture these references.

For weighted fitting, sqrt(w) is an exact power of two. The columns of sqrt(W)*A are checked-unitary columns scaled by j+1, and sqrt(W)*r is a nonzero multiple of the next orthogonal column. For constrained fitting, write y=Q*x and H=diag(5*D^2). The unconstrained minimizer is u=(D*b1+2*D*b2)/diag(H). For the nonconjugated equality c*y=d, lambda=(c*u-d)/(c*H^-1*c^H), y=u-H^-1*c^H*lambda and x=Q^H*y. The stationarity assertion uses A^H*(A*x-b)+C^H*lambda=0. These formulas retain the conjugations required for genuinely complex constraints.

All real/imaginary components must be finite and agree to scaled absolute tolerance 2e-10*max(1,abs(reference component)); input-preservation assertions are exact. The tests are bounded, moderately conditioned examples, not a precision or performance benchmark. Singular square solves, ill-conditioned inverses, near-cutoff pseudoinverse decisions, zero matrices, extreme weights, deficient fitting ranks, inequalities, repeated/clustered Schur spectra, pivoted QR and poisoned unused triangles remain outside these drivers. The exponential driver covers bounded nonnormal Jordan-type matrices, not general matrix-function stability.

## GAMS classification and provenance

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies general complex non-Hermitian determinants (D3c1), systems/inversion (D2c1), positive-definite complex Hermitian systems (D2d1b), ordinary complex non-Hermitian spectra (D4a4), QR (D5), unconstrained least squares (D9a1), constrained least squares (D9b1) and generalized inverses (D9c). The matrix exponential retains broad D rather than inventing a matrix-function leaf. Loading an example does not submit a job. The [coverage report](gams-coverage.md) records remaining work.

## Driver details

### stdlib-complex-determinants-reference (D3c1)

Independent API consumer; pinned sources reviewed. 72 COMPLEX128 determinants: sizes 1..8, three spectral patterns and three scales; checked unitary similarity of prescribed nonzero complex diagonal entries followed by a cyclic row permutation. Independent product and permutation sign; input preservation. Singular matrices, overflow and extreme conditioning excluded.

### stdlib-complex-inverses-reference (D2c1)

Independent API consumer; pinned sources reviewed. 72 COMPLEX128 inverses: sizes 1..8, three patterns and three scales. Checked unitary similarity gives independent reciprocal-diagonal inverse; both left/right identity residuals and exact input preservation. Singular and ill-conditioned matrices excluded.

### stdlib-complex-pseudoinverses-reference (D9c)

Independent API consumer; pinned sources reviewed. 150 COMPLEX128 pseudoinverses on 25 tall/square/wide shapes, full-rank and one-zero-singular-value spectra, three scales. Independent reciprocal nonzero singular values, all four Moore-Penrose identities and input preservation; explicit rtol=1e-12. Near-cutoff singular values, zero matrices and other tolerances excluded.

### stdlib-complex-qr-reference (D5)

Independent API consumer; pinned sources reviewed. 150 COMPLEX128 QR factorizations: 25 tall/square/wide shapes, three prescribed upper-trapezoidal patterns, full/reduced outputs. Checked unitary-times-triangular construction supplies diagonal magnitudes; reconstruction, orthonormal columns, triangular zeros and input preservation. No fixed phases, pivoted or rank-deficient QR claim.

### stdlib-complex-schur-reference (D4a4)

Independent API consumer; pinned sources reviewed. 63 COMPLEX128 Schur decompositions of nonnormal matrices: sizes 2..8, three triangular templates and three scales under checked unitary similarity. Independent diagonal eigenvalues matched one-to-one without ordering assumptions; Schur triangularity, unitary vectors, reconstruction and input preservation. Repeated/clustered eigenvalues and sorting excluded.

### stdlib-complex-matrix-exponential-reference (D)

Independent API consumer; pinned sources reviewed. 180 COMPLEX128 matrix exponentials: sizes 2..7, three nilpotent superdiagonal patterns, five scales, default and order-12 Pade. Independent finite Taylor polynomial for nilpotent N and scalar exp(lambda) for A=lambda*I+N; input preservation. Bounded nonnormal Jordan-type cases only, no general stability/performance claim.

### stdlib-complex-general-systems-reference (D2c1)

Independent API consumer; pinned sources reviewed. 144 COMPLEX128 general linear solves: sizes 1..8, three patterns, three scales, vector and three-column RHS. Row-reversed diagonally dominant non-Hermitian matrices with manufactured solutions; residuals and input preservation. Singular/ill-conditioned cases and overwrite mode excluded.

### stdlib-complex-positive-systems-reference (D2d1b)

Independent API consumer; pinned sources reviewed. 288 COMPLEX128 positive-definite solves: 72 known-factor matrices of sizes 1..8, three patterns/scales, vector and multiple RHS with lower/upper factorization. Manufactured coefficients, residuals and preservation. Both triangles populated; no indefinite or poisoned-unused-triangle behavior claimed.

### stdlib-complex-weighted-fits-reference (D9a1)

Independent API consumer; pinned sources reviewed. 45 COMPLEX128 weighted least-squares fits: n=1..5, m=n+2..n+4, three unitary patterns. Positive weights are exact squares 1,4,16; weighted design columns and a nonzero weighted residual are orthogonal by construction. Known coefficients, rank, weighted stationarity and input preservation checked. Extreme/zero weights and rank deficiency excluded.

### stdlib-complex-equality-fits-reference (D9b1)

Independent API consumer; pinned sources reviewed. 72 COMPLEX128 equality-constrained fits: n=2..7, four unitary patterns, three diagonal scales. Independent diagonal-Hessian one-complex-equality KKT minimizer transformed by checked unitary coordinates; coefficients, feasibility, stationarity and all input preservation. Only one full-row-rank equality and full-column-rank cost; inequalities and deficient ranks excluded.

## Provenance and actual output

### stdlib-complex-determinants-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-determinants-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-determinants-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2666) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_determinant.f90)

```text
Complex determinants versus diagonal products and cyclic permutation signs: 72
PASS stdlib-complex-determinants-reference
```

### stdlib-complex-inverses-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-inverses-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-inverses-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2812) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_inverse_function.f90)

```text
Known reciprocal-spectrum complex inverses and two-sided residuals: 72
PASS stdlib-complex-inverses-reference
```

### stdlib-complex-pseudoinverses-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-pseudoinverses-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-pseudoinverses-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3013) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_pseudoinverse.f90)

```text
Known complex pseudoinverses and four Moore-Penrose identities: 150
PASS stdlib-complex-pseudoinverses-reference
```

### stdlib-complex-qr-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-qr-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-qr-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2216) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_qr.f90)

```text
Known-trapezoid complex QR full/reduced factorizations: 150
PASS stdlib-complex-qr-reference
```

### stdlib-complex-schur-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-schur-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-schur-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2458) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_schur_complex.f90)

```text
Known-spectrum nonnormal complex Schur decompositions: 63
PASS stdlib-complex-schur-reference
```

### stdlib-complex-matrix-exponential-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-matrix-exponential-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-matrix-exponential-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L6437) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_expm.f90)

```text
Finite-polynomial complex matrix exponentials, default/order 12: 180
PASS stdlib-complex-matrix-exponential-reference
```

### stdlib-complex-general-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-general-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-general-systems-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L734) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_solve.f90)

```text
Manufactured general complex vector and multiple-RHS linear solves: 144
PASS stdlib-complex-general-systems-reference
```

### stdlib-complex-positive-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-positive-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-positive-systems-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1052) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_solve_chol.f90)

```text
Manufactured positive-definite complex solves, vector/multiple RHS, lower/upper: 288
PASS stdlib-complex-positive-systems-reference
```

### stdlib-complex-weighted-fits-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-weighted-fits-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-weighted-fits-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2122) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_weighted_lstsq.f90)

```text
Known-coefficient complex weighted fits with nonzero weighted-orthogonal residual: 45
PASS stdlib-complex-weighted-fits-reference
```

### stdlib-complex-equality-fits-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-equality-fits-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-equality-fits-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1903) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_constrained_lstsq1.f90)

```text
Closed-form complex equality-constrained KKT minimizers, feasibility and stationarity: 72
PASS stdlib-complex-equality-fits-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-complex-determinants-reference stdlib-complex-inverses-reference stdlib-complex-pseudoinverses-reference stdlib-complex-qr-reference stdlib-complex-schur-reference stdlib-complex-matrix-exponential-reference stdlib-complex-general-systems-reference stdlib-complex-positive-systems-reference stdlib-complex-weighted-fits-reference stdlib-complex-equality-fits-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
