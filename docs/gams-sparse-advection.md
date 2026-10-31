# Checked sparse systems and periodic advection

These D2 and I2 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-sparse-advection-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## HeatFlow sparse BiCG systems (D2)

Four matrix sizes [5,9,17,33], three banded families and three scales [0.125,1,8] give 36 matrices. All are strictly row-diagonally dominant with positive diagonals: the first family is symmetric tridiagonal, the second changes the upper band to make it nonsymmetric, and the third adds unequal second bands. Sparse storage must retain exactly the nonzero count of the original dense matrix.

Each matrix is solved for three manufactured solutions (constant, alternating with varying magnitude, and a shifted sine), using zero and nonzero initial guesses. All 216 solves check 3,456 known solution entries. Right-hand sides and true residuals are formed with independent scalar dense sums, not the library multiply routine. Right-hand sides must remain unchanged. The sparse allocation is released between matrices.

The requested relative L2 tolerance is 1e-11 with stopping mode 1 and a 500-iteration cap. Returned values and solver error must be finite, iterations must lie in [1,500], and the reported error must be <= 1.01e-11. Independently, max(abs(x-x_exact))/(1+max(abs(x_exact))) must be <= 2e-9 and max(abs(A*x-b))/(1+max(abs(b))) <= 2e-10. Saved maxima are 2.5522e-11 and 2.3739e-11 respectively. These modest, well-conditioned systems do not verify singular/indefinite behavior, other stopping modes, parallel execution or the full HeatFlow evolution/Cattaneo application.

## HR-WENO periodic finite-volume advection (I2)

The independent consumer solves u_t+c*u_x=0 on a unit periodic interval using WENO k=3 reconstruction and third-order TVD Runge-Kutta. It supplies three ghost cells on each side and selects right states for positive velocity or left states for negative velocity. The two endpoint fluxes are identical, making the semidiscrete flux sum telescope. This exercises spatial reconstruction in a PDE, rather than only the package time integrator.

Three grids [64,128,256], modes [0,1,2], velocities [-1.5,0.75], phase origins [0,0.37], and (mean,amplitude) pairs [(1.25,0.2),(-0.5,-0.3)] give 72 problems. Mode zero supplies constant-state tests. Initial data are exact cell averages: mean+amplitude*sin(pi*m*dx)/(pi*m*dx)*sin(2*pi*m*(x-origin)), with the zero-mode factor defined as one. The step is 0.2*dx/abs(c). Two continued calls request travel distances 0.0625 and 0.125, producing 144 checkpoints and 21,504 analytic cell-average references.

This fixed-step API returns the first time beyond the requested time rather than interpolating to it. The harness initially assumed exact output times; source review corrected that assumption. Returned time must be finite and between the requested time and one step beyond it, with a 1e-12 roundoff allowance. The analytic reference shifts the wave by c times the actual returned time.

Every cell must be finite. Constant-state maximum error must be <= 5e-12. For nonzero mode m, the maximum absolute error bound is 5e-12+0.002*abs(amplitude)*(m*64/n)**2. This is an explicit resolution/frequency-dependent acceptance bound, not a claim of a measured convergence order. Every normalized mass error abs(sum(u)*dx-mean)/(1+abs(mean)) must be <= 5e-12. The saved maximum amplitude-scaled cell error is 8.0028e-5, the largest error divided by its fixture bound is 1.0004e-2, and the maximum normalized mass error is 6.9081e-16. Nonuniform grids, shocks, nonlinear fluxes, multidimensional equations and formal convergence rates remain unverified.

## Preserved k=2 accuracy-threshold result

A k=2 probe built but exceeded the proposed accuracy bound: the first failing 64-cell mode-one negative-velocity fixture had maximum cell error 1.4202932710161154e-3 versus bound 4.0000000500000000e-4. This is not an established algorithm defect. Spatial/time discretization error requires a convergence study before judging that configuration; the k=3 suite alone does not verify k=2.

The [preserved probe](gams-candidates/hrweno-k2-accuracy/README.md) retains its exact source, pin, normalized hash and complete result. It is not registered as a checked driver. The successful suite keeps the same reference and bounds, restricted to k=3; no comparison was relaxed and no library source or bounds checking was changed.

## Sources, licenses and actual output

Pinned implementations and the HR-WENO author conservation-law example were reviewed before writing these independent API consumers. The drivers and preserved probe have their own MIT notice. HeatFlow retains its GPL-3.0 terms, and HR-WENO its MIT terms; upstream test and implementation bodies are not copied or relabeled. The HeatFlow record has no pinned author example, so its source was reviewed directly. Loading a link does not submit a job.

### heatflow-bicg-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=heatflow&example=gams-heatflow-bicg-reference) / [Driver source](../fpm_catalog/gams-drivers/heatflow-bicg-reference.f90) / [Pinned procedure](https://github.com/ExeQuantCode/HeatFlow/blob/b0d930caad9160a15f0aeafa238c448f48f28d55/src/heatflow/mod_Sparse.f90#L273) / No pinned author example; API reviewed directly.

```text
Sparse matrices: 36
BiCG solves: 216
Known solution entries: 3456
Maximum normalized solution error:   2.5522E-11
Maximum normalized true residual:   2.3739E-11
PASS heatflow-bicg-reference
```

### hrweno-advection-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=hrweno&example=gams-hrweno-advection-reference) / [Driver source](../fpm_catalog/gams-drivers/hrweno-advection-reference.f90) / [Pinned procedure](https://github.com/HugoMVale/HR-WENO/blob/2885105a7ba98351fed299b22e9bc0c67a809d2f/src/hrweno_weno.f90#L129) / [Author test](https://github.com/HugoMVale/HR-WENO/blob/2885105a7ba98351fed299b22e9bc0c67a809d2f/example/example1_burgers_1d_fv.f90)

```text
Periodic advection problems: 72
Analytic cell-average references: 21504
Maximum amplitude-scaled cell error:   8.0028E-05
Maximum error / fixture bound:   1.0004E-02
Maximum normalized mass error:   6.9081E-16
PASS hrweno-advection-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers heatflow-bicg-reference hrweno-advection-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
