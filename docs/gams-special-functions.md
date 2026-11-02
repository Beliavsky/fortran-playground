# Checked GAMS special-function drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [C7a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C7a) | Gamma, log-Gamma and reciprocal-Gamma at positive real arguments | Fullerton `fgamma`, `log_gamma`, `reciprocal_gamma` |
| [C7c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C7c) | Psi/digamma at positive real arguments | Fullerton `digamma` |
| [C10b1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C10b1) | Modified Bessel I/K, real arguments and integer orders; tested orders 0 and 1 | fortran-bessels `besseli0`, `besseli1`, `besselk0`, `besselk1` |
| [C10](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C10) | Complex J/I sequences and half-order K | AMOS `f90_zbesj`, `f90_zbesi`, `f90_zbesk` |
| [C14](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C14) | Carlson RF and complete elliptic K | `carlson_elliptic_module:drf` |
| [C19](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C19) | Bernoulli numbers and integer power sums | `specfun_module:bernob` |

These demonstrate selected arguments and named procedures. They do not exhaust their GAMS classes or cover all orders, branch cuts, poles or extreme-argument regimes. See the [coverage report](gams-coverage.md) for remaining procedure-class gaps.

## Gamma-family references and precision

The pinned Fullerton APIs use default real, which has 6 decimal digits of precision in the verified GNU build. Calls retain that precision; reference calculations and error measurements use real64. This avoids requiring double-precision accuracy from a single-precision API.

