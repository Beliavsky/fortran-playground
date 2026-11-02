# Ten checked root-solver and structured-matrix drivers

Ten independent REAL64 consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox, reusing existing libraries and compiling only main.f90 and playground-main. The [verification report](gams-roots-structured-ten-validation.json) retains normalized UTF-8/LF source hashes, pins, timings and full output. GAMS coverage remains unfinished.

## Root solvers (F1b)

Separate drivers exercise bisection, Ridders, Brent-Q, ITP and Chandrupatla through their direct solver objects. Each solves 85 manufactured problems: 17 exact dyadic roots r in [-2,2] in each of five families with z=x-r: z*(1+z*z), exp(z)-1, sin(z), log(1+z), and z/(2+z*z). Brackets are [r-0.75,r+1.25], safely inside the logarithm domain. The function shapes and slopes differ; all cases have simple smooth roots. These bounded examples do not establish performance or difficult-root robustness.

Each run checks status, bracket containment, the exact root, reported residual and independently reevaluated residual. Bisection fallback is explicitly disabled and must remain unused. Requested solver tolerances are 1e-13 for function values and 1e-12 for absolute/relative root errors; acceptance uses 2e-9*max(1,abs(reference)). Module callbacks avoid nested callback wrappers.

## Structured matrices

**Strang eigensystems (D4a1):** 17 dimensions n=2..18, manually assembled tridiagonal matrices with diagonal 2 and off-diagonals -1. Eigenvalues are compared with 4*sin(pi*k/(2*(n+1)))**2. Every returned vector is checked against the manual matrix and all columns must be orthonormal. The eigenvalues-only API is checked separately.

**Rectangular Poisson eigensystems (D4a1):** twelve grids nx=2..5, ny=2..4 on side lengths 2 and 3. A manual finite-difference stencil represents the negative-spectrum Laplacian with homogeneous Dirichlet boundaries. Sorted tensor-sine eigenvalues, every vector residual and orthogonality are checked. Eigenvalues-only results are also compared. No other boundary conditions are verified.

**Circulant eigenpairs (D4a2):** fifteen nonsymmetric real matrices n=3..17. The generating vector is the first column, A(i,j)=c(modulo(i-j,n)+1). Direct complex DFT sums supply independent eigenvalues; manually assembled matrices supply right-vector residuals and unitary orthogonality checks. Left eigenvectors are not verified. Caller-owned outputs are explicitly allocated as required by the pinned public interface.

**Circulant singular values (D6):** magnitudes of directly summed DFT eigenvalues, sorted by a local insertion sort, independently check svdvals. This does not verify full SVD vectors or rank-deficient inputs.

**Circulant inverses (D2a1):** both A*inverse and inverse*A must equal identity for fifteen manually assembled diagonally dominant matrices n=3..17. Singular or ill-conditioned matrices are excluded. All matrix checks require finite results and tolerance 2e-9*max(1,abs(reference)).

## Retained unsuccessful probes and provenance

The initial root_scalar convenience-wrapper probes built successfully but crashed with SIGSEGV before numerical output. Their exact sources, pins, hashes and full results are [retained](gams-candidates/roots-structured-api/README.md). The implementation creates a nested internal callback; a sandbox callback/trampoline issue is possible but not established. Successful direct-object drivers do not verify that convenience wrapper. The first circulant eig probe omitted required output allocation and stopped with an array-bound mismatch; this consumer error is preserved with the correction explained. The direct TOMS 748 probe found the exact first root (family 1, r=-2) but returned nonzero status 11021 and signalled IEEE_OVERFLOW_FLAG; a second diagnostic probe confirms this. Both are retained. The cause is undiagnosed; that path has no checked driver. Brent-Q passed the same 85 cases as a separate replacement. No assertion was relaxed and no upstream numerical source was patched.

Pinned implementations and linked author tests were reviewed. These MIT consumers copy no upstream implementation or test bodies. Classifications follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). Loading an example does not submit a job. See the [coverage report](gams-coverage.md) for remaining work.

