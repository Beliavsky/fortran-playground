# Checked matrix square roots and box-constrained quadratics

These D and G2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-matrix-roots-box-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Principal matrix functions: NTPoly (D)

Four positive square-root eigenvalue pairs [1,2], [1,3], [0.5,2] and [2,4] combine with three orthogonal factors: identity, a rotation with cosine/sine [0.6,0.8], and a 45-degree rotation. Both dimensions 2 and 3 are checked; the third dimension adds a decoupled root eigenvalue equal to the pair average. There are 24 symmetric positive-definite matrices and 48 function calls.

Independent scalar sums construct A=Q*diag(r*r)*transpose(Q), its principal root Q*diag(r)*transpose(Q), and its inverse root Q*diag(1/r)*transpose(Q). The package must reproduce both reference matrices with max-entry error divided by max(1,maxabs(reference)) at most 2e-8. Symmetry error must be at most 2e-9. Scalar loops independently check root*root=A, inverse_root*A*inverse_root=I and root*inverse_root=I. Maximum residual must be at most 5e-8; the first identity is normalized by max(1,maxabs(A)). All entries must be finite.

Exactly one MPI process with serialized thread support and a 1x1x1 process grid is used. Solver settings request converge_diff=1e-12, threshold=1e-14 and at most 200 iterations. The cached native MPI/OpenBLAS setup is reused. The author matrix example was reviewed for API usage; these fixtures are independently specified. Distributed scaling, large sparse behavior, complex/indefinite/singular matrices and the separate Invert/D2 API are not verified.

## Known interior box minima: serial QNSTOP (G2)

Four diagonal quadratics have positive weights and known minimizers inside [-2,2] in every coordinate. Three two-variable runs use center [0.25,-0.5] from distinct starts; a three-variable run uses [-0.5,0,0.75]. The objective is sum(weights*(x-center)**2), so the unique minimum is zero at the specified center. Each run seeds the pinned GNU intrinsic generator with its recorded fixed seed.

Mode G uses a 32-point sample design, at most 500 iterations, tau=1 and gain=10. Normal stopping status 1..3, positive evaluation count, finite results and strict box feasibility are required. Coordinates must be within 0.03 of the known minimizer, and the interior objective at most 1e-3. The returned objective must match an independent scalar sum within 1e-10*max(1,reference). These are fixed-seed accuracy smoke checks, not a global-optimum guarantee or a cross-compiler random-sequence guarantee.

Active-bound accuracy is not verified. A separate face-minimum probe returned normal iteration-limit status but missed the 0.03 coordinate tolerance, with error about 0.17212 at both 500 and 2000 iterations. Its sources and actual failed results are retained in the [candidate notes](gams-candidates/qnstop/README.md). The corner fixture in those probes was not reached. The public driver retains its original accuracy thresholds and separately verifies only the four interior fixtures. Noisy objectives, parallel QNSTOPP, active boundaries, all stopping/input modes and performance remain outside the checked scope. The author serial example was reviewed for interfaces; no upstream implementation or test code is copied.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### ntpoly-matrix-root-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=ntpoly&example=gams-ntpoly-matrix-root-reference) / [Driver source](../fpm_catalog/gams-drivers/ntpoly-matrix-root-reference.f90) / [Pinned procedure](https://github.com/william-dawson/NTPoly/blob/7b3d22f76226af1402e9b0a5be18a496e4addc28/Source/Fortran/SquareRootSolversModule.F90#L30) / [Author example/test](https://github.com/william-dawson/NTPoly/blob/7b3d22f76226af1402e9b0a5be18a496e4addc28/Examples/PremadeMatrix/main.f90)

```text
[1793457956.153449] [modal:39   :0]       tcp_iface.c:912  UCX  ERROR scandir(/sys/class/net) failed: No such file or directory
Dimension=2 pair=1 rotation=1 error=  2.2204E-16
Dimension=2 pair=1 rotation=2 error=  3.3307E-16
Dimension=2 pair=1 rotation=3 error=  5.5511E-16
Dimension=2 pair=2 rotation=1 error=  2.2204E-16
Dimension=2 pair=2 rotation=2 error=  3.8955E-16
Dimension=2 pair=2 rotation=3 error=  4.4409E-16
Dimension=2 pair=3 rotation=1 error=  1.1102E-16
Dimension=2 pair=3 rotation=2 error=  6.0834E-16
Dimension=2 pair=3 rotation=3 error=  5.3291E-16
Dimension=2 pair=4 rotation=1 error=  1.1102E-16
Dimension=2 pair=4 rotation=2 error=  1.6653E-16
Dimension=2 pair=4 rotation=3 error=  4.4409E-16
Dimension=3 pair=1 rotation=1 error=  2.2204E-16
Dimension=3 pair=1 rotation=2 error=  3.3307E-16
Dimension=3 pair=1 rotation=3 error=  5.5511E-16
Dimension=3 pair=2 rotation=1 error=  2.2204E-16
Dimension=3 pair=2 rotation=2 error=  3.8955E-16
Dimension=3 pair=2 rotation=3 error=  4.4409E-16
Dimension=3 pair=3 rotation=1 error=  1.1102E-16
Dimension=3 pair=3 rotation=2 error=  6.0834E-16
Dimension=3 pair=3 rotation=3 error=  5.3291E-16
Dimension=3 pair=4 rotation=1 error=  1.1102E-16
Dimension=3 pair=4 rotation=2 error=  2.7079E-16
Dimension=3 pair=4 rotation=3 error=  4.4409E-16
24 SPD fixtures, 48 matrix functions: known orthogonal factors and positive square-root eigenvalues.
Maximum normalized closed-form error:   6.0834E-16
Maximum independent product residual:   8.8818E-16
PASS ntpoly-matrix-root-reference
```

### qnstop-box-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=qnstop&example=gams-qnstop-box-reference) / [Driver source](../fpm_catalog/gams-drivers/qnstop-box-reference.f90) / [Pinned procedure](https://github.com/vtopt/qnstop/blob/39e8273247f586fca8305ef3d8e879b27b6512d0/src/qnstops.f95#L1) / [Author example/test](https://github.com/vtopt/qnstop/blob/39e8273247f586fca8305ef3d8e879b27b6512d0/src/sample_main_s.f95)

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers ntpoly-matrix-root-reference qnstop-box-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
