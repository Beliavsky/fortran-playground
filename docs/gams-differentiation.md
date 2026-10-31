# Checked GAMS differentiation drivers

All three drivers belong to [H1: Numerical differentiation](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H1). They use the same scalar function and evaluation points, making differences in API and method visible. This does not validate every derivative interface in these packages. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Shared problem and independent references

For `f(x)=exp(x)*sin(x)`, elementary differentiation gives:

```text
df/dx   = exp(x)*(sin(x)+cos(x))
d2f/dx2 = 2*exp(x)*cos(x)
d3f/dx3 = 2*exp(x)*(cos(x)-sin(x))
```

Each driver evaluates at `x=[-0.5,0,0.5,1]` using real64 precision. Expected derivatives come from these formulas, independently of the package under test. The scaled error is `abs(computed-reference)/max(1,abs(reference))`. All checked results must be finite. The AD driver also checks the function value.

## Configurations and acceptance criteria

| Package | Method | Orders | Settings and maximum scaled errors |
| --- | --- | --- | --- |
| NumDiff | Adaptive finite differences using Neville extrapolation | 1, 2, 3 | Requested absolute errors `1e-8,1e-8,1e-6`; scaled-error bounds `1e-7,1e-7,1e-6` |
| ForDiff | Forward and backward finite differences | 1 | Step `1e-5`; scaled-error bound `5e-5` |
| ForDiff | Central finite differences | 1 | Step `1e-5`; scaled-error bound `1e-9` |
| ForDiff | Complex step | 1 | Step `1e-20`; scaled-error bound `5e-14` |
| AD_dnSVM | Forward automatic differentiation using overloaded scalar type | 0 through 3 | One independent variable; scaled-error bound `5e-14` |

NumDiff uses the allowed interval `[-0.5,1]`, so the two endpoint cases require one-sided formulas. Every call must return status zero and a nonnegative error estimate within the requested absolute tolerance. The analytic error must also fit the estimate plus `64*epsilon*max(1,abs(reference))` for rounding. An initial trial requesting `1e-8` for all orders could not satisfy the third-derivative request at the lower endpoint. The published driver explicitly requests `1e-6` for third derivatives and retains the status and independent accuracy checks.

ForDiff follows the author's scalar example and supplies separate real and complex callbacks. Complex step requires a complex analytic extension of the function; it is not generally valid for callbacks containing operations such as `abs` or branches that discard the imaginary perturbation. This driver does not validate the vector overloads or choose optimal step sizes automatically.

AD_dnSVM follows the author's `Variable` pattern, requesting `nderiv=3`, and extracts `get_d0`, `get_d1`, `get_d2` and `get_d3`. It checks the one-element derivative tensor sizes and compares ordinary derivatives, without factorial rescaling. Multivariate mixed partials are outside this example.

## Sources and playground links

