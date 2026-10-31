# Checked GAMS linear-algebra drivers

These real64 consumer programs compare fortran-lapack and stdlib on the same small dense systems and unconstrained least-squares problems, with additional fortran-lapack matrix-decomposition examples, BLAS products, sparse products and known pseudoinverses. Procedure mappings describe the reviewed real configurations; other overloads require their own evidence.

| Class | Configuration | Procedures |
| --- | --- | --- |
| [D2a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2a1) | Real nonsymmetric general linear systems | `linear_algebra:solve`; `stdlib_linalg:solve` |
| [D9a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D9a1) | Unconstrained linear least squares, L2 solution | `linear_algebra:lstsq`; `stdlib_linalg:lstsq` |
| [D4a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D4a1) | Ordinary real symmetric eigenproblems | fortran-lapack `la_lapack:syev`, real64 overload |
| [D5](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D5) | Orthogonalization, demonstrated by reduced QR | fortran-lapack `linear_algebra:qr` |
| [D6](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D6) | Singular value decomposition | fortran-lapack `la_lapack:gesvd`, real64 overload |
| [D1b6](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D1b6) | Rectangular real matrix products | blas-interface `blas_gemm` |
| [D1b4](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D1b4) | Rectangular sparse matrix-vector products | fsparse `matvec`, COO/CSR real64 overloads |
| [D9c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D9c) | Generalized inverse | forinv `inv`, SVD method with explicit cutoff |

## Shared dense-system checks

Both solve drivers use the 3-by-3 systems from stdlib `example_solve1` and fortran-lapack `test_dsolve`, with reference solutions `[5,3,-2]` and `[-2,-2,3]`. They preserve the original matrix and right-hand side, check solver status and finite solutions, and require maximum solution error at most `1e-10`. The independently computed scaled residual is `||A*x-b||_inf / (||A||_inf*||x||_inf + ||b||_inf)` and must be at most `1e-12`. Matrix infinity norm means the maximum absolute row sum.

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

## Known pseudoinverses and minimum-norm solutions

The D9c driver uses `forinv:inv(method="gesvd",tol=1e-10)` for five cases. For the rank-one matrix `u*v^T`, `u=[1,2,3]`, `v=[1,2]`, the explicit pseudoinverse is `v*u^T/70`. Its application to `b=u` must produce the minimum-norm solution `[1/5,2/5]`. A full-rank tall matrix with orthogonal columns `[1,2,2]` and `[2,-1,0]` has pseudoinverse rows equal to those columns divided by 9 and 5 respectively. The wide transpose must have the transposed pseudoinverse. The remaining cases are `diag(2,0,4)`, with inverse `diag(1/2,0,1/4)`, and a zero 3-by-2 matrix, with a zero 2-by-3 pseudoinverse.

Each case checks the explicit reference and all four Moore-Penrose conditions: `A*Aplus*A=A`, `Aplus*A*Aplus=Aplus`, symmetry of `A*Aplus`, and symmetry of `Aplus*A`. Maximum-entry errors are divided by `max(1,max(abs(reference)))` for the corresponding matrix and bounded by `1e-11`; all results/errors must be finite. The minimum-norm coefficient error is bounded by `1e-11`. Original matrices are preserved because the pinned ForSVD dependency can overwrite the SVD input despite its declared input intent. The cutoff is absolute in this API. This does not test default cutoff behavior, alternative methods, ill-conditioning, near-threshold numerical ranks or general rank selection.

## Observed high-level link limit

On 2026-10-30, the high-level `linear_algebra:eigh` and `linear_algebra:svd` versions compiled their mains but failed to link under the hosted 16 MiB per-file limit with GNU Fortran 16.2.0/FPM 0.12.0 and the existing precompiled fortran-lapack image at revision `e5e45fdd5a38bfab06d1f703f12b787937aa33bb`. The linker reported:

```text
collect2: fatal error: ld terminated with signal 25 [File size limit exceeded]
```

Saved reproducers: [high-level eigh](gams-candidates/fortran-lapack-eigh.f90) and [high-level svd](gams-candidates/fortran-lapack-svd.f90). These are failed hosted probes for that image, with no successful hosted-run designation. They may be useful for local reproduction or discussing executable size with the package author. The menu examples use the lower-level `syev`/`gesvd` APIs, which passed under the same limits and with the same precompiled library. Sandbox limits were unchanged.

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

The dense examples reuse both authors' problem data and retain both license notices. The least-squares examples adapt author API usage to shared deterministic data. These drivers appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All 16 passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only each main and executable were rebuilt. The [verification report](gams-linear-algebra-validation.json) records source hashes, pins and saved output. These small examples establish checked usage, rather than comprehensive accuracy or performance comparisons. The packages may share underlying algorithms; this is not evidence of independent implementations. Zero printed error means agreement at working precision.

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers fortran-lapack-dense-solve fortran-lapack-least-squares stdlib-dense-solve stdlib-least-squares fortran-lapack-symmetric-eigen fortran-lapack-qr-decomposition fortran-lapack-svd-decomposition minres-indefinite-solve qdldl-quasidefinite-solve kiss-positive-definite-solve slicot-lyapunov-known-matrix slicot-continuous-sylvester slicot-discrete-sylvester blas-gemm-reference fsparse-matvec-reference forinv-pseudoinverse-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. These examples require no backend redeployment or package library rebuild.
