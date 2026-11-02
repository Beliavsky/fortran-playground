# Ten checked stdlib matrix and complex linear algebra drivers

Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. Existing stdlib libraries were reused; only mains and executables were compiled. The [verification report](gams-complex-ten-validation.json) saves normalized UTF-8/LF source hashes, package pins, timings and complete output. GAMS categories are not exhausted.

## Independent references and scope

The first five drivers check elementary matrix operations, predicates and vector norms. The next five exercise pivoted LU and complex Cholesky, Hermitian eigenpairs, thin SVD and least squares. The drivers are independent MIT consumers; pinned API declarations, implementations and linked author examples were reviewed. Upstream implementations and test bodies were not copied. No upstream numerical source was patched.

- **Trace (D1b):** 90 rectangular shapes, including empty dimensions, for REAL64, COMPLEX128 and INT64. Closed-form diagonal sums follow from polynomial entry formulas; input preservation is checked. Rectangular trace means summing through min(m,n).
- **Identity (D1b1):** 90 rectangular identities in three kinds and ten default square shapes, checked by entrywise Kronecker deltas, including empty shapes.
- **Conjugate transpose (D1b3):** 90 real/complex rectangular shapes, including empty shapes. Independent coordinate formulas check transposition, conjugation and input preservation; involution is a secondary check.
- **Structure predicates (R2):** 204 one-hot positions in sizes 1..8, zero matrices, positive real symmetric/skew pairs and genuinely complex Hermitian pairs. Seven APIs distinguish exact structural properties; both triangle orientations and 42 rectangular squareness checks are included. This is an exact-zero test, not approximate symmetry.
- **Vector norms (D1a3):** the exact 3-4-12 Pythagorean triple plus zero gives L1=19, L2=13, Linf=12 and minimum magnitude 0. Seventeen dyadic scales, complex coordinate phases and rank-two dimension reductions use known column factors and independent square-root references. Only orders 1, 2, inf and -inf are claimed.
- **Pivoted LU (D2a1):** 120 REAL64 calls for sizes 1..10, three scales, vector/multiple right-hand sides, preservation and overwrite modes. Row-reversed diagonally dominant matrices have known manufactured solutions; solution errors, residuals and pivot ranges are checked.
- **Complex Cholesky (D2d1b):** 72 positive-definite matrices formed from explicit positive-diagonal lower factors, tested with 144 lower/upper calls. The unique factors, reconstruction, zero unused triangles and input preservation are checked.
- **Complex Hermitian eigenpairs (D4a3):** 320 solves for sizes 2..9, four independently checked unitary patterns, five scales and both storage triangles. Prescribed distinct eigenvalues, eigenpair residuals, orthonormality, reconstruction and input preservation are checked. Eigenvector phases are unrestricted.
- **Complex thin SVD (D6):** 150 cases covering 25 tall/square/wide shapes, full-rank and one-zero-singular-value spectra, and three scales. Known singular values, reconstruction and both singular-vector Gram matrices are checked, without fixing phases or null-space bases.
- **Complex least squares (D9a1):** 45 full-column-rank overdetermined systems with known coefficients and a nonzero residual in an independently checked orthogonal complement. Coefficients, rank, residual, A^H*r stationarity and input preservation are checked. Rank-deficient and underdetermined minimum-norm problems remain outside this driver.

## Manufacturing the complex problems

Each unitary matrix is constructed locally as Q=I-2*v*v^H/(v^H*v), with integer real/imaginary entries of v and nonzero denominator. Q^H*Q is explicitly checked before Q is used. Eigenproblems use A=Q*diag(lambda)*Q^H with prescribed distinct integer eigenvalues at dyadic scales. SVD uses A=Q*Sigma*P^H with prescribed singular values. Least squares uses columns Q(:,j)*(j+1), a known coefficient vector and a nonzero multiple of Q(:,n+1) as residual. Cholesky uses a directly specified triangular factor with positive real diagonal. These constructions supply mathematical references independently of the package routines under test.

