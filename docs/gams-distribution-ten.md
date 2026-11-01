# Ten checked stdlib probability-distribution drivers

Ten independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing stdlib libraries were reused; only mains and executables were compiled. The [verification report](gams-distribution-ten-validation.json) saves normalized source hashes, package pins, timings and full output. GAMS categories are not exhausted.

These examples demonstrate probability density functions (PDFs) and cumulative distribution functions (CDFs), not random-number generators. There are 16,669 reference comparisons altogether. Every result must be finite and nonnegative; CDFs must also stay at or below one and be nondecreasing on the ordered grids (monotonicity slack 3e-14).

## Uniform: interval geometry (L5a1u)

Each driver checks 1,625 inputs: five locations, five positive widths and 65 dyadic relative positions from -0.5 to 1.5. The PDF reference is interval membership divided by width. The pinned API includes both endpoints in the density support; endpoint density values are an API convention. The CDF reference is the relative interval length clipped to [0,1]. Scaled absolute tolerance is 4e-15. Integer/complex overloads, invalid widths and other kinds are not covered.

## Normal: high-precision references (L5a1n)

Each driver checks 585 inputs: standardized z=-8..8 by 0.25 at three locations and standard deviations [0.25,1,4]. Independent standard normal PDF/CDF constants were computed with mpmath 1.3.0 at 80 decimal digits and confirmed at 120 digits to absolute difference below 1e-70. The [reference table](gams-distribution-ten-references.json) records arguments and 26-digit values. Density references transform by inverse standard deviation; CDF references remain unchanged. Scaled absolute tolerance is 3e-14. This does not certify relative accuracy in tiny tails, invalid scales, extreme arguments or complex overloads.

## Exponential: scale and rate interfaces (L5a1e)

Each driver makes 1,170 comparisons over 585 inputs: 65 standardized positions z=-0.5..7.5 by 0.125 and nine location/scale pairs. Both the location/scale interface and the shifted zero-location/rate interface are checked against independent 80/120-digit constants. Rate is the reciprocal of scale. The PDF reference is exp(-z)/scale on support; the CDF reference uses high-precision -expm1(-z). Negative support and the boundary are included, with scaled tolerance 3e-14. Invalid parameters, tiny relative tails and other kinds remain unverified.

## Gamma: integer and noninteger shapes (L5a1g)

The PDF driver has 486 references at shapes [1,1.5,2.5,3,5,8]. The CDF driver has 567 references and also includes shape 0.5. Each uses nine standardized positions [-0.25,0,0.125,0.25,0.5,1,2,4,8], three locations and three positive rates [0.25,1,4]. Inputs satisfy z=rate*(x-location); rate is not scale. The independent 80/120-digit unit-rate density/integral constants transform by rate for PDFs and remain unchanged for CDFs. The CDF is the lower incomplete gamma integral divided by gamma(shape). No second stdlib special-function call supplies the oracle.

The shape-one endpoint density equals rate; for larger shapes it is zero. Singular density endpoints for shape below one are deliberately excluded, while the CDF checks shape 0.5 at its boundary. The scaled absolute tolerance is 3e-12, without a relative-tail accuracy claim. Only explicit-location, REAL64 interfaces and bounded parameter scales are verified; optional-default/error overloads and other kinds are not.

## Beta: polynomial references (L5a1b)

Each driver has 4,428 references: 36 integer shape pairs a,b=2..7, three locations and 41 relative positions from -0.125 to 1.125. For the PDF, a finite product supplies 1/B(a,b), multiplied by z**(a-1)*(1-z)**(b-1). For the CDF, an independent binomial tail sum from j=a to a+b-1 gives the regularized probability. These references call neither gamma/log-gamma nor beta/incomplete-beta routines. The shapes above one have continuous zero endpoint densities; outside-support densities vanish and CDFs saturate. Scaled tolerance is 3e-12. Shape-one/singular endpoint conventions, noninteger shapes, invalid parameters and other kinds remain unverified.

## Classification and provenance

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) places univariate PDFs/CDFs in L5a1, with leaves L5a1u (uniform), L5a1n (normal), L5a1e (exponential), L5a1g (gamma) and L5a1b (beta). Some leaf labels include other distributions; these drivers verify only the specifically named stdlib procedures. They do not establish random-sampling quality or performance.

