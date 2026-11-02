# Ten checked transforms, structured systems, splines and beta-function drivers

Ten independent drivers across FFTPACK, SpecialMatrices, PCHIP and specfunc-fullerton passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-transforms-structures-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings and complete output. GAMS categories are not exhausted.

## FFTPACK: real and trigonometric transforms

- **DCT-I (J1a3):** 92 cases, lengths n=2..24 and four deterministic signals: constant, an impulse, an alternating signed ramp, and a dyadic modular sequence. The independent direct sum is x(0)+(-1)**k*x(n-1)+2*sum(x(j)*cos(pi*j*k/(n-1))), with j=1..n-2 and k=0..n-1. The inverse is normalized by 2*(n-1).
- **DST-I (J1a3):** 96 cases, lengths n=1..24 and the same signal families. Direct sums use 2*sum(x(j)*sin(pi*j*k/(n+1))), j,k=1..n. Two in-place transforms divide by 2*(n+1) for the inverse. The initialization workspace is reused.
- **Packed real FFT (J1a1):** 156 cases, source lengths m=4..16, four signals, and requested lengths m-2,m,m+3, checking truncation and zero-padding. Direct Fourier sums check DC, interleaved real/negative-sine components, and the separate even-length Nyquist component. The unnormalized inverse divides by n. The API returns n real packed entries, not a complex half-spectrum.

All transform results must be finite. Wrapper inputs are preserved exactly and output sizes are checked where requested lengths change them. The DST intentionally transforms a copy in place. These bounded examples do not cover invalid sizes, nonfinite inputs or extreme dynamic range. The direct sums are separate from the package fast-transform algorithms.

## SpecialMatrices: structured solves

- **Strang systems (D2b2a):** 276 vector/multiple-RHS solves, n=2..24, three dyadic solution patterns and iterative refinement off/on. The SPD tridiagonal matrix has diagonal 2 and adjacent diagonals -1. Explicit three-point stencil operations construct RHS vectors and recompute residuals; no package matvec or dense conversion supplies the oracle.
- **Circulant systems (D2a1):** 132 vector/multiple-RHS solves, n=2..23 and three nonsymmetric generators. For i>=2, c(i)=(-1)**i*(1+mod(i*i+pattern,7))/32, while c(1)=2+sum(abs(c(2:n))). Strict diagonal dominance ensures nonsingularity. A locally assembled dense matrix A(i,j)=c(modulo(i-j,n)+1) supplies RHS/residual references and known solutions. This is the first-column generator convention implemented by pinned dense()/FFT routines; the constructor comment displays the transpose convention. No numerical source was changed.
- **Rectangular Poisson systems (I2b1a1a):** 288 vector/multiple-RHS solves, nx,ny=2..7, two rectangular domains and two manufactured solutions. Lx=domain/2 and Ly=(domain+1)/2. The operator is Delta with homogeneous Dirichlet boundaries, not -Delta.

For the Poisson example, u=x*(Lx-x)*y*(Ly-y) has forcing -2*(x*(Lx-x)+y*(Ly-y)), and the five-point stencil reproduces this continuous forcing exactly. A second example uses sin(pi*i/(nx+1))*sin(2*pi*j/(ny+1)) with its discrete Laplacian eigenvalue, not its continuous eigenvalue. Known grid solutions, independent five-point residuals, a second scaled RHS and exact input preservation are checked. These examples verify the specified discrete systems; they do not establish convergence rates for general continuum solutions, variable coefficients, nonzero boundaries or nearly singular systems.

## PCHIP: integrating Hermite pieces and choosing spline boundaries

- **Hermite integrals (E3a3):** 117 arbitrary-bound/node-index integrals of a genuinely piecewise cubic with six nonuniform nodes and caller-supplied dyadic values/slopes. The 81 arbitrary intervals include zero length, reversal, partial panels and multiple panels; another 36 use DPCHID node indices. The driver independently integrates each clipped panel with two-point Gauss quadrature, exact for a cubic. It evaluates the Hermite basis locally, rather than calling a package evaluator for the oracle. The [reference table](gams-transforms-structures-ten-references.json) additionally saves exact Python Fraction antiderivatives for the 81 arbitrary intervals. DPCHIM slope selection and extrapolation are outside this driver.
- **Cubic spline boundaries (E1a):** 225 value/first-derivative queries for three shifted cubics (x-pattern/4)**3-2*x+pattern/8, six nonuniform nodes and not-a-knot/supplied-first-derivative/supplied-second-derivative endpoint conditions. DPCHSP constructs the slopes and DPCHFD evaluates values/derivatives, checked against explicit polynomial formulas at 25 points. The supplied endpoint conditions match each cubic; zero natural conditions are not substituted.

