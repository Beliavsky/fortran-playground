# Checked constrained projections and L-BFGS quadratics

These G2h3b1b and G1b1b drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-projection-lbfgs-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## PSQP ball-and-plane projection (G2h3b1b)

The consumer minimizes f(y)=0.5*sum((y-t)**2), y=x-center, subject to y(1)=h and sum(y**2)<=R**2. Analytic objective gradients and the full constraint Jacobian are supplied through callbacks; their call counts must be positive. This exercises a nonlinear inequality and an equality, with simple variable bounds disabled. The feasible set is convex and the quadratic objective strictly convex, so the analytic projection is the unique global minimizer for these fixtures.

Dimensions [2,3,5], radii [0.5,2], zero/translated centers, two signed target directions and feasible/infeasible ball starts give 48 problems and 160 optimizer-coordinate references. The plane height is h=R/4. Targets have t(1)=0.7*R and norm(t(2:))=2*R. Starts satisfy the plane and set the free coordinates to 0.25 or 1.25 times the target coordinates, putting them inside or outside the ball.

Let r=sqrt(R**2-h**2). The exact solution has y_star(1)=h and y_star(2:)=r*t(2:)/norm(t(2:)). Independent multipliers are mu=(norm(t(2:))/r-1)/2 and nu=t(1)-(1+2*mu)*h, with mu positive. They satisfy stationarity (1+2*mu)*y_star-t+nu*e1=0 for L=f-mu*(R**2-sum(y**2))+nu*(y(1)-h). The reference objective is evaluated directly at y_star.

Only convergence statuses 1 through 4 are accepted; iteration/evaluation limits and negative statuses fail. The callback and returned objective/gradient/constraint summaries must be finite. Coordinate error normalized by 1+max(abs(y_star)) must be <= 2e-5, objective error normalized by 1+f_star <= 5e-8, and the maximum normalized plane/ball violation <= 2e-7. The residual using the independent analytic multipliers, divided by 1+norm(t), must be <= 5e-5. Returned f must also agree with direct evaluation within normalized error 5e-8. Solver-reported residuals alone are not the acceptance test.

Saved maximum coordinate, objective, feasibility and stationarity errors are 5.7909e-12, 9.9295e-12, 1.3172e-11 and 6.7059e-12 respectively. These checks do not verify active variable bounds, nonconvex constraints, arbitrary equality manifolds or general global optimization.

## SEISCOPE L-BFGS SPD quadratics (G1b1b)

Dimensions [2,3,5], condition ratios [1,5,25], diagonal/rotated Hessians, scales [0.25,2] and three starts give 108 minimizations and 360 known minimizer entries. Diagonal cases are centered at zero; rotated cases use quarter-integer centers. Elementary adjacent-column rotations construct Q, and scalar sums form H=scale*Q*diag(lambda)*transpose(Q), with linearly spaced positive eigenvalues from 1 to the requested condition ratio.

The Hessian is rounded to the library callback precision and explicitly symmetrized there. With these small, well-conditioned matrices, rounding is far smaller than the smallest positive eigenvalue. The objective is 0.5*(x-center)^T*H*(x-center), with analytic gradient H*(x-center). Its unique minimizer is center, with zero objective and gradient. Default real is real32 in this GNU 16 image. Native callbacks use scalar loops; a separate real64 audit uses the actual rounded matrix coefficients and returned coordinates.

The optimizer uses memory length 10, iteration limit 1,000 and relative cost tolerance 1e-12. Reverse-communication requests are capped at 20,000 and only flags 1 through 4 are allowed; termination must be convergence flag 2, not line-search failure flag 4. Flag 1 recomputes the objective and gradient, while flag 3 continues with the accepted step. Every native callback result must be finite.

Independent endpoint checks require max(abs(x-center))/(1+max(abs(center))) <= 2e-3, absolute real64 objective divided by 1+initial_cost <= 2e-7, and maximum absolute real64 gradient divided by 1+norm_infinity(H) <= 2e-4. The normalized native-versus-real64 objective/gradient discrepancy must be <= 64*epsilon(real32). Saved maxima are 1.0656e-5 for coordinates, 9.1633e-13 for objective, 1.7733e-6 for gradient and 3.2135e-12 for the callback discrepancy.

The cached package already contains the guarded catalog edit replacing an uninitialized workspace-length argument l with optim%l in descent_LBFGS. This driver reuses that existing build and does not introduce another library patch. The exact edit and original source hash remain in [the package manifest](../fpm_catalog.json) under catalog_patches. Its upstream source link therefore documents the original revision, while the effective build includes the disclosed edit.

Nonquadratic or nonconvex objectives, constrained L-BFGS operation, other precisions, other SEISCOPE optimizer methods and performance remain unverified. A successful quadratic suite does not establish their convergence behavior.

## Sources, licenses and actual output

Pinned APIs/implementations and author tests were reviewed before writing these independent API consumers. The drivers have their own MIT notice; upstream PSQP and SEISCOPE license terms remain separate. No upstream test or implementation bodies are copied or relabeled. Loading a driver does not submit a job.

### psqp-projection-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=psqp&example=gams-psqp-projection-reference) / [Driver source](../fpm_catalog/gams-drivers/psqp-projection-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/psqp/blob/57a853e14e3806d69adad6d6d44396d9665d842e/src/psqp_module.f90#L62) / [Author test](https://github.com/jacobwilliams/psqp/blob/57a853e14e3806d69adad6d6d44396d9665d842e/test/tsqp.f90)

```text
Ball-and-plane projection problems: 48
Analytic optimizer entries: 160
Maximum normalized optimizer error:   5.7909E-12
Maximum normalized objective error:   9.9295E-12
Maximum normalized constraint violation:   1.3172E-11
Maximum analytic-multiplier stationarity residual:   6.7059E-12
PASS psqp-projection-reference
```

### seiscope-lbfgs-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=seiscope-optimization&example=gams-seiscope-lbfgs-reference) / [Driver source](../fpm_catalog/gams-drivers/seiscope-lbfgs-reference.f90) / [Pinned procedure](https://github.com/ofmla/seiscope_opt_toolbox_w_ctypes/blob/74a25c29d13c506e16f8025eb13a2cf396dc23c0/src/sotb/merged-LBFGS.f90#L213) / [Author test](https://github.com/ofmla/seiscope_opt_toolbox_w_ctypes/blob/74a25c29d13c506e16f8025eb13a2cf396dc23c0/app/LBFGS/test_LBFGS.f90)

```text
SPD quadratic minimizations: 108
Known minimizer entries: 360
Maximum normalized minimizer error:   1.0656E-05
Maximum initial-cost-scaled objective:   9.1633E-13
Maximum Hessian-scaled gradient:   1.7733E-06
Maximum independent real64 callback discrepancy:   3.2135E-12
PASS seiscope-lbfgs-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers psqp-projection-reference seiscope-lbfgs-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