At `x=[0.5,1,1.5,2,2.5,5,10]`, Gamma references are built independently from factorials and half-integer values using `sqrt(pi)`. See [NIST DLMF special values](https://dlmf.nist.gov/5.4) and the [Gamma recurrence](https://dlmf.nist.gov/5.5.E1). The driver checks Gamma relative error, `abs(log_gamma(x)-log(reference))/max(1,abs(log(reference)))`, and `abs(reciprocal_gamma(x)*reference-1)`, all within `3e-6`. This independently checks all three outputs, rather than relying only on Gamma times reciprocal-Gamma being one.

## Digamma references and identities

At the same seven arguments, the digamma driver uses harmonic sums and the Euler constant: `psi(n)=H(n-1)-Euler`, `psi(1/2)=-Euler-2*log(2)`, with half-integer shifts formed arithmetically. These [special values](https://dlmf.nist.gov/5.4#ii) provide independent anchors with absolute error at most `5e-6`.

Additional checks use the [recurrence](https://dlmf.nist.gov/5.5.E2) at `[0.25,0.5,1.5,3.25,10]` and [reflection relation](https://dlmf.nist.gov/5.5.E4) at `[0.125,0.25,0.375]`: `psi(x+1)-psi(x)=1/x` and `psi(1-x)-psi(x)=pi/tan(pi*x)`. Each absolute residual must be at most `5e-6`. All values and identity residuals must be finite.

## Modified Bessel references and identities

The fortran-bessels driver tests all four named functions at `[0.125,0.25,0.5,1,2,4,8]`. Its embedded reference table was independently generated with mpmath 1.3.0 at 80 decimal digits, printed with 23 significant digits and rounded into the package's `BK` kind. That kind has 15 decimal digits in the verified build. Every function must have relative table error at most `2e-12` and finite positive values.

It independently sums the positive-term [I-function series](https://dlmf.nist.gov/10.25.E2) for orders 0 and 1 until both next terms are below working epsilon times their sums; relative agreement must be within `2e-12`. It also checks `abs(x*(I0*K1+I1*K0)-1)<=1e-11`, the order-zero [Wronskian identity](https://dlmf.nist.gov/10.28.E2). The table supplies independent anchors for K0/K1 as well; an identity by itself could hide correlated errors.

The reference table can be regenerated separately from the playground:

```python
import mpmath as mp
mp.mp.dps = 80
for text in ("0.125", "0.25", "0.5", "1", "2", "4", "8"):
    x = mp.mpf(text)
    values = (mp.besseli(0,x), mp.besseli(1,x), mp.besselk(0,x), mp.besselk(1,x))
    print(text, *(mp.nstr(v,23) for v in values))
```

mpmath is needed only to regenerate references. The self-contained Fortran driver and the backend do not depend on it.

## Carlson elliptic-integral references

The C14 driver checks three diagonal identities `RF(x,x,x)=1/sqrt(x)` at `x=[0.25,1,4]`, three positive triples `(0.25,1,4)`, `(1,2,4)`, `(2,3,5)`, and complete elliptic integrals `K(k)=RF(0,1-k^2,1)` at `k=[0,0.25,0.75,0.95]`. For positive triples, substitution `u=t^(-2)-1` in the [defining RF integral](https://dlmf.nist.gov/19.16.E1) gives a smooth integral from 0 to 1 with integrand `product(1+(x_i-1)*t^2)^(-1/2)`. Independent composite Simpson sums at 2048 and 4096 panels must agree; the fine sum is the reference. K references use 4096 panels in `integral_0^(pi/2) (1-k^2*sin(theta)^2)^(-1/2) dtheta`.

Three cyclic-permutation and three scale checks supply secondary identities: `RF(y,z,x)=RF(x,y,z)` and `RF(4*x,4*y,4*z)=RF(x,y,z)/2`. All checked results/references must be finite, all RF statuses zero, and scaled error `abs(actual-reference)/max(1,abs(reference))` at most `2e-11`. This does not validate singular moduli, extreme scaling or other Carlson functions.

## Bernoulli references and power sums

The C19 driver checks `B0=1`, `B1=-1/2` and even `B2..B12` against `[1/6,-1/30,1/42,-1/30,5/66,-691/2730]`. It then evaluates the Bernoulli formula for `sum(m^p,m=0..n-1)` at powers 1..8 and `n=[3,10,20]`, comparing 24 results against direct int64 summation. The small integer powers, binomial coefficients and sums fit in int64. Finite scaled errors must be at most `3e-12`.

**Pinned API limitation:** `bernob` leaves odd output positions above B1 unassigned. The driver never reads them: it supplies their known mathematical zeros locally for the power-sum application. This verifies returned even values and B0/B1, not a fully initialized Bernoulli output array. The implementation also writes B0..B2 unconditionally, so calls with `n<2` are outside the driver. These source-level restrictions are recorded in the procedure notes.

## Complex AMOS Bessel references and pinned failure

The C10 driver checks 39 complex values at `z=[0.5+0.25i,1+0.5i,2+0.75i]`. For starting orders `[0.3,0.5,1.25]`, it requests two successive J and I values and compares with independent [J](https://dlmf.nist.gov/10.2.E2) and [I](https://dlmf.nist.gov/10.25.E2) power series using intrinsic Gamma. A 100-term cap and explicit convergence requirement protect the references. K at order 1/2 is checked against [sqrt(pi/(2*z))*exp(-z)](https://dlmf.nist.gov/10.39.E2). Every status and underflow count must be zero; both components must be finite and complex scaled error at most `2e-12`. Only unscaled mode `KODE=1` is tested.

**Pinned failure:** `J_0.3(2-0.75i)` returns approximately `-0.0312577+0.6118974i` instead of `0.4766625+0.3849523i`, a scaled discrepancy about 0.556. The independent series agrees with mpmath 1.3.0 at 80 decimal digits. The [failing source](gams-candidates/amosf90/lower-half-plane-series.f90) and [saved sandbox result with the high-precision reference](gams-candidates/amosf90/lower-half-plane-result.json) are retained for reporting upstream. The checked driver uses upper-right-quadrant arguments and explicitly excludes this known failing case; no package patch or tolerance relaxation is applied. This establishes selected checked usage, not full-domain AMOS correctness.

## Sources and playground links

| Driver | Class | Pinned procedure and author example |
| --- | --- | --- |
| [Load fullerton-gamma-values](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-fullerton-gamma-values) · [Source](../fpm_catalog/gams-drivers/fullerton-gamma-values.f90) | C7a | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L14) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/gamma/test_gamma.f90) |
| [Load fullerton-digamma-values](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-fullerton-digamma-values) · [Source](../fpm_catalog/gams-drivers/fullerton-digamma-values.f90) | C7c | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L42) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/gamma/test_gamma.f90) |
| [Load bessels-modified-values](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-bessels&example=gams-bessels-modified-values) · [Source](../fpm_catalog/gams-drivers/bessels-modified-values.f90) | C10b1 | [Procedure](https://github.com/perazz/fortran-bessels/blob/7bf8d6b144b00d4201a782ca65f6ae14a84d49a1/src/bessels.f90#L752) · [Author example/test](https://github.com/perazz/fortran-bessels/blob/7bf8d6b144b00d4201a782ca65f6ae14a84d49a1/test/bessels_test.f90) |
| [Load carlson-rf-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=carlson-elliptic-integrals&example=gams-carlson-rf-reference) · [Source](../fpm_catalog/gams-drivers/carlson-rf-reference.f90) | C14 | [Procedure](https://github.com/jacobwilliams/carlson-elliptic-integrals/blob/5f25a59a555b7029505aac71a8341d5851f8abed/src/carlson_elliptic_module.F90#L580) |
| [Load bernoulli-power-sums](https://beliavsky.github.io/fortran-playground/fpm/?package=specfun&example=gams-bernoulli-power-sums) · [Source](../fpm_catalog/gams-drivers/bernoulli-power-sums.f90) | C19 | [Procedure](https://github.com/jacobwilliams/specfun/blob/e74d9c810d5c9248b5d8ffab4b766e7bb22ffd23/src/specfun.F90#L776) |
| [Load amos-complex-series](https://beliavsky.github.io/fortran-playground/fpm/?package=amosf90&example=gams-amos-complex-series) · [Source](../fpm_catalog/gams-drivers/amos-complex-series.f90) | C10 | [Procedure](https://github.com/Euler-37/amosf90/blob/b54a4d4a1d8f7c97acd180ed5bbaae8d089a9fa7/src/amos.f90#L4548) · [Author example/test](https://github.com/Euler-37/amosf90/blob/b54a4d4a1d8f7c97acd180ed5bbaae8d089a9fa7/test/check.f90) |
| [Load fastmath-exp-log-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fastmath&example=gams-fastmath-exp-log-reference) · [Source](../fpm_catalog/gams-drivers/fastmath-exp-log-reference.f90) | C4b | [Procedure](https://github.com/perazz/fastmath/blob/ad0f14c455205c0e6c1b9300cd7f333fafb750e2/src/fast_exp.f90#L76) · [Author example/test](https://github.com/perazz/fastmath/blob/ad0f14c455205c0e6c1b9300cd7f333fafb750e2/test/test.f90) |
| [Load fastmath-rsqrt-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fastmath&example=gams-fastmath-rsqrt-reference) · [Source](../fpm_catalog/gams-drivers/fastmath-rsqrt-reference.f90) | C2 | [Procedure](https://github.com/perazz/fastmath/blob/ad0f14c455205c0e6c1b9300cd7f333fafb750e2/src/fast_rsqrt.f90#L55) · [Author example/test](https://github.com/perazz/fastmath/blob/ad0f14c455205c0e6c1b9300cd7f333fafb750e2/test/test.f90) |
| [Load rpn-sinc-sech-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran&example=gams-rpn-sinc-sech-reference) · [Source](../fpm_catalog/gams-drivers/rpn-sinc-sech-reference.f90) | C4 | [Procedure](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/src/funcs.f90#L1) · [Author example/test](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/test/test.f90) |
| [Load rpn-beta-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran&example=gams-rpn-beta-reference) · [Source](../fpm_catalog/gams-drivers/rpn-beta-reference.f90) | C7 | [Procedure](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/src/specfun/gamma.f90#L1) |
| [Load stdlib-legendre-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-legendre-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-legendre-reference.f90) | C3a2 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L8) |
| [Load stdlib-complex-gamma-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-gamma-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-complex-gamma-reference.f90) | C7a | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L396) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90) |
| [Load stdlib-complex-loggamma-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-loggamma-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-complex-loggamma-reference.f90) | C7a | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L978) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90) |
| [Load stdlib-log-factorial-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-log-factorial-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-log-factorial-reference.f90) | C7a | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L51) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90) |
| [Load stdlib-lower-gamma-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-lower-gamma-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-lower-gamma-reference.f90) | C7e | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L62) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90) |
| [Load stdlib-upper-gamma-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-upper-gamma-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-upper-gamma-reference.f90) | C7e | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L98) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90) |
| [Load stdlib-regularized-gamma-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-regularized-gamma-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-regularized-gamma-reference.f90) | C7e | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L134) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90) |
| [Load stdlib-beta-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-beta-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-beta-reference.f90) | C7b | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L205) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90) |
| [Load stdlib-log-beta-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-log-beta-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-log-beta-reference.f90) | C7b | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L214) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90) |
| [Load stdlib-incomplete-beta-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-incomplete-beta-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-incomplete-beta-reference.f90) | C7f | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions_gamma.f90#L223) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_gamma.f90) |
| [Load stdlib-activation-gaussian-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-gaussian-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-activation-gaussian-reference.f90) | C19 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L32) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90) |
| [Load stdlib-activation-elu-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-elu-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-activation-elu-reference.f90) | C19 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L64) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90) |
| [Load stdlib-activation-relu-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-relu-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-activation-relu-reference.f90) | C19 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L100) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90) |
| [Load stdlib-activation-leaky-relu-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-leaky-relu-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-activation-leaky-relu-reference.f90) | C19 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L132) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90) |
| [Load stdlib-activation-gelu-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-gelu-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-activation-gelu-reference.f90) | C19 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L168) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90) |
| [Load stdlib-activation-selu-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-selu-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-activation-selu-reference.f90) | C19 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L232) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90) |
| [Load stdlib-activation-sigmoid-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-sigmoid-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-activation-sigmoid-reference.f90) | C19 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L264) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90) |
| [Load stdlib-activation-silu-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-silu-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-activation-silu-reference.f90) | C19 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L296) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_specialfunctions_activations.f90) |
| [Load stdlib-activation-softplus-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-activation-softplus-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-activation-softplus-reference.f90) | C19 | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L498) |
| [Load stdlib-complex-phase-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-phase-reference) · [Source](../fpm_catalog/gams-drivers/stdlib-complex-phase-reference.f90) | C4a | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L1106) · [Author example/test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_math_arg.f90) |
| [Load specfunc-fullerton-beta-pairs-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-beta-pairs-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-beta-pairs-reference.f90) | C7b | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_beta.f90#L30) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/beta/test_beta.f90) |
| [Load specfunc-fullerton-airy-values-derivatives-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-airy-values-derivatives-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-airy-values-derivatives-reference.f90) | C10d | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_airy.f90#L39) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/airy/test_airy.f90) |
| [Load specfunc-fullerton-modified-bessel-i01-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-modified-bessel-i01-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-modified-bessel-i01-reference.f90) | C10b1 | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_bessel.f90#L52) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/bessel_i0/test_i0.f90) |
| [Load specfunc-fullerton-modified-bessel-k01-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-modified-bessel-k01-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-modified-bessel-k01-reference.f90) | C10b1 | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_bessel.f90#L458) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/bessel_k0/test_k0.f90) |
| [Load specfunc-fullerton-exponential-logarithmic-integrals-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-exponential-logarithmic-integrals-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-exponential-logarithmic-integrals-reference.f90) | C5 | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_ei.f90#L51) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/ei/test_ei.f90) |
| [Load specfunc-fullerton-positive-exponential-integrals-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-positive-exponential-integrals-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-positive-exponential-integrals-reference.f90) | C5 | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_ei.f90#L62) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/ei/test_ei.f90) |
| [Load specfunc-fullerton-sine-cosine-integrals-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-sine-cosine-integrals-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-sine-cosine-integrals-reference.f90) | C6 | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_ei.f90#L378) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/ei/test_ei.f90) |
| [Load specfunc-fullerton-hyperbolic-integrals-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-hyperbolic-integrals-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-hyperbolic-integrals-reference.f90) | C4d | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_ei.f90#L506) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/ei/test_ei.f90) |
| [Load specfunc-fullerton-dawson-values-derivatives-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-dawson-values-derivatives-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-dawson-values-derivatives-reference.f90) | C8c | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_misc.f90#L211) |
| [Load specfunc-fullerton-real-dilogarithm-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-real-dilogarithm-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-real-dilogarithm-reference.f90) | C5 | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_misc.f90#L386) |
| [Load specfunc-fullerton-near-zero-exponential-logarithm-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-near-zero-exponential-logarithm-reference) · [Source](../fpm_catalog/gams-drivers/specfunc-fullerton-near-zero-exponential-logarithm-reference.f90) | C4b | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_misc.f90#L90) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/misc_exp/test_misc_exp.f90) |

