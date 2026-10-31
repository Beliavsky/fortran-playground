# Checked GAMS Lyapunov and Sylvester drivers

These three SLICOT drivers demonstrate [D8: Other matrix equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/D8). The SB04MD and SB04QD procedure mappings add pinned source evidence and numerical-review ledger entries. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Equations and known solutions

| Procedure | Equation solved | Solution size |
| --- | --- | --- |
| SB03MD, continuous | `op(A)^T*X + X*op(A) = scale*C` | 3-by-3 symmetric |
| SB03MD, discrete | `op(A)^T*X*op(A) - X = scale*C` | 3-by-3 symmetric |
| SB04MD | `A*X + X*B = C` | 2-by-3 |
| SB04QD | `X + A*X*B = C` | 2-by-3 |

For each selected equation, the driver chooses a known matrix and constructs the right-hand side by matrix multiplication. After the solve it separately checks the recovered solution and the original equation residual. This does not use output from another solver as a reference.

## Continuous and discrete Lyapunov configurations

```text
A_continuous = [[-1, 2, 0], [-2,-1,0.5], [0,0,-3]]
A_discrete   = [[0.2,0.3,0], [-0.3,0.2,0.1], [0,0,0.5]]
X1 = [[2,0.5,-0.25], [0.5,1,0.2], [-0.25,0.2,1.5]]
X2 = 0.5*X1 + identity(3)
```

The continuous coefficient matrix has eigenvalues `-1+2i,-1-2i,-3`; the discrete matrix has eigenvalues `0.2+0.3i,0.2-0.3i,0.5`. Thus the selected continuous matrix is stable and the selected discrete matrix has spectral radius below one. The complex conjugate pairs exercise real Schur blocks beyond purely diagonal examples.

Each equation is checked with `TRANA=N` (`op(A)=A`) and `TRANA=T` (`op(A)=A^T`). For the first right-hand side, `FACT=N` computes the Schur factors. For the second, `FACT=F` reuses the returned Schur matrix and orthogonal factor while replacing the right-hand side. This gives eight solver calls. `JOB=X` requests only the solution; the driver does not read separation or forward-error outputs.

SB03MD overwrites its right-hand-side array with a scaled solution. The driver requires finite `0<scale<=1`, compares `X_returned/scale` with the known unscaled solution and evaluates the original equation with `scale*C` on its right-hand side. The selected calls return `scale=1`; overflow-driven scaling below one is not independently exercised. Maximum absolute symmetry error must be at most `1e-12`.

## Rectangular Sylvester configurations

```text
A_continuous = [[-1,0.75], [0,-2]]
B_continuous = [[-3,1,0], [0,-4,-0.5], [0,0,-5]]
A_discrete = [[0.2,0.1], [0,0.4]]
B_discrete = [[0.3,-0.2,0], [0,0.5,0.1], [0,0,0.6]]
X1 = [[1,-2,0.5], [3,1,-1]]
X2 = [[-1,0,2], [0.5,-2,1]]
```

The first case uses the listed coefficients and X1. The second uses their transposes and X2, retaining a 2-by-3 solution. The continuous spectra have no pair whose sum is zero; the discrete eigenvalue products are positive and less than one, so `1+lambda(A)*lambda(B)` is nonzero. These choices give unique solutions without intentionally ill-conditioned or singular equations.

Both routines overwrite coefficient and right-hand-side arrays. The driver preserves originals and restores them before evaluating the residual; using returned transformed coefficients would check a different equation. The real workspace length is 1000 and integer workspace length is `4*N`. Each routine must return `INFO=0`.

## Acceptance criteria and limits

All outputs checked here use real64. The scaled solution error is `max(abs(computed-known))/max(1,max(abs(known)))`, bounded by `1e-10`. The scaled residual is `max(abs(LHS-RHS))/max(1,max(abs(RHS)))`, bounded by `1e-12`. Lyapunov residuals use the returned scaled solution and `scale*C`; Sylvester residuals use the unscaled equation. Solutions and residual measures must be finite.

This residual normalization is not claimed to be a condition estimate or a complete normwise backward-error analysis. Near-singular equations, all warning/error branches, condition/error estimates, generalized matrix equations, model reduction and the rest of SLICOT are outside this validation. The examples do not benchmark performance.

## Sources and playground links

| Driver | Pinned procedure and author example |
| --- | --- |
| [Load slicot-lyapunov-known-matrix](https://beliavsky.github.io/fortran-playground/fpm/?package=slicot&example=gams-slicot-lyapunov-known-matrix) / [Source](../fpm_catalog/gams-drivers/slicot-lyapunov-known-matrix.f90) | [Procedure](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/src/SB03MD.f#L1) / [Author example](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/examples/TSB03MD.f) |
| [Load slicot-continuous-sylvester](https://beliavsky.github.io/fortran-playground/fpm/?package=slicot&example=gams-slicot-continuous-sylvester) / [Source](../fpm_catalog/gams-drivers/slicot-continuous-sylvester.f90) | [Procedure](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/src/SB04MD.f#L4) / [Author example](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/examples/TSB04MD.f) |
| [Load slicot-discrete-sylvester](https://beliavsky.github.io/fortran-playground/fpm/?package=slicot&example=gams-slicot-discrete-sylvester) / [Source](../fpm_catalog/gams-drivers/slicot-discrete-sylvester.f90) | [Procedure](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/src/SB04QD.f#L4) / [Author example](https://github.com/SLICOT/SLICOT-Reference/blob/5eeb845d84f5a60f6069754b7819dad468951933/examples/TSB04QD.f) |

The drivers adapt author invocation patterns and retain BSD notices. They appear in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing SLICOT library and compatible LP64 BLAS/LAPACK. Only the mains and executables were rebuilt. The [verification report](gams-matrix-equations-validation.json) records hashes, pins and saved output.

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers slicot-lyapunov-known-matrix slicot-continuous-sylvester slicot-discrete-sylvester
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
