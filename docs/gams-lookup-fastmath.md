# Checked lookup services and approximate elementary functions

These E3, C4b and C2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-lookup-fastmath-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Lookup location and column services (E3)

A nine-point linear grid spans [-2,2] in steps of 0.5. The first column contains 2*x+1. The second resamples five irregular source points `[-2,-1.25,0.25,1,2]`, with values `(x+1)**2`, onto that grid. Adding a third constant column (7) exercises column reallocation. An independent scalar interval scan and endpoint-clamped linear formula construct the expected stored grid values; the lookup routines do not supply their own references.

After making an independent table copy, additive updates shift the first column by 3 and the second by -0.5. Both tables are queried at 49 points from -3 to 3 in steps of 0.125, totaling 98 queries. Four routes must agree with the independent two-stage reference within 2e-12: scalar and all-column lookups, each directly and through a reusable location object. This checks source resampling followed by table interpolation; off-grid values are not assumed equal to the original quadratic.

Location indices and fractions must stay in bounds, and reconstruct the clamped query coordinate within 1e-12. Grid creation, endpoint and internal knots, clamping on both sides, column addition, additive updates and independence of the old copy are covered. Only linear grid spacing is verified. Quadratic/cubic spacing, extrapolation mode, 2D tables, persistence, invalid inputs and performance are outside this driver. Its E3 service checks do not independently verify the separate E1a mapping.

## Approximate exponential and logarithm (C4b)

For 641 values x=-80..80 in steps of 0.25, fexp(x) is compared with intrinsic exp(x), and flog_quintic(exp(x)) with the known x. Relative exponential error must be at most 1e-4; absolute logarithm error at most 1e-3. The approximate composition fexp(flog_quintic(exp(x))) must recover exp(x) with relative error at most 1.2e-3. Finite outputs, positive exponentials, strict monotonicity on this grid and scalar/array consistency are also required.

These are accuracy checks of approximate functions, not replacements promising intrinsic precision. The saved run reports observed errors, separately from the acceptance tolerances. Overflow/underflow boundaries, subnormal and exceptional arguments, other polynomial/spline variants and speed are not verified.

## Approximate reciprocal square root (C2)

Exactly representable dyadic roots `r=(m/8)*2**k`, m=8..15 and k=-250..250 in steps of 25, supply 168 normal finite squares x=r*r. The independent reference is 1/r, without evaluating sqrt. Relative error in frsqrt(x) must be at most 2e-3, and the normalized equation residual `abs(x*y*y-1)` at most 4e-3. Results must be finite and positive, with scalar/array agreement. The fixture spans many exponents and eight mantissas; it does not establish a universal error bound. Zero, negative, subnormal, infinity/NaN inputs, wrapper variants and performance are not verified.

## Checked links and actual output

These independent API consumers have their own MIT notice. Author examples/tests were reviewed for usage; upstream package licenses remain separate. Loading a link does not submit a job.

### lookup-services-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=lookup-table-fortran&example=gams-lookup-services-reference) / [Driver source](../fpm_catalog/gams-drivers/lookup-services-reference.f90) / [Pinned procedure](https://github.com/jannisteunissen/lookup_table_fortran/blob/b7dc72359e7c2cc105abfbf79b570c655a7f1d04/m_lookup_table.f90#L1) / [Author example/test](https://github.com/jannisteunissen/lookup_table_fortran/blob/b7dc72359e7c2cc105abfbf79b570c655a7f1d04/usage_example.f90)

```text
98 queries: updated and independent copied tables, 3 columns, 4 lookup routes.
Maximum error versus independent two-stage interpolation:   2.2204E-16
Location coordinates, endpoints, clamping, resampling, column addition and updates checked.
PASS lookup-services-reference
```

### fastmath-exp-log-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fastmath&example=gams-fastmath-exp-log-reference) / [Driver source](../fpm_catalog/gams-drivers/fastmath-exp-log-reference.f90) / [Pinned procedure](https://github.com/perazz/fastmath/blob/ad0f14c455205c0e6c1b9300cd7f333fafb750e2/src/fast_exp.f90#L76) / [Author example/test](https://github.com/perazz/fastmath/blob/ad0f14c455205c0e6c1b9300cd7f333fafb750e2/test/test.f90)

```text
641 points x=-80..80 in steps of 0.25; log arguments exp(x).
Maximum exponential relative error versus intrinsic exp:   3.1976E-06
Maximum logarithm absolute error versus x:   2.9987E-04
Maximum approximate exp/log round-trip relative error:   2.9982E-04
Positive exponentials, grid monotonicity and scalar/array consistency checked.
PASS fastmath-exp-log-reference
```

### fastmath-rsqrt-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fastmath&example=gams-fastmath-rsqrt-reference) / [Driver source](../fpm_catalog/gams-drivers/fastmath-rsqrt-reference.f90) / [Pinned procedure](https://github.com/perazz/fastmath/blob/ad0f14c455205c0e6c1b9300cd7f333fafb750e2/src/fast_rsqrt.f90#L55) / [Author example/test](https://github.com/perazz/fastmath/blob/ad0f14c455205c0e6c1b9300cd7f333fafb750e2/test/test.f90)

```text
168 exact dyadic squares: roots (m/8)*2**k, m=8..15, k=-250..250 step 25.
Maximum relative error versus reciprocal of known root:   1.7267E-03
Maximum normalized residual abs(x*y*y-1):   3.4503E-03
Finite positive results and scalar/array consistency checked.
PASS fastmath-rsqrt-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers lookup-services-reference fastmath-exp-log-reference fastmath-rsqrt-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
