# GAMS driver coverage audit and next priorities

Planning review: 2026-11-03. This is an audit of the current pinned selected-package records, not a new compilation run, an exhaustive package API inventory, or a ranking of software quality.

There are **503 checked drivers for 503 of 530 source-reviewed procedure records**. **27 records across 19 packages** have no dedicated checked driver. Another **40 mapped procedure/class claims** belong to procedures with a driver for a different class or configuration.

A missing driver does not mean the package cannot compile: ordinary catalog examples have separate evidence. A driver under one class does not automatically establish every other classification of its procedure. Conversely, a cross-class mismatch is not automatically a missing algorithm test; it may need a mapping or presentation review.

## Recommended next numerical candidates

These are ranked **candidates to probe**, not newly verified examples. Prefer a new API or derivative mode over another variation of an already checked routine. Use author examples for API setup and add independent references; do not weaken existing failed assertions to make a batch pass. There is no requirement to fill a batch of ten.

| Priority | Package / mapped procedure | GAMS | New coverage and independent oracle |
| ---: | --- | --- | --- |
| 1 | [nonlin: BFGS without a supplied gradient](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_optimize.f90#L584) | G1b1a | Existing driver supplies analytic derivatives; finite-difference fallback is a distinct unverified configuration. Use translated positive-definite quadratics and Rosenbrock problems with known minima; independently evaluate final objective and gradient and require successful solver status. |
| 2 | [nonlin: Nonlinear least squares without a supplied Jacobian](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_least_squares.f90#L141) | G1b1a | Existing driver supplies the residual Jacobian; automatic differencing needs its own checked configuration. Reuse the independently checked exact exponential family and explicit step factor 1 from the analytic-Jacobian consumer, without supplying its Jacobian. Independently recompute parameters, residual norms and stationarity. |
| 3 | [rpn-calculator-fortran: Signed real cube roots](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/src/funcs.f90#L1) | C2 | The existing consumer checks sinc and sech, leaving this separately mapped procedure unchecked. Use signed exact dyadic cubes, zero, and independently generated high-precision noncube references over a bounded normal range; check finite values, signs and scaled reconstruction. |
| 4 | [rpn-calculator-fortran: Modified Bessel I0](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/src/specfun/i0.f#L1) | C10 | The existing special-function driver covers beta, not the separately mapped Bessel function. Compare besi0 with high-precision modified-Bessel references confirmed at two precisions; include zero, signed values, parity and arguments on both sides of implementation branch boundaries. |
| 5 | [fortranlib: Integration of tabulated data](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L1) | H2 | The checked procedure record currently has a quadratic-root driver; tabulated integration is a different public capability. Derive exact area from the documented piecewise interpolation rule; test affine data, irregular grids, partial intervals and the supported integration-limit conventions. |
| 6 | [fortranlib: Interpolation of tabulated data](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L1) | E1 | A distinct mapped public API currently demonstrated only in the ordinary catalog main. Use irregular knots and independently computed segment weights, exact knot values and the documented endpoint/outside-range behavior. |

### 1. BFGS without a supplied gradient

Mapped record: `nonlin-bfgs`. [Author example/test](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_bfgs_example.f90) / [Author example/test](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/example_problems.f90)

Do not register the gradient callback. Reuse comparable problems from the analytic-gradient driver, with tolerances suitable for numerical differentiation; do not infer a speed ranking.

### 2. Nonlinear least squares without a supplied Jacobian

Mapped record: `nonlin-least-squares`. [Author example/test](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_least_squares_example.f90)

Do not register the residual-Jacobian callback. Retained default-step and nonzero-residual probes already fail even with analytic Jacobians: see docs/gams-candidates/nonlin-least-squares/README.md. Do not broaden this candidate into a general noisy-fit claim or accept convergence status without a correct answer.

### 3. Signed real cube roots

Mapped record: `rpn-elementary`. [Author example/test](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/test/test.f90)

Call the real cube-root API directly; establish the supported kind first. Exclude overflow and subnormals unless independently checked.

### 4. Modified Bessel I0

Mapped record: `rpn-special`. No matching author example is recorded; review the pinned API directly.

Inspect the pinned fixed-form implementation for precision and valid range. Do not reuse the package beta implementation as a reference or claim unscaled overflow behavior.

### 5. Integration of tabulated data

Mapped record: `fortranlib-numerics`. No matching author example is recorded; review the pinned API directly.

Use the catalog's pinned upstream lib_array fixes. Review the actual integral convention before assigning a more specific H2 subclass; do not demand exact integration of arbitrary nonlinear data.

### 6. Interpolation of tabulated data

Mapped record: `fortranlib-numerics`. No matching author example is recorded; review the pinned API directly.

Confirm construction and evaluation semantics in the staged, upstream-patched source. Refine the GAMS subclass only after confirming the interpolant; avoid copying the existing ordinary smoke check alone.

## The remaining uncovered mapped class

Counts are limited to classes used by our procedure mappings. Unused taxonomy branches are not counted as covered or exhausted.

- **L13b — Principal components analysis**: `forpca-pca`, `stdlib-pca`.

At this review, PCA is the outstanding class gap: the stdlib consumer exceeded the hosted link file-size limit and obtained no numerical results; the forpca consumer produced incorrect variances at the pinned revision. Investigate a selective stdlib link or an upstream repair before retrying. An independently reviewed PCA application using a working SVD API could be another route, but it would not verify either existing PCA API.

## Disposition of records with no dedicated driver

| Status | Records | Meaning |
| --- | ---: | --- |
| graphics-promotion | 5 | Ordinary headless artifact example exists; add a dedicated checked graphics problem if useful. |
| retained-failure | 17 | A recorded counterexample or runtime failure needs diagnosis/repair or a separately scoped API. |
| sandbox-limit | 3 | No numerical result; service/link constraints blocked the probe. |
| scope-review | 1 | Review private/overlapping API claims before adding a consumer. |
| workflow-review | 1 | Full application workflow differs from the checked supporting solver. |

### C4d

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [specfunc-fullerton: `specfunc-fullerton-entire-hyperbolic-integral`](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_inv_ci.f90#L32) | **retained-failure**. Resolve the signed Cinh counterexample before claiming full-domain accuracy; the public inverse_chi name does not mean inverse-function evaluation. [Retained evidence](gams-candidates/fullerton-gamma-cinh/README.md) |

### C7e

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [specfunc-fullerton: `specfunc-fullerton-upper-incomplete-gamma`](https://github.com/arjenmarkus/specfunc-fullerton/blob/498b486b8ca18f0289a2d35c6c5bc67eb10aefe3/src/fullerton_gamma.f90#L282) | **retained-failure**. The positive-x path already has a separate checked driver. Keep the full-domain x=0 failure and retest that boundary after a repair; do not add another positive-x duplicate. [Retained evidence](gams-candidates/fullerton-gamma-cinh/README.md) [Retained evidence](gams-candidates/fullerton-upper-gamma) |

### C19

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [stdlib: `stdlib-activation-gelu-gradient`](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L184) | **retained-failure**. Retest the independent differentiated references after an upstream fix; value-only GELU drivers do not cover this derivative. [Retained evidence](gams-candidates/stdlib-activations/gelu-gradient-result.json) |
| [stdlib: `stdlib-activation-silu-gradient`](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_specialfunctions.f90#L312) | **retained-failure**. Retest the independent derivative references after an upstream fix; value-only SiLU drivers do not cover this derivative. [Retained evidence](gams-candidates/stdlib-activations/silu-gradient-result.json) |

### D4a1

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [fortran-lapack: `fortran-lapack-eigh`](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/src/la_eigs.f90#L209) | **sandbox-limit**. Existing high-level eigensystem probes already fail at the hosted file-size linking limit. Investigate link footprint/selective linking before another attempt. The separately checked lower-level syev driver does not verify this high-level API. [Retained evidence](gams-candidates/fortran-lapack/README.md) |

### D6

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [forpca: `forpca-pca`](https://github.com/gha3mi/forpca/blob/d5d87badc4c25c647b3618f22560e712728d8165/src/forpca.f90#L29) | **retained-failure**. Keep the wrong-variance reproducer. Recheck an upstream repair or separately reviewed mode; do not reduce assertions to direction-only checks and call PCA variances verified. [Retained evidence](gams-candidates/forpca/covariance-variances-result.json) [Retained evidence](gams-sparse-integral.md) |
| [fortran-lapack: `fortran-lapack-svd`](https://github.com/perazz/fortran-lapack/blob/e5e45fdd5a38bfab06d1f703f12b787937aa33bb/src/la_svd.f90#L47) | **sandbox-limit**. Existing high-level SVD probes already fail at the hosted file-size linking limit. Investigate link footprint/selective linking before another attempt. The separately checked lower-level gesvd driver does not verify this high-level API. [Retained evidence](gams-candidates/fortran-lapack/README.md) |

### D9a1

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [stdlib: `stdlib-complex-underdetermined-fits`](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L1457) | **retained-failure**. Retest the exact wide COMPLEX128 LSTSQ call after resolving the retained size error. A successful pseudoinverse solve is a separate API, not verification of LSTSQ. [Retained evidence](gams-candidates/stdlib-underdetermined/README.md) |

### F1b

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [roots-fortran: `roots-fortran-toms748-bracketed`](https://github.com/jacobwilliams/roots-fortran/blob/85dc6b98404a61d49944939414f7f56c3f32edd1/src/root_module.F90#L335) | **retained-failure**. Investigate the direct-object status/overflow failure and convenience-wrapper crash separately; correct roots with failed status do not satisfy the checked-driver contract. [Retained evidence](gams-candidates/roots-structured-api/README.md) |

### H1

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [forlab: `forlab-difference-cumsum`](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L2673) | **retained-failure**. The difference-only API already has a checked driver. Resolve or clarify cumsum's sorting behavior before claiming ordered prefix sums; do not add another diff duplicate. [Retained evidence](gams-candidates/forlab-statistics/README.md) |

### H2b1a1

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [quadrature-fortran: `quadrature-fortran-2d-rectangles`](https://github.com/jacobwilliams/quadrature-fortran/blob/1d208fc59569a97b1c2abf9c45f7c352dcc7b318/src/quadrature_module.F90#L295) | **retained-failure**. Diagnose the retained nested-callback runtime crash before repeating the polynomial suite; distinguish callback/toolchain/sandbox behavior from numerical integration error. [Retained evidence](gams-candidates/quadrature-fortran-nested) |
| [quadrature-fortran: `quadrature-fortran-3d-rectangles`](https://github.com/jacobwilliams/quadrature-fortran/blob/1d208fc59569a97b1c2abf9c45f7c352dcc7b318/src/quadrature_module.F90#L329) | **retained-failure**. Diagnose the retained nested-callback runtime crash before repeating the polynomial suite; existing one-dimensional success does not validate nested integration. [Retained evidence](gams-candidates/quadrature-fortran-nested) |

### I1

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [friction: `friction-internal-state`](https://github.com/jchristopherson/friction/blob/8e75dcac26f47417a439adfcbaa24834105d89fe/src/friction_core.f90#L221) | **scope-review**. This record names private interpolation/fitting callbacks. The public LuGre integration API already has a checked driver; review or split the mapping before designing another consumer.  |

### I1b

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [twopnt: `twopnt-solve`](https://github.com/perazz/twopnt/blob/4ce477215f84a88d879f0ca3937cab9bedfb7762/src/twopnt_core.f90#L357) | **retained-failure**. Retest the manufactured full-profile and residual assertions after a source-supported upstream repair; solver success status alone is insufficient. [Retained evidence](gams-candidates/twopnt) |

### I2

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [heatflow: `heatflow-evolution`](https://github.com/ExeQuantCode/HeatFlow/blob/b0d930caad9160a15f0aeafa238c448f48f28d55/src/heatflow/mod_evolve.f90#L44) | **workflow-review**. Inspect simulate and its file/output requirements, then test a bounded manufactured full evolution with profiles and conservation. The separately checked sparse-solver heat example does not verify this application.  |

### K

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [fortran-simplify: `fortran-simplify-perpendicular`](https://github.com/jaiken17/fortran-simplify/blob/f546422216fb88eba97e2a0f4910935efbcdce83/src/simplify.f90#L559) | **retained-failure**. Preserve the repeated-call endpoint and radial-filter failures. Require an independently checked geometric error bound after a repair; the ordinary single-call example is not a general fix. [Retained evidence](fpm-candidates/fortran-simplify) |

### L1a1a

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [forlab: `forlab-median-percentiles`](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L6059) | **retained-failure**. Diagnose the first n=1 median crash. Percentile-only testing could be a separately reviewed consumer because the failed combined probe did not reach it. [Retained evidence](gams-candidates/forlab-statistics/README.md) |
| [orderpack: `orderpack-order-statistics`](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/src/M_orderpack.f90#L1) | **retained-failure**. Resolve the small-n orderloc counterexample first. orderval and orderval_special were not reached on that failing case; they may be reviewed and tested as separate APIs without claiming orderloc is fixed. [Retained evidence](gams-candidates/orderpack-statistics/README.md) |

### L6a21

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [fortran_test_helper: `fortran-test-helper-create-r64-array`](https://github.com/jchristopherson/fortran_test_helper/blob/1557b1485d8a5b042862042552f1e1a34552ca5e/src/fth_arrays.f90#L102) | **retained-failure**. Retest requested bounds after an upstream change; do not accept the observed out-of-range values as a uniform [0,1) driver. [Retained evidence](gams-candidates/test-helper-bounds) |

### L8

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [friction: `friction-fit`](https://github.com/jchristopherson/friction/blob/8e75dcac26f47417a439adfcbaa24834105d89fe/src/friction_core.f90#L315) | **retained-failure**. Resolve the retained double-subtraction diagnosis before repeating the same manufactured fit. [Retained evidence](gams-candidates/friction-double-subtraction) |

### L13b

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [forpca: `forpca-pca`](https://github.com/gha3mi/forpca/blob/d5d87badc4c25c647b3618f22560e712728d8165/src/forpca.f90#L29) | **retained-failure**. Keep the wrong-variance reproducer. Recheck an upstream repair or separately reviewed mode; do not reduce assertions to direction-only checks and call PCA variances verified. [Retained evidence](gams-candidates/forpca/covariance-variances-result.json) [Retained evidence](gams-sparse-integral.md) |
| [stdlib: `stdlib-pca`](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_stats.f90#L4074) | **sandbox-limit**. Highest class-coverage payoff (L13b). Investigate whether a smaller selective link fits the existing file-size limit before another full driver attempt; the failed link established no numerical result. [Retained evidence](gams-candidates/stdlib-pca/analytic-pca-result.json) |

### N5

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [coretran: `coretran-neighbor`](https://github.com/leonfoks/coretran/blob/204c4707f6680b6d7d1e4da39077d0fd3acfe37e/src/spatial/m_KdTree.f90#L1) | **retained-failure**. Retain the valid 31-point failing query; repeat full brute-force nearest-neighbor checks after a repair rather than promote the small ordinary smoke test. [Retained evidence](gams-candidates/coretran-nearest) |

### P

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [coretran: `coretran-neighbor`](https://github.com/leonfoks/coretran/blob/204c4707f6680b6d7d1e4da39077d0fd3acfe37e/src/spatial/m_KdTree.f90#L1) | **retained-failure**. Retain the valid 31-point failing query; repeat full brute-force nearest-neighbor checks after a repair rather than promote the small ordinary smoke test. [Retained evidence](gams-candidates/coretran-nearest) |
| [fortran-simplify: `fortran-simplify-perpendicular`](https://github.com/jaiken17/fortran-simplify/blob/f546422216fb88eba97e2a0f4910935efbcdce83/src/simplify.f90#L559) | **retained-failure**. Preserve the repeated-call endpoint and radial-filter failures. Require an independently checked geometric error bound after a repair; the ordinary single-call example is not a general fix. [Retained evidence](fpm-candidates/fortran-simplify) |

### Q

| Procedure / pinned evidence | Status and next action |
| --- | --- |
| [easy-plplot: `easy-plplot-png`](https://github.com/zoziha/easy_plplot/blob/77b0ac9b30d732196e99438064c35f4c1914eb7c/src/easy_plplot.f90#L1) | **graphics-promotion**. Reuse the headless author-style plotting setup, then add independent source-data/axis checks and artifact validation. A nonempty PNG alone is not mathematical verification.  |
| [gtk-fortran: `gtk-fortran-demo-api`](https://github.com/vmagnin/gtk-fortran/blob/6f731807228c55bcc0551d15f6d1f7f50bf1fe49/src/cairo-auto.f90#L1) | **graphics-promotion**. Keep Cairo image surfaces without GUI initialization; use known geometry and parsed output/status checks. Widgets and event loops remain outside the online sandbox scope.  |
| [m_draw: `m-draw-raster`](https://github.com/urbanjost/M_draw/blob/a70c305f607cdc1b3e95d5c2ed3b723dcc803204/src/M_draw.F90#L1) | **graphics-promotion**. Adapt the existing PPM example into a dedicated driver with parsed dimensions, complete pixel-range checks and independently predictable line/rectangle geometry. Headless output only; avoid unsupported font-dependent drivers.  |
| [ogpf: `ogpf-contour`](https://github.com/kookma/ogpf/blob/bd18021949be028856957c9c03832742513d5c67/src/ogpf.f90#L1) | **graphics-promotion**. Adapt the Gaussian contour example with explicit expected grid samples and headless artifact checks. Do not infer contour accuracy from file existence alone.  |
| [plplot: `plplot-demo-api`](https://github.com/PLplot/PLplot/blob/a28c702862ea466a4ee22faba1b676aade77dc4c/bindings/fortran/plplot.f90#L1) | **graphics-promotion**. Adapt the pinned author API with controlled geometry and output inspection, retaining native-library and device qualifications. Existing preview verification is ordinary-demo evidence, not a dedicated GAMS proof.  |

Records assigned to multiple classes appear more than once above; do not sum those rows. The [machine-readable audit](gams-driver-audit.json) preserves original qualifications, exact pins, source hashes, author links and disposition for every record.

The audit cross-checks older retained-probe reports as well as the procedure notes. In particular, the two high-level fortran-lapack records do not mention their historical linking failures in their notes; their dispositions above include the saved evidence and keep them off the immediate candidate list.

## Additional class claims on procedures that already have a driver

Review these before treating them as new-driver requests. A checked descendant also satisfies its ancestor in this audit; siblings do not. No classification or checked status was changed by this audit.

| Mapped class | Procedure | Existing driver classes | Review action |
| --- | --- | --- | --- |
| A1 | `bstrith-operations` | [N2](../fpm_catalog/gams-drivers/bstrith-bit-reference.f90) | The N2 consumer already contains independently checked additions/subtractions. Review the arithmetic scope of A1 before adding duplicate arithmetic assertions. |
| A1 | `orbs-bitsets` | [N2](../fpm_catalog/gams-drivers/orbs-bitwise-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| A6 | `strith-api` | [A1](../fpm_catalog/gams-drivers/strith-integer-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| C2 | `rpn-elementary` | [C4](../fpm_catalog/gams-drivers/rpn-sinc-sech-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| C10 | `rpn-special` | [C7](../fpm_catalog/gams-drivers/rpn-beta-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| E1 | `fortranlib-numerics` | [F1](../fpm_catalog/gams-drivers/fortranlib-quadratic-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| E1a | `lookup-interpolation` | [E3](../fpm_catalog/gams-drivers/lookup-services-reference.f90) | The E3 service consumer already checks interpolated values. A new E1a driver should demonstrate a distinct construction/interpolation problem; otherwise review cross-class presentation. |
| E2 | `gslib-api` | [L13](../fpm_catalog/gams-drivers/gslib-kriging-reference.f90) | Existing L13 driver checks ordinary kriging systems and covariance. Review E2 interpolation scope and classification; a new driver should add a distinct spatial interpolation problem. |
| E2a | `bspline-fortran-3d-mixed-partials` | [E3a2](../fpm_catalog/gams-drivers/bspline-fortran-3d-mixed-partials-reference.f90) | Existing driver constructs the interpolant and checks values as well as derivatives. Review E2a versus E3a2 presentation before duplicating the same experiment. |
| E2a | `bspline-fortran-4d-mixed-partials` | [E3a2](../fpm_catalog/gams-drivers/bspline-fortran-4d-mixed-partials-reference.f90) | Existing driver constructs the interpolant and checks values as well as derivatives. Review E2a versus E3a2 presentation before duplicating the same experiment. |
| G1b1a | `nonlin-bfgs` | [G1b1b](../fpm_catalog/gams-drivers/nonlin-rosenbrock-bfgs.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| G1b1a | `nonlin-least-squares` | [G1b1b](../fpm_catalog/gams-drivers/nonlin-lsq-jacobian-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| H2 | `formal-divergence` | [H1](../fpm_catalog/gams-drivers/formal-polynomial-reference.f90) | H1 divergence/gradient success is not a time-dependent PDE solution. Split volume-integration and PDE claims; I2 needs a real evolution/boundary problem, not relabeling the operator test. |
| H2 | `fortranlib-numerics` | [F1](../fpm_catalog/gams-drivers/fortranlib-quadratic-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| I2 | `fmm2d-potentials` | [D1](../fpm_catalog/gams-drivers/fmm2d-laplace-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| I2 | `formal-divergence` | [H1](../fpm_catalog/gams-drivers/formal-polynomial-reference.f90) | H1 divergence/gradient success is not a time-dependent PDE solution. Split volume-integration and PDE claims; I2 needs a real evolution/boundary problem, not relabeling the operator test. |
| L6c | `rng-uniform` | [L6a21](../fpm_catalog/gams-drivers/rng-xoroshiro-reference.f90) | Existing golden-stream driver already checks seed/jump behavior. Review whether to expose that proof under L6c before writing a duplicate; cached-normal reseeding remains a separate retained failure. |
| N1 | `m-cli-demo-api` | [N3](../fpm_catalog/gams-drivers/cli-namelist-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N1 | `m-history-demo-api` | [N3](../fpm_catalog/gams-drivers/history-edit-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N1 | `rojff-json` | [N3](../fpm_catalog/gams-drivers/rojff-json-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N1 | `yafyaml-configuration` | [N3](../fpm_catalog/gams-drivers/yaml-values-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N3 | `configuration-values` | [N1](../fpm_catalog/gams-drivers/config-file-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N3 | `fed-format` | [N1](../fpm_catalog/gams-drivers/fed-format-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N3 | `numerical-portability` | [R1](../fpm_catalog/gams-drivers/penf-machine-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `fdict-dictionary` | [N4](../fpm_catalog/gams-drivers/fdict-values-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `flibcpp-sort-search` | [N6](../fpm_catalog/gams-drivers/flibcpp-sort-search-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `ftl-containers` | [N4](../fpm_catalog/gams-drivers/ftl-state-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `fycollections-demo-api` | [N4](../fpm_catalog/gams-drivers/fy-list-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `gftl-shared-containers` | [N4](../fpm_catalog/gams-drivers/gftl-container-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `jeyemhex-regex-strings` | [N3](../fpm_catalog/gams-drivers/regex-language-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `lmdb-transactions` | [N4](../fpm_catalog/gams-drivers/lmdb-rollback-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `qcontainers-storage` | [N4](../fpm_catalog/gams-drivers/qcontainers-state-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `sqliteff-database` | [N1](../fpm_catalog/gams-drivers/sqlite-transactions-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N5 | `utf8-strings` | [N3](../fpm_catalog/gams-drivers/utf8-codepoints-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| N6 | `fortran-utils-splines` | [E1](../fpm_catalog/gams-drivers/fortran-utils-spline-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| P | `spatial-neighbors` | [N5](../fpm_catalog/gams-drivers/kdtree-neighbor-reference.f90) | The N5 consumer already compares 3D nearest/radius searches against brute force. Review P discovery classification versus demonstrated geometry before proposing the same search again. |
| R2 | `assert-contracts` | [S3](../fpm_catalog/gams-drivers/assert-enforcement-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| R2 | `assert-values` | [S3](../fpm_catalog/gams-drivers/fassert-captured-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| R2 | `julienne-diagnosis` | [S3](../fpm_catalog/gams-drivers/julienne-diagnosis-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |
| R3 | `error-validation` | [R2](../fpm_catalog/gams-drivers/error-bounds-reference.f90) | Review whether this is a distinct algorithm/configuration, a supporting capability already exercised, or an overly broad discovery claim. Do not duplicate or relabel a driver automatically. |

## Further expansion after these candidates

The mapped ledger is representative, not a full procedure inventory. Additional valuable work can come from new APIs in already compiled packages, especially common problems enabling accuracy comparisons across libraries. Review each new API and its GAMS mapping before adding a checked driver. The five graphics promotions are useful but lower priority than the distinct numerical APIs/modes above; artifact existence alone is insufficient.

Retained failures can exist outside the procedure ledger. For example, the [Fstats interpolation probes](gams-candidates/fstats-interpolation/README.md) include an unpublished spline mismatch and Hermite reinitialization failure; the successful fresh-object Hermite driver does not erase those limitations.

## Maintenance

```text
python xaudit_gams_drivers.py
python xaudit_gams_drivers.py --check
```

Edit the planning judgments in [gams-driver-priorities.json](../fpm_catalog/gams-driver-priorities.json). Counts and lists are computed from the current classifications and driver manifest; UTF-8/LF-normalized input SHA256 hashes identify the snapshot across Windows and Linux. Completed candidate/class pairs drop out of the next-candidate list. New unchecked records receive needs-triage rather than being silently classified as failures. The script submits no compiler jobs, rebuilds no library and requires no backend deployment. See [coverage](gams-coverage.md) and [numerical review](gams-numerical.md) for the broader catalog.
