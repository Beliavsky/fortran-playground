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
