# Checked iterative least squares: LSQR and LSMR

Both D9a1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-iterative-ls-validation.json) retains source hashes, immutable revisions and actual output. GAMS categories are not exhausted.

## Shared mathematical fixtures

Each driver makes 216 vector solves across 72 fixtures. Matrix shapes are [1,1], [2,1], [3,2], [5,3], [2,3], [3,5]. Signed scales are -4, 0.5, 2; left/right orthogonal factors are identity or Householder reflections Q=I-2*v*vT/(vT*v), with v=[1,...,dimension]. Two residual settings and three right-hand sides are used. Some settings coincide for square/wide matrices; 72 counts fixtures, not distinct matrices.

With k=min(m,n), construct A=L(:,1:k)*diag(scale*[1,...,k])*R(:,1:k)T. For right-hand side c=1,2,3, set z_i=(2*i-c)/4 and x_reference=R(:,1:k)*z. Then b=A*x_reference+noise. Noise is zero except for 18 tall fixtures, where noise_c=0.25*c*L(:,n+1). Orthogonality makes the reference the unique tall least-squares solution and the wide minimum-norm solution. It also gives residual A*x-b=-noise and squared residual norm (0.25*c)**2 in those tall fixtures. References are constructed before invoking either solver, rather than obtained from another numerical solver. These are also the fixtures used in the [linalg least-squares review](gams-least-interpolation.md).

## Checks and interfaces

Every solution must be finite. Maximum coordinate error divided by max(1,maxabs(x_reference)) must be <=3e-12. Prescribed residual error is scaled by max(1,maxabs(b)) and must be <=5e-12. The normal-equation residual A^T*(A*x-b), scaled by max(1,maxabs(b))*max(1,maxabs(A)), must be <=1e-11. The known squared residual norm has normalized tolerance 1e-11. Matrices and right-hand sides must remain unchanged. Accepted stop codes are 0,1,2, alongside all accuracy checks; zero solutions occur explicitly. Iterations must be between 0 and 100.

LSQR uses lsqr_solver_ez with column-major coordinate triples, reinitializing the object for each solve. LSMR uses separate forward/transpose additive matrix-product callbacks and no local reorthogonalization. Both use zero damping, atol=btol=1e-12, conlim=1e8 and iteration limit 100. No library edits are made.

These small, full-rank fixtures check answers, not speed or large sparse scalability. Rank deficiency, severe ill conditioning, damping/regularization, error estimates, invalid inputs and performance remain unverified. Sibling procedures require their own class-specific evidence.

## Checked links and actual output

The independently written API consumers have their own MIT notice. Upstream terms remain separate. Pinned procedures and author tests were reviewed for the interfaces; no upstream code was copied. Loading a link does not submit a job.

### lsqr-least-squares-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=lsqr&example=gams-lsqr-least-squares-reference) / [Driver source](../fpm_catalog/gams-drivers/lsqr-least-squares-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/LSQR/blob/4df2ce600ca26a9f7e80dc01bfd0859d538547b3/src/lsqr.f90#L32) / [Author test](https://github.com/jacobwilliams/LSQR/blob/4df2ce600ca26a9f7e80dc01bfd0859d538547b3/test/lsqrtest_ez.f90)

```text
Full-rank least-squares fixtures: 72; solver calls: 216
Overdetermined fixtures with prescribed nonzero residuals: 18
Square/tall/wide; three vector RHS calls per fixture; zero damping.
Maximum normalized solution error:   3.3751E-15
Maximum normalized prescribed-residual error:   3.3159E-15
Maximum normalized normal-equation residual:   6.6218E-15
PASS lsqr-least-squares-reference
```

### lsmr-least-squares-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=lsmr&example=gams-lsmr-least-squares-reference) / [Driver source](../fpm_catalog/gams-drivers/lsmr-least-squares-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/LSMR/blob/12611e2299c5188441b097437695a66c85369e76/src/lsmrModule.f90#L175) / [Author test](https://github.com/jacobwilliams/LSMR/blob/12611e2299c5188441b097437695a66c85369e76/test/lsmrTestModule.f90)

```text
Full-rank least-squares fixtures: 72; solver calls: 216
Overdetermined fixtures with prescribed nonzero residuals: 18
Square/tall/wide; three vector RHS calls per fixture; zero damping.
Maximum normalized solution error:   3.0198E-15
Maximum normalized prescribed-residual error:   3.0790E-15
Maximum normalized normal-equation residual:   4.3964E-15
PASS lsmr-least-squares-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers lsqr-least-squares-reference lsmr-least-squares-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
