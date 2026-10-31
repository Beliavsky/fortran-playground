# Checked GAMS descriptive-statistics drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [L1a1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L1a1a) | Location of univariate data, demonstrated by real64 means | `stdlib_stats:mean`; `fstats:mean` |
| [L1a1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L1a1b) | Dispersion of univariate data, demonstrated by real64 variances | `stdlib_stats:var`; `fstats:variance` |

These are checked configurations of the named procedures, rather than coverage of all descriptive statistics, distributions or inference. GAMS categories are not exhausted; the [coverage report](gams-coverage.md) tracks remaining procedure-class gaps.

## Shared datasets and independent answers

Let `base=[1,2,3,4,5]`. All four drivers use the same finite real64 datasets:

| Dataset | Mean | Sample variance | Population variance |
| --- | ---: | ---: | ---: |
| `base` | 3 | 2.5 | 2 |
| `1e6+2*base` | 1000006 | 10 | 8 |
| Five copies of `7.25` | 7.25 | 0 | 0 |
| `-3*base` | -9 | 22.5 | 18 |

The references follow directly from the small base dataset and shift/scale identities. The drivers do not obtain their expected answers from the package under test. They require finite results; variances must also be nonnegative. Mean error is `abs(computed-reference)/max(1,abs(reference))`, bounded by `64*epsilon(real64)`. Variance errors use the same scaling and must be at most `1e-12`. The shifted case checks a moderate offset, rather than every numerical-stability regime.

## Sample versus population normalization

Sample variance divides the sum of squared deviations by `N-1`; population variance divides by `N`. The stdlib driver explicitly requests `var(x,corrected=.true.)` and `var(x,corrected=.false.)`, respectively. The fstats API returns sample variance; its driver derives the population value by multiplying by `(N-1)/N`. This conversion is shown explicitly in the code and is not presented as a separate fstats population-variance API.

## Subsets and array dimensions

All four drivers use Fortran `pack` with mask `[T,F,T,F,T]` to select `[1,3,5]`. The known subset mean is 3 and sample variance is 4; these checks use absolute tolerance `1e-12`.

The stdlib drivers also exercise native array masks. The variance driver checks masked population variance `8/3`. For the 5-by-2 matrix with columns `base` and `2*base`, `dim=1` must return means `[3,6]` and sample variances `[2.5,10]`, each within absolute tolerance `1e-12`. All supplemental outputs must be finite. These cases use explicitly selected finite observations.

## Sources and playground links

| Driver | Class | Pinned procedure and author test |
| --- | --- | --- |
| [Load stdlib-mean-checks](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-mean-checks) · [Source](../fpm_catalog/gams-drivers/stdlib-mean-checks.f90) | L1a1a | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L494) · [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_mean.f90) |
| [Load fstats-mean-checks](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-mean-checks) · [Source](../fpm_catalog/gams-drivers/fstats-mean-checks.f90) | L1a1a | [Procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/statistics/fstats_descriptive_statistics.f90#L45) · [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_statistics_tests.f90) |
| [Load stdlib-sample-variance-checks](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-sample-variance-checks) · [Source](../fpm_catalog/gams-drivers/stdlib-sample-variance-checks.f90) | L1a1b | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L1782) · [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_var.f90) |
| [Load fstats-sample-variance-checks](https://beliavsky.github.io/fortran-playground/fpm/?package=fstats&example=gams-fstats-sample-variance-checks) · [Source](../fpm_catalog/gams-drivers/fstats-sample-variance-checks.f90) | L1a1b | [Procedure](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/src/statistics/fstats_descriptive_statistics.f90#L51) · [Author test](https://github.com/jchristopherson/fstats/blob/5fdb86d1e7fa057d776d7d9477942fd6d387dd2f/tests/fstats_statistics_tests.f90) |

The programs adapt author API patterns, retain license notices and use shared deterministic inputs instead of larger test harnesses. The fstats links point to its descriptive-statistics tests. All four appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All four passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only each main and executable were rebuilt. The [verification report](gams-statistics-validation.json) records hashes, pins and saved output. These cases establish selected-data correctness, rather than a general accuracy or speed ranking.

### stdlib-mean-checks

```text
Mean case: 1
Computed mean:   3.00000000000000E+00
Scaled absolute mean error:   0.0000E+00
Mean case: 2
Computed mean:   1.00000600000000E+06
Scaled absolute mean error:   0.0000E+00
Mean case: 3
Computed mean:   7.25000000000000E+00
Scaled absolute mean error:   0.0000E+00
Mean case: 4
Computed mean:  -9.00000000000000E+00
Scaled absolute mean error:   0.0000E+00
Mean of subset [1,3,5]:   3.00000000000000E+00
Column means [base,2*base]:     3.000000000000    6.000000000000
Maximum scaled mean error:   0.0000E+00
PASS stdlib-mean-checks
```

### fstats-mean-checks

```text
Mean case: 1
Computed mean:   3.00000000000000E+00
Scaled absolute mean error:   0.0000E+00
Mean case: 2
Computed mean:   1.00000600000000E+06
Scaled absolute mean error:   1.1641E-16
Mean case: 3
Computed mean:   7.25000000000000E+00
Scaled absolute mean error:   0.0000E+00
Mean case: 4
Computed mean:  -9.00000000000000E+00
Scaled absolute mean error:   0.0000E+00
Mean of subset [1,3,5]:   3.00000000000000E+00
Maximum scaled mean error:   1.1641E-16
PASS fstats-mean-checks
```

### stdlib-sample-variance-checks

```text
Variance case: 1
Sample variance (N-1 denominator):     2.500000000000
Population variance (N denominator):     2.000000000000
Maximum scaled variance error:   0.0000E+00
Variance case: 2
Sample variance (N-1 denominator):    10.000000000000
Population variance (N denominator):     8.000000000000
Maximum scaled variance error:   0.0000E+00
Variance case: 3
Sample variance (N-1 denominator):     0.000000000000
Population variance (N denominator):     0.000000000000
Maximum scaled variance error:   0.0000E+00
Variance case: 4
Sample variance (N-1 denominator):    22.500000000000
Population variance (N denominator):    18.000000000000
Maximum scaled variance error:   0.0000E+00
Sample variance of subset [1,3,5]:     4.000000000000
Column sample variances [base,2*base]:     2.500000000000   10.000000000000
Maximum scaled variance error:   0.0000E+00
PASS stdlib-sample-variance-checks
```

### fstats-sample-variance-checks

```text
Variance case: 1
Sample variance (N-1 denominator):     2.500000000000
Population variance (N denominator):     2.000000000000
Maximum scaled variance error:   2.2204E-16
Variance case: 2
Sample variance (N-1 denominator):    10.000000000000
Population variance (N denominator):     8.000000000000
Maximum scaled variance error:   2.2204E-16
Variance case: 3
Sample variance (N-1 denominator):     0.000000000000
Population variance (N denominator):     0.000000000000
Maximum scaled variance error:   0.0000E+00
Variance case: 4
Sample variance (N-1 denominator):    22.500000000000
Population variance (N denominator):    18.000000000000
Maximum scaled variance error:   0.0000E+00
Sample variance of subset [1,3,5]:     4.000000000000
Maximum scaled variance error:   2.2204E-16
PASS fstats-sample-variance-checks
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-mean-checks fstats-mean-checks stdlib-sample-variance-checks fstats-sample-variance-checks
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
