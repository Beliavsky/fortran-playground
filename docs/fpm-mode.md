# FPM package playground

The separate [FPM page](https://beliavsky.github.io/fortran-playground/fpm/) uses **FPM 0.12.0**, with **GNU Fortran 16.2.0** as the default. The Compiler selector also supports **GNU Fortran 17 experimental (2026-10-18)**, **Intel ifx 2025.3.3**, and **LLVM Flang 23.1.5** when their separate images have been built and verified by the service. It requires its own service deployment; publishing the page alone does not start that service.

The page enables only compilers advertised by the service. Changing compilers clears target suggestions; it does not submit a job. Old pages continue using GNU 16 when no compiler is specified. The updated page also works with an older GNU-only API. Each submission uses a fresh sandbox. Verified [precompiled GNU 16 packages](fpm-precompiled.md) can reuse their libraries for a custom main program; other submissions build the whole dependency tree. `.mod` files and libraries are never shared across compilers. LFortran and ofort are not included in this package interface.

## Using a package

For Python clients and a local browser analog, see [FPM runners and the local package page](fpm-runners.md). The hosted runner uses this package service; local operations use installed FPM and compilers.

Select a starter example, or enter a public GitHub repository URL with an `fpm.toml` at its root. Enter a branch, tag, or commit separately, or leave the revision blank for the repository's default HEAD. Each repository is resolved to a commit, and results show all downloaded repositories, commit IDs, build commands, diagnostics, and output.

Links such as [`?package=fortran-lapack`](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lapack) select a catalog package and load its example when loading is available, without submitting a job. Unknown IDs show a message. The `package` parameter selects from the curated collection and takes precedence over `collection`. These links also work in the main local FPM interface and are included in the [portable catalog export](catalog-export.md).

The **Collection** menu offers Selected and Translated R packages. All is currently disabled; its retained functionality is documented below for future restoration:

- **Selected Fortran packages** (default): the curated catalog, with pinned revisions, example main programs, and verified GNU 16 libraries where deployed. See [the selected catalog and build instructions](fpm-precompiled.md).
- **All Fortran packages** (disabled): the [Fortran packages list](https://beliavsky.github.io/Fortran-packages-list/), plus the selected catalog. Packages have descriptions, categories, GitHub owners, topics where available, and clickable source links. Selected entries retain their pins and examples. Other entries load the package's own workflow with **Build only** selected and use its current default branch. Choose Build, Run, Run examples, or Test, or switch to My main program. New entries build from scratch; no additional packages are precompiled.
- **Translated R packages**: the separate experimental translated collection.

"All" refers to the source list, rather than every Fortran project. A root `fpm.toml` was checked at catalog refresh time; this is not a successful-build guarantee. Entries with missing, invalid, or unverified manifests remain browsable, with **Load package** disabled and an explanation. Packages may require unavailable dependencies or exceed hosted service limits. The full and translated catalogs download only when requested, and browsing never submits compilation jobs. Use `?collection=translated-r` to open that collection directly. While All is disabled, old `?collection=all` links open Selected. See [catalog maintenance](fpm-discovery.md) for refresh commands.

Selecting a curated entry reuses its precompiled library when you submit a custom main with GNU 16 and the pinned revision. Local execution always builds from scratch.

A single click selects a package for review. Double-click a package in the selector or matching search results to select it and **Load package**, including its example main when available. The Load package button remains available for keyboard and touch use. Loading never compiles or runs a program, and unavailable packages cannot be loaded by double-clicking.

Choose **My main program** to edit a program that uses the package's modules. **Compile and Run** creates a temporary FPM consumer project with the downloaded library as a path dependency. **Build only** compiles without executing the main program. The five starter examples come from the audited programs in [fpm-feasibility/demos](fpm-feasibility/demos); `xfpm_examples.py` regenerates their page catalog when the site is built.

Choose **Package's own programs and tests** to work with the repository itself:

| Action | Commands and behavior |
| --- | --- |
| Build only | `fpm build`: compile the package's library and application targets. |
| Compile and Run | Build, then `fpm run`: run the sole application, or the named target. |
| Run examples | Build, then fpm run --example: run the sole example, or selected names/patterns. |
| Test | `fpm build --tests`, then `fpm test`: run all tests or the named test. |

Every command uses `--profile debug --no-prune`, with an explicit compiler executable and GNU C/C++ compilers. GNU 17 uses a `gfortran` shim selecting the pinned snapshot; Intel uses an `ifx` wrapper that initializes its environment. LLVM Flang uses the name `flang-new` so FPM 0.12 selects its LLVM flags rather than classic-Flang flags. Test compilation gets the build allowance; executing the entire selected test suite gets one shared run allowance. Run/Test accept target lists separated by spaces or commas, with `*` and `?` patterns; quotes around patterns are optional in the browser. For example, `demo_*`, `"demo_*"`, or `first second`. Matches run together in one FPM invocation and share the existing 30-second total run/test allowance and the supplied stdin. If Run finds several applications and no targets were supplied, it lists their names without running them; choose names or patterns in the Targets field and submit again. This second submission also builds from scratch. Library-only packages can use Build or a custom main program. Run examples selects FPM example targets using fpm run --example. Applications and examples are separate categories. Passing command-line arguments remains outside this version.

**Find a package** searches names, GitHub owners, descriptions, categories, keywords, and topics in the selected collection and category. Matching packages appear as clickable results below the search field, and a unique match is selected automatically without loading code or submitting a job. When no packages match, use **Search all categories** or the button to search another collection.

**GAMS class** filters selected packages by the [NIST mathematical software classification](https://gams.nist.gov/cgi-bin/serve.cgi). All 20 top-level classes are available, such as **D — Linear Algebra**, **G — Optimization**, and **I — Differential and integral equations**. Selecting a parent with published children reveals a **Subclass** menu: for example, **D2 — Solution of systems of linear equations**, **G1 — Unconstrained**, **G2 — Constrained**, or **L6 — Random number generation**. The saved hierarchy includes all 96 immediate subclasses. A parent includes all packages classified under it, while a subclass requires an explicit assignment; a broad parent assignment alone is insufficient. A package may appear under several classes. Codes such as C1/C10 and L1/L10 are siblings and are matched separately.

The filter combines with Category, text search, topic source, and sorting. Use **All subclasses** to return to the parent's full set or **All classes** to clear both filters. Explicit searches such as `GAMS D` or `GAMS: L6` use the same hierarchy. Ordinary text searches also include class descriptions. GitHub-only topics do not disable GAMS matching. Selecting a package shows links to its NIST class definitions.

The [numerical package review](gams-numerical.md) covers the selected numerical, statistical, geometry, and supporting packages. Detailed searches include `GAMS I1a1a` for nonstiff one-step initial-value methods, `GAMS I1a2` for stiff/DAE methods, `GAMS G2h1a2` for smooth bound-constrained optimization with user gradients, and `GAMS L6a21` for uniform random numbers. Generic APIs retain broader classifications where configurations differ. Package details link to the reviewed procedures; the portable catalog export carries their source evidence and coverage notes. Source review does not mean that every author example has been tested in the sandbox.

All selected packages have parent classifications; 140 also have immediate-subclass assignments. Broader assignments are retained when no appropriate immediate subclass is available or more review is needed. The translated R collection hides the filters and switching collections clears them; the retained All collection inherits classifications only for selected packages. Review the [package assignments, qualifications, example links, and class counts](fpm-gams.md). Assignments are maintained separately from topics in `fpm_catalog/gams.json`. The [G1 optimization pilot](gams-g1.md) adds G1a (Univariate) and G1b (Multivariate), 11 source-reviewed procedure mappings in seven packages, and three drivers adapted from author examples and verified on hosted GNU Fortran 16.2.0. Search by these codes or procedure names such as lmdif1. Package details link to pinned procedures and offer matching driver load buttons; the example menu also contains the drivers. Links with ?package=minpack&example=gams-minpack-bard load a driver without running it. Comparative benchmarks remain future work. Filtering is local to the browser and never submits compilation jobs. The hosted and main local pages share these controls; no hosted service redeployment is required.

**Sort by** defaults to **Name**, alphabetically, in both the dropdown and search results. Choose **GitHub stars** for descending saved repository star counts, with alphabetical ties and missing counts last. Counts and their refresh date appear when using this order. Search buttons show the first 20 matches in the selected order; the dropdown contains every match. Sorting preserves the current selection and never submits a job or contacts GitHub. The translated R collection uses name sorting because its packages share one repository. Stars indicate popularity, separately from build verification. See [refreshing topics and stars](fpm-precompiled.md#refresh-github-topics-and-stars) for maintenance.

The selected and full collections search saved **GitHub topics** and **playground topics** by default. Our topics supplement inconsistent or missing repository labels with common terms such as `ode`, `sparse-matrices`, and `least-squares`. Choose **Topics: GitHub only** to exclude our additions from topic matching; names, owners, descriptions, categories, and keywords remain searchable. The two topic sources are stored and displayed separately. Review all selected packages in [Playground topics by package](fpm-package-topics.md).

For example, `adams-bashforth` or `adams bashforth` finds DVODE through its GitHub topics. Selecting a package displays the enabled topic sources as clickable labels, with descriptive GitHub topics ahead of generic labels such as `fortran`. Clicking a topic searches the current collection and clears the category filter; it does not load code or submit a job. Packages without topics remain searchable by their other metadata. Translated R packages use their individual keywords and categories rather than sharing the same repository-wide topics. Topic metadata is stored with the site, so searching does not contact GitHub or the compilation service.

**Preprocess** enables compiler preprocessing alongside FPM's debug profile. It requires the updated backend and uses a clean build. Discovered applications, examples, and compiled tests appear in action buttons and a target menu; choosing one never submits a job. Choose Test to build and discover test targets. New discovery entries without supplied main programs start with **Build only**. See the [20-package compatibility audit](fpm-discovery-audit.md) for tested revisions and verified fixes.

Standard input is supplied from the optional text box; there is no interactive terminal. **Program output only** is enabled by default in both the hosted and main local FPM pages. Successful executions show program output; successful builds without execution show a brief confirmation. Failures and target-selection messages always show the full report. **Show build details** reveals retained commands, diagnostics, timings, and resolved commits without rerunning. Uncheck Program output only to always show that report; this preference is saved in your browser. **Copy results** copies the displayed view. Loading an example never submits a job automatically.

## Supported dependencies and bounds

The preparation service downloads sources as data and rewrites supported dependencies to staged relative paths. It never builds or executes downloaded code. Compilation, optional FPM build hooks, applications, and tests run only inside the isolated execution sandbox.

- Public HTTPS GitHub repository URLs only; no credentials, private repositories, arbitrary download hosts, submodules, or Git LFS fetching.
- GitHub `git` dependencies, with optional `branch`, `tag`, or `rev`, and path dependencies contained within the same repository. Transitive library dependencies and target-specific dependency tables are resolved too. Package workflow retains development dependencies; consumer workflow omits them.
- OpenMP and BLAS metapackages (`openmp = "*"`, `blas = "*"`) are retained for offline FPM discovery. Clean GNU 16/17 builds provide BLAS/LAPACK/OpenBLAS libraries. Registry dependencies and other metapackages, including stdlib and HDF5, remain unsupported. Packages needing unavailable external libraries/tools, MPI, graphical interfaces, or downloads during a build may fail. A repository URL does not establish compatibility.
- At most 12 downloaded repositories, 32 dependency manifests, 32 MiB combined downloads, and a prepared source tree of 64 MiB / 20000 entries. Each archive has a 16 MiB compressed / 64 MiB expanded / 10000-entry bound; the prepared compressed bundle is at most 16 MiB. Links, special files, duplicate archive paths, and paths escaping the extraction directory are rejected.
- Preparation has a 60-second download deadline. The sandbox has a 250-second lifetime, a 180-second build command limit, and a 30-second run/test command limit. A job can also stop at the coordinator's 360-second limit.
- Sandbox CPU request/limit: 0.5/1 CPU; memory request/limit: 512/1024 MiB. Execution runs as UID/GID 65534 with no network, secrets, persistent volumes, or OIDC identity. Core dumps are disabled, files are limited to 16 MiB each, and open files/processes to 128. Each stage captures at most 200000 bytes of combined stdout/stderr.

The callback restriction described in the [feasibility audit](fpm-feasibility/README.md#callback-limitation-found) still applies: some internal-procedure callbacks crash in this sandbox. The quadrature and roots starter programs use the working module-callback / object-oriented approaches.

### Compiler validation and known package limitations

All five starter consumer programs passed with GNU 17, ifx, and LLVM Flang. Package Build, application target selection, stdin, tests, compilation failure handling, output bounds, and coordinator completion/cancellation were also exercised. The upstream datetime-fortran, PCHIP, and toml-f test suites passed with ifx and Flang. GNU 17 passed datetime/PCHIP tests, but hit an internal compiler error (`gfc_get_location_with_offset`) while compiling toml-f's test-drive dependency under FPM's debug flags. The toml-f consumer example still passes with GNU 17. This is retained as a known experimental-compiler failure, with diagnostics shown to the user; no flags or package sources are silently changed to bypass it.

See [the package/worker matrix](fpm-multicompiler-validation.json) and [HTTP validation](fpm-http-validation.json). Supporting a compiler does not guarantee support for every package. The deployment smoke checks additionally exercise a Fortran module calling a C function under Build, Run, and Test, with the normal sandbox bounds.

## Independent hosting on Modal

This service lives in this repository and does not require the Python-to-Fortran project or its service. Create a Modal account and authenticate an environment with `requirements-fpm.txt` installed. For example, from the repository root on Windows:

```powershell
python -m venv .venv-fpm
.\.venv-fpm\Scripts\python.exe -m pip install -r requirements-fpm.txt
.\.venv-fpm\Scripts\python.exe -m modal setup
.\.venv-fpm\Scripts\python.exe -X utf8 xdeploy_fpm.py
```

On Linux/macOS, create and activate a virtual environment, install the same requirements, authenticate with `python -m modal setup`, and run `python xdeploy_fpm.py`. An existing authenticated environment with Modal 1.6.0 can also be used.

`xdeploy_fpm.py` builds separate immutable sandbox images for GNU 16, GNU 17, ifx, and Flang, with a verified FPM binary checksum. Before publishing each image, it verifies mixed C/Fortran package Build, Run, and Test inside network-blocked sandboxes. GNU 16 failure stops deployment; an optional compiler that fails construction or verification is reported and omitted from the advertised compiler list. It then deploys the separate `fortran-playground-fpm` app. No compiler installation or image construction occurs during a user's submission.

Pinned installer scripts are included in `fpm_toolchains/`; a fork needs no files or service from the Python-to-Fortran repository. A first GNU 17 build compiles GCC from source and can take considerably longer than later deployments, which reuse cached compiler layers. To deploy only selected compilers, use `python xdeploy_fpm.py --compilers gfortran ifx`; GNU 16 is always included. Wait for the final successful deployment message and copy the URL of its `api` function into [site/fpm/service.json](../site/fpm/service.json):

```json
{"url": "https://YOUR-WORKSPACE--fortran-playground-fpm-api.modal.run"}
```

Use the exact **Execution API URL** printed by the deployment script, including a regional component such as `.us-east.modal.run` if present. The `https://modal.com/apps/...` link is the management dashboard and cannot be used as the execution endpoint.

The script checks the deployed HTTP health endpoint and browser-origin access before reporting `HTTP health and browser access: PASS`. If deployment succeeds but this check fails, the app exists but is not ready to use; inspect the startup logs with `python -m modal app logs fortran-playground-fpm`. Owner-secret configuration is carried into both container environments so their Modal dependency definitions match the deployment; the secret value remains attached to the API only.

Then commit that configuration and publish the static site using the usual Pages workflow. Until the URL is configured and reachable, the page displays an explanation and disables submission while keeping examples and editing available. After worker changes, rerun `xdeploy_fpm.py`; API-only changes can also use that command, reusing cached image layers.

For a fork, pass your allowed browser origin when deploying:

```powershell
python xdeploy_fpm.py --origins https://YOUR-USERNAME.github.io
```

The defaults also permit the repository's static preview origins, `http://127.0.0.1:8766` and `http://localhost:8766`. An optional `--owner-secret p2f-owner` attaches an existing Modal secret containing `P2F_OWNER_KEY` to the API only. Requests carrying the matching `X-P2F-Owner-Key` bypass public rate/daily limits; no owner control is exposed on the public page, and neither preparation containers nor execution sandboxes receive the secret. Do not place the key in static configuration or URLs.

Other hosting services can implement the same HTTP contract. They must provide equivalent isolation, resource limits, source preparation, admission control, and cancellation. Update the page's `connect-src` CSP as well as its service URL if the host is outside `*.modal.run`.

## Capacity, state, and clean builds

FPM has its own service, runtime image, admission state, and queue. It admits at most two active jobs, limits each public address to 30 submissions per ten minutes, and permits 100 public submissions per UTC day. The API serializes admission updates in one container and persists limits in a Modal Dict. Random 256-bit job identifiers authorize polling/cancellation; results expire after 30 minutes. Cancel requests keep the slot reserved until the coordinator stops. Preparation may finish its current bounded download before cancellation takes effect.

Ordinary playground modes load no FPM code and make no FPM service requests. FPM traffic does not enter their queue or consume their service's usage allowance. Both apps still share the owner's Modal account spending and account-wide capacity limits.

Every request downloads/prepares sources and compiles them in a fresh sandbox. Upstream root build directories and `fpm.lock` files are removed during staging. No compiled package cache is implemented. A later cache must key objects, libraries, and `.mod` files together by exact dependency commits, compiler/version, platform, build settings, and FPM version. It should remain exclusive to this FPM service.

## Verification

Run the ordinary Python and JavaScript suites:

```powershell
python -m unittest discover -s tests
npm test
python xsite.py
```

For live validation with an authenticated Modal environment, run:

```powershell
python -X utf8 xverify_fpm.py
python -X utf8 xverify_fpm.py --compilers gfortran17 ifx flang --report docs/fpm-multicompiler-validation.json
python -X utf8 xverify_fpm_http.py
```

These commands create ephemeral apps, not production API deployments. `xverify_fpm.py` exercises the five starter programs, package build/test/run workflows, target discovery/selection, standard input, compilation failure, output limits, and upstream datetime/PCHIP/toml-f test suites for the requested compilers. It also runs the preparation/coordinator path through completion and cancellation. Its default report is [fpm-validation.json](fpm-validation.json). The specific known GNU 17 internal compiler error described above is recorded as a known failure, with `result.ok` remaining false; other unexpected failures make verification fail.

`xverify_fpm_http.py` verifies and publishes the immutable images, then checks the temporary HTTP API's compiler catalog and submits a starter program with each of the four compilers, polling until completion. It writes [fpm-http-validation.json](fpm-http-validation.json). The live checks require `tomli-w` in the invoking environment. Downloading mutable dependency branches may resolve to newer commits on a later verification run; the package reports record the resolved commits.

A successful build with no program executed is reported as **BUILD PASS — nothing run**, rather than a compilation failure. This includes missing targets and cases where a target selection is still needed.
