# Checked GAMS ODE initial-value drivers

The DOP853, rklib and DDEABM consumers share the analytic three-state problem below. Other consumers in the recorded results use separately documented fixtures. Each proof concerns the named configuration, rather than every method offered by each package or performance on stiff equations. The [FLINT review](gams-adaptive-ad.md) covers four adaptive methods, three analytic systems, forward/backward intervals and repeated dense output. The [DASKR review](gams-dae-fft.md) covers index-one DAEs, supplied consistent initial data, dense direct solves and numerical/user Jacobians.

| Class | Configuration | Procedure |
| --- | --- | --- |
| [I1a1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a1a) | One-step methods for general nonstiff or mildly stiff IVPs | DOP853 `dop853_class%integrate`; rklib `rk4_class%integrate` |
| [I1a1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a1b) | Multistep methods for general nonstiff or mildly stiff IVPs | DDEABM `ddeabm_class%integrate` |
| [I1a2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a2) | Stiff/DAE IVPs; checked dense-direct index-one configuration | DASKR `ddaskr` |

## Shared analytic problem

```text
u' = -u,   q' = v,   v' = -q
(u,q,v)(0) = (1,1,0)
(u,q,v)(t) = (exp(-t),cos(t),-sin(t))
```

Each driver advances from 0 to `2*pi`, checking all three states at ten equally spaced output times. It requires finite values, nonnegative decay state, maximum absolute state error at most `1e-8` and oscillator energy error `abs(q*q+v*v-1)` at most `2e-8`. Checking the analytic state also detects phase errors that an energy check could miss. These bounds apply at the reported checkpoints, rather than every internal step.

DOP853 and DDEABM request absolute and relative tolerances `1e-10`. DOP853 must return status 1; DDEABM must return 2 or 3, both of which mean the requested time was reached. Both drivers also check the returned output time. A positive intermediate-step status is insufficient. DDEABM keeps its history across output requests; DOP853 is called for each successive interval.

rklib uses classical fixed-step RK4 with step `0.01`, shortened at each requested endpoint, and requires status 0. Its API returns the state for the supplied final time, rather than a separate actual-time output. Fixed-step and adaptive tolerance settings are different accuracy controls; matching the problem and acceptance checks does not make their settings equivalent.

## RK4 step refinement

A separate RK4 experiment integrates the same problem directly to `2*pi` with nominal steps `2*pi/100` and `2*pi/200`. Both runs must complete with finite states, and their coarse/fine endpoint-error ratio must lie between 12 and 20. Fourth-order convergence suggests a ratio approaching 16 in this range. These coarser runs are separate from the `1e-8` checkpoint acceptance test. Floating-point endpoint rounding can produce a tiny additional final step, so callback counts need not equal four times the nominal step count.

## Sources and playground links

