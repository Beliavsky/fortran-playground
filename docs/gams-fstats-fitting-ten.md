# Ten checked Fstats probability, interpolation and regression drivers

Ten independent REAL64 Fstats consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox, reusing the existing library and compiling only main.f90 and playground-main. The [verification report](gams-fstats-fitting-ten-validation.json) preserves normalized UTF-8/LF source hashes, pins, timings and complete output. GAMS coverage remains unfinished.

## Checked problems

| Driver | GAMS | Independent checks |
| --- | --- | --- |
| Chi-squared positive tails | L5a1c | 30 inputs; five degrees and six positive values |
| F positive tails | L5a1f | 20 inputs; four degree pairs and five positive values |
| Lognormal observation scale | L5a1l | 42 inputs; log-mean/log-scale conventions and nonpositive support |
| Bivariate normal densities | L5b1n | 150 points; explicit 2-by-2 determinant/inverse references |
| Piecewise linear values | E1a | 123 queries and 15 nodes on irregular grids |
| Polynomial interpolation | E1b | 164 queries, degrees 1..4 |
| Global Hermite values and derivatives | E1b | 165 queries, degrees 1..5, supplied first derivatives |
| Linear regression residuals | L8a1a1 | 138 noisy fits, with and without intercept |
| Quadratic regression projections | L8b1b1 | 15 quartic-contaminated fits; independent moment projection |
| Experimental factor coding | L7g | 27 physical/coded coordinates and round trips |

## Probability definitions

The [reference tables](gams-fstats-fitting-ten-references.json) contain 92 parameter/value combinations generated independently with mpmath 1.3.0 at 80 decimal digits and confirmed at 120 digits (absolute differences below 1e-60). Inputs are exact dyadics; references are written with 18 significant digits. Chi-squared uses its defining gamma density and lower/upper incomplete-gamma integrals. F uses its beta normalization and complementary beta-integral definitions. Lognormal uses a Gaussian change of variables: mean_value and standard_deviation describe log(X), while evaluation points are in observation space. Its negative and zero inputs must have zero density/CDF and unit survival.

Each univariate consumer checks PDF, CDF, strict upper survival P(X>x), and finite log density where the reference density is positive. Probability error must be <=2e-9*max(abs(reference),1e-30), so zero references are effectively exact. Other finite scalar/log comparisons use abs(error)<=2e-10*max(1,abs(reference)). Invalid parameters, infinite log outputs, inverse functions, extreme underflow and chi-squared/F support-boundary singularities are excluded.

The bivariate driver uses covariances [[2,rho],[rho,1]] with rho=-1/2,0,1/2, two mean vectors, and 25 dyadic offsets per case. Independent scalar determinants and explicit inverse quadratic forms supply PDF and log-density references, rather than repeating the package Cholesky solve. CDFs, singular/invalid covariances and higher dimensions are not verified.

## Interpolation

Piecewise-linear interpolation uses three irregular-grid data sets, independent segment weights, scalar/vector routes and bounded extrapolation. Polynomial interpolation reproduces explicit polynomials of degrees 1..4 at 41 points each, including bounded extrapolation. These checks do not establish high-degree conditioning or behavior for duplicate/invalid knots.

Global Hermite interpolation uses three irregular nodes with supplied function values and first derivatives, and reproduces polynomials of degrees 1..5 at 33 points each, including derivative evaluation. A fresh object is allocated and released for each polynomial. This is global Hermite polynomial interpolation, not piecewise cubic Hermite. Reinitialization of an existing object failed in the retained probe and is not claimed to work.

## Regression and design coding

The linear consumer uses sizes 3..25 and three dyadic noisy families, with and without an intercept (138 fits). Independent centered-sum or through-origin formulas provide coefficients. It checks every fitted value, the modeled-minus-actual residual convention, and residual orthogonality to the design columns.

The quadratic consumer uses five symmetric grids of 5..13 points and three quadratic signals with a quartic perturbation. An independent 2-by-2 even-moment projection supplies the fitted constant and quadratic coefficient; symmetry supplies the linear coefficient. All 15 fits check coefficients, fitted values, residuals and the three normal-equation orthogonality conditions. These bounded full-rank fits do not verify inference, confidence intervals, weighting, rank-deficient data or high-degree stability.

