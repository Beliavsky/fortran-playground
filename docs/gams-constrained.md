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
| [Load lbfgsb-box-quadratic](https://beliavsky.github.io/fortran-playground/fpm/?package=lbfgsb&example=gams-lbfgsb-box-quadratic) · [Source](../fpm_catalog/gams-drivers/lbfgsb-box-quadratic.f90) | G2h1a2 | [Procedure](https://github.com/jacobwilliams/lbfgsb/blob/ce1a9322016d6f31b652393e000a914b63af6fef/src/lbfgsb.f90#L88) · [Author example](https://github.com/jacobwilliams/lbfgsb/blob/ce1a9322016d6f31b652393e000a914b63af6fef/test/driver1.f90) · [Verification](gams-constrained-validation.json) |
| [Load nlopt-box-quadratic](https://beliavsky.github.io/fortran-playground/fpm/?package=nlopt-f&example=gams-nlopt-box-quadratic) · [Source](../fpm_catalog/gams-drivers/nlopt-box-quadratic.f90) | G2h1a2 | [Procedure](https://github.com/awvwgk/nlopt-f/blob/83d21e7ebda9279a6dd4cc11fe6c735f48eb8689/src/nlopt_wrap.f90#L268) · Original public-API driver · [Verification](gams-constrained-validation.json) |
| [Load slsqp-circle-equality](https://beliavsky.github.io/fortran-playground/fpm/?package=slsqp&example=gams-slsqp-circle-equality) · [Source](../fpm_catalog/gams-drivers/slsqp-circle-equality.f90) | G2h3b1b | [Procedure](https://github.com/jacobwilliams/slsqp/blob/e28b14fc48189fd4fce5f359327164fca55b52be/src/slsqp_module.f90#L21) · [Author example](https://github.com/jacobwilliams/slsqp/blob/e28b14fc48189fd4fce5f359327164fca55b52be/test/slsqp_test.f90) · [Verification](gams-constrained-validation.json) |
| [Load conmax-linear-program-certificate](https://beliavsky.github.io/fortran-playground/fpm/?package=conmax&example=gams-conmax-linear-program-certificate) · [Source](../fpm_catalog/gams-drivers/conmax-linear-program-certificate.f90) | G2a | [Procedure](https://github.com/jacobwilliams/conmax/blob/ab7f237d30f94f7d13b86997e0c49f3d67bd7c54/src/conmax.f90#L1912) · [Author example](https://github.com/jacobwilliams/conmax/blob/ab7f237d30f94f7d13b86997e0c49f3d67bd7c54/test/lp.f90) · [Verification](gams-constrained-validation.json) |
| [Load bobyqa-box-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=powellopt&example=gams-bobyqa-box-reference) · [Source](../fpm_catalog/gams-drivers/bobyqa-box-reference.f90) | G2h1a1 | [Procedure](https://github.com/jacobwilliams/PowellOpt/blob/0987cd09d695cec968a3d02c8230d4ce5af33533/src/bobyqa.f90#L77) · Original public-API driver · [Verification](gams-constrained-validation.json) |
| [Load pikaia-rastrigin-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=pikaia&example=gams-pikaia-rastrigin-reference) · [Source](../fpm_catalog/gams-drivers/pikaia-rastrigin-reference.f90) | G2i | [Procedure](https://github.com/jacobwilliams/pikaia/blob/c080c4004896243bf9b8bbb4577e402c9e31c5e3/src/pikaia_module.f90#L65) · [Author example](https://github.com/jacobwilliams/pikaia/blob/c080c4004896243bf9b8bbb4577e402c9e31c5e3/test/xpk2.f90) · [Verification](gams-constrained-validation.json) |
| [Load qnstop-box-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=qnstop&example=gams-qnstop-box-reference) · [Source](../fpm_catalog/gams-drivers/qnstop-box-reference.f90) | G2 | [Procedure](https://github.com/vtopt/qnstop/blob/39e8273247f586fca8305ef3d8e879b27b6512d0/src/qnstops.f95#L1) · [Author example](https://github.com/vtopt/qnstop/blob/39e8273247f586fca8305ef3d8e879b27b6512d0/src/sample_main_s.f95) · [Verification](gams-matrix-roots-box-validation.json) |
| [Load psqp-projection-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=psqp&example=gams-psqp-projection-reference) · [Source](../fpm_catalog/gams-drivers/psqp-projection-reference.f90) | G2h3b1b | [Procedure](https://github.com/jacobwilliams/psqp/blob/57a853e14e3806d69adad6d6d44396d9665d842e/src/psqp_module.f90#L62) · [Author example](https://github.com/jacobwilliams/psqp/blob/57a853e14e3806d69adad6d6d44396d9665d842e/test/tsqp.f90) · [Verification](gams-projection-lbfgs-validation.json) |
| [Load opti-rastrigin-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=opti&example=gams-opti-rastrigin-reference) · [Source](../fpm_catalog/gams-drivers/opti-rastrigin-reference.f90) | G2i | [Procedure](https://github.com/Konrad1991/opti/blob/6fb22db21bd2338e00690ff3706be61a1f101101/src/particle_swarm.f90#L57) · [Author example](https://github.com/Konrad1991/opti/blob/6fb22db21bd2338e00690ff3706be61a1f101101/test/check.f90) · [Verification](gams-gradient-swarm-validation.json) |
| [Load optgra-halfspace-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=optgra&example=gams-optgra-halfspace-reference) · [Source](../fpm_catalog/gams-drivers/optgra-halfspace-reference.f90) | G2h3b1b | [Procedure](https://github.com/jacobwilliams/optgra/blob/914bed713e80faa4a190e03beb3a8307077eb028/src/optgra.F90#L36) · [Author example](https://github.com/jacobwilliams/optgra/blob/914bed713e80faa4a190e03beb3a8307077eb028/test/optgra_test.f90) · [Verification](gams-projection-training-validation.json) |
| [Load conmin-ball-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=conmin&example=gams-conmin-ball-reference) · [Source](../fpm_catalog/gams-drivers/conmin-ball-reference.f90) | G2h3b1b | [Procedure](https://github.com/jacobwilliams/conmin/blob/201f3b29f023baf7bef13ad8f49b906ffb1c7757/src/conmin.F90#L46) · [Author example](https://github.com/jacobwilliams/conmin/blob/201f3b29f023baf7bef13ad8f49b906ffb1c7757/test/TP37.f90) · [Verification](gams-directions-fitting-validation.json) |
| [Load annealing-rastrigin-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=simulated-annealing&example=gams-annealing-rastrigin-reference) · [Source](../fpm_catalog/gams-drivers/annealing-rastrigin-reference.f90) | G2i | [Procedure](https://github.com/jacobwilliams/simulated-annealing/blob/a2fa094d1ee39525c7e081cfd67866975e9e1dc5/src/simulated_annealing.F90#L59) · [Author example](https://github.com/jacobwilliams/simulated-annealing/blob/a2fa094d1ee39525c7e081cfd67866975e9e1dc5/test/test.f90) · [Verification](gams-directions-fitting-validation.json) |
| [Load vtmop-pareto-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=vtmop&example=gams-vtmop-pareto-reference) · [Source](../fpm_catalog/gams-drivers/vtmop-pareto-reference.f90) | G2 | [Procedure](https://github.com/vtopt/VTMOP/blob/794a1de23801731ef6edd1924b52d69b679af6a0/src/vtmop.f90#L1) · [Author example](https://github.com/vtopt/VTMOP/blob/794a1de23801731ef6edd1924b52d69b679af6a0/src/samples.f90) · [Verification](gams-pareto-diis-validation.json) |

The L-BFGS-B and SLSQP drivers adapt author API patterns and retain license notices. All 13 appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All 13 passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only each main and executable were rebuilt. The per-driver reports linked above record hashes, pins and saved output; the [original report](gams-constrained-validation.json) covers its six initial drivers. Evaluation counts exclude derivative sanity checks and describe these simple cases, rather than establishing a general speed ranking.

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

### qnstop-box-reference

```text
Fixture=1 status=1 position error=  3.1203E-05 gap=  1.0836E-09
Fixture=2 status=1 position error=  1.1523E-04 gap=  1.5740E-08
Fixture=3 status=1 position error=  1.5896E-04 gap=  2.8910E-08
Fixture=4 status=1 position error=  7.3446E-04 gap=  1.0132E-06
Four seeded box-constrained quadratics with interior minima; active bounds are not verified.
Maximum coordinate error versus projected minimizer:   7.3446E-04
Maximum normalized objective gap:   1.0132E-06
PASS qnstop-box-reference
```

### psqp-projection-reference

```text
Ball-and-plane projection problems: 48
Analytic optimizer entries: 160
Maximum normalized optimizer error:   5.7909E-12
Maximum normalized objective error:   9.9295E-12
Maximum normalized constraint violation:   1.3172E-11
Maximum analytic-multiplier stationarity residual:   6.7059E-12
PASS psqp-projection-reference
```

The [dedicated review](gams-gradient-swarm.md) explains the seeded tests; the complete progress output remains in its verification report.

### opti-rastrigin-reference

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

### optgra-halfspace-reference

```text
Halfspace projections: 48; analytic coordinates: 160
Analytic derivative callbacks: 240
Max point, objective, feasibility, KKT, returned-value errors:    1.34283E-06   4.12945E-12   1.25825E-15   2.16013E-06   4.11316E-17
PASS optgra-halfspace-reference
```

### conmin-ball-reference

```text
Case:     2    1    0    1    0    9   1.093E-05   2.778E-10   4.441E-17   1.581E-05   0.000E+00
Case:     2    1    0    1    1   13   1.458E-05   4.946E-10   0.000E+00   2.110E-05   0.000E+00
Case:     2    1    0    2    0    9   1.094E-05   2.783E-10   0.000E+00   1.583E-05   0.000E+00
Case:     2    1    0    2    1   13   1.458E-05   4.945E-10   0.000E+00   2.110E-05   0.000E+00
Case:     2    1    1    1    0    9   1.080E-05   2.815E-10   0.000E+00   1.592E-05   0.000E+00
Case:     2    1    1    1    1   13   1.431E-05   4.944E-10   0.000E+00   2.109E-05   0.000E+00
Case:     2    1    1    2    0    9   1.919E-05   8.570E-10   0.000E+00   2.777E-05   0.000E+00
Case:     2    1    1    2    1   11   3.882E-08   3.503E-15   0.000E+00   5.618E-08   0.000E+00
Case:     2    2    0    1    0    9   2.268E-05   1.667E-09   1.776E-16   2.530E-05   0.000E+00
Case:     2    2    0    1    1   13   3.026E-05   2.967E-09   0.000E+00   3.376E-05   0.000E+00
Case:     2    2    0    2    0   10   2.270E-05   1.669E-09   1.776E-16   2.532E-05   0.000E+00
Case:     2    2    0    2    1   13   3.026E-05   2.967E-09   0.000E+00   3.375E-05   0.000E+00
Case:     2    2    1    1    0   10   2.270E-05   1.670E-09   0.000E+00   2.533E-05   0.000E+00
Case:     2    2    1    1    1   13   3.026E-05   2.967E-09   0.000E+00   3.375E-05   0.000E+00
Case:     2    2    1    2    0   10   2.269E-05   1.668E-09   0.000E+00   2.531E-05   0.000E+00
Case:     2    2    1    2    1   13   3.026E-05   2.967E-09   0.000E+00   3.375E-05   0.000E+00
Case:     3    1    0    1    0   10   1.216E-05   2.777E-10   0.000E+00   1.703E-05   0.000E+00
Case:     3    1    0    1    1   13   1.623E-05   4.947E-10   0.000E+00   2.273E-05   0.000E+00
Case:     3    1    0    2    0    9   1.216E-05   2.780E-10   4.441E-17   1.704E-05   0.000E+00
Case:     3    1    0    2    1   13   1.623E-05   4.946E-10   0.000E+00   2.273E-05   0.000E+00
Case:     3    1    1    1    0    9   1.211E-05   2.685E-10   0.000E+00   1.675E-05   0.000E+00
Case:     3    1    1    1    1   13   1.641E-05   4.934E-10   0.000E+00   2.270E-05   0.000E+00
Case:     3    1    1    2    0    9   1.032E-05   2.778E-10   0.000E+00   1.704E-05   0.000E+00
Case:     3    1    1    2    1   13   1.377E-05   4.946E-10   0.000E+00   2.273E-05   0.000E+00
Case:     3    2    0    1    0   10   2.617E-05   1.666E-09   0.000E+00   2.725E-05   0.000E+00
Case:     3    2    0    1    1   13   3.492E-05   2.967E-09   1.776E-16   3.637E-05   0.000E+00
Case:     3    2    0    2    0   10   2.619E-05   1.669E-09   1.776E-16   2.727E-05   0.000E+00
Case:     3    2    0    2    1   13   3.492E-05   2.967E-09   0.000E+00   3.637E-05   0.000E+00
Case:     3    2    1    1    0   10   2.896E-05   1.668E-09   1.776E-16   2.727E-05   0.000E+00
Case:     3    2    1    1    1   13   3.863E-05   2.968E-09   0.000E+00   3.637E-05   0.000E+00
Case:     3    2    1    2    0   10   2.389E-05   1.668E-09   0.000E+00   2.727E-05   0.000E+00
Case:     3    2    1    2    1   13   3.186E-05   2.967E-09   0.000E+00   3.637E-05   0.000E+00
Case:     5    1    0    1    0    7   3.465E-05   1.944E-09   0.000E+00   4.634E-05   0.000E+00
Case:     5    1    0    1    1   11   1.059E-06   1.814E-12   0.000E+00   1.416E-06   0.000E+00
Case:     5    1    0    2    0    7   3.465E-05   1.944E-09   0.000E+00   4.634E-05   0.000E+00
Case:     5    1    0    2    1   11   3.743E-06   2.268E-11   0.000E+00   5.005E-06   0.000E+00
Case:     5    1    1    1    0    9   9.838E-06   2.744E-10   0.000E+00   1.741E-05   0.000E+00
Case:     5    1    1    1    1   13   1.312E-05   4.879E-10   0.000E+00   2.322E-05   0.000E+00
Case:     5    1    1    2    0    9   8.397E-06   2.781E-10   0.000E+00   1.753E-05   0.000E+00
Case:     5    1    1    2    1   13   1.119E-05   4.942E-10   0.000E+00   2.336E-05   0.000E+00
Case:     5    2    0    1    0   10   2.984E-05   1.667E-09   0.000E+00   2.803E-05   0.000E+00
Case:     5    2    0    1    1   13   3.963E-05   2.941E-09   0.000E+00   3.723E-05   0.000E+00
Case:     5    2    0    2    0   10   2.985E-05   1.668E-09   0.000E+00   2.804E-05   0.000E+00
Case:     5    2    0    2    1   13   3.981E-05   2.967E-09   0.000E+00   3.739E-05   0.000E+00
Case:     5    2    1    1    0   10   2.728E-05   1.680E-09   0.000E+00   2.814E-05   0.000E+00
Case:     5    2    1    1    1   13   3.625E-05   2.966E-09   0.000E+00   3.739E-05   0.000E+00
Case:     5    2    1    2    0    8   5.982E-05   1.166E-08   0.000E+00   7.414E-05   0.000E+00
Case:     5    2    1    2    1   11   2.873E-08   2.665E-15   0.000E+00   3.561E-08   0.000E+00
Ball projections: 48; analytic coordinates: 160
User-gradient requests: 426
Max point, objective, feasibility, KKT, returned-objective errors:    5.98188E-05   1.16625E-08   1.77636E-16   7.41370E-05   0.00000E+00
PASS conmin-ball-reference
```

### annealing-rastrigin-reference

```text
Case dimension, amplitude, seed pair, objective/point/identity:         2        1        1        2   1.50725E-12   2.27304E-07   5.60958E-17
Case dimension, amplitude, seed pair, objective/point/identity:         2        1     1234     5678   2.80888E-12   3.61574E-07   2.64689E-17
Case dimension, amplitude, seed pair, objective/point/identity:         2        1       91     2718   6.50271E-13   1.74380E-07   7.81583E-17
Case dimension, amplitude, seed pair, objective/point/identity:         2       10        1        2   1.31118E-12   7.95924E-08   5.91253E-17
Case dimension, amplitude, seed pair, objective/point/identity:         2       10     1234     5678   6.55403E-14   1.30836E-08   8.16990E-16
Case dimension, amplitude, seed pair, objective/point/identity:         2       10       91     2718   2.19404E-12   1.03784E-07   2.80461E-16
Seeded annealing runs: 6; global minimizer coordinates: 12
Independently counted objective callbacks: 271406
Max independent objective, point error, objective identity error:    2.80888E-12   3.61574E-07   8.16990E-16
PASS annealing-rastrigin-reference
```

### vtmop-pareto-reference

```text
n=2 seed=1729 archive=32 best/worst relative distance and span:    0.000000   0.128205   0.978158
Near-front points: 28; their segment span:    0.978158
n=2 seed=2903 archive=32 best/worst relative distance and span:    0.000000   0.128205   0.978158
Near-front points: 28; their segment span:    0.978158
n=3 seed=1729 archive=22 best/worst relative distance and span:    0.000000   0.181848   0.970018
Near-front points: 5; their segment span:    0.970018
n=3 seed=2903 archive=22 best/worst relative distance and span:    0.000000   0.181848   0.970018
Near-front points: 5; their segment span:    0.970018
Seeded Pareto searches: 4; returned points checked: 108
Objective callback evaluations: 800
Returned points within relative distance 0.05: 66
Worst best-distance, worst all-point distance and minimum span:    0.00000E+00   1.81848E-01   9.70018E-01
Maximum Pareto projection identity error:    3.03702E-16
Near-front subset verified; the entire archive is not uniformly close to the exact Pareto set.
Fixed small quadratic searches only; not a general convergence guarantee.
PASS vtmop-pareto-reference
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