| Driver | Pinned procedure and author example |
| --- | --- |
| [Load numdiff-analytic-derivatives](https://beliavsky.github.io/fortran-playground/fpm/?package=numdiff&example=gams-numdiff-analytic-derivatives) / [Source](../fpm_catalog/gams-drivers/numdiff-analytic-derivatives.f90) | [Procedure](https://github.com/jacobwilliams/NumDiff/blob/687157df8d2dec072b5484974bab71f7b14b0e9f/src/diff_module.f90#L33) / [Author example](https://github.com/jacobwilliams/NumDiff/blob/687157df8d2dec072b5484974bab71f7b14b0e9f/test/diff_test.f90) |
| [Load fordiff-analytic-derivatives](https://beliavsky.github.io/fortran-playground/fpm/?package=fordiff&example=gams-fordiff-analytic-derivatives) / [Source](../fpm_catalog/gams-drivers/fordiff-analytic-derivatives.f90) | [Procedure](https://github.com/gha3mi/fordiff/blob/f1a1099a590107645314f1388c432624ff97b9bc/src/fordiff.F90#L26) / [Author example](https://github.com/gha3mi/fordiff/blob/f1a1099a590107645314f1388c432624ff97b9bc/example/demo1.f90) |
| [Load ad-dnsvm-analytic-derivatives](https://beliavsky.github.io/fortran-playground/fpm/?package=ad_dnsvm&example=gams-ad-dnsvm-analytic-derivatives) / [Source](../fpm_catalog/gams-drivers/ad-dnsvm-analytic-derivatives.f90) | [Procedure](https://github.com/lauvergn/AD_dnSVM/blob/32db0bd122ce1dae290e9cf4c1fda4ab8f3de6f1/SRC/ADdnSVM/dnS_m.f90#L236) / [Author example](https://github.com/lauvergn/AD_dnSVM/blob/32db0bd122ce1dae290e9cf4c1fda4ab8f3de6f1/APP/Example_dnS.f90) |

The programs adapt author API patterns and retain license notices. NumDiff and ForDiff use module callbacks to avoid executable-stack trampolines. These drivers appear in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-differentiation-validation.json) records source hashes, pins and saved output. Different methods, tolerances and derivative orders make these demonstrations unsuitable as a general accuracy or performance ranking.

### numdiff-analytic-derivatives

```text
order=1 status=0 estimated error=  9.13E-09
x= -0.5 order=1 derivative=  2.41494E-01 estimate=  9.13E-09
order=2 status=0 estimated error=  4.78E-09
x= -0.5 order=2 derivative=  1.06456E+00 estimate=  4.78E-09
order=3 status=0 estimated error=  8.01E-07
x= -0.5 order=3 derivative=  1.64613E+00 estimate=  8.01E-07
order=1 status=0 estimated error=  4.44E-15
x=  0.0 order=1 derivative=  1.00000E+00 estimate=  4.44E-15
order=2 status=0 estimated error=  9.65E-09
x=  0.0 order=2 derivative=  2.00000E+00 estimate=  9.65E-09
order=3 status=0 estimated error=  8.62E-07
x=  0.0 order=3 derivative=  2.00000E+00 estimate=  8.62E-07
order=1 status=0 estimated error=  7.83E-09
x=  0.5 order=1 derivative=  2.23733E+00 estimate=  7.83E-09
order=2 status=0 estimated error=  6.01E-09
x=  0.5 order=2 derivative=  2.89378E+00 estimate=  6.01E-09
order=3 status=0 estimated error=  6.99E-07
x=  0.5 order=3 derivative=  1.31290E+00 estimate=  6.99E-07
order=1 status=0 estimated error=  8.75E-09
x=  1.0 order=1 derivative=  3.75605E+00 estimate=  8.75E-09
order=2 status=0 estimated error=  7.82E-09
x=  1.0 order=2 derivative=  2.93739E+00 estimate=  7.82E-09
order=3 status=0 estimated error=  8.66E-07
x=  1.0 order=3 derivative= -1.63732E+00 estimate=  8.66E-07
Maximum scaled analytic error:   6.1684E-08
PASS numdiff-analytic-derivatives
```

### fordiff-analytic-derivatives

```text
x= -0.5 forward  derivative=  2.41500E-01
x= -0.5 backward derivative=  2.41489E-01
x= -0.5 central  derivative=  2.41494E-01
x= -0.5 complex  derivative=  2.41494E-01
x=  0.0 forward  derivative=  1.00001E+00
x=  0.0 backward derivative=  9.99990E-01
x=  0.0 central  derivative=  1.00000E+00
x=  0.0 complex  derivative=  1.00000E+00
x=  0.5 forward  derivative=  2.23734E+00
x=  0.5 backward derivative=  2.23731E+00
x=  0.5 central  derivative=  2.23733E+00
x=  0.5 complex  derivative=  2.23733E+00
x=  1.0 forward  derivative=  3.75606E+00
x=  1.0 backward derivative=  3.75603E+00
x=  1.0 central  derivative=  3.75605E+00
x=  1.0 complex  derivative=  3.75605E+00
forward  maximum scaled analytic error:   1.0000E-05
backward maximum scaled analytic error:   1.0000E-05
central  maximum scaled analytic error:   3.3333E-11
complex  maximum scaled analytic error:   1.9849E-16
PASS fordiff-analytic-derivatives
```

### ad-dnsvm-analytic-derivatives

```text
x= -0.5 value and derivatives 1..3:  -2.907863E-01   2.414944E-01   1.064561E+00   1.646134E+00
x=  0.0 value and derivatives 1..3:   0.000000E+00   1.000000E+00   2.000000E+00   2.000000E+00
x=  0.5 value and derivatives 1..3:   7.904391E-01   2.237328E+00   2.893778E+00   1.312900E+00
x=  1.0 value and derivatives 1..3:   2.287355E+00   3.756049E+00   2.937388E+00  -1.637323E+00
Maximum scaled analytic error:   1.6913E-16
PASS ad-dnsvm-analytic-derivatives
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers numdiff-analytic-derivatives fordiff-analytic-derivatives ad-dnsvm-analytic-derivatives
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
