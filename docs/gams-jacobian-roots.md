# Checked Jacobian-based nonlinear least squares and scalar Newton methods

These G1b1b and F1b drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-jacobian-roots-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## User-Jacobian nonlinear fits: MINPACK lmder1 (G1b1b)

Twenty-four exact-data fits use five residuals f_i(a,b)=a*exp(b*t_i)-a0*exp(b0*t_i), with t=[-1,-0.5,0,0.5,1]. Known amplitudes a0=0.5 or 2, exponents b0=-1,0.25,1 and four starting combinations a/a0=0.5 or 1.5, b-b0=-0.5 or 0.5 give the 24 cases. The supplied residual-Jacobian columns are exp(b*t_i) and a*t_i*exp(b*t_i). The unique exact solution is [a0,b0]; it yields zero residual and hence a global least-squares minimum.

Sixteen nonzero-residual fits use f_i(a,b)=exp(a)-2+t_i*(b**3-1)+rho*q_i, with t=[-2,-1,0,1,2] and q=[1,-2,2,-2,1]. The q vector is orthogonal to both the constant and t vectors, whose squared norms are 5 and 10; norm(q)**2=14. Consequently the exact squared objective is 5*(exp(a)-2)**2+10*(b**3-1)**2+14*rho**2. Its unique global minimizer is [log(2),1], with minimum 14*rho**2. Four rho values [-0.5,-0.125,0.125,0.5] and starts a=log(2)+/-0.7, b=0.5 or 1.5 give 16 fits. Starting at the flat b=0 stationary point is outside this checked scope.

Before each fit, both analytical Jacobian columns are checked by central differences with step 1e-5*max(1,abs(start_parameter)). Maximum entry discrepancy in a column divided by max(1,maxabs(analytical_column)) must be at most 2e-7: 400 entries across 40 starting points. This independently checks the user-supplied derivatives before testing lmder1. The solver receives tolerance 1e-12 and correctly sized real/integer work arrays; both residual iflag=1 and Jacobian iflag=2 callbacks must actually be used.

Acceptance requires normal stopping info in 1..4, finite parameters and residuals, and maximum parameter error divided by max(1,maxabs(expected_parameters)) at most 2e-7. Recomputed and returned residuals must agree within 1e-11. Squared residual norm must equal the known minimum with error divided by max(1,minimum) at most 1e-10. Maximum absolute component of transpose(J)*f must be at most 1e-6. Exact-data fits must additionally have maximum absolute residual at most 1e-8. G1b1b here describes nonlinear least squares with user residual Jacobians; the interface does not accept a general scalar-objective gradient. These fixtures establish successful solutions at the recorded starts, not a global convergence guarantee. Rank deficiency, arbitrary data noise, malformed inputs, every stopping mode and performance remain unverified.

## Three Newton configurations with prescribed roots: forsolver (F1b)

Ninety-six fixtures combine three functions of u=x-center, four prescribed roots center=[-2,0,0.5,3], scales [0.5,2] and starting offsets [-2,-0.5,0.5,2]. The functions are scale*(u+u**3), scale*(exp(u)-1), and scale*(u+0.25*sin(u)). Each has exactly one real root, u=0: its derivative is strictly positive everywhere. Analytic derivatives are scale*(1+3*u*u), scale*exp(u), and scale*(1+0.25*cos(u)). Real and complex callbacks implement the same analytic expressions.

Each fixture is solved using analytic-derivative Newton, central-finite-difference Newton with step setting 1e-6, and complex-step Newton with setting 1e-20: 288 solves. All use maxit=100, TolFun=1e-12 and verbosity=0. Callback counters must show the required real/derivative or complex evaluation occurred. The complex root must have finite real and imaginary parts and imaginary magnitude at most 1e-12.

Every real root must be finite and agree with the prescribed center within error divided by max(1,abs(center)) of 1e-9. Its residual divided by max(1,abs(scale)) must be at most 1e-10. The three methods must agree within normalized spread 1e-9. Agreement alone is insufficient: all methods independently face the known-root and residual tests. The invoked API has no returned convergence-status value, so these are answer-based checks. Vector systems, arbitrary complex roots, derivative singularities, failure recovery, global convergence and performance remain outside the verified scope.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream terms remain separate. Author sources were reviewed for interfaces, and no upstream implementation or example code is copied. Loading a link does not submit a job.

### minpack-lmder-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=minpack&example=gams-minpack-lmder-reference) / [Driver source](../fpm_catalog/gams-drivers/minpack-lmder-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/src/minpack.f90#L1846) / [Author example/test](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/examples/example_lmder1.f90)

```text
Total / exact-fit / nonzero-residual fits:    40   24   16
Analytical Jacobian entries checked by central differences at starting points: 400
Maximum normalized parameter error:   5.9266E-11
Maximum normalized Jacobian finite-difference error:   1.3978E-10
Maximum absolute J-transpose-residual component:   1.1853E-09
PASS minpack-lmder-reference
```

### forsolver-newton-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forsolver&example=gams-forsolver-newton-reference) / [Driver source](../fpm_catalog/gams-drivers/forsolver-newton-reference.f90) / [Pinned procedure](https://github.com/gha3mi/forsolver/blob/6c0644b287cb49a7310d883415b9b9ba581d51c5/src/forsolver.f90#L15) / [Author example/test](https://github.com/gha3mi/forsolver/blob/6c0644b287cb49a7310d883415b9b9ba581d51c5/test/test_solver3.f90)

```text
Unique-root fixtures: 96; three-method solves: 288
Analytic Newton, central finite differences and complex step; all roots independently prescribed.
Maximum normalized root error:   2.0894E-13
Maximum normalized residual:   2.1405E-13
Maximum normalized inter-method spread:   3.3307E-15
PASS forsolver-newton-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers minpack-lmder-reference forsolver-newton-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
