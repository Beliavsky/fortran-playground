# Checked full-rank least squares and one-dimensional interpolation

These D9a1 and E1a drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-least-interpolation-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Prescribed least-squares solutions and residuals: linalg (D9a1)

Seventy-two fixtures combine shapes [1,1], [2,1], [3,2], [5,3], [2,3], [3,5]; signed scales [-4,0.5,2]; identity/Householder factors; and two residual settings. Let k=min(m,n). Scalar sums construct A=L(:,1:k)*diag(d)*transpose(R(:,1:k)), with d(i)=i*scale and known orthogonal L/R. For each of three right-hand sides c, z(i)=(2*i-c)/4 and x_star=R(:,1:k)*z. The right-hand side is b=A*x_star+noise. Noise is zero for the first residual setting and for square/underdetermined systems; in the second overdetermined setting it is 0.25*c*L(:,n+1). Thus 18 fixtures have prescribed nonzero residuals. Settings coincide when a nonzero orthogonal residual is unavailable; the count describes evaluations, not 72 distinct matrices.

All matrices have full rank. For tall systems the noise is orthogonal to A's columns, so x_star is the unique least-squares minimizer and the exact residual is -noise. For wide systems b is consistent and x_star lies in A's row space, so it is the unique minimum-norm solution. Each three-column matrix solve is checked alongside three separate vector solves: 288 solver calls. The author API is source-reviewed; no matching author example is recorded for this procedure, so these fixtures and references are independently constructed.

Every solution must have the expected shape and finite values, and must match x_star within maximum-entry error divided by max(1,maxabs(x_star)) of 3e-12. Inputs must remain unchanged. Scalar products independently reconstruct A*x-b; it must equal -noise within max-entry error divided by max(1,maxabs(b)) of 5e-12. Squared residual norms must match (rho*c)**2 with absolute error divided by max(1,(rho*c)**2) at most 1e-11. Normal-equation products transpose(A)*(A*x-b) must be at most 1e-11 after division by max(1,maxabs(b))*max(1,maxabs(A)). Both exact-fit and nonzero-residual cases are checked. Rank-deficient, complex, malformed-input and large/ill-conditioned systems, alternative least-squares APIs and performance remain unverified.

## Affine exactness and shape-preserving cubics: interpolation (E1a)

Two five-knot grids are [-2,-1,0,1,2] and [-2,-1.5,-0.25,0.5,2]. For each grid, methods linear, pchip and its cubic alias interpolate three affine components with slopes [2,-0.75,0] and offsets [1,2,-3] at 41 queries on [-2,2]. All four combinations of scalar/vector tabulated quantities and scalar/vector queries are checked. Explicit extrapolation at -3 and 3 must reproduce those affine functions; the default behavior at the same outside points must instead return NaN. There are 2,988 exact affine references and 36 explicit NaN checks.

PCHIP is then sampled at 129 queries on each grid for the plateau profile [0,1,1,2,3], the turning profile [0,2,-1,3,1], and their negatives. Every sample must be finite and lie between its independently identified bracketing data values, within 2e-12. Both signs of the plateau profile must remain monotone. These give 1,032 interval-bound checks and 512 adjacent monotonicity checks; all five knots for each of eight profiles add 40 exact references.

An explicit nonlinear reference uses [0,1,0] at [0,1,2]. This package uses endpoint secant slopes and a zero slope at the middle peak. On [0,1], the Hermite constraints give f(t)=-t**3+t**2+t; on [1,2] the function is its reflection f(2-t). Both pchip and cubic must reproduce that polynomial at 129 points, adding 258 exact references. The endpoint convention is part of this pinned package's checked behavior; no equivalence to every other PCHIP implementation is claimed.

In total 3,286 exact values must be finite and agree within error divided by max(1,abs(reference)) of 2e-12. The fixture does not independently certify error bounds for arbitrary smooth functions, nonlinear extrapolation, malformed or unsorted input, the interpolator class interface or every possible shape. Author tests were reviewed for public API and boundary behavior; no upstream code is copied.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream terms remain separate. Loading a link does not submit a job.

### linalg-least-squares-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-least-squares-reference) / [Driver source](../fpm_catalog/gams-drivers/linalg-least-squares-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_least_squares.f90#L14)

```text
Full-rank least-squares fixtures: 72; solver calls: 288
Overdetermined fixtures with prescribed nonzero residuals: 18
Square/tall/wide; one matrix RHS and three vector RHS calls per fixture.
Maximum normalized solution error:   7.7716E-16
Maximum normalized prescribed-residual error:   3.2058E-16
Maximum normalized normal-equation residual:   2.9143E-16
PASS linalg-least-squares-reference
```

### interp1-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=interpolation&example=gams-interp1-reference) / [Driver source](../fpm_catalog/gams-drivers/interp1-reference.f90) / [Pinned procedure](https://github.com/furstj/interpolation/blob/bf6d22ad931855d510dcfb5bdd6870cce8924b22/src/interpolation.f90#L14) / [Author example/test](https://github.com/furstj/interpolation/blob/bf6d22ad931855d510dcfb5bdd6870cce8924b22/test/interp1_test.f90)

```text
Exact affine references across all four overloads, including extrapolation: 2988
Exact mirrored cubic references (pchip/cubic aliases): 258
Total exact / NaN / interval-bound / monotonicity checks:   3286    36  1032   512
Maximum normalized exact-reference error:   1.5543E-15
PASS interp1-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers linalg-least-squares-reference interp1-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
