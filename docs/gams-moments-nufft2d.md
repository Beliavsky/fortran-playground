# Checked quadrature moments and two-dimensional Fourier sums

These H2c and J1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-moments-nufft2d-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Exact moments: QDUtilLib (H2c)

Orders 1,2,3,4,6,8,12 for LegendreP and HO give 14 rules. Initialization must succeed and return finite nodes/weights of shape [1,n] and [n], with positive weights. Legendre nodes must be strictly inside [-1,1]. Copied node/weight pairs are sorted before checking symmetry; native ordering is not prescribed. Paired node sums must be at most 1e-11*max(1,maxabs(nodes)); paired effective-weight differences must be at most 1e-11*max(1,maxabs(weights)).

Legendre moments through degree 2*n-1 have exact references zero for odd powers and 2/(p+1) for even powers. HO stores full-function weights: the consumer explicitly includes exp(-x*x) to obtain Gaussian polynomial moments on the real line. Odd Gaussian moments vanish; even references start at M0=sqrt(pi), with Mp=(p-1)*M(p-2)/2. These analytical recurrences are independent of the generated rule.

There are 144 Legendre/Gaussian moments. Another 47 shifted Legendre moments use (x+2)**p for p=0..min(2*n-1,8), with exact integral (3**(p+1)-1)/(p+1). All 191 sums must be finite and satisfy abs(actual-reference)/max(1,abs(reference),sum(abs(weighted_terms))) <=5e-11. Scaling by absolute contributions accounts for cancellation of large odd Gaussian terms. After every rule, deallocation must release the public node/weight arrays. Other rule families, arbitrary weighted integrals, adaptive integration, invalid inputs and performance are not verified.

## Direct nonuniform Fourier sums: NUFFT2D (J1)

Source counts [8,31,64], mode grids [8,10], [9,11], [16,18], four point/strength patterns, both exponent signs and tolerance requests 1e-7/1e-10 give 144 transforms. Integer mode ranges are -ms/2..(ms-1)/2 and -mt/2..(mt-1)/2. All 22,416 coefficients are checked.

Scattered points use x_j=pi*sin(0.71*j), y_j=pi*cos(0.43*j), with strengths cos(0.13*j)+i*sin(0.17*j). Coincident points are all at the origin. A repeated near-boundary pattern uses x=+/-(pi-1e-6) and y cycling through -pi/2,0,pi/2. A fourth pattern uses scattered points with zero strengths. Exact +/-pi endpoints are not included.

Independent scalar loops form F(k,l)=sum_j c_j*(cos(phase)+i*sin(phase))/nj before calling the library, with phase=sign*(k*x_j+l*y_j). The 1/nj normalization is checked separately at the DC mode. Each call requires success, finite complex coefficients and unchanged coordinates/strengths. Maximum complex error divided by max(1,maxabs(direct_reference)) must be at most 50 times the requested tolerance. Zero strengths must give exactly zero coefficients.

The existing checksum-guarded legacy extent-one FFT dummy-array adapter is reused unchanged. No formulas, local arrays or library build settings change. Type-2/type-3 transforms, the static Fortran 77 interface, every FFT path, exact periodic endpoints, large grids and performance remain unverified. Direct-sum agreement does not establish a speed ranking.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream terms remain separate. Author sources were reviewed for interfaces; no upstream code is copied. Loading a link does not submit a job.

### qdutillib-moments-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=qdutillib&example=gams-qdutillib-moments-reference) / [Driver source](../fpm_catalog/gams-drivers/qdutillib-moments-reference.f90) / [Pinned procedure](https://github.com/lauvergn/QDUtilLib/blob/8a1fa9ca7cf52683c98cc4bcb40f21dc41df6ed5/SRC/Quadrature/Quadrature_m.f90#L81) / [Author example/test](https://github.com/lauvergn/QDUtilLib/blob/8a1fa9ca7cf52683c98cc4bcb40f21dc41df6ed5/APP/App_QDLib.f90)

```text
Rules: 14; Legendre/Gaussian moments: 144; shifted moments: 47
Orders 1,2,3,4,6,8,12: positive weights, symmetry, exact polynomial moments and deallocation.
Maximum moment error normalized by reference/absolute contributions:   2.5962E-15
PASS qdutillib-moments-reference
```

### nufft2d-direct-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nufft2d&example=gams-nufft2d-direct-reference) / [Driver source](../fpm_catalog/gams-drivers/nufft2d-direct-reference.f90) / [Pinned procedure](https://github.com/zgimbutas/nufft2d/blob/8353c5fb20cd0a8fe6821fae18355e303ed23ed3/nufft2df90.f#L1) / [Author example/test](https://github.com/zgimbutas/nufft2d/blob/8353c5fb20cd0a8fe6821fae18355e303ed23ed3/nufft2d_demof90.f)

```text
Two-dimensional type-1 NUFFT calls: 144; direct coefficient comparisons: 22416
Even/odd grids, both signs, two tolerances; scattered, coincident, near-boundary and zero-strength data.
Maximum normalized direct-sum error:   1.3607E-08
PASS nufft2d-direct-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers qdutillib-moments-reference nufft2d-direct-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