| Driver | Class | Pinned procedure and author example |
| --- | --- | --- |
| [Load dop853-decay-oscillator](https://beliavsky.github.io/fortran-playground/fpm/?package=dop853&example=gams-dop853-decay-oscillator) · [Source](../fpm_catalog/gams-drivers/dop853-decay-oscillator.f90) | I1a1a | [Procedure](https://github.com/jacobwilliams/dop853/blob/1e9d0dbf4dcbc692ca557c0467629112dd1f0ce6/src/dop853_module.F90#L204) · [Author example](https://github.com/jacobwilliams/dop853/blob/1e9d0dbf4dcbc692ca557c0467629112dd1f0ce6/test/dop853_test.f90) |
| [Load ddeabm-decay-oscillator](https://beliavsky.github.io/fortran-playground/fpm/?package=ddeabm&example=gams-ddeabm-decay-oscillator) · [Source](../fpm_catalog/gams-drivers/ddeabm-decay-oscillator.f90) | I1a1b | [Procedure](https://github.com/jacobwilliams/ddeabm/blob/dba70c8c65388638662df2694339c5ba7feaf12a/src/ddeabm_module.F90#L60) · [Author example](https://github.com/jacobwilliams/ddeabm/blob/dba70c8c65388638662df2694339c5ba7feaf12a/test/ddeabm_test.f90) |
| [Load rklib-decay-oscillator](https://beliavsky.github.io/fortran-playground/fpm/?package=rklib&example=gams-rklib-decay-oscillator) · [Source](../fpm_catalog/gams-drivers/rklib-decay-oscillator.f90) | I1a1a | [Procedure](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/src/rklib_fixed_steps.f90#L203) · [Author example](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/test/rk_decay.F90) |
| [Load dvode-stiff-two-scale](https://beliavsky.github.io/fortran-playground/fpm/?package=dvode&example=gams-dvode-stiff-two-scale) · [Source](../fpm_catalog/gams-drivers/dvode-stiff-two-scale.f90) | I1a2 | [Procedure](https://github.com/jacobwilliams/dvode/blob/59d2eedd1410a4bd6c196c24d08f95a7c20565c0/src/dvode_module.F90#L251) · [Author example](https://github.com/jacobwilliams/dvode/blob/59d2eedd1410a4bd6c196c24d08f95a7c20565c0/test/dvdemo.f90) |
| [Load lsoda-stiff-two-scale](https://beliavsky.github.io/fortran-playground/fpm/?package=odepack&example=gams-lsoda-stiff-two-scale) · [Source](../fpm_catalog/gams-drivers/lsoda-stiff-two-scale.f90) | I1a2 | [Procedure](https://github.com/Nicholaswogan/odepack/blob/d5db96093dc14fff54e10575cc586fa85392b078/src/odepack_mod.f90#L13) · [Author example](https://github.com/Nicholaswogan/odepack/blob/d5db96093dc14fff54e10575cc586fa85392b078/test/benchmark.f90) |
| [Load stiff3-stiff-two-scale](https://beliavsky.github.io/fortran-playground/fpm/?package=stiff3&example=gams-stiff3-stiff-two-scale) · [Source](../fpm_catalog/gams-drivers/stiff3-stiff-two-scale.f90) | I1a2 | [Procedure](https://github.com/ivan-pi/stiff3/blob/70ab5c86c2ac922ed148bbb1182345cca248e077/src/stiff3_solver.f90#L71) · [Author example](https://github.com/ivan-pi/stiff3/blob/70ab5c86c2ac922ed148bbb1182345cca248e077/example/hires.f90) |
| [Load featom-coulomb-spectrum](https://beliavsky.github.io/fortran-playground/fpm/?package=featom&example=gams-featom-coulomb-spectrum) · [Source](../fpm_catalog/gams-drivers/featom-coulomb-spectrum.f90) | I1b | [Procedure](https://github.com/atomic-solvers/featom/blob/87872a3266ceeee61a7244e6ecd134dc3bda790f/src/schroed_dirac_solver.f90#L18) · [Author example](https://github.com/atomic-solvers/featom/blob/87872a3266ceeee61a7244e6ecd134dc3bda790f/test/test_coulomb_schroed.f90) |
| [Load hrweno-tvd-ode-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=hrweno&example=gams-hrweno-tvd-ode-reference) · [Source](../fpm_catalog/gams-drivers/hrweno-tvd-ode-reference.f90) | I1 | [Procedure](https://github.com/HugoMVale/HR-WENO/blob/2885105a7ba98351fed299b22e9bc0c67a809d2f/src/hrweno_tvdode.f90#L97) · [Author example](https://github.com/HugoMVale/HR-WENO/blob/2885105a7ba98351fed299b22e9bc0c67a809d2f/None) |
| [Load rkf45-analytic-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=rkf45&example=gams-rkf45-analytic-reference) · [Source](../fpm_catalog/gams-drivers/rkf45-analytic-reference.f90) | I1a1a | [Procedure](https://github.com/zoziha/rkf45/blob/93cd129369357ee08e34be7868256b21a500cc98/src/rkf45.F90#L57) · [Author example](https://github.com/zoziha/rkf45/blob/93cd129369357ee08e34be7868256b21a500cc98/test/test_rkf45.f90) |
| [Load diffeq-rk45-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=diffeq&example=gams-diffeq-rk45-reference) · [Source](../fpm_catalog/gams-drivers/diffeq-rk45-reference.f90) | I1a1a | [Procedure](https://github.com/jchristopherson/diffeq/blob/989b320179c23aaff4bfe72994c90e9034f50c74/src/singlestep/explicit/diffeq_rk45.f90#L32) · [Author example](https://github.com/jchristopherson/diffeq/blob/989b320179c23aaff4bfe72994c90e9034f50c74/examples/rk45_example.f90) |
| [Load dynamics-response-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=dynamics&example=gams-dynamics-response-reference) · [Source](../fpm_catalog/gams-drivers/dynamics-response-reference.f90) | I1 | [Procedure](https://github.com/jchristopherson/dynamics/blob/580d04859a25126d3261e44b3fbec5111835e3a4/src/frequency/dynamics_frequency_response.f90#L119) · [Author example](https://github.com/jchristopherson/dynamics/blob/580d04859a25126d3261e44b3fbec5111835e3a4/examples/frf_example_1.f90) |
| [Load flint-ivp-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=flint&example=gams-flint-ivp-reference) · [Source](../fpm_catalog/gams-drivers/flint-ivp-reference.f90) | I1a1a | [Procedure](https://github.com/princemahajan/FLINT/blob/b6322037cb751b11fa64ea66cf23173ae572fff6/src/ERK.f90#L72) · [Author example](https://github.com/princemahajan/FLINT/blob/b6322037cb751b11fa64ea66cf23173ae572fff6/tests/test_WP.f90) |
| [Load daskr-dae-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=daskr&example=gams-daskr-dae-reference) · [Source](../fpm_catalog/gams-drivers/daskr-dae-reference.f90) | I1a2 | [Procedure](https://github.com/davidpfister/daskr/blob/b43533edc5d6900088a846d802e3a86d0f9a06ad/src/ddaskr.f#L1) · [Author example](https://github.com/davidpfister/daskr/blob/b43533edc5d6900088a846d802e3a86d0f9a06ad/examples/web/dweb.f) |
| [Load fatode-tangent-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fatode&example=gams-fatode-tangent-reference) · [Source](../fpm_catalog/gams-drivers/fatode-tangent-reference.f90) | I1 | [Procedure](https://github.com/ComputationalScienceLaboratory/FATODE/blob/3f237c49bd377644a597c2a49ae5a83f090bfab5/TLM/ERK_TLM/ERK_TLM_f90_Integrator.F90#L1) · [Author example](https://github.com/ComputationalScienceLaboratory/FATODE/blob/3f237c49bd377644a597c2a49ae5a83f090bfab5/EXAMPLES/swe/SWE_ERK_TLM/swe2D_erk_tlm_dr.F90) |
| [Load dftatom-hydrogen-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=dftatom&example=gams-dftatom-hydrogen-reference) · [Source](../fpm_catalog/gams-drivers/dftatom-hydrogen-reference.f90) | I1 | [Procedure](https://github.com/certik/dftatom/blob/e49b3042de6e2471afe5eea992c9ba50dac08f95/src/reigen.f90#L1) · [Author example](https://github.com/certik/dftatom/blob/e49b3042de6e2471afe5eea992c9ba50dac08f95/tests/hydrogen/hydrogen.f90) |
| [Load friction-lugre-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=friction&example=gams-friction-lugre-reference) · [Source](../fpm_catalog/gams-drivers/friction-lugre-reference.f90) | I1 | [Procedure](https://github.com/jchristopherson/friction/blob/8e75dcac26f47417a439adfcbaa24834105d89fe/src/models/friction_lugre.f90#L161) · [Author example](https://github.com/jchristopherson/friction/blob/8e75dcac26f47417a439adfcbaa24834105d89fe/examples/lugre_example.f90) |

The drivers adapt author callback and integration API patterns to the shared analytic problem, without plotting dependencies; license notices are retained. They appear in hosted and main local FPM example menus and downloaded FPM projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-ode-validation.json) records source hashes, revisions and saved output. RHS callback counts cover solver evaluations, including startup and rejected steps where applicable; analytic reference checks are excluded. RK4 refinement counts are reported separately. Counts for this simple problem are not a general efficiency ranking.

### dop853-decay-oscillator

```text
       t      max state error      oscillator energy error
  0.628319      4.7220005683E-12      1.3413714584E-12
  1.256637      1.0212719559E-11      2.8211877279E-12
  1.884956      1.7763845950E-11      4.5562442708E-12
  2.513274      1.8615886610E-11      6.4901417574E-12
  3.141593      3.2305712626E-11      8.2807094515E-12
  3.769911      3.5819125443E-11      1.0435208253E-11
  4.398230      4.3393177940E-11      1.2283951634E-11
  5.026548      5.4541149375E-11      1.4214296407E-11
  5.654867      4.5995873776E-11      1.6230350397E-11
  6.283185      6.9760896379E-11      1.8041790284E-11
Maximum checkpoint state error:   6.9761E-11
Maximum checkpoint energy error:   1.8042E-11
RHS callback calls (checkpoint run): 500
Final solver status: 1
PASS dop853-decay-oscillator
```

### ddeabm-decay-oscillator

```text
       t      max state error      oscillator energy error
  0.628319      9.9187325020E-12      2.9487523534E-13
  1.256637      7.9399820052E-12      3.2843727737E-12
  1.884956      3.7807035280E-11      3.0371927195E-11
  2.513274      6.8081207338E-11      6.7992278474E-11
  3.141593      6.9838206565E-11      6.6069372195E-11
  3.769911      7.5627393237E-11      4.8849368994E-11
  4.398230      6.9915073730E-11      3.6267655545E-11
  5.026548      8.5696505447E-11      2.4099167106E-11
  5.654867      7.3835493275E-11      2.9862778916E-12
  6.283185      9.2504358673E-11      1.7406964758E-11
Maximum checkpoint state error:   9.2504E-11
Maximum checkpoint energy error:   6.7992E-11
RHS callback calls (checkpoint run): 147
Final solver status: 3
PASS ddeabm-decay-oscillator
```

### rklib-decay-oscillator

```text
       t      max state error      oscillator energy error
  0.628319      4.2321035565E-11      8.6464169158E-13
  1.256637      9.8637653601E-11      1.7299495170E-12
  1.884956      1.4875839449E-10      2.5960344985E-12
  2.513274      1.6724022167E-10      3.4624525469E-12
  3.141593      2.5996158248E-10      4.3276493500E-12
  3.769911      2.5389534919E-10      5.1938453538E-12
  4.398230      3.4518038428E-10      6.0593752238E-12
  5.026548      3.9662578777E-10      6.9247940715E-12
  5.654867      3.7624592331E-10      7.7906570084E-12
  6.283185      5.1987922788E-10      8.6557427892E-12
Maximum checkpoint state error:   5.1988E-10
Maximum checkpoint energy error:   8.6557E-12
RHS callback calls (checkpoint run): 2520
Final solver status: 0
RK4 nominal steps: 100; endpoint state error:   8.1490E-07; RHS calls: 404
RK4 nominal steps: 200; endpoint state error:   5.0985E-08; RHS calls: 804
Coarse/fine error ratio (fourth order suggests 16):    15.983086
PASS rklib-decay-oscillator
```

### dvode-stiff-two-scale

```text
t=  0.0010 state=   1.3668798588   0.9990004998
Scaled state error / fast-mode error:   6.0148E-08   8.2215E-08
Total steps=47 RHS evaluations=73
t=  0.0100 state=   0.9900952416   0.9900498337
Scaled state error / fast-mode error:   7.9264E-09   7.9263E-09
Total steps=133 RHS evaluations=170
t=  0.1000 state=   0.9048374278   0.9048374278
Scaled state error / fast-mode error:   9.7559E-09   2.1970E-12
Total steps=176 RHS evaluations=220
t=  1.0000 state=   0.3678794742   0.3678794742
Scaled state error / fast-mode error:   3.3000E-08   0.0000E+00
Total steps=198 RHS evaluations=250
PASS dvode-stiff-two-scale
```

### lsoda-stiff-two-scale

```text
t=  0.0010 state=   1.3668799572   0.9990004998
Scaled state error / fast-mode error:   1.1823E-08   1.6160E-08
Current method (1=Adams, 2=BDF)=1 total steps=24 RHS evaluations=53
t=  0.0100 state=   0.9900952331   0.9900498337
Scaled state error / fast-mode error:   5.9979E-10   5.9980E-10
Current method (1=Adams, 2=BDF)=1 total steps=72 RHS evaluations=151
t=  0.1000 state=   0.9048374287   0.9048374287
Scaled state error / fast-mode error:   1.0631E-08   6.0019E-13
Current method (1=Adams, 2=BDF)=2 total steps=115 RHS evaluations=241
t=  1.0000 state=   0.3678794484   0.3678794484
Scaled state error / fast-mode error:   7.2435E-09   4.5147E-13
Current method (1=Adams, 2=BDF)=2 total steps=142 RHS evaluations=294
PASS lsoda-stiff-two-scale
```

### stiff3-stiff-two-scale

```text
t=  0.0010 state=   1.3668799408   0.9990004998
Scaled state error / fast-mode error:   1.3871E-10   1.8960E-10
Interval accepted/rejected, RHS/Jacobian, LU/solves:      40       0     201      80     120     360
t=  0.0100 state=   0.9900952335   0.9900498337
Scaled state error / fast-mode error:   1.5324E-10   1.5324E-10
Interval accepted/rejected, RHS/Jacobian, LU/solves:     128       0     641     256     384    1152
t=  0.1000 state=   0.9048374180   0.9048374180
Scaled state error / fast-mode error:   9.1952E-12   3.3307E-16
Interval accepted/rejected, RHS/Jacobian, LU/solves:      20       0     101      40      60     180
t=  1.0000 state=   0.3678794411   0.3678794411
Scaled state error / fast-mode error:   1.0953E-10   0.0000E+00
Interval accepted/rejected, RHS/Jacobian, LU/solves:      39       0     196      78     117     351
PASS stiff3-stiff-two-scale
```

### featom-coulomb-spectrum

```text
Nuclear charge: 1; finite-element degrees of freedom: 159
n,l=  1  0; energy=     -0.499999999999; error=   1.170E-12
n,l=  2  0; energy=     -0.125000000000; error=   1.481E-13
n,l=  2  1; energy=     -0.125000000000; error=   5.784E-14
n,l=  3  0; energy=     -0.055555555556; error=   3.703E-14
n,l=  3  1; energy=     -0.055555555556; error=   1.198E-14
n,l=  3  2; energy=     -0.055555555556; error=   3.404E-14
Nuclear charge: 2; finite-element degrees of freedom: 159
n,l=  1  0; energy=     -2.000000000002; error=   1.704E-12
n,l=  2  0; energy=     -0.500000000000; error=   4.960E-13
n,l=  2  1; energy=     -0.500000000000; error=   1.903E-13
n,l=  3  0; energy=     -0.222222222222; error=   1.632E-13
n,l=  3  1; energy=     -0.222222222222; error=   5.218E-15
n,l=  3  2; energy=     -0.222222222222; error=   8.696E-14
Maximum absolute energy error:    1.70441E-12
Only the first six levels per charge are checked; full wavefunction accuracy is not claimed.
PASS featom-coulomb-spectrum
```

### hrweno-tvd-ode-reference

```text
Order=1 steps=8 continuous error=  7.0445E-02
Order=1 steps=16 continuous error=  3.4536E-02
Order=1 steps=32 continuous error=  1.7093E-02
Order=1 steps=64 continuous error=  8.5025E-03
Order=2 steps=8 continuous error=  6.8852E-03
Order=2 steps=16 continuous error=  1.5529E-03
Order=2 steps=32 continuous error=  3.6962E-04
Order=2 steps=64 continuous error=  9.0215E-05
Order=3 steps=8 continuous error=  4.3052E-04
Order=3 steps=16 continuous error=  4.8694E-05
Order=3 steps=32 continuous error=  5.7894E-06
Order=3 steps=64 continuous error=  7.0578E-07
Maximum error against independent discrete references:   4.4409E-16
12 ODE runs: orders 1..3, exponential decay, nonautonomous forcing and grid convergence.
PASS hrweno-tvd-ode-reference
```

### rkf45-analytic-reference

```text
Family 1: forward/backward runs at two rates and two initial states passed.
Family 2: forward/backward runs at two rates and two initial states passed.
Family 3: forward/backward runs at two rates and two initial states passed.
Integration runs: 24; requested target calls: 384
RHS evaluations: 11669
Maximum normalized analytical state error:   4.6749E-10
PASS rkf45-analytic-reference
```

### diffeq-rk45-reference

```text
Analytical IVP runs: 24; requested solution points: 408
RHS callback evaluations: 5616
Exponential/polynomial/oscillator; two rates, both directions and two tolerances.
Maximum normalized solution error:   1.6661E-08
PASS diffeq-rk45-reference
```

### dynamics-response-reference

```text
Harmonic response fixtures: 24; complex coordinate checks: 384
Unit mass, diagonal stiffness only; broader failed probes retained separately.
Maximum normalized response error:   0.0000E+00
PASS dynamics-response-reference
```

### flint-ivp-reference

```text
Adaptive integrations: 96
Endpoint reference entries: 288
Dense-output reference entries: 9792
Maximum normalized error:   1.6699E-09
PASS flint-ivp-reference
```

### daskr-dae-reference

```text
DAE trajectories: 96
Requested checkpoints: 768
Analytic state/derivative entries: 4608
Trajectories using user Jacobians: 48
Maximum normalized state error:   4.6001E-10
Maximum normalized derivative error:   1.6290E-07
Maximum normalized constraint error:   6.9436E-11
Maximum scaled residual:   1.0779E-08
PASS daskr-dae-reference
```

### fatode-tangent-reference

```text
Tangent integrations: 540; state entries: 2160; derivative entries: 8640
Actual RHS and analytic-Jacobian callbacks:       535978      535978
Maximum normalized state and tangent errors:    4.43326E-10   7.23387E-10
Dopri5/Dopri853, forward/backward time, full initial-state/parameter derivatives checked.
PASS fatode-tangent-reference
```

### dftatom-hydrogen-reference

```text
Case Z,mesh,n,l and six errors:      1  3000     1     0   2.171E-11   9.504E-11   1.204E-05   3.537E-06   7.696E-11   5.373E-11
Case Z,mesh,n,l and six errors:      1  3000     2     0   2.637E-11   3.242E-10   4.257E-06   3.537E-06   5.302E-10   5.208E-11
Case Z,mesh,n,l and six errors:      1  3000     2     1   8.325E-12   1.624E-10   4.719E-11   3.537E-06   1.841E-10   1.621E-11
Case Z,mesh,n,l and six errors:      1  3000     3     0   4.765E-11   9.192E-10   2.317E-06   3.537E-06   2.115E-09   9.095E-11
Case Z,mesh,n,l and six errors:      1  3000     3     1   2.604E-11   6.062E-10   1.374E-10   3.537E-06   1.190E-09   4.860E-11
Case Z,mesh,n,l and six errors:      1  3000     3     2   6.144E-12   2.419E-10   4.210E-11   3.537E-06   3.026E-10   1.172E-11
Case Z,mesh,n,l and six errors:      1  4500     1     0   5.142E-12   1.943E-11   5.226E-06   1.572E-06   1.664E-11   1.341E-11
Case Z,mesh,n,l and six errors:      1  4500     2     0   5.229E-12   6.474E-11   1.848E-06   1.572E-06   1.072E-10   1.100E-11
Case Z,mesh,n,l and six errors:      1  4500     2     1   1.649E-12   3.214E-11   9.322E-12   1.572E-06   3.660E-11   3.243E-12
Case Z,mesh,n,l and six errors:      1  4500     3     0   1.229E-12   2.745E-10   1.006E-06   1.572E-06   6.493E-10   4.669E-11
Case Z,mesh,n,l and six errors:      1  4500     3     1   5.143E-12   1.202E-10   2.722E-11   1.572E-06   2.369E-10   9.819E-12
Case Z,mesh,n,l and six errors:      1  4500     3     2   1.217E-12   4.792E-11   9.130E-12   1.572E-06   6.031E-11   2.359E-12
Case Z,mesh,n,l and six errors:      2  3000     1     0   2.171E-11   9.504E-11   1.204E-05   3.537E-06   7.696E-11   5.373E-11
Case Z,mesh,n,l and six errors:      2  3000     2     0   2.637E-11   3.242E-10   4.257E-06   3.537E-06   5.302E-10   5.208E-11
Case Z,mesh,n,l and six errors:      2  3000     2     1   8.325E-12   1.624E-10   4.719E-11   3.537E-06   1.841E-10   1.621E-11
Case Z,mesh,n,l and six errors:      2  3000     3     0   4.765E-11   9.192E-10   2.317E-06   3.537E-06   2.115E-09   9.095E-11
Case Z,mesh,n,l and six errors:      2  3000     3     1   2.604E-11   6.062E-10   1.374E-10   3.537E-06   1.190E-09   4.860E-11
Case Z,mesh,n,l and six errors:      2  3000     3     2   6.144E-12   2.419E-10   4.210E-11   3.537E-06   3.026E-10   1.172E-11
Case Z,mesh,n,l and six errors:      2  4500     1     0   5.142E-12   1.943E-11   5.226E-06   1.572E-06   1.664E-11   1.341E-11
Case Z,mesh,n,l and six errors:      2  4500     2     0   5.229E-12   6.474E-11   1.848E-06   1.572E-06   1.072E-10   1.100E-11
Case Z,mesh,n,l and six errors:      2  4500     2     1   1.649E-12   3.214E-11   9.322E-12   1.572E-06   3.660E-11   3.243E-12
Case Z,mesh,n,l and six errors:      2  4500     3     0   1.229E-12   2.745E-10   1.006E-06   1.572E-06   6.493E-10   4.669E-11
Case Z,mesh,n,l and six errors:      2  4500     3     1   5.143E-12   1.202E-10   2.722E-11   1.572E-06   2.369E-10   9.819E-12
Case Z,mesh,n,l and six errors:      2  4500     3     2   1.217E-12   4.792E-11   9.130E-12   1.572E-06   6.031E-11   2.359E-12
Case Z,mesh,n,l and six errors:      4  3000     1     0   2.171E-11   9.504E-11   1.204E-05   3.537E-06   7.696E-11   5.373E-11
Case Z,mesh,n,l and six errors:      4  3000     2     0   2.637E-11   3.242E-10   4.257E-06   3.537E-06   5.302E-10   5.208E-11
Case Z,mesh,n,l and six errors:      4  3000     2     1   8.325E-12   1.624E-10   4.719E-11   3.537E-06   1.841E-10   1.621E-11
Case Z,mesh,n,l and six errors:      4  3000     3     0   4.765E-11   9.192E-10   2.317E-06   3.537E-06   2.115E-09   9.095E-11
Case Z,mesh,n,l and six errors:      4  3000     3     1   2.604E-11   6.062E-10   1.374E-10   3.537E-06   1.190E-09   4.860E-11
Case Z,mesh,n,l and six errors:      4  3000     3     2   6.144E-12   2.419E-10   4.210E-11   3.537E-06   3.026E-10   1.172E-11
Case Z,mesh,n,l and six errors:      4  4500     1     0   5.142E-12   1.943E-11   5.226E-06   1.572E-06   1.664E-11   1.341E-11
Case Z,mesh,n,l and six errors:      4  4500     2     0   5.229E-12   6.474E-11   1.848E-06   1.572E-06   1.072E-10   1.100E-11
Case Z,mesh,n,l and six errors:      4  4500     2     1   1.649E-12   3.214E-11   9.322E-12   1.572E-06   3.660E-11   3.243E-12
Case Z,mesh,n,l and six errors:      4  4500     3     0   1.229E-12   2.745E-10   1.006E-06   1.572E-06   6.493E-10   4.669E-11
Case Z,mesh,n,l and six errors:      4  4500     3     1   5.143E-12   1.202E-10   2.722E-11   1.572E-06   2.369E-10   9.819E-12
Case Z,mesh,n,l and six errors:      4  4500     3     2   1.217E-12   4.792E-11   9.130E-12   1.572E-06   6.031E-11   2.359E-12
Radial eigenproblems: 36; P references and Q references each: 135036
Max energy, P, Q, normalization, radius and inverse-radius errors:    4.76529E-11   9.19163E-10   1.20398E-05   3.53696E-06   2.11486E-09   9.09494E-11
Nonrelativistic Coulomb states only; Dirac, general potentials and self-consistent DFT unverified.
PASS dftatom-hydrogen-reference
```

### friction-lugre-reference

```text
LuGre constant-velocity segments: 288; state/derivative/force references each: 1440
Numerical integration callback evaluations: 80598
Max normalized state, derivative and force errors:    1.18833E-11   4.33973E-17   1.13208E-10
72 histories; velocity reversals, rest, changing loads and nonzero initial bristle states.
Public LuGre state integration only; private fitting callbacks and parameter fitting unverified.
PASS friction-lugre-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers dop853-decay-oscillator ddeabm-decay-oscillator rklib-decay-oscillator
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
