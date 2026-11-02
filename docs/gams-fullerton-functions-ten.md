# Ten checked Fullerton special-function drivers

Ten independent specfunc-fullerton drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. The existing package library was reused; only each main and executable were compiled. The [verification report](gams-fullerton-functions-ten-validation.json) saves normalized UTF-8/LF source hashes, the exact package pin, timings and complete output. GAMS categories are not exhausted.

## Precision and independent references

The pinned APIs accept and return default REAL32. The drivers use exact dyadic input arguments, convert them to that kind for each call, and widen the returned values solely for checking. This does not supply REAL64 accuracy. References were generated independently with mpmath 1.3.0 at 80 decimal digits and confirmed at 120 digits with absolute differences below 1e-60. The [reference table](gams-fullerton-functions-ten-references.json) records every API, argument, integer order where applicable, and 18-significant-digit expected value.

Every returned value must be finite and satisfy abs(actual-reference)/max(abs(reference),1e-30)<=5e-5. The small floor makes the exact zero cases effectively exact checks without relaxing relative accuracy for tiny nonzero results. Each driver reports its actual maximum relative error under this convention. These bounded checks are not a precision or performance benchmark, and do not establish accuracy near excluded function zeros, singularities, overflow or underflow.

## Checked APIs and problem classes

| Driver | GAMS | Checked cases |
| --- | --- | --- |
| Airy values and derivatives | C10d | 56 Ai, Bi, Ai-prime and Bi-prime comparisons at 14 dyadics in [-8,8] |
| Modified Bessel I0/I1 | C10b1 | 36 comparisons at 18 signed dyadics in [-16,16], including zero |
| Modified Bessel K0/K1 | C10b1 | 18 comparisons at nine positive dyadics from 1/256 to 16 |
| Exponential/logarithmic integrals | C5 | 15 real Ei and 10 real li comparisons, avoiding their singular arguments |
| Positive exponential integrals | C5 | Nine E1 values and 20 En values, with n=1..5 |
| Sine/cosine integrals | C6 | 18 positive-argument Si/Ci comparisons |
| Hyperbolic integrals | C4d | 20 positive-argument Shi/Chi comparisons, including x=3/8 |
| Dawson values and derivatives | C8c | 28 signed-argument value/first-derivative comparisons in [-8,8] |
| Real dilogarithm | C5 | 12 Li2 comparisons on [-8,1], including zero and one |
| Near-zero exponential/logarithm | C4b | 38 log1p/exprel comparisons, including tiny arguments and zero limits |

## Definitions and scope

**Airy functions:** both function values and first derivatives are compared directly with high-precision Airy references. Samples include oscillatory negative arguments and decaying/growing positive arguments, along with zero. Complex/scaled variants and arguments near function zeros are excluded. Independent tests check the ODE power series on a bounded subset, exact zero-argument gamma formulas and the Wronskian identity using the saved values.

**Modified Bessel functions:** the I0/I1 driver includes both signs, testing the even/odd conventions, while K0/K1 uses strictly positive arguments. Relative comparisons retain sensitivity for the small exponentially decaying K values. Only orders zero and one are verified. The separate bessel_in/bessel_kn higher-order wrappers, fractional-order routines, scaled functions and extreme-range behavior are not promoted by these results. Independent tests reconstruct I0/I1 with their power series and check K0/K1 using their defining positive quadrature integral.

**Ei, li and En:** Ei uses the real principal-value branch on nonzero real arguments. li(x) is the unoffset logarithmic integral Ei(log(x)), not the offset integral starting at 2; x=1 is excluded. E1 and En use integral_1^infinity exp(-x*t)/t**n dt for positive x. E1 is checked on nine dyadics 1/256..16; En is checked for n=1..5 at x=1/8,1/2,1,2. No conclusion is drawn about the higher-order forward recurrence at larger x. Independent tests use exponential-integral power series on a bounded subset and the En integration-by-parts recurrence.

**Si/Ci and Shi/Chi:** Si(x)=integral_0^x sin(t)/t dt, while Ci(x)=EulerGamma+log(x)+integral_0^x (cos(t)-1)/t dt on the positive real domain. The hyperbolic counterparts replace sin/cos by sinh/cosh. Chi and Ci are tested only for positive arguments, with no complex-continuation claim. Independent tests use the corresponding power series on a bounded subset.

**Dawson:** F(x)=sqrt(pi)*exp(-x*x)*erfi(x)/2. The high-precision derivative reference is obtained by differentiating this definition with mpmath, rather than by reusing the package derivative. Independent tests also check F-prime+2*x*F=1 and the ODE power series for bounded arguments. Extreme asymptotics and derivative zeros are excluded.

**Spence/dilogarithm:** the public integral_spence routine uses integral_0^x -log(abs(1-t))/t dt. On the demonstrated domain x<=1 it equals real Li2(x), the mpmath polylog(2,x) reference. This convention differs from APIs that call Li2(1-x) Spence's function. Independent tests use the convergent dilogarithm series and negative-argument inversion identities. The x>1 real continuation and complex values are excluded.