The programs use author APIs, retain applicable license notices and use deterministic reference checks instead of the larger author harnesses. They appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All 41 passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only each main and executable were rebuilt. The [verification report](gams-special-functions-validation.json) records hashes, pins and saved output. These cases establish checked usage and selected-point agreement, rather than accuracy over each function's complete domain.

### fullerton-gamma-values

```text
Default-real precision (decimal digits): 6
       x        Gamma(x)           relative Gamma error   scaled log error   relative reciprocal error
    0.50    1.7724537849E+00        3.721557E-08        1.658650E-08        5.196426E-08
    1.00    1.0000000000E+00        0.000000E+00        0.000000E+00        0.000000E+00
    1.50    8.8622689247E-01        3.721557E-08        3.339232E-08        5.196426E-08
    2.00    1.0000000000E+00        0.000000E+00        0.000000E+00        0.000000E+00
    2.50    1.3293403387E+00        3.721557E-08        3.036405E-08        5.196426E-08
    5.00    2.4000000000E+01        0.000000E+00        8.038898E-09        2.980232E-08
   10.00    3.6288000000E+05        0.000000E+00        3.855416E-09        1.376611E-08
Maximum Gamma/log/reciprocal errors:   3.7216E-08  3.3392E-08  5.1964E-08
PASS fullerton-gamma-values
```

