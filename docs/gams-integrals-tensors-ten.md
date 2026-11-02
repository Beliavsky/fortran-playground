# Ten checked specialized integrals, tensor interpolation and nonlinear-system drivers

Ten independent drivers across QUADPACK, finterp, bspline-fortran and MINPACK passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-integrals-tensors-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings and complete output. GAMS categories are not exhausted.

## QUADPACK: specialized integration APIs

Five drivers use module-procedure callbacks, separate workspace arrays and the pinned public wrappers. Every call requires ier=0, positive integrand evaluations, finite result and finite nonnegative estimated error. Returned error estimates are sanity-checked; the actual result is judged independently against an analytic reference. These examples do not establish that estimated error bounds are rigorous.

- **DQAGI half-lines (H2a3a1):** 32 exponential tails, decay rates 1/2,1,2,4 and finite bound magnitudes 0,1/2,1,3/2, on both right and left half-lines. The callback is exp(-rate*abs(x)); the exact integral is exp(-rate*bound)/rate on the tested domains. Whole-line, oscillatory-tail and divergent cases are excluded.
- **DQAGP interior breakpoints (H2a2a1):** 18 integrals of abs(x-c)**p, p=-1/2,1/2,3/2, on [0,1] and [-1,2], at quarter/midpoint/three-quarter breakpoints. Splitting the elementary antiderivative at c supplies the reference. A value of zero at the isolated singular point does not change the integral.
- **DQAWC principal values (H2a2a1):** 36 integrals on [0,1], [-1,2] and [-2,3], using three interior pole fractions and smooth numerator (x-c)**power, power=0..3. The integrator supplies the 1/(x-c) weight. The constant numerator has principal value log((b-c)/(c-a)); the other powers have ordinary polynomial antiderivatives.
- **DQAWO sine/cosine weights (H2a2a1):** 72 finite exponential integrals, three rates/lengths, frequencies 1/2,4,32,-4, and both trigonometric weights. Direct elementary antiderivatives supply references, including the sign change for negative-frequency sine. Infinite Fourier integration and reuse of Chebyshev moments are outside this driver.
- **DQAWS endpoint weights (H2a2a1):** 144 integrals on [0,1], endpoint exponents alpha,beta=-1/2,0,1/2, smooth numerators x**p, p=0..3, and all four no-log/log(x)/log(1-x)/both-log modes. The callback supplies only x**p.

For DQAWS let A=alpha+p+1, B=beta+1, S=A+B and W=Beta(A,B). The four exact expressions are W, W*(psi(A)-psi(S)), W*(psi(B)-psi(S)), and W*((psi(A)-psi(S))*(psi(B)-psi(S))-psi1(S)), where psi and psi1 are digamma/trigamma. The [reference table](gams-integrals-tensors-ten-references.json) saves every configuration and 18-digit value. mpmath 1.3.0 evaluations at 80 digits were confirmed at 120 digits within absolute 1e-65; no numerical quadrature generated these references. Tests additionally reconstruct the references from integer/half-integer Gamma and polygamma recurrences.

### Retained DQAWO counter probe

The initial consumer failed its last>0 assertion before checking the first numerical result. The pinned DQAWOE implementation initializes Last=0 and returns directly if the initial estimate is accepted. The [original exact source and complete hosted result](gams-candidates/quadpack-oscillatory-counter/README.md) are retained. The corrected driver accepts nonnegative last, still requires positive neval and ier=0, and reports how many calls used last=0. All 72 independent numerical comparisons remain in place. This counter assertion did not establish a numerical error or sandbox limit; no upstream source was patched.

## finterp: three- and four-dimensional cells (E2a)

Two drivers use four nonuniform nodes per axis: [-1,-1/4,1/2,2]*j/2 for coordinate j. One dataset is the multiaffine polynomial 1+sum(j*x_j)+product(x)+x1*x2-2*x2*x3, which tensor linear interpolation must reproduce. The second adds sum(j*x_j**2). Its reference uses each cell's exact quadratic secant (a+b)*x-a*b, rather than incorrectly requiring reproduction of the original quadratic. Every cell is queried at all endpoint/midpoint combinations: 1458 queries in 3D and 13122 in 4D across the two datasets. Thus grid nodes, shared boundaries and cell interiors are checked. API statuses, finite results and input-data preservation are required; extrapolation is excluded.

