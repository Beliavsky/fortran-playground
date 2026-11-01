# Checked feasible directions and annealing; a failed friction fit

The G2h3b1b and G2i drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-directions-fitting-validation.json) retains pins, source hashes and complete output. GAMS categories are not exhausted.

## CONMIN nonlinear ball projections (G2h3b1b)

The independent driver minimizes f(x)=0.5*norm(x-target)**2 subject to g(x)=norm(x-center)**2-R**2<=0. The target is center+2*R*d for a unit direction d; the exact solution is center+R*d, with objective R**2/2 and multiplier 1/2 for the constraint g<=0. Strict convexity gives a unique global minimizer on this convex ball. Independent endpoint checks use these formulas, including the stationarity residual (x-target)+(x-center).

Dimensions [2,3,5], radii [0.5,2], zero/quarter-integer centers, two signed target directions and feasible/infeasible noncollinear starts give 48 problems and 160 coordinate references. Direction d normalizes entries (-1)**(direction*i)*i. A perpendicular unit vector q is obtained by normalizing e1-d(1)*d. Starts are center+R*(0.25*d+0.1*q) and center+R*(1.25*d+0.1*q), so the optimizer must correct a tangential error as well as the radial error.

NFDG=1 supplies both objective and constraint derivatives. Reverse communication services INFO=1 with values and INFO=2 with the objective gradient and active constraint Jacobian, stored by columns. The active set is provided through NAC/IC when g>=CT; the sphere is marked nonlinear. There were 426 user-gradient requests. Variable bounds and automatic scaling are disabled. The nonlinear constraint thickness starts at -0.01*R**2 and its minimum magnitude is 1e-9*R**2. Objective relative and absolute change settings are 1e-12.

The driver caps solver iterations at 300 and reverse-communication requests at 10,000. IGOTO=0 is required, with the iteration cap not reached, finite values and positive gradient-request counts. CONMIN exposes no separate success code here, so return alone is not an accuracy certificate. Independent normalized coordinate error must be <=2e-4, objective error <=2e-7, positive ball violation <=2e-7, stationarity residual <=2e-4 and returned/direct objective discrepancy <=1e-8. Normalizers are respectively 1+max(abs(x_star)), 1+R**2/2, 1+R**2, 1+2*R and 1+actual_f.

Saved maxima were 5.98188e-5, 1.16625e-8, 1.77636e-16, 7.41370e-5 and zero. Multiple simultaneous constraints, equality constraints, active variable bounds, nonconvex feasible sets and general optimizer robustness remain unverified.

## Simulated annealing shifted Rastrigin (G2i)

The driver searches R(x)=sum(z_i**2+A*(1-cos(2*pi*z_i))), with z=x-center, center=[-0.25,0] and bounds center +/- 3. Every summand is nonnegative, and only z=0 makes all quadratic terms zero; the unique global minimizer is center with objective zero. An independent sin-squared identity sum(z_i**2+2*A*sin(pi*z_i)**2) checks the returned value.

Two amplitudes [1,10] and seed pairs [(1,2),(1234,5678),(91,2718)] give six two-dimensional searches and 12 known minimizer coordinates. Seeds use the library generator, not Fortran random_seed. The start is center+[-2.5,2.5], initial steps are 1, temperature is 20 and the cooling factor is 0.9. Settings are ns=20, nt=10, neps=4, eps=1e-9, adaptive step mode 1, and n_resets=1. At this pin n_resets counts complete main-loop runs, not additional restarts. Known-minimum early stopping is disabled, so the reference answer does not steer termination.

Termination must return status 0; finite callback and final points must remain inside bounds. Each reported evaluation count must equal the independent callback count and be <=600,000. Independent objective must be <=1e-5, maximum coordinate error <=1e-3, and normalized returned-value discrepancy <=2e-12. Saved maxima were 2.80888e-12, 3.61574e-7 and 8.16990e-16; the six runs used 271,406 callbacks. These are fixture results, not a performance comparison.

A valid three-dimensional amplitude-10 search with seed (1,2) returned status 0 at objective approximately 0.994959, both with cooling factors 0.85 and 0.9. The [finite-schedule probes](gams-candidates/annealing-finite-budget/README.md) retain exact sources and results. That is a nonglobal finite-budget outcome, not evidence of a certified global solution or necessarily a library defect. The published driver covers only two dimensions and keeps all three original seed pairs and its original answer tolerances.

A separate [two-loop probe](gams-candidates/annealing-reset-objective/README.md) failed objective identity checks, consistent with repeated conversion of the internally negated minimization value. The checked driver uses one main-loop run; multi-loop correctness remains unverified. An earlier [zero-loop consumer](gams-candidates/annealing-loop-count/README.md) used an invalid configuration and is documented as a consumer error. No general global-convergence, success-probability or cross-compiler RNG guarantee follows from the six successes.

## Friction fitting remains unverified (L8)

The independent Coulomb probe generated exact signed-force data for coefficient 0.375 and varied positive normal loads. The identifiable scalar least-squares answer is sum(a_i*F_i)/sum(a_i**2), where a_i=sign(v_i)*N_i, giving exactly 0.375. The cached library instead fitted 0.7499999991182843 and reported residual convergence; independently recomputed force discrepancy reached 1.499999996473137. The unchanged 1e-7 coefficient comparison rejected it.

Source review finds fit_fcn subtracts observed force before returning callback values, while fmdl_fit also supplies observed force as the least-squares dependent data. The pinned fstats dependency expects model predictions, so this explains the observed doubling. The [preserved probe](gams-candidates/friction-double-subtraction/README.md) records the complete cached GNU 16 result, source hash, pins and source-based diagnosis. The L8 record has no checked driver, and no library patch or upstream-confirmed fix is claimed. Ordinary algebraic force evaluation remains separately demonstrated; dynamic internal-state fitting is not verified.

## Sources, licenses and actual output

Pinned APIs, implementations and author tests were reviewed before writing these independent consumers. No implementation or test bodies are copied. Drivers/probes have their own MIT notice; upstream CONMIN, simulated-annealing and friction licenses remain separate. Loading a driver does not submit a job.

### conmin-ball-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=conmin&example=gams-conmin-ball-reference) / [Driver source](../fpm_catalog/gams-drivers/conmin-ball-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/conmin/blob/201f3b29f023baf7bef13ad8f49b906ffb1c7757/src/conmin.F90#L46) / [Author test](https://github.com/jacobwilliams/conmin/blob/201f3b29f023baf7bef13ad8f49b906ffb1c7757/test/TP37.f90)

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

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=simulated-annealing&example=gams-annealing-rastrigin-reference) / [Driver source](../fpm_catalog/gams-drivers/annealing-rastrigin-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/simulated-annealing/blob/a2fa094d1ee39525c7e081cfd67866975e9e1dc5/src/simulated_annealing.F90#L59) / [Author test](https://github.com/jacobwilliams/simulated-annealing/blob/a2fa094d1ee39525c7e081cfd67866975e9e1dc5/test/test.f90)

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers conmin-ball-reference annealing-rastrigin-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
