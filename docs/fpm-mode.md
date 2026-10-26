# FPM package playground

The separate [FPM page](https://beliavsky.github.io/fortran-playground/fpm/) uses **GNU Fortran 16.2.0** and **FPM 0.12.0**. It requires its own service deployment; publishing the page alone does not start that service.

## Using a package

Select a starter example, or enter a public GitHub repository URL with an `fpm.toml` at its root. Enter a branch, tag, or commit separately, or leave the revision blank for the repository's default HEAD. Each repository is resolved to a commit, and results show all downloaded repositories, commit IDs, build commands, diagnostics, and output.

Choose **My main program** to edit a program that uses the package's modules. **Compile and Run** creates a temporary FPM consumer project with the downloaded library as a path dependency. **Build only** compiles without executing the main program. The five starter examples come from the audited programs in [fpm-feasibility/demos](fpm-feasibility/demos); `xfpm_examples.py` regenerates their page catalog when the site is built.

Choose **Package's own programs and tests** to work with the repository itself:

| Action | Commands and behavior |
| --- | --- |
| Build only | `fpm build`: compile the package's library and application targets. |
| Compile and Run | Build, then `fpm run`: run the sole application, or the named target. |
| Test | `fpm build --tests`, then `fpm test`: run all tests or the named test. |

Every command uses `--profile debug --compiler gfortran --no-prune`. Test compilation gets the build allowance; executing the entire selected test suite gets one shared run allowance. Run/Test accept an optional target name. If Run finds several applications, it lists their names without running them; choose a name in the Target field and submit again. This second submission also builds from scratch. Library-only packages can use Build or a custom main program. Running `example/` targets and passing command-line arguments are outside this first version.

Standard input is supplied from the optional text box; there is no interactive terminal. Copy results preserves the captured output, diagnostics, timings, and resolved commits. Loading an example never submits a job automatically.

## Supported dependencies and bounds

The preparation service downloads sources as data and rewrites supported dependencies to staged relative paths. It never builds or executes downloaded code. Compilation, optional FPM build hooks, applications, and tests run only inside the isolated execution sandbox.

- Public HTTPS GitHub repository URLs only; no credentials, private repositories, arbitrary download hosts, submodules, or Git LFS fetching.
- GitHub `git` dependencies, with optional `branch`, `tag`, or `rev`, and path dependencies contained within the same repository. Transitive library dependencies and target-specific dependency tables are resolved too. Package workflow retains development dependencies; consumer workflow omits them.
- Registry dependencies and metapackages are not supported yet. Packages needing unavailable external libraries/tools, MPI, graphical interfaces, or downloads during a build may fail. A repository URL does not establish compatibility.
- At most 12 downloaded repositories, 32 dependency manifests, 32 MiB combined downloads, and a prepared source tree of 64 MiB / 20000 entries. Each archive has a 16 MiB compressed / 64 MiB expanded / 10000-entry bound; the prepared compressed bundle is at most 16 MiB. Links, special files, duplicate archive paths, and paths escaping the extraction directory are rejected.
- Preparation has a 60-second download deadline. The sandbox has a 250-second lifetime, a 180-second build command limit, and a 30-second run/test command limit. A job can also stop at the coordinator's 360-second limit.
- Sandbox CPU request/limit: 0.5/1 CPU; memory request/limit: 512/1024 MiB. Execution runs as UID/GID 65534 with no network, secrets, persistent volumes, or OIDC identity. Core dumps are disabled, files are limited to 16 MiB each, and open files/processes to 128. Each stage captures at most 200000 bytes of combined stdout/stderr.

The callback restriction described in the [feasibility audit](fpm-feasibility/README.md#callback-limitation-found) still applies: some internal-procedure callbacks crash in this sandbox. The quadrature and roots starter programs use the working module-callback / object-oriented approaches.

## Independent hosting on Modal

This service lives in this repository and does not require the Python-to-Fortran project or its service. Create a Modal account and authenticate an environment with `requirements-fpm.txt` installed. For example, from the repository root on Windows:

```powershell
python -m venv .venv-fpm
.\.venv-fpm\Scripts\python.exe -m pip install -r requirements-fpm.txt
.\.venv-fpm\Scripts\python.exe -m modal setup
.\.venv-fpm\Scripts\python.exe -X utf8 xdeploy_fpm.py
```

On Linux/macOS, create and activate a virtual environment, install the same requirements, authenticate with `python -m modal setup`, and run `python xdeploy_fpm.py`. An existing authenticated environment with Modal 1.6.0 can also be used.

`xdeploy_fpm.py` first builds and publishes the immutable GNU/FPM sandbox image, with a verified FPM binary checksum. It then deploys the separate `fortran-playground-fpm` app. Image construction happens during deployment, not during user submissions. Wait for the final successful deployment message and copy the URL of its `api` function into [site/fpm/service.json](../site/fpm/service.json):

```json
{"url": "https://YOUR-WORKSPACE--fortran-playground-fpm-api.modal.run"}
```

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
```

This creates an ephemeral app, not a production API deployment. It exercises the five starter programs, package build/test/run workflows, target discovery/selection, standard input, compilation failure, output limits, and upstream datetime/PCHIP/toml-f test suites. It also runs the preparation/coordinator path through completion and cancellation. It writes [fpm-validation.json](fpm-validation.json) with the results. The live check currently requires `tomli-w` in the invoking environment. Downloading mutable dependency branches may resolve to newer commits on a later verification run; the report records the resolved commits.