## bspline-fortran: tensor mixed derivatives (E3a2)

Two independent cubic tensor consumers fit five dyadic nonuniform nodes per axis, [-1,-1/2,0,3/4,2]*j/2, using spline order four in every dimension. Input values use the explicit polynomial 1+sum(j*x_j**3)+product(x)+2*x1**2*x2-x2*x3**2. Reference derivatives use separately recorded coefficients/exponents and analytic falling factorials; those tables are saved with the endpoint-weight references. These are not finite-difference references.

The 3D example checks all 27 partial-order combinations 0..2 per coordinate at 64 interior points (1728 evaluations). The 4D example checks all 81 combinations at 256 interior points (20736 evaluations). The coefficient representation and explicit nodal formula are independently cross-checked in tests. Initialization/evaluation statuses, finite scaled agreement within 1e-8 and exact nodal-data preservation are required. Records also retain gridded-interpolation E2a assignments, while the checked drivers primarily demonstrate derivative evaluation E3a2. Extrapolation, noisy fitting and higher derivative orders are outside scope.

## MINPACK: user-supplied Jacobians (F2)

HYBRJ1 solves 60 triangular nonlinear systems with dimensions n=2..6, three component-scaled alternating-sign start patterns and four displacement scales. Define u_i=x_i-i/4; f_1=u_1+u_1**3/8 and f_i=u_i+u_i**3/8+u_(i-1)**2/4 for i>1. The unique real root follows by forward induction because u+u**3/8 is strictly increasing with its only real zero at zero. The Jacobian is bidiagonal, with diagonal 1+3*u_i**2/8 and subdiagonal u_(i-1)/2. Tests check that analytic Jacobian against independent exact polynomial differentiation. The consumer requires info=1, both callback paths, root/residual errors <=1e-8 and returned/recomputed residual agreement within 1e-12. Singular systems and global convergence are not claimed.

## Limits, provenance and maintenance

Real results must be finite and agree within 2e-9*max(1,abs(reference)), except spline mixed derivatives use 1e-8 and the nonlinear-system checks use their stated tolerances. QUADPACK requests absolute and relative tolerance 1e-10. These are bounded correctness demonstrations, not performance or extreme-condition benchmarks.

Pinned public APIs, implementations and linked author tests were reviewed. These are independent MIT consumers; upstream implementation and author-test bodies were not copied. No upstream numerical source was patched. The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies the classifications, including automatic half-line quadrature H2a3a1 and interpolation derivative evaluation E3a2. Loading an example does not submit a job. The [coverage report](gams-coverage.md) records remaining work.

## Driver details

### quadpack-improper-halflines-reference (H2a3a1)

Independent API consumer; pinned sources reviewed. 32 REAL64 exponential integrals on left/right half-lines: four positive decay rates and four finite nonnegative bound magnitudes. Exact antiderivative exp(-rate*bound)/rate; ier=0, finite nonnegative error estimate and positive work counters required. Whole-line integrals, divergent/oscillatory tails and error-estimator guarantees excluded.

### quadpack-interior-breakpoints-reference (H2a2a1)

Independent API consumer; pinned sources reviewed. 18 REAL64 finite integrals of abs(x-c)**p with supplied interior breakpoint c, p=-1/2,1/2,3/2, two intervals and three breakpoint fractions. Independent split antiderivatives; ier=0 and work/error sanity checks. The callback assigns zero at the isolated singular point, which has no effect on the integral. Multiple singularities and divergent exponents excluded.

### quadpack-cauchy-principal-values-reference (H2a2a1)

Independent API consumer; pinned sources reviewed. 36 REAL64 Cauchy principal-value integrals of (x-c)**power/(x-c), powers 0..3, three intervals and three interior pole fractions. Logarithmic principal value for constant numerator and polynomial antiderivatives otherwise. The callback supplies only the smooth numerator. ier=0 and finite error/work checks; endpoint poles excluded.

### quadpack-oscillatory-weights-reference (H2a2a1)

Independent API consumer; pinned sources reviewed. 72 REAL64 finite-interval exponential integrals with sine/cosine weights: three rates, three lengths and four signed frequencies. Closed elementary antiderivatives, ier=0 and error/work checks. Callback supplies exp(-rate*x), not the oscillating weight. Infinite Fourier integrals and reused Chebyshev moments excluded. The pinned initial-estimate acceptance path leaves last=0; this is allowed and counted, while neval must remain positive.

