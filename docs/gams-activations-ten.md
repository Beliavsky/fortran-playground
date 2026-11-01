# Ten checked stdlib activation and normalization drivers

Ten independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-activations-ten-validation.json) saves normalized source hashes, pins, timings and complete output. GAMS categories are not exhausted.

## Scalar values and independently differentiated references

Nine drivers check Gaussian, ELU, ReLU, leaky ReLU, GELU, SELU, sigmoid, SiLU and softplus values on 97 exact dyadic points x=-6..6 by 0.125. ELU uses parameters [0.125,1,2]; leaky ReLU uses [0.125,0.5,1]. The other functions have no free parameter. The [reference table](gams-activations-ten-references.json) contains 1,261 value rows and independent derivative references, including those needed to reproduce the failed gradient probes.

Definitions used by the independent mpmath 1.3.0 reference generator:

```text
Gaussian: exp(-x*x)
ELU: x for x>=0, otherwise alpha*expm1(x)
ReLU: max(x,0)
leaky ReLU: x for x>=0, otherwise alpha*x
GELU: x*Phi(x), with Phi the standard normal CDF
SELU: scale*(x for x>0, otherwise alpha*expm1(x))
sigmoid: 1/(1+exp(-x))
SiLU: x/(1+exp(-x))
softplus: log1p(exp(x))
```

mp.diff differentiates these definitions independently at 80 decimal digits. Values and derivatives are confirmed at 120 digits to absolute difference below 1e-65; 26-digit constants are stored in the table. SELU uses canonical decimal scale 1.0507009873554804934193349852946 and alpha 1.6732632423543772848170429916717. The Fortran comparisons use scaled absolute tolerance 2e-12, finite outputs and input preservation.

Seven scalar drivers verify gradients as well as values. Derivative assertions at zero are omitted for ELU, ReLU, leaky ReLU and SELU, where piecewise definitions can have a kink. A chosen API branch value at such a point is not claimed as a unique mathematical derivative. GELU and SiLU gradients failed and are excluded from their published value-only drivers. Thus the successful scalar tests cover 1,261 values and 1,059 derivative values.

All claims are limited to these bounded REAL64 grids. Large-input overflow/underflow behavior, relative accuracy of tiny outputs, other kinds and performance are unverified. In particular this is not a blanket stability claim for exp-based scalar activations. Approximate GELU and the fast approximate intrinsic APIs are not tested.

## Softmax, log-softmax and diagonal derivatives

The tenth driver normalizes 144 rank-one vectors of lengths 1..12 and 24 rank-two 3x4 arrays with explicit dim=1 and dim=2. Positive dyadic weights independently define probabilities w/sum(w), their logarithms and diagonal derivatives p*(1-p). Logits are log(w) plus a common shift from [-1000,0,1000]. These shifts test normalization without overflowing exp of the unshifted logits.

Each of softmax, logsoftmax and softmax_grad has 1,224 entry references: 3,672 comparisons altogether. Finite values, normalization sums and unchanged inputs are checked at absolute tolerance 3e-12. Singleton and tied-logit cases are included. softmax_grad returns the Jacobian diagonal only; this driver does not claim a full Jacobian. Rank-three/four APIs, empty or nonfinite inputs, invalid dimensions, extreme dynamic ranges and performance remain unverified.

## Retained gradient failures

The exact [GELU and SiLU gradient probes and full results](gams-candidates/stdlib-activations/README.md) are retained. Both compiled and ran against the pinned cached library, then failed comparison with independent derivatives at x=-6:

| API | Actual | Independent derivative |
| --- | ---: | ---: |
| gelu_grad | -6.3628744084007051e-8 | -3.5468709453902015e-8 |
| silu_grad | -1.2320303571493932e-2 | -1.2326432591525513e-2 |

For GELU=x*Phi(x), the derivative is Phi(x)+x*phi(x). The pinned exponential term omits 1/sqrt(pi). For SiLU, the derivative is sigmoid(x)+x*sigmoid(x)*(1-sigmoid(x)); the pinned leading term uses exp(x) instead of sigmoid(x). The upstream SiLU gradient test repeats that implementation expression, illustrating why it is insufficient as an independent oracle. No upstream numerical source was patched.

The failed gradient APIs have separate source-reviewed procedure records without checked drivers. Successful GELU/SiLU value checks do not promote their gradients, and neither failed gradient call appears in the published examples.