### fullerton-digamma-values

```text
Default-real precision (decimal digits): 6
       x           psi(x)              absolute reference error
    0.50     -1.963510036469E+00            1.044708E-08
    1.00     -5.772156715393E-01            6.637774E-09
    1.50      3.648997470737E-02            7.287886E-10
    2.00      4.227843284607E-01            6.637774E-09
    2.50      7.031567096710E-01            6.902578E-08
    5.00      1.506117701530E+00            3.309866E-08
   10.00      2.251752614975E+00            2.590825E-08
Maximum absolute reference error:   6.9026E-08
Maximum recurrence residual:   1.4901E-07
Maximum reflection residual:   1.9368E-07
PASS fullerton-digamma-values
```

### bessels-modified-values

```text
Bessel kind precision (decimal digits): 15
       x       relative table error     relative I-series error   Wronskian residual
   0.125          2.01139285E-16          2.21611488E-16          1.11022302E-16
   0.250          1.18517783E-16          2.18615373E-16          2.22044605E-16
   0.500          0.00000000E+00          2.15247681E-16          0.00000000E+00
   1.000          0.00000000E+00          1.75381557E-16          0.00000000E+00
   2.000          0.00000000E+00          1.94811402E-16          0.00000000E+00
   4.000          1.57172988E-16          1.57172988E-16          2.22044605E-16
   8.000          3.70108880E-16          2.84307265E-16          4.44089210E-16
Maximum relative table error (all four functions):   3.7011E-16
Maximum relative I0/I1 series error:   2.8431E-16
Maximum Wronskian residual:   4.4409E-16
PASS bessels-modified-values
```

