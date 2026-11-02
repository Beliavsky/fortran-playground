# Fortran software by GAMS classification

The [GAMS catalog](https://beliavsky.github.io/fortran-playground/gams/) browses the selected precompiled packages independently of the FPM playground. It has an index of the 20 main classes, a page for every recorded class or subclass, and a detail page for every package.

Class pages include packages explicitly assigned to that class or its descendants. They show matching reviewed APIs where available. Package pages include descriptions, topics, classifications, pinned repository sources, procedure evidence, author example/test references and links to checked playground examples. Classification and source review do not imply coverage of every problem in a class or a performance benchmark. A checked package example may exercise only part of the mapped functionality.

Each package page also lists **Package dependencies** and **Used by**. These use the resolved GitHub source records from the verified playground build, combining direct and indirect dependencies. Dependencies with their own selected catalog entry link to that page; other repositories link to GitHub. Every dependency includes a link to the exact source revision, with a note when it differs from the selected catalog version. Reverse lists cover only selected builds, not usage elsewhere on GitHub. Large reverse lists are collapsed initially.

The dependency list describes the pinned playground configuration, including any playground adaptations. It does not classify edges as direct, identify internal Fortran module relationships, or list native system libraries and build tools. An empty list means no additional GitHub repository dependencies were recorded; it does not claim the package needs no external software. These sections are generated offline and add no compilation, service requests or backend deployment requirements.

Package lists and navigation are present in the HTML and work without JavaScript. Optional browser search combines words across names, GitHub owners, descriptions, categories, author and curated topics, class labels and procedure names. Search changes the `q` parameter, so a filtered page can be bookmarked or shared.

Repository owner names are clickable on package cards and detail pages. An owner page lists that account's selected precompiled packages and links to its GitHub profile. The [owner index](https://beliavsky.github.io/fortran-playground/gams/authors/) searches both public display names and account names. Names appear as “Federico Perini (perazz)” when a public display name is supplied; otherwise the account name is shown. Organizations use the same convention. These are repository owners, not necessarily the original or sole authors.

The `fortran-lang` account is displayed as **fortran-lang**, since its GitHub display name names the language. Its original public profile metadata remains saved for provenance and search.

The [curated attribution review](name-attributions.md) records explicit public source credits separately from account identities. Confirmed source authors are searchable and shown with their scope and evidence under **Name attribution** on package and owner pages. An author credited in an example is not automatically identified as the owner of the account.

## Addresses

- Index: `/fortran-playground/gams/`
- Linear systems: `/fortran-playground/gams/D2/`
- Multivariate unconstrained optimization: `/fortran-playground/gams/G1b/`
- Package details: `/fortran-playground/gams/packages/fortran-lapack/`
- Repository owners: `/fortran-playground/gams/authors/`
- An owner's packages: `/fortran-playground/gams/authors/perazz/`
- Search: `/fortran-playground/gams/?q=jacobwilliams+optimization`
- Sitemap: `/fortran-playground/gams/sitemap.xml`

Class pages use explicit parent links, rather than code-prefix matching: C1 and C10 are siblings. Empty classes remain linkable and explain that there is no currently classified selected package.

Class and package cards link directly to checked drivers where available. A
class page shows only drivers whose recorded problem class belongs to that
class or a descendant. For example, [G1b1a](https://beliavsky.github.io/fortran-playground/gams/G1b1a/)
offers the derivative-free Rosenbrock driver, while
[G1b1b](https://beliavsky.github.io/fortran-playground/gams/G1b1b/) offers the
analytic-gradient versions. A procedure supporting both configurations does
not make its analytic-gradient driver a derivative-free example. Loading a
driver selects the package and source without submitting a job. The
[G1 review](gams-g1.md) records exact procedures, provenance, shared accuracy
checks and saved results.

The [quadrature review](gams-quadrature.md) similarly connects the smooth
finite-interval class H2a1a1 and special-integrand class H2a2a1 to checked
programs. Driver records identify their verification report explicitly;
publication and portable catalog provenance include every report used, while
older optimization records retain their existing report addresses.

The [scalar-root review](gams-roots.md) connects F1b to checked Brent and safeguarded Newton drivers using shared nonpolynomial equations, independent accuracy checks and callback counts.

The [linear-algebra review](gams-linear-algebra.md) connects real dense solves (D2a1) and unconstrained linear least squares (D9a1) to shared fortran-lapack and stdlib examples, including a rank-deficient minimum-norm case.

The [ODE review](gams-ode.md) connects nonstiff one-step methods (I1a1a) and multistep methods (I1a1b) to DOP853, rklib RK4 and DDEABM drivers with a shared analytic decay/oscillator problem and a separate RK4 convergence check.

The [interpolation review](gams-interpolation.md) connects E1a to finterp, PCHIP and bspline-fortran drivers with common affine/monotone data, sampled shape checks, and a separate cubic B-spline value/derivative check.

The [transform review](gams-transforms.md) connects J1a2/J1a3 to complex FFT and cosine-transform drivers with independent direct-sum references and explicit normalization/precision settings. The generated [coverage report](gams-coverage.md) tracks source-reviewed procedures and dedicated checked drivers separately, including classes still awaiting drivers. A taxonomy leaf is not treated as an exhausted domain.

The [constrained-optimization review](gams-constrained.md) links G2h1a2 to comparable box-constrained quadratic drivers and G2h3b1b to a checked SLSQP equality/nonlinear-inequality example, including independent feasibility and constrained-stationarity checks.

The [special-function review](gams-special-functions.md) connects Gamma, digamma and modified Bessel procedures (C7a, C7c and C10b1) to precision-aware checked examples with independent reference values and supplementary identities.

The linear-algebra review also covers symmetric eigenproblems (D4a1), reduced QR (D5) and reduced SVD (D6), with known spectra and reconstruction/orthogonality checks. It retains reproducers for high-level wrapper calls that exceeded the hosted link-size limit; the menu uses verified lower-level SYEV/GESVD interfaces.

The [statistics review](gams-statistics.md) connects location and dispersion (L1a1a/L1a1b) to comparable stdlib and fstats mean/variance drivers, with known shifted/scaled answers, explicit sample/population normalization and subset checks.

## Updating packages and classifications

Continue the existing catalog workflow. Edit `fpm_catalog.json`, the classifications and procedure records in `fpm_catalog/gams.json`, the numerical review ledger, topics and checked example references as appropriate. Then regenerate the playground and review files:

```text
python xpackage_topics.py
python xpackage_gams.py
python xfpm_examples.py
```

Every normal `python xsite.py` build publishes the portable catalog feed and passes that same data to `xgams_site.py`. The generator writes class pages, package pages and a sitemap into `_site/gams/`. Counts and membership are computed from the feed, so there is no second classification list to maintain. Obsolete generated class/package HTML is removed on a rebuild. CSS and browser search live in `site/gams/`; generated HTML is not committed.

GitHub Actions already runs `xsite.py` when changes reach `main`. Publishing these pages requires no backend redeployment, package recompilation or Modal jobs. The playground loads only its own existing assets; the new pages and their search script are separate.

## Public owner names

The [combined GitHub/name mapping table](github-name-mappings.md) lists every selected repository owner, the catalog name, profile/manual source, review dates, pending attribution notes, evidence and package links. The [manual attribution review](name-attributions.md) gives the detailed reasoning behind curated records.

`fpm_catalog/owners.json` stores each owner's public GitHub display name once, keyed by the lowercase account ID. Each record contains its account type, profile/source URLs and retrieval time. The portable catalog exports this shared mapping too. Site builds read the saved snapshot offline; account names remain the fallback for a newly added owner without saved metadata.

Fetch profiles for newly added accounts:

```text
python xgithub_owners.py --refresh --missing
```

Periodically refresh all accounts with `python xgithub_owners.py --refresh`. To update just one, use `python xgithub_owners.py --refresh --owners perazz`. The API reader uses `GITHUB_TOKEN` or `GH_TOKEN` when present. If the public API is rate-limited, wait before retrying or explicitly read the public profile headings instead:

```text
python xgithub_owners.py --refresh --missing --html
```

Refresh errors retain saved names. A successful refresh with no public name clears the previous name. Names are read only from public profile fields/headings; they are not inferred from account names, README acknowledgments, commits or email addresses. Run `python xgithub_owners.py` to validate the snapshot and report coverage without network access. Commit the snapshot, then publish through the ordinary Pages build.

## Curated names and source credits

Edit `fpm_catalog/name-attributions.json` for manual research. `owner_names` holds account-name mappings; `project_authors` holds credits for specific projects or source files. Each record requires a name, confirmed/inferred status, scope, rationale, review date and public evidence links. Prefer exact commit and line links. Do not collect unrelated personal information. Source credits establish authorship within their stated scope; they do not alone establish an account identity or sole authorship of a project.

Only confirmed account mappings override owner labels. Display order is confirmed manual account name, saved GitHub display name, then account ID. Inferred account mappings remain in the review table and portable feed, but do not rename accounts. Confirmed project/source credits are displayed and searched independently. Differences between a manual name and a GitHub display name are flagged in the review table and explained on the owner page. GitHub profile refreshes never overwrite curated records.

After editing the manual file, refreshing profiles or adding packages, regenerate both the combined name table and manual review table:

```text
python xpackage_attributions.py
python xpackage_attributions.py --check
```

The site build exports these records and renders the name-attribution sections automatically. The initial AD_dnSVM record credits David Lauvergnat for `APP/Example_dnS.f90`; the possible connection to account `lauvergn` is recorded separately as inferred.

## Preview and verification

```text
python xsite.py
python -m http.server 8878 --bind 127.0.0.1 --directory _site
```

Open <http://127.0.0.1:8878/gams/>. Stop the preview server with Ctrl+C.

```text
python -m unittest discover -s tests -p test_gams_site.py
node tests/gams_search.mjs
```

The checks cover hierarchy membership, generated navigation, pinned package links, HTML escaping, removal of obsolete pages, search and restoration of shared search queries. The ordinary site-build test also checks the published pages and versioned assets.

## A broader catalog

The renderer consumes the [portable catalog feed](catalog-export.md), rather than compiling or discovering packages itself. A future catalog can import the maintained records and add non-FPM projects or individual Fortran sources with their own review status. Keep those additions in a separate catalog so playground availability is not implied. The catalog's canonical base address is currently shared with the exporter in `catalog_export.py`.

The [random-generator review](gams-random.md) connects uniform generation (L6a21) and seeding support (L6c) to exact reference-sequence and replay checks for MT19937-64, rngff and stdlib.

The [differentiation review](gams-differentiation.md) connects H1 to shared analytic derivative checks for NumDiff, ForDiff and AD_dnSVM, covering finite differences, complex step and automatic differentiation.

The [nonlinear-system review](gams-systems.md) connects F2 to a shared two-equation problem with known root for MINPACK, nonlin and nlesolver-fortran, including explicit Jacobian configurations and independently checked residuals.

The [sparse and positive-definite system review](gams-sparse.md) connects D2b4 and D2b1b to checked MINRES, qdldl-fortran and KISS examples, including two right-hand sides, factor reuse, matrix requirements and scaled backward errors.

The [cubature and quadrature-rule review](gams-cubature.md) connects H2b1a1 and H2c to checked DCUHRE box integrals, Gauss-Jacobi weighted moments and reference-element cubature moments, preserving the distinction between adaptive integration and rule generation.

The [surface-interpolation review](gams-surfaces.md) connects E2a to shared nonuniform-grid bilinear checks for finterp and bspline-fortran, with additional bicubic value and mixed-partial checks for B-splines.

The [stiff-ODE review](gams-stiff.md) connects I1a2 to a common exact two-scale ODE for DVODE, LSODA and stiff3, including BDF-mode observation, distinct tolerance controls and fast/slow mode checks. It does not claim DAE validation.

The [polynomial-root review](gams-polynomial.md) connects F1a to the polyroots, rpoly and cpolyroots procedures, with distinct-root matching, normalized polynomial residuals and coefficient scaling checks.

The [convolution review](gams-convolution.md) connects J2 to spectrum and fastconv direct-sum checks, documenting full, central and valid output conventions, native precision, and the pinned fastconv shape-preserving boundary limitation.

The [regression review](gams-regression.md) connects L8 to odrpack95 orthogonal line fits and lib_statistics grouped-binomial logistic fits, with separate error models, closed-form parameters and independently checked objectives/statistics/covariance.

The [matrix-equation review](gams-matrix-equations.md) connects D8 to SLICOT Lyapunov and Sylvester drivers, including continuous/discrete forms, rectangular solutions, transpose options and Schur-factor reuse.

Class-page **Try in playground** links select an available checked driver for that class, preferring an exact class over a descendant. If no matching driver exists, the fallback is labeled **Open default example**. Package/owner pages keep their general links. See the [stdlib sorting example and link behavior](gams-sorting.md).

Class cards distinguish **Verified**, **Source-supported**, and **Uncertain** mappings. Verification applies to the matching driver's tested configuration; a sibling-class driver or a successful package default does not verify this classification. Descendant drivers identify their narrower class. Package details label evidence separately for each procedure/class pair.

The generated [mapping evidence and review queue](gams-mapping-evidence.md) lists discovery assignments needing source review and procedures still needing matching drivers. If inspection shows that a claimed algorithm is absent, narrow or remove its classification. Record sandbox limits, missing dependencies and upstream defects in the existing review notes rather than treating those failures as proof of absence.

The [number-theory review](gams-number-theory.md) covers both selected B packages: prime enumeration/primality against trial division and GCD/LCM against enumerated integer references. Their class-page links open these checked drivers. The review retains a pinned large-int64 primality timeout reproducer and documents the LCM(0,0) restriction.

The [arithmetic review](gams-arithmetic.md) connects A1 to signed decimal-integer checks, A2 to exact rational addition, and A6 to bit-preserving binary64 decimal round trips. It documents fraction-reduction and representation limits. The A1 strith driver does not verify strith's separate A6 mapping.

The same review connects A3c/A4c to MPFUN real/complex addition with exact 120-digit reference identities, and N2 to 5120 binary-string checks against native integer operations. The real and complex examples are selected separately on their class pages; arithmetic coverage does not imply verification of other package routines.

The [special-function review](gams-special-functions.md) also covers C14 Carlson elliptic integrals against independent quadrature, C19 Bernoulli values and exact integer power sums, and C10 complex AMOS Bessel sequences against separate series/closed forms. It retains an AMOS lower-half-plane discrepancy and documents unassigned odd Bernoulli outputs at the pinned revision.

The [linear-algebra review](gams-linear-algebra.md) also connects D1b6 to BLAS transpose/scaling checks against scalar loops, D1b4 to accumulated COO/CSR matrix-vector products, and D9c to five known pseudoinverses and a minimum-norm solution. The sparse multiplication driver does not verify the separate storage-conversion class.

The [applied-methods review](gams-applied-methods.md) connects K1 to least-squares spline fits with known noisy-data residuals and derivatives, L10a2a to direct/FFT autocovariance and correlation against scalar lag sums, and H2b1a2 to 67 exact polynomial integrals over rectangles, a variable-bound region and a 3D box. Panel counts and zero-variance correlation restrictions are explicit.

The [constrained-optimization review](gams-constrained.md) also connects G2a to linear programs with analytical dual certificates, G2h1a1 to BOBYQA on the shared box quadratic, and G2i to three seeded PIKAIA Rastrigin searches. Solver return codes, evaluation limits and finite-run global-search limitations are distinguished from independent answer checks.

The [boundary-value review](gams-boundary.md) connects I1b to featom Coulomb energy checks and retains a rejected TWOPNT Poisson probe that reports success but returns the preceding iterate. The failed probe is absent from the checked-driver menus. The [linear-algebra review](gams-linear-algebra.md) adds shared ARPACK/linalg_fortran Dirichlet eigenpair checks, refining their reviewed APIs to the real symmetric D4a1 class.

The [resampling and Markov-model review](gams-resampling-markov.md) connects L4 to FJsample leave-one-out uncertainty checks and M to econ-toolchain analytic stationary distributions and Gaussian AR(1) transition probabilities. It documents the jackknife bias convention and the differing row/column probability conventions. Both class pages open matching checked drivers.

The [Fourier and geometry review](gams-fourier-geometry.md) connects J1a1 to 42 spectrum forward real transforms against direct Fourier sums and P to 12 geodesic-fortran routes with independent spherical and WGS84 references. The [storage-conversion review](gams-linear-algebra.md#sparse-storage-conversion) connects D1b9 to explicit COO coordinates and CSR row pointers, values and reconstruction. Class links select these checked examples; inverse FFT and sparse threshold behavior remain outside their verified scope.

The [sparse LU and stored-spline integration review](gams-sparse-integral.md) connects D2a4 to Y12M factor reuse on nonsymmetric systems and H2a2b2 to fitpack integrals against polynomial antiderivatives. It also retains a failed forpca variance probe with its pinned source and actual result; that probe is absent from checked-driver menus and leaves the PCA mapping source-supported.

The [spatial and nonuniform-transform review](gams-spatial-nufft.md) connects N5 to exhaustive kdtree2 neighbor searches, E2 to DelaunaySparse three-dimensional interpolation with checked simplex geometry, and J1 to 24 NUFFT1D transforms against direct Fourier sums. The kdtree2 N5 driver does not independently verify its separate broad P mapping; class-page links preserve this distinction.

The [PDE review](gams-pde.md) connects I2 to fishpack nonzero-boundary Poisson/Helmholtz problems and PoisFFT periodic Poisson problems. Exact discrete solutions distinguish solver error from continuous discretization error; grid refinement, independent finite-difference residuals and FFT-plan reuse are checked. Each I2 package card opens its matching problem; unrelated source-supported mappings retain their default-example labels.

The [numeric parsing, storage and machine-kind review](gams-data-kinds.md) connects N3 to exact fortran-fast-float parsing references and error outcomes, N4 to an independent FIFO record model, and R1 to PENF numerical kinds, machine constants and a runtime roundoff experiment. The PENF R1 driver does not verify its separate N3 conversion mapping.

The [scalar-product, assertion and error-status review](gams-products-status.md) connects D1 to exact blocked fordot products, S3 to captured fassert comparison outcomes and diagnostics, and R3 to errstat success/failure/recovery sequences with independent copied statuses. The fassert S3 example does not verify its separate R2 mapping; errstat supplies status handling while the arithmetic routine is provided by the driver.

The [kriging and neural-network review](gams-kriging-network.md) connects L13 to GSLIB ordinary kriging against closed-form weights for three covariance models, and K to FKB forward evaluation with independent scalar references and model save/reload checks. The GSLIB L13 driver does not verify its separate E2 mapping; the FKB example does not claim training or approximation quality.

The [lookup services and approximate-functions review](gams-lookup-fastmath.md) connects E3 to lookup-table-fortran locations, columns, resampling and independent copied tables; C4b to fastmath exponentials/logarithms against intrinsic and inverse references; and C2 to reciprocal square roots of known dyadic squares. Observed approximation errors and acceptance tolerances are documented separately. The E3 service driver does not verify lookup-table-fortran's separate E1a mapping.

The [complex circuits and beta-identities review](gams-circuits-beta.md) connects A4 to ECX R/C/L impedances, with driver-composed series RLC and parallel RC circuits; C4 to real sinc/sech series and exponential references; and C7 to beta-function factorial identities. The RPN calculator's C2 cube-root and C10 Bessel mappings remain source-supported for these records.

The [matrix inversion and TVD ODE review](gams-inverse-tvd.md) connects D2 to linalg_fortran inverse/determinant formulas for known triangular factors and row permutations, and I1 to HR-WENO first-/second-/third-order time integration with discrete references and continuous convergence checks. The ODE example uses documented single-step mode and does not verify ordinary interval mode or the separate spatial WENO mapping.

The [quadratic, spline and quadrature review](gams-roots-splines-quadrature.md) connects F1 to fortranlib known-root quadratics, E1 to fortran-utils polynomial values/derivatives on uniform and nonuniform knots, and H2 to SciFortran sampled/adaptive integration with finite, infinite and endpoint-singular closed forms. Checked links preserve the distinction between these procedures and unrelated interpolation, integration or sorting mappings in the same packages.

The [numeric file I/O and bounds-validation review](gams-io-bounds.md) connects N1 to IO-Fortran-Library files checked by independent native readers/writers, and R2 to fortran-error-handler inclusive bounds across integer, real32 and real64 inputs. Exact endpoints and their nearest floating-point neighbors are checked. Returned validation diagnostics do not verify the separate R3 error-triggering/handling mapping.

The [derivative-free optimization and spacing review](gams-optimization-spacing.md) connects G1b to ForTimize Nelder-Mead known minima from multiple starts and R to pointsets arithmetic/geometric grids against real64 formulas. Pointsets' real32 precision and unchanged-array guards are documented. The optimizer result does not verify the separate GradientDescent record or concurrent use of its module-level callbacks.

The [software raster and seeded-distribution review](gams-raster-distributions.md) connects Q to fortran-sdl2 exact pixels before/after PNG export and L6 to rng-fortran seeded replay, geometric norms and broad analytic moment checks. The graphics example runs without a window. Distribution smoke checks do not certify randomness quality or resolve the pinned normal-reseeding cache issue.

The [physical-quantity and zonal-harmonic review](gams-quantities-spherical.md) connects A to quaff SI conversion factors and typed arithmetic, and J to Spherepack scalar transforms checked against known Legendre coefficients and independent coefficient injection. The transform driver does not verify the separate spherical PDE solver mapping.

The [delay-equation and numerical-embedding review](gams-delay-embedding.md) connects I to dde_solver method-of-steps polynomials and exact oscillators, and S to fortran-lua54 numeric results, stack discipline and recovery after expected script errors. The delayed equations retain the broad I assignment; the Lua 5.4 driver does not verify the separate Lua 5.3 package.

The [matrix-root and box-optimization review](gams-matrix-roots-box.md) connects D to NTPoly known principal square/inverse-square roots using one MPI process, and G2 to four QNSTOP interior-minimum checks. Failed face-minimum probes at 500 and 2,000 iterations are retained with their sources and actual results; active-bound accuracy is not claimed. The matrix-root driver does not verify the separate Invert/D2 mapping.

The [oscillator and dispersion review](gams-dispersion.md) connects D4 to 36 libmbd two-oscillator Hamiltonians with closed-form eigenvalues and Z to the DFT-D4 upstream energy reference, all 48 Cartesian gradients and rigid transformations. The checks cover only bare nonperiodic oscillators and the specified two-body molecular fixture; the class links open their matching checked drivers.

The [quadrature-rule and finite-difference review](gams-rules-differences.md) connects H2c to seven Kronrod rules and 155 exact polynomial moments, and H1 to 90 periodic Fourier fixtures with first/second-order refinement checks. The failed Gauss-order-one probe remains documented; neither adaptive integration nor PDE evolution is promoted by these drivers.

The [QR and automatic-differentiation review](gams-qr-autodiff.md) connects D5 to 576 linalg QR factorizations, including rectangular and rank-deficient matrices with free/locked pivots, and H1 to differentia scalar, gradient and dense-Jacobian analytical references. Reused workspaces and two dimension errors are checked. Sibling procedures and the separate forwarddiff alias require their own matching evidence.

The [dense-spectrum review](gams-dense-spectra.md) connects D4a1 to 96 linalg symmetric matrices with prescribed eigenvalues and D6 to 144 rectangular matrices with prescribed singular values. Eigenvector, one-sided SVD, null-space, reconstruction and orthogonality checks are explicit. The repeated high-level fortran-lapack link-size failures are preserved without numerical verification.

The [least-squares and interpolation review](gams-least-interpolation.md) connects D9a1 to 288 linalg solver calls with prescribed solutions, orthogonal residuals and underdetermined minimum-norm references, and E1a to interp1 affine/cubic exactness across four overloads, boundary behavior and shape preservation. Rank-deficient solves, arbitrary nonlinear extrapolation and malformed inputs remain outside this checked scope.

The [RKF45 and QAGS review](gams-rkf-qags.md) connects I1a1a to 24 analytical forward/backward IVP runs and H2a1a1 to 40 finite-interval integrals, including endpoint singularities and oscillatory cancellation. Continuation, invariants, callback state and workspace reuse are checked; error estimates are not promoted to rigorous bounds.

The [user-Jacobian and Newton-method review](gams-jacobian-roots.md) connects G1b1b to 40 MINPACK lmder1 fits with independently known parameters/objectives and checked user Jacobians, and F1b to 288 forsolver calls across analytic, central-difference and complex-step Newton methods. Known answers are checked separately from convergence status and method agreement; no global convergence guarantee is inferred.

The [higher-order AD review](gams-higher-ad.md) connects H1 to 1,575 DNAOAD-FPM complex derivative references through order five and 95 diffstruc polynomial value/derivative references, including 45 Hessian entries. Direction masks and reset behavior are explicit; graph disposal and long-lived memory behavior are outside the verified scope.

The [quadrature-moment and 2D-transform review](gams-moments-nufft2d.md) connects H2c to 191 QDUtilLib exact moments and J1 to 144 NUFFT2D transforms with 22,416 direct coefficient comparisons. Hermite full-function weights, cancellation scaling, both signs, odd/even grids and DC normalization are explicit; other rule families and transform types retain separate scope.

The [iterative least-squares review](gams-iterative-ls.md) connects D9a1 to LSQR and LSMR, each checked on 216 solves across 72 square/tall/wide fixtures with exact minimum-norm answers and prescribed orthogonal residuals. Damping, rank deficiency and large sparse performance remain outside this checked scope.

The [forsvd and foreig spectral review](gams-spectral-wrappers.md) connects D6 to 432 reduced SVD calls and D4a1 to 96 symmetric eigenproblems with prescribed spectra, scalar residuals and orthogonality checks. The SVD consumer copies its input; foreig checks upper-triangle selection and input preservation. Neither wrapper exposes LAPACK status, and other methods retain separate scope.

The [regridding and RK45 review](gams-regrid-rk45.md) connects E1a to REGRIDPACK linear/cubic polynomial exactness, piecewise-linear values, eight diagnostics and recovery, and I1a1a to diffeq analytical solutions at 408 requested times in both directions. Multidimensional interpolation, stiff integration and event detection retain separate scope.

The [FITPACK polynomial review](gams-fitpack-polynomials.md) connects E1a to 11,016 value references and H1 to 44,352 derivative/value references from linear, cubic and quintic interpolating splines. Scalar/vector overloads, reversed source data, object reset and destruction are checked; differentiation of arbitrary callbacks and positive smoothing are outside this scope.

The [diagonal-solve and harmonic-response review](gams-diagonal-response.md) connects D2 to 180 SpecialMatrices diagonal solves and I1 to 24 dynamics response fixtures for uncoupled unit-mass systems. Failed non-unit-mass and coupled response probes are preserved; the successful driver does not verify those configurations.

The [ranking and magic-square review](gams-ranking-magic.md) connects N6 to 23,988 ORDERPACK typed ranking calls with independent sorted-value references, and D1 to 124 M_LA magic-square constructions with exact permutation and line-sum checks. Tie stability, NaN ordering and unrelated matrix utilities are outside this scope.

The [WGS84 and forlab review](gams-geodesy-forlab.md) connects P to 680 maptran3d conversions checked against ellipsoid geometry, and D9a1 to 108 single-precision forlab overdetermined solves with prescribed solutions and residuals. A failed wide-system probe is preserved; inverse poles and underdetermined solves are not verified.

The [user-Jacobian and rigid-transform review](gams-jacobian-transforms.md) connects G1b1b to 24 nonlin exact exponential fits with explicit step bound 1, and D1 to fglm vector components and 72 transformation compositions. Default-bound and nonzero-residual false-convergence probes are preserved; finite-difference least-squares mode is not verified.

The [expression-evaluation review](gams-expression-evaluation.md) connects N3 to Fortran Function Parser and M_calculator on 280 shared arithmetic references each, explicit error reporting and successful recovery. Variable input/state behavior is checked; neither driver establishes symbolic-algebra capability or complete grammar coverage.

The [decimal-conversion and Delaunay review](gams-conversion-triangulation.md) connects A6 to 244 str2real conversions with arithmetic and formatted-READ references, and P to 36 GEOMPACK triangulations with independent empty-circle, area, edge and neighbor checks. Malformed numeric input and degenerate point sets are outside this scope.

The [graph-ordering and sorting review](gams-graph-sorting.md) connects P to 4,102 DAGLIB sorts with cycle rejection and recovery, and N6 to 23,988 coretran calls using explicit stable=true. Failed unstable-sorting and nearest-neighbor probes are preserved; sorting evidence does not promote spatial search.

The [nearest-neighbor and sparse-product review](gams-neighbors-sparse.md) connects N5 to 96,072 fortran-flann returned neighbors checked against direct distances, and D1b4 to 1,500 sparse_fortran COO/CSR products checked against scalar dense references. Tied indices, rectangular matrices, transpose products and empty storage segments are included; approximate searches and incremental sparse edits remain unverified.

The [automatic differentiation and adaptive-IVP review](gams-adaptive-ad.md) connects H1 to 1,749 forwarddiff scalar calls with analytic slopes, and I1a1a to 96 FLINT integrations with four methods and independent endpoint/dense-output references. Forward/backward integration, scalar/vector tolerances and repeated interpolation are checked; higher-order derivatives, stiff systems and events remain unverified.

The [LU and orbital-conversion review](gams-lu-orbits.md) connects D2a1 to 384 linalg vector/matrix solves, independent pivot/factor checks and eight singular diagnostics, and P to 864 Fortran Astrodynamics Toolkit conic-state conversions with Cartesian references and physical invariants. Complex LU, inverse orbital conversion, near-singular conventions and propagation remain outside this checked scope.

The [DAE and FFT-plan review](gams-dae-fft.md) connects I1a2 to 96 DASKR trajectories with closed-form states/derivatives, algebraic constraints and continued BDF history, and J1a2 to 672 NAFPack FFT calls checked against direct sums. Numerical/user Jacobians, repeated plans and forward/backward polynomial DAEs are included; Krylov methods, inconsistent initial data, inverse FFTs and other radices remain unverified.

The [partial-SVD and Laplace-kernel review](gams-propack-fmm.md) connects D6 to 108 historical PROPACK calls with prescribed leading triplets, two-sided residuals and orthogonality, and D1 to 120 FMM2D charge-potential calls checked by direct sums. Wide/tall operators, clustered sources and cancelling charges are included; restarted SVD, source self-potentials and complete PDE solves remain unverified.

The [GMRES and SPD-inverse review](gams-gmres-inverse.md) connects D2 to 288 LightKrylov solves with manufactured solutions, true residuals and actual restart cycles, and 48 one-process NTPoly inversions with analytic spectra and two-sided identity checks. Transpose solves and nonzero initial guesses are included; preconditioners, singular systems and distributed scaling remain unverified. Native diagnostics are retained in the saved proof.

The [polynomial-calculus and periodic-distance review](gams-periodic-calculus.md) connects H1 to 24,354 Formal derivative references, analytic integrals and conservation checks, and P to 2,520 RAFFLE distance references from independent image enumeration in orthogonal cells. A failed skew-cell probe is preserved; neither the geometry proof nor the calculus proof verifies a complete PDE solver.

The [expression and sky-coordinate review](gams-expressions-sky.md) connects N3 to 16,464 FEQParse scalar/batch formula references with reordered variables, and P to 1,296 astro-fortran Galactic/ICRS directions checked against independent elementary rotations. Poles and longitude wraps are included; malformed expressions, symbolic algebra and time-dependent astrometry remain unverified.

The [unsigned arithmetic and bitset review](gams-unsigned-bitsets.md) connects A1 to 17,307 exact uint-fortran checks for 8/16/32-bit values, and N2 to 37,760 ORBS binary-string references through 129 bits. Modular sums/differences, comparisons, logical operators and shifts are included; multiplication, uint64 and mixed-width bitsets remain unverified.

The [sparse-system and advection review](gams-sparse-advection.md) connects D2 to 216 HeatFlow BiCG solves with manufactured answers and independent residuals, and I2 to 72 HR-WENO k=3 periodic-advection problems with 21,504 analytic cell-average references and conservation checks. A k=2 accuracy-threshold probe is preserved without claiming an upstream defect; full HeatFlow evolution and nonlinear advection remain unverified.

The [matrix-product and graph-partition review](gams-products-partitions.md) connects D1 to 576 ForMatmul matrix/matrix-vector calls with scalar references, and P to 108 METIS k-way partitions with exact weighted-cut checks. Existing transpose-flag failures and a new Fortran/C option-index mismatch are documented; heuristic optimality and distributed products remain unverified.

The [multidimensional Fourier review](gams-multidimensional-fft.md) connects J1 to direct-sum checked 2-D dtFFT and 3-D 2DECOMP&FFT transforms, with independent inverse inputs, axis-dependent fixtures and Parseval checks. A dtFFT destroyed-plan recreation failure is preserved; one-process results do not verify distributed execution or narrower univariate transform classes.

The [sparse-update and symmetric-spectrum review](gams-sparse-spectra.md) connects D2a4 to 384 LUSOL normal/transpose solves before and after single column replacements, and D4a1 to 384 ScaLAPACKFX eigensystems with prescribed spectra and poisoned unused triangles. A repeated-update accuracy probe is preserved; rank changes and distributed eigensystems remain unverified.

The [constrained-projection and L-BFGS review](gams-projection-lbfgs.md) connects G2h3b1b to 48 PSQP ball-and-plane projections with analytic optima/multipliers, and G1b1b to 108 SEISCOPE SPD quadratics with known minimizers and independent real64 endpoint audits. User gradients, feasibility and convergence statuses are checked; nonconvex constraints and nonquadratic convergence remain unverified.

The [fixed-gradient and particle-swarm review](gams-gradient-swarm.md) connects G1b to 240 ForTimize analytic quadratic trajectories, and G2i to 12 Opti shifted-Rastrigin searches with known global minima. The gradient routine returns a preceding-iterate objective, which the driver verifies and recomputes; seeded swarm successes do not establish general global convergence or cross-compiler RNG reproducibility.

The [halfspace-projection and affine-training review](gams-projection-training.md) connects G2h3b1b to 48 Optgra weighted projections with analytic solutions and multipliers, and G1b to 24 neural-fortran network%train runs with 3,168 real64 affine prediction references. Convergence status, feasibility and independent training loss are checked; nonlinear constraints and nonlinear networks remain unverified.

The [feasible-directions, annealing and fitting review](gams-directions-fitting.md) connects G2h3b1b to 48 CONMIN nonlinear ball projections with analytic KKT checks, and G2i to six two-dimensional simulated-annealing searches with known global minima. Failed three-dimensional and multi-loop probes are retained. A Coulomb parameter fit returned twice the known coefficient; its L8 mapping remains unverified, with an exact reproducer for follow-up.

The [KISS and random-spacing review](gams-random-references.md) connects L6a21 to seven rndgen-fortran streams checked against independent integer vectors and checksums, and L6 to 63 pointsets spacing fixtures plus 60,000 samples of the analytic three-point law. The random_spacing mapping is broadened from L6a21 because normalized uniform increments do not give uniform order statistics; statistical quality and cross-compiler RNG behavior remain unverified.

The [tangent-flow and block-product review](gams-tangents-blocks.md) connects I1 to 540 FATODE forward/backward integrations with 8,640 analytic tangent entries, and D1 to 32 DBCSR products with irregular blocks, all N/T pairs, scaled accumulation and scalar-loop references. The larger DBCSR Cartesian draft hit the output limit on native diagnostics and is not counted; stiff integrators and distributed sparse products remain unverified.

The [radial-state and dense-layer review](gams-radial-dense.md) connects I1 to 36 dftatom Coulomb eigenproblems with 270,072 analytic radial-function/derivative entries and independent moments, and K to 192 Athena fixed layers with four activations and 4,928 scalar output references. A temporary-input ownership error is preserved separately; relativistic modes, training and dataset approximation quality remain unverified.

The [Fiats and ennuf inference review](gams-inference-pairs.md) connects K to 48 Fiats multilayer networks with scalar references and 2,640 ennuf pipeline batches with 35,200 layer-output references, plus an 81-point closed-form check of the existing generated model across all four ReLU regions. Fixed function evaluation is checked; training, model conversion and approximation quality on datasets remain unverified.

The [checked spherical Helmholtz and uniform-stream drivers](gams-helmholtz-streams.md) cover nonresonant spherical PDEs and exact seeded bitstream/jump behavior. Statistical quality, resonant shifts and the known normal-cache reseeding defect remain outside these checks.

The [checked LuGre and FTorch drivers](gams-friction-torch.md) verify public constitutive state integration and fixed affine tensor inference. Private fitting callbacks, parameter fitting, nonlinear networks and training remain unverified.

The [checked Pareto-segment and Jacobi/DIIS drivers](gams-pareto-diis.md) retain failed small-history and uniform-archive-accuracy probes alongside the successful scoped checks. They verify a near-front subset and default-history linear solves, without claiming either stronger behavior is fixed.

The [ten checked data-handling drivers](gams-data-ten.md) add exact container, text, sorting/searching and register-conversion references, with per-driver limits. All use existing cached libraries.

The [ten configuration, state and reference drivers](gams-state-ten.md) include checked storage/configuration, SQL transactions, expressions and SI photon calculations, with retained failed probes and explicit scope limits.

The [ten structured-data and interoperability drivers](gams-interop-ten.md) check JSON/YAML values, NPY headers and payloads, container states, diagnostic filtering, Linux file operations and Lua/Python bindings, with retained consumer corrections and explicit limits.

The [ten storage, configuration and binding drivers](gams-storage-ten.md) check graphs, resource lifetimes, NetCDF metadata/indexing, regex languages, transactions, configuration, containers, logging and offline URL parsing with independent references.

The [ten command-line, testing and workflow drivers](gams-workflows-ten.md) check typed command-line options, native NAMELIST conversion, assertion outcomes, Tcl, pipes, file operations, vector/list state and scripted history edits.

The [ten statistical, matrix, quadrature and service drivers](gams-statistics-services-ten.md) add checked stdlib median/covariance/correlation/moment/determinant/inverse/trapezoidal procedures, native timer brackets, enabled assertion enforcement and one-process MPI identities. The random-helper requested-bound failure remains explicitly unverified with its reproducer retained.

The [ten stdlib factorization, matrix and quadrature drivers](gams-factorization-rules-ten.md) check QR, Cholesky, symmetric eigensystems, SVD, rank-one pseudoinverses, matrix norms/exponentials, Simpson integration and Gauss/Lobatto rules against defining equations and independent analytic references.

The [ten stdlib special-function drivers](gams-special-functions-ten.md) check Legendre values/derivatives, complex gamma/log-gamma, log-factorial, incomplete/regularized gamma and beta-family functions against independent polynomials, sums, products and high-precision constants.

The [ten stdlib linear-system and spectral drivers](gams-systems-spectra-ten.md) add direct/factored SPD solves, constrained/weighted least squares, nonsymmetric eigenproblems, Schur form, generalized eigenvalues and CG/PCG/BiCGSTAB kernels. Retained failures distinguish unsupported vector/wrapper interfaces from checked ones.

The [ten stdlib probability-distribution drivers](gams-distribution-ten.md) check uniform, normal, exponential, gamma and beta PDFs/CDFs against independent high-precision constants, interval geometry and polynomial sums/products, including support boundaries and parameter transformations.

The [ten checked ordering and array-algebra drivers](gams-pca-ordering-ten.md) cover selection, index/payload sorting, unique sets, differences, vector/tensor/outer products and diagonals. A separate stdlib PCA probe hit the executable-size limit and remains source-supported, with exact failure notes retained.

The [ten activation and normalization drivers](gams-activations-ten.md) check scalar activation values, independently differentiated references, and stable softmax/log-softmax normalization. Failed GELU/SiLU gradients are retained separately and are excluded from the published value-only examples.

Grid and numerical utility drivers: [review and actual results](gams-grids-ten.md).
