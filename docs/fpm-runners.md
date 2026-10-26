# FPM from Python and the local browser

Both command-line runners accept an explicit `--fpm` mode. Ordinary source-file commands retain their existing behavior. FPM mode requires Python 3.11 or later; the clients and local server use the standard library.

## Hosted packages: xplayground_run.py

The hosted runner submits a public GitHub FPM package to the separate package service:

```text
python xplayground_run.py --fpm https://github.com/jacobwilliams/PCHIP --action build
python xplayground_run.py --fpm https://github.com/jacobwilliams/PCHIP --action test --compiler ifx
python xplayground_run.py --fpm https://github.com/jacobwilliams/PCHIP --main main.f90 --compilers gfortran ifx flang --diff numeric
```

Without `--main`, Build, Run, and Test operate on the downloaded package. `--main FILE` reads a local UTF-8 main program and creates a consumer project using the downloaded package as its dependency; it supports Build and Run. Supply `--revision BRANCH_OR_TAG_OR_COMMIT` to choose a revision. The service records resolved commits. Omitting the revision uses the repository's default HEAD.

`--target NAME` selects a package application or test. Run without a target builds and either runs the only application or reports available application names. Test without a target runs all tests. `--stdin-file FILE` supplies UTF-8 standard input. `--compile-only` aliases `--action build`. Targets and stdin do not apply to Build, and target selection does not apply to a custom main program.

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

## Local browser page

Start the server at the package directory or a parent workspace:

```text
python xfortran_serve.py --workspace C:\fortran\mypackage --fpm
python xfortran_serve.py --workspace C:\fortran --fpm --fpm-path C:\tools\fpm.exe
```

Use the full session URL printed by the server. The ordinary local playground also links to **Local FPM packages**. The package page discovers projects within the workspace, excluding hidden/build directories; you can enter a workspace-relative directory yourself. Use `.` for the workspace root. A package directory cannot escape that workspace.

The page offers package/custom-main workflows, single- or multi-compiler operation, Build/Run/Test, optional targets, debug/release profiles, stdin text/file loading, configurable timeouts, Stop, and stop-on-first-failure. It uses the same local runner as `xfortran_run.py`. Only one source-file or FPM job runs through this server at a time. The compiler environment and executable overrides are inherited from the server's launch terminal.

The main-program editor provides syntax highlighting, configurable indentation (default three spaces), local file loading, Format via installed fprettify, and Check via installed Fortitude. Results show every selected compiler's timings, commands, stdout/stderr, and available targets. Copy all results and optional exact/whitespace/numeric output comparisons submit no extra jobs. Text and source edits remain in the browser until submitted; the editor does not overwrite package source files.

The local API retains the existing loopback Host/Origin/session-token checks. The session fragment is carried between local pages, while session storage supports reloads. Unrelated websites cannot submit jobs through the browser. The local tools themselves run with your normal permissions, so use packages you trust.

To copy the local tools into a separate project, take `xfortran_run.py`, `xfortran_serve.py`, `fortran_fpm.py`, `fpm_runner.py`, `fortran_output_diff.py`, `fortran_plot.py`, `vendor/pyplot-fortran/`, and `local_site/` together. No hosted backend modules or Modal SDK are needed for local FPM operation. Standalone hosted FPM use additionally needs `xplayground_run.py`, `fpm_sources.py`, `fpm_compilers.py`, and a package-service configuration or `--service-url`. See [plotting](plotting.md) for PNG examples, required local Python packages, and `--plot-dir`.

For package options, run `python xfortran_run.py --fpm . --help` or `python xplayground_run.py --fpm URL --help`.
