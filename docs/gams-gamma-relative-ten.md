# Ten checked gamma and relative-function drivers

Ten independent specfunc-fullerton consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. The cached library was reused and only main.f90 and playground-main were compiled. The [verification report](gams-gamma-relative-ten-validation.json) retains normalized UTF-8/LF source hashes, exact pins, timings and full output. GAMS coverage remains unfinished.

## Precision and references

All demonstrated public APIs accept and return default REAL32. Exact dyadic inputs are converted to that kind; widening outputs to REAL64 for comparison does not provide REAL64 function accuracy. Independent references were generated with mpmath 1.3.0 at 80 decimal digits and confirmed at 120 digits, with absolute differences below 1e-60. The [reference table](gams-gamma-relative-ten-references.json) records every argument, integer order where relevant and 18-significant-digit expected value.

All returned values must be finite and satisfy abs(actual-reference)/max(abs(reference),1e-30)<=5e-5. Exact zero references are therefore checked effectively exactly. Gamma signs are checked separately against exact +/-1. Each driver prints its actual maximum relative error. These bounded cases are not a precision or performance benchmark.

| Driver | GAMS | Independent checks |
| --- | --- | --- |
| Lower incomplete gamma | C7e | 49 unnormalized lower integrals; positive shapes 1/2..8, x=0..8 |
| Upper gamma, positive x | C7e | 66 unnormalized tail integrals; positive and selected nonpositive shapes, strictly positive x |
| Tricomi incomplete gamma | C7e | 49 scaled lower-gamma values, including exact x=0 limits |
| Signed log gamma | C7a | 18 log-absolute values plus exact signs, including negative half-integers |
| Generalized Pochhammer | C7a | 48 gamma ratios, including signed, fractional and integer shifts |
| Relative Pochhammer | C7a | 35 cancellation-sensitive ratios and exact zero-shift digamma limits |
| Factorials | C1 | 34 finite REAL32 factorials n=0..33 |
| Signed cube roots | C2 | 55 dyadic inputs, signs and zero, exponents -90..90 |
| Entire cosine integral | C6 | 11 nonnegative Cin values, zero, tiny inputs and x up to 16 |
| Reciprocal gamma pole zeros | C7a | 13 exact pole zeros and 28 signed half-integer values |

## Definitions and bounded scope

The lower incomplete gamma is integral_0^x exp(-t)*t**(a-1) dt, not a regularized probability. Its positive-shape cases include x=0. The upper incomplete gamma is the corresponding tail integral_x^infinity. The positive-x driver tests x=1/8,1/2,1,2,4,8 for shapes 1/2,1,3/2,2,3,4,8,-2,-1,-1/2,0. Its documented but broken x=0 path is excluded and retained separately below. Tricomi uses x**(-a)*lower_gamma(a,x)/Gamma(a), with limit 1/Gamma(a+1) at x=0; only positive shapes are verified.

sign_log_gamma returns log(abs(Gamma(x))) and a separate sign, verified at eight negative half-integers and ten positive dyadics in [1/8,32]. Pochhammer uses Gamma(a+x)/Gamma(a) with positive a and a+x. poch1 uses (Gamma(a+x)/Gamma(a)-1)/x; independent expm1/loggamma references avoid cancellation for signed shifts as small as 2**(-16), and x=0 uses the digamma limit. Poles, near-pole perturbations, negative-base continuation and large-shift asymptotics are excluded.

Factorials n=0..33 are compared with independent integer factorials rounded only when making reference constants. This does not claim n=33 is the largest representable factorial: 34! is also within REAL32 range but is not tested here. Signed real cube roots include zero and normal REAL32 inputs with significands 1,5/4,7/4 and exponents -90,-30,-9,-3,0,3,9,30,90. Subnormal and exceptional inputs are excluded.

The misleading public name inverse_ci denotes Cin(x)=integral_0^x (1-cos(t))/t dt, not an inverse function. Only x>=0 is checked. Independent high-precision EulerGamma+log(x)-Ci(x) references handle tiny nonzero arguments; zero is supplied by the exact limit. Reciprocal gamma is checked as an entire function with exact zeros at 0,-1,...,-12 and signed half-integer values from -23/2 to 31/2.

## Retained failures

The broad upper-gamma probe returned NaN at a=1/2,x=0 instead of sqrt(pi). The source rejects x<=0 before an x==0 branch, making that branch unreachable. The [original probe](gams-candidates/fullerton-upper-gamma/) and [diagnostic probe](gams-candidates/fullerton-gamma-cinh/README.md) are retained with normalized hashes, pins and full hosted results. Its broad procedure record has no driver. The separate positive-x consumer does not verify or repair that endpoint.

