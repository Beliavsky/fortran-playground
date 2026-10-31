# Checked GAMS sparse and positive-definite linear-system drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [D2b4](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2b4) | Real symmetric sparse systems | `minres_solver`; `qdldl_type%analyze/factor/solve` |
| [D2b1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2b1b) | Real symmetric positive-definite systems | KISS `cg_dense` |

These examples distinguish the matrix requirements and storage used by each API. GAMS categories are not exhausted; the [coverage report](gams-coverage.md) tracks the remaining class-specific driver gaps.

## Shared symmetric indefinite problem

MINRES and qdldl-fortran solve the same five-variable system for two right-hand sides:

```text
A = [[4, 1,  0,  1,  0],
     [1, 5, -1,  2,  0],
     [0,-1,  6, -1,  1],
     [1, 2, -1, -2,  0],
     [0, 0,  1,  0, -3]]

x1 = [ 1, -2, 3, -1,  2]
x2 = [-1,0.5, 2,  1, -2]
b1 = A*x1; b2 = A*x2
```

This is a quasi-definite block matrix `[[H,B^T],[B,-C]]`. The leading 3-by-3 `H` is symmetric with positive diagonal and strictly diagonally dominant; `C=diag(2,3)` is positive definite. The full matrix has three positive and two negative eigenvalues and no zero eigenvalues. This supplies an independent inertia check without calling another eigensolver.

The solver representation stores the 11 upper-triangle nonzeros. Both drivers use a separate explicit dense matrix to construct right-hand sides and check residuals. MINRES additionally checks its sparse operator product against this dense reference before solving.

## Solver configurations

MINRES receives a module matrix-vector callback, zero shift, symmetry checking enabled, no preconditioning, relative tolerance `1e-12` and at most 100 iterations. Only stop reasons 1 or 2 (residual convergence) are accepted for these nonzero right-hand sides. An identity preconditioner callback is supplied for the API but preconditioning is disabled. Singular least-squares behavior, shifts and preconditioners are not demonstrated.

qdldl-fortran performs symbolic analysis and numeric factorization once for each of natural, RCM and AMD orderings. Each factorization is reused to solve both right-hand sides. Analysis, factorization and solve must each report success, and computed inertia must be `(3,2,0)`. Static regularization and iterative refinement are explicitly disabled because this matrix already satisfies the quasi-definite requirement. The method does not pivot; these checks do not extend its guarantees to arbitrary symmetric indefinite matrices.

## Positive-definite conjugate-gradient problem

KISS solves a separate 20-by-20 symmetric tridiagonal matrix with diagonal 4 and off-diagonals -1. Positive diagonal and strict diagonal dominance establish positive definiteness. The driver uses `cg_dense`, so the matrix is stored densely even though its entries form a sparse stencil. This illustrates the reviewed dense API and is not a sparse-storage performance example.

The known solutions are `x(i)=i/20` and `x(i)=(-1)**i`. Right-hand sides are constructed independently with `b(i)=4*x(i)-x(i-1)-x(i+1)`, omitting neighbors outside the interval. Each solve starts at zero, with `rtol=1e-12`, `atol=1e-14` and `maxiter=200`; returned `info` must be zero. Other KISS iterative methods and indefinite matrices are outside this driver.

## Common acceptance criteria

All three require finite solutions, maximum absolute solution error at most `1e-9`, and scaled normwise backward error at most `1e-11`:

```text
eta = ||A*x-b||_inf / (||A||_inf*||x||_inf + ||b||_inf)
```

The matrix infinity norm is the maximum absolute row sum. Each example prints the absolute residual as well as the solution and backward errors. These small deterministic cases check the recorded configurations; they do not measure large-system scalability or rank packages by speed.

## Sources and playground links

| Driver | Pinned procedure and author example |
| --- | --- |
| [Load minres-indefinite-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=minres&example=gams-minres-indefinite-solve) / [Source](../fpm_catalog/gams-drivers/minres-indefinite-solve.f90) | [Procedure](https://github.com/willdickson/minres/blob/c7bb4c7a0ddf13729d3556878ccc688a208a052a/src/minres/minres_mod.f90#L40) / [Author example](https://github.com/willdickson/minres/blob/c7bb4c7a0ddf13729d3556878ccc688a208a052a/test/minres_test.f90) |
| [Load qdldl-quasidefinite-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=qdldl-fortran&example=gams-qdldl-quasidefinite-solve) / [Source](../fpm_catalog/gams-drivers/qdldl-quasidefinite-solve.f90) | [Procedure](https://github.com/jacobwilliams/qdldl-fortran/blob/8ebdd7fa1075bfb89115d0955806b0996b6b29d5/src/qdldl_module.f90#L28) / [Author example](https://github.com/jacobwilliams/qdldl-fortran/blob/8ebdd7fa1075bfb89115d0955806b0996b6b29d5/example/example_kkt.f90) |
| [Load kiss-positive-definite-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=kiss&example=gams-kiss-positive-definite-solve) / [Source](../fpm_catalog/gams-drivers/kiss-positive-definite-solve.f90) | [Procedure](https://github.com/ivan-pi/kiss/blob/55f0f7ccb1601a0628a17928b5b6b79f61da2892/src/kiss.F90#L147) / [Author example](https://github.com/ivan-pi/kiss/blob/55f0f7ccb1601a0628a17928b5b6b79f61da2892/test/test_kiss.f90) |

The drivers adapt author API patterns and retain license notices. They appear in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-sparse-validation.json) records hashes, pins and saved output.

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers minres-indefinite-solve qdldl-quasidefinite-solve kiss-positive-definite-solve
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
