# Checked GAMS special-function drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [C7a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C7a) | Gamma, log-Gamma and reciprocal-Gamma at positive real arguments | Fullerton `fgamma`, `log_gamma`, `reciprocal_gamma` |
| [C7c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C7c) | Psi/digamma at positive real arguments | Fullerton `digamma` |
| [C10b1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/C10b1) | Modified Bessel I/K, real arguments and integer orders; tested orders 0 and 1 | fortran-bessels `besseli0`, `besseli1`, `besselk0`, `besselk1` |

These demonstrate selected positive arguments and named procedures. They do not exhaust their GAMS classes or cover arbitrary orders, complex arguments, poles or extreme-argument regimes. See the [coverage report](gams-coverage.md) for remaining procedure-class gaps.

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

## Sources and playground links

| Driver | Class | Pinned procedure and author example |
| --- | --- | --- |
| [Load fullerton-gamma-values](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-fullerton-gamma-values) · [Source](../fpm_catalog/gams-drivers/fullerton-gamma-values.f90) | C7a | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L14) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/gamma/test_gamma.f90) |
| [Load fullerton-digamma-values](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-fullerton-digamma-values) · [Source](../fpm_catalog/gams-drivers/fullerton-digamma-values.f90) | C7c | [Procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L42) · [Author example/test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/gamma/test_gamma.f90) |
| [Load bessels-modified-values](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-bessels&example=gams-bessels-modified-values) · [Source](../fpm_catalog/gams-drivers/bessels-modified-values.f90) | C10b1 | [Procedure](https://github.com/perazz/fortran-bessels/blob/7bf8d6b144b00d4201a782ca65f6ae14a84d49a1/src/bessels.f90#L752) · [Author example/test](https://github.com/perazz/fortran-bessels/blob/7bf8d6b144b00d4201a782ca65f6ae14a84d49a1/test/bessels_test.f90) |

The programs adapt author API patterns, retain license notices and use deterministic reference checks instead of the larger author harnesses. They appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only each main and executable were rebuilt. The [verification report](gams-special-functions-validation.json) records hashes, pins and saved output. These cases establish checked usage and selected-point agreement, rather than accuracy over each function's complete domain.

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers fullerton-gamma-values fullerton-digamma-values bessels-modified-values
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
