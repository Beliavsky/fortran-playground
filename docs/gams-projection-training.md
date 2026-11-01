# Checked halfspace projections and affine-network training

These G2h3b1b and G1b drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-projection-training-validation.json) retains pins, source hashes and complete output. GAMS categories are not exhausted.

## Optgra weighted halfspace projections (G2h3b1b)

The independent consumer minimizes f(x)=0.5*sum(h_i*(x_i-c_i)**2) subject to a dot (x-c)>=b. Every h_i is positive and b>0. The unconstrained minimizer c is infeasible; the unique constrained minimizer is x_star=c+lambda*a/h, with lambda=b/sum(a_i**2/h_i)>0 and f_star=b**2/(2*sum(a_i**2/h_i)). These formulas follow directly from the single active constraint and stationarity h*(x-c)-lambda*a=0. The driver checks them independently of the optimizer.

Dimensions [2,3,5], diagonal condition ratios [1,5], heights [0.5,2], zero/quarter-integer centers and feasible/infeasible starts give 48 projections and 160 optimizer-coordinate references. Diagonal entries are linearly spaced from 1 to the condition ratio, and a_i=(-1)**i*(1+i/4). Starts are c and c+2*(x_star-c). The supplied callbacks return the objective gradient and full affine-constraint Jacobian; analytic mode Varder=1 must actually call the derivative callback. There were 240 derivative calls.

Optgra must return status 1 (feasible optimum) with finite coordinates and returned values. The method is spectral conjugate gradients (Optmet=2), with a 300-iteration limit and constraint/objective Consca thresholds 1e-9/1e-11. Consca contains convergence thresholds, not scale factors. Coordinate error normalized by 1+max(abs(x_star)) must be <=2e-4, objective error divided by 1+f_star <=1e-7, inequality violation divided by 1+b <=2e-7, and stationarity residual divided by 1+max(abs(lambda*a)) <=2e-4. Returned objective/constraint values must also agree with direct evaluation within normalized error 1e-8.

Saved maximum point, objective, feasibility, stationarity and returned-value discrepancies were 1.34283e-6, 4.12945e-12, 1.25825e-15, 2.16013e-6 and 4.11316e-17. This driver checks only one affine inequality with strictly convex quadratic objectives. It does not verify nonlinear constraints, equality constraints, multiple active constraints, nonconvex objectives or general solver robustness.

## neural-fortran affine-network training (G1b)

The independent consumer calls network%train directly, rather than implementing its own training loop. A single dense layer with linear activation learns two-output affine maps from one or two input coordinates. For map index m=1 or 2, weight rows are m*[0.75,-0.5] and [-0.25,1]/m, and bias is m*[0.5,-0.75]; the second weight column is omitted for one input. These dyadic coefficients have exact representations in the default real32 precision used by this cached build.

The Cartesian training grid is {-1,0,1} in each input dimension, with three or nine observations and two output channels. Its augmented design matrix has full column rank. A linear dense layer can represent the map exactly, so the known global minimum training loss is zero; this is a convex least-squares fixture, not a nonlinear neural-network convergence claim.

Two dimensions, two affine maps, seeds [42,1729,314159] and two batch settings give 24 training runs. Each GNU random seed array contains seed+37*i. Stochastic batches have size 1; full batches use every observation. network%train runs 400 epochs with SGD learning rate 0.1 and its default quadratic loss. At this pin stochastic training draws random contiguous batches with replacement, so an epoch need not visit every observation. Full batches include the complete grid. Only one coarray image is used.

A separate real64 scalar affine formula checks predictions on 11-point Cartesian grids from -1 to 1 in steps of 0.2, including points absent from training. The 3,168 output entries must be finite and have maximum absolute error divided by 1+max(abs(expected)) <=2e-4. Training MSE is independently recomputed in real64 against the affine formula, averaged across observations and output channels; it must be <=1e-8 and <=1e-5 of its initial value. This is not a check of a library-reported loss.

Saved maximum normalized prediction error, final training MSE and final/initial MSE ratio were 8.84756e-7, 4.52182e-13 and 5.87537e-13. Nonlinear activations, hidden layers, noisy data, other optimizers, parallel training and cross-compiler RNG reproducibility remain unverified. The G1b mapping is network-specific internal-backpropagation optimization; it is not a general scalar-objective callback solver.

## Sources, licenses and actual output

Pinned implementations/interfaces and author API examples were reviewed before writing these independent consumers. No upstream implementation or test bodies are copied. The drivers have their own MIT notice; Optgra and neural-fortran retain their respective upstream license terms. Loading a driver does not submit a job.

### optgra-halfspace-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=optgra&example=gams-optgra-halfspace-reference) / [Driver source](../fpm_catalog/gams-drivers/optgra-halfspace-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/optgra/blob/914bed713e80faa4a190e03beb3a8307077eb028/src/optgra.F90#L36) / [Author test](https://github.com/jacobwilliams/optgra/blob/914bed713e80faa4a190e03beb3a8307077eb028/test/optgra_test.f90)

```text
Halfspace projections: 48; analytic coordinates: 160
Analytic derivative callbacks: 240
Max point, objective, feasibility, KKT, returned-value errors:    1.34283E-06   4.12945E-12   1.25825E-15   2.16013E-06   4.11316E-17
PASS optgra-halfspace-reference
```

### neural-affine-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=neural-fortran&example=gams-neural-affine-reference) / [Driver source](../fpm_catalog/gams-drivers/neural-affine-reference.f90) / [Pinned procedure](https://github.com/modern-fortran/neural-fortran/blob/b2073fa542c8dcdf9466d1a192d2888b628a5df3/src/nf/nf_network.f90#L248) / [Author test](https://github.com/modern-fortran/neural-fortran/blob/b2073fa542c8dcdf9466d1a192d2888b628a5df3/example/quadratic.f90)

```text
Affine training runs: 24; test prediction entries: 3168
Max normalized prediction error, final MSE, final/initial MSE:    8.84756E-07   4.52182E-13   5.87537E-13
PASS neural-affine-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers optgra-halfspace-reference neural-affine-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
