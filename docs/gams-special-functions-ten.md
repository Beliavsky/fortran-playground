# Ten checked stdlib special-function drivers

Ten independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing stdlib libraries were reused; only mains and executables were compiled. The [verification report](gams-special-functions-ten-validation.json) retains normalized source hashes, package pins, timings and full output. GAMS categories are not exhausted.

## Independent references and limits

Legendre values and their first derivatives use the explicit Rodrigues polynomial coefficients, differentiated term by term. This differs from the upstream three-term recurrence. Degrees 0..10 at 33 dyadic points in [-1,1] give 363 value references and 363 derivative references, including endpoints. The scaled absolute tolerance is 2e-11. This is polynomial class C3a2, without a claim about associated or noninteger Legendre functions.

Complex gamma and log-gamma each have 24 independent reference constants from mpmath 1.3.0 at 80 decimal digits, confirmed at 120 digits to better than 1e-70. The [reference table](gams-special-functions-ten-references.json) records exact dyadic arguments and 26-digit component values. Gamma includes negative real parts away from poles; log-gamma uses positive real parts and the analytic branch real on the positive real axis. Both use scaled complex absolute tolerance 2e-11. This does not certify the full complex plane or branch cuts.

Log-factorial checks INT64 arguments 0..200 against a REAL64 running sum of log(k). The pinned API returns REAL32 for every integer kind. Converting that result to REAL64 does not add precision, so the scaled tolerance is 2e-6; a double-precision accuracy claim would be incorrect.

Lower, upper and regularized incomplete gamma use 264 shape/argument pairs each: integer-valued REAL64 shapes n=1..8 and x=0..8 in steps of 0.25. The independent oracle is Q(n,x)=exp(-x)*sum(x**k/k!,k=0..n-1), P=1-Q. Multiply by (n-1)! for unregularized integrals. The regularized driver checks both P and Q and their sum. Endpoints, x=n and both continuation branches are covered; noninteger shapes and integer overloads are not. Absolute/scaled tolerance 3e-12 does not promise relative accuracy in tiny tails.

Beta and log-beta each check 144 integer-valued REAL64 shape pairs 1..12, in both argument orders. The reference uses B(a,1)=1/a followed by finite products B(a,b+1)=b*B(a,b)/(a+b), with a logarithm for log-beta. There are 288 references per driver, scaled absolute tolerance 3e-12.

Despite its name, incomplete_beta returns the regularized I_x(a,b), not the unnormalized integral. For integer shapes, an independent binomial tail sum from j=a to a+b-1 gives I_x. Shapes a,b=1..8 at 33 dyadic x in [0,1] give 2,112 references, including both endpoints and both symmetry branches, with scaled absolute tolerance 5e-12. No gamma, beta or numerical quadrature routine is used by this oracle.

All floating results must be finite. Invalid inputs, extreme parameter scales, noninteger incomplete-integral shapes, other kinds and performance remain unverified. Passing these bounded examples does not establish accuracy for every argument supported by an API.

## Classification and provenance

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies C3a2 (Chebyshev, Legendre), C7a (gamma/log gamma), C7b (beta/log beta), C7e (incomplete gamma) and C7f (incomplete beta). Log-factorial uses C7a as log-gamma evaluated at n+1. These are independent MIT consumers; upstream implementation and test bodies were not copied. The pinned gamma-family author tests were reviewed; no direct Legendre example/test was found in those source trees. Loading a driver does not submit a job.

### stdlib-legendre-reference (C3a2)

Independent API consumer; pinned sources reviewed. Degrees 0..10 at 33 dyadic points including -1, 0 and 1: 363 values and 363 derivatives. Independent explicit Rodrigues coefficients, differentiated term by term, not the upstream three-term recurrence. Scaled absolute tolerance 2e-11. Negative degrees, higher degrees, other kinds and associated/noninteger Legendre functions unverified. No direct author Legendre consumer found in the pinned example/test trees.

### stdlib-complex-gamma-reference (C7a)

Independent API consumer; pinned sources reviewed. 24 complex REAL64 points with nonzero imaginary parts, including conjugate pairs. Real parts -1.25, -0.25, 0.25, 0.75, 1.5 and 3.5 test reflection and direct branches. Independent mpmath 1.3.0 constants evaluated at 80 digits and confirmed at 120; scaled complex absolute tolerance 2e-11. Poles, near-pole behavior, extreme arguments, single precision and full-plane branch behavior unverified.

### stdlib-complex-loggamma-reference (C7a)

Independent API consumer; pinned sources reviewed. 24 complex REAL64 points with nonzero imaginary parts, including conjugate pairs. Positive real parts 0.25, 0.75, 1.5, 3.5, 6.5 and 12.5 avoid ambiguity across the negative-real branch cut. Independent mpmath 1.3.0 constants evaluated at 80 digits and confirmed at 120; scaled complex absolute tolerance 2e-11. Poles, near-pole behavior, extreme arguments, single precision and full-plane branch behavior unverified.

### stdlib-log-factorial-reference (C7a)

Independent API consumer; pinned sources reviewed. 201 INT64 arguments 0..200 against a REAL64 running sum of log(k). The pinned API returns REAL32 for every integer kind; converting to REAL64 does not add precision. Scaled tolerance 2e-6 explicitly reflects that contract. Negative arguments, larger integers, overflow boundaries and a REAL64-accuracy result are not claimed.

### stdlib-lower-gamma-reference (C7e)

