# Ten checked Fstats summaries, distributions and design drivers

Ten independent REAL64 Fstats consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. The cached library was reused; only main.f90 and playground-main were compiled. The [verification report](gams-fstats-summaries-ten-validation.json) retains normalized UTF-8/LF source hashes, exact pins, timings and complete output. GAMS coverage remains unfinished.

## Checked problems

| Driver | GAMS | Independent checks |
| --- | --- | --- |
| Median and quantile conventions | L1a1a | 99 data sets; median and seven clamped (n+1)*q quantiles |
| Trimmed locations | L1a1a | 99 data sets at three per-tail fractions; subset means and in-place sorting |
| Paired covariances | L1c1b | 96 paired data sets; centered sums, symmetry and affine relation |
| Raw median deviations | L1a1b | 99 data sets; median of absolute distances from an independent median |
| Pooled group variances | L1a1b | 15 summaries of 2..6 groups; explicit degrees-of-freedom weighting |
| Normal tail functions | L5a1n | 66 inputs; PDF, CDF, survival and finite log density |
| Binomial boundaries | L5a1b | 165 inputs; degenerate parameters, complete integer support and adjacent outside values |
| Poisson tail functions | L5a1p | 35 inputs; five rates including zero, integer support and tails |
| Student t finite values | L5a1t | 44 inputs; degrees 1,2,5,10 and signed values -8..8 |
| Full factorial designs | L7f | 12 designs; exact dimensions, Cartesian coverage and marginal/pairwise balance |

## Summaries and conventions

The four raw-data summary drivers use three deterministic affine dyadic families at sizes 1..33 (covariance starts at n=2). Local insertion sorting supplies independent references. Median averages the central pair for even sizes. Quantiles explicitly use the plotting position (n+1)*q, linear interpolation and endpoint clamping, with q=0,0.1,0.25,0.5,0.75,0.9,1; method numbering is not relied upon.

Trimmed means remove floor(n*p) entries from each end for p=0,1/8,1/4. The consumer also checks the documented in-place sorting of its work array. Covariances use explicit centered cross-products divided by n-1, plus argument symmetry and covariance(x,2*x+1)=2*sample_variance(x). MAD is the raw median absolute deviation, with no normal-consistency scaling. Pooled variance uses supplied sample variances and sample counts with weights n_i-1; raw-container and column overloads are not verified.

Summary and finite log-density comparisons require finite results and abs(actual-reference)<=2e-10*max(1,abs(reference)). Empty arrays, nonfinite data, invalid trimming/quantile parameters, constant/near-overflow robustness and missing-value policies are not established by these bounded tests.

## Probability references and tails

The [reference table](gams-fstats-summaries-ten-references.json) records every distribution parameter, evaluation point, PDF/PMF, CDF and survival value. References were generated independently with mpmath 1.3.0 at 80 decimal digits, confirmed at 120 digits with absolute differences below 1e-60, and written as 18-significant-digit constants. Inputs are exact dyadics. Every probability must be finite and satisfy abs(actual-reference)/max(abs(reference),1e-30)<=2e-9. Exact zero references are effectively checked exactly. Finite log densities are checked against log of the independently referenced positive density; infinite log values are not requested.

Normal cases use means -1,0,1, standard deviations 1/2,2, and eleven standardized offsets from -6 to 6. PDF references use the defining Gaussian exponential and CDF/survival use high-precision complementary error functions. Binomial cases use n=0,1,2,5,10, p=0,1/8,1/2,7/8,1 and every integer k=-1..n+1; independent finite binomial sums test both support boundaries and degenerate p=0/1 or n=0.

Poisson rates are 0,1/8,1/2,2,8 at k=-1,0,1,2,4,8,12. PMF and CDF references use the defining exponential/factorial finite sums, retaining tails in high precision rather than subtracting rounded REAL64 CDFs. Student t degrees are 1,2,5,10 at eleven signed arguments -8..8, using high-precision gamma/beta definitions. Separate tests check the degree-1 Cauchy and degree-2 closed forms. All survival functions represent the strict upper tail P(X>x), including discrete distributions. Undefined low-degree moments, invalid parameters, fractional discrete inputs, extreme-tail underflow and inverse distributions are excluded.