## Driver details

### roots-fortran-bisection-bracketed-reference (F1b)

Independent API consumer. 85 manufactured roots across shifted cubic, exponential, sine, logarithmic and rational families; exact root, returned residual, independently reevaluated residual, bracket and status checked. Bisection fallback explicitly disabled. Smooth simple roots only; not a convergence or speed benchmark. Uses direct object API and a module callback; root_scalar convenience wrapper crashed in the hosted sandbox and is not verified.

### roots-fortran-ridders-bracketed-reference (F1b)

Independent API consumer. 85 manufactured roots across shifted cubic, exponential, sine, logarithmic and rational families; exact root, returned residual, independently reevaluated residual, bracket and status checked. Bisection fallback explicitly disabled. Smooth simple roots only; not a convergence or speed benchmark. Uses direct object API and a module callback; root_scalar convenience wrapper crashed in the hosted sandbox and is not verified.

### roots-fortran-brentq-bracketed-reference (F1b)

Independent API consumer. 85 manufactured roots across shifted cubic, exponential, sine, logarithmic and rational families; exact root, returned residual, independently reevaluated residual, bracket and status checked. Bisection fallback explicitly disabled. Smooth simple roots only; not a convergence or speed benchmark. Uses the direct brentq object API and a module callback; no numerical source patched.

### roots-fortran-itp-bracketed-reference (F1b)

Independent API consumer. 85 manufactured roots across shifted cubic, exponential, sine, logarithmic and rational families; exact root, returned residual, independently reevaluated residual, bracket and status checked. Bisection fallback explicitly disabled. Smooth simple roots only; not a convergence or speed benchmark. Uses direct object API and a module callback; root_scalar convenience wrapper crashed in the hosted sandbox and is not verified.

### roots-fortran-chandrupatla-bracketed-reference (F1b)

Independent API consumer. 85 manufactured roots across shifted cubic, exponential, sine, logarithmic and rational families; exact root, returned residual, independently reevaluated residual, bracket and status checked. Bisection fallback explicitly disabled. Smooth simple roots only; not a convergence or speed benchmark. Uses direct object API and a module callback; root_scalar convenience wrapper crashed in the hosted sandbox and is not verified.

### specialmatrices-strang-eigenpairs-reference (D4a1)

Independent API consumer. Strang tridiagonal eigensystems for n=2..18; independent dense stencil, sine eigenvalues, eigenvector residuals and orthogonality. Simple real symmetric spectra only.

### specialmatrices-poisson-eigenpairs-reference (D4a1)

Independent API consumer. Twelve rectangular Poisson eigensystems (nx=2..5, ny=2..4), unequal side lengths 2 and 3; manually assembled negative Laplacian stencil, sorted analytic tensor-sine spectra, residuals and orthogonality. Homogeneous Dirichlet boundaries only.

### specialmatrices-circulant-eigenpairs-reference (D4a2)

Independent API consumer. Fifteen nonsymmetric real circulants n=3..17; manual first-column dense matrices, direct O(n^2) complex DFT eigenvalues, right eigenvector residuals and unitary orthogonality. Does not verify left eigenvectors.

### specialmatrices-circulant-singular-values-reference (D6)

Independent API consumer. Fifteen circulants n=3..17; singular values compared with magnitudes of an independently summed complex DFT, sorted by a local insertion sort. Full SVD vectors, rank-deficient matrices and tiny singular values excluded.

### specialmatrices-circulant-inverses-reference (D2a1)

Independent API consumer. Fifteen diagonally dominant nonsymmetric circulants n=3..17; both left and right inverse products checked against identity using a manually assembled first-column matrix. Singular and ill-conditioned cases excluded.

## Provenance and actual output

### roots-fortran-bisection-bracketed-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=roots-fortran&example=gams-roots-fortran-bisection-bracketed-reference) / [Driver source](../fpm_catalog/gams-drivers/roots-fortran-bisection-bracketed-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/src/root_module.F90#L335) / [Author test](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/test/root_tests.f90)

