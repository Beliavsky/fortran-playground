# Ten checked stdlib linear-system and spectral drivers

Ten independent drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing stdlib libraries were reused; only mains and executables were compiled. The [verification report](gams-systems-spectra-ten-validation.json) saves normalized source hashes, package pins, timings and full output. GAMS categories are not exhausted.

## Direct SPD solves (D2b1b)

Two drivers construct 72 SPD matrices each, orders 2..10, from known dyadic positive-diagonal lower factors L. The matrices are A=L*transpose(L). Three prescribed solution vectors generate right-hand sides by scalar loops. Both triangle choices and vector/three-RHS matrix interfaces give 288 solve calls per driver. One driver calls solve_chol to factor and solve; the other calls solve_lower_chol/solve_upper_chol with independently constructed factors, without using a package factorization as its oracle. Both check finite solutions, prescribed values, original-matrix residuals, status and input preservation, with scaled tolerance 3e-12. Invalid SPD inputs, complex values, overwriting and general conditioning are not covered.

## Equality-constrained and weighted least squares

The D9b1 driver has 96 full-rank 6x3 fits with one equality constraint. Before a shear change of coordinates, the objective Hessian is diagonal H and the unconstrained minimizer is u. For constraint c*x=d, the independent answer is u-H**(-1)*c*lambda, with lambda=(c*u-d)/(c*H**(-1)*c). Applying the explicit inverse shear gives the reference in mixed coordinates. The residual is generally nonzero. The driver checks the solution, equality feasibility, Lagrange stationarity, status, finiteness and input preservation at scaled tolerance 5e-12. Multiple constraints and deficient ranks are not claimed.

The D9a1 driver has 96 weighted line fits with 4..15 observations and nonuniform positive weights with ratio at most 16. Scalar sums sw, sx, sxx, sy and sxy give intercept/slope through an explicit two-by-two determinant. This independent formula and the weighted normal residuals are checked at tolerance 5e-12. Non-exact quadratic/noisy data prevent a merely interpolating fit. Zero/negative weights, rank deficiency and extreme weight ratios remain unverified.

## Ordinary eigenproblems, Schur form and generalized eigenvalues

Each spectral driver has 64 real 3x3 problems obtained by explicit shear similarities of a planar rotation block and a distinct real eigenvalue. The analytic spectrum has one conjugate pair alpha +/- i*beta and one real value r. Each driver matches all 192 eigenvalues without assuming output order at absolute tolerance 8e-12. Ordinary eig also checks both left/right eigenvector equations and Euclidean unit norms. Real schur checks orthogonal Z, reconstruction A=Z*T*transpose(Z) and nonoverlapping quasi-triangular blocks. Schur vectors are not individual eigenvectors.

The generalized D4b2 driver forms B=S*diag(1,2,4)*inverse(S) and A=B*S*T*inverse(S), giving the same analytic eigenvalues for an invertible nonsymmetric B. Only the eigenvalue-only interface is verified. Singular pencils, defective/repeated spectra, complex input and other sizes remain unverified.

The initial generalized-vector consumer incorrectly required Euclidean unit norms; GGEV uses max(abs(real(v))+abs(imag(v)))=1. Correcting that consumer exposed a second failure: complex eigenvalues were returned with real-only vectors and right residual about 0.322. The nearly conjugate scaled eigenvalues fail an exact equality comparison used by the pinned vector reconstruction routine. That is a likely cause, not a patched fix. The [exact sources and full failures](gams-candidates/stdlib-systems/README.md) are retained. The checked eigenvalue-only result does not promote returned generalized eigenvectors.

## Iterative public kernels

CG, Jacobi PCG and unpreconditioned BiCGSTAB each solve 102 manufactured dense systems, orders 2..18, with six solution families and nonzero initial guess 0.125. Matrix-vector products and preconditioners are ordinary module procedures; callers own and initialize the workspaces. Right-hand sides and final residuals are independently recomputed with scalar loops.

CG uses symmetric strictly diagonally-dominant SPD matrices; PCG applies positive diagonal congruence factors spanning 0.1..10 and an explicit inverse diagonal preconditioner. Both request rtol=1e-12 and check solution/residual errors at 2e-9. BiCGSTAB uses nonsymmetric strictly diagonally-dominant matrices, requests rtol=1e-10 and checks errors at 5e-8. These bounded results do not certify all requested tolerances, breakdown recovery or arbitrary ill-conditioning. Sparse convenience interfaces, boundary masks, zero RHS and performance remain unverified.

The dense convenience wrappers for all three methods compiled but segfaulted in this hosted configuration. Their exact probes are retained in the same [candidate notes](gams-candidates/stdlib-systems/README.md). The wrappers use internal procedure callbacks; the crash cause has not been established. Only the public kernels with module-level callbacks are demonstrated here; their success does not verify those failed wrappers. No upstream numerical source was patched.