The Hermite nodes are [-1,-1/2,1/4,1,7/4,3], values [2,-1/4,1/2,3/4,-1,3/2], and slopes [1/2,-3/4,1,0,5/4,-1/2]. Arbitrary bounds divide the full interval into eight equal subintervals. Independent tests check the saved rational antiderivatives using exact Simpson integration of each clipped Hermite panel, a different rule from the driver's Gauss oracle. Successful statuses are required; no extrapolation warnings are accepted.

## Fullerton: default REAL32 beta functions

The pinned specfunc-fullerton APIs accept and return default REAL32. Consumers convert the exactly representable input parameters to that kind and widen results for comparison; widening does not supply REAL64 accuracy.

- **Beta/log-beta pairs (C7b):** 64 positive pairs a,b from {1/2,1,3/2,5/2,4,8,16,32}, including the larger-argument logarithmic path. Independent mpmath 1.3.0 beta/log-beta values at 80 digits were confirmed at 120 digits within absolute 1e-65. The saved table retains 18 significant digits. Beta must be positive/finite with relative error <=5e-5; log-beta uses 5e-5*max(1,abs(reference)). Independent tests additionally use integer/half-integer Gamma recurrences.
- **Integer-shape regularized beta CDF (L5a1b):** 252 queries with a,b=1..6 and x=0,1/8,1/4,1/2,3/4,7/8,1. Exact rational references use sum(binomial(n,j)*x**j*(1-x)**(n-j)), j=a..n, n=a+b-1. Results must be finite, within [0,1], sampled monotone in x and agree within absolute 3e-6. Noninteger shapes, extreme tails, nonpositive parameters, underflow and REAL64 accuracy claims are excluded.

## Retained unsuccessful probes

The [2D/3D quadrature-fortran sources and full results](gams-candidates/quadrature-fortran-nested/README.md) are retained with pins and normalized source hashes. Both compiled and reused cached libraries, then segfaulted with process exit 139 before numerical output. Their procedure records remain source-supported with no checked drivers and are excluded from menus. The implementation assigns pointers to internal wrapper procedures; compatibility with that mechanism is one possible cause to investigate, not an established diagnosis. These were execution failures, not observed numerical mismatches or reported time/size limits. The separate working 1D consumer is unchanged.

The initial beta-CDF consumer had a [generated literal error](gams-candidates/fullerton-beta-cdf-literals/README.md): zero/one constants appeared as integer 0_wp/1_wp in a REAL64 constructor. That consumer compilation failure is preserved with exact source and response. Changing only those literals to 0._wp/1._wp passed all 252 numerical comparisons and bounds/monotonicity checks. This was a consumer error, not a package numerical failure or sandbox limit.

## Limits, provenance and maintenance

Except for the stated REAL32 beta-function tolerances, results must be finite and agree within 2e-9*max(1,abs(reference)); integer/status and preservation checks are exact. These are bounded correctness demonstrations, not precision or performance benchmarks.

Pinned public APIs, implementations and linked author tests were reviewed. These are independent MIT consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source was patched. The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies the classifications, including real/trigonometric transforms, SPD tridiagonal systems, rectangular Poisson problems and fitted-function quadrature. Loading an example does not submit a job. The [coverage report](gams-coverage.md) records remaining work.

## Driver details

### fftpack-cosine-type1-reference (J1a3)

Independent API consumer; pinned sources reviewed. 92 REAL64 DCT-I cases, lengths 2..24 and four deterministic signal patterns. Independent endpoint-weighted direct cosine sums and inverse normalization 2*(n-1), including smallest valid length. Finite results and source preservation; invalid sizes excluded.

### fftpack-sine-type1-reference (J1a3)

Independent API consumer; pinned sources reviewed. 96 REAL64 in-place DST-I cases, lengths 1..24 and four deterministic signal patterns. Direct 2*sum(x_j*sin(pi*j*k/(n+1))) references, normalization 2*(n+1), reused initialization workspace and finite checks. Invalid sizes and extreme-range inputs excluded.