```text
Manufactured roots, five nonlinear families: 85
PASS roots-fortran-bisection-bracketed-reference
```

### roots-fortran-ridders-bracketed-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=roots-fortran&example=gams-roots-fortran-ridders-bracketed-reference) / [Driver source](../fpm_catalog/gams-drivers/roots-fortran-ridders-bracketed-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/src/root_module.F90#L335) / [Author test](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/test/root_tests.f90)

```text
Manufactured roots, five nonlinear families: 85
PASS roots-fortran-ridders-bracketed-reference
```

### roots-fortran-brentq-bracketed-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=roots-fortran&example=gams-roots-fortran-brentq-bracketed-reference) / [Driver source](../fpm_catalog/gams-drivers/roots-fortran-brentq-bracketed-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/src/root_module.F90#L335) / [Author test](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/test/root_tests.f90)

```text
Manufactured roots, five nonlinear families: 85
PASS roots-fortran-brentq-bracketed-reference
```

### roots-fortran-itp-bracketed-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=roots-fortran&example=gams-roots-fortran-itp-bracketed-reference) / [Driver source](../fpm_catalog/gams-drivers/roots-fortran-itp-bracketed-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/src/root_module.F90#L335) / [Author test](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/test/root_tests.f90)

```text
Manufactured roots, five nonlinear families: 85
PASS roots-fortran-itp-bracketed-reference
```

### roots-fortran-chandrupatla-bracketed-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=roots-fortran&example=gams-roots-fortran-chandrupatla-bracketed-reference) / [Driver source](../fpm_catalog/gams-drivers/roots-fortran-chandrupatla-bracketed-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/src/root_module.F90#L335) / [Author test](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/test/root_tests.f90)

```text
Manufactured roots, five nonlinear families: 85
PASS roots-fortran-chandrupatla-bracketed-reference
```

### specialmatrices-strang-eigenpairs-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-strang-eigenpairs-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-strang-eigenpairs-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Strang/eigh.f90#L6) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_strang.f90)

```text
17 Strang spectra: analytic eigenvalues, residuals and orthogonality checked.
PASS specialmatrices-strang-eigenpairs-reference
```

### specialmatrices-poisson-eigenpairs-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-poisson-eigenpairs-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-poisson-eigenpairs-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Poisson2D/eigh.f90#L8) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_poisson2D.f90)

```text
12 rectangular Poisson spectra: stencil residuals and tensor-sine values checked.
PASS specialmatrices-poisson-eigenpairs-reference
```

### specialmatrices-circulant-eigenpairs-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-circulant-eigenpairs-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-circulant-eigenpairs-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Circulant/eig.f90#L6) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_circulant.f90)

```text
15 nonsymmetric real circulants, dimensions 3..17, independently checked.
PASS specialmatrices-circulant-eigenpairs-reference
```

### specialmatrices-circulant-singular-values-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-circulant-singular-values-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-circulant-singular-values-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Circulant/svd.f90#L7) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_circulant.f90)

```text
15 nonsymmetric real circulants, dimensions 3..17, independently checked.
PASS specialmatrices-circulant-singular-values-reference
```

### specialmatrices-circulant-inverses-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-circulant-inverses-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-circulant-inverses-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Circulant/inv.f90#L5) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_circulant.f90)

```text
15 nonsymmetric real circulants, dimensions 3..17, independently checked.
PASS specialmatrices-circulant-inverses-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers roots-fortran-bisection-bracketed-reference roots-fortran-ridders-bracketed-reference roots-fortran-brentq-bracketed-reference roots-fortran-itp-bracketed-reference roots-fortran-chandrupatla-bracketed-reference specialmatrices-strang-eigenpairs-reference specialmatrices-poisson-eigenpairs-reference specialmatrices-circulant-eigenpairs-reference specialmatrices-circulant-singular-values-reference specialmatrices-circulant-inverses-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
