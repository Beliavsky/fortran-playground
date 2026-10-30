# Checked GAMS scalar-root drivers

These consumer programs solve two nonpolynomial scalar equations using roots-fortran Brent, nonlin Brent and nonlin safeguarded Newton. They map to [F1b: nonpolynomial single equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/F1b). F1b has no deeper derivative-specific classes; the procedure records distinguish derivative requirements.

## Shared checks

| Equation | Bracket | Reference root |
| --- | --- | --- |
| `sin(x)/x = 0` | `[1.5,5]` | `pi` |
| `exp(x)-2 = 0` | `[0,2]` | `log(2)` |

Each driver requests function/variable tolerances `1e-12` and independently requires both root error and absolute residual at most `1e-9`. It checks convergence, finite results, bracket membership and agreement between the returned residual and a fresh function evaluation. Counters include solver callbacks only. The Newton driver supplies an analytic derivative, checks it against a central difference at the bracket midpoint, resets the counters and verifies that the solver uses it. nonlin chooses its initial point from the bracket; these drivers do not assume that its input root variable controls the initial iterate.

## Sources and playground links

| Driver | Pinned procedure | Author example |
| --- | --- | --- |
| [Load roots-fortran-brent](https://beliavsky.github.io/fortran-playground/fpm/?package=roots-fortran&example=gams-roots-fortran-brent) · [Source](../fpm_catalog/gams-drivers/roots-fortran-brent.f90) | [Procedure](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/src/root_module.F90#L123) | Original driver using the public object API |
| [Load nonlin-roots-brent](https://beliavsky.github.io/fortran-playground/fpm/?package=nonlin&example=gams-nonlin-roots-brent) · [Source](../fpm_catalog/gams-drivers/nonlin-roots-brent.f90) | [Procedure](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_solve.f90#L92) | [Example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_brent_example.f90) |
| [Load nonlin-roots-newton](https://beliavsky.github.io/fortran-playground/fpm/?package=nonlin&example=gams-nonlin-roots-newton) · [Source](../fpm_catalog/gams-drivers/nonlin-roots-newton.f90) | [Procedure](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_solve.f90#L101) | [Example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_newton1d_example.f90) |

The nonlin drivers adapt the author examples, including the `sin(x)/x` equation; MIT notices are retained. Loading a link selects code without submitting a job. These examples also appear in the main local FPM playground and downloaded FPM projects.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only the mains and executables were rebuilt. The [verification report](gams-roots-validation.json) records source hashes, revisions and run output. Evaluation counts describe these two cases, rather than a general performance ranking. Zero printed error means agreement at working precision.

### roots-fortran-brent

```text
Case: sin(x)/x = 0 on [1.5,5], root pi
Computed root:   3.14159265358979E+00
Actual root error:   0.0000E+00
Independent absolute residual:   3.8982E-17
Function callback calls: 10
Derivative callback calls: 0
Solver status: 0
Case: exp(x)-2 = 0 on [0,2], root log(2)
Computed root:   6.93147180559945E-01
Actual root error:   1.1102E-16
Independent absolute residual:   2.2204E-16
Function callback calls: 9
Derivative callback calls: 0
Solver status: 0
PASS roots-fortran-brent
```

### nonlin-roots-brent

```text
Case: sin(x)/x = 0 on [1.5,5], root pi
Computed root:   3.14159265358979E+00
Actual root error:   0.0000E+00
Independent absolute residual:   3.8982E-17
Function callback calls: 10
Derivative callback calls: 0
Case: exp(x)-2 = 0 on [0,2], root log(2)
Computed root:   6.93147180559945E-01
Actual root error:   1.1102E-16
Independent absolute residual:   2.2204E-16
Function callback calls: 9
Derivative callback calls: 0
PASS nonlin-roots-brent
```

### nonlin-roots-newton

```text
Case: sin(x)/x = 0 on [1.5,5], root pi
Computed root:   3.14159265358979E+00
Actual root error:   0.0000E+00
Independent absolute residual:   3.8982E-17
Function callback calls: 8
Derivative callback calls: 5
Case: exp(x)-2 = 0 on [0,2], root log(2)
Computed root:   6.93147180560025E-01
Actual root error:   8.0158E-14
Independent absolute residual:   1.6032E-13
Function callback calls: 8
Derivative callback calls: 5
PASS nonlin-roots-newton
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers roots-fortran-brent nonlin-roots-brent nonlin-roots-newton
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
