# Checked Pareto-segment searches and Jacobi/DIIS systems

Both independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing package libraries were reused; only mains and executables compiled. The [verification report](gams-pareto-diis-validation.json) retains pins, source hashes, build commands and actual output. GAMS categories are not exhausted. Two failed initial probes are preserved with exact sources and full service results; neither failure is described as fixed.

## ddPCM Jacobi/DIIS linear systems (D2)

The consumer calls the cached external jacobi_diis routine directly, separately from the ordinary formaldehyde solvation demonstration. It manufactures strictly row-diagonally-dominant systems of sizes 3, 7 and 13. The symmetric pattern has off-diagonal a_ij=(modulo(i+j,5)-2)/16; the nonsymmetric pattern uses (modulo(3*i-2*j,7)-3)/16. Both use a_ii=2+i/4+2*sum_j(abs(offdiag_ij)), so the diagonal is positive and dominates the off-diagonal row sum.

Two prescribed solutions are x_i=(modulo(3*i,11)-5)/4 and x_i=1/(i+1). A separate scalar loop forms b=A*x_exact. Initial guesses are zero or the repeating pattern modulo(i,3)-1. Every combination runs in all four library convergence modes, both as plain Jacobi (history 0) and DIIS with the package default history 25. This gives 192 solves and 1,472 scalar solution references; 48 runs exercise the custom maximum-norm callback.

The matvec callback must supply only the off-diagonal matrix, because the implementation subtracts it from b before applying the inverse diagonal. The public comments call it a matrix-vector product, but supplying the entire A would implement the wrong splitting. Both callbacks must run; the custom norm must run only in mode 4. Convergence, iteration limit and finite solutions are checked. Every result must match x_exact within normalized error 2e-9 and satisfy an independently formed full-matrix residual within 2e-10. The solver uses tolerance 1e-11; this is an increment criterion, so the true residual is checked separately. Observed maxima were 2.29881e-11 and 6.57610e-11.

The first probe used history 4 and hit a GNU bounds error at makeb with index -5. Source review finds that diis removes ten entries whenever nmat reaches ndiis, so a small history makes nmat negative. The [retained probe](gams-candidates/ddpcm-diis-history/README.md) includes the exact main, normalized hash, package pin and full result. The published consumer uses the existing default history 25; it does not patch the library or claim to repair small histories. Arbitrary matrix conditioning, nonconvergence behavior, every history/eviction path, molecular coupling and forces remain outside this direct-solver check.

## VTMOP quadratic Pareto segment (G2)

The driver minimizes f1(x)=sum((x-a)**2) and f2(x)=sum((x-b)**2) on [0,1]^n. For n=2 and n=3, a_i=(i+1)/10 and b_i=1-a_i. The exact Pareto set is the segment p(t)=a+t*(b-a), 0<=t<=1. Orthogonal projection onto that segment cannot increase either objective. If the unclamped projection lies inside the segment, both objective improvements equal the squared distance from x to its projection. These formulas provide independent geometric references without another optimizer.

Two intrinsic RANDOM_SEED settings (1729 and 2903) are applied for each dimension. All four runs use the existing serial VTMOP/GPS/LSHEP setup, a 200-evaluation black-box budget, 40 maximum iterations, search budget 6, initial search budget 10 and local optimization budget 200. Both seed settings produced identical observed archives for each dimension. These are seeded repeats of two problem configurations, not four demonstrably independent stochastic searches or a reproducibility guarantee across compilers.

Every archive point must be finite and feasible, its two objectives must match independent scalar recomputation within 1e-12, and no other returned point may dominate it. The projection dominance and interior orthogonal-distance identities are checked within 1e-12. Distances to the exact Pareto segment are divided by its length. Each run must have at least five returned points within relative distance 0.05, and those near-front points must span at least 0.25 in clamped segment coordinate t. Best and worst full-archive distances are reported rather than hiding distant points.

There were 800 objective evaluations and 108 returned points. The two 2-D archives each had 32 points, 28 near-front points, maximum relative distance 0.128205 and near-front span 0.978158. The two 3-D archives each had 22 points, five near-front points, maximum relative distance 0.181848 and near-front span 0.970018. Thus 66 points met the near-front threshold, all four best distances were zero at printed precision, and the largest projection identity error was 3.03702e-16. This is a modest finite-budget approximation check, not a tight solution-accuracy or global convergence guarantee.

The first consumer required all archive points to have relative distance <=0.15. It passed both 2-D runs but failed on the first 3-D run. The [retained exact probe](gams-candidates/vtmop-archive-distance/README.md) documents that unsupported stronger assertion. The revised driver verifies a useful near-front subset and reports the full-archive maximum; it does not claim the failed all-point accuracy bound. Other objective families, dimensions, surrogate choices, parallel evaluation, checkpoint recovery and comparative performance remain unverified.

## Sources, licenses and actual output

Pinned solver interfaces, implementations and author examples were reviewed. The drivers are independently written MIT API consumers; upstream ddPCM LGPL and VTMOP MIT terms remain separate and unchanged. No upstream implementation or example bodies are copied. Loading a driver does not submit a job.

### ddpcm-jacobi-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=ddpcm&example=gams-ddpcm-jacobi-reference) / [Driver source](../fpm_catalog/gams-drivers/ddpcm-jacobi-reference.f90) / [Pinned procedure](https://github.com/filippolipparini/ddPCM/blob/36f22feb86c81c6ba1f59c373ef215368d3e3c13/cosmo.f90#L1) / [Author test](https://github.com/filippolipparini/ddPCM/blob/36f22feb86c81c6ba1f59c373ef215368d3e3c13/main.f90)

```text
Manufactured linear systems: 192; scalar solution references: 1472
Maximum normalized solution error and true residual:    2.29881E-11   6.57610E-11
Symmetric/nonsymmetric diagonal dominance; two guesses, four norm modes, Jacobi and DIIS(25).
Off-diagonal and inverse-diagonal callbacks checked; molecular coupling and forces unverified here.
PASS ddpcm-jacobi-reference
```

### vtmop-pareto-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=vtmop&example=gams-vtmop-pareto-reference) / [Driver source](../fpm_catalog/gams-drivers/vtmop-pareto-reference.f90) / [Pinned procedure](https://github.com/vtopt/VTMOP/blob/794a1de23801731ef6edd1924b52d69b679af6a0/src/vtmop.f90#L1) / [Author test](https://github.com/vtopt/VTMOP/blob/794a1de23801731ef6edd1924b52d69b679af6a0/src/samples.f90)

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
python xverify_gams_drivers.py --drivers ddpcm-jacobi-reference vtmop-pareto-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