Real and imaginary components must be finite and agree to scaled absolute tolerance 2e-10*max(1,abs(reference component)); integer/predicate and input-preservation checks are exact. These are bounded, moderately conditioned examples, not a precision benchmark. Extreme scales, ill-conditioned systems, repeated eigenvalues, singular/error handling and other overloads need separate drivers. Full storage is populated even when selecting an upper/lower triangle; poisoned-unused-triangle behavior is not tested.

## GAMS classifications

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies elementary matrix operations (D1b), initialization (D1b1), transpose (D1b3), vector norms (D1a3), error checking (R2), general real systems (D2a1), positive-definite complex Hermitian systems/factorization (D2d1b), ordinary complex Hermitian eigenproblems (D4a3), SVD (D6) and linear least squares (D9a1). Predicates do not claim to solve the matrix problems they recognize. Loading a driver does not submit a job. The [coverage report](gams-coverage.md) records remaining work.

## Driver details

### stdlib-matrix-trace-reference (D1b)

Independent API consumer; pinned sources reviewed. REAL64, COMPLEX128 and INT64 traces for 90 rectangular shapes including empty dimensions; closed-form diagonal sums from entry formulas, plus exact input preservation. Rectangular trace means the sum through min(m,n). Integer overflow and arbitrary kinds excluded.

### stdlib-identity-matrices-reference (D1b1)

Independent API consumer; pinned sources reviewed. 90 rectangular identities with REAL64 default, COMPLEX128 and INT64 mold selection, including empty shapes; entrywise Kronecker-delta references. Ten default square shapes also checked. Negative dimensions excluded.

### stdlib-conjugate-transpose-reference (D1b3)

Independent API consumer; pinned sources reviewed. REAL64 and COMPLEX128 conjugate transpose over 90 rectangular shapes including empty dimensions; independent entry formulas, reversed shapes, exact input preservation and secondary involution. Integer and other overloads excluded.

### stdlib-matrix-structure-reference (R2)

Independent API consumer; pinned sources reviewed. Seven exact matrix predicates: 204 one-hot positions in square sizes 1..8 with real/complex input; zero matrices, real symmetric/skew pairs and genuinely complex Hermitian pairs; triangular/Hessenberg orientations and 42 rectangular squareness checks. No tolerance, nonfinite or invalid-selector behavior claimed.

### stdlib-vector-norms-reference (D1a3)

Independent API consumer; pinned sources reviewed. REAL64/COMPLEX128 vector norms for the exact 3-4-12 triple with zero (L1=19,L2=13,Linf=12,min=0), 17 dyadic scales, and complex coordinate phases. Rank-two arrays have three scaled columns, known aggregate norms and explicit dimension reductions. Only orders 1,2,inf,-inf; no empty or extreme-scale inputs claimed.

### stdlib-pivoted-lu-systems-reference (D2a1)

Independent API consumer; pinned sources reviewed. REAL64 pivoted LU with preallocated solution/pivots: sizes 1..10, three dyadic scales, vector and three-column RHS, both preservation and overwrite_a modes (120 calls). Row-reversed diagonally dominant matrices force pivoting for n>1. Known manufactured solutions, residuals and pivot ranges; singular/error cases excluded.

### stdlib-complex-cholesky-reference (D2d1b)

Independent API consumer; pinned sources reviewed. COMPLEX128 positive-definite matrices manufactured as L*L^H from explicit positive-real-diagonal triangular factors: sizes 1..8, three entry patterns and three scales (72 matrices; 144 lower/upper calls). Compare unique factors, zero unused triangles, reconstruction and input preservation. No indefinite/error cases or extreme conditioning claimed.

### stdlib-complex-hermitian-eigenpairs-reference (D4a3)

Independent API consumer; pinned sources reviewed. COMPLEX128 Hermitian spectra built with independently checked Householder unitary matrices and prescribed distinct integer eigenvalues: sizes 2..9, four patterns, five scales, both lower/upper storage (320 solves). Eigenvalues, residuals, orthonormality, reconstruction and input preservation checked; no phase-specific eigenvector comparison, repeated eigenvalues or generalized problem claimed.