### quadpack-endpoint-weights-reference (H2a2a1)

Independent API consumer; pinned sources reviewed. 144 REAL64 endpoint-weighted integrals on [0,1], alpha/beta=-1/2,0,1/2, numerator x**power for powers 0..3, and all four no-log/log(x)/log(1-x)/both-log modes. Analytic beta-function derivatives evaluated independently at 80/120 digits; 18-digit constants and exact configurations saved. ier=0 plus finite error/work checks. Nonintegrable endpoint exponents excluded.

### finterp-3d-cell-polynomials-reference (E2a)

Independent API consumer; pinned sources reviewed. 1458 REAL64 3D tensor interpolation queries on dyadic nonuniform grids: two datasets, every cell at endpoint/midpoint coordinate combinations. A multiaffine polynomial must reproduce exactly; added coordinate squares use independently derived cell secants (a+b)*x-a*b rather than the original quadratic value. Data preservation, node/cell boundaries and API statuses checked. Extrapolation excluded.

### finterp-4d-cell-polynomials-reference (E2a)

Independent API consumer; pinned sources reviewed. 13122 REAL64 4D tensor interpolation queries on dyadic nonuniform grids: two datasets, every cell at endpoint/midpoint coordinate combinations. A multiaffine polynomial must reproduce exactly; added coordinate squares use independently derived cell secants (a+b)*x-a*b rather than the original quadratic value. Data preservation, node/cell boundaries and API statuses checked. Extrapolation excluded.

### bspline-fortran-3d-mixed-partials-reference (E3a2)

Independent API consumer; pinned sources reviewed. 1728 REAL64 cubic tensor value/derivative queries on a five-node-per-axis dyadic nonuniform grid. Every partial-order combination 0..2 per coordinate at 64 interior points; explicit cubic/cross-term input formulas and independent coefficient/falling-factorial derivatives. API statuses, finite scaled agreement within 1e-8 and data preservation required. Extrapolation, noisy data and derivative orders above two excluded.

### bspline-fortran-4d-mixed-partials-reference (E3a2)

Independent API consumer; pinned sources reviewed. 20736 REAL64 cubic tensor value/derivative queries on a five-node-per-axis dyadic nonuniform grid. Every partial-order combination 0..2 per coordinate at 256 interior points; explicit cubic/cross-term input formulas and independent coefficient/falling-factorial derivatives. API statuses, finite scaled agreement within 1e-8 and data preservation required. Extrapolation, noisy data and derivative orders above two excluded.

### minpack-analytic-jacobian-systems-reference (F2)

Independent API consumer; pinned sources reviewed. 60 REAL64 triangular nonlinear systems, dimensions 2..6, three alternating-sign, component-scaled patterns and four initial displacement scales. f_i=u_i+u_i**3/8+u_(i-1)**2/4 (last term omitted for i=1), u_i=x_i-i/4. Strict monotonicity in each u_i gives the unique known real root by forward induction. Analytic bidiagonal Jacobian, ier/info=1, both callback paths, returned/recomputed residual consistency and root error <=1e-8. Singular systems and global-convergence claims excluded.

## Provenance and actual output

### quadpack-improper-halflines-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-improper-halflines-reference) / [Driver source](../fpm_catalog/gams-drivers/quadpack-improper-halflines-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L514) / [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90)

```text
Left/right exponential half-line integrals: 32
PASS quadpack-improper-halflines-reference
```

### quadpack-interior-breakpoints-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-interior-breakpoints-reference) / [Driver source](../fpm_catalog/gams-drivers/quadpack-interior-breakpoints-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L1058) / [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90)

```text
Supplied interior breakpoints, cusps and integrable singularities: 18
PASS quadpack-interior-breakpoints-reference
```

### quadpack-cauchy-principal-values-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-cauchy-principal-values-reference) / [Driver source](../fpm_catalog/gams-drivers/quadpack-cauchy-principal-values-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L2233) / [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90)

```text
Cauchy principal values with polynomial numerators: 36
PASS quadpack-cauchy-principal-values-reference
```

### quadpack-oscillatory-weights-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-oscillatory-weights-reference) / [Driver source](../fpm_catalog/gams-drivers/quadpack-oscillatory-weights-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L3107) / [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90)

