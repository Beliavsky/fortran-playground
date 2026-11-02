# Ten checked banded-matrix and structured-product drivers

Ten independent REAL64 SpecialMatrices consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. The cached library was reused; only main.f90 and playground-main were compiled. The [verification report](gams-banded-products-ten-validation.json) saves normalized UTF-8/LF source hashes, the exact package pin, timings and full output. GAMS coverage remains unfinished.

## Checked problems and independent references

| Driver | GAMS | Cases and oracle |
| --- | --- | --- |
| Symmetric positive systems | D2b2a | 15 variable SPD tridiagonal systems; manufactured solutions, vector and three-column RHS, refinement off/on |
| Symmetric indefinite systems | D2b1a | 15 alternating-sign symmetric tridiagonal systems; general factorization, same independent solution/residual checks |
| Pivoted tridiagonal systems | D2a2a | 15 nonsymmetric systems requiring a first-column row pivot; vector and multiple RHS, refinement off/on |
| Positive tridiagonal determinants | D3b2a | 15 SPD matrices; independent dense elimination with row pivoting |
| Nonsymmetric tridiagonal determinants | D3a2a | 15 matrices with a small leading diagonal; independent pivoted dense determinants |
| Variable tridiagonal eigenpairs | D4a5 | 15 symmetric indefinite matrices; residuals, orthogonality, spectrum invariants and eigenvalues-only agreement |
| Rectangular Toeplitz products | D1b6 | 48 shapes; manual elementwise matrices, vector/matrix products and transpose products |
| Rectangular Hankel products | D1b6 | 48 shapes; independent A(i,j)=v(i+j-1), vector/matrix products and transpose products |
| Bidiagonal systems | D2a3 | 30 lower/upper systems; vector and three-column manufactured solutions |
| Bidiagonal spectra | D4a2 | 30 lower/upper matrices; known distinct diagonal eigenvalues, trace and determinant |

All scalar comparisons require finite results and abs(actual-reference)<=2e-9*max(1,abs(reference)); matrix comparisons also check shape. Square problems cover n=2..16. Matrices, RHS and expected solutions are assembled independently without dense() or another package solver supplying the oracle. Singular, extremely scaled and ill-conditioned cases are excluded.

## Linear systems and determinants

Positive symmetric matrices have variable positive diagonal 3+mod(i,4)/8 and small off-diagonals; strict diagonal dominance establishes positive definiteness. The indefinite family alternates the diagonal signs and uses the general symmetric tridiagonal path. The nonsymmetric family sets the first diagonal to 1/8 and first subdiagonal to 5/4, requiring a first-column pivot. Each of these three solve drivers checks three manufactured RHS together and a separate vector RHS, both with and without refinement. Dense residuals independently verify the matrix convention and returned solution.

Both determinant drivers compare the structured continuant routines against an independently authored dense Gaussian-elimination routine with row pivoting, not a second implementation of the same recurrence. The bidiagonal solver checks lower and upper orientations, alternating-sign nonzero diagonals and variable off-diagonals. These bounded accuracy tests do not characterize conditioning or refinement improvement.

## Spectra

The variable symmetric eigensystem driver uses alternating-sign diagonal matrices and checks every dense eigenvector residual, all column inner products, ascending eigenvalue order, the trace, sum of squared eigenvalues against the dense Frobenius norm squared, and the eigenvalue product against an independent dense determinant. The eigenvalues-only API must also agree. Residuals and orthogonality establish the complete returned eigensystem without invoking a second eigensolver as a reference.

A triangular bidiagonal matrix has the diagonal entries as its spectrum. Both orientations are checked against these known distinct real values using nearest matching, with additional trace and determinant checks. The pinned implementation delegates this API to a dense stdlib eigensolver; this example makes no claim that it exploits a specialized bidiagonal eigenvalue algorithm. Eigenvectors, repeated eigenvalues and strongly nonnormal conditioning are excluded.

## Rectangular products

Toeplitz and Hankel cases cover m=2..7 and n=2..9, including tall, wide and square shapes with odd and even dimensions. Each checks dense conversion, a three-column product, a vector product, dense transpose conversion and transpose-vector multiplication. Toeplitz entries are assembled from first-column/first-row vectors, with the first column defining the shared (1,1) entry. Hankel uses A(i,j)=v(i+j-1). The reference products use ordinary dense intrinsic operations on the manual matrices. No FFT performance or large-size claim is made.

