# Checked fixed gradient steps and seeded particle swarms

These G1b and G2i drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-gradient-swarm-validation.json) retains pins, source hashes and complete output. GAMS categories are not exhausted.

## ForTimize fixed-step gradient descent (G1b)

The independent consumer minimizes SPD quadratics f(x)=0.5*(x-center)^T*H*(x-center). Dimensions [2,3,5], condition ratios [1,5], diagonal/rotated Hessians, step settings [0.5,1.5]/lambda_max, iteration counts [1,2,5,25,100] and two starts give 240 runs and 800 coordinate references. Centers are quarter-integers; starts have positive or alternating displacements. Elementary adjacent-column rotations construct Q and scalar sums form H=Q*diag(lambda)*transpose(Q), with explicit symmetrization in working precision.

An independent spectral reference computes x_N=center+Q*diag((1-step*lambda)**N)*transpose(Q)*(x_0-center), and the analogous previous point and objective. Steps remain strictly inside the SPD stability interval; the larger setting exercises sign-alternating contraction in the highest mode. The gradient callback must be requested exactly N times. The implementation uses max_iters as a fixed count and does not use convergence_tolerance for early termination.

Every returned point and objective must be finite. Coordinate discrepancies, scaled by 1+max(abs(x_0-center)), must be <= 2e-12. Objectives are compared with the spectral sums using scale 1+f_0 and the same 2e-12 bound. Recomputed endpoint cost must not exceed initial cost beyond roundoff, and f_100/f_0 must be <= 1e-8. Saved maximum point, returned-cost and endpoint-cost discrepancies are 1.8504e-16, 1.7504e-16 and 1.2643e-16. The largest f_100/f_0 is 4.6923e-10.

## Verified returned-objective caveat

At this pinned [gradient-descent implementation](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/src/with_derivatives/gradient_descent.f90#L23), the callback evaluates F before each update and the routine does not refresh F after the final update. Returned X is x_N, but returned F is f(x_(N-1)). The driver explicitly checks the preceding-iterate reference, then recomputes the objective at returned X. It does not present the stale value as the endpoint objective.

The first one-step fixture returns 0.625 while the endpoint objective is 0.15625. This discrepancy is printed in the successful proof and is visible when the example is run. No library source patch or relaxed numeric comparison was introduced. The dedicated test establishes fixed-step behavior on these quadratics, not adaptive stopping, a reliable final-objective API, arbitrary step choices or nonquadratic convergence.

## Opti seeded shifted Rastrigin search (G2i)

Two and three dimensions, amplitudes A=[1,10] and seeds [314159,271828,161803] give 12 bounded stochastic searches and 30 known minimizer entries. Centers have coordinates (i-2)/4, and each coordinate is bounded by center plus/minus 3. The objective is sum(d**2+A*(1-cos(2*pi*d))), d=x-center. Every term is nonnegative; zero is attained uniquely at center, providing an analytic global reference for these nonconvex multimodal benchmarks.

Each call uses 80 particles, a 1,200-generation cap, desired_error=1e-10 and adaptive topology 2. The GNU random-seed array is initialized with seed(i)=base_seed+37*i after querying its required size. The resulting positions must be finite and inside their boxes. Callback counts must be positive and within the conservative 2*80*(1200+2) bound; the successful run used 644,800 optimizer callback evaluations overall.

An independent identity evaluates the returned objective as sum(d**2+2*A*sin(pi*d)**2), avoiding subtraction of nearly equal cosine values near a minimum. It must agree with the callback formula within 2e-12*(1+reference). The independent objective must be <= 1e-5 and maximum coordinate distance from center <= 1e-3. Saved maxima are 9.8261e-11 and 1.6632e-6 respectively.

These are recorded successful seeds and work budgets, not a global-convergence guarantee or a measured success probability. The RNG sequence is not claimed portable across compilers or versions. The API exposes no termination status, so the driver checks results independently instead of interpreting an unavailable success flag. Other topologies, dimensions, bound-active optima, arbitrary multimodal landscapes and performance remain unverified. The package prints progress during each call; this review shows its final verification summary, while the complete progress output remains in the saved report.

## Sources, licenses and actual output

Pinned implementations and author API examples were reviewed before writing these independent consumers. Their own MIT notice covers only these drivers. ForTimize upstream licensing remains unspecified; the driver notice does not relicense the package, and no upstream example body is copied. Opti retains its GPL-2.0-or-later terms. Loading a driver does not submit a job.

### fortimize-gradient-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortimize&example=gams-fortimize-gradient-reference) / [Driver source](../fpm_catalog/gams-drivers/fortimize-gradient-reference.f90) / [Pinned procedure](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/src/minimize.f90#L7) / [Author test](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/example/gradient.f90)

```text
First returned / endpoint objective:    6.25000E-01   1.56250E-01
Fixed-step quadratic runs: 240
Analytic iterate entries: 800
Maximum normalized iterate discrepancy:   1.8504E-16
Maximum normalized returned-objective discrepancy:   1.7504E-16
Maximum normalized endpoint-objective discrepancy:   1.2643E-16
Maximum final / initial cost after 100 steps:   4.6923E-10
Returned objective is for the preceding iterate; endpoint objective is recomputed.
PASS fortimize-gradient-reference
```

### opti-rastrigin-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=opti&example=gams-opti-rastrigin-reference) / [Driver source](../fpm_catalog/gams-drivers/opti-rastrigin-reference.f90) / [Pinned procedure](https://github.com/Konrad1991/opti/blob/6fb22db21bd2338e00690ff3706be61a1f101101/src/particle_swarm.f90#L57) / [Author test](https://github.com/Konrad1991/opti/blob/6fb22db21bd2338e00690ff3706be61a1f101101/test/check.f90)

```text
Swarm verification summary:
Seeded shifted-Rastrigin problems: 12
Known global-minimizer entries: 30
Optimizer callback evaluations: 644800
Maximum independently evaluated objective:   9.8261E-11
Maximum coordinate error from known global optimum:   1.6632E-06
These seeded successes do not guarantee global convergence or portability of the RNG sequence.
PASS opti-rastrigin-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fortimize-gradient-reference opti-rastrigin-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
