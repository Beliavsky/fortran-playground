# FPM from Python and the local browser

Both command-line runners accept an explicit `--fpm` mode. Ordinary source-file commands retain their existing behavior. FPM mode requires Python 3.11 or later; the command-line clients and directory-based local page use the standard library. The local catalog page also requires `tomli-w` for source preparation.

## Hosted packages: xplayground_run.py

The online and local catalog pages include a separate [Translated R packages collection](translated-r-playground.md). The hosted runner accepts `--subdirectory NAME` for a package in that repository; ordinary root-level FPM repositories are unchanged.

The hosted runner submits a public GitHub FPM package to the separate package service:

```text
python xplayground_run.py --fpm https://github.com/jacobwilliams/PCHIP --action build
python xplayground_run.py --fpm https://github.com/jacobwilliams/PCHIP --action test --compiler ifx
python xplayground_run.py --fpm https://github.com/jacobwilliams/PCHIP --main main.f90 --compilers gfortran ifx flang --diff numeric
```

Without `--main`, Build, Run, and Test operate on the downloaded package. `--main FILE` reads a local UTF-8 main program and creates a consumer project using the downloaded package as its dependency; it supports Build and Run. Supply `--revision BRANCH_OR_TAG_OR_COMMIT` to choose a revision. The service records resolved commits. Omitting the revision uses the repository's default HEAD.

`--target "NAME_OR_PATTERN ..."` selects package applications or tests. Names may be separated by spaces or commas; `*` matches any string and `?` matches one character. For example, `--target "demo_* other"` or `--target "first,second"`. Quote patterns/lists in the command shell; quotes are optional inside the browser's Targets box. Matches are expanded against available targets, deduplicated, and passed together to one FPM invocation. A pattern with no match reports available names. Selected programs share the invocation's standard-input stream and one run/test timeout. Run without a target builds and either runs the only application or reports available application names. Test without a target runs all tests. `--stdin-file FILE` supplies UTF-8 standard input. `--compile-only` aliases `--action build`. Targets and stdin do not apply to Build, and target selection does not apply to a custom main program.

The default compiler is GNU 16. The runner checks the package service's advertised compiler list before submitting; additional choices are GNU 17 experimental, ifx, and LLVM Flang when enabled. Selected compilers run successively. Compilation/execution failures do not stop the next compiler unless `--fail-fast` is set. Service, authentication, quota, or connection errors stop further submissions. Every compiler submission counts as a separate job under the package service's limits; the Python client does not bypass them.

The default API origin comes from `site/fpm/service.json`, independently of the ordinary compiler service. Use `--service-url HTTPS_ORIGIN` and `--origin FRONTEND_ORIGIN` for another deployment. Existing owner access is available with `--owner`, reading `P2F_OWNER_KEY` or prompting without echo. Credentials are never included in the output. A GNU-only older FPM API is supported.

`--timeout SECONDS` limits the total client wait per compiler (default 450 seconds); server build/run/resource limits still apply. Interrupting or losing a connection triggers a cancellation request for a known job ID. Submissions are never retried automatically, because a lost response does not establish whether a job was accepted.

## Local packages: xfortran_run.py

Install FPM and the desired compilers, then point the local runner at an existing project directory:

```text
python xfortran_run.py --fpm . --action build
python xfortran_run.py --fpm C:\fortran\mypackage --action test --compilers gfortran ifx flang
python xfortran_run.py --fpm . --target demo --stdin-file input.txt
python xfortran_run.py --fpm . --main main.f90 --compilers gfortran ifx --diff numeric --diff-atol 1e-12
python xfortran_run.py --fpm . --action test --profile release --compile-timeout 0 --run-timeout 0
```

Source URLs and repository downloads are not managed by the local runner. Clone packages yourself. Native FPM resolves dependencies normally, using its cache and network; no Modal service or hosted quota is involved.

Builds run in the package directory and create/update the package's `build` directory as normal. Applications and tests run with your account's permissions. They can read/write files and use the network. For a custom main program, the runner creates a temporary consumer directory under the selected package, with a relative path dependency. The consumer is compiled and run there, then removed, including files its program creates there. Package source files and the original manifest are not overwritten. Use the package workflow when you want its normal project working directory or retained output files.

Local compiler choices are gfortran, gfortran17, ifx, flang, and experimental lfortran. ofort is not supported for FPM builds. Installed compiler/FPM versions determine package compatibility. GNU 17 discovery requires an actual GNU 17 executable. Use `--compiler-path COMPILER=PATH` or `--fpm-path PATH` for executables not found on PATH. Initialize Intel's developer environment in the same terminal before running ifx or starting the server; Windows LLVM Flang also needs the appropriate MSVC linker environment.

Compiler adapters give FPM unambiguous compiler names and avoid its Windows command-path quoting problems. GNU and GNU 17 have distinct adapter names so compiler selections use separate FPM build directories. The LLVM adapter uses `flang-new` for FPM 0.12's LLVM detection. On Windows it removes FPM's unsupported `-fPIC` argument and reports that adaptation in the results; all other compiler arguments are preserved. Compiler binaries remain in their installation directories. Native checks covered GNU/GNU 17, ifx, and LLVM Flang with package Build/Run/Test and custom consumers, including project paths containing spaces. LFortran remains experimental.

The default build timeout is 120 seconds and run/test timeout is 30 seconds. Set either to `0` for unlimited time. Each selected test suite shares one run timeout. `--max-output-mb N` bounds each captured stream (default 4 MiB, maximum 64 MiB). Truncated output is marked and cannot be used for output comparisons. These controls do not create a security sandbox.

## Results and comparisons