Experimental factor coding checks nine exact dyadic levels over each of three unequal physical ranges. Both directions are compared with prescribed coordinates, including low/high/midpoint, and then round-tripped. Equal/reversed ranges and invalid shapes are excluded. This is a service routine for experimental designs, not an ANOVA solver.

## Retained unsuccessful probes

The [interpolation reproductions](gams-candidates/fstats-interpolation/README.md) preserve exact consumers, hashes, pins and full hosted results. The clamped cubic spline failed an independent irregular-grid cubic value check; it has no published checked driver. The initial Hermite consumer hit an allocation error when reinitializing the same object. Fresh-object consumers passed all original numerical assertions. No upstream numerical code was patched and tolerances were not relaxed.

## Provenance

Pinned implementations and linked author distribution, interpolation, regression and experimental-design tests informed API usage. These are independent MIT consumers; no author test or implementation bodies were copied. Classifications follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). No backend redeployment or package-library rebuild is needed.

## Driver details

### fstats-chi-squared-positive-tails-reference (L5a1c)

Independent API consumer. 30 REAL64 distribution inputs. Five positive degrees and six positive abscissae, with gamma-integral definitions. Support boundary x=0 and singular densities excluded. PDF/PMF, CDF, strict upper survival and finite log-density checked with independent 80/120 digit references. Probability relative tolerance 2e-9 with floor 1e-30; invalid parameters and infinite log values excluded.

### fstats-f-positive-tails-reference (L5a1f)

Independent API consumer. 20 REAL64 distribution inputs. Four degree pairs and five positive abscissae; independent beta-integral definitions. Moments and support boundary excluded. PDF/PMF, CDF, strict upper survival and finite log-density checked with independent 80/120 digit references. Probability relative tolerance 2e-9 with floor 1e-30; invalid parameters and infinite log values excluded.

### fstats-lognormal-observation-scale-reference (L5a1l)

Independent API consumer. 42 REAL64 distribution inputs. Log-mean -1,0,1 and log-standard-deviation 1/2,2; seven observation-scale values include negative and zero support checks. Positive values use Gaussian change of variables. PDF/PMF, CDF, strict upper survival and finite log-density checked with independent 80/120 digit references. Probability relative tolerance 2e-9 with floor 1e-30; invalid parameters and infinite log values excluded.

### fstats-piecewise-linear-values-reference (E1a)

Independent API consumer. Three irregular-grid data sets, 41 queries each including extrapolation, scalar and vector APIs. Independent segment weights; exact nodes included. Increasing grids only, invalid/duplicate knots excluded.

### fstats-polynomial-interpolation-values-reference (E1b)

Independent API consumer. Degrees 1..4 on five irregular knots, 41 queries each including bounded extrapolation. Known polynomial reproduction and scalar/vector agreement; no ill-conditioned high-degree claim.

### fstats-hermite-values-derivatives-reference (E1b)

Independent API consumer. Degree 1..5 global Hermite polynomials with values and supplied first derivatives at three irregular nodes; 33 queries each. Checks values and derivatives against explicit polynomial sums. This is global Hermite interpolation, not piecewise cubic; estimated derivatives excluded. Fresh object for each degree; reinitialization fails in retained probe docs/gams-candidates/fstats-interpolation/.

### fstats-linear-regression-residuals-reference (L8a1a1)

Independent API consumer. Sizes 3..25 and three noisy dyadic data sets, with and without intercept: 138 fits. Independent centered-sum or origin-constrained coefficients, fitted values, modeled-minus-actual residuals and normal-equation orthogonality checked. No confidence intervals, weighting or rank-deficient cases.

### fstats-quadratic-regression-projections-reference (L8b1b1)

Independent API consumer. Five symmetric grids (5..13 points), three quartic-contaminated quadratic families: 15 fits. Independent even-moment 2-by-2 projection gives coefficients, while odd symmetry supplies linear coefficient. Fitted values, residual convention and three orthogonality equations checked. Bounded full-rank quadratic fits only.

### fstats-experimental-factor-coding-reference (L7g)

