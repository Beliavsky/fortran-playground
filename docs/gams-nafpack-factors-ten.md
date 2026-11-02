# Ten checked NAFPack factorization drivers

Ten independent REAL64 NAFPack consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. The existing cached library was reused; only main.f90 and playground-main were compiled. The [verification report](gams-nafpack-factors-ten-validation.json) records normalized UTF-8/LF source hashes, exact pins, timings and full output. GAMS coverage remains unfinished.

## Checked APIs and references

| Driver | GAMS | Independent checks |
| --- | --- | --- |
| Triangular substitution | D2a3 | 27 lower/upper pairs; known vector solutions and residuals |
| Known LU factors | D2a1 | 27 known unit-lower/upper factorizations, reconstruction and solved RHS |
| Known LDU factors | D2a1 | 27 known L,D,U factors, unit triangular diagonals and reconstruction |
| Cholesky lower factor | D2b1b | 27 known lower factors; consume only written lower entries and reconstruct SPD matrices |
| Known LDL-transpose factors | D2b1b | 27 known unit-lower/positive diagonal factors and reconstruction |
| Householder QR | D5 | 27 full-rank square cases; orthogonality, triangularity, reconstruction and solved RHS |
| Givens QR | D5 | Same independent checks on 27 cases |
| Classical Gram-Schmidt QR | D5 | Same independent checks on 27 cases |
| Modified Gram-Schmidt QR | D5 | Same independent checks on 27 cases |
| Characteristic coefficients | D4c | 15 known spectra; independent polynomial products, scalar root evaluations and Cayley-Hamilton residuals |

All drivers explicitly require NAFPack REAL64 storage and finite results. The scalar tolerance is abs(actual-reference)<=2e-9*max(1,abs(reference)); matrix checks also verify shape. No upstream numerical source was patched. These bounded tests do not establish performance, difficult-matrix accuracy or behavior outside the demonstrated domains.

## Known factors and triangular solves

The nine solve/factor drivers use n=2..10 at scales 1/2,1,2. Deterministic dyadic unit-lower factors and nonsingular upper factors form A=L*U. For LU, both returned factors are checked individually before reconstructing A. A manufactured solution supplies a RHS for the returned forward/backward factors. LDU checks the known diagonal and corresponding unit-upper factor separately. These unpivoted decompositions are tested only with nonzero leading minors; matrices requiring pivoting are excluded.

The triangular-substitution driver independently forms RHS values from the original known triangular matrices, then checks each recovered solution and direct residual. LDL-transpose cases use A=L*D*transpose(L), with positive diagonal D and known unit-lower L. This verifies the SPD path, not pivoted indefinite LDL.

## Cholesky output convention

The pinned Cholesky_decomposition writes the diagonal and lower triangle of its output but leaves the upper triangle unwritten. The driver never reads those unwritten entries. It copies the lower entries into a separate zero-filled matrix, checks them against a known lower-triangular factor, and verifies A=L*transpose(L). It does not claim the returned upper triangle contains zeros. Nonpositive-definite or singular inputs are excluded.

## Four QR algorithms

Each direct QR API is checked separately on 27 square full-rank matrices. The driver checks transpose(Q)*Q=I, every entry below R diagonal, and Q*R=A. A known solution gives b=A*x; a local upper-triangular substitution applied to transpose(Q)*b must recover x, and the original matrix must reproduce b. This uses the returned factors to solve an actual system while keeping the known solution independent of the algorithm. Factor signs are not prescribed. Rectangular, rank-deficient and ill-conditioned cases, pivoted QR and stability comparisons are excluded.

## Characteristic-polynomial coefficients

For n=2..6 and three scales, the driver constructs an analytic Householder matrix Q and distinct signed eigenvalues d, then A=Q*diag(d)*transpose(Q). Independently multiplying the linear factors (lambda-d_i) supplies every expected coefficient in descending-power order. Faddeev_Leverrier results must match these coefficients, vanish at each known eigenvalue under scalar Horner evaluation, and satisfy the matrix Cayley-Hamilton identity under matrix Horner evaluation. The optional inverse output is not requested or verified. Large degree and ill-conditioned coefficient problems are excluded. D4c is the broad GAMS associated-eigenvalue-operations class; no unsupported finer leaf is invented.

## Provenance and maintenance

Pinned public interfaces and implementations were reviewed directly. No matching direct-call author examples for these routines were found in the reviewed pinned test tree, so author_example is null rather than pointing at unrelated Fourier or array examples. The consumers are original MIT examples and copy no implementation bodies. Classifications follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). Loading a driver does not submit a job. The [coverage report](gams-coverage.md) tracks remaining work.

## Driver details

### nafpack-triangular-substitution-reference (D2a3)

Independent API consumer. 27 known lower/upper triangular pairs, n=2..10 and three scales. Manufactured vector RHS, exact solutions and direct residuals checked independently. No zero-diagonal, singular or extreme-scale inputs.

### nafpack-known-lu-factors-reference (D2a1)

Independent API consumer. 27 matrices constructed from known unit-lower and nonsingular upper factors. Both exact factors, A=L*U, triangular structure and manufactured-solution forward/back substitution checked. Unpivoted LU with nonzero leading minors only.

### nafpack-known-ldu-factors-reference (D2a1)

Independent API consumer. 27 matrices constructed from known L,D,U factors, unit diagonals in L/U, three scales and n=2..10. Individual factors and reconstruction checked independently. No pivoting, singular leading minors or ill-conditioned matrices.

### nafpack-cholesky-lower-factor-reference (D2b1b)

