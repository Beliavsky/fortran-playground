# Checked quadratic roots, spline derivatives and quadrature

These F1, E1 and H2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-roots-splines-quadrature-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Known quadratic roots: fortranlib (F1)

All 21 distinct pairs from [-4,-2,-0.5,0,0.5,2,4] are used to form `a*(x-r1)*(x-r2)`, with a in [-8,-0.5,0.5,8]: 84 calls. Coefficients and roots are dyadic, so this moderate fixture avoids coefficient-rounding ambiguity. Returned roots are sorted by the caller and must match the known pair within absolute error 2e-12. Root sums and products are also checked within 2e-12.

Each root must have polynomial residual, divided by `max(1,abs(a*x*x)+abs(b*x)+abs(c))`, at most 2e-12. The ordinary real64 quadratic API is checked. No matching author driver is recorded. Repeated or complex roots, zero leading coefficient, Pascal/reduced variants, real32, severe cancellation and extreme scaling are outside this example. This F1 mapping describes a quadratic solver; it does not claim a general iterative root finder or verify the separate E1 interpolation and H2 integration mappings.

## Cubic-spline values and derivatives: fortran-utils (E1)

Four polynomials, degrees 0,1,2,3, are sampled on uniform grids of 5,9,17 points and a nine-point nonuniform grid, all spanning [-1,1]. There are 16 polynomial/grid fixtures. The polynomials are `1`, `2*x-1`, `3*x*x-2*x+0.5` and `x**3-0.5*x*x+2*x-1`. Known formulas supply values and both derivatives at 65 queries from -1 to 1 in steps of 1/32: 3120 independent scalar references.

The consistent-cubic endpoint conditions selected by spline3ders should reproduce these polynomials. Every component must be finite and within absolute error 5e-10. Three additional calls per fixture request only the first derivative, only the second derivative, and only values with reversed query order; they must agree with the full call within 5e-12. In total, 64 spline calls check endpoints, knots, interior values, optional outputs and decreasing query order. The author spline tests were reviewed for usage. Extrapolation, nonpolynomial convergence, other endpoint conditions, invalid grids and the separate N6 sorting mapping are not verified.

## Sampled and adaptive integration: SciFortran (H2)

On intervals [-1,1], [0,1] and [-0.5,1.5], sample counts [5,8,9,16,17] exercise even and odd panel counts. Powers x**p, p=0..3, give 60 fixtures. Simpson and trapezoidal calls use both endpoint and step-size overloads: 240 sampled-rule calls. Simpson must reproduce the polynomial antiderivative. The independent trapezoidal reference adds `(b-a)*h*h/6` for x*x and `(b*b-a*a)*h*h/4` for x**3 to the exact integral; for degrees 0 and 1 it is exact. This checks the expected discrete rule, rather than treating trapezoidal discretization error as solver failure. Normalized errors must be at most 2e-12.

Adaptive integration checks powers 0..7 on the same three intervals with the default wrapper and all six Gauss-Kronrod keys: 168 calls. Six exponential tails have rates [0.5,1,2], lower endpoints [0,1] and reference exp(-rate*a)/rate. Whole-line Gaussian and Cauchy integrals have references sqrt(pi) and pi. Endpoint-singular mode integrates sqrt(x) and 1/sqrt(x) on [0,1], with references 2/3 and 2. These total 178 adaptive calls. Requested absolute/relative tolerances are 1e-11, with normalized closed-form error at most 5e-11. All results must be finite; normalization is max(1,abs(reference)).

Module callbacks follow the working upstream usage. This uses the existing selected SciFortran integration subset and coefficient-precision repairs; no library rebuild or new source patch is introduced. Weighted/pole integrals, complex and nonuniform sampled rules, all QUADPACK error paths and performance are outside this example.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### fortranlib-quadratic-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-quadratic-reference) / [Driver source](../fpm_catalog/gams-drivers/fortranlib-quadratic-reference.f90) / [Pinned procedure](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_algebra.f90#L1)

```text
84 quadratics: 21 distinct dyadic root pairs and four positive/negative coefficient scales.
Maximum absolute root error:   0.0000E+00
Maximum normalized polynomial residual:   0.0000E+00
Root order normalized by caller; sums and products checked independently.
PASS fortranlib-quadratic-reference
```

### fortran-utils-spline-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-utils&example=gams-fortran-utils-spline-reference) / [Driver source](../fpm_catalog/gams-drivers/fortran-utils-spline-reference.f90) / [Pinned procedure](https://github.com/certik/fortran-utils/blob/b43bd24cd421509a5bc6d3b9c3eeae8ce856ed88/src/splines.f90#L1) / [Author example/test](https://github.com/certik/fortran-utils/blob/b43bd24cd421509a5bc6d3b9c3eeae8ce856ed88/tests/splines/test_splines.f90)

```text
16 polynomial/grid fixtures, 65 queries each, 3120 value/derivative references.
Maximum errors: value, first derivative, second derivative:   2.2204E-16  8.8818E-16  1.7764E-15
Uniform/nonuniform knots, endpoints, optional outputs and reversed query order checked.
PASS fortran-utils-spline-reference
```

### scifortran-quadrature-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=scifortran&example=gams-scifortran-quadrature-reference) / [Driver source](../fpm_catalog/gams-drivers/scifortran-quadrature-reference.f90) / [Pinned procedure](https://github.com/SciFortran/SciFortran/blob/ca4a55f49cfdf7a94e388bc3475a5db574d5de99/src/SF_INTEGRATE/SF_INTEGRATE.f90#L1) / [Author example/test](https://github.com/SciFortran/SciFortran/blob/ca4a55f49cfdf7a94e388bc3475a5db574d5de99/test/src/SF_INTEGRATE/01_test_sf_integrate_quad.f90)

```text
60 sampled-polynomial cases, 240 Simpson/trapezoid calls, even/odd panel counts.
178 adaptive calls: polynomial rules, exponential tails, whole-line and endpoint-singular integrals.
Maximum normalized sampled-rule reference error:   3.8065E-16
Maximum normalized adaptive closed-form error:   7.7716E-16
PASS scifortran-quadrature-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fortranlib-quadratic-reference fortran-utils-spline-reference scifortran-quadrature-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
