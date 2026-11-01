# Checked GAMS linear-algebra drivers

These real64 consumer programs compare fortran-lapack and stdlib on the same small dense systems and unconstrained least-squares problems, with additional fortran-lapack matrix-decomposition examples, exact scalar products, BLAS products, sparse products, storage conversion and known pseudoinverses. Procedure mappings describe the reviewed real configurations; other overloads require their own evidence.

| Class | Configuration | Procedures |
| --- | --- | --- |
| [D1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D1) | Real scalar products, direct and blocked methods | fordot `dot_product` |
| [D2a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2a1) | Real nonsymmetric general linear systems | `linear_algebra:solve`; `stdlib_linalg:solve` |
| [D2a4](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2a4) | Real nonsymmetric sparse linear systems | Y12M `y12mb, y12mc, y12md` |
| [D9a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D9a1) | Unconstrained linear least squares, L2 solution | `linear_algebra:lstsq`; `stdlib_linalg:lstsq` |
| [D4a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D4a1) | Ordinary real symmetric eigenproblems | fortran-lapack `la_lapack:syev`; ARPACK `DSAUPD/DSEUPD`; linalg_fortran `linalg%eigh` |
| [D5](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D5) | Orthogonalization, demonstrated by reduced QR | fortran-lapack `linear_algebra:qr` |
| [D6](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D6) | Singular value decomposition | fortran-lapack `la_lapack:gesvd`, real64 overload |
| [D1b6](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D1b6) | Rectangular real matrix products | blas-interface `blas_gemm` |
| [D1b4](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D1b4) | Rectangular sparse matrix-vector products | fsparse `matvec`, COO/CSR real64 overloads |
| [D9c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D9c) | Generalized inverse | forinv `inv`, SVD method with explicit cutoff |

## Exact scalar products

The fordot driver checks 231 default and m1..m4 products over five lengths and three deterministic input patterns. Exact int64 numerators divided by 32 supply independent dyadic references. Valid distinct block counts 1, 3 and n cover unequal blocks and single-element blocks. See the [reference details and output](gams-products-status.md).

## Shared dense-system checks

Both solve drivers use the 3-by-3 systems from stdlib `example_solve1` and fortran-lapack `test_dsolve`, with reference solutions `[5,3,-2]` and `[-2,-2,3]`. They preserve the original matrix and right-hand side, check solver status and finite solutions, and require maximum solution error at most `1e-10`. The independently computed scaled residual is `||A*x-b||_inf / (||A||_inf*||x||_inf + ||b||_inf)` and must be at most `1e-12`. Matrix infinity norm means the maximum absolute row sum.

## Nonsymmetric sparse solves

The Y12M driver uses two nonsymmetric 10-by-10 matrices, including a cyclic row permutation, and reuses one LU factorization for four right-hand sides per matrix. Independent manufactured solutions and scalar residuals determine acceptance. See the [fixtures, tolerances and output](gams-sparse-integral.md).

## Shared least-squares checks

Use `t=[-2,-1,0,1,2]`, noise `e=[1,-2,2,-2,1]`, and observations `b=1+2*t+e`. The noise is orthogonal to the constant and linear columns. The full-rank design `[1,t]` therefore has reference coefficients `[1,2]`. A second design `[1,t,t]` has duplicate columns; the SVD-based solvers should return the minimum-norm coefficients `[1,1,1]`. Both have rank 2 and residual sum of squares 14.

The drivers check solver status, finite coefficients, numerical rank and coefficient error at most `1e-10`. They independently require `max(abs(transpose(A)*(A*x-b))) <= 1e-10` and residual sum of squares within `1e-10` of 14. A nonzero residual is expected for these inconsistent systems; a small normal-equation residual alone would not identify the minimum-norm solution in the rank-deficient case. The known coefficient check does.

## Symmetric eigenvalue checks

The real symmetric matrix has a 2-by-2 block `[[2,1],[1,2]]` and a third diagonal entry 4, giving eigenvalues `[1,3,4]`. A second case changes that entry to 3, giving a repeated eigenvalue `[1,3,3]`. The driver queries workspace and calls the lower-level `syev` interface, checking `info=0`, finite factors and eigenvalue error at most `1e-12`. It independently checks `A*V=V*diag(lambda)`, reconstruction of A and orthonormality of V, each within `1e-12`. Matrix residuals use Frobenius norm divided by `max(1,||A||_F)`; orthogonality uses the unscaled Frobenius norm.

## Reduced QR and its least-squares application

For `t=[-1,0,1,2]`, the full-rank design is `[1,t,t**2]`. The reduced QR driver checks reconstruction, column orthonormality and the lower-triangular entries of R within `1e-12`. It then solves the triangular system for observations `b=A*[1,-2,0.5]+[-0.1,0.3,-0.3,0.1]`. The added noise is orthogonal to all design columns, so the coefficients are known independently and the residual sum of squares is 0.2. Coefficient error, normal-equation residual and residual-sum error must each be within `1e-12`.

A second QR case replaces the third column with twice the second. Factorization identities must still pass, and the final diagonal entry of R must be near zero relative to matrix scale. The driver skips the triangular solve for this known dependent-column case; it does not treat unpivoted QR as a general rank-revealing method.

## Reduced SVD checks

The 4-by-3 matrix has an upper 2-by-2 block filled with 1.5, entry `(3,3)=2` and other entries zero. Its singular values are `[3,2,0]`. A second case sets row 4 to `[1,-1,0]`, giving `[3,2,sqrt(2)]`. The driver queries workspace and calls lower-level `gesvd` for reduced factors. It checks successful status, finite factors, nonnegative descending singular values and agreement with the known spectrum within `1e-12`. Reconstruction and left/right orthogonality must each be within `1e-12`, using the same residual scaling as the eigenvalue driver. The numerical rank threshold is `4*epsilon*max(singular_values)`, giving ranks 2 and 3 in these two cases.

These decomposition checks allow valid factor sign choices and arbitrary bases in repeated or null subspaces. They compare reconstruction and invariant properties, rather than requiring a particular vector listing.

## BLAS matrix multiplication

The D1b6 driver computes a 3-by-2 times 2-by-4 product with `A(i,k)=2*i-3*k`, `B(k,j)=3*k-j` and `C0(i,j)=(i-j)/2`. Twelve calls cover all NN/NT/TN/TT storage/transpose combinations and `(alpha,beta)=[(1,0),(-2,0.5),(0,-1)]`. Independent scalar triple loops form `alpha*A*B+beta*C0`; no MATMUL or separate BLAS call supplies the reference. The zero-alpha case checks scaling of an existing output independently of the product. Every result must be finite with scaled maximum-entry error at most `1e-12`. The package is an interface to the installed BLAS implementation. Complex overloads, padded leading dimensions and other BLAS routines are outside the driver.

## Sparse accumulated matrix-vector products

The D1b4 driver uses the nonsymmetric 4-by-3 matrix with rows `[2,0,4]`, `[0,3,0]`, `[0,0,0]`, `[-1,0,5]`. Inputs `[1,-2,3]`, `[0,1,-1]` and zero give products `[14,-6,0,14]`, `[-4,3,0,-5]` and zero. Scalar row/column loops independently compute each reference. COO and CSR forms are checked with both zero and nonzero initial output `[0.5,-1,7,2]`, and every call is repeated to check `y := y+A*x` accumulation rather than replacement. All 24 calls must return finite vectors with absolute maximum-entry error at most `1e-12`.

The empty third row must retain its initial output value. The test exercises the conversion helpers to prepare storage, but its verified problem class is D1b4; the separate D1b9 storage-conversion mapping is not marked verified by this driver. Symmetric-storage shortcuts, complex overloads and other sparse formats are outside the example.

## Sparse storage conversion

