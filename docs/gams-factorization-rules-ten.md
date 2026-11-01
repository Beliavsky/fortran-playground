# Ten checked stdlib factorization, matrix and quadrature drivers

Ten newly reviewed stdlib procedures passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox on their first verification runs. Existing compiled stdlib libraries were reused; only mains and executables were compiled. The [verification report](gams-factorization-rules-ten-validation.json) records package pins, normalized source hashes, timings and complete output. GAMS categories are not exhausted.

## Factorizations and spectral references

For 64 real 5x3 inputs, full and reduced QR must reconstruct the input, have orthonormal Q columns and triangular R. These defining equations avoid assuming a particular choice of factor signs. For 56 SPD matrices, the independent reference is the positive-diagonal dyadic lower factor used to form A=L*L**T. Both Cholesky triangle choices are compared directly, including unused-half zeroing.

Symmetric eigenproblems use A=shift*I+rho*u*u**T. Its spectrum has n-1 copies of shift and one value shift+rho*(u**T*u). Upper/lower triangle selections, eigenpair residuals and orthonormality are checked for 96 eigensystems. No arbitrary basis is prescribed for the repeated eigenspaces.

The SVD inputs are real 4x3 matrices constructed from orthonormal factors and prescribed singular values, with ranks one through three. Forty-eight decompositions check all 144 singular values, both singular-vector equations, reconstruction and thin-factor orthogonality. Singular-vector signs and nullspace bases are not unique. The pseudoinverse reference for A=u*v**T is v*u**T/((u**T*u)*(v**T*v)); 80 rectangular cases check 1,120 entries and all four Moore-Penrose identities with explicit rtol=1e-10.

## Norms and matrix exponentials

Independent scalar loops compute maximum absolute column/row sums and the square root of the sum of squares. These supply 525 1/infinity/Frobenius norm references, including 35 zero matrices. This does not test the spectral 2-norm or higher-rank reduction APIs.

For a strictly upper-triangular 3x3 N, N**3=0, so exp(shift*I+N) equals exp(shift)*(I+N+N**2/2). A second family is the 2x2 plane-rotation generator, whose exponential has analytic sine/cosine entries. Default and order-12 Pade calls supply 858 entry references across 132 calls. These bounded families do not certify accuracy for general stiff or badly scaled matrices.

## Quadrature references

Simpson integration checks analytic cubic antiderivatives on uniform odd grids and quadratic antiderivatives on nonuniform odd grids: 432 references over lengths 3..33. No second numerical quadrature routine supplies the expected integral. Even-grid policies, adaptivity and arbitrary-integrand errors remain unverified.

Gauss-Legendre and Lobatto node/weight routines each generate 33 rules, orders 2..12, on [-1,1], [0,1] and [-0.5,1.5]. With z=(2*x-a-b)/(b-a), the exact integral of z**p is zero for odd p and (b-a)/(p+1) for even p. Gauss rules check 462 moments through degree 2*n-1; Lobatto rules check 396 through degree 2*n-3 and require interval endpoints. Both check positive weights, ordered nodes and symmetry. Moment tolerance is 5e-12 times interval width; high-order or reversed-interval behavior is not claimed.

## Classification and provenance

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies matrix norm class D1b2; QR, real SPD factorization, symmetric eigenproblems, SVD and generalized inverses use D5, D2b1b, D4a1, D6 and D9c. Simpson is nonautomatic sampled-grid quadrature H2a1b2; node/weight generation uses H2c. Matrix exponentials retain broad linear algebra D: a matrix-polynomial classification would not describe the general exponential procedure. Verification belongs only to these recorded stdlib APIs and configurations; no other package is promoted by these results.

### stdlib-qr-reference (D5)

Independent API consumer; pinned sources and author tests reviewed. 64 real 5x3 inputs factored with full and reduced storage: 128 decompositions. Reconstruction, orthonormal columns, triangular R, finite factors and input preservation checked, scaled absolute tolerance 5e-12. Factor signs are nonunique and not compared. Pivoting, complex values, workspace APIs, other shapes and extreme conditioning unverified.

### stdlib-cholesky-reference (D2b1b)

Independent API consumer; pinned sources and author tests reviewed. 56 SPD matrices constructed from known dyadic lower-triangular factors with positive diagonal, orders 2..8. Both lower/upper factors, unused-half zeroing, reconstruction and input preservation checked: 112 factorizations. Factor tolerance 2e-12 and scaled residual tolerance 2e-12. Nonpositive-definite errors, complex values, overwriting and all conditioning unverified.

### stdlib-eigh-reference (D4a1)

Independent API consumer; pinned sources and author tests reviewed. 48 real symmetric shifted rank-one matrices, orders 3..8, each using upper/lower triangle selection. 528 analytic eigenvalues, eigenpair residuals, orthonormal vectors and input preservation; scaled absolute tolerance 3e-12. Repeated eigenspaces are checked by residuals rather than a chosen basis. Generalized/complex problems, inconsistent triangles and ill-conditioning unverified.

### stdlib-svd-reference (D6)

Independent API consumer; pinned sources and author tests reviewed. 48 real 4x3 matrices constructed with orthonormal factors and prescribed ranks 1..3. All 144 singular values, left/right singular equations, reconstruction, thin-factor orthogonality and input preservation checked; scaled absolute tolerance 5e-12. Vector signs/nullspace bases are nonunique. Complex/wide/full-storage problems, near-threshold rank decisions and general conditioning unverified.

### stdlib-pinv-reference (D9c)