## Experimental designs

The full-factorial consumer uses 1..4 factors with 1..4 levels, twelve combinations of factor count and level pattern. It checks dimensions against an independent product, all legal levels, unique mixed-radix keys spanning the entire Cartesian product, and exact marginal and pairwise level counts. It does not prescribe row ordering. Huge designs, fractional factorials, model fitting and statistical optimality are excluded.

## Provenance and maintenance

Pinned public APIs, implementations and linked author statistics/distribution/experimental-design tests were reviewed. Those tests informed API conventions; these drivers are independent MIT consumers and copy no implementation or author-test bodies. No upstream code was patched. Classifications follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). Loading a driver does not submit a job. The [coverage report](gams-coverage.md) records remaining work.

## Driver details

### fstats-median-quantile-conventions-reference (L1a1a)

Independent API consumer. 99 data sets n=1..33. Median and seven quantiles checked against independently sorted values with clamped (n+1)*q interpolation, with the mathematical convention stated explicitly rather than relying on method numbering. Nonfinite/empty inputs and other quantile conventions excluded.

### fstats-trimmed-locations-reference (L1a1a)

Independent API consumer. 99 data sets n=1..33 and per-tail fractions 0,1/8,1/4. Explicit sorted-subset means and documented in-place sorting checked. Invalid fractions and missing data excluded.

### fstats-paired-covariances-reference (L1c1b)

Independent API consumer. 96 paired data sets n=2..33; explicit centered cross-products, argument symmetry and covariance of x with 2*x+1 checked. Sample normalization n-1 only; nonfinite and unequal-length inputs excluded.

### fstats-raw-median-deviations-reference (L1a1b)

Independent API consumer. 99 data sets n=1..33. Raw, unscaled MAD checked by independently sorting absolute distances from the independently computed median. No normal-consistency multiplier, missing data or overflow-limit claim.

### fstats-pooled-group-variances-reference (L1a1b)

Independent API consumer. Fifteen summaries of 2..6 groups with three scaling choices. Pooled sample variance compared with explicit degrees-of-freedom weighted sums. Summary-variance overload only; raw array-container/column overloads and invalid group sizes excluded.

### fstats-normal-tail-functions-reference (L5a1n)

Independent API consumer. 66 REAL64 distribution inputs. Normal locations -1,0,1, scales 1/2,2 and standardized offsets -6..6. PDF/PMF, CDF, strict upper survival and finite log-density checked with independent 80/120 digit references. Probability relative tolerance 2e-9 with floor 1e-30; invalid parameters and infinite log values excluded.

### fstats-binomial-boundaries-reference (L5a1b)

Independent API consumer. 165 REAL64 distribution inputs. Trials n=0,1,2,5,10; probabilities 0,1/8,1/2,7/8,1; every integer k=-1..n+1 including support and degenerate boundaries. PDF/PMF, CDF, strict upper survival and finite log-density checked with independent 80/120 digit references. Probability relative tolerance 2e-9 with floor 1e-30; invalid parameters and infinite log values excluded.

### fstats-poisson-tail-functions-reference (L5a1p)

Independent API consumer. 35 REAL64 distribution inputs. Rates 0,1/8,1/2,2,8; integer k=-1,0,1,2,4,8,12, with high precision finite PMF sums and independently retained tails. PDF/PMF, CDF, strict upper survival and finite log-density checked with independent 80/120 digit references. Probability relative tolerance 2e-9 with floor 1e-30; invalid parameters and infinite log values excluded.

### fstats-student-t-finite-values-reference (L5a1t)