```text
Finite sine/cosine-weighted exponential integrals: 72
Initial-estimate acceptances with last=0: 72
PASS quadpack-oscillatory-weights-reference
```

### quadpack-endpoint-weights-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=quadpack&example=gams-quadpack-endpoint-weights-reference) / [Driver source](../fpm_catalog/gams-drivers/quadpack-endpoint-weights-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/src/quadpack_generic.F90#L3757) / [Author test](https://github.com/jacobwilliams/quadpack/blob/ab42d50794280a8e7996f2ee4cda1f8753dfde5b/test/quadpack_test_module.F90)

```text
Algebraic/logarithmic endpoint weights against beta derivatives: 144
PASS quadpack-endpoint-weights-reference
```

### finterp-3d-cell-polynomials-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=finterp&example=gams-finterp-3d-cell-polynomials-reference) / [Driver source](../fpm_catalog/gams-drivers/finterp-3d-cell-polynomials-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/finterp/blob/95aaceaf86f5d4d49328b783c5dff9b006b0bfc9/src/linear_interpolation_module.F90#L519) / [Author test](https://github.com/jacobwilliams/finterp/blob/95aaceaf86f5d4d49328b783c5dff9b006b0bfc9/test/test.f90)

```text
Tensor linear node/interior/cell-boundary checks: 1458
PASS finterp-3d-cell-polynomials-reference
```

### finterp-4d-cell-polynomials-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=finterp&example=gams-finterp-4d-cell-polynomials-reference) / [Driver source](../fpm_catalog/gams-drivers/finterp-4d-cell-polynomials-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/finterp/blob/95aaceaf86f5d4d49328b783c5dff9b006b0bfc9/src/linear_interpolation_module.F90#L563) / [Author test](https://github.com/jacobwilliams/finterp/blob/95aaceaf86f5d4d49328b783c5dff9b006b0bfc9/test/test.f90)

```text
Tensor linear node/interior/cell-boundary checks: 13122
PASS finterp-4d-cell-polynomials-reference
```

### bspline-fortran-3d-mixed-partials-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=bspline-fortran&example=gams-bspline-fortran-3d-mixed-partials-reference) / [Driver source](../fpm_catalog/gams-drivers/bspline-fortran-3d-mixed-partials-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/bspline-fortran/blob/047c724451aeee7f883c0d5acba3f7bd22a5de01/src/bspline_oo_module.f90#L1448) / [Author test](https://github.com/jacobwilliams/bspline-fortran/blob/047c724451aeee7f883c0d5acba3f7bd22a5de01/test/test_oo.f90)

```text
Tensor cubic values and analytic mixed partial derivatives: 1728
PASS bspline-fortran-3d-mixed-partials-reference
```

### bspline-fortran-4d-mixed-partials-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=bspline-fortran&example=gams-bspline-fortran-4d-mixed-partials-reference) / [Driver source](../fpm_catalog/gams-drivers/bspline-fortran-4d-mixed-partials-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/bspline-fortran/blob/047c724451aeee7f883c0d5acba3f7bd22a5de01/src/bspline_oo_module.f90#L1751) / [Author test](https://github.com/jacobwilliams/bspline-fortran/blob/047c724451aeee7f883c0d5acba3f7bd22a5de01/test/test_oo.f90)

```text
Tensor cubic values and analytic mixed partial derivatives: 20736
PASS bspline-fortran-4d-mixed-partials-reference
```

### minpack-analytic-jacobian-systems-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=minpack&example=gams-minpack-analytic-jacobian-systems-reference) / [Driver source](../fpm_catalog/gams-drivers/minpack-analytic-jacobian-systems-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/src/minpack.f90#L1401) / [Author test](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/test/test_hybrj.f90)

```text
Known-root triangular nonlinear systems with analytic Jacobians: 60
Maximum root error:   5.6475E-12; residual:   5.6475E-12
PASS minpack-analytic-jacobian-systems-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers quadpack-improper-halflines-reference quadpack-interior-breakpoints-reference quadpack-cauchy-principal-values-reference quadpack-oscillatory-weights-reference quadpack-endpoint-weights-reference finterp-3d-cell-polynomials-reference finterp-4d-cell-polynomials-reference bspline-fortran-3d-mixed-partials-reference bspline-fortran-4d-mixed-partials-reference minpack-analytic-jacobian-systems-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