Independent API consumer; pinned sources and author tests reviewed. 80 rank-one rectangular outer products with 2..6 rows and 2..5 columns. 1,120 closed-form inverse entries plus all four Moore-Penrose identities, finite output and input preservation. Explicit rtol=1e-10; absolute/scaled identity tolerance 2e-11. Zero matrices, arbitrary ranks, cutoff sensitivity, complex values and all error paths unverified.

### stdlib-matrix-norms-reference (D1b2)

Independent API consumer; pinned sources and author tests reviewed. 175 real matrices of shapes [1..5,1..7], including 35 zero matrices. 525 1/infinity/Frobenius norms against independent scalar row/column sums and sum-of-squares; scaled absolute tolerance 2e-12. Spectral 2-norm, complex/higher-rank inputs, overflow/underflow scaling and invalid orders unverified.

### stdlib-expm-reference (D)

Independent API consumer; pinned sources and author tests reviewed. 132 real matrix-exponential calls using default Pade order and order 12: shifted nilpotent 3x3 matrices with a finite polynomial closed form and 2x2 plane rotations with analytic sine/cosine form. 858 entry references, scaled absolute tolerance 2e-11. Broad D classification avoids inventing a matrix-function leaf. General stiff matrices, scaling extremes, complex values and invalid inputs unverified.

### stdlib-simpson-reference (H2a1b2)

Independent API consumer; pinned sources and author tests reviewed. 432 analytic integral references on odd grids of lengths 3..33: uniform cubics through explicit-grid/spacing APIs and nonuniform quadratics. Scaled absolute tolerance 2e-12. No numerical quadrature routine supplies the oracle. Even-grid policy, nonlinear error estimates, adaptivity, malformed grids and other kinds unverified.

### stdlib-gauss-reference (H2c)

Independent API consumer; pinned sources and author tests reviewed. 33 Gauss-Legendre node/weight rules, orders 2..12 on three intervals. 462 centered monomial moments through degree 2*n-1 against exact integrals; positive weights, interior ordered nodes and symmetry checked. Interval-scaled absolute tolerance 5e-12. Higher orders, reversed intervals and general integrand accuracy unverified.

### stdlib-lobatto-reference (H2c)

Independent API consumer; pinned sources and author tests reviewed. 33 Gauss-Legendre-Lobatto rules, orders 2..12 on three intervals. 396 centered monomial moments through degree 2*n-3 against exact integrals, endpoints, positive weights, node ordering and symmetry. Interval-scaled absolute tolerance 5e-12. Higher orders, reversed intervals and general integrand accuracy unverified.

## Provenance and actual output

Pinned public APIs, implementations and author tests were reviewed. These are independent MIT consumers; upstream implementation/test bodies were not copied and upstream license terms remain separate. Input preservation and finite outputs are checked where specified. Loading an example does not submit a job.

### stdlib-qr-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-qr-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-qr-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2216) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_qr.f90)

```text
64 real 5x3 matrices; 128 full/reduced QR decompositions, reconstruction, orthogonality and triangularity
PASS stdlib-qr-reference
```

### stdlib-cholesky-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-cholesky-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-cholesky-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L67) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_cholesky.f90)

```text
56 SPD matrices, orders 2..8; 112 Cholesky factors against constructed positive-diagonal factors
PASS stdlib-cholesky-reference
```

### stdlib-eigh-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-eigh-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-eigh-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3725) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_eigenvalues.f90)

```text
96 symmetric eigensystems, orders 3..8; analytic eigenvalues with repeated roots: 528
PASS stdlib-eigh-reference
```

### stdlib-svd-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-svd-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-svd-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3922) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_svd.f90)

```text
48 real 4x3 matrices, ranks 1..3; 144 known singular values, paired residuals and orthogonality
PASS stdlib-svd-reference
```

### stdlib-pinv-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-pinv-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-pinv-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3013) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_pseudoinverse.f90)

```text
80 rank-one rectangular matrices; closed-form pseudoinverse entries and four identities: 1120
PASS stdlib-pinv-reference
```

### stdlib-matrix-norms-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-matrix-norms-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-matrix-norms-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L6082) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_mnorm.f90)

```text
175 real matrices, including zeros; scalar-loop 1/infinity/Frobenius norm references: 525
PASS stdlib-matrix-norms-reference
```

### stdlib-expm-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-expm-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-expm-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L6437) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_expm.f90)

```text
132 exponential calls; shifted nilpotent and plane-rotation closed-form entries: 858
PASS stdlib-expm-reference
```

### stdlib-simpson-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-simpson-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-simpson-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L62) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_simps.f90)

```text
Odd grids, lengths 3..33; uniform cubics and nonuniform quadratics versus antiderivatives: 432
PASS stdlib-simpson-reference
```

### stdlib-gauss-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-gauss-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-gauss-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L113) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_gauss.f90)

```text
33 Gauss-Legendre rules, orders 2..12; centered monomial moments through degree 2*n-1: 462
PASS stdlib-gauss-reference
```

### stdlib-lobatto-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-lobatto-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-lobatto-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L124) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_gauss.f90)

```text
33 Lobatto rules, orders 2..12; endpoints and centered monomial moments through degree 2*n-3: 396
PASS stdlib-lobatto-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-qr-reference stdlib-cholesky-reference stdlib-eigh-reference stdlib-svd-reference stdlib-pinv-reference stdlib-matrix-norms-reference stdlib-expm-reference stdlib-simpson-reference stdlib-gauss-reference stdlib-lobatto-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