The inverse_chi/Cinh probe built but returned 2.7167096138000488 at x=-3 instead of 3.2845641411959674. Its exact source and full result are retained alongside the gamma diagnostic. This broad Cinh record has no checked driver; no assertion was relaxed and no library code was patched. The separate reciprocal-gamma consumer replaces this candidate. Other successful special functions do not establish Cinh correctness.

## Provenance

Pinned public APIs, implementations and linked author tests were reviewed. The cube-root example has no author test in the reviewed pinned test tree, so its implementation was reviewed directly. All ten consumers are independent MIT examples; upstream implementations and author test bodies were not copied. Classifications follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). Loading a driver does not submit a job. See the [coverage report](gams-coverage.md) for remaining work.

## Driver details

### specfunc-fullerton-lower-incomplete-gamma-reference (C7e)

Independent API consumer. 49 unnormalized lower incomplete gamma integrals, seven positive integer/half-integer shapes 1/2..8 and seven x=0..8. Direct high precision lower-integral references; not regularized probabilities. Negative shapes, analytic continuation and extremes excluded.

### specfunc-fullerton-tricomi-incomplete-gamma-reference (C7e)

Independent API consumer. 49 scaled Tricomi incomplete gamma values for positive shapes 1/2..8 and x=0..8. Independent x**(-a)*lower_gamma(a,x)/Gamma(a) references, with limit 1/Gamma(a+1) at zero. Nonpositive-shape analytic continuation excluded.

### specfunc-fullerton-signed-log-gamma-reference (C7a)

Independent API consumer. 18 signed log-absolute-gamma evaluations, including eight negative half-integers and positive dyadics 1/8..32. Independent log(abs(Gamma(x))) and exact sign checked separately. Gamma poles and neighborhoods of poles excluded.

### specfunc-fullerton-pochhammer-ratios-reference (C7a)

Independent API consumer. 48 generalized Pochhammer Gamma(a+x)/Gamma(a) values for positive dyadic a=1/2..8 and signed/fractional/integer shifts -1/4..5; a+x stays positive. Independent rising-factorial references; poles and large-argument asymptotics excluded.

### specfunc-fullerton-relative-pochhammer-reference (C7a)

Independent API consumer. 35 relative Pochhammer values (Gamma(a+x)/Gamma(a)-1)/x with positive a=1/2..8 and signed shifts down to 2**(-16), including exact x=0 digamma limits. Independent high precision expm1/loggamma references avoid cancellation. Negative a, poles and large shifts excluded.

### specfunc-fullerton-factorials-real32-reference (C1)

Independent API consumer. 34 default REAL32 factorials n=0..33 compared with independently computed integer factorials. Includes zero and moderately large finite factorials; invalid negative inputs and n>=34 excluded (34! is also representable but not tested here).

### specfunc-fullerton-signed-cube-roots-reference (C2)

Independent API consumer. 55 signed cube roots, zero and exact dyadic inputs with exponents -90..90 and significands 1,5/4,7/4. Independent high precision real cube roots; signs, small and large normal REAL32 magnitudes checked. Subnormal inputs and exceptional values excluded.

### specfunc-fullerton-entire-cosine-integral-reference (C6)

Independent API consumer. 11 nonnegative Cin integral values, x=0..16 including tiny positive arguments. Public inverse_ci computes Cin(x)=integral_0^x (1-cos(t))/t dt; it is not an inverse of Ci. Independent high precision entire-integral references. Negative inputs and complex continuation excluded.

### specfunc-fullerton-upper-gamma-positive-x-reference (C7e)

Independent API consumer. 66 unnormalized upper incomplete gamma integrals for strictly positive x=1/8..8, with seven positive shapes 1/2..8 and shapes -2,-1,-1/2,0. Independent high precision tail integrals. The documented x=0 path returns NaN in a retained failed probe and is expressly excluded, not repaired or verified. Near-pole noninteger negative shapes and extremes excluded.

### specfunc-fullerton-reciprocal-gamma-pole-zeros-reference (C7a)

Independent API consumer. 41 reciprocal-gamma values: exact zeros at 0,-1,..,-12 and signed half-integers -23/2..31/2. Independent high precision entire reciprocal gamma references test sign changes, pole zeros and finite values. Near-pole perturbations and extreme magnitudes excluded.