Pinned public APIs, implementations and author tests were reviewed. These independent MIT consumers do not copy upstream implementation or test bodies; upstream license terms remain separate. No numerical source was patched. Loading a driver does not submit a job.

### stdlib-uniform-pdf-reference (L5a1u)

Independent API consumer; pinned sources and author tests reviewed. 1,625 REAL64 interval references across five locations, five positive widths and 65 dyadic relative abscissas from -0.5 to 1.5. Density reference is interval membership divided by interval width; the API includes both endpoints. Scaled absolute tolerance 4e-15 and finite/nonnegative results. Invalid widths, integer/complex overloads, other kinds and random generation unverified.

### stdlib-uniform-cdf-reference (L5a1u)

Independent API consumer; pinned sources and author tests reviewed. 1,625 REAL64 interval references across five locations, five positive widths and 65 dyadic relative abscissas from -0.5 to 1.5. CDF reference is clipped relative interval length; probability bounds and monotonicity also checked. Scaled absolute tolerance 4e-15 and finite/nonnegative results. Invalid widths, integer/complex overloads, other kinds and random generation unverified.

### stdlib-normal-pdf-reference (L5a1n)

Independent API consumer; pinned sources and author tests reviewed. 585 REAL64 references: 65 standardized abscissas -8..8 by 0.25, three locations and three positive standard deviations. Independent mpmath 80-digit constants confirmed at 120 digits. Density constants transform with the inverse scale. Scaled absolute tolerance 3e-14; small tails are not certified to relative accuracy. Finite/nonnegative outputs checked. Invalid scales, complex overloads, other kinds, extreme arguments and random generation unverified.

### stdlib-normal-cdf-reference (L5a1n)

Independent API consumer; pinned sources and author tests reviewed. 585 REAL64 references: 65 standardized abscissas -8..8 by 0.25, three locations and three positive standard deviations. Independent mpmath 80-digit constants confirmed at 120 digits. CDF bounds and monotonicity checked. Scaled absolute tolerance 3e-14; small tails are not certified to relative accuracy. Finite/nonnegative outputs checked. Invalid scales, complex overloads, other kinds, extreme arguments and random generation unverified.

### stdlib-exponential-pdf-reference (L5a1e)

Independent API consumer; pinned sources and author tests reviewed. 1,170 REAL64 comparisons over 585 inputs: z=-0.5..7.5 by 0.125, three locations and three positive scales. Both location/scale and shifted zero-location/rate overloads checked against independent 80/120-digit mpmath references; rate=1/scale. Density reference is exp(-z)/scale on support. Support boundary and negative arguments included. Scaled absolute tolerance 3e-14; tiny relative tails, invalid parameters, complex/other kinds and random generation unverified.

### stdlib-exponential-cdf-reference (L5a1e)

Independent API consumer; pinned sources and author tests reviewed. 1,170 REAL64 comparisons over 585 inputs: z=-0.5..7.5 by 0.125, three locations and three positive scales. Both location/scale and shifted zero-location/rate overloads checked against independent 80/120-digit mpmath references; rate=1/scale. CDF reference uses high-precision -expm1(-z), with bounds and monotonicity checks. Support boundary and negative arguments included. Scaled absolute tolerance 3e-14; tiny relative tails, invalid parameters, complex/other kinds and random generation unverified.

### stdlib-gamma-pdf-reference (L5a1g)

Independent API consumer; pinned sources and author tests reviewed. 486 REAL64 references with shapes [1.0, 1.5, 2.5, 3.0, 5.0, 8.0], three locations, three positive rates and nine standardized abscissas -0.25..8. Independent mpmath density/integral values at 80 digits confirmed at 120; includes noninteger shapes, negative support and x=loc. Shape-one endpoint density is rate; larger-shape endpoint density is zero. Singular density endpoints for shapes below one are deliberately excluded. Scaled absolute tolerance 3e-12; small tails are not certified relatively. Explicit location only; invalid inputs, complex/other kinds, extreme scales and random generation unverified.

### stdlib-gamma-cdf-reference (L5a1g)

Independent API consumer; pinned sources and author tests reviewed. 567 REAL64 references with shapes [0.5, 1.0, 1.5, 2.5, 3.0, 5.0, 8.0], three locations, three positive rates and nine standardized abscissas -0.25..8. Independent mpmath density/integral values at 80 digits confirmed at 120; includes noninteger shapes, negative support and x=loc. CDF normalization is the lower incomplete gamma integral divided by gamma(shape); bounds and monotonicity checked. Scaled absolute tolerance 3e-12; small tails are not certified relatively. Explicit location only; invalid inputs, complex/other kinds, extreme scales and random generation unverified.

