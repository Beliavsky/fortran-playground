# Checked GAMS partial differential equation drivers

These I2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, using existing precompiled libraries. Only their main programs and executables were compiled. The [verification report](gams-pde-validation.json) records source hashes, package pins and actual output. These examples do not exhaust PDE methods or the GAMS categories.

Both drivers separate solver error against an exact discrete solution from error against the continuous PDE. The latter includes spatial discretization error and should not be interpreted as failure of the linear solver. The domains, boundary conditions and methods differ, so these runs are not a performance comparison.

## Nonzero Dirichlet Poisson/Helmholtz: fishpack

On `[0,2] x [-1,1]`, the continuous solution is `u=1+x/2-y/4+sin(pi*x/2)*sin(pi*(y+1))`. The driver supplies the nonzero affine boundary values and sampled forcing for `Laplacian(u)+lambda*u=f`, with `lambda=0` and `-0.75`. Three rectangular meshes have 16-by-12, 32-by-24 and 64-by-48 intervals, for six solves.

Let `w` denote the sine product, `a=1+x/2-y/4`, `mu_c=-(pi/2)^2-pi^2`, and `mu_h=-4*sin(pi/(2*m))^2/hx^2-4*sin(pi/n)^2/hy^2`. The forcing is `lambda*a+(mu_c+lambda)*w`. Because the affine part has zero discrete Laplacian and the sine product is a five-point eigenvector, the exact discrete solution is `a+((mu_c+lambda)/(mu_h+lambda))*w`.

Solver status must be zero; the solution and forcing perturbation must be finite. Perturbation and boundary errors must be at most `1e-12`. Maximum error against the exact discrete solution must be at most `1e-11`. Scalar five-point residuals are independently evaluated on the preserved forcing; the maximum residual divided by `max(1,max(abs(f_interior)))` must be at most `1e-11`.

These grids contain sine-product extrema, so the maximum continuous error must agree with `abs((mu_c+lambda)/(mu_h+lambda)-1)` within `1e-11`. Halving both spacings must reduce continuous error by a factor between 3.8 and 4.2. Positive Helmholtz shifts, Neumann/periodic boundary modes, singular compatibility corrections and general nonsmooth forcing are not verified.

## Periodic spectral and finite-difference Poisson: PoisFFT

On a periodic interval of length `2*pi`, the continuous solution is `u=sin(x)+cos(3*x)/4` and forcing `f=-sin(x)-9*cos(3*x)/4`. Grid sizes 16, 32 and 64 sample the interval without duplicating its endpoint. Only roundoff-level mean forcing is removed for compatibility.

The double-precision serial solver is tested with spectral approximation and with the documented `approximation=2` second-order centered operator. For each mode k, the spectral eigenvalue is `-k^2`; the finite-difference eigenvalue is `mu_k=-4*sin(k*pi/n)^2/h^2`. The exact discrete reference is `-sin(x)/mu_1-9*cos(3*x)/(4*mu_3)`. The spectral reference therefore equals the continuous solution.

All computed values must be finite, the maximum error against the exact discrete solution at most `1e-11`, and the solution mean at most `1e-11` in magnitude. Spectral continuous error must also be at most `1e-11`. Finite-difference solutions additionally pass an independent periodic three-point residual check with wraparound indexes, scaled by `max(1,max(abs(f)))` and bounded by `1e-11`. Their continuous error reduction factors must lie between 3.5 and 4.5 on successive doubled grids.

Each of the six solver objects uses FFTW estimate planning and is reused for a second solve with zero forcing, which must return a finite zero solution within `1e-11`. Each object is finalized afterwards: twelve solves in total. The invoked API has no returned numerical status, so independent answer checks determine acceptance. Other boundary conditions, incompatible nonzero-mean forcing, higher dimensions, single precision and MPI/PFFT variants are not verified. Existing package build wrappers and FFTW links were unchanged.

## Checked links and actual output

These independently written API consumers have their own MIT notice. Pinned author examples were reviewed for calling conventions; upstream package terms remain separate. Loading a link selects source without submitting a job.

### fishpack-helmholtz-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fishpack&example=gams-fishpack-helmholtz-reference) / [Driver source](../fpm_catalog/gams-drivers/fishpack-helmholtz-reference.f90) / [Pinned procedure](https://github.com/jlokimlin/fishpack/blob/9dc7d2e7a847fa6a610752d4e91eda3ef9c6130d/src/centered_cartesian_solver.f90#L305) / [Author example/test](https://github.com/jlokimlin/fishpack/blob/9dc7d2e7a847fa6a610752d4e91eda3ef9c6130d/examples/thwscrt.f90)

```text
lambda=  0.00 grid=16x12 solver error=  2.33E-15 PDE error=  1.91E-02 residual=  2.99E-14
lambda=  0.00 grid=32x24 solver error=  4.88E-15 PDE error=  4.74E-03 residual=  1.70E-13
lambda=  0.00 grid=64x48 solver error=  1.15E-14 PDE error=  1.18E-03 residual=  9.96E-13
lambda= -0.75 grid=16x12 solver error=  1.07E-14 PDE error=  1.80E-02 residual=  2.55E-14
lambda= -0.75 grid=32x24 solver error=  3.86E-14 PDE error=  4.47E-03 residual=  1.46E-13
lambda= -0.75 grid=64x48 solver error=  1.43E-13 PDE error=  1.12E-03 residual=  1.87E-12
Six nonzero-Dirichlet Poisson/Helmholtz solves checked against exact discrete solutions.
PASS fishpack-helmholtz-reference
```

### poisfft-periodic-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=poisfft&example=gams-poisfft-periodic-reference) / [Driver source](../fpm_catalog/gams-drivers/poisfft-periodic-reference.f90) / [Pinned procedure](https://github.com/LadaF/PoisFFT/blob/7e7ebcd75130553ef2cf58548ec519933a3d3426/src/poisfft-inc.f90#L1) / [Author example/test](https://github.com/LadaF/PoisFFT/blob/7e7ebcd75130553ef2cf58548ec519933a3d3426/src/testpoisson.f90)

```text
Approximation=0 n=16 solver error=  8.60E-16 continuous PDE error=  8.60E-16
Approximation=0 n=32 solver error=  1.11E-15 continuous PDE error=  1.11E-15
Approximation=0 n=64 solver error=  8.33E-16 continuous PDE error=  8.33E-16
Approximation=2 n=16 solver error=  7.77E-16 continuous PDE error=  4.06E-02
Approximation=2 n=32 solver error=  1.33E-15 continuous PDE error=  9.89E-03
Approximation=2 n=64 solver error=  8.88E-16 continuous PDE error=  2.51E-03
Spectral and second-order periodic Poisson solvers checked at three grids; plans reused for zero forcing.
PASS poisfft-periodic-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fishpack-helmholtz-reference poisfft-periodic-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