## Classification and provenance

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies broad C19 (other special functions) for the scalar activation functions and D1a11 (other vector operations) for normalization. These records do not claim a fitting/training algorithm or an invented neural-network taxonomy leaf.

Pinned public APIs, implementations and available author tests were reviewed. No direct softplus author consumer was found in the pinned test file; its public API and implementation were reviewed directly. These are independent MIT consumers; upstream implementation/test bodies were not copied and upstream license terms remain separate. Loading a driver does not submit a job.

### stdlib-activation-gaussian-reference (C19)

Independent API consumer; pinned sources reviewed. REAL64 elemental arrays on 97 exact dyadic points -6..6 by 0.125. Independent mpmath function values and mp.diff first derivatives at 80 digits, confirmed at 120 digits; scaled tolerance 2e-12. Finite outputs and input preservation checked. Large-magnitude/overflow behavior, relative tiny-tail accuracy, other kinds and performance unverified.

### stdlib-activation-elu-reference (C19)

Independent API consumer; pinned sources reviewed. REAL64 elemental arrays on 97 exact dyadic points -6..6 by 0.125 at parameters [0.125, 1.0, 2.0]. Independent mpmath function values and mp.diff first derivatives at 80 digits, confirmed at 120 digits; scaled tolerance 2e-12. Value at zero checked; derivative assertions omit zero rather than prescribing a derivative at a possible kink. Finite outputs and input preservation checked. Large-magnitude/overflow behavior, relative tiny-tail accuracy, other kinds and performance unverified.

### stdlib-activation-relu-reference (C19)

Independent API consumer; pinned sources reviewed. REAL64 elemental arrays on 97 exact dyadic points -6..6 by 0.125. Independent mpmath function values and mp.diff first derivatives at 80 digits, confirmed at 120 digits; scaled tolerance 2e-12. Value at zero checked; derivative assertions omit zero rather than prescribing a derivative at a possible kink. Finite outputs and input preservation checked. Large-magnitude/overflow behavior, relative tiny-tail accuracy, other kinds and performance unverified.

### stdlib-activation-leaky-relu-reference (C19)

Independent API consumer; pinned sources reviewed. REAL64 elemental arrays on 97 exact dyadic points -6..6 by 0.125 at parameters [0.125, 0.5, 1.0]. Independent mpmath function values and mp.diff first derivatives at 80 digits, confirmed at 120 digits; scaled tolerance 2e-12. Value at zero checked; derivative assertions omit zero rather than prescribing a derivative at a possible kink. Finite outputs and input preservation checked. Large-magnitude/overflow behavior, relative tiny-tail accuracy, other kinds and performance unverified.

### stdlib-activation-gelu-reference (C19)

Independent API consumer; pinned sources reviewed. 97 REAL64 gelu function-value references on exact dyadic points -6..6 by 0.125. Independent mpmath values at 80 digits, confirmed at 120 digits; scaled tolerance 2e-12. Finite outputs and input preservation checked. gelu_grad failed a retained independent derivative probe and is deliberately excluded from the published driver. No gradient accuracy, large-magnitude/overflow behavior, relative tiny-tail accuracy, other kinds or performance is claimed.

### stdlib-activation-selu-reference (C19)

Independent API consumer; pinned sources reviewed. REAL64 elemental arrays on 97 exact dyadic points -6..6 by 0.125. Independent mpmath function values and mp.diff first derivatives at 80 digits, confirmed at 120 digits; scaled tolerance 2e-12. Value at zero checked; derivative assertions omit zero rather than prescribing a derivative at a possible kink. Canonical scale=1.0507009873554804934193349852946 and alpha=1.6732632423543772848170429916717. Finite outputs and input preservation checked. Large-magnitude/overflow behavior, relative tiny-tail accuracy, other kinds and performance unverified.

### stdlib-activation-sigmoid-reference (C19)

Independent API consumer; pinned sources reviewed. REAL64 elemental arrays on 97 exact dyadic points -6..6 by 0.125. Independent mpmath function values and mp.diff first derivatives at 80 digits, confirmed at 120 digits; scaled tolerance 2e-12. Finite outputs and input preservation checked. Large-magnitude/overflow behavior, relative tiny-tail accuracy, other kinds and performance unverified.