Independent API consumer. Three independent physical factor ranges at nine prescribed coded levels -1..1. Checks both affine directions against exact dyadic coordinates and round trips, with low/high/midpoint included. Equal/reversed ranges and invalid dimensions excluded.

### fstats-bivariate-normal-densities-reference (L5b1n)

Independent API consumer. Three positive-definite 2-by-2 covariances (negative, zero and positive correlation), two means, 25 offsets each: 150 PDF and log-density checks. Independent scalar determinant and explicit 2-by-2 inverse quadratic form. Invalid covariances, CDFs and higher dimensions excluded.

## Provenance and actual output

### fstats-chi-squared-positive-tails-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-chi-squared-positive-tails-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-chi-squared-positive-tails-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/distributions/fstats_chi_squared_distribution.f90#L35) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_distribution_tests.f90)

```text
Independent distribution reference cases: 30
PASS fstats-chi-squared-positive-tails-reference
```

### fstats-f-positive-tails-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-f-positive-tails-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-f-positive-tails-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/distributions/fstats_f_distribution.f90#L35) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_distribution_tests.f90)

```text
Independent distribution reference cases: 20
PASS fstats-f-positive-tails-reference
```

### fstats-lognormal-observation-scale-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-lognormal-observation-scale-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-lognormal-observation-scale-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/distributions/fstats_log_normal_distribution.f90#L35) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_distribution_tests.f90)

```text
Independent distribution reference cases: 42
PASS fstats-lognormal-observation-scale-reference
```

### fstats-piecewise-linear-values-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-piecewise-linear-values-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-piecewise-linear-values-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/interpolation/fstats_interp.f90#L464) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_interp_tests.f90)

```text
123 irregular-grid piecewise-linear queries and 15 nodes checked.
PASS fstats-piecewise-linear-values-reference
```

### fstats-polynomial-interpolation-values-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-polynomial-interpolation-values-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-polynomial-interpolation-values-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/interpolation/fstats_interp.f90#L576) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_interp_tests.f90)

```text
164 polynomial queries, degrees 1 through 4, checked.
PASS fstats-polynomial-interpolation-values-reference
```

### fstats-hermite-values-derivatives-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-hermite-values-derivatives-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-hermite-values-derivatives-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/interpolation/fstats_interp.f90#L979) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_interp_tests.f90)

```text
165 global Hermite values and first derivatives independently checked.
PASS fstats-hermite-values-derivatives-reference
```

### fstats-linear-regression-residuals-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-linear-regression-residuals-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-linear-regression-residuals-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/regression/fstats_linear_regression.f90#L14) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_regression_tests.f90)

```text
138 noisy linear fits, coefficients, residuals and orthogonality checked.
PASS fstats-linear-regression-residuals-reference
```

### fstats-quadratic-regression-projections-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-quadratic-regression-projections-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-quadratic-regression-projections-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/regression/fstats_linear_regression.f90#L14) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_regression_tests.f90)

```text
15 noisy quadratic projections and normal-equation residuals checked.
PASS fstats-quadratic-regression-projections-reference
```

### fstats-experimental-factor-coding-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-experimental-factor-coding-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-experimental-factor-coding-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/design/fstats_doe_coding.f90#L11) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_experimental_design_tests.f90)

```text
27 experimental factor coordinates: encoding, decoding and round trips checked.
PASS fstats-experimental-factor-coding-reference
```

### fstats-bivariate-normal-densities-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-bivariate-normal-densities-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-bivariate-normal-densities-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/distributions/fstats_multivariate_normal_distribution.f90#L58) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_distribution_tests.f90)

```text
150 bivariate normal PDF and log-density values independently checked.
PASS fstats-bivariate-normal-densities-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fstats-chi-squared-positive-tails-reference fstats-f-positive-tails-reference fstats-lognormal-observation-scale-reference fstats-piecewise-linear-values-reference fstats-polynomial-interpolation-values-reference fstats-hermite-values-derivatives-reference fstats-linear-regression-residuals-reference fstats-quadratic-regression-projections-reference fstats-experimental-factor-coding-reference fstats-bivariate-normal-densities-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