## Provenance and actual output

### specfunc-fullerton-lower-incomplete-gamma-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-lower-incomplete-gamma-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-lower-incomplete-gamma-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L238) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/gamma/test_gamma.f90)

```text
Default REAL32 comparisons with independent high precision references: 49
Maximum relative error (reference floor 1e-30):   8.0582E-07
PASS specfunc-fullerton-lower-incomplete-gamma-reference
```

### specfunc-fullerton-tricomi-incomplete-gamma-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-tricomi-incomplete-gamma-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-tricomi-incomplete-gamma-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L412) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/gamma/test_gamma.f90)

```text
Default REAL32 comparisons with independent high precision references: 49
Maximum relative error (reference floor 1e-30):   5.0771E-07
PASS specfunc-fullerton-tricomi-incomplete-gamma-reference
```

### specfunc-fullerton-signed-log-gamma-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-signed-log-gamma-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-signed-log-gamma-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L55) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/gamma/test_gamma.f90)

```text
Default REAL32 comparisons with independent high precision references: 18
Maximum relative error (reference floor 1e-30):   6.8320E-07
PASS specfunc-fullerton-signed-log-gamma-reference
```

### specfunc-fullerton-pochhammer-ratios-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-pochhammer-ratios-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-pochhammer-ratios-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_poch.f90#L33) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/poch/test_poch.f90)

```text
Default REAL32 comparisons with independent high precision references: 48
Maximum relative error (reference floor 1e-30):   8.1681E-08
PASS specfunc-fullerton-pochhammer-ratios-reference
```

### specfunc-fullerton-relative-pochhammer-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-relative-pochhammer-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-relative-pochhammer-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_poch.f90#L187) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/poch/test_poch.f90)

```text
Default REAL32 comparisons with independent high precision references: 35
Maximum relative error (reference floor 1e-30):   1.0143E-05
PASS specfunc-fullerton-relative-pochhammer-reference
```

### specfunc-fullerton-factorials-real32-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-factorials-real32-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-factorials-real32-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_poch.f90#L419) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/poch/test_poch.f90)

```text
Default REAL32 comparisons with independent high precision references: 34
Maximum relative error (reference floor 1e-30):   3.1331E-06
PASS specfunc-fullerton-factorials-real32-reference
```

### specfunc-fullerton-signed-cube-roots-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-signed-cube-roots-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-signed-cube-roots-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_misc.f90#L39) / No pinned author example; API reviewed directly.

```text
Default REAL32 comparisons with independent high precision references: 55
Maximum relative error (reference floor 1e-30):   6.5368E-08
PASS specfunc-fullerton-signed-cube-roots-reference
```

### specfunc-fullerton-entire-cosine-integral-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-entire-cosine-integral-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-entire-cosine-integral-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_inv_ci.f90#L101) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/inv_ci/test_inv_ci.f90)

```text
Default REAL32 comparisons with independent high precision references: 11
Maximum relative error (reference floor 1e-30):   5.9834E-08
PASS specfunc-fullerton-entire-cosine-integral-reference
```

### specfunc-fullerton-upper-gamma-positive-x-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-upper-gamma-positive-x-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-upper-gamma-positive-x-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L282) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/gamma/test_gamma.f90)

```text
Default REAL32 comparisons with independent high precision references: 66
Maximum relative error (reference floor 1e-30):   9.4607E-07
PASS specfunc-fullerton-upper-gamma-positive-x-reference
```

### specfunc-fullerton-reciprocal-gamma-pole-zeros-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-reciprocal-gamma-pole-zeros-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-reciprocal-gamma-pole-zeros-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L204) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/gamma/test_gamma.f90)

```text
Default REAL32 comparisons with independent high precision references: 41
Maximum relative error (reference floor 1e-30):   3.4738E-06
PASS specfunc-fullerton-reciprocal-gamma-pole-zeros-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers specfunc-fullerton-lower-incomplete-gamma-reference specfunc-fullerton-tricomi-incomplete-gamma-reference specfunc-fullerton-signed-log-gamma-reference specfunc-fullerton-pochhammer-ratios-reference specfunc-fullerton-relative-pochhammer-reference specfunc-fullerton-factorials-real32-reference specfunc-fullerton-signed-cube-roots-reference specfunc-fullerton-entire-cosine-integral-reference specfunc-fullerton-upper-gamma-positive-x-reference specfunc-fullerton-reciprocal-gamma-pole-zeros-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
