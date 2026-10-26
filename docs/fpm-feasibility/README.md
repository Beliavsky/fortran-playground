# FPM feasibility audit

**Result: five packages passed two clean-build/run trials each under the configured playground resource limits.** This meets the proposed five-package threshold for proceeding with an FPM mode. The audit used short consumer programs that depend on these libraries; it did not run each upstream repository's complete application/example/test suite.

Measured on 2026-10-26 in fresh, disposable Modal gVisor sandboxes. The existing public service was not deployed or changed. This audit is a separate temporary app with no shared production queue or state.

| Package | Demonstration and checked result | Clean build, seconds (two trials) | Run, seconds (two trials) | Maximum build-process RSS, MiB |
| --- | --- | --- | --- | --- |
| [quadrature-fortran](https://github.com/jacobwilliams/quadrature-fortran) | Integrate x² on [0,1], verify 1/3 | 0.429 / 0.534 | 0.019 / 0.024 | 63.4 |
| [roots-fortran](https://github.com/jacobwilliams/roots-fortran) | Brent solver through its object-oriented API, verify √2 | 0.598 / 0.880 | 0.023 / 0.025 | 70.2 |
| [PCHIP](https://github.com/jacobwilliams/PCHIP) | Interpolate linear data, verify an interior value | 2.158 / 0.773 | 0.025 / 0.034 | 68.8 |
| [toml-f](https://github.com/toml-f/toml-f) | Parse TOML and retrieve integer 42 | 2.980 / 3.964 | 0.041 / 0.057 | 79.9 |
| [datetime-fortran](https://github.com/milancurcic/datetime-fortran) | Add two days across leap day, verify 2024-03-01 | 0.788 / 1.109 | 0.022 / 0.026 | 124.1 |

The worst clean build was 3.964 seconds against a 180-second limit, and the worst run was 0.057 seconds against a 30-second limit. Every trial also meets the more conservative 120-second build / 20-second run headroom thresholds. No compiled objects were shared between trials. Maximum scratch usage was about 5 MiB; the largest individual file was about 1.36 MiB, below the sandbox's 16 MiB file-size limit.

RSS comes from GNU `/usr/bin/time` and reflects the largest process in a command's process tree, not aggregate container peak memory. The independent sandbox hard limit was still applied to the entire container.

## Environment and measurement

- The same pinned GNU base image used by the configured backend: GNU Fortran 16.2.0, Debian trixie. Full image digest is in [results.json](results.json).
- FPM 0.12.0 Linux x86-64 release binary, verified against its release checksum. This is an FPM audit image built separately from the production runtime images.
- CPU request/limit 0.5/1.0 CPU, memory request/limit 512/1024 MiB, gVisor, network blocked, no secrets or persistent volumes, OIDC token disabled, unprivileged UID 65534.
- A 250-second sandbox lifetime, 180 seconds for the build command, 30 seconds for the run command, 16 MiB per-file size cap, 128 processes/open files, core dumps disabled. Output was additionally bounded to 200,000 bytes total per stage, stricter than the backend's per-stream capture bound.
- Each dependency is a complete upstream archive pinned to a Git commit, with a recorded archive SHA-256. Package sources/manifests were not patched. The consumer refers to the staged package using an FPM path dependency.
- `fpm build --profile debug --compiler gfortran --no-prune`, followed by `fpm run` with the same options. Debug is FPM's default profile; optimized/release builds were not benchmarked. `--no-prune` prevents the consumer example from obtaining an artificially small result by pruning unused library modules.
- Run timing includes FPM's startup, dependency scan/up-to-date check, and launching the already built program. Every demonstration performs correctness assertions and must emit its own PASS marker.

Package archives were downloaded and validated on the preparation host before creating the network-blocked sandboxes. Their recorded download times (about 0.13–0.28 seconds here) are observations from that host, not guarantees about a future public fetch service. Cloning, dependency preparation, and network variability would need their own limits. These five library dependency graphs need no additional runtime/package dependencies; upstream development/test dependencies are intentionally outside the consumer build.

Image creation and sandbox provisioning are excluded from build/run timing. The CSV separately records client-observed sandbox creation/build-image overhead plus worker execution: about 2–8 seconds in the final trials. The first-ever image preparation is a separate setup expense and was not part of those final timings. A future FPM service should build its compiler/FPM image ahead of requests, rather than build an image for every requested repository.

## Callback limitation found

The initial quadrature and root-finding demos built but segfaulted when using internal-procedure callbacks. Quadrature worked after moving the callback to a module. Roots-fortran's procedural `root_scalar` wrapper still segfaulted with a module callback; its implementation has an internal callback adapter. Using the library's object-oriented `brent_solver` API with a module callback worked in both final trials.

This behavior is consistent with a callback trampoline/executable-stack restriction, but its precise cause was not conclusively diagnosed. It is a sandbox/compiler compatibility issue to document, not excessive compilation cost. No sandbox limits were relaxed to make the tests pass. Earlier failing demonstrations and their logs are retained in [limitations/internal-callbacks](limitations/internal-callbacks) and [limitations/procedural-root-wrapper](limitations/procedural-root-wrapper). Future package examples involving callbacks should be tested under the real sandbox, not merely on a local machine.

## What this establishes

There is sufficient time and memory headroom for an initial **package-as-library** playground: choose a package, enter a short main program that uses it, then build and run. The five demonstrations in [demos](demos) form a working starter collection. This is a deliberately selected feasibility sample, not an estimate of what percentage of the complete package list will work. Arbitrary repositories, large dependency graphs, full test suites, plotting/GUI programs, external libraries, MPI, and release builds remain unassessed.

A repository URL by itself does not guarantee a runnable default target: many useful FPM packages are libraries. A future interface should explicitly distinguish a user-written consumer program from running a named upstream executable/example. Fetching all development dependencies and building/running every upstream test is not required for the validated consumer workflow.

## Keeping ordinary playground modes unaffected

Use a separate package page or lazily loaded interface, a separate prebuilt FPM execution image, and a separate Modal service/queue with its own bounded concurrency and usage budget. Fetch and stage pinned sources/dependencies before entering the network-blocked execution sandbox. The existing single-source and compiler-comparison paths should neither import the FPM resolver nor wait for package preparation. In particular, do not put FPM builds behind the existing API container's single shared control queue or add package initialization to ordinary compiler jobs.

This can avoid additional work or latency in existing request paths. It cannot promise absolute independence while sharing an account: account-wide concurrency ceilings and overall spending limits still apply. Reserve a bounded share of capacity/budget for FPM work so a package workload cannot consume the ordinary playground's allocation. The audit itself changed no production frontend, image definition, routing, quota state, or service deployment.

## Evidence and reproduction

- [results.csv](results.csv): one row per successful final trial, suitable for sorting.
- [results.json](results.json): exact environment, source and demonstration hashes, commands, compiler/FPM versions, timing, memory, file sizes, stdout/stderr, timestamps, and exit codes. Python worker and Fortran demonstration hashes use UTF-8 with normalized LF line endings.
- [packages.lock.json](packages.lock.json): pinned revisions, catalog links, archive checksums, and demonstration hashes (UTF-8 with normalized LF line endings).
- [xfpm_audit.py](../../xfpm_audit.py) and [xfpm_audit_worker.py](../../xfpm_audit_worker.py): preparation and isolated measurement scripts.

From the repository root, use a Python 3.12+ environment with `modal==1.6.0` and an authenticated Modal profile:

```text
python xfpm_audit.py --prepare-only
python xfpm_audit.py --repetitions 2
python -m unittest discover -s tests -p test_fpm_audit.py -v
```

The first command only prepares pinned downloads. The second creates a temporary audit app, incurs its own Modal usage, writes fresh JSON/CSV results, and exits unsuccessfully unless five packages pass all repetitions with headroom. It does not deploy the public API. Downloads are cached in ignored `.fpm-audit-cache/`; no compiler artifacts are reused between trials. Update the narrative table if rerunning produces new measurements.