### fftpack-packed-real-transforms-reference (J1a1)

Independent API consumer; pinned sources reviewed. 156 REAL64 packed real-transform cases, source lengths 4..16, four patterns and truncation/unchanged/zero-padding lengths m-2,m,m+3. Direct Fourier sums check DC, interleaved real/negative-sine components and even-length Nyquist coefficient; inverse normalized by n. Exact source preservation and output shapes checked. Packed representation is real, not a complex half-spectrum.

### specialmatrices-strang-systems-reference (D2b2a)

Independent API consumer; pinned sources reviewed. 276 REAL64 vector/multiple-RHS solves for the SPD tridiagonal Strang matrix (2 on diagonal, -1 off diagonal), n=2..24, three solution patterns and refinement off/on. Known dyadic solutions and independently assembled three-point stencil RHS/residuals; exact RHS preservation and finite checks. General variable-coefficient tridiagonals excluded.

### specialmatrices-circulant-systems-reference (D2a1)

Independent API consumer; pinned sources reviewed. 132 REAL64 vector/multiple-RHS solves, n=2..23 and three strictly diagonally dominant nonsymmetric circulant generators. Explicit dense reference A(i,j)=c(modulo(i-j,n)+1), known dyadic solutions, independent dense RHS/residuals and exact RHS preservation. The generator is the first column, following pinned dense()/FFT implementation; the constructor comment displays a transposed convention. Near-singular Fourier eigenvalues excluded.

### specialmatrices-rectangular-poisson-reference (I2b1a1a)

Independent API consumer; pinned sources reviewed. 288 REAL64 vector/multiple-RHS rectangular Dirichlet Laplacian solves: nx,ny=2..7, two aspect-ratio domains and polynomial/sine manufactured solutions. The quartic product x*(Lx-x)*y*(Ly-y) has exactly reproduced continuous forcing under the five-point stencil; the sine case uses the discrete eigenvalue. Independent stencil residuals, known grid solutions and exact RHS preservation. Operator is Delta, not -Delta. No continuum-convergence or nonzero-boundary claim.

### pchip-hermite-integrals-reference (E3a3)

Independent API consumer; pinned sources reviewed. 117 REAL64 piecewise cubic Hermite integrals on a six-node nonuniform grid with explicitly supplied dyadic values/slopes. 81 arbitrary-bound and 36 node-index intervals include zero/reversed/multi-panel bounds. Independent per-panel two-point Gauss integration of Hermite basis polynomials, plus saved Python Fraction antiderivatives. The slopes are caller-supplied; this does not test DPCHIM slope selection. Extrapolation excluded.

### pchip-cubic-boundaries-reference (E1a)

Independent API consumer; pinned sources reviewed. 225 REAL64 cubic reproduction queries: three shifted cubics, six nonuniform nodes, and not-a-knot/supplied first derivative/supplied second derivative endpoint conditions. DPCHSP constructs slopes; DPCHFD values and first derivatives must match independent explicit cubic formulas at 25 points per case. Natural zero-second-derivative conditions are not imposed on nonmatching cubics. Extrapolation and noisy-data claims excluded.

### specfunc-fullerton-beta-pairs-reference (C7b)

Independent API consumer; pinned sources reviewed. 64 positive-parameter pairs for default REAL32 beta/log_beta functions, a,b in {1/2,1,3/2,5/2,4,8,16,32}. Independent mpmath 80/120-digit references saved to 18 digits; beta requires relative error <=5e-5 and log-beta scaled absolute error <=5e-5. Includes the large-argument log-domain path. Nonpositive parameters, underflow and REAL64 accuracy claims excluded.

### specfunc-fullerton-integer-beta-cdf-reference (L5a1b)

Independent API consumer; pinned sources reviewed. 252 default REAL32 regularized beta-CDF queries, integer a,b=1..6 and seven dyadic x values including endpoints. Independent exact rational binomial upper-tail formula with n=a+b-1; absolute error <=3e-6, boundedness and sampled monotonicity. Noninteger shapes, extreme tails and REAL64 accuracy excluded.

## Provenance and actual output

### fftpack-cosine-type1-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fftpack&example=gams-fftpack-cosine-type1-reference) / [Driver source](../fpm_catalog/gams-drivers/fftpack-cosine-type1-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/src/fftpack_dct.f90#L6) / [Author test](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/test/test_fftpack_dct.f90)