A separate D1b9 driver checks `dense2coo`, `coo2dense`, `coo2csr` and `csr2coo` with five matrices: a 5-by-4 matrix with entries `(2,1)=-2`, `(2,4)=0.5`, `(4,2)=3`, `(4,4)=-4`; its transpose; an all-zero 3-by-2 matrix; a fully populated 2-by-3 matrix `A(i,j)=(2*i+3*j)/2`; and the 1-by-1 matrix `[-7]`. The sparse fixtures include leading, interior and trailing empty rows and empty columns. All entries are moderate exact dyadic values.

Independent scalar row/column loops check every COO coordinate/value against the original matrix, not just a round trip. Independently counted row entries determine every expected CSR row pointer. Dimensions, array sizes, nonzero counts, one-based indexing, CSR columns and values, and finite stored data must agree exactly. A separate scalar CSR reconstruction, CSR-to-COO conversion and both COO-to-dense restorations must recover the original matrix exactly. The caller zero-initializes dense outputs because `coo2dense` writes stored entries only. Fresh storage is used for each fixture. Duplicate coordinates, preallocated-storage reuse, complex/symmetric formats and threshold/subnormal behavior are outside this checked configuration. In particular, the pinned `dense2coo` source counts `abs(value)>tiny` but skips `abs(value)<tiny` while copying; equality at the threshold needs a separate bounds-checked investigation. No such values are included or certified here.

## Known pseudoinverses and minimum-norm solutions

The D9c driver uses `forinv:inv(method="gesvd",tol=1e-10)` for five cases. For the rank-one matrix `u*v^T`, `u=[1,2,3]`, `v=[1,2]`, the explicit pseudoinverse is `v*u^T/70`. Its application to `b=u` must produce the minimum-norm solution `[1/5,2/5]`. A full-rank tall matrix with orthogonal columns `[1,2,2]` and `[2,-1,0]` has pseudoinverse rows equal to those columns divided by 9 and 5 respectively. The wide transpose must have the transposed pseudoinverse. The remaining cases are `diag(2,0,4)`, with inverse `diag(1/2,0,1/4)`, and a zero 3-by-2 matrix, with a zero 2-by-3 pseudoinverse.

Each case checks the explicit reference and all four Moore-Penrose conditions: `A*Aplus*A=A`, `Aplus*A*Aplus=Aplus`, symmetry of `A*Aplus`, and symmetry of `Aplus*A`. Maximum-entry errors are divided by `max(1,max(abs(reference)))` for the corresponding matrix and bounded by `1e-11`; all results/errors must be finite. The minimum-norm coefficient error is bounded by `1e-11`. Original matrices are preserved because the pinned ForSVD dependency can overwrite the SVD input despite its declared input intent. The cutoff is absolute in this API. This does not test default cutoff behavior, alternative methods, ill-conditioning, near-threshold numerical ranks or general rank selection.

## Shared Dirichlet spectral problem

ARPACK and linalg_fortran use the same 20-by-20 real symmetric tridiagonal matrix with diagonal 2 and off-diagonals -1. Its exact eigenvalues are `lambda_j=4*sin(j*pi/(2*(n+1)))^2` and normalized eigenvectors `v_i=sqrt(2/(n+1))*sin(i*j*pi/(n+1))`. The reviewed procedure mappings are refined from broad D4 to D4a1 for these real symmetric ordinary-problem APIs; no generalized or nonsymmetric eigenproblem claim is made.

The ARPACK driver requests the three smallest and three largest eigenpairs in separate standard-mode runs (`SM`/`LM`, `BMAT=I`, `IPARAM(7)=1`). It supplies a reproducible nonzero initial residual, caps Arnoldi iterations at 1000 and operator calls at 10000, and requires successful convergence and extraction with all three requested pairs converged. Eigenvalue errors and Euclidean eigen-equation residuals must be at most `1e-9`; orthonormality error at most `1e-10`. Every vector must match its analytic sine direction up to sign, with `abs(abs(dot_product(computed,exact))-1)<=1e-8`.

The dense linalg_fortran driver checks all 20 eigenpairs, with eigenvalue, equation-residual, orthonormality and maximum-entry reconstruction errors at most `1e-11`. It uses the same sign-independent sine-vector check and prints the six pairs corresponding to the ARPACK selections. Both drivers require finite eigenvalues/vectors. The dense API has no returned status in this invocation; answer checks determine acceptance. The shared mathematical problem supports comparisons of selected results, not a general speed ranking. Shift-invert, generalized, nonsymmetric and arbitrary-spectrum problems are not verified.

## Observed high-level link limit

On 2026-10-30, the high-level `linear_algebra:eigh` and `linear_algebra:svd` versions compiled their mains but failed to link under the hosted 16 MiB per-file limit with GNU Fortran 16.2.0/FPM 0.12.0 and the existing precompiled fortran-lapack image at revision `e5e45fdd5a38bfab06d1f703f12b787937aa33bb`. The linker reported:

```text
collect2: fatal error: ld terminated with signal 25 [File size limit exceeded]
```

Saved reproducers: [high-level eigh](gams-candidates/fortran-lapack-eigh.f90) and [high-level svd](gams-candidates/fortran-lapack-svd.f90). These are failed hosted probes for that image, with no successful hosted-run designation. They may be useful for local reproduction or discussing executable size with the package author. The menu examples use the lower-level `syev`/`gesvd` APIs, which passed under the same limits and with the same precompiled library. Sandbox limits were unchanged.

The separate [PROPACK and FMM2D review](gams-propack-fmm.md) covers leading singular triplets with prescribed spectra and real Laplace kernel-matrix applications. The latter is not a checked complete PDE solver.

The [GMRES and inverse review](gams-gmres-inverse.md) covers normal/transpose LightKrylov solves with known solutions and one-process NTPoly SPD inverses with analytic references and two-sided identity residuals.

## Sources and playground links