### carlson-rf-reference

```text
k             Complete elliptic K(k)
  0.00        1.5707963267948968
  0.25        1.5962422221317838
  0.75        1.9109897807518292
  0.95        2.5900112308745018
Maximum scaled reference/identity error:   1.2257E-13
PASS carlson-rf-reference
```

### bernoulli-power-sums

```text
B(0) =       1.000000000000000
B(1) =      -0.500000000000000
B(2) =       0.166666666666667
B(4) =      -0.033333333333276
B(6) =       0.023809523809522
B(8) =      -0.033333333333333
B(10) =       0.075757575757576
B(12) =      -0.253113553113553
Independent integer power sums checked: 24
Maximum scaled error:   7.5865E-13
Odd outputs above B1 are unassigned at this pin and are not read.
PASS bernoulli-power-sums
```

### amos-complex-series

```text
z =     0.5000    0.2500; K_0.5(z) =       0.900965265411     -0.471142820764
z =     1.0000    0.5000; K_0.5(z) =       0.324403658502     -0.291381750651
z =     2.0000    0.7500; K_0.5(z) =       0.069439816411     -0.092990708451
Independent complex Bessel values checked: 39
Maximum scaled error:   3.5643E-16
PASS amos-complex-series
```

### fastmath-exp-log-reference

