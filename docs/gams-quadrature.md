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

## Maintenance

After changing a driver, verify it again using existing compiled package images:

```text
python xverify_gams_drivers.py --drivers quadpack-smooth quadrature-fortran-smooth quadpack-endpoint-singular
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

The verifier requires Modal authentication and the local `.fpm-audit-cache/precompiled.json` build report. Each driver manifest entry identifies its verification report, allowing optimization and quadrature evidence to be maintained separately. Publication checks the correct report for every driver. These examples and classifications require no backend redeployment or library rebuild.
