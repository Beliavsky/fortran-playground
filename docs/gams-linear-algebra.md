# Checked GAMS linear-algebra drivers

These real64 consumer programs compare fortran-lapack and stdlib on the same small dense systems and unconstrained least-squares problems. Procedure mappings describe the reviewed real configurations; other overloads require their own evidence.

| Class | Configuration | Procedures |
| --- | --- | --- |
| [D2a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D2a1) | Real nonsymmetric general linear systems | `linear_algebra:solve`; `stdlib_linalg:solve` |
| [D9a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D9a1) | Unconstrained linear least squares, L2 solution | `linear_algebra:lstsq`; `stdlib_linalg:lstsq` |

## Shared dense-system checks

Both solve drivers use the 3-by-3 systems from stdlib `example_solve1` and fortran-lapack `test_dsolve`, with reference solutions `[5,3,-2]` and `[-2,-2,3]`. They preserve the original matrix and right-hand side, check solver status and finite solutions, and require maximum solution error at most `1e-10`. The independently computed scaled residual is `||A*x-b||_inf / (||A||_inf*||x||_inf + ||b||_inf)` and must be at most `1e-12`. Matrix infinity norm means the maximum absolute row sum.

## Shared least-squares checks

Use `t=[-2,-1,0,1,2]`, noise `e=[1,-2,2,-2,1]`, and observations `b=1+2*t+e`. The noise is orthogonal to the constant and linear columns. The full-rank design `[1,t]` therefore has reference coefficients `[1,2]`. A second design `[1,t,t]` has duplicate columns; the SVD-based solvers should return the minimum-norm coefficients `[1,1,1]`. Both have rank 2 and residual sum of squares 14.

The drivers check solver status, finite coefficients, numerical rank and coefficient error at most `1e-10`. They independently require `max(abs(transpose(A)*(A*x-b))) <= 1e-10` and residual sum of squares within `1e-10` of 14. A nonzero residual is expected for these inconsistent systems; a small normal-equation residual alone would not identify the minimum-norm solution in the rank-deficient case. The known coefficient check does.

## Sources and playground links

| Driver | Class | Pinned procedure and author example |
| --- | --- | --- |
| [Load fortran-lapack-dense-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lapack&example=gams-fortran-lapack-dense-solve) · [Source](../fpm_catalog/gams-drivers/fortran-lapack-dense-solve.f90) | D2a1 | [Procedure](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/src/la_solve.f90#L139) · [Author example](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/test/test_la_solve.f90) |
| [Load fortran-lapack-least-squares](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lapack&example=gams-fortran-lapack-least-squares) · [Source](../fpm_catalog/gams-drivers/fortran-lapack-least-squares.f90) | D9a1 | [Procedure](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/src/la_least_squares.f90#L168) · [Author example](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/test/test_linalg_lstsq.f90) |
| [Load stdlib-dense-solve](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-dense-solve) · [Source](../fpm_catalog/gams-drivers/stdlib-dense-solve.f90) | D2a1 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L734) · [Author example](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_solve1.f90) |
| [Load stdlib-least-squares](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-least-squares) · [Source](../fpm_catalog/gams-drivers/stdlib-least-squares.f90) | D9a1 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1393) · [Author example](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_lstsq1.f90) |

The dense examples reuse both authors' problem data and retain both license notices. The least-squares examples adapt author API usage to shared deterministic data. These drivers appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All four passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only each main and executable were rebuilt. The [verification report](gams-linear-algebra-validation.json) records source hashes, pins and saved output. These small examples establish checked usage, rather than comprehensive accuracy or performance comparisons. The packages may share underlying algorithms; this is not evidence of independent implementations. Zero printed error means agreement at working precision.

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers fortran-lapack-dense-solve stdlib-dense-solve fortran-lapack-least-squares stdlib-least-squares
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. These examples require no backend redeployment or package library rebuild.