Independent API consumer. 27 SPD matrices formed from known lower-triangular factors. Only returned lower-triangle entries are consumed, copied to a zero-filled matrix and checked against exact factors and A=L*transpose(L). Pinned implementation does not write the upper triangle; no zero-upper-output claim. Non-SPD inputs excluded.

### nafpack-known-ldlt-factors-reference (D2b1b)

Independent API consumer. 27 SPD matrices formed from known unit-lower factors and positive diagonal D. Individual factors and A=L*D*transpose(L) checked. No pivoted indefinite LDL, singular or non-SPD claim.

### nafpack-qr-householder-reference (D5)

Independent API consumer. 27 square full-rank matrices n=2..10 and three scales, Householder QR. Orthogonality, upper-triangular R, reconstruction and manufactured-solution back substitution checked. Signs are not fixed; rectangular, rank-deficient and ill-conditioned cases excluded.

### nafpack-qr-givens-reference (D5)

Independent API consumer. 27 square full-rank matrices n=2..10 and three scales, Givens QR. Orthogonality, upper-triangular R, reconstruction and manufactured-solution back substitution checked. Signs are not fixed; rectangular, rank-deficient and ill-conditioned cases excluded.

### nafpack-qr-classical-gram-schmidt-reference (D5)

Independent API consumer. 27 square full-rank matrices n=2..10 and three scales, Gram_Schmidt_Classical QR. Orthogonality, upper-triangular R, reconstruction and manufactured-solution back substitution checked. Signs are not fixed; rectangular, rank-deficient and ill-conditioned cases excluded.

### nafpack-qr-modified-gram-schmidt-reference (D5)

Independent API consumer. 27 square full-rank matrices n=2..10 and three scales, Gram_Schmidt_Modified QR. Orthogonality, upper-triangular R, reconstruction and manufactured-solution back substitution checked. Signs are not fixed; rectangular, rank-deficient and ill-conditioned cases excluded.

### nafpack-characteristic-coefficients-reference (D4c)

Independent API consumer. 15 known Householder-rotated spectra, n=2..6 and three scales. Every characteristic coefficient checked against independently multiplied linear factors, plus Cayley-Hamilton matrix residual and scalar root evaluations. Optional inverse output, large degree, repeated roots and ill-conditioned coefficient problems excluded.

## Provenance and actual output

### nafpack-triangular-substitution-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-triangular-substitution-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-triangular-substitution-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_decomposition.f90#L28) / No pinned author example; API reviewed directly.

```text
27 known matrix families, dimensions 2..10 and three scales, checked.
PASS nafpack-triangular-substitution-reference
```

### nafpack-known-lu-factors-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-known-lu-factors-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-known-lu-factors-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_decomposition.f90#L67) / No pinned author example; API reviewed directly.

```text
27 known matrix families, dimensions 2..10 and three scales, checked.
PASS nafpack-known-lu-factors-reference
```

### nafpack-known-ldu-factors-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-known-ldu-factors-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-known-ldu-factors-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_decomposition.f90#L95) / No pinned author example; API reviewed directly.

```text
27 known matrix families, dimensions 2..10 and three scales, checked.
PASS nafpack-known-ldu-factors-reference
```

### nafpack-cholesky-lower-factor-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-cholesky-lower-factor-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-cholesky-lower-factor-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_decomposition.f90#L179) / No pinned author example; API reviewed directly.

```text
27 known matrix families, dimensions 2..10 and three scales, checked.
PASS nafpack-cholesky-lower-factor-reference
```

### nafpack-known-ldlt-factors-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-known-ldlt-factors-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-known-ldlt-factors-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_decomposition.f90#L200) / No pinned author example; API reviewed directly.

```text
27 known matrix families, dimensions 2..10 and three scales, checked.
PASS nafpack-known-ldlt-factors-reference
```

### nafpack-qr-householder-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-qr-householder-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-qr-householder-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_decomposition.f90#L283) / No pinned author example; API reviewed directly.

```text
27 known matrix families, dimensions 2..10 and three scales, checked.
PASS nafpack-qr-householder-reference
```

### nafpack-qr-givens-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-qr-givens-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-qr-givens-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_decomposition.f90#L333) / No pinned author example; API reviewed directly.

```text
27 known matrix families, dimensions 2..10 and three scales, checked.
PASS nafpack-qr-givens-reference
```

### nafpack-qr-classical-gram-schmidt-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-qr-classical-gram-schmidt-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-qr-classical-gram-schmidt-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_decomposition.f90#L360) / No pinned author example; API reviewed directly.

```text
27 known matrix families, dimensions 2..10 and three scales, checked.
PASS nafpack-qr-classical-gram-schmidt-reference
```

### nafpack-qr-modified-gram-schmidt-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-qr-modified-gram-schmidt-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-qr-modified-gram-schmidt-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_decomposition.f90#L383) / No pinned author example; API reviewed directly.

```text
27 known matrix families, dimensions 2..10 and three scales, checked.
PASS nafpack-qr-modified-gram-schmidt-reference
```

### nafpack-characteristic-coefficients-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-characteristic-coefficients-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-characteristic-coefficients-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/linear_algebra/Matrix/NAFPack_matrix_tools.f90#L13) / No pinned author example; API reviewed directly.

```text
15 characteristic polynomials: coefficient products and Cayley-Hamilton checked.
PASS nafpack-characteristic-coefficients-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers nafpack-triangular-substitution-reference nafpack-known-lu-factors-reference nafpack-known-ldu-factors-reference nafpack-cholesky-lower-factor-reference nafpack-known-ldlt-factors-reference nafpack-qr-householder-reference nafpack-qr-givens-reference nafpack-qr-classical-gram-schmidt-reference nafpack-qr-modified-gram-schmidt-reference nafpack-characteristic-coefficients-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