```text
Independent direct trigonometric sums and normalized inverse cases: 92
PASS fftpack-cosine-type1-reference
```

### fftpack-sine-type1-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fftpack&example=gams-fftpack-sine-type1-reference) / [Driver source](../fpm_catalog/gams-drivers/fftpack-sine-type1-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/src/fftpack.f90#L190) / [Author test](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/test/test_fftpack_original.f90)

```text
Independent direct trigonometric sums and normalized inverse cases: 96
PASS fftpack-sine-type1-reference
```

### fftpack-packed-real-transforms-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fftpack&example=gams-fftpack-packed-real-transforms-reference) / [Driver source](../fpm_catalog/gams-drivers/fftpack-packed-real-transforms-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/src/fftpack_rfft.f90#L6) / [Author test](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/test/test_fftpack_rfft.f90)

```text
Packed real DFT, odd/even lengths, truncation and zero-padding cases: 156
PASS fftpack-packed-real-transforms-reference
```

### specialmatrices-strang-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-strang-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-strang-systems-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Strang/specialmatrices_strang.f90#L137) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_strang.f90)

```text
SPD tridiagonal vector/multiple-RHS solves, with/without refinement: 276
PASS specialmatrices-strang-systems-reference
```

### specialmatrices-circulant-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-circulant-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-circulant-systems-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Circulant/specialmatrices_circulant.f90#L155) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_circulant.f90)

```text
Strictly diagonally dominant circulant vector/multiple-RHS systems: 132
PASS specialmatrices-circulant-systems-reference
```

### specialmatrices-rectangular-poisson-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-rectangular-poisson-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-rectangular-poisson-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Poisson2D/specialmatrices_poisson2D.f90#L152) / [Author test](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/test/test_poisson2D.f90)

```text
Rectangular homogeneous-Dirichlet Laplacian vector/multiple-RHS solves: 288
PASS specialmatrices-rectangular-poisson-reference
```

### pchip-hermite-integrals-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=pchip&example=gams-pchip-hermite-integrals-reference) / [Driver source](../fpm_catalog/gams-drivers/pchip-hermite-integrals-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/PCHIP/blob/8f5350565072622a2344dd0ec75193832b31eb10/src/pchip_module.f90#L1652) / [Author test](https://github.com/jacobwilliams/PCHIP/blob/8f5350565072622a2344dd0ec75193832b31eb10/test/pchip_test.f90)

```text
Piecewise cubic integrals with arbitrary/reversed/node-index bounds: 117
PASS pchip-hermite-integrals-reference
```

### pchip-cubic-boundaries-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=pchip&example=gams-pchip-cubic-boundaries-reference) / [Driver source](../fpm_catalog/gams-drivers/pchip-cubic-boundaries-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/PCHIP/blob/8f5350565072622a2344dd0ec75193832b31eb10/src/pchip_module.f90#L2456) / [Author test](https://github.com/jacobwilliams/PCHIP/blob/8f5350565072622a2344dd0ec75193832b31eb10/test/pchip_test.f90)

```text
Cubic spline values/derivatives: not-a-knot, first/second derivative boundaries: 225
PASS pchip-cubic-boundaries-reference
```

### specfunc-fullerton-beta-pairs-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-beta-pairs-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-beta-pairs-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_beta.f90#L30) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/beta/test_beta.f90)

```text
Positive integer/half-integer beta and log-beta reference pairs: 64
PASS specfunc-fullerton-beta-pairs-reference
```

### specfunc-fullerton-integer-beta-cdf-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specfunc-fullerton&example=gams-specfunc-fullerton-integer-beta-cdf-reference) / [Driver source](../fpm_catalog/gams-drivers/specfunc-fullerton-integer-beta-cdf-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_beta.f90#L75) / [Author test](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/test/beta/test_beta.f90)

```text
Integer-parameter regularized beta CDF versus exact binomial tails: 252
PASS specfunc-fullerton-integer-beta-cdf-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fftpack-cosine-type1-reference fftpack-sine-type1-reference fftpack-packed-real-transforms-reference specialmatrices-strang-systems-reference specialmatrices-circulant-systems-reference specialmatrices-rectangular-poisson-reference pchip-hermite-integrals-reference pchip-cubic-boundaries-reference specfunc-fullerton-beta-pairs-reference specfunc-fullerton-integer-beta-cdf-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
