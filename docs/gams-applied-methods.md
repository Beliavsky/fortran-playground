# Checked GAMS fitting, time-series and iterated-integration drivers

| Class | Problem | Package |
| --- | --- | --- |
| K1 | Least-squares approximation with a cubic-spline basis | splpak |
| L10a2a | Time-series summary autocovariance and autocorrelation | fortsa |
| H2b1a2 | Nonautomatic multidimensional/iterated integration | integrate_fortran |

These class-specific links select checked drivers. They verify the configurations below, not every package capability. The GAMS categories are not exhausted.

## Known least-squares spline fits

The splpak driver fits 24 observations at 12 coordinates in [0,1], each coordinate occurring twice. Three datasets have known fitted functions: `2*x`, `1-3*x` with paired noise `+1/4,-1/4`, and the constant `-2.25` with nonuniform positive weights (equal within each pair). Ten spline nodes/coefficients and the author API's `xtrap=1` setting are used.

For the noisy data, each equal-weight pair contributes `2*(fitted-true_line)^2 + 2*(1/4)^2` to the objective. Thus the known line is the least-squares fit and its training sum of squared errors is exactly `24*(1/4)^2=1.5`. This is a nonzero-residual check, not just interpolation of noiseless data. The other datasets have zero reference residual.

Each fitted function and its first derivative are checked at 21 points, including both endpoints: 126 independent value/derivative comparisons. Maximum absolute value error must be at most `1e-8`; derivative error at most `1e-7`. Initialization/evaluation statuses must be zero, values finite, noisy SSE within `1e-8` of 1.5 and the noiseless training SSE at most `1e-14`. The driver destroys state between fits. General curved-function fitting, multidimensional fitting, extrapolation and ill-conditioned data are outside the example.

## Autocovariance and autocorrelation references

The fortsa driver uses the eight observations `[1,-1,2,-2,3,-3,4,-4]`, a shift by 10, a transformation `-2*base+3`, and a constant series 7. For every lag 0..7, scalar loops independently form `sum((x_i-mean)*(x_(i+lag)-mean))/N`. This is the biased normalization by N, not the lag-dependent denominator N-lag. Three base-series anchors are `gamma(0)=7.5`, `gamma(1)=-6.25`, `gamma(7)=-0.5`.

The public `acvf`, `acvf_opt` direct method 0, and FFT method 1 each must agree with these independent sums: 12 covariance calls, each with eight outputs. For the three nonconstant datasets, `acvf2acf` is checked against `gamma(lag)/gamma(0)`: nine calls with eight outputs. All outputs must be finite and maximum absolute errors at most `1e-10`. Constant-series covariance is checked as zero; its undefined zero-variance correlation is deliberately not requested. Missing data, partial correlations, other estimators and ARIMA fitting are not verified.

## Fixed-rule multidimensional polynomial moments

The integrate_fortran driver supplies module callbacks to `gauss_leg_nd`. Its `js` entries are panel counts per dimension, not quadrature orders. Every panel uses the implementation's fixed six-point Gauss-Legendre rule; the caller chooses the panels and no adaptive error estimate is promised.

Fifty checks integrate `x^p*y^q`, p,q=0..4, over `[-1,2]` times `[0,3]` using one and two panels per dimension. References are products of exact monomial antiderivatives. Sixteen more checks use p,q=0..3 over `0<=x<=1`, `0<=y<=1+x^2`, with the independent reference `sum(binomial(q+1,r)/((q+1)*(p+2*r+1)),r=0..q+1)`. This polynomial has x degree at most 11 after integrating y. A final 3D box check integrates `x^2*y^3*z` over `[-1,1]` times `[0,2]` times `[1,3]`, with exact value `32/3`.

All 67 results must be finite with scaled error `abs(actual-reference)/max(1,abs(reference))<=1e-11`. The bounds callback reads x only for the second variable in the iterated case, after the first variable is defined. Singular, infinite-domain and highly oscillatory integrands, invalid panel counts and automatic accuracy selection are outside this verification.

## Sources, playground links and saved output

All three passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only the mains and executables were compiled. The [verification report](gams-applied-methods-validation.json) records source hashes and actual output. The independently written drivers have their own MIT notice; upstream package licenses remain separate. Loading a link selects source without submitting a job; the examples appear in hosted and main local FPM menus.

### splpak-paired-noise-fit

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=splpak&example=gams-splpak-paired-noise-fit) / [Driver source](../fpm_catalog/gams-drivers/splpak-paired-noise-fit.f90) / [Pinned procedure](https://github.com/jacobwilliams/splpak/blob/35340cb2d193c7aa44f03978db21660df8297cc0/src/splpak.F90#L45)

[Pinned author test](https://github.com/jacobwilliams/splpak/blob/35340cb2d193c7aa44f03978db21660df8297cc0/test/splpak_test.f90)

```text
Fit 1 training SSE:     0.000000000000
Fit 2 training SSE:     1.500000000000
Fit 3 training SSE:     0.000000000000
Maximum value/derivative errors:    3.10862E-15   3.29736E-14
PASS splpak-paired-noise-fit
```

### fortsa-autocorrelation-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortsa&example=gams-fortsa-autocorrelation-reference) / [Driver source](../fpm_catalog/gams-drivers/fortsa-autocorrelation-reference.f90) / [Pinned procedure](https://github.com/zoziha/fortsa/blob/d31da12286617ab82e06e9fa0a6f20d11778581c/src/fortsa_stats.f90#L18)

[Pinned author test](https://github.com/zoziha/fortsa/blob/d31da12286617ab82e06e9fa0a6f20d11778581c/test/stats/test_stats.f90)

```text
Lag       Direct autocorrelation
  0        1.00000000000000
  1       -0.83333333333333
  2        0.66666666666667
  3       -0.51666666666667
  4        0.36666666666667
  5       -0.25000000000000
  6        0.13333333333333
  7       -0.06666666666667
Covariance/correlation calls checked:    12    9
Maximum absolute error:    3.55271E-15
Constant-series covariance checked; zero-variance correlation is undefined and is not requested.
PASS fortsa-autocorrelation-reference
```

### integrate-nd-polynomial-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=integrate_fortran&example=gams-integrate-nd-polynomial-reference) / [Driver source](../fpm_catalog/gams-drivers/integrate-nd-polynomial-reference.f90) / [Pinned procedure](https://github.com/Euler-37/integrate_fortran/blob/5281426a7407aa8cef7f684ff8cf1f7e4a4df906/src/gauss_leg.f90#L34)

[Pinned author test](https://github.com/Euler-37/integrate_fortran/blob/5281426a7407aa8cef7f684ff8cf1f7e4a4df906/test/check.f90)

```text
3D integral of x^2*y^3*z:      10.66666666666667
Exact polynomial integral checks: 67
Maximum scaled error:    5.31644E-16
Panel counts are explicit; each panel uses six Gauss-Legendre nodes per dimension.
PASS integrate-nd-polynomial-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers splpak-paired-noise-fit fortsa-autocorrelation-reference integrate-nd-polynomial-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining classes without checked drivers.