```text
641 points x=-80..80 in steps of 0.25; log arguments exp(x).
Maximum exponential relative error versus intrinsic exp:   3.1976E-06
Maximum logarithm absolute error versus x:   2.9987E-04
Maximum approximate exp/log round-trip relative error:   2.9982E-04
Positive exponentials, grid monotonicity and scalar/array consistency checked.
PASS fastmath-exp-log-reference
```

### fastmath-rsqrt-reference

```text
168 exact dyadic squares: roots (m/8)*2**k, m=8..15, k=-250..250 step 25.
Maximum relative error versus reciprocal of known root:   1.7267E-03
Maximum normalized residual abs(x*y*y-1):   3.4503E-03
Finite positive results and scalar/array consistency checked.
PASS fastmath-rsqrt-reference
```

### rpn-sinc-sech-reference

```text
133 real arguments: -8..8 step 0.125, plus signed near-zero values.
Maximum sinc absolute error versus 64-term power series:   8.2434E-15
Maximum sech absolute error versus exponential formula:   1.1102E-16
Zero values, even symmetry, sech range and scalar/array consistency checked.
PASS rpn-sinc-sech-reference
```

### rpn-beta-reference

```text
128 positive integer/half-integer pairs; 512 beta evaluations checked.
Independent factorial identities, symmetry and both one-step recurrences checked.
Maximum relative error against closed-form references:   4.4409E-16
PASS rpn-beta-reference
```

### stdlib-legendre-reference

```text
363 Legendre values and 363 derivatives, degrees 0..10, versus explicit polynomial coefficients
PASS stdlib-legendre-reference
```

### stdlib-complex-gamma-reference

```text
24 complex references from independent 80/120-digit mpmath evaluations
PASS stdlib-complex-gamma-reference
```

### stdlib-complex-loggamma-reference

```text
24 complex references from independent 80/120-digit mpmath evaluations
PASS stdlib-complex-loggamma-reference
```

### stdlib-log-factorial-reference

```text
201 log-factorials versus summed logarithms; upstream result is REAL32 (tolerance 2e-6)
PASS stdlib-log-factorial-reference
```

### stdlib-lower-gamma-reference

```text
Finite Poisson-sum reference pairs (integer-valued REAL64 shapes 1..8, x=0..8): 264
PASS stdlib-lower-gamma-reference
```

### stdlib-upper-gamma-reference

```text
Finite Poisson-sum reference pairs (integer-valued REAL64 shapes 1..8, x=0..8): 264
PASS stdlib-upper-gamma-reference
```

### stdlib-regularized-gamma-reference

```text
Finite Poisson-sum reference pairs (integer-valued REAL64 shapes 1..8, x=0..8): 264
PASS stdlib-regularized-gamma-reference
```

### stdlib-beta-reference

```text
288 beta-family references using independent finite products, shapes 1..12
PASS stdlib-beta-reference
```

### stdlib-log-beta-reference

```text
288 beta-family references using independent finite products, shapes 1..12
PASS stdlib-log-beta-reference
```

### stdlib-incomplete-beta-reference

```text
2112 regularized incomplete-beta references versus independent binomial tail sums
PASS stdlib-incomplete-beta-reference
```

### stdlib-activation-gaussian-reference

```text
Independent 80/120-digit activation references: values=97, derivatives=97
PASS stdlib-activation-gaussian-reference
```

### stdlib-activation-elu-reference

```text
Independent 80/120-digit activation references: values=291, derivatives=288
PASS stdlib-activation-elu-reference
```

### stdlib-activation-relu-reference

```text
Independent 80/120-digit activation references: values=97, derivatives=96
PASS stdlib-activation-relu-reference
```