Independent API consumer. 44 REAL64 distribution inputs. Student t degrees 1,2,5,10 at eleven signed dyadic values -8..8. Only function evaluation; undefined low-degree moments are not requested. PDF/PMF, CDF, strict upper survival and finite log-density checked with independent 80/120 digit references. Probability relative tolerance 2e-9 with floor 1e-30; invalid parameters and infinite log values excluded.

### fstats-full-factorial-designs-reference (L7f)

Independent API consumer. Twelve full factorial designs with 1..4 factors and 1..4 levels. Independent dimensions, all legal levels, unique mixed-radix keys covering the full Cartesian product, and exact marginal/pairwise level balance checked. Row order not prescribed; huge designs and fractional factorials excluded.

## Provenance and actual output

### fstats-median-quantile-conventions-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-median-quantile-conventions-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-median-quantile-conventions-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/statistics/fstats_descriptive_statistics.f90#L227) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_statistics_tests.f90)

```text
Three finite dyadic data families, lengths through 33, independently checked.
PASS fstats-median-quantile-conventions-reference
```

### fstats-trimmed-locations-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-trimmed-locations-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-trimmed-locations-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/statistics/fstats_descriptive_statistics.f90#L323) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_statistics_tests.f90)

```text
Three finite dyadic data families, lengths through 33, independently checked.
PASS fstats-trimmed-locations-reference
```

### fstats-paired-covariances-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-paired-covariances-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-paired-covariances-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/statistics/fstats_descriptive_statistics.f90#L360) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_statistics_tests.f90)

```text
Three finite dyadic data families, lengths through 33, independently checked.
PASS fstats-paired-covariances-reference
```

### fstats-raw-median-deviations-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-raw-median-deviations-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-raw-median-deviations-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/statistics/fstats_robust_statistics.f90#L45) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_statistics_tests.f90)

```text
Three finite dyadic data families, lengths through 33, independently checked.
PASS fstats-raw-median-deviations-reference
```

### fstats-pooled-group-variances-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-pooled-group-variances-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-pooled-group-variances-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/statistics/fstats_descriptive_statistics.f90#L411) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_statistics_tests.f90)

```text
15 pooled-variance summaries independently checked.
PASS fstats-pooled-group-variances-reference
```

### fstats-normal-tail-functions-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-normal-tail-functions-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-normal-tail-functions-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/distributions/fstats_normal_distribution.f90#L35) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_distribution_tests.f90)

```text
Independent distribution reference cases: 66
PASS fstats-normal-tail-functions-reference
```

### fstats-binomial-boundaries-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-binomial-boundaries-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-binomial-boundaries-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/distributions/fstats_binomial_distribution.f90#L35) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_distribution_tests.f90)

```text
Independent distribution reference cases: 165
PASS fstats-binomial-boundaries-reference
```

### fstats-poisson-tail-functions-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-poisson-tail-functions-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-poisson-tail-functions-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/distributions/fstats_poisson_distribution.f90#L35) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_distribution_tests.f90)

```text
Independent distribution reference cases: 35
PASS fstats-poisson-tail-functions-reference
```

### fstats-student-t-finite-values-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-student-t-finite-values-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-student-t-finite-values-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/distributions/fstats_t_distribution.f90#L35) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_distribution_tests.f90)

```text
Independent distribution reference cases: 44
PASS fstats-student-t-finite-values-reference
```

### fstats-full-factorial-designs-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-full-factorial-designs-reference) / [Driver source](../fpm_catalog/gams-drivers/fstats-full-factorial-designs-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/design/fstats_doe_designs.f90#L44) / [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_experimental_design_tests.f90)

```text
12 full-factorial designs: Cartesian coverage and level balance checked.
PASS fstats-full-factorial-designs-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fstats-median-quantile-conventions-reference fstats-trimmed-locations-reference fstats-paired-covariances-reference fstats-raw-median-deviations-reference fstats-pooled-group-variances-reference fstats-normal-tail-functions-reference fstats-binomial-boundaries-reference fstats-poisson-tail-functions-reference fstats-student-t-finite-values-reference fstats-full-factorial-designs-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
