# Checked GAMS ODE initial-value drivers

These consumer programs connect specific nonstiff initial-value solvers to the same analytic three-state problem. They test the named configuration, rather than every method offered by each package or performance on stiff equations.

| Class | Configuration | Procedure |
| --- | --- | --- |
| [I1a1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a1a) | One-step methods for general nonstiff or mildly stiff IVPs | DOP853 `dop853_class%integrate`; rklib `rk4_class%integrate` |
| [I1a1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a1b) | Multistep methods for general nonstiff or mildly stiff IVPs | DDEABM `ddeabm_class%integrate` |

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers dop853-decay-oscillator ddeabm-decay-oscillator rklib-decay-oscillator
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