### stdlib-beta-pdf-reference (L5a1b)

Independent API consumer; pinned sources and author tests reviewed. 4,428 REAL64 references: shape pairs a,b=2..7, three locations and 41 dyadic abscissas -0.125..1.125 relative to location. Independent finite-product normalization times z**(a-1)*(1-z)**(b-1), without log-gamma/log-beta. Shapes above one give continuous zero endpoint densities. Scaled absolute tolerance 3e-12; no second probability API supplies the oracle. Shape-one/singular endpoint policies, noninteger shapes, invalid parameters, complex/other kinds and random generation unverified.

### stdlib-beta-cdf-reference (L5a1b)

Independent API consumer; pinned sources and author tests reviewed. 4,428 REAL64 references: shape pairs a,b=2..7, three locations and 41 dyadic abscissas -0.125..1.125 relative to location. Independent binomial tail polynomial sum from j=a to a+b-1, with support saturation, probability bounds and monotonicity checks. Scaled absolute tolerance 3e-12; no second probability API supplies the oracle. Shape-one/singular endpoint policies, noninteger shapes, invalid parameters, complex/other kinds and random generation unverified.

## Provenance and actual output

### stdlib-uniform-pdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-uniform-pdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-uniform-pdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_uniform.f90#L57) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_uniform.f90)

```text
Uniform references on and outside 25 shifted intervals, including both endpoints: 1625
PASS stdlib-uniform-pdf-reference
```

### stdlib-uniform-cdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-uniform-cdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-uniform-cdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_uniform.f90#L76) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_uniform.f90)

```text
Uniform references on and outside 25 shifted intervals, including both endpoints: 1625
PASS stdlib-uniform-cdf-reference
```

### stdlib-normal-pdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-normal-pdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-normal-pdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_normal.f90#L43) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_normal.f90)

```text
Normal references from independent 80/120-digit constants, z=-8..8, nine location/scale pairs: 585
PASS stdlib-normal-pdf-reference
```

### stdlib-normal-cdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-normal-cdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-normal-cdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_normal.f90#L56) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_normal.f90)

```text
Normal references from independent 80/120-digit constants, z=-8..8, nine location/scale pairs: 585
PASS stdlib-normal-cdf-reference
```

### stdlib-exponential-pdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-exponential-pdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-exponential-pdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_exponential.f90#L56) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_exponential.f90)

```text
Exponential scale and rate overload references, shifted support and z=-0.5..7.5: 1170
PASS stdlib-exponential-pdf-reference
```

### stdlib-exponential-cdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-exponential-cdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-exponential-cdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_exponential.f90#L80) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_exponential.f90)

```text
Exponential scale and rate overload references, shifted support and z=-0.5..7.5: 1170
PASS stdlib-exponential-cdf-reference
```

### stdlib-gamma-pdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-gamma-pdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-gamma-pdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_gamma.f90#L43) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_gamma.f90)

```text
Gamma references at integer/noninteger shapes, three locations/rates and nine support/tail points: 486
PASS stdlib-gamma-pdf-reference
```

### stdlib-gamma-cdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-gamma-cdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-gamma-cdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_gamma.f90#L62) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_gamma.f90)

```text
Gamma references at integer/noninteger shapes, three locations/rates and nine support/tail points: 567
PASS stdlib-gamma-cdf-reference
```

### stdlib-beta-pdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-beta-pdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-beta-pdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_beta.f90#L37) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_beta.f90)

```text
Shifted beta references for integer shapes 2..7, three locations and 41 support/boundary points: 4428
PASS stdlib-beta-pdf-reference
```

### stdlib-beta-cdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-beta-cdf-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-beta-cdf-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats_distribution_beta.f90#L56) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_distribution_beta.f90)

```text
Shifted beta references for integer shapes 2..7, three locations and 41 support/boundary points: 4428
PASS stdlib-beta-cdf-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-uniform-pdf-reference stdlib-uniform-cdf-reference stdlib-normal-pdf-reference stdlib-normal-cdf-reference stdlib-exponential-pdf-reference stdlib-exponential-cdf-reference stdlib-gamma-pdf-reference stdlib-gamma-cdf-reference stdlib-beta-pdf-reference stdlib-beta-cdf-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
