# GAMS G1 procedure review

Unconstrained optimization is refined by dimension, smoothness and user-supplied derivatives, using the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). This review covers 12 procedure mappings in 8 selected packages. Assignments describe specific functionality at pinned revisions, not complete coverage of a class.

## Detailed problem classes

| Class | Problem | User-supplied derivatives |
| --- | --- | --- |
| [G1a1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G1a1a) | Smooth univariate minimization | None |
| [G1b1a](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G1b1a) | Smooth multivariate minimization | None |
| [G1b1b](https://gams.nist.gov/cgi-bin/serve.cgi/Class/G1b1b) | Smooth multivariate minimization | First derivatives |

Finite-difference mode and analytic-gradient mode are classified separately. For smooth nonlinear least squares, an analytic residual Jacobian supplies first-derivative information for the squared-residual objective. Those solvers retain their specialized residual/Jacobian interfaces. Broader mappings remain where a more specific review has not been made.

## Reviewed procedures

| Package | Module / procedure | Class | Derivatives | Source and author examples | Notes |
| --- | --- | --- | --- | --- | --- |
| fmin | `fmin_module` / `fmin` | G1a1a | none | [Source](https://github.com/jacobwilliams/fmin/blob/3d094fba0e9b98d132414f8442c7c76d32da1d30/src/fmin_module.f90#L94) · [Author example](https://github.com/jacobwilliams/fmin/blob/3d094fba0e9b98d132414f8442c7c76d32da1d30/test/test.f90) | Search interval brackets a scalar minimizer; this is not a general constraint solver. |
| minpack | `minpack_module` / `lmdif1` | G1b1a | finite-difference residual Jacobian | [Source](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/src/minpack.f90#L2331) · [Author example](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/examples/example_lmdif1.f90) | Nonlinear least squares using residual values; the scalar objective is their squared norm. |
| minpack | `minpack_module` / `lmder1` | G1b1b | user residual Jacobian | [Source](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/src/minpack.f90#L1846) · [Author example](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/examples/example_lmder1.f90) | Nonlinear least squares; requires both residual values and their Jacobian. For smooth nonlinear least squares, the user residual Jacobian supplies first-derivative information for the squared-residual objective; this is not a general scalar-objective gradient interface. |
| fortimize | `ForTimize` / `minimize with NelderMead` | G1b | none | [Source](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/src/minimize.f90#L7) · [Source](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/src/gradient_free/nelder_mead.f90#L9) · [Author example](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/example/gradient.f90) | The existing catalog quadratic program is an independently written API example. Upstream licensing is unspecified; no upstream example code is copied here. |
| fortimize | `ForTimize` / `minimize with GradientDescent` | G1b | user gradient | [Source](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/src/minimize.f90#L7) · [Source](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/src/with_derivatives/gradient_descent.f90#L23) · [Author example](https://github.com/fedebenelli/ForTimize/blob/3431b656cd86f89135d0f35bf6afdbd787d9daf3/example/gradient.f90) | Fixed-iteration gradient descent. The author example is API evidence, not a verified reference for gradient accuracy. |
| nonlin | `nonlin` / `nelder_mead%solve` | G1b1a | none | [Source](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_optimize.f90#L127) · [Author example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_nm_opt_example.f90) · [Author example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/example_problems.f90) | Accepts a scalar objective through fcnnvar_helper. |
| nonlin | `nonlin` / `bfgs%solve` | G1b1a, G1b1b | optional user gradient; finite-difference fallback | [Source](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_optimize.f90#L584) · [Source](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_multi_var.f90#L204) · [Author example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_bfgs_example.f90) · [Author example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/example_problems.f90) | User gradients are registered with fcnnvar_helper%set_gradient_fcn. G1b1a applies to finite-difference mode; G1b1b applies when the user supplies the gradient/Jacobian. The driver, where present, identifies its selected configuration. |
| nonlin | `nonlin` / `least_squares_solver%solve` | G1b1a, G1b1b | optional user residual Jacobian | [Source](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_least_squares.f90#L141) · [Author example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_least_squares_example.f90) | The unconstrained least_squares_solver is mapped; constrained_least_squares_solver is a distinct type. For smooth nonlinear least squares, the user residual Jacobian supplies first-derivative information for the squared-residual objective; this is not a general scalar-objective gradient interface. G1b1a applies to finite-difference mode; G1b1b applies when the user supplies the gradient/Jacobian. The driver, where present, identifies its selected configuration. |
| nlopt-f | `nlopt_wrap` / `nlopt_opt%optimize with LD_LBFGS` | G1b1b | user gradient | [Source](https://github.com/awvwgk/nlopt-f/blob/83d21e7ebda9279a6dd4cc11fe6c735f48eb8689/src/nlopt_wrap.f90#L268) · [Source](https://github.com/awvwgk/nlopt-f/blob/83d21e7ebda9279a6dd4cc11fe6c735f48eb8689/src/nlopt_enum.F90#L301) | The algorithm selection is part of the mapping. test/test_opt.f90 uses constrained LD_MMA and is not accepted as a G1 author example; the existing catalog demo uses LD_LBFGS. |
| libdogleg-f | `dogleg` / `dl_optimize (dl_optimize_dense2)` | G1b1b | user residual Jacobian | [Source](https://github.com/ivan-pi/libdogleg-f/blob/32b65ae4f880a052768c05d24c24b79920710681/src/dogleg.f90#L142) · [Author example](https://github.com/ivan-pi/libdogleg-f/blob/32b65ae4f880a052768c05d24c24b79920710681/example/lmder_example.f90) | Dense nonlinear least squares; Jacobian layout is parameters by residuals, transposed relative to MINPACK. For smooth nonlinear least squares, the user residual Jacobian supplies first-derivative information for the squared-residual objective; this is not a general scalar-objective gradient interface. |
| neural-fortran | `nf` / `network%train` | G1b | internal backpropagation | [Source](https://github.com/modern-fortran/neural-fortran/blob/b2073fa542c8dcdf9466d1a192d2888b628a5df3/src/nf/nf_network.f90#L248) · [Source](https://github.com/modern-fortran/neural-fortran/blob/b2073fa542c8dcdf9466d1a192d2888b628a5df3/src/nf/nf_optimizers.f90#L123) · [Author example](https://github.com/modern-fortran/neural-fortran/blob/b2073fa542c8dcdf9466d1a192d2888b628a5df3/example/quadratic.f90) | Network-specific training with SGD/other optimizer types, not a general scalar-objective callback solver. No small deterministic training benchmark is claimed. |
| seiscope-optimization | `opt_LBFGS` / `LBFGS` | G1b1b | user first derivatives | [Source](https://github.com/ofmla/seiscope_opt_toolbox_w_ctypes/blob/74a25c29d13c506e16f8025eb13a2cf396dc23c0/src/sotb/merged-LBFGS.f90#L213) · [Author example](https://github.com/ofmla/seiscope_opt_toolbox_w_ctypes/blob/74a25c29d13c506e16f8025eb13a2cf396dc23c0/app/LBFGS/test_LBFGS.f90) | Unconstrained smooth multivariate minimization requiring user first derivatives. The guarded catalog edit replaces an uninitialized workspace-length actual argument with optim%l. |

Nonlin’s Brent example finds a root; it is not evidence of univariate minimization. The NLopt author example reviewed uses constrained MMA; the unconstrained Rosenbrock driver is independently written. Neural-fortran training is network-specific, rather than a general objective callback API. ForTimize has no clear source license at the reviewed revision; its author example is linked, not copied.

## Working demonstrations

Author examples are adapted where suitable, with license notices retained. Independently written API drivers are identified below. Drivers use module callbacks, independent accuracy checks and readable output. Loading a link does not submit a job.

| Driver | Problem / class | Driver origin | License |
| --- | --- | --- | --- |
| [Load fmin-sine](https://beliavsky.github.io/fortran-playground/fpm/?package=fmin&example=gams-fmin-sine) · [Source](../fpm_catalog/gams-drivers/fmin-sine.f90) | sine-minimum / G1a1a | [Author example](https://github.com/jacobwilliams/fmin/blob/3d094fba0e9b98d132414f8442c7c76d32da1d30/test/test.f90) | BSD-3-Clause · [License](../fpm_catalog/gams-drivers/licenses/fmin-BSD-3.txt) |
| [Load minpack-bard](https://beliavsky.github.io/fortran-playground/fpm/?package=minpack&example=gams-minpack-bard) · [Source](../fpm_catalog/gams-drivers/minpack-bard.f90) | bard-15 / G1b1a | [Author example](https://github.com/jacobwilliams/minpack/blob/c0b5aea9fcd2b83865af921a7a7e881904f8d3c2/examples/example_lmdif1.f90) | MIT · [License](../fpm_catalog/gams-drivers/licenses/minpack-MIT.txt) |
| [Load libdogleg-bard](https://beliavsky.github.io/fortran-playground/fpm/?package=libdogleg-f&example=gams-libdogleg-bard) · [Source](../fpm_catalog/gams-drivers/libdogleg-bard.f90) | bard-15 / G1b1b | [Author example](https://github.com/ivan-pi/libdogleg-f/blob/32b65ae4f880a052768c05d24c24b79920710681/example/lmder_example.f90) | LGPL-3.0-or-later · [License](../fpm_catalog/gams-drivers/licenses/libdogleg-COPYING), [License](../fpm_catalog/gams-drivers/licenses/libdogleg-COPYING.LESSER) |
| [Load nonlin-rosenbrock-nm](https://beliavsky.github.io/fortran-playground/fpm/?package=nonlin&example=gams-nonlin-rosenbrock-nm) · [Source](../fpm_catalog/gams-drivers/nonlin-rosenbrock-nm.f90) | rosenbrock-2 / G1b1a | [Author example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_nm_opt_example.f90) | MIT · [License](../fpm_catalog/gams-drivers/licenses/nonlin-MIT.txt) |
| [Load nonlin-rosenbrock-bfgs](https://beliavsky.github.io/fortran-playground/fpm/?package=nonlin&example=gams-nonlin-rosenbrock-bfgs) · [Source](../fpm_catalog/gams-drivers/nonlin-rosenbrock-bfgs.f90) | rosenbrock-2 / G1b1b | [Author example](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_bfgs_example.f90) | MIT · [License](../fpm_catalog/gams-drivers/licenses/nonlin-MIT.txt) |
| [Load nlopt-rosenbrock-lbfgs](https://beliavsky.github.io/fortran-playground/fpm/?package=nlopt-f&example=gams-nlopt-rosenbrock-lbfgs) · [Source](../fpm_catalog/gams-drivers/nlopt-rosenbrock-lbfgs.f90) | rosenbrock-2 / G1b1b | Independent API driver | MIT · [License](../fpm_catalog/gams-drivers/licenses/nonlin-MIT.txt) |

All 6 drivers passed the hosted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. The [saved verification results](gams-g1-validation.json) include source hashes and program output. Publishing checks that these hashes and package revisions still match.

The sine driver minimizes sin(x) on [-4,0] and checks the solution against −π/2. Both Bard drivers fit the same 15 observations, start from (1,1,1), and check against (0.08241058, 1.133037, 2.343695), with maximum parameter error below 0.0002. Both require the residual norm to differ from 0.09063596 by less than 0.0000001. MINPACK estimates the Jacobian by finite differences; libdogleg uses an analytic Jacobian. Callback counts and individual sandbox timings are not a fair performance ranking.

## Common Rosenbrock problem

The three Rosenbrock drivers minimize `(1-x)^2 + 100*(y-x^2)^2`, starting from `(-1.2,1)`. They independently check the known minimizer `(1,1)` with maximum parameter error at most `1e-4`, objective at most `1e-10`, finite results and agreement with the solver-reported objective. The gradient-based drivers first check their analytic gradient against central differences. Solver termination settings differ across APIs; the independent acceptance checks are shared.

| Driver | Maximum parameter error | Independent objective | Objective calls | Gradient calls |
| --- | --- | --- | --- | --- |
| nonlin-rosenbrock-nm | 1.1213E-06 | 6.3877E-13 | 202 | 0 |
| nonlin-rosenbrock-bfgs | 3.3307E-15 | 1.2819E-28 | 72 | 50 |
| nlopt-rosenbrock-lbfgs | 1.4780E-11 | 7.3573E-23 | 56 | 56 |

Counts describe the recorded runs, exclude the preliminary gradient checks and do not establish a general performance ranking. Derivative-free and analytic-gradient methods perform different work. All libraries were reused; only the supplied main programs and executables were compiled.

The examples are also available in the hosted and main local FPM playground example menu. For local use, load a driver and download the complete FPM project, or use its source as an application in an FPM project depending on the linked pinned package.

## Maintenance and portability

Procedure evidence, revision pins, derivative requirements, author-example paths, and raw upstream SHA-256 hashes are recorded in [gams.json](../fpm_catalog/gams.json). Driver provenance and licenses are in [gams-drivers.json](../fpm_catalog/gams-drivers.json). Driver hashes normalize UTF-8 line endings to LF. The portable catalog export includes both the procedure mappings and demonstrations.

Run `python xpackage_gams.py` and `python xfpm_examples.py` after changing reviewed metadata. Changed drivers must be verified again on GNU Fortran 16 before publication. With Modal installed and authenticated, verify selected drivers against the existing compiled images:

```text
python xverify_gams_drivers.py --drivers nonlin-rosenbrock-nm nonlin-rosenbrock-bfgs nlopt-rosenbrock-lbfgs
```

The verifier uses the local `.fpm-audit-cache/precompiled.json` build report and records results in `docs/gams-g1-validation.json`. It does not rebuild package libraries or deploy the service. These metadata and example changes require no backend deployment or package recompilation.