### stdlib-complex-thin-svd-reference (D6)

Independent API consumer; pinned sources reviewed. COMPLEX128 thin SVD for 25 tall/square/wide sizes 2..6, full-rank and one-zero-singular-value spectra, three dyadic scales (150 cases). Independently checked unitary factors manufacture known singular values; reconstruction and both unitary Gram matrices verified without choosing singular-vector phases. No ill-conditioned rank cutoff or full-matrix API claim.

### stdlib-complex-least-squares-reference (D9a1)

Independent API consumer; pinned sources reviewed. COMPLEX128 full-column-rank overdetermined least squares: n=1..5, m=n+2..n+4, three unitary patterns (45 cases). Known coefficients and nonzero residual in an explicitly checked orthogonal complement; recovered coefficients, rank, residual and A^H*r stationarity checked. Inputs preserved; no rank-deficient or underdetermined/minimum-norm claim.

## Provenance and actual output

### stdlib-matrix-trace-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-matrix-trace-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-matrix-trace-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L402) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_trace.f90)

```text
Closed-form trace shapes: 90; three kinds including empty rectangles
PASS stdlib-matrix-trace-reference
```

### stdlib-identity-matrices-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-identity-matrices-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-identity-matrices-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L419) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_eye1.f90)

```text
Kronecker-delta identity references: 90 rectangles in three kinds and 10 default squares
PASS stdlib-identity-matrices-reference
```

### stdlib-conjugate-transpose-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-conjugate-transpose-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-conjugate-transpose-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L646) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_hermitian.f90)

```text
Coordinate conjugate-transpose references: 90 real and complex shapes; secondary involution
PASS stdlib-conjugate-transpose-reference
```

### stdlib-matrix-structure-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-matrix-structure-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-matrix-structure-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L558) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg.f90)

```text
Matrix-structure one-hot positions: 204; seven predicates and 42 rectangular shapes
PASS stdlib-matrix-structure-reference
```

### stdlib-vector-norms-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-vector-norms-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-vector-norms-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L4219) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_norm.f90)

```text
Pythagorean vector norms: 17 scales, real/complex, four orders and rank-two reductions
PASS stdlib-vector-norms-reference
```

### stdlib-pivoted-lu-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-pivoted-lu-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-pivoted-lu-systems-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L916) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_solve.f90)

```text
Manufactured pivoted LU calls (vector/multiple RHS, preserve/overwrite): 120
PASS stdlib-pivoted-lu-systems-reference
```

### stdlib-complex-cholesky-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-cholesky-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-cholesky-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L126) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_cholesky.f90)

```text
Known-factor complex Cholesky lower/upper factorizations: 144
PASS stdlib-complex-cholesky-reference
```

### stdlib-complex-hermitian-eigenpairs-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-hermitian-eigenpairs-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-hermitian-eigenpairs-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3725) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_eigh.f90)

```text
Prescribed-spectrum complex Hermitian eigenproblems: 320
PASS stdlib-complex-hermitian-eigenpairs-reference
```

### stdlib-complex-thin-svd-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-thin-svd-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-thin-svd-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3922) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_svd.f90)

```text
Prescribed-singular-value complex thin SVD cases: 150
PASS stdlib-complex-thin-svd-reference
```

### stdlib-complex-least-squares-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-least-squares-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-least-squares-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1457) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_lstsq1.f90)

```text
Known-coefficient complex least squares with nonzero orthogonal residual: 45
PASS stdlib-complex-least-squares-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-matrix-trace-reference stdlib-identity-matrices-reference stdlib-conjugate-transpose-reference stdlib-matrix-structure-reference stdlib-vector-norms-reference stdlib-pivoted-lu-systems-reference stdlib-complex-cholesky-reference stdlib-complex-hermitian-eigenpairs-reference stdlib-complex-thin-svd-reference stdlib-complex-least-squares-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
