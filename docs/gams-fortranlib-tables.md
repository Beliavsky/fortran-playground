# Five checked scientific-table drivers for fortranlib

All five independent REAL64 consumers passed GNU Fortran 16.2.0 / FPM 0.12.0 with the existing cached fortranlib library. Only main.f90 and playground-main were compiled. The [verification report](gams-fortranlib-tables-validation.json) preserves exact package pins, normalized UTF-8/LF source hashes, timings and full output. No new failed probe was produced. No backend deployment or package rebuild is needed. GAMS coverage remains unfinished.

## Checked problems

| Driver | GAMS | Independent checks |
| --- | --- | --- |
| Logarithmic interpolation | E1c | 715 scalar/vector query pairs from eleven analytic families |
| Logarithmic areas and prefixes | H2a1b2 | 726 subset areas, eleven full integrals and 55 cumulative values |
| Conservative rebinning | H2c | 84 cell means and fourteen total-area identities |
| Bilinear surfaces | E2a | 1875 interior/boundary values and twelve outside fills |
| Masked histograms | L1a1d | Six weighted/unweighted 1D histograms and three 2D count maps |

## Why this smaller batch

The existing mapped-procedure queue is mostly retained failures, service limits or overlapping classification claims. Repeating near-identical drivers solely to fill another batch of ten would offer little benefit. These five consumers instead cover previously unreviewed public APIs and distinct scientific-data operations in an already compiled package. This does not imply that all package APIs or all GAMS branches have been exhausted.

For subsequent work, prefer a named capability with a clear independent oracle, a common problem comparing multiple packages, resolution of the PCA linking limitation, or retesting an upstream repair. I recommend pausing automatic gap-filling batches rather than treating the driver count as a target. The [coverage audit](gams-driver-audit.md) retains the outstanding work.

## Analytic table conventions

The data consumers use the irregular positive grid [1/2,1,2,4,8]. A shared independent reference model defines four elementary families and explicit antiderivatives: linear 2+p*x; exponential 3*exp(p*x); affine-logarithm 2+p*log(x); and power law 3*x**p. Exponential parameters are -1/4,0,1/4, affine-log parameters -1/2,0,1/2, and power exponents -2,-1,0,1/2,2. Linear rebinning also uses p=-1,0,1. These are eleven log-mode families and fourteen rebinning families, not separate drivers for each variation.

The upstream names linlog, loglin and loglog mean log(y) versus linear x, linear y versus log(x), and log(y) versus log(x), respectively. These conventions are stated explicitly because reversing the axes changes the mathematical problem. Constant cases and the reciprocal power-law integral are checked without dividing by a zero parameter. All finite numerical comparisons use abs(actual-reference)<=2e-11*max(1,abs(reference)).

## Interpolation and integration

For every log family, interpolation checks 61 in-domain queries including knots and boundaries, plus four positive outside-domain queries using bounds_error=false and fill_value=-123. Both scalar and array interfaces are checked against the defining elementary function. Invalid/nonpositive log inputs, duplicate/descending knots, extrapolation and arbitrary nonanalytic tables are excluded.

The area consumer evaluates every ordered pair from eleven limits spanning [1/4,9], giving 66 intervals per family. Limits are independently clipped to [1/2,8] and the explicit antiderivative supplies the reference. Empty, outside, same-segment and knot-crossing intervals are included. Full-domain and each cumulative-prefix value are checked independently. Reversed limits, error estimation and ill-conditioned near-reciprocal/near-constant branches are not established.

These tests use functions exactly representable by the selected interpolant. They do not claim that interpolating or integrating arbitrary data reproduces an unknown underlying physical function, or that an adaptive accuracy target is supported. E1c records nonpolynomial interpolation; H2a1b2 records a nonautomatic finite-grid quadrature API.

## Conservative remapping

All four rebin APIs map samples onto six irregular cell centers [1/2,1,3/2,5/2,4,8]. For linear-x modes the interior cell edges are arithmetic midpoints; for log-x modes they are geometric midpoints. The first and last centers themselves bound the domain, rather than extending half a cell beyond it.

Each expected output is the independent analytic integral over its cell divided by cell width. The width-weighted sum of all six returned means must equal the known full-domain integral. This checks a conservation property and distinguishes cell averaging from evaluating the field at the center. Arbitrary density reconstruction, degenerate cells and invalid log inputs are excluded.

## Bilinear surfaces and histograms

Three fields a+b*x+c*y+d*x*y on irregular 4-by-3 grids check axis orientation and independent cross terms. Each uses a 25-by-25 query grid including all four outer edges and corners, followed by four explicit outside-fill calls. Higher-order surfaces, invalid shapes, descending coordinates and extrapolation are not checked.

One-dimensional histograms use eleven exact dyadic samples spanning outside [-1,1], four equal bins, positive dyadic weights, and three masks (all, alternating, none). Each mask is checked with and without weights. Independent half-open membership enumeration supplies bin counts and weight sums, with the final upper endpoint included in the last bin. Bin centers are checked separately. The Cartesian 121-point grid supplies three masked two-dimensional count maps, checked cell by cell. 2D weighting, density normalization, variable widths, descending bounds and random-distribution quality are not asserted.

## Provenance and limits