Independent API consumer; pinned sources reviewed. 264 (shape,x) pairs: integer-valued REAL64 shapes 1..8 and x=0..8 in steps of 0.25, including x=shape and both continuation branches. Independent finite Poisson sum Q(n,x)=exp(-x)*sum(x**k/k!,k=0..n-1), P=1-Q; unregularized references multiply by (n-1)!. Scaled absolute tolerance 3e-12, so tiny tails are not certified to relative accuracy. Noninteger shapes, negative x, extreme tails, integer-overload semantics and other kinds unverified.

### stdlib-upper-gamma-reference (C7e)

Independent API consumer; pinned sources reviewed. 264 (shape,x) pairs: integer-valued REAL64 shapes 1..8 and x=0..8 in steps of 0.25, including x=shape and both continuation branches. Independent finite Poisson sum Q(n,x)=exp(-x)*sum(x**k/k!,k=0..n-1), P=1-Q; unregularized references multiply by (n-1)!. Scaled absolute tolerance 3e-12, so tiny tails are not certified to relative accuracy. Noninteger shapes, negative x, extreme tails, integer-overload semantics and other kinds unverified.

### stdlib-regularized-gamma-reference (C7e)

Independent API consumer; pinned sources reviewed. 264 (shape,x) pairs: integer-valued REAL64 shapes 1..8 and x=0..8 in steps of 0.25, including x=shape and both continuation branches. Independent finite Poisson sum Q(n,x)=exp(-x)*sum(x**k/k!,k=0..n-1), P=1-Q; unregularized references multiply by (n-1)!. Both P and Q plus P+Q=1 checked. Scaled absolute tolerance 3e-12, so tiny tails are not certified to relative accuracy. Noninteger shapes, negative x, extreme tails, integer-overload semantics and other kinds unverified.

### stdlib-beta-reference (C7b)

Independent API consumer; pinned sources reviewed. 144 positive integer-valued REAL64 shape pairs 1..12, both argument orders: 288 references. Beta oracle uses B(a,1)=1/a then product recurrence B(a,b+1)=b*B(a,b)/(a+b); log-beta oracle is log of that independently formed product. Scaled absolute tolerance 3e-12. Noninteger shapes, invalid inputs, underflow and extreme parameter scales unverified.

### stdlib-log-beta-reference (C7b)

Independent API consumer; pinned sources reviewed. 144 positive integer-valued REAL64 shape pairs 1..12, both argument orders: 288 references. Beta oracle uses B(a,1)=1/a then product recurrence B(a,b+1)=b*B(a,b)/(a+b); log-beta oracle is log of that independently formed product. Scaled absolute tolerance 3e-12. Noninteger shapes, invalid inputs, underflow and extreme parameter scales unverified.

### stdlib-incomplete-beta-reference (C7f)

Independent API consumer; pinned sources reviewed. 2,112 regularized I_x(a,b) references for integer-valued REAL64 shapes 1..8 at 33 dyadic x in [0,1], including both endpoints. Independent binomial tail sum from j=a to a+b-1 of choose(a+b-1,j)*x**j*(1-x)**(a+b-1-j); polynomial evaluation needs no gamma/beta or continued fraction calls. Scaled absolute tolerance 5e-12. Noninteger shapes, tiny relative tails, invalid inputs, larger shapes and other kinds unverified.

## Provenance and actual output

### stdlib-legendre-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-legendre-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-legendre-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L8) / No pinned author example; API reviewed directly.

```text
363 Legendre values and 363 derivatives, degrees 0..10, versus explicit polynomial coefficients
PASS stdlib-legendre-reference
```

### stdlib-complex-gamma-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-gamma-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-gamma-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L396) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90)

```text
24 complex references from independent 80/120-digit mpmath evaluations
PASS stdlib-complex-gamma-reference
```

### stdlib-complex-loggamma-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-loggamma-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-loggamma-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L978) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90)

```text
24 complex references from independent 80/120-digit mpmath evaluations
PASS stdlib-complex-loggamma-reference
```

### stdlib-log-factorial-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-log-factorial-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-log-factorial-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L51) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90)

```text
201 log-factorials versus summed logarithms; upstream result is REAL32 (tolerance 2e-6)
PASS stdlib-log-factorial-reference
```

### stdlib-lower-gamma-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-lower-gamma-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-lower-gamma-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L62) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90)

```text
Finite Poisson-sum reference pairs (integer-valued REAL64 shapes 1..8, x=0..8): 264
PASS stdlib-lower-gamma-reference
```

### stdlib-upper-gamma-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-upper-gamma-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-upper-gamma-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L98) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90)

```text
Finite Poisson-sum reference pairs (integer-valued REAL64 shapes 1..8, x=0..8): 264
PASS stdlib-upper-gamma-reference
```

### stdlib-regularized-gamma-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-regularized-gamma-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-regularized-gamma-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L134) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90)

```text
Finite Poisson-sum reference pairs (integer-valued REAL64 shapes 1..8, x=0..8): 264
PASS stdlib-regularized-gamma-reference
```

### stdlib-beta-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-beta-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-beta-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L205) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90)

```text
288 beta-family references using independent finite products, shapes 1..12
PASS stdlib-beta-reference
```

### stdlib-log-beta-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-log-beta-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-log-beta-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L214) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90)

```text
288 beta-family references using independent finite products, shapes 1..12
PASS stdlib-log-beta-reference
```

### stdlib-incomplete-beta-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-incomplete-beta-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-incomplete-beta-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L223) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90)

```text
2112 regularized incomplete-beta references versus independent binomial tail sums
PASS stdlib-incomplete-beta-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-legendre-reference stdlib-complex-gamma-reference stdlib-complex-loggamma-reference stdlib-log-factorial-reference stdlib-lower-gamma-reference stdlib-upper-gamma-reference stdlib-regularized-gamma-reference stdlib-beta-reference stdlib-log-beta-reference stdlib-incomplete-beta-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
