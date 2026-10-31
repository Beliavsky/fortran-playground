# Checked GAMS constrained-optimization drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [G2h1a2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2h1a2) | Smooth simple-bound optimization with user first derivatives | L-BFGS-B `setulb`; NLopt `LD_LBFGS` with explicit bounds |
| [G2h3b1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2h3b1b) | Smooth nonlinear equality/inequality optimization with user objective and constraint first derivatives | SLSQP `slsqp_solver%optimize`, analytic mode |
| [G2a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2a) | Free-variable inequality-constrained linear programming | CONMAX `slnpro` |
| [G2h1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2h1a1) | Simple bounds, no derivatives supplied | PowellOpt `bobyqa` |
| [G2i](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G2i) | Bounded global search for a nonconvex problem | PIKAIA `pikaia_class%solve` |

Each driver demonstrates its recorded configuration. Other constrained optimization classes and other procedures in these classes still need checked drivers; see the [coverage report](gams-coverage.md).

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

## Linear programming with an optimality certificate

Three CONMAX problems maximize `-y` subject to `x+y>=a`, `x-y<=b`, with `(a,b)=[(2,4),(5,1),(-3,7)]`. Variables are free, so negative solution components are permitted. The exact solutions are `[(3,-1),(3,2),(2,-5)]`. The inequality rows are multiplied by positive scale pairs `[(1,1),(0.5,3),(4,0.25)]` without changing their feasible sets.

For inequality matrix A, right side d and scales s1,s2, the nonnegative dual weights `lambda=[1/(2*s1),1/(2*s2)]` satisfy `transpose(A)*lambda=[0,-1]`. Their bound `dot_product(lambda,d)=(b-a)/2` is an independent upper bound on the maximized objective. The driver requires status 0, finite parameters/reported objective, solution error and feasibility violation at most `1e-9`, reported objective agreement and primal-dual gap at most `1e-9`. Original constraints are preserved because the solver overwrites its tableau. Infeasible/unbounded problems and general LP robustness are not tested.

## Derivative-free box quadratic

BOBYQA solves the same quadratic and box used by the derivative-based drivers, from `[0.25,1]`, `[0.9,0.1]` and `[0.1,1.8]`. No gradient is supplied to the optimizer. Five interpolation points, initial/final radii `0.1`/`1e-9`, and a maximum of 1000 objective calls are used. Every callback checks finite parameters and bound feasibility. After solving, the driver independently checks solution `[1,0]`, objective 2 and the projected-gradient residual, all within `1e-8`.

The pinned BOBYQA API has no returned status flag. A normal return is insufficient: explicit answer checks must pass and the evaluation budget must not be exhausted. The reference gradient is used only after the solve. These convex cases do not verify arbitrary nonconvex objectives.

## Seeded multimodal global search

PIKAIA minimizes the two-dimensional Rastrigin objective `R(x)=sum(x_i^2+10*(1-cos(2*pi*x_i)))` on `[-2,2]^2` by maximizing `fitness=1/(1+R)`. Every term in R is nonnegative; the exact global minimum is zero at `[0,0]`, giving fitness 1. Three runs use seeds `[12345,6789,24680]`, population 100, 600 generations and seven decimal encoding digits. The convergence window is 601, longer than the generation budget, so a short plateau does not stop the test early.

Initialization/solve status must be zero, callback/final points finite and within bounds, maximum parameter error at most `0.01`, objective at most `0.01` and reported fitness within `1e-10` of an independently recomputed value. Callback counts are printed. Fixed-seed finite-budget success does not guarantee global convergence or certify arbitrary nonconvex problems. No general global-optimality claim follows from solver status.

## Sources and playground links