| Driver | Class | Pinned procedure and author example |
| --- | --- | --- |
| [Load fortran-lapack-dense-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lapack&example=gams-fortran-lapack-dense-solve) · [Source](../fpm_catalog/gams-drivers/fortran-lapack-dense-solve.f90) | D2a1 | [Procedure](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/src/la_solve.f90#L139) · [Author example](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/test/test_la_solve.f90) |
| [Load fortran-lapack-least-squares](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lapack&example=gams-fortran-lapack-least-squares) · [Source](../fpm_catalog/gams-drivers/fortran-lapack-least-squares.f90) | D9a1 | [Procedure](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/src/la_least_squares.f90#L168) · [Author example](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/test/test_linalg_lstsq.f90) |
| [Load stdlib-dense-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-dense-solve) · [Source](../fpm_catalog/gams-drivers/stdlib-dense-solve.f90) | D2a1 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L734) · [Author example](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_solve1.f90) |
| [Load stdlib-least-squares](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-least-squares) · [Source](../fpm_catalog/gams-drivers/stdlib-least-squares.f90) | D9a1 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1393) · [Author example](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_lstsq1.f90) |
| [Load fortran-lapack-symmetric-eigen](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lapack&example=gams-fortran-lapack-symmetric-eigen) · [Source](../fpm_catalog/gams-drivers/fortran-lapack-symmetric-eigen.f90) | D4a1 | [Procedure](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/src/la_lapack_eigv_sym.f90#L6095) · Original lower-level API driver |
| [Load fortran-lapack-qr-decomposition](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lapack&example=gams-fortran-lapack-qr-decomposition) · [Source](../fpm_catalog/gams-drivers/fortran-lapack-qr-decomposition.f90) | D5 | [Procedure](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/src/la_qr.f90#L56) · [Author example](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/test/test_la_qr.f90) |
| [Load fortran-lapack-svd-decomposition](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lapack&example=gams-fortran-lapack-svd-decomposition) · [Source](../fpm_catalog/gams-drivers/fortran-lapack-svd-decomposition.f90) | D6 | [Procedure](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/src/la_lapack_eigv_svd_drivers.f90#L2310) · Original lower-level API driver |
| [Load minres-indefinite-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=minres&example=gams-minres-indefinite-solve) · [Source](../fpm_catalog/gams-drivers/minres-indefinite-solve.f90) | D2b4 | [Procedure](https://github.com/willdickson/minres/blob/c7bb4c7a0ddf13729d3556878ccc688a208a052a/src/minres/minres_mod.f90#L40) · [Author example](https://github.com/willdickson/minres/blob/c7bb4c7a0ddf13729d3556878ccc688a208a052a/test/minres_test.f90) |
| [Load qdldl-quasidefinite-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=qdldl-fortran&example=gams-qdldl-quasidefinite-solve) · [Source](../fpm_catalog/gams-drivers/qdldl-quasidefinite-solve.f90) | D2b4 | [Procedure](https://github.com/jacobwilliams/qdldl-fortran/blob/8ebdd7fa1075bfb89115d0955806b0996b6b29d5/src/qdldl_module.f90#L28) · [Author example](https://github.com/jacobwilliams/qdldl-fortran/blob/8ebdd7fa1075bfb89115d0955806b0996b6b29d5/example/example_kkt.f90) |
| [Load kiss-positive-definite-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=kiss&example=gams-kiss-positive-definite-solve) · [Source](../fpm_catalog/gams-drivers/kiss-positive-definite-solve.f90) | D2b1b | [Procedure](https://github.com/ivan-pi/kiss/blob/55f0f7ccb1601a0628a17928b5b6b79f61da2892/src/kiss.F90#L147) · [Author example](https://github.com/ivan-pi/kiss/blob/55f0f7ccb1601a0628a17928b5b6b79f61da2892/test/test_kiss.f90) |
| [Load slicot-lyapunov-known-matrix](https://beliavsky.github.io/fortran-playground/fpm/?package=slicot&example=gams-slicot-lyapunov-known-matrix) · [Source](../fpm_catalog/gams-drivers/slicot-lyapunov-known-matrix.f90) | D8 | [Procedure](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/src/SB03MD.f#L1) · [Author example](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/examples/TSB03MD.f) |
| [Load slicot-continuous-sylvester](https://beliavsky.github.io/fortran-playground/fpm/?package=slicot&example=gams-slicot-continuous-sylvester) · [Source](../fpm_catalog/gams-drivers/slicot-continuous-sylvester.f90) | D8 | [Procedure](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/src/SB04MD.f#L4) · [Author example](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/examples/TSB04MD.f) |
| [Load slicot-discrete-sylvester](https://beliavsky.github.io/fortran-playground/fpm/?package=slicot&example=gams-slicot-discrete-sylvester) · [Source](../fpm_catalog/gams-drivers/slicot-discrete-sylvester.f90) | D8 | [Procedure](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/src/SB04QD.f#L4) · [Author example](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/examples/TSB04QD.f) |
| [Load blas-gemm-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=blas-interface&example=gams-blas-gemm-reference) · [Source](../fpm_catalog/gams-drivers/blas-gemm-reference.f90) | D1b6 | [Procedure](https://github.com/awvwgk/blas-interface/blob/552a2e6a41443843003216fedad6419af55f8e35/src/blas/level3.f90#L35) · Original lower-level API driver |
| [Load fsparse-matvec-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fsparse&example=gams-fsparse-matvec-reference) · [Source](../fpm_catalog/gams-drivers/fsparse-matvec-reference.f90) | D1b4 | [Procedure](https://github.com/jalvesz/FSPARSE/blob/fa8233420ab0110bb688d565879164386521a8fc/src/matvec/fsparse_matvec.f90#L14) · [Author example](https://github.com/jalvesz/FSPARSE/blob/fa8233420ab0110bb688d565879164386521a8fc/test/test_matrices.f90) |
| [Load forinv-pseudoinverse-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=forinv&example=gams-forinv-pseudoinverse-reference) · [Source](../fpm_catalog/gams-drivers/forinv-pseudoinverse-reference.f90) | D9c | [Procedure](https://github.com/gha3mi/forinv/blob/80b5dbed9709c001e4309382424276a2ceb984f3/src/forinv.f90#L15) · [Author example](https://github.com/gha3mi/forinv/blob/80b5dbed9709c001e4309382424276a2ceb984f3/test/test1.f90) |
| [Load arpack-poisson-eigenpairs](https://beliavsky.github.io/fortran-playground/fpm/?package=arpack-ng&example=gams-arpack-poisson-eigenpairs) · [Source](../fpm_catalog/gams-drivers/arpack-poisson-eigenpairs.f90) | D4a1 | [Procedure](https://github.com/opencollab/arpack-ng/blob/66faef9e09bb35f5acafe02960885050acc46fa0/SRC/dsaupd.f#L1) · [Author example](https://github.com/opencollab/arpack-ng/blob/66faef9e09bb35f5acafe02960885050acc46fa0/EXAMPLES/SYM/dsdrv1.f) |
| [Load linalg-poisson-eigenpairs](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg_fortran&example=gams-linalg-poisson-eigenpairs) · [Source](../fpm_catalog/gams-drivers/linalg-poisson-eigenpairs.f90) | D4a1 | [Procedure](https://github.com/Euler-37/linalg_fortran/blob/30e7237ab54ca176e1c8dae4be2d9d44800e1f83/src/linalg_fortran.f90#L672) · Original lower-level API driver |
| [Load fsparse-storage-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fsparse&example=gams-fsparse-storage-reference) · [Source](../fpm_catalog/gams-drivers/fsparse-storage-reference.f90) | D1b9 | [Procedure](https://github.com/jalvesz/FSPARSE/blob/fa8233420ab0110bb688d565879164386521a8fc/src/conversion/fsparse_conversions.f90#L17) · [Author example](https://github.com/jalvesz/FSPARSE/blob/fa8233420ab0110bb688d565879164386521a8fc/test/test_matrices.f90) |
| [Load y12m-sparse-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=y12m&example=gams-y12m-sparse-reference) · [Source](../fpm_catalog/gams-drivers/y12m-sparse-reference.f90) | D2a4 | [Procedure](https://github.com/ivan-pi/y12m/blob/5245418ed3f87c72bff4660432212328640a6322/src/y12m.f90#L91) · [Author example](https://github.com/ivan-pi/y12m/blob/5245418ed3f87c72bff4660432212328640a6322/test/test_y12mc_errors.F90) |
| [Load fordot-exact-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fordot&example=gams-fordot-exact-reference) · [Source](../fpm_catalog/gams-drivers/fordot-exact-reference.f90) | D1 | [Procedure](https://github.com/gha3mi/fordot/blob/3966625781a9c1dffe037e3032fa4a0b6f958760/src/fordot.f90#L21) · [Author example](https://github.com/gha3mi/fordot/blob/3966625781a9c1dffe037e3032fa4a0b6f958760/test/test1.f90) |
| [Load linalg-inverse-factor-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg_fortran&example=gams-linalg-inverse-factor-reference) · [Source](../fpm_catalog/gams-drivers/linalg-inverse-factor-reference.f90) | D2 | [Procedure](https://github.com/Euler-37/linalg_fortran/blob/30e7237ab54ca176e1c8dae4be2d9d44800e1f83/src/linalg_fortran.f90#L489) · [Author example](https://github.com/Euler-37/linalg_fortran/blob/30e7237ab54ca176e1c8dae4be2d9d44800e1f83/test/check.f90) |
| [Load ntpoly-matrix-root-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=ntpoly&example=gams-ntpoly-matrix-root-reference) · [Source](../fpm_catalog/gams-drivers/ntpoly-matrix-root-reference.f90) | D | [Procedure](https://github.com/william-dawson/NTPoly/blob/7b3d22f76226af1402e9b0a5be18a496e4addc28/Source/Fortran/SquareRootSolversModule.F90#L30) · [Author example](https://github.com/william-dawson/NTPoly/blob/7b3d22f76226af1402e9b0a5be18a496e4addc28/Examples/PremadeMatrix/main.f90) |
| [Load libmbd-dimer-spectrum](https://beliavsky.github.io/fortran-playground/fpm/?package=libmbd&example=gams-libmbd-dimer-spectrum) · [Source](../fpm_catalog/gams-drivers/libmbd-dimer-spectrum.f90) | D4 | [Procedure](https://github.com/libmbd/libmbd/blob/77d7ab424d21f43dea9f57734b355ce4ea4d1a42/src/mbd.F90#L1) · [Author example](https://github.com/libmbd/libmbd/blob/77d7ab424d21f43dea9f57734b355ce4ea4d1a42/tests/mbd_api_tests.F90) |
| [Load linalg-qr-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-qr-reference) · [Source](../fpm_catalog/gams-drivers/linalg-qr-reference.f90) | D5 | [Procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_qr.f90#L20) · [Author example](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/examples/linalg_qr_example.f90) |
| [Load linalg-eigen-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-eigen-reference) · [Source](../fpm_catalog/gams-drivers/linalg-eigen-reference.f90) | D4a1 | [Procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_eigen.f90#L17) · [Author example](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/tests/test_eigen.f90) |
| [Load linalg-svd-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-svd-reference) · [Source](../fpm_catalog/gams-drivers/linalg-svd-reference.f90) | D6 | [Procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_svd.f90#L12) · [Author example](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/tests/test_svd.f90) |
| [Load linalg-least-squares-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-least-squares-reference) · [Source](../fpm_catalog/gams-drivers/linalg-least-squares-reference.f90) | D9a1 | [Procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_least_squares.f90#L14) · Original lower-level API driver |
| [Load lsqr-least-squares-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=lsqr&example=gams-lsqr-least-squares-reference) · [Source](../fpm_catalog/gams-drivers/lsqr-least-squares-reference.f90) | D9a1 | [Procedure](https://github.com/jacobwilliams/LSQR/blob/4df2ce600ca26a9f7e80dc01bfd0859d538547b3/src/lsqr.f90#L32) · [Author example](https://github.com/jacobwilliams/LSQR/blob/4df2ce600ca26a9f7e80dc01bfd0859d538547b3/test/lsqrtest_ez.f90) |
| [Load lsmr-least-squares-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=lsmr&example=gams-lsmr-least-squares-reference) · [Source](../fpm_catalog/gams-drivers/lsmr-least-squares-reference.f90) | D9a1 | [Procedure](https://github.com/jacobwilliams/LSMR/blob/12611e2299c5188441b097437695a66c85369e76/src/lsmrModule.f90#L175) · [Author example](https://github.com/jacobwilliams/LSMR/blob/12611e2299c5188441b097437695a66c85369e76/test/lsmrTestModule.f90) |
| [Load forsvd-spectrum-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=forsvd&example=gams-forsvd-spectrum-reference) · [Source](../fpm_catalog/gams-drivers/forsvd-spectrum-reference.f90) | D6 | [Procedure](https://github.com/gha3mi/forsvd/blob/f39bba7afcb048a21947a7a640bdf9a18337f8ac/src/forsvd.f90#L57) · [Author example](https://github.com/gha3mi/forsvd/blob/f39bba7afcb048a21947a7a640bdf9a18337f8ac/test/test1.f90) |
| [Load foreig-symmetric-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=foreig&example=gams-foreig-symmetric-reference) · [Source](../fpm_catalog/gams-drivers/foreig-symmetric-reference.f90) | D4a1 | [Procedure](https://github.com/gha3mi/foreig/blob/8fcfcab03e5d7cf5eda8c51c7a1e97fe52954c39/src/foreig.f90#L11) · [Author example](https://github.com/gha3mi/foreig/blob/8fcfcab03e5d7cf5eda8c51c7a1e97fe52954c39/test/test1.f90) |
| [Load specialmatrices-diagonal-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-diagonal-reference) · [Source](../fpm_catalog/gams-drivers/specialmatrices-diagonal-reference.f90) | D2 | [Procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Diagonal/specialmatrices_diagonal.f90#L191) · Original lower-level API driver |
| [Load m-la-magic-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=m_la&example=gams-m-la-magic-reference) · [Source](../fpm_catalog/gams-drivers/m-la-magic-reference.f90) | D1 | [Procedure](https://github.com/urbanjost/M_LA/blob/db59eeab0deab7e84eadf2542ad49c1c719dfb94/src/M_LA.f90#L1561) · Original lower-level API driver |
| [Load forlab-least-squares-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-least-squares-reference) · [Source](../fpm_catalog/gams-drivers/forlab-least-squares-reference.f90) | D9a1 | [Procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L7796) · Original lower-level API driver |
| [Load fglm-transform-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fglm&example=gams-fglm-transform-reference) · [Source](../fpm_catalog/gams-drivers/fglm-transform-reference.f90) | D1 | [Procedure](https://github.com/jordan4ibanez/fglm/blob/e1b6a5404b3e7a266da33173a07166970c16dd86/src/matrix_4f.f90#L267) · Original lower-level API driver |
| [Load sparse-matvec-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=sparse_fortran&example=gams-sparse-matvec-reference) · [Source](../fpm_catalog/gams-drivers/sparse-matvec-reference.f90) | D1b4 | [Procedure](https://github.com/Euler-37/sparse_fortran/blob/600f586a1ed099a22054ed283225787de36a31c1/src/sparse_coo_fortran.f90#L193) · [Author example](https://github.com/Euler-37/sparse_fortran/blob/600f586a1ed099a22054ed283225787de36a31c1/app/main.f90) |
| [Load linalg-lu-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-lu-reference) · [Source](../fpm_catalog/gams-drivers/linalg-lu-reference.f90) | D2a1 | [Procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_lu.f90#L18) · [Author example](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/examples/linalg_lu_example.f90) |
| [Load propack-spectrum-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=propack&example=gams-propack-spectrum-reference) · [Source](../fpm_catalog/gams-drivers/propack-spectrum-reference.f90) | D6 | [Procedure](https://github.com/scipy/PROPACK/blob/36f95269ecee6ae42af0c00707b3c3cf3f869a35/double/dlansvd.F#L1) · Original lower-level API driver |
| [Load fmm2d-laplace-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fmm2d&example=gams-fmm2d-laplace-reference) · [Source](../fpm_catalog/gams-drivers/fmm2d-laplace-reference.f90) | D1 | [Procedure](https://github.com/flatironinstitute/fmm2d/blob/7e7509ecd6ebe31b9292cb00825410b478f44808/src/laplace/rfmm2dwrap.f#L1) · [Author example](https://github.com/flatironinstitute/fmm2d/blob/7e7509ecd6ebe31b9292cb00825410b478f44808/test/laplace/test_rfmm2d.f) |
| [Load lightkrylov-gmres-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=lightkrylov&example=gams-lightkrylov-gmres-reference) · [Source](../fpm_catalog/gams-drivers/lightkrylov-gmres-reference.f90) | D2 | [Procedure](https://github.com/nekStab/LightKrylov/blob/849fa1d2f29c14d0181315e76e731bff7f0b2d08/src/IterativeSolvers/IterativeSolvers.f90#L379) · [Author example](https://github.com/nekStab/LightKrylov/blob/849fa1d2f29c14d0181315e76e731bff7f0b2d08/test/Tests.f90) |
| [Load ntpoly-inverse-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=ntpoly&example=gams-ntpoly-inverse-reference) · [Source](../fpm_catalog/gams-drivers/ntpoly-inverse-reference.f90) | D2 | [Procedure](https://github.com/william-dawson/NTPoly/blob/7b3d22f76226af1402e9b0a5be18a496e4addc28/Source/Fortran/InverseSolversModule.F90#L29) · [Author example](https://github.com/william-dawson/NTPoly/blob/7b3d22f76226af1402e9b0a5be18a496e4addc28/Examples/PremadeMatrix/main.f90) |
| [Load heatflow-bicg-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=heatflow&example=gams-heatflow-bicg-reference) · [Source](../fpm_catalog/gams-drivers/heatflow-bicg-reference.f90) | D2 | [Procedure](https://github.com/ExeQuantCode/HeatFlow/blob/b0d930caad9160a15f0aeafa238c448f48f28d55/src/heatflow/mod_Sparse.f90#L273) · Original lower-level API driver |
| [Load formatmul-products-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=formatmul&example=gams-formatmul-products-reference) · [Source](../fpm_catalog/gams-drivers/formatmul-products-reference.f90) | D1 | [Procedure](https://github.com/gha3mi/formatmul/blob/4b5747d49c27f0df92288e7a61d0e479e34ac78e/src/formatmul.f90#L585) · [Author example](https://github.com/gha3mi/formatmul/blob/4b5747d49c27f0df92288e7a61d0e479e34ac78e/test/test1.f90) |
| [Load lusol-update-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=lusol&example=gams-lusol-update-reference) · [Source](../fpm_catalog/gams-drivers/lusol-update-reference.f90) | D2a4 | [Procedure](https://github.com/jacobwilliams/lusol/blob/2d95174d44ec9bf9dabbbd07652c84c11fe56d71/src/lusol.f90#L101) · [Author example](https://github.com/jacobwilliams/lusol/blob/2d95174d44ec9bf9dabbbd07652c84c11fe56d71/test/lusol_test.f90) |
| [Load scalapackfx-eigen-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=scalapackfx&example=gams-scalapackfx-eigen-reference) · [Source](../fpm_catalog/gams-drivers/scalapackfx-eigen-reference.f90) | D4a1 | [Procedure](https://github.com/dftbplus/scalapackfx/blob/570cbf45836ed05cf791bc3f404f4f10929e5017/lib/scalapackfx.fpp#L1) · [Author example](https://github.com/dftbplus/scalapackfx/blob/570cbf45836ed05cf791bc3f404f4f10929e5017/test/test_diag.f90) |
| [Load dbcsr-products-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=dbcsr&example=gams-dbcsr-products-reference) · [Source](../fpm_catalog/gams-drivers/dbcsr-products-reference.f90) | D1 | [Procedure](https://github.com/cp2k/dbcsr/blob/cd6f522ec5005da8c59d2883975a89a2da607eac/src/mm/dbcsr_multiply_api.F#L1) · [Author example](https://github.com/cp2k/dbcsr/blob/cd6f522ec5005da8c59d2883975a89a2da607eac/examples/dbcsr_example_3.F) |

The dense examples reuse both authors' problem data and retain both license notices. The least-squares examples adapt author API usage to shared deterministic data. These drivers appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All 47 passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only each main and executable were rebuilt. The verification reports record source hashes, pins and saved output: [gams-dense-spectra-validation.json](gams-dense-spectra-validation.json), [gams-diagonal-response-validation.json](gams-diagonal-response-validation.json), [gams-dispersion-validation.json](gams-dispersion-validation.json), [gams-geodesy-forlab-validation.json](gams-geodesy-forlab-validation.json), [gams-gmres-inverse-validation.json](gams-gmres-inverse-validation.json), [gams-inverse-tvd-validation.json](gams-inverse-tvd-validation.json), [gams-iterative-ls-validation.json](gams-iterative-ls-validation.json), [gams-jacobian-transforms-validation.json](gams-jacobian-transforms-validation.json), [gams-least-interpolation-validation.json](gams-least-interpolation-validation.json), [gams-linear-algebra-validation.json](gams-linear-algebra-validation.json), [gams-lu-orbits-validation.json](gams-lu-orbits-validation.json), [gams-matrix-equations-validation.json](gams-matrix-equations-validation.json), [gams-matrix-roots-box-validation.json](gams-matrix-roots-box-validation.json), [gams-neighbors-sparse-validation.json](gams-neighbors-sparse-validation.json), [gams-products-partitions-validation.json](gams-products-partitions-validation.json), [gams-products-status-validation.json](gams-products-status-validation.json), [gams-propack-fmm-validation.json](gams-propack-fmm-validation.json), [gams-qr-autodiff-validation.json](gams-qr-autodiff-validation.json), [gams-ranking-magic-validation.json](gams-ranking-magic-validation.json), [gams-sparse-advection-validation.json](gams-sparse-advection-validation.json), [gams-sparse-integral-validation.json](gams-sparse-integral-validation.json), [gams-sparse-spectra-validation.json](gams-sparse-spectra-validation.json), [gams-sparse-validation.json](gams-sparse-validation.json), [gams-spectral-wrappers-validation.json](gams-spectral-wrappers-validation.json), [gams-tangents-blocks-validation.json](gams-tangents-blocks-validation.json). These small examples establish checked usage, rather than comprehensive accuracy or performance comparisons. The packages may share underlying algorithms; this is not evidence of independent implementations. Zero printed error means agreement at working precision.

### fortran-lapack-dense-solve

```text
Dense nonsymmetric case: 1
Solution:     5.000000000000    3.000000000000   -2.000000000000
Maximum solution error:   0.0000E+00
Scaled infinity-norm residual:   0.0000E+00
Dense nonsymmetric case: 2
Solution:    -2.000000000000   -2.000000000000    3.000000000000
Maximum solution error:   0.0000E+00
Scaled infinity-norm residual:   0.0000E+00
PASS fortran-lapack-dense-solve
```

### fortran-lapack-least-squares

```text
Least-squares case (2 has duplicate columns): 1
Coefficients:     1.000000000000    2.000000000000
Numerical rank: 2
Maximum coefficient error:   2.2204E-16
Maximum absolute A-transpose residual:   0.0000E+00
Residual sum of squares (expected 14):    14.000000000000
Least-squares case (2 has duplicate columns): 2
Coefficients:     1.000000000000    1.000000000000    1.000000000000
Numerical rank: 2
Maximum coefficient error:   4.4409E-16
Maximum absolute A-transpose residual:   4.4409E-16
Residual sum of squares (expected 14):    14.000000000000
PASS fortran-lapack-least-squares
```

### stdlib-dense-solve

```text
Dense nonsymmetric case: 1
Solution:     5.000000000000    3.000000000000   -2.000000000000
Maximum solution error:   0.0000E+00
Scaled infinity-norm residual:   0.0000E+00
Dense nonsymmetric case: 2
Solution:    -2.000000000000   -2.000000000000    3.000000000000
Maximum solution error:   0.0000E+00
Scaled infinity-norm residual:   0.0000E+00
PASS stdlib-dense-solve
```

### stdlib-least-squares

```text
Least-squares case (2 has duplicate columns): 1
Coefficients:     1.000000000000    2.000000000000
Numerical rank: 2
Maximum coefficient error:   2.2204E-16
Maximum absolute A-transpose residual:   0.0000E+00
Residual sum of squares (expected 14):    14.000000000000
Least-squares case (2 has duplicate columns): 2
Coefficients:     1.000000000000    1.000000000000    1.000000000000
Numerical rank: 2
Maximum coefficient error:   4.4409E-16
Maximum absolute A-transpose residual:   4.4409E-16
Residual sum of squares (expected 14):    14.000000000000
PASS stdlib-least-squares
```

### fortran-lapack-symmetric-eigen

```text
Symmetric eigenproblem case (2 has a repeated eigenvalue): 1
Eigenvalues:     1.000000000000    3.000000000000    4.000000000000
Relative Frobenius eigen-equation residual:   0.0000E+00
Relative Frobenius reconstruction error:   1.2696E-16
Column orthogonality error:   3.1561E-16
Symmetric eigenproblem case (2 has a repeated eigenvalue): 2
Eigenvalues:     1.000000000000    3.000000000000    3.000000000000
Relative Frobenius eigen-equation residual:   0.0000E+00
Relative Frobenius reconstruction error:   1.4852E-16
Column orthogonality error:   3.1561E-16
PASS fortran-lapack-symmetric-eigen
```

### fortran-lapack-qr-decomposition

```text
Reduced QR case (2 has dependent columns): 1
Maximum lower-triangular R entry:   0.0000E+00
Least-squares coefficients:     1.000000000000   -2.000000000000    0.500000000000
Maximum absolute A-transpose residual:   1.9984E-15
Residual sum of squares (expected 0.2):     0.200000000000
Relative Frobenius reconstruction error:   9.6719E-17
Column orthogonality error:   2.9635E-16
Reduced QR case (2 has dependent columns): 2
Maximum lower-triangular R entry:   0.0000E+00
Dependent column detected; triangular solve skipped.
Relative Frobenius reconstruction error:   4.7600E-17
Column orthogonality error:   2.6622E-16
PASS fortran-lapack-qr-decomposition
```

### fortran-lapack-svd-decomposition

```text
Reduced SVD case (1 has rank 2; 2 has rank 3): 1
Singular values:     3.000000000000    2.000000000000    0.000000000000
Numerical rank: 2
Right-factor orthogonality error:   3.1561E-16
Relative Frobenius reconstruction error:   1.2317E-16
Column orthogonality error:   5.6051E-16
Reduced SVD case (1 has rank 2; 2 has rank 3): 2
Singular values:     3.000000000000    2.000000000000    1.414213562373
Numerical rank: 3
Right-factor orthogonality error:   3.1976E-16
Relative Frobenius reconstruction error:   3.8137E-16
Column orthogonality error:   6.3292E-16
PASS fortran-lapack-svd-decomposition
```

### minres-indefinite-solve

```text
RHS 1 stop=1 iterations=5
Solution:   1.0000000  -2.0000000   3.0000000  -1.0000000   2.0000000
Max solution error / residual / scaled backward error:   1.7764E-15   1.4211E-14   2.8422E-16
RHS 2 stop=1 iterations=5
Solution:  -1.0000000   0.5000000   2.0000000   1.0000000  -2.0000000
Max solution error / residual / scaled backward error:   3.3307E-16   1.9984E-15   7.5411E-17
PASS minres-indefinite-solve
```

### qdldl-quasidefinite-solve

```text
natural RHS 1 inertia (+,-,0):  3  2  0
Solution:   1.0000000  -2.0000000   3.0000000  -1.0000000   2.0000000
Max solution error / residual / scaled backward error:   4.4409E-16   3.5527E-15   7.1054E-17
natural RHS 2 inertia (+,-,0):  3  2  0
Solution:  -1.0000000   0.5000000   2.0000000   1.0000000  -2.0000000
Max solution error / residual / scaled backward error:   2.2204E-16   8.8818E-16   3.3516E-17
RCM     RHS 1 inertia (+,-,0):  3  2  0
Solution:   1.0000000  -2.0000000   3.0000000  -1.0000000   2.0000000
Max solution error / residual / scaled backward error:   4.4409E-16   1.7764E-15   3.5527E-17
RCM     RHS 2 inertia (+,-,0):  3  2  0
Solution:  -1.0000000   0.5000000   2.0000000   1.0000000  -2.0000000
Max solution error / residual / scaled backward error:   2.2204E-16   8.8818E-16   3.3516E-17
AMD     RHS 1 inertia (+,-,0):  3  2  0
Solution:   1.0000000  -2.0000000   3.0000000  -1.0000000   2.0000000
Max solution error / residual / scaled backward error:   4.4409E-16   3.5527E-15   7.1054E-17
AMD     RHS 2 inertia (+,-,0):  3  2  0
Solution:  -1.0000000   0.5000000   2.0000000   1.0000000  -2.0000000
Max solution error / residual / scaled backward error:   2.2204E-16   4.4409E-16   1.6758E-17
PASS qdldl-quasidefinite-solve
```

### kiss-positive-definite-solve

```text
RHS 1 status=0
First five solution entries:   0.0500000   0.1000000   0.1500000   0.2000000   0.2500000
Max solution error / residual / scaled backward error:   2.2204E-16   1.1102E-15   1.2268E-16
RHS 2 status=0
First five solution entries:  -1.0000000   1.0000000  -1.0000000   1.0000000  -1.0000000
Max solution error / residual / scaled backward error:   2.2204E-16   8.8818E-16   7.4015E-17
PASS kiss-positive-definite-solve
```

### slicot-lyapunov-known-matrix

```text
DICO=C TRANA=N FACT=N RHS=1
Scale / solution error / residual / symmetry:   1.0000E+00   2.2204E-16   2.0186E-16   0.0000E+00
DICO=C TRANA=N FACT=F RHS=2
Scale / solution error / residual / symmetry:   1.0000E+00   2.2204E-16   1.7080E-16   0.0000E+00
DICO=C TRANA=T FACT=N RHS=1
Scale / solution error / residual / symmetry:   1.0000E+00   2.2204E-16   1.4803E-16   0.0000E+00
DICO=C TRANA=T FACT=F RHS=2
Scale / solution error / residual / symmetry:   1.0000E+00   2.2204E-16   1.2688E-16   0.0000E+00
DICO=D TRANA=N FACT=N RHS=1
Scale / solution error / residual / symmetry:   1.0000E+00   1.1102E-16   1.1748E-16   0.0000E+00
DICO=D TRANA=N FACT=F RHS=2
Scale / solution error / residual / symmetry:   1.0000E+00   2.7756E-17   3.0585E-17   0.0000E+00
DICO=D TRANA=T FACT=N RHS=1
Scale / solution error / residual / symmetry:   1.0000E+00   1.1102E-16   1.2545E-16   0.0000E+00
DICO=D TRANA=T FACT=F RHS=2
Scale / solution error / residual / symmetry:   1.0000E+00   1.1102E-16   1.2652E-16   0.0000E+00
PASS slicot-lyapunov-known-matrix
```

### slicot-continuous-sylvester

```text
Rectangular Sylvester case 1
Scaled solution error / residual:   0.0000E+00   0.0000E+00
Recovered 2-by-3 solution:
    1.00000000   -2.00000000    0.50000000
    3.00000000    1.00000000   -1.00000000
Rectangular Sylvester case 2
Scaled solution error / residual:   0.0000E+00   0.0000E+00
Recovered 2-by-3 solution:
   -1.00000000    0.00000000    2.00000000
    0.50000000   -2.00000000    1.00000000
PASS slicot-continuous-sylvester
```

### slicot-discrete-sylvester

```text
Rectangular Sylvester case 1
Scaled solution error / residual:   1.4803E-16   1.3217E-16
Recovered 2-by-3 solution:
    1.00000000   -2.00000000    0.50000000
    3.00000000    1.00000000   -1.00000000
Rectangular Sylvester case 2
Scaled solution error / residual:   1.1102E-16   9.4891E-17
Recovered 2-by-3 solution:
   -1.00000000    0.00000000    2.00000000
    0.50000000   -2.00000000    1.00000000
PASS slicot-discrete-sylvester
```

### blas-gemm-reference

```text
3-by-2 times 2-by-4 matrix product:
    -22.0000    -17.0000    -12.0000     -7.0000
     -8.0000     -7.0000     -6.0000     -5.0000
      6.0000      3.0000      0.0000     -3.0000
Transpose/scaling combinations checked: 12
Maximum scaled error:   0.0000E+00
PASS blas-gemm-reference
```

### fsparse-matvec-reference

```text
A*x for vector 1:     14.000    -6.000     0.000    14.000
A*x for vector 2:     -4.000     3.000     0.000    -5.000
A*x for vector 3:      0.000     0.000     0.000     0.000
COO/CSR accumulated products checked: 24
Rectangular 4-by-3 matrix includes an empty row; zero/nonzero output and zero input checked.
PASS fsparse-matvec-reference
```

### forinv-pseudoinverse-reference

```text
Case 1 reference and identity errors:    2.082E-17   1.480E-16   1.388E-17   1.110E-16   1.110E-16
Rank-one minimum-norm solution:     0.2000000000    0.4000000000
Case 2 reference and identity errors:    1.110E-16   2.220E-16   1.110E-16   2.776E-17   2.190E-17
Case 3 reference and identity errors:    1.110E-16   2.220E-16   5.551E-17   2.190E-17   2.776E-17
Case 4 reference and identity errors:    0.000E+00   0.000E+00   0.000E+00   0.000E+00   0.000E+00
Case 5 reference and identity errors:    0.000E+00   0.000E+00   0.000E+00   0.000E+00   0.000E+00
Known pseudoinverses and all four Moore-Penrose identities checked: 5
Tall, wide, rank-one, singular diagonal and zero matrices; explicit cutoff 1e-10.
PASS forinv-pseudoinverse-reference
```

### arpack-poisson-eigenpairs

```text
Spectrum selection: SM
  1      0.02233834754974      0.02233834754974    1.0970E-15
  2      0.08885438842772      0.08885438842772    1.1443E-15
  3      0.19806226419516      0.19806226419516    5.0502E-15
Matrix-vector callback count: 91
Spectrum selection: LM
 18      3.80193773580484      3.80193773580484    3.8823E-12
 19      3.91114561157228      3.91114561157228    1.1876E-14
 20      3.97766165245026      3.97766165245026    3.8082E-15
Matrix-vector callback count: 71
PASS arpack-poisson-eigenpairs
```

### linalg-poisson-eigenpairs

```text
Index       Computed eigenvalue        Exact eigenvalue          Residual
  1       0.022338347549742       0.022338347549743    1.6894E-15
  2       0.088854388427718       0.088854388427719    1.7069E-15
  3       0.198062264195162       0.198062264195162    1.2668E-15
 18       3.801937735804838       3.801937735804839    1.6422E-15
 19       3.911145611572282       3.911145611572281    1.7166E-15
 20       3.977661652450256       3.977661652450257    1.2187E-15
All 20 checked; maximum eigenvalue/reconstruction errors:    8.88178E-16   3.55271E-15
Six listed eigenpairs use the same n=20 Dirichlet matrix as the ARPACK driver.
PASS linalg-poisson-eigenpairs
```

### fsparse-storage-reference

```text
Dense/COO/CSR checked: 5 x 4 nnz=4
Dense/COO/CSR checked: 4 x 5 nnz=4
Dense/COO/CSR checked: 3 x 2 nnz=0
Dense/COO/CSR checked: 2 x 3 nnz=6
Dense/COO/CSR checked: 1 x 1 nnz=1
PASS fsparse-storage-reference
```

### y12m-sparse-reference

```text
Matrix 1, RHS 1 solution error=  2.22E-16 backward error=  6.58E-17
Matrix 1, RHS 2 solution error=  8.88E-17 backward error=  4.55E-17
Matrix 1, RHS 3 solution error=  0.00E+00 backward error=  0.00E+00
Matrix 1, RHS 4 solution error=  4.43E-17 backward error=  1.75E-17
One sparse LU factorization reused for four right-hand sides.
Matrix 2, RHS 1 solution error=  2.22E-16 backward error=  1.32E-16
Matrix 2, RHS 2 solution error=  1.78E-16 backward error=  9.11E-17
Matrix 2, RHS 3 solution error=  0.00E+00 backward error=  0.00E+00
Matrix 2, RHS 4 solution error=  0.00E+00 backward error=  0.00E+00
One sparse LU factorization reused for four right-hand sides.
PASS y12m-sparse-reference
```

### fordot-exact-reference

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

### linalg-inverse-factor-reference

```text
132 scaled/permuted known-factor matrices, dimensions 1,2,3,4,5,8; two singular rejections.
Maximum inverse error / max(1,maxabs(reference)):   2.1274E-16
Maximum independently accumulated left/right inverse residual:   3.6082E-16
Maximum determinant relative error:   0.0000E+00
PASS linalg-inverse-factor-reference
```

### ntpoly-matrix-root-reference

```text
[1793457956.153449] [modal:39   :0]       tcp_iface.c:912  UCX  ERROR scandir(/sys/class/net) failed: No such file or directory
Dimension=2 pair=1 rotation=1 error=  2.2204E-16
Dimension=2 pair=1 rotation=2 error=  3.3307E-16
Dimension=2 pair=1 rotation=3 error=  5.5511E-16
Dimension=2 pair=2 rotation=1 error=  2.2204E-16
Dimension=2 pair=2 rotation=2 error=  3.8955E-16
Dimension=2 pair=2 rotation=3 error=  4.4409E-16
Dimension=2 pair=3 rotation=1 error=  1.1102E-16
Dimension=2 pair=3 rotation=2 error=  6.0834E-16
Dimension=2 pair=3 rotation=3 error=  5.3291E-16
Dimension=2 pair=4 rotation=1 error=  1.1102E-16
Dimension=2 pair=4 rotation=2 error=  1.6653E-16
Dimension=2 pair=4 rotation=3 error=  4.4409E-16
Dimension=3 pair=1 rotation=1 error=  2.2204E-16
Dimension=3 pair=1 rotation=2 error=  3.3307E-16
Dimension=3 pair=1 rotation=3 error=  5.5511E-16
Dimension=3 pair=2 rotation=1 error=  2.2204E-16
Dimension=3 pair=2 rotation=2 error=  3.8955E-16
Dimension=3 pair=2 rotation=3 error=  4.4409E-16
Dimension=3 pair=3 rotation=1 error=  1.1102E-16
Dimension=3 pair=3 rotation=2 error=  6.0834E-16
Dimension=3 pair=3 rotation=3 error=  5.3291E-16
Dimension=3 pair=4 rotation=1 error=  1.1102E-16
Dimension=3 pair=4 rotation=2 error=  2.7079E-16
Dimension=3 pair=4 rotation=3 error=  4.4409E-16
24 SPD fixtures, 48 matrix functions: known orthogonal factors and positive square-root eigenvalues.
Maximum normalized closed-form error:   6.0834E-16
Maximum independent product residual:   8.8818E-16
PASS ntpoly-matrix-root-reference
```

### libmbd-dimer-spectrum

```text
Bare two-oscillator Hamiltonian calls: 72
Maximum normalized closed-form eigenvalue error:   7.8944E-16
Maximum scalar eigenvector residual:   2.2204E-15
Maximum orthogonality error:   1.5543E-15
PASS libmbd-dimer-spectrum
```

### linalg-qr-reference

```text
Real matrix fixtures: 192; QR factorizations: 576
Square/tall/wide, repeated/zero columns, zero matrices; free and locked pivots.
Maximum normalized scalar reconstruction error:   4.4409E-16
Maximum scalar orthogonality error:   6.6613E-16
PASS linalg-qr-reference
```

### linalg-eigen-reference

```text
Known-spectrum symmetric matrices: 96; eigen calls: 192
Lower triangle with unused-upper-half poison; eigenvalues only and eigenvectors.
Maximum normalized eigenvalue error:   4.4409E-16
Maximum normalized scalar eigenvector residual:   6.1062E-16
Maximum scalar orthogonality error:   1.1102E-15
PASS linalg-eigen-reference
```

### linalg-svd-reference

```text
Known-spectrum rectangular matrices: 144; SVD calls: 576
Full/values-only/U-only/VT-only; distinct/repeated/rank-one/zero spectra at signed scales.
Maximum normalized singular-value error:   4.4409E-16
Maximum normalized scalar reconstruction error:   3.3307E-16
Maximum scalar orthogonality error:   8.8818E-16
Maximum normalized scalar singular-vector residual:   6.9081E-16
PASS linalg-svd-reference
```

### linalg-least-squares-reference

```text
Full-rank least-squares fixtures: 72; solver calls: 288
Overdetermined fixtures with prescribed nonzero residuals: 18
Square/tall/wide; one matrix RHS and three vector RHS calls per fixture.
Maximum normalized solution error:   7.7716E-16
Maximum normalized prescribed-residual error:   3.2058E-16
Maximum normalized normal-equation residual:   2.9143E-16
PASS linalg-least-squares-reference
```

### lsqr-least-squares-reference

```text
Full-rank least-squares fixtures: 72; solver calls: 216
Overdetermined fixtures with prescribed nonzero residuals: 18
Square/tall/wide; three vector RHS calls per fixture; zero damping.
Maximum normalized solution error:   3.3751E-15
Maximum normalized prescribed-residual error:   3.3159E-15
Maximum normalized normal-equation residual:   6.6218E-15
PASS lsqr-least-squares-reference
```

### lsmr-least-squares-reference

```text
Full-rank least-squares fixtures: 72; solver calls: 216
Overdetermined fixtures with prescribed nonzero residuals: 18
Square/tall/wide; three vector RHS calls per fixture; zero damping.
Maximum normalized solution error:   3.0198E-15
Maximum normalized prescribed-residual error:   3.0790E-15
Maximum normalized normal-equation residual:   4.3964E-15
PASS lsmr-least-squares-reference
```

### forsvd-spectrum-reference

```text
Known-spectrum rectangular matrices: 144; SVD calls: 432
Default/GESVD/GESDD; reduced factors, distinct/repeated/rank-one/zero spectra.
Maximum normalized singular-value error:   4.4409E-16
Maximum normalized scalar reconstruction error:   3.3307E-16
Maximum scalar orthogonality error:   9.9920E-16
Maximum normalized scalar singular-vector residual:   6.9081E-16
PASS forsvd-spectrum-reference
```

### foreig-symmetric-reference

```text
Known-spectrum symmetric matrices: 96; eigen calls: 96
Upper triangle with unused-lower-half poison; SYEV eigenvalues and eigenvectors.
Maximum normalized eigenvalue error:   1.1102E-15
Maximum normalized scalar eigenvector residual:   9.9920E-16
Maximum scalar orthogonality error:   1.1102E-15
PASS foreig-symmetric-reference
```

### specialmatrices-diagonal-reference

```text
Nonsingular diagonal fixtures: 36; solve calls: 180
Known solution coordinate checks: 3024
One four-column RHS and four vector RHS calls; signed diagonals and zero RHS.
Maximum normalized solution error:   0.0000E+00
Maximum normalized scalar residual:   0.0000E+00
PASS specialmatrices-diagonal-reference
```

### m-la-magic-reference

```text
Magic-square calls: 124
Entry checks: 45744; exact line-sum checks: 4456
Orders 1 and 3..32; odd/doubly-even/singly-even; compact/padded storage; repeated calls.
PASS m-la-magic-reference
```

### forlab-least-squares-reference

```text
Full-rank least-squares fixtures: 36; solver calls: 108
Overdetermined fixtures with prescribed nonzero residuals: 18
Overdetermined only; three vector RHS calls per fixture; native catalog RPRE.
Maximum normalized solution error:   4.1723E-07
Maximum normalized prescribed-residual error:   2.1397E-07
Maximum normalized normal-equation residual:   3.3833E-07
Forlab real storage bits: 32
PASS forlab-least-squares-reference
```

### fglm-transform-reference

```text
Double-precision vector operations: 48
Single-precision rigid transforms: 72; coordinate references: 864
Both composition orders; points and directions; orthogonality and determinant.
Maximum vector component error:   0.0000E+00
Maximum normalized transform error:   1.0066E-07
PASS fglm-transform-reference
```

### sparse-matvec-reference

```text
Matrix/order fixtures: 250
COO/CSR products: 1500
Checked result entries: 9300
PASS sparse-matvec-reference
```

### linalg-lu-reference

```text
Nonsingular factorizations: 96
Vector/matrix solve calls: 384
Known solution entries: 3072
Singular NaN diagnostics: 8
Factorizations with row swaps: 48
Maximum normalized solution error:   4.0219E-16
Maximum scaled residual:   2.3570E-16
Maximum scaled factorization error:   2.8115E-16
PASS linalg-lu-reference
```

### propack-spectrum-reference

```text
Partial SVD calls: 108
Checked leading triplets: 216
Maximum operator-scaled singular-value error:   1.8808E-15
Maximum operator-scaled triplet residual:   3.4320E-14
Maximum orthogonality error:   1.2801E-13
PASS propack-spectrum-reference
```

### fmm2d-laplace-reference

```text
FMM potential calls: 120
Direct target references: 2880
Maximum cancellation-scaled error at eps=1e-6:   5.6386E-12
Maximum cancellation-scaled error at eps=1e-10:   2.8739E-13
PASS fmm2d-laplace-reference
```

### lightkrylov-gmres-reference

```text
2026-10-31 21:39:55.363: LightKrylov_Logger % comm_setup: Setup serial run
2026-10-31 21:39:55.363: LightKrylov_Logger % logger_setup: IO rank = 0
GMRES solves: 288
Known solution entries: 2016
Solves requiring multiple outer cycles: 100
Maximum normalized solution error:   5.3793E-09
Maximum scaled true residual:   9.2868E-11
PASS lightkrylov-gmres-reference
```

### ntpoly-inverse-reference

```text
[1793482797.721677] [modal:39   :0]       tcp_iface.c:912  UCX  ERROR scandir(/sys/class/net) failed: No such file or directory
SPD matrix inversions: 48
Analytic inverse entries: 1224
Maximum normalized inverse error:   3.4957E-14
Maximum left identity residual:   1.7244E-14
Maximum right identity residual:   9.7700E-15
Maximum normalized symmetry error:   3.3869E-15
PASS ntpoly-inverse-reference
```

### heatflow-bicg-reference

```text
Sparse matrices: 36
BiCG solves: 216
Known solution entries: 3456
Maximum normalized solution error:   2.5522E-11
Maximum normalized true residual:   2.3739E-11
PASS heatflow-bicg-reference
```

### formatmul-products-reference

```text
Matrix/matrix-vector calls: 576
Independent scalar product entries: 6588
Maximum sum-absolute-product scaled error:   1.6933E-16
PASS formatmul-products-reference
```

### lusol-update-reference

```text
Sparse LU factorizations: 32
Single column replacements: 32
Normal/transpose solves: 384
Known solution entries: 1728
Maximum normalized solution error:   2.2204E-16
Maximum normalized true residual:   5.1194E-16
PASS lusol-update-reference
```

### scalapackfx-eigen-reference

```text
[1793489440.169304] [modal:39   :0]       tcp_iface.c:912  UCX  ERROR scandir(/sys/class/net) failed: No such file or directory
Symmetric eigensystems: 384
Prescribed eigenvalue references: 1728
Maximum normalized eigenvalue error:   1.0151E-15
Maximum normalized eigenpair residual:   6.4223E-16
Maximum orthogonality residual:   2.2204E-15
PASS scalapackfx-eigen-reference
```

### dbcsr-products-reference

```text
Block-sparse products: 32; scalar reference entries: 496
Maximum normalized product error:    1.91702E-16
All N/T flag pairs, irregular blocks, sparse/empty inputs and alpha/beta accumulation checked.
Serial real64 CPU build only; MPI, accelerators and symmetry storage unverified.
PASS dbcsr-products-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fortran-lapack-dense-solve fortran-lapack-least-squares stdlib-dense-solve stdlib-least-squares fortran-lapack-symmetric-eigen fortran-lapack-qr-decomposition fortran-lapack-svd-decomposition minres-indefinite-solve qdldl-quasidefinite-solve kiss-positive-definite-solve slicot-lyapunov-known-matrix slicot-continuous-sylvester slicot-discrete-sylvester blas-gemm-reference fsparse-matvec-reference forinv-pseudoinverse-reference arpack-poisson-eigenpairs linalg-poisson-eigenpairs fsparse-storage-reference y12m-sparse-reference fordot-exact-reference linalg-inverse-factor-reference ntpoly-matrix-root-reference libmbd-dimer-spectrum linalg-qr-reference linalg-eigen-reference linalg-svd-reference linalg-least-squares-reference lsqr-least-squares-reference lsmr-least-squares-reference forsvd-spectrum-reference foreig-symmetric-reference specialmatrices-diagonal-reference m-la-magic-reference forlab-least-squares-reference fglm-transform-reference sparse-matvec-reference linalg-lu-reference propack-spectrum-reference fmm2d-laplace-reference lightkrylov-gmres-reference ntpoly-inverse-reference heatflow-bicg-reference formatmul-products-reference lusol-update-reference scalapackfx-eigen-reference dbcsr-products-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. These examples require no backend redeployment or package library rebuild.