Pinned lib_array APIs and implementations were reviewed directly; no matching pinned author example is recorded for these consumers. The independent MIT drivers copy no author implementation or test bodies. The source pin is 60fd094d3e137137ce00ec120b085e9b23ebf68b; the cached image already contains the checksum-locked upstream lib_array fixes matching 844611933cba06d71490033e68b355f6f0ff704f. Those existing adaptations, dependency pins, image recipe and precompiled build report remain unchanged.

Classifications use the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). Loading an example does not submit a job. The catalog now has 514 checked drivers and 541 mapped procedure records. These new APIs add an E1c class demonstration; the previously outstanding PCA class remains unverified.

## Driver details

### fortranlib-logarithmic-interpolation-reference (E1c)

Independent API consumer. 715 scalar/vector evaluations across eleven exact exponential, affine-logarithm and power-law tables. Irregular positive grid, 61 in-domain values and four explicit fill queries per family. Modes mean log(y) versus x, y versus log(x), and log(y) versus log(x), respectively. Constant data, negative/zero exponents and reciprocal power included. Tolerance 2e-11*max(1,abs(reference)); nonpositive log inputs, descending/duplicate grids and extrapolation excluded.

### fortranlib-logarithmic-areas-reference (H2a1b2)

Independent API consumer. Eleven exponential, affine-log and power-law families. 726 ordered clipped subset integrals, eleven full integrals and 55 cumulative prefix values against explicit antiderivatives. Includes constant/reciprocal cases, empty/outside/same-segment and knot-crossing intervals. Existing pinned lib_array upstream fixes are reused. Tolerance 2e-11*max(1,abs(reference)); reversed limits, invalid log inputs and near-reciprocal cancellation are excluded.

### fortranlib-conservative-rebinning-reference (H2c)

Independent API consumer. Fourteen linear/exponential/affine-log/power-law data sets rebinned onto six irregular cell centers. 84 cell means checked against independently integrated analytic densities and fourteen total-area conservation identities. Arithmetic cell edges for linear-x modes and geometric edges for log-x modes; first/last centers are domain edges. Existing upstream fixes unchanged. Tolerance 2e-11*max(1,abs(reference)); not pointwise interpolation, arbitrary nonanalytic densities or invalid log inputs.

### fortranlib-bilinear-surfaces-reference (E2a)

Independent API consumer. Three bilinear surfaces with independent cross terms on irregular 4-by-3 grids. 1875 values including edges/corners plus twelve explicit outside-fill queries; direct analytic field reference checks axis orientation and boundary handling. Tolerance 2e-11*max(1,abs(reference)); higher-order surfaces, invalid shapes and extrapolation excluded.

### fortranlib-masked-histograms-reference (L1a1d)

Independent API consumer. Six masked/unmasked weighted/unweighted 1D histograms and three 2D count histograms on exact dyadic boundary/outside fixtures. Independent half-open bin enumeration, closed final endpoint, empty-mask zeros, bin centers and per-cell counts/sums. 1D weights positive dyadics; 2D API unweighted. Counts and weight sums checked exactly; not probability densities, random-distribution validation, descending bounds or arbitrary bin widths.

## Provenance and actual output

### fortranlib-logarithmic-interpolation-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-logarithmic-interpolation-reference) / [Driver source](../fpm_catalog/gams-drivers/fortranlib-logarithmic-interpolation-reference.f90) / [Pinned procedure](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L579) / No pinned author example; API reviewed directly.

```text
Logarithmic scalar/vector query pairs checked: 715
PASS fortranlib-logarithmic-interpolation-reference
```

### fortranlib-logarithmic-areas-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-logarithmic-areas-reference) / [Driver source](../fpm_catalog/gams-drivers/fortranlib-logarithmic-areas-reference.f90) / [Pinned procedure](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L330) / No pinned author example; API reviewed directly.

```text
Logarithmic subset areas checked: 726
11 full integrals and 55 cumulative-prefix values independently checked.
PASS fortranlib-logarithmic-areas-reference
```

### fortranlib-conservative-rebinning-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-conservative-rebinning-reference) / [Driver source](../fpm_catalog/gams-drivers/fortranlib-conservative-rebinning-reference.f90) / [Pinned procedure](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L852) / No pinned author example; API reviewed directly.

```text
Independent conservative cell means checked: 84
14 total-area conservation identities checked.
PASS fortranlib-conservative-rebinning-reference
```

### fortranlib-bilinear-surfaces-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-bilinear-surfaces-reference) / [Driver source](../fpm_catalog/gams-drivers/fortranlib-bilinear-surfaces-reference.f90) / [Pinned procedure](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L772) / No pinned author example; API reviewed directly.

```text
Independent bilinear values including boundaries: 1875
12 explicit outside-fill values checked.
PASS fortranlib-bilinear-surfaces-reference
```

### fortranlib-masked-histograms-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortranlib&example=gams-fortranlib-masked-histograms-reference) / [Driver source](../fpm_catalog/gams-drivers/fortranlib-masked-histograms-reference.f90) / [Pinned procedure](https://github.com/astrofrog/fortranlib/blob/60fd094d3e137137ce00ec120b085e9b23ebf68b/src/lib_array.f90#L1016) / No pinned author example; API reviewed directly.

```text
6 one-dimensional histograms and 3 two-dimensional histograms independently checked.
PASS fortranlib-masked-histograms-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fortranlib-logarithmic-interpolation-reference fortranlib-logarithmic-areas-reference fortranlib-conservative-rebinning-reference fortranlib-bilinear-surfaces-reference fortranlib-masked-histograms-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