**Near zero:** lnrel(x)=log(1+x) and exprel(x)=(exp(x)-1)/x, with exprel(0)=1. Independent log1p/expm1 references avoid subtractive cancellation. The 19 arguments include signed powers down to 2**(-24), zero, and dyadic samples on both sides of the 3/8 and 1/2 approximation boundaries. All lnrel inputs are greater than -1; overflow regions are excluded.

## Provenance and maintenance

Pinned public APIs, implementations and available linked author tests were reviewed. Dawson and dilogarithm have no pinned author driver in the reviewed test tree; their public implementations were reviewed directly and the examples are original consumers. All ten are independent MIT consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source was patched.

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies C10d Airy/Scorer, C10b1 real integer-order modified Bessel, C5 exponential/logarithmic integrals, C6 sine/cosine integrals, C4d elementary-function integrals, C8c Dawson and C4b exponential/logarithmic classifications. No new numerical failure was observed in these bounded probes. Loading an example does not submit a job. The [coverage report](gams-coverage.md) records remaining work.

## Driver details

### specfunc-fullerton-airy-values-derivatives-reference (C10d)

Independent API consumer; pinned sources reviewed. 56 default REAL32 Ai/Bi values and first derivatives at 14 exact dyadic arguments spanning -8..8, including zero and oscillatory/decaying/growing regions. Independent high-precision values and derivatives, relative tolerance 5e-5 with reference floor 1e-30. Complex/scaled variants, function zeros and extreme arguments excluded.

### specfunc-fullerton-modified-bessel-i01-reference (C10b1)

Independent API consumer; pinned sources reviewed. 36 default REAL32 modified Bessel I0/I1 values at 18 signed dyadic arguments spanning -16..16, including zero. Independent high-precision references include parity and near-zero behavior. Only orders zero and one are verified; bessel_in, higher-order recurrences, scaled functions and overflow ranges are excluded.

### specfunc-fullerton-modified-bessel-k01-reference (C10b1)

Independent API consumer; pinned sources reviewed. 18 default REAL32 modified Bessel K0/K1 values at nine strictly positive dyadic arguments from 1/256 to 16. High-precision relative references check logarithmic/pole behavior at small positive x and exponential decay. Only orders zero and one; bessel_kn, fractional/higher orders, zero arguments, scaling and underflow excluded.

### specfunc-fullerton-exponential-logarithmic-integrals-reference (C5)

Independent API consumer; pinned sources reviewed. 25 default REAL32 real-branch Ei/li references: Ei on 15 nonzero signed dyadic arguments -16..16 and logarithmic integral li on ten positive dyadics away from x=1. Independent principal-value definitions via mpmath; singular arguments, complex branches and large overflow regions excluded.

### specfunc-fullerton-positive-exponential-integrals-reference (C5)

Independent API consumer; pinned sources reviewed. 29 default REAL32 positive-domain exponential integral references: E1 on nine dyadics 1/256..16 and En for n=1..5 at x=1/8,1/2,1,2. References independently evaluate integral_1^infinity exp(-x*t)/t**n dt. Higher-order forward recurrence at large x, zero/negative x and underflow excluded.

### specfunc-fullerton-sine-cosine-integrals-reference (C6)

Independent API consumer; pinned sources reviewed. 18 default REAL32 sine/cosine integral values at nine positive dyadic arguments 1/256..16, spanning small-argument, series-transition and oscillatory ranges. Independent high-precision Si/Ci definitions; nonpositive Ci, complex branches and extreme arguments excluded.

### specfunc-fullerton-hyperbolic-integrals-reference (C4d)

Independent API consumer; pinned sources reviewed. 20 default REAL32 Shi/Chi references at ten positive dyadic arguments 1/256..16, including the small-argument branch boundary 3/8. Independent hyperbolic-integral values with relative tolerance 5e-5. Nonpositive Chi, complex continuation and overflow ranges excluded.

### specfunc-fullerton-dawson-values-derivatives-reference (C8c)

Independent API consumer; pinned sources reviewed. 28 default REAL32 Dawson integral/first-derivative references at 14 signed dyadic arguments -8..8. Values use the independent high-precision erfi definition; derivatives use mpmath differentiation of that definition. Includes zero, odd/even parity and multiple approximation ranges. Extreme asymptotic arguments and derivative zeros excluded.

### specfunc-fullerton-real-dilogarithm-reference (C5)

Independent API consumer; pinned sources reviewed. 12 default REAL32 real dilogarithm Li2(x) references at dyadic x in [-8,1], including zero/one and transformation boundaries. Public integral_spence uses integral_0^x -log(abs(1-t))/t dt, which equals real Li2 here. No claim about the x>1 real continuation or complex values.

### specfunc-fullerton-near-zero-exponential-logarithm-reference (C4b)