### stdlib-activation-leaky-relu-reference

```text
Independent 80/120-digit activation references: values=291, derivatives=288
PASS stdlib-activation-leaky-relu-reference
```

### stdlib-activation-gelu-reference

```text
Independent 80/120-digit activation references: values=97, derivatives=0
PASS stdlib-activation-gelu-reference
```

### stdlib-activation-selu-reference

```text
Independent 80/120-digit activation references: values=97, derivatives=96
PASS stdlib-activation-selu-reference
```

### stdlib-activation-sigmoid-reference

```text
Independent 80/120-digit activation references: values=97, derivatives=97
PASS stdlib-activation-sigmoid-reference
```

### stdlib-activation-silu-reference

```text
Independent 80/120-digit activation references: values=97, derivatives=0
PASS stdlib-activation-silu-reference
```

### stdlib-activation-softplus-reference

```text
Independent 80/120-digit activation references: values=97, derivatives=97
PASS stdlib-activation-softplus-reference
```

### stdlib-complex-phase-reference

```text
Independent quadrant phase references: 600 (radians, degrees, pi units)
PASS stdlib-complex-phase-reference
```

### specfunc-fullerton-beta-pairs-reference

```text
Positive integer/half-integer beta and log-beta reference pairs: 64
PASS specfunc-fullerton-beta-pairs-reference
```

### specfunc-fullerton-airy-values-derivatives-reference

```text
Default REAL32 function comparisons with independent references: 56
Maximum relative error (reference floor 1e-30):   4.7517E-06
PASS specfunc-fullerton-airy-values-derivatives-reference
```

### specfunc-fullerton-modified-bessel-i01-reference

```text
Default REAL32 function comparisons with independent references: 36
Maximum relative error (reference floor 1e-30):   1.2325E-07
PASS specfunc-fullerton-modified-bessel-i01-reference
```

### specfunc-fullerton-modified-bessel-k01-reference

```text
Default REAL32 function comparisons with independent references: 18
Maximum relative error (reference floor 1e-30):   2.0714E-07
PASS specfunc-fullerton-modified-bessel-k01-reference
```

### specfunc-fullerton-exponential-logarithmic-integrals-reference

```text
Default REAL32 function comparisons with independent references: 25
Maximum relative error (reference floor 1e-30):   1.8218E-06
PASS specfunc-fullerton-exponential-logarithmic-integrals-reference
```

### specfunc-fullerton-positive-exponential-integrals-reference

```text
Default REAL32 function comparisons with independent references: 29
Maximum relative error (reference floor 1e-30):   1.9123E-07
PASS specfunc-fullerton-positive-exponential-integrals-reference
```

### specfunc-fullerton-sine-cosine-integrals-reference

```text
Default REAL32 function comparisons with independent references: 18
Maximum relative error (reference floor 1e-30):   1.6805E-07
PASS specfunc-fullerton-sine-cosine-integrals-reference
```

### specfunc-fullerton-hyperbolic-integrals-reference

```text
Default REAL32 function comparisons with independent references: 20
Maximum relative error (reference floor 1e-30):   5.2300E-07
PASS specfunc-fullerton-hyperbolic-integrals-reference
```

### specfunc-fullerton-dawson-values-derivatives-reference

```text
Default REAL32 function comparisons with independent references: 28
Maximum relative error (reference floor 1e-30):   1.8587E-05
PASS specfunc-fullerton-dawson-values-derivatives-reference
```

### specfunc-fullerton-real-dilogarithm-reference

```text
Default REAL32 function comparisons with independent references: 12
Maximum relative error (reference floor 1e-30):   6.6263E-08
PASS specfunc-fullerton-real-dilogarithm-reference
```

### specfunc-fullerton-near-zero-exponential-logarithm-reference

```text
Default REAL32 function comparisons with independent references: 38
Maximum relative error (reference floor 1e-30):   8.1069E-08
PASS specfunc-fullerton-near-zero-exponential-logarithm-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fullerton-gamma-values fullerton-digamma-values bessels-modified-values
python xverify_gams_drivers.py --drivers carlson-rf-reference bernoulli-power-sums amos-complex-series
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