## Provenance and maintenance

Pinned constructors, implementations and linked author tests were reviewed. These original MIT consumers copy no upstream numerical or author-test bodies, and no upstream source was patched. Classifications follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html), including D3 for determinants and D2 for linear systems. Loading an example does not submit a job. The [coverage report](gams-coverage.md) tracks remaining work.

## Driver details

### specialmatrices-symmetric-positive-systems-reference (D2b2a)

Independent API consumer. Variable diagonally dominant symmetric positive-definite tridiagonal systems; explicit positive-definite path. Fifteen dimensions 2..16, three manufactured RHS and separate vector RHS, both refinement settings. Independent solution and dense residual checks; singular and ill-conditioned cases excluded.

### specialmatrices-symmetric-indefinite-systems-reference (D2b1a)

Independent API consumer. Variable symmetric indefinite tridiagonal systems with alternating-sign diagonal; general factorization path. Fifteen dimensions 2..16, three manufactured RHS and separate vector RHS, both refinement settings. Independent solution and dense residual checks; singular and ill-conditioned cases excluded.

### specialmatrices-pivoted-tridiagonal-systems-reference (D2a2a)

Independent API consumer. Nonsymmetric tridiagonal systems with a small leading diagonal and larger first subdiagonal, requiring a first-column pivot. Fifteen dimensions 2..16, three manufactured RHS and separate vector RHS, both refinement settings. Independent solution and dense residual checks; singular and ill-conditioned cases excluded.

### specialmatrices-positive-tridiagonal-determinants-reference (D3b2a)

Independent API consumer. Fifteen dimensions 2..16; structured determinant compared with independent dense Gaussian elimination with row pivoting, not the package continuant recurrence. Positive symmetric banded or nonsymmetric pivot-requiring family as named. Singular and extreme-scale matrices excluded.

### specialmatrices-nonsymmetric-tridiagonal-determinants-reference (D3a2a)

Independent API consumer. Fifteen dimensions 2..16; structured determinant compared with independent dense Gaussian elimination with row pivoting, not the package continuant recurrence. Positive symmetric banded or nonsymmetric pivot-requiring family as named. Singular and extreme-scale matrices excluded.

### specialmatrices-variable-tridiagonal-eigenpairs-reference (D4a5)

Independent API consumer. Fifteen variable symmetric indefinite tridiagonal eigensystems, n=2..16. Dense residuals, full orthogonality, ascending order, eigenvalues-only agreement, trace, Frobenius invariant and determinant product checked. No second eigenvalue library supplies the oracle; repeated or ill-conditioned cases excluded.

### specialmatrices-toeplitz-rectangular-products-reference (D1b6)

Independent API consumer. 48 rectangular shapes m=2..7,n=2..9, including square/tall/wide and odd/even dimensions. Independent elementwise dense reference; vector and three-column matrix products, transpose dense values and transpose-vector products checked. First-column entry overrides the first-row entry at (1,1). Extreme dimensions and FFT performance excluded.

### specialmatrices-hankel-rectangular-products-reference (D1b6)

Independent API consumer. 48 rectangular shapes m=2..7,n=2..9, including square/tall/wide and odd/even dimensions. Independent elementwise dense reference; vector and three-column matrix products, transpose dense values and transpose-vector products checked. A(i,j)=v(i+j-1). Extreme dimensions and FFT performance excluded.

### specialmatrices-bidiagonal-systems-reference (D2a3)

Independent API consumer. Thirty lower/upper bidiagonal systems n=2..16, distinct alternating-sign diagonals and variable off-diagonals. Three manufactured RHS and a separate vector RHS checked against exact solutions and manually assembled dense residuals. Singular diagonals excluded.

### specialmatrices-bidiagonal-spectra-reference (D4a2)

Independent API consumer. Thirty lower/upper bidiagonal spectra n=2..16, compared with known distinct real diagonal eigenvalues using order-independent nearest matching, plus trace and determinant products. Eigenvectors, repeated eigenvalues and ill-conditioned nonnormal families excluded.

