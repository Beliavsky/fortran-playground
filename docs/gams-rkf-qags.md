# Checked RKF45 initial-value integration and adaptive quadrature

These I1a1a and H2a1a1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-rkf-qags-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Forward and backward analytical IVPs: RKF45 (I1a1a)

Twenty-four two-variable runs combine three nonstiff problem families, rates a=0.25 or 1, two initial states, and both time directions. Frequencies w=1 or 3 accompany the two rates. Each run integrates from -0.5 to 1.5 or from 1.5 to -0.5, with 16 equally spaced requested targets and continued solver state: 384 calls. Every run resets the work arrays, initial flag and callback counter. The pinned package must provide at least 15 decimal digits of real precision.

Family 1 is damped rotation: y1'=-a*y1-w*y2, y2'=w*y1-a*y2. Its exact solution is exp(-a*(t-t0)) times rotation by w*(t-t0) of the initial vector [1,-0.5] or [-0.25,2]. Its squared norm must also follow the independently known decay law norm(y0)**2*exp(-2*a*(t-t0)).

Family 2 is a manufactured nonautonomous tracking system y'=-a*(y-g(t))+g'(t), with g=[sin(w*t)+t*t,cos(w*t)+t]. Its exact solution is g(t)+exp(-a*(t-t0))*offset, for offsets [0.25,-0.5] or [-0.75,0.125]. The implemented right-hand side explicitly differentiates g; the solution reference uses the separate exponential correction.

Family 3 contains two independent logistic equations with rates a and a/2, starting at [0.25,0.75] or [0.1,0.6]. The exact component is p/(p+(1-p)*exp(-rate*(t-t0))). Both components must remain strictly between zero and one throughout forward and backward runs.

Every requested target must return normal flag 2, finite states and time within 16*epsilon(t)*max(1,abs(target)). Relative and absolute tolerance requests are 1e-10 and 1e-12. Maximum state error divided by max(1,maxabs(exact_state)) must be at most 5e-8; the normalized damped-rotation norm error must be at most 1e-7. The callback must actually be evaluated in every run. These are answer checks, not a claim that every returned global error obeys the local tolerance request. Stiff equations, single-step mode, warning recovery, all tolerance regimes, long trajectories and performance remain unverified.

## Analytical finite-interval QAGS integrals: FGSL (H2a1a1)

Twenty integrals are each evaluated at two absolute/relative tolerance pairs, both 1e-7 and both 1e-10: 40 calls. The five families are:

- x**p on [0,1], for p=-0.5,-0.25,0.5,2,5, with integral 1/(p+1).
- x**p*log(x) on [0,1] for the same p, with integral -1/(p+1)**2. The negative powers and logarithm exercise integrable endpoint singularities.
- 1/(1+(p*x)**2) on [-2,3], for p=0.5,1,2, with integral (atan(3*p)-atan(-2*p))/p.
- exp(p*x) on [-1,2], for p=-1,0.5,2, with integral (exp(2*p)-exp(-p))/p.
- sin(p*x) on [0,pi], for p=1,3,5,16, with integral (1-cos(p*pi))/p; the last case checks a cancellation-dominated zero integral.

One 1000-subinterval workspace and one C-interoperable callback handle are reused across all cases. A BIND(C) settings object passes the changing family and parameter through C_LOC/C_F_POINTER; its target remains alive until the handle is freed. Both the function handle and workspace are released after all calls. The package's pinned GNU/Linux LP64 configuration and C support are reused.

Every call requires success status and at least one callback evaluation. Value and estimated absolute error must be finite. Error divided by max(1,abs(exact_integral)) must be at most 5 times the requested tolerance. The reported estimate must be nonnegative and no larger than max(epsabs,epsrel*abs(value)), allowing additive roundoff of 32*epsilon(value)*max(1,abs(value)). This verifies the estimate's consistency with the requested stopping budget; it does not establish a rigorous upper bound on actual error. Arbitrary singularities, infinite intervals, invalid-input recovery, every GSL integration strategy, other FGSL interfaces and performance are outside the checked scope.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream terms remain separate. Author sources were reviewed for interfaces, and no upstream implementation or example code is copied. Loading a link does not submit a job.

### rkf45-analytic-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rkf45&example=gams-rkf45-analytic-reference) / [Driver source](../fpm_catalog/gams-drivers/rkf45-analytic-reference.f90) / [Pinned procedure](https://github.com/zoziha/rkf45/blob/93cd129369357ee08e34be7868256b21a500cc98/src/rkf45.F90#L57) / [Author example/test](https://github.com/zoziha/rkf45/blob/93cd129369357ee08e34be7868256b21a500cc98/test/test_rkf45.f90)

```text
Family 1: forward/backward runs at two rates and two initial states passed.
Family 2: forward/backward runs at two rates and two initial states passed.
Family 3: forward/backward runs at two rates and two initial states passed.
Integration runs: 24; requested target calls: 384
RHS evaluations: 11669
Maximum normalized analytical state error:   4.6749E-10
PASS rkf45-analytic-reference
```

### fgsl-qags-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fgsl&example=gams-fgsl-qags-reference) / [Driver source](../fpm_catalog/gams-drivers/fgsl-qags-reference.f90) / [Pinned procedure](https://github.com/reinh-bader/fgsl/blob/27a3e7cc0809623bcfde680c39a6fdcf0f590c4c/api/integration.finc#L1) / [Author example/test](https://github.com/reinh-bader/fgsl/blob/27a3e7cc0809623bcfde680c39a6fdcf0f590c4c/doc/examples/integration.f90)

```text
Requested absolute/relative tolerance   1.0000E-07: all five integral families passed.
Requested absolute/relative tolerance   1.0000E-10: all five integral families passed.
Adaptive finite-interval integrals with one reused workspace: 40
Integrand evaluations: 4704
Maximum normalized analytical integral error:   3.5069E-13
Maximum normalized reported error estimate:   3.1979E-08
PASS fgsl-qags-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers rkf45-analytic-reference fgsl-qags-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
