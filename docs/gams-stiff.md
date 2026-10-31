# Checked GAMS stiff-ODE drivers

These three examples demonstrate the stiff ODE part of [I1a2: Stiff and mixed algebraic-differential equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/I1a2). They do not establish DAE support or validate every method in these packages. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Shared autonomous two-scale system

```text
dy1/dt = -1000*y1 + 999*y2
dy2/dt = -y2
y(0) = [2,1]

y1(t) = exp(-t) + exp(-1000*t)
y2(t) = exp(-t)
y1(t)-y2(t) = exp(-1000*t)
```

The constant Jacobian has eigenvalues -1000 and -1, giving fast and slow decaying modes with time scales 0.001 and 1. The exact solution follows directly from the two differential equations. Each real64 driver advances through `t=[0.001,0.01,0.1,1]`, so the first point includes the fast transient and the later points follow its decay.

Every output requires finite time/state values, successful solver status and absolute time error at most `1e-12`. Maximum scaled state error `max(abs(y-exact)/max(1,abs(exact)))` must be at most `2e-6`. The absolute error in the fast-mode identity `y1-y2=exp(-1000*t)` must be at most `4e-6`. References use the analytic exponentials, not output from another solver. These are checks at the four requested times, not uniform error bounds between output points.

## Configurations and status checks

| Package | Configuration | Required success |
| --- | --- | --- |
| DVODE | `dvode_t%solve`, `MF=22`: BDF and an internally approximated full Jacobian; scalar `rtol=1e-8`, `atol=1e-10`; real/integer workspaces 100/40 | State `2` at each output |
| ODEPACK | `lsoda_class%integrate`: automatic Adams/BDF switching; internal Jacobian; `rtol=1e-8`, `atol=[1e-10]`; maximum 5000 internal steps per call | State `2` at each output; at least one reported BDF method indicator |
| stiff3 | Third-order autonomous Rosenbrock solver; analytic constant Jacobian; `eps=1e-8`, weights `[1,1]`, initial suggested half-step `1e-6` | Status `0` at each output |

DVODE and LSODA initialize once, then continue the solution through successive output requests. The DVODE state and work arrays are retained. stiff3 advances the returned state/time over each successive interval and carries forward the suggested step size; the simple API is called anew for each interval.

stiff3 uses its own weighted error test based on `w(i)*abs(estimated_error(i))/(1+abs(y(i)))` and `eps`. This is not an identical tolerance contract to the `rtol/atol` controls of DVODE and LSODA. The analytic Jacobian is supplied only to stiff3 in these examples.

LSODA reports its current method indicator through `info(meth=...)`: `1=Adams`, `2=BDF`. The saved run reports Adams at 0.001 and 0.01, then BDF at 0.1 and 1. The driver requires observation of BDF mode, without fixing a particular switching time or requiring an exact history of internal steps.

Step/evaluation counters are printed as API examples. DVODE and LSODA counters are cumulative; stiff3 statistics are for each interval. Different methods, Jacobian configurations, counters and error tests make these outputs unsuitable as a controlled performance or accuracy ranking.

## Scope and sources

The examples adapt author callback and invocation patterns to a common small linear ODE. Nonlinear stiffness, large sparse Jacobians, DAEs, events, discontinuities and all failure modes are outside this validation. The separate [nonstiff ODE review](gams-ode.md) covers other configurations.

| Driver | Pinned procedure and author example |
| --- | --- |
| [Load dvode-stiff-two-scale](https://beliavsky.github.io/fortran-playground/fpm/?package=dvode&example=gams-dvode-stiff-two-scale) / [Source](../fpm_catalog/gams-drivers/dvode-stiff-two-scale.f90) | [Procedure](https://github.com/jacobwilliams/dvode/blob/59d2eedd1410a4bd6c196c24d08f95a7c20565c0/src/dvode_module.F90#L251) / [Author example](https://github.com/jacobwilliams/dvode/blob/59d2eedd1410a4bd6c196c24d08f95a7c20565c0/test/dvdemo.f90) |
| [Load lsoda-stiff-two-scale](https://beliavsky.github.io/fortran-playground/fpm/?package=odepack&example=gams-lsoda-stiff-two-scale) / [Source](../fpm_catalog/gams-drivers/lsoda-stiff-two-scale.f90) | [Procedure](https://github.com/Nicholaswogan/odepack/blob/d5db96093dc14fff54e10575cc586fa85392b078/src/odepack_mod.f90#L13) / [Author example](https://github.com/Nicholaswogan/odepack/blob/d5db96093dc14fff54e10575cc586fa85392b078/test/benchmark.f90) |
| [Load stiff3-stiff-two-scale](https://beliavsky.github.io/fortran-playground/fpm/?package=stiff3&example=gams-stiff3-stiff-two-scale) / [Source](../fpm_catalog/gams-drivers/stiff3-stiff-two-scale.f90) | [Procedure](https://github.com/ivan-pi/stiff3/blob/70ab5c86c2ac922ed148bbb1182345cca248e077/src/stiff3_solver.f90#L71) / [Author example](https://github.com/ivan-pi/stiff3/blob/70ab5c86c2ac922ed148bbb1182345cca248e077/example/hires.f90) |

License notices, including the ODEPACK LLNL public-domain notice, are retained. Module callbacks avoid executable-stack trampolines. The drivers appear in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-stiff-validation.json) records hashes, pins and saved output.

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers dvode-stiff-two-scale lsoda-stiff-two-scale stiff3-stiff-two-scale
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
