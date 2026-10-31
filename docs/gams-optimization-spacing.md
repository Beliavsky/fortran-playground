# Checked derivative-free optimization and deterministic spacing

These G1b and R drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-optimization-spacing-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Known unconstrained minima: ForTimize Nelder-Mead (G1b)

Three coupled positive-definite quadratic problems use dimensions 2,3,5. For errors e=x-center, the objective is `sum(i*mixed(i)**2)`, where mixed(i)=e(i)+0.25*e(i+1), except for the final component e(n). The upper-bidiagonal transformation is invertible, so the unique minimizer is the specified center and the objective there is zero. Alternating signed half-integer centers and three displaced starting points per dimension give nine solves.

Three further solves minimize `(1-x1)**2+100*(x2-x1*x1)**2`, starting at [-1.2,1], [0,0] and [2,2]. Its unique zero is [1,1]. All twelve results must be finite, within coordinate error 2e-4 of the known minimizer, and have objective in [0,1e-8]. A scalar recomputation of the objective must agree with the returned value within 1e-12. The callback rejects any derivative request, verifying that this configuration is derivative-free.

The initial simplex step is 0.4, convergence_tolerance is 1e-20, konvge is 20 and the actual function-evaluation limit kcount is 50000. The pinned wrapper does not expose its underlying termination status and does not use max_iters to bound this Nelder-Mead call; acceptance therefore depends on the independently checked result, not a success flag. The author example was reviewed for API usage; the driver and objectives are independently written. Upstream licensing remains separate from the driver notice.

Other optimizer methods, nonsmooth/global problems, scaling extremes, all failure paths and performance are not verified. The implementation uses module-level callback/data pointers, so this serial driver does not verify concurrent independent optimizations. Its success does not verify the separate GradientDescent procedure record.

## Arithmetic and geometric grids: pointsets (R)

Array lengths [2,3,5,9,17] and endpoint pairs [0,1], [-2,3], [3,-2] and [1,1] give 20 arithmetic grids. Geometric spacing uses the same fixtures with ratios [0.5,0.75,1.25,2], giving 80 further grids. Closed-form real64 references are `a+(b-a)*i/(n-1)` and `a+(b-a)*(q**i-1)/(q**(n-1)-1)`, i=0..n-1. These do not repeat the package accumulation algorithm.

The pinned package selects wp=real32. Reference inputs are promoted from that working kind, and maximum coordinate error divided by max(1,abs(a),abs(b)) must stay within 32 working-kind epsilons. Both endpoints are checked separately. Increasing/decreasing grids must be strictly ordered; equal endpoints must produce a constant array. The reported maximum error retains the precision distinction.

Seven guarded calls verify unchanged-array behavior: empty and singleton arrays for each routine, and geometric ratios -1,0,1 on a five-element sentinel array. In particular, ratio 1 does not fill a uniform grid at this pin; use arithmetic_spacing for that purpose. The author pointset tests were reviewed for usage. Random point generators, large arrays, extreme ratios, ratios approaching one and other pointset routines are outside this deterministic service example.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### fortimize-nelder-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortimize&example=gams-fortimize-nelder-reference) / [Driver source](../fpm_catalog/gams-drivers/fortimize-nelder-reference.f90) / [Pinned procedure](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/src/minimize.f90#L7) / [Author example/test](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/example/gradient.f90)

```text
Variables=2 Rosenbrock=F coordinate error=  1.0398E-07
Variables=2 Rosenbrock=F coordinate error=  7.7813E-09
Variables=2 Rosenbrock=F coordinate error=  3.5760E-07
Variables=3 Rosenbrock=F coordinate error=  1.6225E-07
Variables=3 Rosenbrock=F coordinate error=  1.2630E-06
Variables=3 Rosenbrock=F coordinate error=  2.6251E-07
Variables=5 Rosenbrock=F coordinate error=  2.0231E-06
Variables=5 Rosenbrock=F coordinate error=  6.3183E-06
Variables=5 Rosenbrock=F coordinate error=  1.4186E-06
Variables=2 Rosenbrock=T coordinate error=  1.0168E-06
Variables=2 Rosenbrock=T coordinate error=  3.1978E-08
Variables=2 Rosenbrock=T coordinate error=  6.4622E-06
12 derivative-free solves: coupled quadratics in 2/3/5 variables and Rosenbrock, three starts each.
Maximum coordinate error versus known minimizer:   6.4622E-06
Maximum returned objective:   3.9378E-11
PASS fortimize-nelder-reference
```

### pointsets-spacing-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=pointsets&example=gams-pointsets-spacing-reference) / [Driver source](../fpm_catalog/gams-drivers/pointsets-spacing-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/pointsets/blob/a1c381777f893d656018366cfabfa4cc7531e4dd/src/pointsets.f90#L26) / [Author example/test](https://github.com/arjenmarkus/pointsets/blob/a1c381777f893d656018366cfabfa4cc7531e4dd/test/pointsets/test_pointsets.f90)

```text
Working precision decimal digits: 6
20 arithmetic and 80 geometric grids; increasing, decreasing and equal endpoints.
Maximum normalized error versus real64 formulas:   1.4845E-07
Acceptance tolerance, 32 working-kind epsilons:   3.8147E-06
Seven empty/singleton/ratio guards checked as unchanged-array behavior.
PASS pointsets-spacing-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fortimize-nelder-reference pointsets-spacing-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
