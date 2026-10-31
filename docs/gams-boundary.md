# Checked GAMS boundary-value spectral problem and retained failed probe

The checked featom driver demonstrates a radial nonrelativistic boundary-value eigenproblem in I1b. A separate TWOPNT manufactured-problem probe failed its independent checks and is retained without a verified-driver designation. Boundary-value methods and GAMS categories are not exhausted.

## Coulomb bound-state energies: featom

The driver calls `total_energy` in its nonrelativistic point-Coulomb branch for nuclear charges Z=1 and Z=2. For principal quantum numbers n=1..3 and angular indices l=0..n-1, the exact energies are `E_n=-Z^2/(2*n^2)` Hartree. Twelve returned energies are compared with this independent formula, including the angular degeneracy within each n. Maximum absolute error must be at most `1e-7` Hartree.

Both solves use eight radial elements, polynomial degree 20, 43 quadrature points per element, radial endpoint 100 and mesh grading parameter 100. Returned dimensions must support the first six levels, degrees of freedom must be positive, and the checked energies and first six wavefunctions must be finite. Finiteness alone does not verify wavefunction shape or normalization. Dirac/relativistic and self-consistent DFT branches, higher levels, mesh convergence and full-spectrum accuracy are not verified.

The driver passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package library. Only its main and executable were compiled. The [verification report](gams-boundary-validation.json) records source hashes and actual output. Its independent API-consumer source has its own MIT notice; upstream package terms remain separate.

### featom-coulomb-spectrum

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=featom&example=gams-featom-coulomb-spectrum) / [Driver source](../fpm_catalog/gams-drivers/featom-coulomb-spectrum.f90) / [Pinned procedure](https://github.com/atomic-solvers/featom/blob/87872a3266ceeee61a7244e6ecd134dc3bda790f/src/schroed_dirac_solver.f90#L18)

```text
Nuclear charge: 1; finite-element degrees of freedom: 159
n,l=  1  0; energy=     -0.499999999999; error=   1.170E-12
n,l=  2  0; energy=     -0.125000000000; error=   1.481E-13
n,l=  2  1; energy=     -0.125000000000; error=   5.784E-14
n,l=  3  0; energy=     -0.055555555556; error=   3.703E-14
n,l=  3  1; energy=     -0.055555555556; error=   1.198E-14
n,l=  3  2; energy=     -0.055555555556; error=   3.404E-14
Nuclear charge: 2; finite-element degrees of freedom: 159
n,l=  1  0; energy=     -2.000000000002; error=   1.704E-12
n,l=  2  0; energy=     -0.500000000000; error=   4.960E-13
n,l=  2  1; energy=     -0.500000000000; error=   1.903E-13
n,l=  3  0; energy=     -0.222222222222; error=   1.632E-13
n,l=  3  1; energy=     -0.222222222222; error=   5.218E-15
n,l=  3  2; energy=     -0.222222222222; error=   8.696E-14
Maximum absolute energy error:    1.70441E-12
Only the first six levels per charge are checked; full wavefunction accuracy is not claimed.
PASS featom-coulomb-spectrum
```

## TWOPNT probe that was not accepted

The manufactured problem is `u_second_derivative=-2` on [0,1], `u(0)=u(1)=0`, with exact profile `u=x*(1-x)`. The probe implements a derived `TwoPntBVProblem`, conservative three-point spatial residuals, the solver's finite-difference Jacobian and a zero initial guess. It intended to check fixed uniform grids of 9, 17 and 33 points, full-profile errors, endpoint conditions and a separately evaluated discrete equation residual.

On the first nine-point grid, the pinned solver prints `SUCCESS` and returns a false error flag but leaves the zero initial guess unchanged. The profile error is 0.25 and residual error is 2, so the independent driver rejects the result. The later grids are not reached. This is an observed failure, not a successful boundary-value demonstration.

Inspection of the [pinned search routine](https://github.com/perazz/twopnt/blob/4ce477215f84a88d879f0ca3937cab9bedfb7762/src/twopnt_core.f90) shows a convergence exit for the trial iterate `v1` before the subsequent `v0=v1` assignment. The return therefore exposes the preceding iterate; for this linear problem the first Newton trial solves the equations, but the returned initial iterate does not. This source-based explanation is an inference supported by the retained run, not an upstream-confirmed diagnosis.

[Failing source](gams-candidates/twopnt/poisson-returned-iterate.f90) / [Saved sandbox result](gams-candidates/twopnt/poisson-returned-iterate-result.json)

The failed probe is absent from the checked-driver manifest and example menus. Its source-supported I1b mapping remains, with the limitation in its procedure notes. No library patch, cached-package rebuild or tolerance relaxation was applied. A corrected upstream implementation or a separately reviewed patch is needed before promoting this probe to a verified driver.

## Related spectral checks

The [linear-algebra review](gams-linear-algebra.md) gives matching ARPACK and linalg_fortran D4a1 drivers for the same 20-by-20 Dirichlet matrix, with analytic eigenvalues and eigenvectors. Those ordinary matrix eigenproblems are separate from featom's radial boundary-value formulation.

## Maintenance

```text
python xverify_gams_drivers.py --drivers featom-coulomb-spectrum
python xverify_gams_drivers.py --drivers arpack-poisson-eigenpairs linalg-poisson-eigenpairs
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. Publishing these checked examples requires no backend redeployment or package library rebuild.
