# Checked GAMS quadrature drivers

These examples connect specific integration and quadrature-rule procedures to GAMS problem classes. They are checked consumer programs at the catalog source revisions, rather than tests of every quadrature rule or a performance benchmark.

| Class | Problem | Procedures |
| --- | --- | --- |
| [H2a1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a1a1) | Automatic one-dimensional integration on a finite interval, integrand supplied as a procedure | QUADPACK `dqag`; quadrature-fortran `integration_class_1d%integrate`; FGSL `fgsl_integration_qags` |
| [H2a2a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a2a1) | Automatic finite-interval integration for special integrands supplied as procedures | QUADPACK `dqags`, demonstrated with integrable endpoint singularities |
| [H2a2b2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a2b2) | Nonautomatic integration of a stored spline | fitpack `fitpack_curve%integral` |

The [stored-spline integration review](gams-sparse-integral.md) describes the fitpack polynomial antiderivative checks, reversed and zero-width intervals, and partition additivity.

Rule generators in H2c have their own exact-moment checks. The [quadrature-moment and 2D-transform review](gams-moments-nufft2d.md) describes QDUtilLib Legendre and full-function-weight Hermite rules; other generator checks retain their recorded scope below.

## Shared smooth-integral checks

Both smooth drivers integrate `exp(x)` and `cos(20*x)` over `[0,1]`. Analytic reference values are `exp(1)-1` and `sin(20)/20`. They request accuracy `1e-10` and independently require absolute error at most `1e-9`. QUADPACK uses `dqag` key 1 (15-point Gauss-Kronrod); quadrature-fortran uses its adaptive 8-point Gaussian method. These algorithm settings differ even though the functions, intervals and independent acceptance checks are shared.

## Endpoint singularities

The `dqags` driver adapts the author's inverse-square-root test and adds a logarithmic variant: `integral(1/sqrt(x),0,1)=2` and `integral(log(x)/sqrt(x),0,1)=-4`. It requests absolute/relative accuracy `1e-10` and independently requires absolute error at most `1e-8`. The module callback rejects evaluation at the singular endpoint. The driver does not claim support for every special integrand in H2a2a1.

## Sources and playground links