Independent API consumer; pinned sources reviewed. 38 default REAL32 lnrel(x)=log(1+x) and exprel(x)=(exp(x)-1)/x references at 19 dyadics from -7/8 to 8. Tiny signed arguments down to 2**(-24), exact zero limits and samples around 3/8 and 1/2 branch boundaries. High-precision log1p/expm1 references avoid cancellation. x<=-1 and overflow ranges excluded.

## Provenance and actual output

### specfunc-fullerton-airy-values-derivatives-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-airy-values-derivatives-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-airy-values-derivatives-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_airy.f90#L39) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/airy/test_airy.f90)

```text
Default REAL32 function comparisons with independent references: 56
Maximum relative error (reference floor 1e-30):   4.7517E-06
PASS specfunc-fullerton-airy-values-derivatives-reference
```

### specfunc-fullerton-modified-bessel-i01-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-modified-bessel-i01-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-modified-bessel-i01-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_bessel.f90#L52) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/bessel_i0/test_i0.f90)

```text
Default REAL32 function comparisons with independent references: 36
Maximum relative error (reference floor 1e-30):   1.2325E-07
PASS specfunc-fullerton-modified-bessel-i01-reference
```

### specfunc-fullerton-modified-bessel-k01-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-modified-bessel-k01-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-modified-bessel-k01-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_bessel.f90#L458) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/bessel_k0/test_k0.f90)

```text
Default REAL32 function comparisons with independent references: 18
Maximum relative error (reference floor 1e-30):   2.0714E-07
PASS specfunc-fullerton-modified-bessel-k01-reference
```

### specfunc-fullerton-exponential-logarithmic-integrals-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-exponential-logarithmic-integrals-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-exponential-logarithmic-integrals-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_ei.f90#L51) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/ei/test_ei.f90)

```text
Default REAL32 function comparisons with independent references: 25
Maximum relative error (reference floor 1e-30):   1.8218E-06
PASS specfunc-fullerton-exponential-logarithmic-integrals-reference
```

### specfunc-fullerton-positive-exponential-integrals-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-positive-exponential-integrals-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-positive-exponential-integrals-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_ei.f90#L62) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/ei/test_ei.f90)

```text
Default REAL32 function comparisons with independent references: 29
Maximum relative error (reference floor 1e-30):   1.9123E-07
PASS specfunc-fullerton-positive-exponential-integrals-reference
```

### specfunc-fullerton-sine-cosine-integrals-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-sine-cosine-integrals-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-sine-cosine-integrals-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_ei.f90#L378) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/ei/test_ei.f90)

```text
Default REAL32 function comparisons with independent references: 18
Maximum relative error (reference floor 1e-30):   1.6805E-07
PASS specfunc-fullerton-sine-cosine-integrals-reference
```

### specfunc-fullerton-hyperbolic-integrals-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-hyperbolic-integrals-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-hyperbolic-integrals-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_ei.f90#L506) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/ei/test_ei.f90)

```text
Default REAL32 function comparisons with independent references: 20
Maximum relative error (reference floor 1e-30):   5.2300E-07
PASS specfunc-fullerton-hyperbolic-integrals-reference
```

### specfunc-fullerton-dawson-values-derivatives-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-dawson-values-derivatives-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-dawson-values-derivatives-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_misc.f90#L211) / No pinned author example; API reviewed directly.

```text
Default REAL32 function comparisons with independent references: 28
Maximum relative error (reference floor 1e-30):   1.8587E-05
PASS specfunc-fullerton-dawson-values-derivatives-reference
```

### specfunc-fullerton-real-dilogarithm-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-real-dilogarithm-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-real-dilogarithm-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_misc.f90#L386) / No pinned author example; API reviewed directly.

```text
Default REAL32 function comparisons with independent references: 12
Maximum relative error (reference floor 1e-30):   6.6263E-08
PASS specfunc-fullerton-real-dilogarithm-reference
```

### specfunc-fullerton-near-zero-exponential-logarithm-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-near-zero-exponential-logarithm-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-near-zero-exponential-logarithm-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_misc.f90#L90) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/misc_exp/test_misc_exp.f90)

```text
Default REAL32 function comparisons with independent references: 38
Maximum relative error (reference floor 1e-30):   8.1069E-08
PASS specfunc-fullerton-near-zero-exponential-logarithm-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers specfunc-fullerton-airy-values-derivatives-reference specfunc-fullerton-modified-bessel-i01-reference specfunc-fullerton-modified-bessel-k01-reference specfunc-fullerton-exponential-logarithmic-integrals-reference specfunc-fullerton-positive-exponential-integrals-reference specfunc-fullerton-sine-cosine-integrals-reference specfunc-fullerton-hyperbolic-integrals-reference specfunc-fullerton-dawson-values-derivatives-reference specfunc-fullerton-real-dilogarithm-reference specfunc-fullerton-near-zero-exponential-logarithm-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
