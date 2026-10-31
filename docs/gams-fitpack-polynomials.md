# Checked FITPACK polynomial values and derivatives

These E1a and H1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-fitpack-polynomials-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## Common fixtures

Each independent driver constructs 144 interpolating fits. Source sizes 8 and 13 use uniform ascending coordinates x=-0.5+2*t, t=(i-1)/(n-1), or nonuniform coordinates x=-0.5+2*(t+0.2*t*(1-t)) supplied in reverse order. Spline degrees k=1,3,5 use every monomial x**p for p=0..k with scales -2,0.5,3. All fits explicitly request smoothing=0. Some constant fixtures coincide; 144 counts fits, not distinct data sets.

The same curve object is reused through new_fit, including changes in data size and spline degree. Original coordinates and values must remain unchanged. Fitting and every evaluation must return a successful FITPACK status. All outputs must be finite. Final destroy must reset m and release public x, y and knot arrays. This checks the observed public state, not all internal memory management.

## Values and interpolation (E1a)

At 33 uniformly spaced targets on [-0.5,1.5], including both endpoints, the scalar and vector eval overloads are each compared directly to scale*x**p. These give 9,504 checks. Vector evaluation at the original source nodes adds 1,512 checks, for 11,016 total value references. Reversed source data are sorted before use as vector evaluation targets, independently of FITPACK source sorting.

Maximum value error divided by max(1,maxabs(reference)) must be <=5e-12. Node errors use the analogous normalization from source values. Scalar and vector agreement is not the reference: both must independently reproduce the polynomial.

## Derivatives of the stored spline (H1)

Every fit is checked at the same 33 targets using both scalar and vector dfdx overloads for orders r=0..k. Independent analytical references are zero for r>p and scale*p!/(p-r)!*x**(p-r) otherwise. Falling factorials are formed with small integer-factor products. There are 34,848 positive-order derivative checks and 9,504 zeroth-order value checks, totaling 44,352 references. Quintic fits exercise derivative orders through five, including derivatives of lower-degree polynomials that should vanish.

Maximum error for each derivative-order/fixture pair is divided by max(1,maxabs(analytical_derivative)) and must be <=1e-8. This looser threshold than the value threshold accounts for amplification of coefficient roundoff in higher spline derivatives. It is an explicit acceptance criterion, not an error bound promised by the package. No finite-difference approximation or second numerical library supplies reference derivatives.

## Scope

The H1 link differentiates a fitted spline representation, not an arbitrary callback. These drivers check polynomial reproduction and supported interfaces. Positive smoothing, noisy-data approximation, periodic curves, roots/integrals, extrapolation, malformed inputs, arbitrary nonlinear accuracy and performance remain outside these drivers. The separate stored-spline integration driver retains its own [H2a2b2 evidence](gams-sparse-integral.md).

## Checked links and actual output

These independently written API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and author tests/examples were reviewed for interfaces, without copying upstream code. Loading a link does not submit a job.

### fitpack-polynomial-values

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fitpack&example=gams-fitpack-polynomial-values) / [Driver source](../fpm_catalog/gams-drivers/fitpack-polynomial-values.f90) / [Pinned procedure](https://github.com/perazz/fitpack/blob/1907c7bad9f5c4557970e906bdd4909eb52b2d4c/src/fitpack_curves.f90#L54) / [Author test](https://github.com/perazz/fitpack/blob/1907c7bad9f5c4557970e906bdd4909eb52b2d4c/test/fitpack_curve_tests.f90)

```text
Polynomial fits: 144; value references: 11016
Degrees 1/3/5; uniform and reversed nonuniform data; scalar/vector overloads.
Maximum normalized value error:   6.6613E-16
PASS fitpack-polynomial-values
```

### fitpack-polynomial-derivatives

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fitpack&example=gams-fitpack-polynomial-derivatives) / [Driver source](../fpm_catalog/gams-drivers/fitpack-polynomial-derivatives.f90) / [Pinned procedure](https://github.com/perazz/fitpack/blob/1907c7bad9f5c4557970e906bdd4909eb52b2d4c/src/fitpack_curves.f90#L118) / [Author test](https://github.com/perazz/fitpack/blob/1907c7bad9f5c4557970e906bdd4909eb52b2d4c/examples/example_curve.f90)

```text
Polynomial fits: 144; derivative/value references: 44352
Degrees 1/3/5; uniform and reversed nonuniform data; scalar/vector overloads.
Maximum normalized derivative/value error:   7.1948E-10
PASS fitpack-polynomial-derivatives
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fitpack-polynomial-values fitpack-polynomial-derivatives
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
