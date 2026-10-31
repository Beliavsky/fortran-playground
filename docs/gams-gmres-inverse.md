# Checked GMRES systems and SPD matrix inverses

These D2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-gmres-inverse-validation.json) retains pins, source hashes, actual output and native diagnostics. GAMS categories are not exhausted.

## LightKrylov real GMRES (D2)

The driver uses the real double-precision dense operator/vector implementation. Sizes [2,5,8,13] are combined with three matrix families: nonsymmetric strictly row-diagonally-dominant matrices, a nonsymmetric tridiagonal with upper entry 0.5 and lower entry -0.125, and the symmetric tridiagonal Poisson matrix with diagonal 2 and adjacent entries -1. These modest full-rank systems do not establish behavior on arbitrary matrix-free or sparse adapters.

Three exact solution vectors are ones, alternating signed i/8, and i*(n+1-i)/4. Scalar loops generate the right-hand side for either A*x or transpose(A)*x. Each system is solved from zero and from a deliberately incorrect constant -0.25 initial guess. Both a full n-vector Krylov dimension and a min(3,n)-vector dimension are selected with gmres_dp_opts; maxiter is set to 500. Requested RTol=1e-10 and ATol=1e-12 are identical across these configurations.

The cross product gives 288 solves and 2,016 known solution entries. Convergence metadata must be true and the information flag nonnegative; returned states must be allocated, correctly sized and finite. A negative iteration-count flag is rejected. There must actually be at least one solve with more than one outer cycle; the saved run contains 100 such solves. Exact initial guesses and zero right-hand sides are outside the verified scope.

The maximum abs(x-x_exact)/(1+abs(x_exact)) must not exceed 5e-8. Independently recomputed scalar true residuals must satisfy norm_inf(A_effective*x-b)/(norm_inf(A_effective)*norm_inf(x)+norm_inf(b)) <= 2e-10, where A_effective is A or its transpose. This uses the true matrix product rather than only the internal residual estimate or solver-to-solver agreement. Original operator data and right-hand sides must remain unchanged. Saved maxima are 5.3793e-9 for normalized solution error and 9.2868e-11 for scaled true residual.

Logging is reduced through the public logger_setup API, preserving solver error checks. The saved run still has two initialization messages and a Fortran runtime warning that an array temporary was created for DTRTRS. That warning did not prevent the run from returning zero and passing every answer check; bounds checks and native library code were unchanged. Preconditioners, custom matrix-free operators, complex/single precision, exact-start/zero-RHS behavior, singular systems, parallel operation and performance remain unverified.

## NTPoly Hotelling inversion with one MPI process (D2)

The driver uses InverseSolversModule:Invert, separate from the previously checked SquareRoot/InverseSquareRoot APIs. It initializes MPI with serialized thread support, requires MPI_SUCCESS and exactly one process, and uses the existing one-process process-grid and shared-memory/self-transport recipe. It does not test distributed scaling or multi-process correctness.

Sizes [2,3,5,8], prescribed spectral condition numbers [2,10,50], scales [1/4,4], and diagonal/rotated eigenbases give 48 real SPD inversions and 1,224 analytic inverse entries. The eigenvalues are scale*(1+(condition-1)*(i-1)/(n-1)). An identity eigenbasis is used directly or transformed by chained adjacent-plane rotations. Scalar sums form A=Q*diag(lambda)*transpose(Q), with independently known inverse Q*diag(1/lambda)*transpose(Q). No other inversion solver is used as the oracle.

Input matrices are filled through triplet lists; inverse and original matrices are gathered through separate lists, checking every returned index and rejecting nonfinite entries. Solver parameters are converge_diff=1e-12, threshold=1e-14, max_iterations=200 and be_verbose=false. Invert has no returned convergence-status argument here: the independent mathematical checks determine acceptance.

Each inverse entry must agree with its analytic value within abs(result-reference)/(1+abs(reference)) <= 5e-9. Separate scalar loops check every entry of A*inverse and inverse*A against identity, each with maximum absolute residual <= 5e-9. Normalized symmetry error must also be <= 5e-9. Gathering the original matrix after inversion must preserve it within 2e-12 relative maximum-entry error. Saved maxima are 3.4957e-14 for inverse entries, 1.7244e-14 for A*inverse, 9.7700e-15 for inverse*A and 3.3869e-15 for normalized symmetry.

The saved output includes a UCX discovery diagnostic: scandir(/sys/class/net) failed because the path is absent in the sandbox. MPI initialization/finalization nevertheless returned MPI_SUCCESS and the one-process run returned zero with all mathematical checks passing. This proof concerns that one-process configuration; the diagnostic is retained rather than hidden. Nonsymmetric/indefinite/singular matrices, complex inverses, load balancing, multi-process execution and performance remain unverified.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and author examples were reviewed without copying upstream code. Loading a link does not submit a job.

### lightkrylov-gmres-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=lightkrylov&example=gams-lightkrylov-gmres-reference) / [Driver source](../fpm_catalog/gams-drivers/lightkrylov-gmres-reference.f90) / [Pinned procedure](https://github.com/nekStab/LightKrylov/blob/849fa1d2f29c14d0181315e76e731bff7f0b2d08/src/IterativeSolvers/IterativeSolvers.f90#L379) / [Author test](https://github.com/nekStab/LightKrylov/blob/849fa1d2f29c14d0181315e76e731bff7f0b2d08/test/Tests.f90)

```text
2026-10-31 21:39:55.363: LightKrylov_Logger % comm_setup: Setup serial run
2026-10-31 21:39:55.363: LightKrylov_Logger % logger_setup: IO rank = 0
GMRES solves: 288
Known solution entries: 2016
Solves requiring multiple outer cycles: 100
Maximum normalized solution error:   5.3793E-09
Maximum scaled true residual:   9.2868E-11
PASS lightkrylov-gmres-reference
```

### ntpoly-inverse-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=ntpoly&example=gams-ntpoly-inverse-reference) / [Driver source](../fpm_catalog/gams-drivers/ntpoly-inverse-reference.f90) / [Pinned procedure](https://github.com/william-dawson/NTPoly/blob/7b3d22f76226af1402e9b0a5be18a496e4addc28/Source/Fortran/InverseSolversModule.F90#L29) / [Author test](https://github.com/william-dawson/NTPoly/blob/7b3d22f76226af1402e9b0a5be18a496e4addc28/Examples/PremadeMatrix/main.f90)

```text
[1793482797.721677] [modal:39   :0]       tcp_iface.c:912  UCX  ERROR scandir(/sys/class/net) failed: No such file or directory
SPD matrix inversions: 48
Analytic inverse entries: 1224
Maximum normalized inverse error:   3.4957E-14
Maximum left identity residual:   1.7244E-14
Maximum right identity residual:   9.7700E-15
Maximum normalized symmetry error:   3.3869E-15
PASS ntpoly-inverse-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers lightkrylov-gmres-reference ntpoly-inverse-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
