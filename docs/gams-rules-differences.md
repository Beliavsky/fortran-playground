# Checked quadrature rules and periodic finite differences

These H2c and H1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-rules-differences-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Exact polynomial moments: Kronrod (H2c)

The unchanged original internal procedures are exposed through the checksum-guarded playground_kronrod catalog module. The driver independently requests Gauss orders 2,3,4,5,6,7,10 and their 2*n+1-node symmetric Kronrod extensions. The package returns the nonnegative half in descending order. Every Kronrod weight must be positive, every embedded Gauss weight nonnegative, nodes strictly ordered in [0,1), and the central node zero within 1e-50. Counting reflected nonzero Gauss weights must give exactly n nodes.

Using MPFUN arithmetic, the driver checks 64 Kronrod even moments through the even portion of degree 3*n+1+mod(n,2), and 37 embedded Gauss even moments through degree 2*n-2. Exact references are 2/(p+1) for integral x**p on [-1,1]. Odd moments on the symmetric interval cancel by construction and are not counted as independent checks. An additional 54 moments on [1,3] use explicitly reflected nodes 2+x and 2-x; powers 0 through min(2*n-1,8), including odd powers, must match (3**(p+1)-1)/(p+1). The total is 155 exact polynomial moments. Node iteration requests 1e-50; every moment error divided by max(1,abs(reference)) must be at most 1e-40. The package is configured for at least 1000 decimal digits. This does not independently validate MPFUN arithmetic, all orders, error estimators or adaptive integration.

Gauss order 1 is not verified. A separate three-node probe failed even the constant integral: its weights summed to about 1.156959262120 instead of 2. Its source and actual failed result are retained in the [candidate notes](gams-candidates/kronrod/README.md). Later cases in that probe were not reached. The seven public orders were separately run and passed without relaxing the original moment tolerance. The author main normally demonstrates orders 7 through 87; the cause of the small-order failure is not established.

## Fourier modes and convergence: Tsunami Chapter 4 (H1)

The original serial mod_diff module returns raw differences without division by physical grid spacing. This independent consumer explicitly divides by h=2*pi/n on periodic grids of 16,32,64,128,256 cells. Ninety fixtures combine sine/cosine, wavenumbers 1,2,3 and phases 0,0.37,1.1. Grid samples are rounded to REAL32, matching the API; reference formulas and RMS error accumulation use REAL64.

For a sine mode with theta=k*x+phase and q=k*h, the exact discrete centered derivative is sin(q)*cos(theta)/h and the upwind derivative is ((1-cos(q))*sin(theta)+sin(q)*cos(theta))/h. The cosine counterparts are -sin(q)*sin(theta)/h and ((1-cos(q))*cos(theta)-sin(q)*sin(theta))/h. All results must be finite. Maximum absolute discrepancy from these formulas must be at most 8*epsilon(REAL32)/h, explicitly allowing input/stencil roundoff amplification by grid spacing.

Five additional nonsmooth, exactly representable dyadic fixtures check every output against independently indexed left/right neighbors, including both wraparound boundaries, and require exact telescoping sums of zero. Five constant fixtures require exact zero derivatives. Continuous sine-derivative RMS errors on successive grids must decrease with ratios in [3.8,4.2] for the centered stencil and [1.9,2.1] for the upwind stencil. This checks second-order and first-order convergence over the recorded grids; it does not promise continued refinement below REAL32 roundoff.

This H1 driver does not verify PDE evolution, other chapters, coarrays, parallel scaling or nonperiodic boundaries. The ordinary package demo still illustrates wave evolution, but it is not promoted to a class-specific PDE driver by these differentiation checks.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream terms remain separate. Author sources were reviewed for interfaces, and no upstream implementation or test code is copied. Loading a link does not submit a job.

### kronrod-moments-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=kronrod&example=gams-kronrod-moments-reference) / [Driver source](../fpm_catalog/gams-drivers/kronrod-moments-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/kronrod/blob/312278846b6e403fdea410a823d88ef4fb92a3cc/app/main.f90#L1) / [Author example/test](https://github.com/jacobwilliams/kronrod/blob/312278846b6e403fdea410a823d88ef4fb92a3cc/app/main.f90)

```text
Gauss order 2; Kronrod nodes 5
Gauss order 3; Kronrod nodes 7
Gauss order 4; Kronrod nodes 9
Gauss order 5; Kronrod nodes 11
Gauss order 6; Kronrod nodes 13
Gauss order 7; Kronrod nodes 15
Gauss order 10; Kronrod nodes 21
Kronrod / Gauss / translated polynomial moments:    64   37   54
Maximum normalized moment error:    6.6667E-103
PASS kronrod-moments-reference
```

### tsunami-differences-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=tsunami&example=gams-tsunami-differences-reference) / [Driver source](../fpm_catalog/gams-drivers/tsunami-differences-reference.f90) / [Pinned procedure](https://github.com/modern-fortran/tsunami/blob/70b5702aed42bbea0733335d50e0eb70cb159e08/src/ch04/mod_diff.f90#L1) / [Author example/test](https://github.com/modern-fortran/tsunami/blob/70b5702aed42bbea0733335d50e0eb70cb159e08/src/ch04/tsunami.f90)

```text
N=16; centered/upwind RMS errors:   1.80345E-02  1.38246E-01
N=32; centered/upwind RMS errors:   4.53479E-03  6.93457E-02
N=64; centered/upwind RMS errors:   1.13534E-03  3.47007E-02
N=128; centered/upwind RMS errors:   2.83939E-04  1.73538E-02
N=256; centered/upwind RMS errors:   7.09932E-05  8.67736E-03
Fourier fixtures: 90; nonsmooth/constant fixtures: 10
Maximum exact-discrete derivative error:   2.3591E-06
Minimum refinement ratios, centered/upwind:    3.97692   1.99358
PASS tsunami-differences-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers kronrod-moments-reference tsunami-differences-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