## Classification and provenance

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies D2b1b (real SPD), D2a1 (general real nonsymmetric), D9a1 (unconstrained least squares), D9b1 (constrained least squares), D4a2 (ordinary real nonsymmetric eigenproblems) and D4b2 (real general pencils). The dense iterative examples do not claim sparse interfaces. These are independent MIT consumers. Pinned public APIs, implementations and author tests were reviewed; implementation/test bodies were not copied. Loading an example does not submit a job.

### stdlib-spd-solve-reference (D2b1b)

Independent API consumer; pinned sources and author tests reviewed. 72 REAL64 SPD matrices of orders 2..10 formed from dyadic positive-diagonal triangular factors. Both triangle choices and vector/three-RHS matrix interfaces: 288 solves per driver. Three prescribed solution families, scalar-loop right-hand sides, original-matrix residuals, finite results and input preservation; scaled tolerance 3e-12. solve_chol factors the full matrix internally. Indefinite errors, complex values, overwriting, arbitrary conditioning and speed unverified.

### stdlib-factored-spd-solve-reference (D2b1b)

Independent API consumer; pinned sources and author tests reviewed. 72 REAL64 SPD matrices of orders 2..10 formed from dyadic positive-diagonal triangular factors. Both triangle choices and vector/three-RHS matrix interfaces: 288 solves per driver. Three prescribed solution families, scalar-loop right-hand sides, original-matrix residuals, finite results and input preservation; scaled tolerance 3e-12. Lower/upper factors are constructed directly; no upstream factorization supplies the oracle. Indefinite errors, complex values, overwriting, arbitrary conditioning and speed unverified.

### stdlib-constrained-ls-reference (D9b1)

Independent API consumer; pinned sources and author tests reviewed. 96 full-rank REAL64 6x3 least-squares problems with one equality constraint and nonzero residuals. Repeated diagonal observations give an independent diagonal-Hessian Lagrange-multiplier solution; shear transforms mix the columns. Check solution, primal feasibility, stationarity, finite output, status and input preservation at scaled tolerance 5e-12. Multiple constraints, rank deficiency, complex values, workspace/overwrite modes and ill-conditioning unverified.

### stdlib-weighted-ls-reference (D9a1)

Independent API consumer; pinned sources and author tests reviewed. 96 non-exact REAL64 weighted line fits, 4..15 observations, positive nonuniform weights with ratio at most 16. Independent scalar weighted sums and a two-by-two determinant give intercept/slope. Full-rank problems; check known coefficients, weighted normal residuals, status, finiteness and matrix preservation; scaled tolerance 5e-12. Zero/negative weights, rank deficiency, complex values, other shapes and extreme weight ratios unverified.

### stdlib-nonsymmetric-eig-reference (D4a2)

Independent API consumer; pinned sources and author tests reviewed. 64 REAL64 nonsymmetric 3x3 problems constructed by explicit shear similarities of a planar rotation block plus a distinct real eigenvalue. All 192 analytic eigenvalues matched without assuming output order; finite outputs, status and input preservation checked. Both left/right eigenvector equations and Euclidean unit norms checked. Scaled residual tolerance 8e-12, absolute eigenvalue tolerance 8e-12. Singular pencils, defective/repeated spectra, complex input, arbitrary conditioning, other sizes and speed unverified.

### stdlib-generalized-eig-reference (D4b2)

Independent API consumer; pinned sources and author tests reviewed. 64 REAL64 nonsymmetric 3x3 generalized eigenvalue-only problems. A=B*S*T*inverse(S) and B=S*diag(1,2,4)*inverse(S), where T has a planar rotation block and a distinct real eigenvalue. All 192 analytic eigenvalues matched without assuming order, with absolute tolerance 8e-12; finite output, status and input preservation checked. The eigenvector-returning interface failed a retained complex-eigenpair probe and is not promoted. Singular pencils, defective/repeated spectra, complex input, other sizes, arbitrary conditioning and speed unverified.

### stdlib-real-schur-reference (D4a2)

Independent API consumer; pinned sources and author tests reviewed. 64 REAL64 nonsymmetric 3x3 problems constructed by explicit shear similarities of a planar rotation block plus a distinct real eigenvalue. All 192 analytic eigenvalues matched without assuming output order; finite outputs, status and input preservation checked. Real Schur factor reconstruction, orthogonality and nonoverlapping quasi-triangular blocks checked. Schur vectors are not claimed to be individual eigenvectors. Scaled residual tolerance 8e-12, absolute eigenvalue tolerance 8e-12. Singular pencils, defective/repeated spectra, complex input, arbitrary conditioning, other sizes and speed unverified.

### stdlib-cg-kernel-reference (D2b1b)

Independent API consumer; pinned sources and author tests reviewed. 102 dense REAL64 known-solution systems, orders 2..18, six right-hand-side families and a nonzero initial guess passed directly to the kernel. Dense symmetric strictly diagonally-dominant positive-definite matrices, no preconditioner. Requested rtol=1e-12; independent solution/residual tolerance 2e-9. Right-hand sides and final residuals use scalar loops. Finite results and matrix preservation checked. Public kernel with module-level matrix-vector/preconditioner callbacks and caller-owned workspace. Dense convenience wrappers segfaulted in this hosted configuration and are not promoted; exact probes are retained. Sparse convenience interfaces, zero RHS, boundary masks, arbitrary ill-conditioning, convergence diagnostics and speed unverified.

