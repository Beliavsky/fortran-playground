# Checked GAMS nonlinear-system drivers

These three drivers demonstrate [F2: Systems of nonlinear equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/F2). The task is to find a zero of a vector function. The related Rosenbrock optimization drivers minimize a scalar objective and have separate GAMS assignments. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Shared problem and independent checks

All three solve the square two-variable system:

```text
F1(x,y) = 1-x
F2(x,y) = 10*(y-x**2)
J(x,y)  = [[-1, 0], [-20*x, 10]]
```

The exact root is `(1,1)`: the first equation fixes `x=1`, and the second then fixes `y=1`. Each driver starts from both `(-1.2,1)` and `(2,2)`. The analytic Jacobian is nonsingular everywhere (determinant `-10`), but that alone does not guarantee convergence of every iteration strategy.

Every run requires finite returned values, a successful termination condition, `max(abs(x-[1,1])) <= 1e-8` and an independently recomputed residual infinity norm `max(abs([1-x,10*(y-x**2)])) <= 1e-8`. MINPACK and nonlin also return a residual vector; it must agree with the recomputed vector within `1e-12`. These extra checks prevent a small step or stationary point alone from being accepted as a root.

## Configurations and termination

| Package and procedure | Configuration | Accepted termination |
| --- | --- | --- |
| MINPACK `hybrd1` | Powell hybrid method; finite-difference Jacobian; `tol=1e-10`; documented workspace size | `info=1`, plus root/residual checks |
| nonlin `newton_solver%solve` | Newton with backtracking; both default finite-difference and supplied analytic Jacobians; function tolerance `1e-10`, variable/gradient tolerances `1e-12`; at most 2000 function evaluations | Function or variable-change convergence, plus root/residual checks |
| nlesolver-fortran `nlesolver_type%solve` | Dense analytic Jacobian; backtracking (`step_mode=2`); Broyden updates disabled; function tolerance `1e-10`, variable tolerance `1e-12`; at most 200 iterations | Initialization status `0`, then solve status `1` (required accuracy achieved), plus root/residual checks |

The nonlin driver uses separate function-helper objects so the finite-difference case has no analytic Jacobian attached. All four nonlin runs reported function convergence in the saved verification. nlesolver-fortran adapts callback and status patterns from the author sparse test, while explicitly selecting dense mode for this small system. Its sparse solvers are not exercised here.

Iteration and evaluation counts are shown to explain the API. Package counters and algorithms differ; for example, a reported function count need not account for every evaluation used to approximate a Jacobian. These outputs are not a controlled speed comparison. Other starting points, ill-conditioned or singular systems, larger dimensions and general convergence guarantees are outside this review.

## Sources and playground links

| Driver | Pinned procedure and author example |
| --- | --- |
| [Load minpack-rosenbrock-system](https://beliavsky.github.io/fortran-playground/fpm/?package=minpack&example=gams-minpack-rosenbrock-system) / [Source](../fpm_catalog/gams-drivers/minpack-rosenbrock-system.f90) | [Procedure](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/src/minpack.f90#L959) / [Author example](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/examples/example_hybrd1.f90) |
| [Load nonlin-rosenbrock-system](https://beliavsky.github.io/fortran-playground/fpm/?package=nonlin&example=gams-nonlin-rosenbrock-system) / [Source](../fpm_catalog/gams-drivers/nonlin-rosenbrock-system.f90) | [Procedure](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_solve.f90#L83) / [Author example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_newton_example.f90) |
| [Load nlesolver-rosenbrock-system](https://beliavsky.github.io/fortran-playground/fpm/?package=nlesolver-fortran&example=gams-nlesolver-rosenbrock-system) / [Source](../fpm_catalog/gams-drivers/nlesolver-rosenbrock-system.f90) | [Procedure](https://github.com/jacobwilliams/nlesolver-fortran/blob/60f38870a25e6b448dd552f184aa2f8616fc8cb0/src/nlesolver_module.F90#L97) / [Author example](https://github.com/jacobwilliams/nlesolver-fortran/blob/60f38870a25e6b448dd552f184aa2f8616fc8cb0/test/sparse_test.f90) |

The drivers adapt author API patterns, retain license notices and use module callbacks to avoid executable-stack trampolines. They appear in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-systems-validation.json) records source hashes, pins and saved output.

### minpack-rosenbrock-system

```text
Start:  -1.200   1.000 root:  1.0000000000  1.0000000000
info=1 function calls=22 residual=  0.00E+00 root error=  0.00E+00
Start:   2.000   2.000 root:  1.0000000000  1.0000000000
info=1 function calls=7 residual=  0.00E+00 root error=  0.00E+00
PASS minpack-rosenbrock-system
```

### nonlin-rosenbrock-system

```text
Finite-difference Jacobian
Start:  -1.200   1.000 root:  1.0000000000  1.0000000000
iterations=15 function calls=28 residual=  0.00E+00 root error=  0.00E+00
function convergence=T change convergence=F
Start:   2.000   2.000 root:  1.0000000000  1.0000000000
iterations=3 function calls=4 residual=  0.00E+00 root error=  0.00E+00
function convergence=T change convergence=F
Analytic Jacobian
Start:  -1.200   1.000 root:  1.0000000000  1.0000000000
iterations=14 function calls=27 residual=  0.00E+00 root error=  0.00E+00
function convergence=T change convergence=F
Start:   2.000   2.000 root:  1.0000000000  1.0000000000
iterations=2 function calls=3 residual=  0.00E+00 root error=  0.00E+00
function convergence=T change convergence=F
PASS nonlin-rosenbrock-system
```

### nlesolver-rosenbrock-system

```text
Start:  -1.200   1.000 root:  1.0000000000  1.0000000000
status=1 Required accuracy achieved
function calls=120 Jacobian calls=26 residual=  0.00E+00 root error=  0.00E+00
Start:   2.000   2.000 root:  1.0000000000  1.0000000000
status=1 Required accuracy achieved
function calls=151 Jacobian calls=32 residual=  0.00E+00 root error=  0.00E+00
PASS nlesolver-rosenbrock-system
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers minpack-rosenbrock-system nonlin-rosenbrock-system nlesolver-rosenbrock-system
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