## Provenance and actual output

### specialmatrices-symmetric-positive-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-symmetric-positive-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-symmetric-positive-systems-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/SymTridiagonal/solve.f90#L12) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_symtridiagonal_matrices.f90)

```text
15 independently assembled matrices, dimensions 2..16, checked.
PASS specialmatrices-symmetric-positive-systems-reference
```

### specialmatrices-symmetric-indefinite-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-symmetric-indefinite-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-symmetric-indefinite-systems-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/SymTridiagonal/solve.f90#L12) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_symtridiagonal_matrices.f90)

```text
15 independently assembled matrices, dimensions 2..16, checked.
PASS specialmatrices-symmetric-indefinite-systems-reference
```

### specialmatrices-pivoted-tridiagonal-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-pivoted-tridiagonal-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-pivoted-tridiagonal-systems-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Tridiagonal/solve.f90#L12) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_tridiagonal_matrices.f90)

```text
15 independently assembled matrices, dimensions 2..16, checked.
PASS specialmatrices-pivoted-tridiagonal-systems-reference
```

### specialmatrices-positive-tridiagonal-determinants-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-positive-tridiagonal-determinants-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-positive-tridiagonal-determinants-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/SymTridiagonal/det.f90#L5) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_symtridiagonal_matrices.f90)

```text
15 independently assembled matrices, dimensions 2..16, checked.
PASS specialmatrices-positive-tridiagonal-determinants-reference
```

### specialmatrices-nonsymmetric-tridiagonal-determinants-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-nonsymmetric-tridiagonal-determinants-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-nonsymmetric-tridiagonal-determinants-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Tridiagonal/det.f90#L5) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_tridiagonal_matrices.f90)

```text
15 independently assembled matrices, dimensions 2..16, checked.
PASS specialmatrices-nonsymmetric-tridiagonal-determinants-reference
```

### specialmatrices-variable-tridiagonal-eigenpairs-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-variable-tridiagonal-eigenpairs-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-variable-tridiagonal-eigenpairs-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/SymTridiagonal/eigh.f90#L50) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_symtridiagonal_matrices.f90)

```text
15 independently assembled matrices, dimensions 2..16, checked.
PASS specialmatrices-variable-tridiagonal-eigenpairs-reference
```

### specialmatrices-toeplitz-rectangular-products-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-toeplitz-rectangular-products-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-toeplitz-rectangular-products-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Toeplitz/constructors.f90#L5) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_toeplitz.f90)

```text
48 rectangular shapes: dense, vector/matrix products and transposes checked.
PASS specialmatrices-toeplitz-rectangular-products-reference
```

### specialmatrices-hankel-rectangular-products-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-hankel-rectangular-products-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-hankel-rectangular-products-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Hankel/constructors.f90#L5) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_hankel.f90)

```text
48 rectangular shapes: dense, vector/matrix products and transposes checked.
PASS specialmatrices-hankel-rectangular-products-reference
```

### specialmatrices-bidiagonal-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-bidiagonal-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-bidiagonal-systems-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Bidiagonal/solve.f90#L40) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_bidiagonal_matrices.f90)

```text
30 lower/upper bidiagonal matrices, dimensions 2..16, checked.
PASS specialmatrices-bidiagonal-systems-reference
```

### specialmatrices-bidiagonal-spectra-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-bidiagonal-spectra-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-bidiagonal-spectra-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Bidiagonal/eig.f90#L6) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_bidiagonal_matrices.f90)

```text
30 lower/upper bidiagonal matrices, dimensions 2..16, checked.
PASS specialmatrices-bidiagonal-spectra-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers specialmatrices-symmetric-positive-systems-reference specialmatrices-symmetric-indefinite-systems-reference specialmatrices-pivoted-tridiagonal-systems-reference specialmatrices-positive-tridiagonal-determinants-reference specialmatrices-nonsymmetric-tridiagonal-determinants-reference specialmatrices-variable-tridiagonal-eigenpairs-reference specialmatrices-toeplitz-rectangular-products-reference specialmatrices-hankel-rectangular-products-reference specialmatrices-bidiagonal-systems-reference specialmatrices-bidiagonal-spectra-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