| Driver | Class | Pinned procedure and author test |
| --- | --- | --- |
| [Load quadpack-smooth](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-smooth) · [Driver source](../fpm_catalog/gams-drivers/quadpack-smooth.f90) | H2a1a1 | [Procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L96) · [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90) |
| [Load quadrature-fortran-smooth](https://beliavsky.github.io/fortran-playground/fpm/?package=quadrature-fortran&example=gams-quadrature-fortran-smooth) · [Driver source](../fpm_catalog/gams-drivers/quadrature-fortran-smooth.f90) | H2a1a1 | [Procedure](https://github.com/jacobwilliams/quadrature-fortran/blob/1d208fc59569a97b1c2abf9c45f7c352dcc7b318/src/quadrature_module.F90#L72) · [Author test](https://github.com/jacobwilliams/quadrature-fortran/blob/1d208fc59569a97b1c2abf9c45f7c352dcc7b318/test/test.f90) |
| [Load quadpack-endpoint-singular](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-endpoint-singular) · [Driver source](../fpm_catalog/gams-drivers/quadpack-endpoint-singular.f90) | H2a2a1 | [Procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L1711) · [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90) |
| [Load dcuhre-box-integrals](https://beliavsky.github.io/fortran-playground/fpm/?package=dcuhre&example=gams-dcuhre-box-integrals) · [Driver source](../fpm_catalog/gams-drivers/dcuhre-box-integrals.f90) | H2b1a1 | [Procedure](https://github.com/Zaneham/dcuhre/blob/da8becb7f5313c1d7387066ef2106be9e156e20c/src/dcuhre.f#L1) · [Author test](https://github.com/Zaneham/dcuhre/blob/da8becb7f5313c1d7387066ef2106be9e156e20c/test/dtest1.f) |
| [Load gauss-jacobi-polynomial-moments](https://beliavsky.github.io/fortran-playground/fpm/?package=gaussjacobiquad&example=gams-gauss-jacobi-polynomial-moments) · [Driver source](../fpm_catalog/gams-drivers/gauss-jacobi-polynomial-moments.f90) | H2c | [Procedure](https://github.com/HaoZeke/GaussJacobiQuad/blob/ffb970c68eea0b39b140f80f788c8994547d8bfb/src/GaussJacobiQuad.f90#L45) · [Author test](https://github.com/HaoZeke/GaussJacobiQuad/blob/ffb970c68eea0b39b140f80f788c8994547d8bfb/app/gjp_quad.f90) |
| [Load cubatures-simplex-moments](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran_cubatures&example=gams-cubatures-simplex-moments) · [Driver source](../fpm_catalog/gams-drivers/cubatures-simplex-moments.f90) | H2c | [Procedure](https://github.com/willklausler/fortran_cubatures/blob/aca04975d09aed329fd4210defd7052926dc01c1/src/cubatures.f90#L100) · [Author test](https://github.com/willklausler/fortran_cubatures/blob/aca04975d09aed329fd4210defd7052926dc01c1/test/test_cubatures.f90) |
| [Load integrate-nd-polynomial-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=integrate_fortran&example=gams-integrate-nd-polynomial-reference) · [Driver source](../fpm_catalog/gams-drivers/integrate-nd-polynomial-reference.f90) | H2b1a2 | [Procedure](https://github.com/Euler-37/integrate_fortran/blob/5281426a7407aa8cef7f684ff8cf1f7e4a4df906/src/gauss_leg.f90#L34) · [Author test](https://github.com/Euler-37/integrate_fortran/blob/5281426a7407aa8cef7f684ff8cf1f7e4a4df906/test/check.f90) |
| [Load fitpack-spline-integral](https://beliavsky.github.io/fortran-playground/fpm/?package=fitpack&example=gams-fitpack-spline-integral) · [Driver source](../fpm_catalog/gams-drivers/fitpack-spline-integral.f90) | H2a2b2 | [Procedure](https://github.com/perazz/fitpack/blob/1907c7bad9f5c4557970e906bdd4909eb52b2d4c/src/fitpack_curves.f90#L105) · [Author test](https://github.com/perazz/fitpack/blob/1907c7bad9f5c4557970e906bdd4909eb52b2d4c/examples/example_curve.f90) |
| [Load scifortran-quadrature-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=scifortran&example=gams-scifortran-quadrature-reference) · [Driver source](../fpm_catalog/gams-drivers/scifortran-quadrature-reference.f90) | H2 | [Procedure](https://github.com/SciFortran/SciFortran/blob/ca4a55f49cfdf7a94e388bc3475a5db574d5de99/src/SF_INTEGRATE/SF_INTEGRATE.f90#L1) · [Author test](https://github.com/SciFortran/SciFortran/blob/ca4a55f49cfdf7a94e388bc3475a5db574d5de99/test/src/SF_INTEGRATE/01_test_sf_integrate_quad.f90) |
| [Load kronrod-moments-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=kronrod&example=gams-kronrod-moments-reference) · [Driver source](../fpm_catalog/gams-drivers/kronrod-moments-reference.f90) | H2c | [Procedure](https://github.com/jacobwilliams/kronrod/blob/312278846b6e403fdea410a823d88ef4fb92a3cc/app/main.f90#L1) · [Author test](https://github.com/jacobwilliams/kronrod/blob/312278846b6e403fdea410a823d88ef4fb92a3cc/app/main.f90) |
| [Load fgsl-qags-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fgsl&example=gams-fgsl-qags-reference) · [Driver source](../fpm_catalog/gams-drivers/fgsl-qags-reference.f90) | H2a1a1 | [Procedure](https://github.com/reinh-bader/fgsl/blob/27a3e7cc0809623bcfde680c39a6fdcf0f590c4c/api/integration.finc#L1) · [Author test](https://github.com/reinh-bader/fgsl/blob/27a3e7cc0809623bcfde680c39a6fdcf0f590c4c/doc/examples/integration.f90) |
| [Load qdutillib-moments-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=qdutillib&example=gams-qdutillib-moments-reference) · [Driver source](../fpm_catalog/gams-drivers/qdutillib-moments-reference.f90) | H2c | [Procedure](https://github.com/lauvergn/QDUtilLib/blob/8a1fa9ca7cf52683c98cc4bcb40f21dc41df6ed5/SRC/Quadrature/Quadrature_m.f90#L81) · [Author test](https://github.com/lauvergn/QDUtilLib/blob/8a1fa9ca7cf52683c98cc4bcb40f21dc41df6ed5/APP/App_QDLib.f90) |
| [Load stdlib-trapezoid-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-trapezoid-reference) · [Driver source](../fpm_catalog/gams-drivers/stdlib-trapezoid-reference.f90) | H2a1b2 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L18) · [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_trapz.f90) |
| [Load stdlib-simpson-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-simpson-reference) · [Driver source](../fpm_catalog/gams-drivers/stdlib-simpson-reference.f90) | H2a1b2 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L62) · [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_simps.f90) |
| [Load stdlib-gauss-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-gauss-reference) · [Driver source](../fpm_catalog/gams-drivers/stdlib-gauss-reference.f90) | H2c | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L113) · [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_gauss.f90) |
| [Load stdlib-lobatto-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-lobatto-reference) · [Driver source](../fpm_catalog/gams-drivers/stdlib-lobatto-reference.f90) | H2c | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L124) · [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_gauss.f90) |
| [Load stdlib-trapz-grid-weights-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-trapz-grid-weights-reference) · [Driver source](../fpm_catalog/gams-drivers/stdlib-trapz-grid-weights-reference.f90) | H2a1b2 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L46) · [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_trapz_weights.f90) |
| [Load stdlib-simps-grid-weights-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-simps-grid-weights-reference) · [Driver source](../fpm_catalog/gams-drivers/stdlib-simps-grid-weights-reference.f90) | H2a1b2 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_quadrature.f90#L95) · [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_simps_weights.f90) |
| [Load quadpack-improper-halflines-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-improper-halflines-reference) · [Driver source](../fpm_catalog/gams-drivers/quadpack-improper-halflines-reference.f90) | H2a3a1 | [Procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L514) · [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90) |
| [Load quadpack-interior-breakpoints-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-interior-breakpoints-reference) · [Driver source](../fpm_catalog/gams-drivers/quadpack-interior-breakpoints-reference.f90) | H2a2a1 | [Procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L1058) · [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90) |
| [Load quadpack-cauchy-principal-values-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-cauchy-principal-values-reference) · [Driver source](../fpm_catalog/gams-drivers/quadpack-cauchy-principal-values-reference.f90) | H2a2a1 | [Procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L2233) · [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90) |
| [Load quadpack-oscillatory-weights-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-oscillatory-weights-reference) · [Driver source](../fpm_catalog/gams-drivers/quadpack-oscillatory-weights-reference.f90) | H2a2a1 | [Procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L3107) · [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90) |
| [Load quadpack-endpoint-weights-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-endpoint-weights-reference) · [Driver source](../fpm_catalog/gams-drivers/quadpack-endpoint-weights-reference.f90) | H2a2a1 | [Procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L3757) · [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90) |
| [Load fortranlib-tabulated-integrals-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-tabulated-integrals-reference) · [Driver source](../fpm_catalog/gams-drivers/fortranlib-tabulated-integrals-reference.f90) | H2 | [Procedure](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L1) · [Author test](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/None) |

Loading a link selects code without submitting a job. The same drivers are available in the hosted and main local FPM playgrounds and in downloaded FPM projects. Author license notices are retained with the drivers.

## Recorded results

All 24 passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only each main and executable were compiled. The verification reports lock driver hashes and source revisions: [gams-applied-methods-validation.json](gams-applied-methods-validation.json), [gams-cubature-validation.json](gams-cubature-validation.json), [gams-factorization-rules-ten-validation.json](gams-factorization-rules-ten-validation.json), [gams-grids-spectra-ten-validation.json](gams-grids-spectra-ten-validation.json), [gams-integrals-tensors-ten-validation.json](gams-integrals-tensors-ten-validation.json), [gams-moments-nufft2d-validation.json](gams-moments-nufft2d-validation.json), [gams-next-numerical-validation.json](gams-next-numerical-validation.json), [gams-quadrature-validation.json](gams-quadrature-validation.json), [gams-rkf-qags-validation.json](gams-rkf-qags-validation.json), [gams-roots-splines-quadrature-validation.json](gams-roots-splines-quadrature-validation.json), [gams-rules-differences-validation.json](gams-rules-differences-validation.json), [gams-sparse-integral-validation.json](gams-sparse-integral-validation.json), [gams-statistics-services-ten-validation.json](gams-statistics-services-ten-validation.json).

Success is status `0` for QUADPACK and `1` for quadrature-fortran. The latter reports a signed error estimate. Estimates are printed separately from actual errors against the analytic references; they are not certified error bounds. Zero printed actual error means agreement at the working floating-point precision. Evaluation counts describe these runs and do not establish a general speed ranking.

### quadpack-smooth

```text
Case: exp(x) on [0,1]
Computed integral:   1.71828182845905E+00
Actual absolute error:   0.0000E+00
Reported error estimate:   1.9077E-14
Integrand callback calls: 15
Solver status: 0
Case: cos(20*x) on [0,1]
Computed integral:   4.56472625363813E-02
Actual absolute error:   4.1633E-17
Reported error estimate:   1.2936E-11
Integrand callback calls: 105
Solver status: 0
PASS quadpack-smooth
```

### quadrature-fortran-smooth

```text
Case: exp(x) on [0,1]
Computed integral:   1.71828182845905E+00
Actual absolute error:   0.0000E+00
Reported error estimate:   0.0000E+00
Integrand callback calls: 24
Solver status: 1
Case: cos(20*x) on [0,1]
Computed integral:   4.56472625363814E-02
Actual absolute error:   6.9389E-18
Reported error estimate:  -4.5280E-13
Integrand callback calls: 120
Solver status: 1
PASS quadrature-fortran-smooth
```

### quadpack-endpoint-singular

```text
Case: 1/sqrt(x) on [0,1]; exact integral 2
Computed integral:   2.00000000000000E+00
Actual absolute error:   1.5543E-15
Reported error estimate:   5.7732E-15
Integrand callback calls: 231
Solver status: 0
Case: log(x)/sqrt(x) on [0,1]; exact integral -4
Computed integral:  -4.00000000000000E+00
Actual absolute error:   1.3323E-15
Reported error estimate:   2.5269E-13
Integrand callback calls: 315
Solver status: 0
PASS quadpack-endpoint-singular
```

### dcuhre-box-integrals

```text
Dimensions=2 evaluations=195
Integral / analytic value / estimated error / scaled analytic error
   6.6666666667E-01   6.6666666667E-01   5.3808589798E-15   1.1102230246E-16
   2.9524924420E+00   2.9524924420E+00   3.4203775530E-15   3.0082326615E-16
Dimensions=3 evaluations=635
Integral / analytic value / estimated error / scaled analytic error
   8.0000000000E+00   8.0000000000E+00   1.1139457705E-14   0.0000000000E+00
   1.8863639844E+01   1.8863639844E+01   7.5642426791E-09   1.8419318894E-13
PASS dcuhre-box-integrals
```

### gauss-jacobi-polynomial-moments

```text
recurrence alpha= 0.0 maximum scaled moment error=  2.2204E-16
Nodes:    -0.8611363116  -0.3399810436   0.3399810436   0.8611363116
Weights:   0.3478548451   0.6521451549   0.6521451549   0.3478548451
recurrence alpha= 1.0 maximum scaled moment error=  5.5511E-16
Nodes:    -0.8857916078  -0.4463139727   0.1671808647   0.7204802713
Weights:   0.5420276537   0.8138582720   0.5193901904   0.1247238838
gw alpha= 0.0 maximum scaled moment error=  5.5511E-16
Nodes:    -0.8611363116  -0.3399810436   0.3399810436   0.8611363116
Weights:   0.3478548451   0.6521451549   0.6521451549   0.3478548451
gw alpha= 1.0 maximum scaled moment error=  3.8858E-16
Nodes:    -0.8857916078  -0.4463139727   0.1671808647   0.7204802713
Weights:   0.5420276537   0.8138582720   0.5193901904   0.1247238838
PASS gauss-jacobi-polynomial-moments
```

### cubatures-simplex-moments

```text
triangle degree=5 points=7 moments=21
Maximum scaled moment error:  2.7756E-17
tetrahedron degree=4 points=27 moments=35
Maximum scaled moment error:  2.7756E-17
quadrilateral degree=5 points=9 moments=36
Maximum scaled moment error:  6.6613E-16
PASS cubatures-simplex-moments
```

### integrate-nd-polynomial-reference

```text
3D integral of x^2*y^3*z:      10.66666666666667
Exact polynomial integral checks: 67
Maximum scaled error:    5.31644E-16
Panel counts are explicit; each panel uses six Gauss-Legendre nodes per dimension.
PASS integrate-nd-polynomial-reference
```

### fitpack-spline-integral

```text
Polynomial degree 0 maximum integral error=  2.22E-16
Polynomial degree 1 maximum integral error=  4.44E-16
Polynomial degree 2 maximum integral error=  8.88E-16
Polynomial degree 3 maximum integral error=  8.88E-16
36 integrals checked, including reversed/zero intervals and off-knot partition additivity.
PASS fitpack-spline-integral
```

### scifortran-quadrature-reference

```text
60 sampled-polynomial cases, 240 Simpson/trapezoid calls, even/odd panel counts.
178 adaptive calls: polynomial rules, exponential tails, whole-line and endpoint-singular integrals.
Maximum normalized sampled-rule reference error:   3.8065E-16
Maximum normalized adaptive closed-form error:   7.7716E-16
PASS scifortran-quadrature-reference
```

### kronrod-moments-reference

```text
Gauss order 2; Kronrod nodes 5
Gauss order 3; Kronrod nodes 7
Gauss order 4; Kronrod nodes 9
Gauss order 5; Kronrod nodes 11
Gauss order 6; Kronrod nodes 13
Gauss order 7; Kronrod nodes 15
Gauss order 10; Kronrod nodes 21
Kronrod / Gauss / translated polynomial moments:    64   37   54
Maximum normalized moment error:    6.6667E-103
PASS kronrod-moments-reference
```

### fgsl-qags-reference

```text
Requested absolute/relative tolerance   1.0000E-07: all five integral families passed.
Requested absolute/relative tolerance   1.0000E-10: all five integral families passed.
Adaptive finite-interval integrals with one reused workspace: 40
Integrand evaluations: 4704
Maximum normalized analytical integral error:   3.5069E-13
Maximum normalized reported error estimate:   3.1979E-08
PASS fgsl-qags-reference
```

### qdutillib-moments-reference

```text
Rules: 14; Legendre/Gaussian moments: 144; shifted moments: 47
Orders 1,2,3,4,6,8,12: positive weights, symmetry, exact polynomial moments and deallocation.
Maximum moment error normalized by reference/absolute contributions:   2.5962E-15
PASS qdutillib-moments-reference
```

### stdlib-trapezoid-reference

```text
Affine antiderivatives on nonuniform, reversed and constant-spacing grids: 864
PASS stdlib-trapezoid-reference
```

### stdlib-simpson-reference

```text
Odd grids, lengths 3..33; uniform cubics and nonuniform quadratics versus antiderivatives: 432
PASS stdlib-simpson-reference
```

### stdlib-gauss-reference

```text
33 Gauss-Legendre rules, orders 2..12; centered monomial moments through degree 2*n-1: 462
PASS stdlib-gauss-reference
```

### stdlib-lobatto-reference

```text
33 Lobatto rules, orders 2..12; endpoints and centered monomial moments through degree 2*n-3: 396
PASS stdlib-lobatto-reference
```

### stdlib-trapz-grid-weights-reference

```text
Irregular-grid weight cases and exact polynomial integrals: 102
PASS stdlib-trapz-grid-weights-reference
```

### stdlib-simps-grid-weights-reference

```text
Irregular-grid weight cases and exact polynomial integrals: 306
PASS stdlib-simps-grid-weights-reference
```

### quadpack-improper-halflines-reference

```text
Left/right exponential half-line integrals: 32
PASS quadpack-improper-halflines-reference
```

### quadpack-interior-breakpoints-reference

```text
Supplied interior breakpoints, cusps and integrable singularities: 18
PASS quadpack-interior-breakpoints-reference
```

### quadpack-cauchy-principal-values-reference

```text
Cauchy principal values with polynomial numerators: 36
PASS quadpack-cauchy-principal-values-reference
```

### quadpack-oscillatory-weights-reference

```text
Finite sine/cosine-weighted exponential integrals: 72
Initial-estimate acceptances with last=0: 72
PASS quadpack-oscillatory-weights-reference
```

### quadpack-endpoint-weights-reference

```text
Algebraic/logarithmic endpoint weights against beta derivatives: 144
PASS quadpack-endpoint-weights-reference
```

### fortranlib-tabulated-integrals-reference

```text
Clipped piecewise-linear area intervals plus three full integrals: 198
PASS fortranlib-tabulated-integrals-reference
```

## Maintenance

After changing a driver, verify it again using existing compiled package images:

```text
python xverify_gams_drivers.py --drivers quadpack-smooth quadrature-fortran-smooth quadpack-endpoint-singular dcuhre-box-integrals gauss-jacobi-polynomial-moments cubatures-simplex-moments integrate-nd-polynomial-reference fitpack-spline-integral scifortran-quadrature-reference kronrod-moments-reference fgsl-qags-reference qdutillib-moments-reference stdlib-trapezoid-reference stdlib-simpson-reference stdlib-gauss-reference stdlib-lobatto-reference stdlib-trapz-grid-weights-reference stdlib-simps-grid-weights-reference quadpack-improper-halflines-reference quadpack-interior-breakpoints-reference quadpack-cauchy-principal-values-reference quadpack-oscillatory-weights-reference quadpack-endpoint-weights-reference fortranlib-tabulated-integrals-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

The verifier requires Modal authentication and the local `.fpm-audit-cache/precompiled.json` build report. Each driver manifest entry identifies its verification report, allowing optimization and quadrature evidence to be maintained separately. Publication checks the correct report for every driver. These examples and classifications require no backend redeployment or library rebuild.
