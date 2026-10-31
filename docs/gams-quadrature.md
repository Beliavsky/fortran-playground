# Checked GAMS quadrature drivers

These examples connect specific integration procedures to finite-interval GAMS problem classes. They are checked consumer programs at the catalog source revisions, rather than tests of every quadrature rule or a performance benchmark.

| Class | Problem | Procedures |
| --- | --- | --- |
| [H2a1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a1a1) | Automatic one-dimensional integration on a finite interval, integrand supplied as a procedure | QUADPACK `dqag`; quadrature-fortran `integration_class_1d%integrate` |
| [H2a2a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2a2a1) | Automatic finite-interval integration for special integrands supplied as procedures | QUADPACK `dqags`, demonstrated with integrable endpoint singularities |

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

Loading a link selects code without submitting a job. The same drivers are available in the hosted and main local FPM playgrounds and in downloaded FPM projects. Author license notices are retained with the drivers.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only each main and executable were compiled. The [verification report](gams-quadrature-validation.json) locks the driver hashes and source revisions.

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

## Maintenance

After changing a driver, verify it again using existing compiled package images:

```text
python xverify_gams_drivers.py --drivers quadpack-smooth quadrature-fortran-smooth quadpack-endpoint-singular
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

The verifier requires Modal authentication and the local `.fpm-audit-cache/precompiled.json` build report. Each driver manifest entry identifies its verification report, allowing optimization and quadrature evidence to be maintained separately. Publication checks the correct report for every driver. These examples and classifications require no backend redeployment or library rebuild.