### stdlib-activation-silu-reference (C19)

Independent API consumer; pinned sources reviewed. 97 REAL64 silu function-value references on exact dyadic points -6..6 by 0.125. Independent mpmath values at 80 digits, confirmed at 120 digits; scaled tolerance 2e-12. Finite outputs and input preservation checked. silu_grad failed a retained independent derivative probe and is deliberately excluded from the published driver. No gradient accuracy, large-magnitude/overflow behavior, relative tiny-tail accuracy, other kinds or performance is claimed.

### stdlib-activation-softplus-reference (C19)

Independent API consumer; pinned sources reviewed. REAL64 elemental arrays on 97 exact dyadic points -6..6 by 0.125. Independent mpmath function values and mp.diff first derivatives at 80 digits, confirmed at 120 digits; scaled tolerance 2e-12. Finite outputs and input preservation checked. Large-magnitude/overflow behavior, relative tiny-tail accuracy, other kinds and performance unverified.

### stdlib-softmax-normalization-reference (D1a11)

Independent API consumer; pinned sources reviewed. 144 rank-one REAL64 vectors (lengths 1..12) and 24 rank-two 3x4 arrays normalized on both dimensions, including singletons and tied logits. Positive dyadic weights provide independent rational probabilities, logarithms of those ratios, and diagonal derivatives p*(1-p). Common shifts -1000,0,1000 test stable normalization. 1,224 entry references per function, 3,672 comparisons; finite outputs, normalization sums and input preservation checked at absolute tolerance 3e-12. softmax_grad is checked only as the Jacobian diagonal, not a full Jacobian. Empty/nonfinite inputs, rank-three/four overloads, invalid dimensions, extreme dynamic ranges and performance unverified.

## Provenance and actual output

### stdlib-activation-gaussian-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-gaussian-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-activation-gaussian-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L32) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90)

```text
Independent 80/120-digit activation references: values=97, derivatives=97
PASS stdlib-activation-gaussian-reference
```

### stdlib-activation-elu-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-elu-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-activation-elu-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L64) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90)

```text
Independent 80/120-digit activation references: values=291, derivatives=288
PASS stdlib-activation-elu-reference
```

### stdlib-activation-relu-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-relu-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-activation-relu-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L100) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90)

```text
Independent 80/120-digit activation references: values=97, derivatives=96
PASS stdlib-activation-relu-reference
```

### stdlib-activation-leaky-relu-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-leaky-relu-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-activation-leaky-relu-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L132) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90)

```text
Independent 80/120-digit activation references: values=291, derivatives=288
PASS stdlib-activation-leaky-relu-reference
```

### stdlib-activation-gelu-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-gelu-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-activation-gelu-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L168) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90)

```text
Independent 80/120-digit activation references: values=97, derivatives=0
PASS stdlib-activation-gelu-reference
```

### stdlib-activation-selu-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-selu-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-activation-selu-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L232) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90)

```text
Independent 80/120-digit activation references: values=97, derivatives=96
PASS stdlib-activation-selu-reference
```

### stdlib-activation-sigmoid-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-sigmoid-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-activation-sigmoid-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L264) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90)

```text
Independent 80/120-digit activation references: values=97, derivatives=97
PASS stdlib-activation-sigmoid-reference
```

### stdlib-activation-silu-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-silu-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-activation-silu-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L296) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90)

```text
Independent 80/120-digit activation references: values=97, derivatives=0
PASS stdlib-activation-silu-reference
```

### stdlib-activation-softplus-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-softplus-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-activation-softplus-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L498) / No pinned author example; API reviewed directly.

```text
Independent 80/120-digit activation references: values=97, derivatives=97
PASS stdlib-activation-softplus-reference
```

### stdlib-softmax-normalization-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-softmax-normalization-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-softmax-normalization-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L360) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90)

```text
Rational/log-ratio softmax references: vectors=144, matrices=24, entries per function=1224
PASS stdlib-softmax-normalization-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-activation-gaussian-reference stdlib-activation-elu-reference stdlib-activation-relu-reference stdlib-activation-leaky-relu-reference stdlib-activation-gelu-reference stdlib-activation-selu-reference stdlib-activation-sigmoid-reference stdlib-activation-silu-reference stdlib-activation-softplus-reference stdlib-softmax-normalization-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
