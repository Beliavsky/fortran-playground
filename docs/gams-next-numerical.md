# Six checked drivers from the numerical coverage audit

All six ranked candidates passed GNU Fortran 16.2.0 / FPM 0.12.0 in the hosted sandbox, reusing the existing package libraries and compiling only main.f90 and playground-main. The [verification report](gams-next-numerical-validation.json) preserves exact package pins, normalized UTF-8/LF source hashes, timings and complete output. The [coverage audit](gams-driver-audit.md) now removes these completed candidates from its pending list. GAMS coverage remains unfinished.

## Checked problems

| Driver | GAMS | Independent checks |
| --- | --- | --- |
| nonlin BFGS, finite differences | G1b1a | 12 coupled SPD quadratics and three Rosenbrock starts |
| nonlin least squares, finite differences | G1b1a | 24 exact exponential fits without a registered Jacobian |
| RPN signed real cube roots | C2 | 55 zero, signed dyadic cube and noncube references |
| RPN modified Bessel I0 | C10 | 29 values, signs, tiny inputs and branch-15 neighbors |
| fortranlib tabulated interpolation | E1 | 207 scalar/vector queries on irregular knots and explicit fill values |
| fortranlib tabulated integration | H2 | 198 clipped intervals and three full integrals |

## Finite-difference optimization configurations

The BFGS consumer registers only an objective callback. Twelve coupled positive-definite quadratic problems cover dimensions 2..5 with three starts each, and three further starts solve Rosenbrock. Independent known minimizers, explicit objective and analytic stationarity formulas, reported-objective agreement and normal termination flags are required. Maximum normalized parameter error is bounded by 5e-5, objective by 2e-9 and gradient infinity norm by 2e-5; reported objective agreement is 1e-12 absolute. These are correctness checks, not global convergence or performance guarantees.

The residual-only least-squares consumer registers no Jacobian and requires its analytic callback count to remain zero. It keeps the same 24 exact exponential fixtures and explicit step factor 1 as the separately checked analytic-Jacobian driver. Independent model formulas check the known parameters (normalized tolerance 2e-7), returned residuals (1e-11 consistency), exact-fit residual infinity norm (1e-8), squared residual norm (1e-10) and analytic J-transpose-residual (1e-6). The independently computed stationarity Jacobian is also checked by central differences at the starting points; it is never supplied to the solver.

The [retained nonlin least-squares failures](gams-candidates/nonlin-least-squares/README.md) with default step factor and nonzero-residual families remain unresolved. Passing the exact-fit family in another derivative mode does not verify those cases. No stopping rule, library implementation or tolerance was patched to make this batch pass.

## Elementary and special functions

The [reference tables](gams-next-numerical-references.json) contain exact rational inputs and 18-significant-digit outputs generated with mpmath 1.3.0 at 80 and 120 decimal digits. Definitions agree within 1e-50*max(1,abs(reference)). The consumer requires the package kind to equal REAL64 and finite relative error <=2e-12 with a reference floor of 1e-100.

Cube roots include 42 signed exact cubes from dyadic roots at exponents -30..30 (input exponents around -90..90), zero and 12 additional signed noncube-family inputs. Checks compare high-precision real cube roots, signs and cube reconstruction. Some additional inputs are themselves exact cubes; no complex-root or subnormal claim is made.

Unscaled modified Bessel I0 uses 29 signed inputs through 64, including zero, tiny dyadics, and 15-1/1024,15,15+1/1024 on both signs around the pinned implementation branch. Positivity and evenness are checked. Independent high-precision Bessel definitions supply the values; separate Decimal-series tests check the recorded constants. Scaled Bessel functions, overflow and arbitrary extreme arguments are excluded.

## Tabulated interpolation and integration

Both consumers use five irregular knots [-2,-3/4,0,1/2,2] and three deterministic signed value sets. Interpolation checks 65 in-domain queries and four outside queries per set, for 207 scalar/vector comparisons. Independent segment weights supply the interior references; the caller explicitly requests bounds_error=false and fill_value=-123. Outside values are filled, not extrapolated. Increasing grids only; duplicate/descending knots and log interpolants are excluded.

Integration checks every ordered pair from eleven limits (-3..3), including equal, same-segment, partial, outside and clipped intervals, for 198 subset integrals plus three full-domain integrals. Independent polynomial antiderivatives are integrated over the clipped overlap of each segment. These are areas under the piecewise-linear tabulated interpolant, not exact quadrature of an arbitrary underlying nonlinear function. Reversed limits and non-linear interpolant variants are excluded. Both consumers use absolute-scaled error <=2e-12*max(1,abs(reference)).

The cached fortranlib image already contains the checksum-locked upstream lib_array fixes recorded in the catalog (matching upstream 844611933cba06d71490033e68b355f6f0ff704f). Those adaptations, dependency pins, images and build report are unchanged. This batch adds consumers only; it does not apply new package edits.

## Classification, provenance and maintenance

Six separate records now identify the finite-difference modes and the individual cube-root, Bessel, interpolation and integration APIs. Their classes have been removed from the older composite records, which retain their existing analytic-gradient, sinc/sech, beta and quadratic drivers. This avoids leaving fulfilled claims in the audit or suggesting one driver validates a different mode. There are now 509 checked drivers and 536 mapped procedure records; 27 records still have no dedicated checked driver.

Pinned implementations and recorded author examples/tests informed API usage. These are independent MIT consumers, including reuse of the playground-owned exact-fit fixture in a distinct solver configuration. Loading a driver submits no job. No backend redeployment or library rebuilding is needed.