| Driver | Class | Pinned procedure and author example |
| --- | --- | --- |
| [Load lbfgsb-box-quadratic](https://beliavsky.github.io/fortran-playground/fpm/?package=lbfgsb&example=gams-lbfgsb-box-quadratic) · [Source](../fpm_catalog/gams-drivers/lbfgsb-box-quadratic.f90) | G2h1a2 | [Procedure](https://github.com/jacobwilliams/lbfgsb/blob/ce1a9322016d6f31b652393e000a914b63af6fef/src/lbfgsb.f90#L88) · [Author example](https://github.com/jacobwilliams/lbfgsb/blob/ce1a9322016d6f31b652393e000a914b63af6fef/test/driver1.f90) |
| [Load nlopt-box-quadratic](https://beliavsky.github.io/fortran-playground/fpm/?package=nlopt-f&example=gams-nlopt-box-quadratic) · [Source](../fpm_catalog/gams-drivers/nlopt-box-quadratic.f90) | G2h1a2 | [Procedure](https://github.com/awvwgk/nlopt-f/blob/83d21e7ebda9279a6dd4cc11fe6c735f48eb8689/src/nlopt_wrap.f90#L268) · Original public-API driver |
| [Load slsqp-circle-equality](https://beliavsky.github.io/fortran-playground/fpm/?package=slsqp&example=gams-slsqp-circle-equality) · [Source](../fpm_catalog/gams-drivers/slsqp-circle-equality.f90) | G2h3b1b | [Procedure](https://github.com/jacobwilliams/slsqp/blob/e28b14fc48189fd4fce5f359327164fca55b52be/src/slsqp_module.f90#L21) · [Author example](https://github.com/jacobwilliams/slsqp/blob/e28b14fc48189fd4fce5f359327164fca55b52be/test/slsqp_test.f90) |
| [Load conmax-linear-program-certificate](https://beliavsky.github.io/fortran-playground/fpm/?package=conmax&example=gams-conmax-linear-program-certificate) · [Source](../fpm_catalog/gams-drivers/conmax-linear-program-certificate.f90) | G2a | [Procedure](https://github.com/jacobwilliams/conmax/blob/ab7f237d30f94f7d13b86997e0c49f3d67bd7c54/src/conmax.f90#L1912) · [Author example](https://github.com/jacobwilliams/conmax/blob/ab7f237d30f94f7d13b86997e0c49f3d67bd7c54/test/lp.f90) |
| [Load bobyqa-box-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=powellopt&example=gams-bobyqa-box-reference) · [Source](../fpm_catalog/gams-drivers/bobyqa-box-reference.f90) | G2h1a1 | [Procedure](https://github.com/jacobwilliams/PowellOpt/blob/0987cd09d695cec968a3d02c8230d4ce5af33533/src/bobyqa.f90#L77) · Original public-API driver |
| [Load pikaia-rastrigin-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=pikaia&example=gams-pikaia-rastrigin-reference) · [Source](../fpm_catalog/gams-drivers/pikaia-rastrigin-reference.f90) | G2i | [Procedure](https://github.com/jacobwilliams/pikaia/blob/c080c4004896243bf9b8bbb4577e402c9e31c5e3/src/pikaia_module.f90#L65) · [Author example](https://github.com/jacobwilliams/pikaia/blob/c080c4004896243bf9b8bbb4577e402c9e31c5e3/test/xpk2.f90) |

The L-BFGS-B and SLSQP drivers adapt author API patterns and retain license notices. All 6 appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All 6 passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only each main and executable were rebuilt. The [verification report](gams-constrained-validation.json) records hashes, pins and saved output. Evaluation counts exclude derivative sanity checks and describe these simple cases, rather than establishing a general speed ranking.

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

### conmax-linear-program-certificate

```text
Case 1: x,y=    3.000000   -1.000000; maximum -y=    1.000000; certificate gap=   0.000E+00
Case 2: x,y=    3.000000    2.000000; maximum -y=   -2.000000; certificate gap=   0.000E+00
Case 3: x,y=    2.000000   -5.000000; maximum -y=    5.000000; certificate gap=   0.000E+00
Free variables, mixed-sign optima and rescaled inequalities checked.
PASS conmax-linear-program-certificate
```

### bobyqa-box-reference

```text
Start 1: solution=   1.000000000   0.000000000; f=   2.000000000; evaluations=30
Start 2: solution=   1.000000000   0.000000000; f=   2.000000000; evaluations=26
Start 3: solution=   1.000000000   0.000000000; f=   2.000000000; evaluations=32
No objective derivatives supplied; reference gradient is used only after solving.
This API has no returned status flag; checked answers and budget use determine acceptance.
PASS bobyqa-box-reference
```

### pikaia-rastrigin-reference

```text
Seed 12345: x=  -0.000000400  -0.000000400; objective=   6.349E-11; evaluations=60691
Seed 6789: x=  -0.000000400  -0.000000400; objective=   6.349E-11; evaluations=60691
Seed 24680: x=  -0.000000400   0.000000000; objective=   3.174E-11; evaluations=60691
These fixed-seed finite searches do not guarantee global convergence on other problems.
PASS pikaia-rastrigin-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers lbfgsb-box-quadratic nlopt-box-quadratic slsqp-circle-equality
python xverify_gams_drivers.py --drivers conmax-linear-program-certificate bobyqa-box-reference pikaia-rastrigin-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
