# Checked GAMS constrained-optimization drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [G2h1a2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2h1a2) | Smooth simple-bound optimization with user first derivatives | L-BFGS-B `setulb`; NLopt `LD_LBFGS` with explicit bounds |
| [G2h3b1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2h3b1b) | Smooth nonlinear equality/inequality optimization with user objective and constraint first derivatives | SLSQP `slsqp_solver%optimize`, analytic mode |

Both are deepest recorded GAMS classes for the demonstrated configurations. Other constrained optimization classes and other procedures in these classes still need checked drivers; see the [coverage report](gams-coverage.md).

## Shared bound-constrained quadratic

Minimize `f(x)=(x1-2)**2+(x2+1)**2` subject to `0<=x1<=1` and `0<=x2<=2`, starting at `[0.25,1]`. Projection of the unconstrained minimizer `[2,-1]` onto the box gives the unique solution `[1,0]`, with objective 2. One variable is on its upper bound and the other on its lower bound.

The two drivers check their analytic gradient against central differences before solving. They require actual convergence, finite results, parameter/objective error at most `1e-8`, maximum bound violation at most `1e-10`, agreement of reported and independent objectives within `1e-10`, and projected-gradient residual at most `1e-8`. The latter is `max(abs(x-clip(x-gradient(f),lower,upper)))`. At a boundary solution, the ordinary gradient need not be zero.

L-BFGS-B uses reverse communication and must return a convergence task. NLopt must return one of its convergence codes 1 through 4; an evaluation/time limit does not count as success. The NLopt bound configuration has a separate procedure record from its unconstrained Rosenbrock example. These packages are not asserted to use identical algorithms.

## Equality plus nonlinear inequality

The SLSQP driver minimizes the same objective over a different feasible set: `c1=x1+x2-1=0`, `c2=1-x1**2-x2**2>=0`, with inactive safety bounds `[-2,2]` and feasible start `[0.5,0.5]`. Equalities come first in the callback; SLSQP inequalities use the nonnegative convention. Analytic mode (`gradient_mode=0`) supplies both the objective gradient and constraint Jacobian, which are sanity-checked by central differences.

On the line `x1+x2=1`, the circle restricts `x1` to `[0,1]`, and the objective becomes `2*(x1-2)**2`. The unique constrained solution is therefore `[1,0]`, with objective 2. The driver requires solver status 0, finite values and parameter/objective errors at most `1e-7`. It independently checks primal feasibility, stationarity and complementarity within `1e-7`, using the exact multipliers `lambda=2` and `mu=2>=0`:

```text
gradient(f) - lambda*gradient(c1) - mu*gradient(c2) = 0
mu*c2 = 0
```

The multipliers are known from this test problem, not reported by SLSQP. The convex problem gives an independently known global solution; a successful run of a general nonlinear optimizer is not by itself a global-optimality guarantee.

## Sources and playground links

| Driver | Class | Pinned procedure and author example |
| --- | --- | --- |
| [Load lbfgsb-box-quadratic](https://beliavsky.github.io/fortran-playground/fpm/?package=lbfgsb&example=gams-lbfgsb-box-quadratic) · [Source](../fpm_catalog/gams-drivers/lbfgsb-box-quadratic.f90) | G2h1a2 | [Procedure](https://github.com/jacobwilliams/lbfgsb/blob/ce1a9322016d6f31b652393e000a914b63af6fef/src/lbfgsb.f90#L88) · [Author example](https://github.com/jacobwilliams/lbfgsb/blob/ce1a9322016d6f31b652393e000a914b63af6fef/test/driver1.f90) |
| [Load nlopt-box-quadratic](https://beliavsky.github.io/fortran-playground/fpm/?package=nlopt-f&example=gams-nlopt-box-quadratic) · [Source](../fpm_catalog/gams-drivers/nlopt-box-quadratic.f90) | G2h1a2 | [Procedure](https://github.com/awvwgk/nlopt-f/blob/83d21e7ebda9279a6dd4cc11fe6c735f48eb8689/src/nlopt_wrap.f90#L268) · Original public-API driver |
| [Load slsqp-circle-equality](https://beliavsky.github.io/fortran-playground/fpm/?package=slsqp&example=gams-slsqp-circle-equality) · [Source](../fpm_catalog/gams-drivers/slsqp-circle-equality.f90) | G2h3b1b | [Procedure](https://github.com/jacobwilliams/slsqp/blob/e28b14fc48189fd4fce5f359327164fca55b52be/src/slsqp_module.f90#L21) · [Author example](https://github.com/jacobwilliams/slsqp/blob/e28b14fc48189fd4fce5f359327164fca55b52be/test/slsqp_test.f90) |

The L-BFGS-B and SLSQP drivers adapt author API patterns and retain license notices. All three appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only each main and executable were rebuilt. The [verification report](gams-constrained-validation.json) records hashes, pins and saved output. Evaluation counts exclude derivative sanity checks and describe these simple cases, rather than establishing a general speed ranking.

### lbfgsb-box-quadratic

```text
Computed minimizer:     1.000000000000    0.000000000000
Independent objective (expected 2):     2.000000000000
Maximum bound violation:   0.0000E+00
Projected gradient residual:   0.0000E+00
Objective evaluations: 2
Gradient evaluations: 2
Solver termination: CONVERGENCE: NORM_OF_PROJECTED_GRADIENT_<=_PGTOL
PASS lbfgsb-box-quadratic
```

### nlopt-box-quadratic

```text
Computed minimizer:     1.000000000000    0.000000000000
Independent objective (expected 2):     2.000000000000
Maximum bound violation:   0.0000E+00
Projected gradient residual:   0.0000E+00
Objective evaluations: 3
Gradient evaluations: 3
Solver termination code: 1
PASS nlopt-box-quadratic
```

### slsqp-circle-equality

```text
Required accuracy for solution obtained
Computed minimizer:     1.000000000000   -0.000000000000
Independent objective (expected 2):     2.000000000000
Maximum primal constraint violation:   1.1102E-16
Stationarity with known multipliers (2,2):   4.4409E-16
Complementarity residual:   4.4409E-16
Objective/constraint callback calls: 8
Gradient/Jacobian callback calls: 8
Iterations: 8
Solver termination code: 0
PASS slsqp-circle-equality
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers lbfgsb-box-quadratic nlopt-box-quadratic slsqp-circle-equality
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