## Driver details

### nonlin-bfgs-finite-differences-reference (G1b1a)

Independent API consumer. 15 REAL64 minimizations: 12 coupled positive-definite quadratics of sizes 2..5 and three Rosenbrock starts. No gradient callback registered. Independent known minimizers, objective values, analytic stationarity, reported objective and termination flags checked. Parameter tolerance 5e-5, objective 2e-9 and gradient 2e-5. Not a benchmark or global-convergence claim.

### nonlin-lsq-finite-differences-reference (G1b1a)

Independent API consumer. 24 exact exponential fits with step factor 1 and no registered residual Jacobian. Same independent parameters, residual norm, returned residual consistency and analytic stationarity as the checked analytic-Jacobian family. Numerical parameter tolerance 2e-7; exact-fit residual 1e-8. Analytic callback invocation count must stay zero. Known default-step and noisy-fit failures remain unverified; see docs/gams-candidates/nonlin-least-squares/README.md.

### rpn-real-cube-roots-reference (C2)

Independent API consumer. 55 REAL64 values, independent 80/120 digit definitions and 18-digit constants. Signed dyadic cubes spanning input exponents -90..90, zero and noncubes; signs and cube reconstruction. Complex and subnormal roots excluded. Relative tolerance 2e-12 with floor 1e-100; no upstream source changes.

### rpn-bessel-i0-values-reference (C10)

Independent API consumer. 29 REAL64 values, independent 80/120 digit definitions and 18-digit constants. Signed arguments through 64, zero, tiny dyadics and values either side of branch 15; positivity and evenness. Unscaled I0 only; overflow and scaled functions excluded. Relative tolerance 2e-12 with floor 1e-100; no upstream source changes.

### fortranlib-linear-interpolation-reference (E1)

Independent API consumer. 207 scalar/vector queries over three irregular-grid data sets; exact knots, segment weights and explicit out-of-domain fill values. Independent segment interpolation, absolute-scaled tolerance 2e-12. Increasing knots and explicit nonfatal bounds mode only; descending/duplicate grids and other interpolants excluded. Existing catalog lib_array upstream fixes remain unchanged.

### fortranlib-tabulated-integrals-reference (H2)

Independent API consumer. 198 ordered intervals plus three full integrals on three five-knot irregular-grid data sets. Independent piecewise polynomial antiderivatives, clipped domain, same-segment/empty/outside/partial/full intervals and signed areas. Tolerance 2e-12*max(1,abs(reference)). Reversed limits and non-linear interpolation variants excluded. Uses existing pinned upstream lib_array integration fixes; no new package edits.

## Provenance and actual output

### nonlin-bfgs-finite-differences-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nonlin&example=gams-nonlin-bfgs-finite-differences-reference) / [Driver source](../fpm_catalog/gams-drivers/nonlin-bfgs-finite-differences-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_optimize.f90#L584) / [Author test](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_bfgs_example.f90)

```text
Finite-difference BFGS fits with no gradient callback: 15
Worst normalized parameter / independent gradient errors:    8.96291E-06   5.97998E-06
PASS nonlin-bfgs-finite-differences-reference
```

### nonlin-lsq-finite-differences-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nonlin&example=gams-nonlin-lsq-finite-differences-reference) / [Driver source](../fpm_catalog/gams-drivers/nonlin-lsq-finite-differences-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_least_squares.f90#L141) / [Author test](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_least_squares_example.f90)

```text
Total / exact-fit solves:    24   24
Independent stationarity Jacobian entries checked at starting points: 240
Maximum normalized parameter error:   1.1102E-16
Maximum normalized Jacobian finite-difference error:   4.1373E-11
Maximum absolute J-transpose-residual component:   5.7772E-15
PASS nonlin-lsq-finite-differences-reference
```

### rpn-real-cube-roots-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran&example=gams-rpn-real-cube-roots-reference) / [Driver source](../fpm_catalog/gams-drivers/rpn-real-cube-roots-reference.f90) / [Pinned procedure](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/src/funcs.f90#L229) / [Author test](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/test/test.f90)

```text
Independent high precision reference points: 55
PASS rpn-real-cube-roots-reference
```

### rpn-bessel-i0-values-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran&example=gams-rpn-bessel-i0-values-reference) / [Driver source](../fpm_catalog/gams-drivers/rpn-bessel-i0-values-reference.f90) / [Pinned procedure](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/src/specfun/i0.f#L1) / No pinned author example; API reviewed directly.

```text
Independent high precision reference points: 29
PASS rpn-bessel-i0-values-reference
```

### fortranlib-linear-interpolation-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-linear-interpolation-reference) / [Driver source](../fpm_catalog/gams-drivers/fortranlib-linear-interpolation-reference.f90) / [Pinned procedure](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L1) / No pinned author example; API reviewed directly.

```text
Irregular-grid scalar/vector queries including fill values: 207
PASS fortranlib-linear-interpolation-reference
```

### fortranlib-tabulated-integrals-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-tabulated-integrals-reference) / [Driver source](../fpm_catalog/gams-drivers/fortranlib-tabulated-integrals-reference.f90) / [Pinned procedure](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L1) / No pinned author example; API reviewed directly.

```text
Clipped piecewise-linear area intervals plus three full integrals: 198
PASS fortranlib-tabulated-integrals-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers nonlin-bfgs-finite-differences-reference nonlin-lsq-finite-differences-reference rpn-real-cube-roots-reference rpn-bessel-i0-values-reference fortranlib-linear-interpolation-reference fortranlib-tabulated-integrals-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
