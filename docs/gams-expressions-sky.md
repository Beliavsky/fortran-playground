# Checked expressions and sky-coordinate rotations

These N3 and P drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-expressions-sky-validation.json) retains pins, source hashes, stdout and stderr. GAMS categories are not exhausted.

## FEQParse multivariable expression evaluation (N3)

Twelve valid real64 expressions cover arithmetic, parentheses, powers, pi, trigonometric functions, exp, log, sqrt, abs and compositions. Each is evaluated on a 7 by 7 by 7 grid: x,y,z range from -1.5 to 1.5 in steps of 0.5. These 343 tuples stay inside the real domains of every expression.

There are 24 parser objects: one with declarations [x,y,z] and one with [z,y,x] for each expression. Scalar and batch evaluations use correspondingly reordered inputs; reversed declarations are also evaluated in reverse scalar traversal. All 16,464 outputs are checked against direct native Fortran formulas, rather than merely against another parser call. Quartics use explicit products; the real power 2**(x/2) uses exp(log(2)*x/2) as its reference. Inputs must remain unchanged.

Every output must be finite and abs(result-reference)/(1+abs(reference)) <= 2e-12. The maximum saved error is 9.1974e-17. The run retains array-temporary warnings for noncontiguous row sections passed to scalar evaluation; bounds checking was not disabled. This verifies selected valid real64 expressions and variable binding, not complete grammar coverage, malformed-input recovery, custom functions, other precisions/ranks or symbolic algebra.

## astro-fortran Galactic/ICRS directions (P)

The independent reference applies three elementary passive rotations sequentially, using the defining pole right ascension 192.85948 degrees, pole declination 27.12825 degrees and node longitude 32.93192 degrees. It does not copy the library matrix or author test body. For ICRS to Galactic it applies z(pi/2+pole_ra), x(pi/2-pole_dec), z(-node); the opposite direction uses the inverse sequence. A passive z rotation maps (x,y) to (cos(a)*x+sin(a)*y,-sin(a)*x+cos(a)*y), with the analogous y,z rule for x rotations.

There are 24 longitude samples, nine latitudes [-90,-75,-45,-10,0,10,45,75,90] degrees, and three longitude shifts [-4*pi,0,6*pi] in each starting frame. The 1,296 direction fixtures exercise 2,592 forward/inverse calls. Every forward output is compared with an independently rotated Cartesian unit vector, and every round trip with its original input vector. Longitude equality at a pole is deliberately not required.

Direct and roundtrip vector discrepancies and unit-norm errors must each be <= 2e-12. Saved maxima are 8.9509e-16, 9.4857e-16 and 2.2204e-16 respectively. Output angles must be finite and within the canonical intervals with an absolute endpoint allowance of 64 real64 machine epsilons. An initial strict [0,2*pi) assertion encountered exactly 2*pi from wrapping a tiny negative angle; the roundoff allowance addresses that equivalent direction without changing vector accuracy checks. No assertion about precession, proper motion, astrometric corrections, unrelated coordinate APIs or physical accuracy of the frame definition follows.

## Sources, licenses and actual output

Pinned implementations and author tests were reviewed before writing these independent API consumers. The drivers have their own MIT notice. Upstream package terms, including astro-fortran's retained SOFA-derived notices, remain separate; the package sources and author test bodies are not relabeled or copied. Loading a driver link does not submit a job.

### feq-expression-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=feq-parse&example=gams-feq-expression-reference) / [Driver source](../fpm_catalog/gams-drivers/feq-expression-reference.f90) / [Pinned procedure](https://github.com/FluidNumerics/feq-parse/blob/2e80c5940b128a52c5070a3f56909674fb85a379/src/FEQParse.f90#L83) / [Author test](https://github.com/FluidNumerics/feq-parse/blob/2e80c5940b128a52c5070a3f56909674fb85a379/example/gaussian_scalar_multivar.f90)

```text
Parsed expressions: 12
Scalar/batch formula references: 16464
Maximum normalized evaluation error:   9.1974E-17
PASS feq-expression-reference
```

### astro-sky-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=astro-fortran&example=gams-astro-sky-reference) / [Driver source](../fpm_catalog/gams-drivers/astro-sky-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/astro-fortran/blob/9d61091d225a1b314ff8170153b06a8691aba283/src/astro_module.f90#L12646) / [Author test](https://github.com/jacobwilliams/astro-fortran/blob/9d61091d225a1b314ff8170153b06a8691aba283/test/t_sofa_f.f90)

```text
Sky direction fixtures: 1296
Forward/inverse conversion calls: 2592
Independent rotation vector references: 1296
Maximum direct vector discrepancy:   8.9509E-16
Maximum roundtrip vector discrepancy:   9.4857E-16
Maximum unit-norm error:   2.2204E-16
PASS astro-sky-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers feq-expression-reference astro-sky-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