Both modes print compiler-labeled results, FPM logs, commands, and a summary with Total, Compile, Run, and Other times in seconds. Build timing includes FPM preparation and compilation; Run/Test timing includes FPM startup and its up-to-date check. Hosted Total additionally includes network, scheduling, and polling overhead. These are not controlled compiler benchmarks.

Use `--terse` to omit versions, project metadata, and individual command/timing headings while retaining FPM logs and diagnostics. `--list` prints the submitted main program and requires `--main`; it does not list an entire package tree.

Output comparison remains optional: `--diff`, `--diff exact`, or `--diff numeric`, with `--diff-atol`, `--diff-rtol`, and `--diff-reference`. It compares captured execution stdout, retaining the original output. Build-only, failed, skipped, timed-out, cancelled, or truncated operations are not comparable. Output differences do not alter the exit code: `0` means all requested operations passed, `1` means an operation failed or was skipped, `2` means a request/configuration/service error, and `130` means interrupted.

## Local FPM playground

The main local package playground uses the same interface, package catalog, examples, source links, downloads, editor and plot display as the hosted FPM page. It executes through the loopback server using installed compilers and FPM, with no Modal account or hosted requests.

```text
python -m pip install tomli-w==1.2.0
python xfortran_serve.py --workspace C:\fortran --fpm
```

Open the full session URL printed by the server. Select a catalog entry or enter a public GitHub repository and optional revision. You can edit a main program using the package or choose the package's own Build, Run or Test action. Standard input and application/test target selection work as on the hosted page. The compiler selector lists discovered local FPM compilers: gfortran, gfortran17, ifx, Flang and LFortran when installed. The default is the installed gfortran, whose actual version is shown; to use GNU 16, put that version on PATH or pass `--compiler-path gfortran=PATH_TO_GFORTRAN16`. `--fpm-path PATH` overrides the FPM executable. Initialize Intel's environment before starting the server when using ifx.

Each submission downloads sources into a fresh temporary directory inside the workspace, compiles from scratch, and removes its source/build tree when finished. There is no persistent precompiled-package directory yet. Catalog consumer jobs use the recorded source/dependency pins, checksums, manifest adaptations and patches. The package's own programs/tests use development dependencies resolved during preparation; they do not reuse the hosted consumer cache. GitHub downloads retain the source preparer's archive/path checks. Local compilation and execution have no hosted timeouts or job quotas; Cancel stops active work. Only one job runs through this server at a time.

Install native libraries such as BLAS, LAPACK or SQLite locally when required; the server does not install them. Catalog recipes with GNU-specific compiler flags require gfortran or gfortran17. Other catalog entries and custom repositories can be tried with the other installed compilers. First local builds of large packages such as stdlib may take several minutes. Plotting requires NumPy and Matplotlib on the local machine.

## Local FPM projects

The secondary **Local FPM projects** page works with existing packages on disk. Open it using the link in the main local playground, or launch it directly:

```text
python xfortran_serve.py --workspace C:\fortran --fpm-projects
```

It discovers package directories within the workspace, excluding hidden/build directories. You can enter a workspace-relative directory yourself; `.` means the workspace root. A package directory cannot escape that workspace. It supports package/custom-main workflows, single- or multi-compiler operation, Build/Run/Test, optional targets, debug/release profiles, stdin text/file loading, configurable timeouts, Stop, and stop-on-first-failure. Existing projects retain their normal FPM build directories, so ordinary FPM incremental builds still apply on this page.

The main-program editor provides syntax highlighting, configurable indentation (default three spaces), local file loading, Format via installed fprettify, and Check via installed Fortitude. Results show every selected compiler's timings, commands, stdout/stderr, and available targets. Copy all results and optional exact/whitespace/numeric output comparisons submit no extra jobs. Text and source edits remain in the browser until submitted; the editor does not overwrite package source files.

Both pages use the same local execution backend as `xfortran_run.py`. The API retains the loopback Host/Origin/session-token checks, and navigation carries the session between local pages. Reloads use per-tab session storage. Local programs run with your normal permissions, so use packages you trust.

## Moving the local tools

For source-file and existing-directory FPM operation, copy `xfortran_run.py`, `xfortran_serve.py`, `fortran_fpm.py`, `fpm_targets.py`, `fpm_runner.py`, `fortran_output_diff.py`, `fortran_plot.py`, `fortran_image.py`, `vendor/pyplot-fortran/`, and `local_site/` together. The main catalog page additionally needs `local_fpm_catalog.py`, `fpm_collections.py`, `fpm_sources.py`, `fpm_compilers.py`, `fpm_catalog_build.py`, `fpm_catalog_patches.py`, `fpm_catalog.json`, and the shared `site/` frontend assets. It does not need the Modal SDK or execution-service modules. The source catalog and frontend assets can be generated in this repository before copying them.

Standalone hosted FPM use additionally needs `xplayground_run.py` and a package-service configuration or `--service-url`. See [plotting](plotting.md) for PNG examples, local Python requirements, and `--plot-dir`.

For package options, run `python xfortran_run.py --fpm . --help` or `python xplayground_run.py --fpm URL --help`.

## Running FPM examples

Use the browser action **Run examples**, or CLI **--action example**, to run FPM example targets with the same name/pattern selection and total timeout as applications. For example:

`	ext
python xplayground_run.py --fpm https://github.com/urbanjost/M_CLI2 --action example --target demo1
python xfortran_run.py --fpm DIRECTORY --action example --target "demo*"
`

Successful compilation with no executed program is displayed as **BUILD PASS — nothing run**. Its machine-readable status is NOT_RUN and the requested operation remains incomplete. Consumer main programs support Build and Run; examples and tests operate on the package itself.

Use `--preprocess` with either Python FPM runner to enable preprocessing alongside the chosen build profile. Hosted use requires the updated backend. Downloaded projects preserve this setting. Standalone local FPM use with this option also needs `fpm_compilers.py`.