### stdlib-pcg-kernel-reference (D2b1b)

Independent API consumer; pinned sources and author tests reviewed. 102 dense REAL64 known-solution systems, orders 2..18, six right-hand-side families and a nonzero initial guess passed directly to the kernel. SPD matrices scaled by positive diagonal congruence factors spanning 0.1..10; explicit Jacobi preconditioning. Requested rtol=1e-12; independent solution/residual tolerance 2e-9. Right-hand sides and final residuals use scalar loops. Finite results and matrix preservation checked. Public kernel with module-level matrix-vector/preconditioner callbacks and caller-owned workspace. Dense convenience wrappers segfaulted in this hosted configuration and are not promoted; exact probes are retained. Sparse convenience interfaces, zero RHS, boundary masks, arbitrary ill-conditioning, convergence diagnostics and speed unverified.

### stdlib-bicgstab-kernel-reference (D2a1)

Independent API consumer; pinned sources and author tests reviewed. 102 dense REAL64 known-solution systems, orders 2..18, six right-hand-side families and a nonzero initial guess passed directly to the kernel. Nonsymmetric strictly diagonally-dominant matrices; requested rtol=1e-10 and independently checked solution/residual tolerance 5e-8. This does not certify the requested tolerance for all inputs or breakdown recovery. Right-hand sides and final residuals use scalar loops. Finite results and matrix preservation checked. Public kernel with module-level matrix-vector/preconditioner callbacks and caller-owned workspace. Dense convenience wrappers segfaulted in this hosted configuration and are not promoted; exact probes are retained. Sparse convenience interfaces, zero RHS, boundary masks, arbitrary ill-conditioning, convergence diagnostics and speed unverified.

## Provenance and actual output

### stdlib-spd-solve-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-spd-solve-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-spd-solve-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1052) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_solve_chol.f90)

```text
72 SPD systems, vector and three-RHS matrix interfaces, lower/upper factors; solve calls: 288
PASS stdlib-spd-solve-reference
```

### stdlib-factored-spd-solve-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-factored-spd-solve-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-factored-spd-solve-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1189) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_solve_chol.f90)

```text
72 SPD systems, vector and three-RHS matrix interfaces, lower/upper factors; solve calls: 288
PASS stdlib-factored-spd-solve-reference
```

### stdlib-constrained-ls-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-constrained-ls-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-constrained-ls-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1903) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_constrained_lstsq.f90)

```text
96 equality-constrained fits versus independent diagonal-Hessian/shear oracle, feasibility and stationarity
PASS stdlib-constrained-ls-reference
```

### stdlib-weighted-ls-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-weighted-ls-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-weighted-ls-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2122) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_lstsq.f90)

```text
96 weighted line fits versus independent scalar-sum formulas and weighted normal equations
PASS stdlib-weighted-ls-reference
```

### stdlib-nonsymmetric-eig-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-nonsymmetric-eig-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-nonsymmetric-eig-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3309) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_eigenvalues.f90)

```text
64 nonsymmetric three-by-three problems with analytic spectra: 192 eigenvalue references
PASS stdlib-nonsymmetric-eig-reference
```

### stdlib-generalized-eig-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-generalized-eig-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-generalized-eig-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L3345) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_eigenvalues.f90)

```text
64 generalized three-by-three eigenvalue-only problems with analytic spectra: 192 eigenvalue references
PASS stdlib-generalized-eig-reference
```

### stdlib-real-schur-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-real-schur-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-real-schur-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L2458) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_schur.f90)

```text
64 nonsymmetric three-by-three problems with analytic spectra: 192 eigenvalue references
PASS stdlib-real-schur-reference
```

### stdlib-cg-kernel-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-cg-kernel-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-cg-kernel-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg_iterative_solvers.f90#L99) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_solve_iterative.f90)

```text
Dense known-solution systems, orders 2..18, nonzero initial guess, independently recomputed residuals: 102
PASS stdlib-cg-kernel-reference
```

### stdlib-pcg-kernel-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-pcg-kernel-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-pcg-kernel-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg_iterative_solvers.f90#L180) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_solve_iterative.f90)

```text
Dense known-solution systems, orders 2..18, nonzero initial guess, independently recomputed residuals: 102
PASS stdlib-pcg-kernel-reference
```

### stdlib-bicgstab-kernel-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-bicgstab-kernel-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-bicgstab-kernel-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg_iterative_solvers.f90#L208) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg_solve_iterative.f90)

```text
Dense known-solution systems, orders 2..18, nonzero initial guess, independently recomputed residuals: 102
PASS stdlib-bicgstab-kernel-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-spd-solve-reference stdlib-factored-spd-solve-reference stdlib-constrained-ls-reference stdlib-weighted-ls-reference stdlib-nonsymmetric-eig-reference stdlib-generalized-eig-reference stdlib-real-schur-reference stdlib-cg-kernel-reference stdlib-pcg-kernel-reference stdlib-bicgstab-kernel-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
