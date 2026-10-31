# Checked automatic differentiation and adaptive IVPs

These H1 and I1a1a drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-adaptive-ad-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## forwarddiff analytic scalar derivatives (H1)

The differentia derivative entry point seeds one dual-number direction and returns both the function value and its first derivative. The driver compares those outputs with elementary analytic formulas, without finite differences or another differentiation package. A lifted constant 0*x+3 and monomials x**p for p=1..8 are checked at 65 points x=i/16, i=-32..32. This gives 585 calls and includes zero and negative inputs. The constant is explicitly lifted into the seeded dual space rather than assigning a real to an uninitialized dual.

Twelve smooth functions are each checked at 97 points x=i/32, i=-48..48: 1/(1+x*x), exp(sin(x)), log(2+x), sqrt(2+x), sin(2*x)*cos(x), atan(x), tan(x/2), (2+x)**1.5, 2**x, (2+x)**(1+x/4), asin(x/2), and acos(x/2). These exercise chain, product and quotient rules, integer/real/dual exponents, and several elementary intrinsic overloads. Logarithms, roots and variable powers stay strictly inside their real domains; inverse trigonometric endpoints and tangent poles are avoided.

Total: 1,749 derivative calls and 3,498 analytic value/slope comparisons. Both results must be finite and abs(result-reference)/(1+abs(reference)) must not exceed 2e-12. The saved maximum normalized error is 1.6666e-16. This is a first scalar derivative check, not a gradient, Jacobian, higher-order AD, nonsmooth-function, exceptional-input or performance verification.

## FLINT explicit adaptive integration and dense output (I1a1a)

All four exposed methods are exercised: DOP853, DOP54, VERNER98R and VERNER65E. Three analytic three-state systems provide independent endpoint and dense-output references:

```text
Diagonal exponentials:
  y = [1,-2,1/2] * exp(a*[-1/2,1/4,-3/2]*t)
  y' = a*[-1/2,1/4,-3/2]*y
Oscillator plus nonautonomous polynomial:
  y = [cos(a*t)+sin(a*t)/4, -sin(a*t)+cos(a*t)/4, t**3-2*t+1]
  y' = [a*y2,-a*y1,3*t*t-2]
Coupled triangular system:
  y = [1,t,t*t]*exp(-a*t)
  y' = [-a*y1,y1-a*y2,2*y2-a*y3]
```

The cross product is four methods, three systems, parameters a=1/2 or 3/2, starting times -1/2 or 3/4, and forward/backward intervals of length 5/4: 96 integrations. Each fixture starts with its exact state at the specified nonzero initial time and creates a fresh equation/solver object. The initial step is selected automatically (StepSz=0); no constant-step mode is used.

For a=1/2 the requested scalar tolerances are ATol=1e-12 and RTol=1e-11. For a=3/2 they are componentwise [1,2,4]*1e-12 and [1,2,4]*1e-11. Initialization and integration must report FLINT_SUCCESS, the reached time must be finite and agree with the requested endpoint within 32*epsilon*max(1,abs(endpoint)), and the initial state must remain unchanged. The returned endpoint state is compared with the closed form, giving 288 endpoint reference entries.

Each stored dense solution is sampled at 17 equally spaced times including both endpoints, ordered in the integration direction. It is sampled twice: the first call retains coefficients with SaveInterpCoeffs=true, and the second releases them with SaveInterpCoeffs=false. Both calls must report success; every state entry is checked against the closed form, and the repeated output must be identical. There are 9,792 dense-output reference entries, including the repeated calls.

All returned states must be finite. Endpoint and dense errors use abs(result-reference)/(1+abs(reference)) <= 5e-9. The saved maximum across these checks is 1.6699e-9. Requested local error tolerances and independently checked solution errors have different meanings. These examples do not rank methods by speed or accuracy. Stiff equations, event detection, step-advance/constant-step modes, invalid requests and failure diagnostics remain unverified.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources, implementations and author examples were reviewed without copying upstream code. Loading a link does not submit a job.

### forwarddiff-analytic-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forwarddiff&example=gams-forwarddiff-analytic-reference) / [Driver source](../fpm_catalog/gams-drivers/forwarddiff-analytic-reference.f90) / [Pinned procedure](https://github.com/Nicholaswogan/forwarddiff/blob/2388e8ecf300a7bbc0904feab47023413464edf9/src/differentia_derivative.f90#L54) / [Author test](https://github.com/Nicholaswogan/forwarddiff/blob/2388e8ecf300a7bbc0904feab47023413464edf9/test/test_differentia.f90)

```text
Scalar derivative calls: 1749
Analytic value/slope references: 3498
Maximum normalized error:   1.6666E-16
PASS forwarddiff-analytic-reference
```

### flint-ivp-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=flint&example=gams-flint-ivp-reference) / [Driver source](../fpm_catalog/gams-drivers/flint-ivp-reference.f90) / [Pinned procedure](https://github.com/princemahajan/FLINT/blob/b6322037cb751b11fa64ea66cf23173ae572fff6/src/ERK.f90#L72) / [Author test](https://github.com/princemahajan/FLINT/blob/b6322037cb751b11fa64ea66cf23173ae572fff6/tests/test_WP.f90)

```text
Adaptive integrations: 96
Endpoint reference entries: 288
Dense-output reference entries: 9792
Maximum normalized error:   1.6699E-09
PASS flint-ivp-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers forwarddiff-analytic-reference flint-ivp-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
