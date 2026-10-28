# FPM candidate investigation notes

These notes preserve problems encountered while evaluating packages for Selected, including limitations of this playground. They are not claims that a package is generally broken. No messages or issues have been sent to the authors.

The hosted checks use **GNU Fortran 16.2.0, FPM 0.12.0, Linux, and gVisor**, with network access and secrets disabled. Visitor builds use the debug profile, a 180-second build limit and a 30-second run limit. Offline precompilation has a larger allowance; a separate edited-main test must still pass under visitor limits, with unchanged library artifacts.

The usual consumer commands are:

```text
fpm build --profile debug --compiler gfortran --c-compiler gcc --cxx-compiler g++ --no-prune
fpm run --profile debug --compiler gfortran --c-compiler gcc --cxx-compiler g++ --no-prune
```

[Machine-readable candidate checks](fpm-candidate-checks.json) record complete commit IDs, archive SHA-256 hashes, dependency pins, build adaptations and example hashes. [Successful precompiled checks](fpm-precompiled-validation.json) are recorded separately. Reproduction against another compiler or outside gVisor may produce different results.

| Candidate or feature | Outcome | Evidence |
| --- | --- | --- |
| M_datapac | Preparation limit; compiler not reached | [Archive investigation](#m_datapac) |
| wavepack | Compile failure | [Build log and example](#wavepack) |
| MINRES convenience wrapper | Sandbox run failure; lower-level solver works and is selected | [Reproducer and result](#minres-wrapper) |
| FLINT event root finding | Sandbox run failure; integration and dense output work and are selected | [Reproducer](#flint-events) |
| Auto-Diff | Numerical check failure | [Reproducer and expected results](#auto-diff) |
| kronrod | No reusable library for a custom main | [Source-layout investigation](#kronrod) |
| Parff | Works with heap trampolines for callbacks | [Main and run diagnostics](#parff) |
| DASKR | Works with recorded declaration fixes | [Original diagnostics and patch](#daskr) |
| ffilesystem | Works at an FPM 0.12-compatible pin | [Manifest compatibility](#ffilesystem) |
| NCIO | Works at a pin without the rejected archive symlink | [Archive compatibility](#ncio) |
| ForCAD | GNU 16 internal compiler error; deferred | [Pins, diagnostics and attempted workaround](#forcad) |
| KISS | Works with heap trampolines for callbacks | [Initial failure and verified recipe](#kiss) |
| Sodium | Compile errors; consumer not run | [Diagnostics and attempted fix](#sodium) |
| Yaeos | Dependency archive rejected; compiler not reached | [Forbear archive investigation](#yaeos) |
| fortran_cubatures | Works with FPM 0.12 manifest adaptation | [Manifest and verification](#fortran_cubatures) |
| OPTGRA | Works with explicit convergence thresholds | [Initial settings and correction](#optgra) |
| ForInv | Works with an explicit input workspace copy | [SVD input modification](#forinv) |
| fast_math | Compensated-summation accuracy check failed; deferred | [Hosted and native reproducer](#fast_math) |
| Forlab | Works with guarded optional norm arguments | [Native/hosted crash and narrow fix](#forlab) |
| Polynomial_arnoldi | GNU 16 internal compiler error in dependency; deferred | [Locked recipe and compiler diagnostic](#polynomial_arnoldi) |

## M_datapac

Repository: [urbanjost/M_datapac](https://github.com/urbanjost/M_datapac). The exact checked commit is in the candidate JSON.

The downloaded archive contains **1,736 entries** and expands to **71.93 MiB**, above the preparer's **64 MiB** limit. The entry-count limit was not exceeded. Large files include generated HTML copies of the source, generated search indexes and files under `Archive/`. This is an archive/preparation limitation, not a compiler failure. Neither compilation nor the proposed probability-distribution consumer was attempted.

From the playground repository, this reproduces the preparation step without compiling anything (substitute the full pinned commit from the candidate JSON):

```text
python -c "from fpm_sources import Preparer; Preparer('mdatapac-repro').repository('https://github.com/urbanjost/M_datapac', '9695613622354d6a372fea1e3b4a62e29430bb21')"
```

Observed error:

```text
ValueError: Package archive exceeds the 64 MiB / 10000-entry limit.
```

A source-only distribution or a repository without generated documentation/archive files would be easier for this service to prepare. Adding an explicitly audited source-selection mechanism to the playground is another possible solution. The extraction limit has not been raised.

## wavepack

Repository: [zoziha/wavepack](https://github.com/zoziha/wavepack), commit `b31cddb6703fbe237c7d24ece24a67d31feed871`.

The literal `version = "VERSION"` in `fpm.toml` was normalized to **0.0.1**, matching the upstream VERSION file. Its FFTPACK dependency was pinned to `jacobwilliams/fftpack` at `5601a66e02c97c4e4eadcaff3260f9c92dbdde54`. No Fortran source changes were made.

Compilation then failed in `src/chisqr.f90:2500`:

```text
b = ipmpar(4)
Error: Procedure 'ipmpar' called with an implicit interface [-Werror=implicit-interface]
```

The full captured [build log](fpm-candidates/wavepack/build.log) and the [attempted main program](fpm-candidates/wavepack/main.f90) are retained. The example generates a sinusoid and checks its dominant wavelet period; it was **not executed**, because compilation failed first.

A short local reproduction of this compile error, without FPM's version handling or the FFT dependency, is:

```text
git clone https://github.com/zoziha/wavepack wavepack-repro
cd wavepack-repro
git checkout b31cddb6703fbe237c7d24ece24a67d31feed871
gfortran -c -g -fcheck=bounds -Werror=implicit-interface -fmax-errors=1 src/wavepack_kinds.f90 src/chisqr.f90
```

This short reproduction was also confirmed locally with GNU Fortran 17.0.0 (20260510): it stops at the same implicit `ipmpar` call.

Source inspection found `integer ipmpar` and `external ipmpar` inside `spmpar`, although `ipmpar` is already a procedure in the same module. Those declarations appear to hide the module procedure. Other EXTERNAL declarations deserve the same review. Separately, `wavepack.f90` calls `cffti`, `cfftf` and `cfftb` without importing its dependency's explicit interfaces; the pinned FFTPACK exports `zffti`, `zfftf` and `zfftb` through module `fftpack`. These are suggested investigation points, not applied or verified fixes. The older significance routines also retain deleted language features, reported as warnings in the log.

## MINRES wrapper

Repository: [willdickson/minres](https://github.com/willdickson/minres), commit `c7bb4c7a0ddf13729d3556878ccc688a208a052a`.

The `minres_ez_t` convenience wrapper **compiled successfully**, but execution in the hosted sandbox terminated with **SIGSEGV / exit code 139**, before printing results. The [original main](fpm-candidates/minres-wrapper/main.f90) and [structured build/run result](fpm-candidates/minres-wrapper/result.json) are preserved.

To submit the original consumer to the hosted service from the repository root:

```text
python xplayground_run.py --fpm https://github.com/willdickson/minres --revision c7bb4c7a0ddf13729d3556878ccc688a208a052a --main docs/fpm-candidates/minres-wrapper/main.f90 --compilers gfortran
```

The wrapper passes internal procedures `aprod` and `msolve` to `minres_solver`. Calling `minres_solver` directly with **module procedures** passed in the same sandbox, recovering the known solution `(1,2,3)` and a residual below `1e-9`. That checked [lower-level example](../fpm_catalog/demos/minres.f90) is the Selected entry. The difference suggests an interaction between GNU's internal-procedure callbacks and sandbox execution restrictions; the exact crash mechanism has not been confirmed. Do not assume that a normal local run will crash.

## FLINT events

Repository: [princemahajan/FLINT](https://github.com/princemahajan/FLINT), commit `b6322037cb751b11fa64ea66cf23173ae572fff6`.

An [event-root-finding consumer](fpm-candidates/flint-events/main.f90) for `y'=-y` compiled with preprocessing enabled, then terminated with SIGSEGV / exit code 139 in the hosted sandbox. It should stop at `y=0.5`, at time `log(2)`. The same example passed locally with GNU Fortran 17.0.0 (20260510), finding approximately `0.69314714` and `y=0.50000002`.

Hosted reproduction:

```text
python xplayground_run.py --fpm https://github.com/princemahajan/FLINT --revision b6322037cb751b11fa64ea66cf23173ae572fff6 --main docs/fpm-candidates/flint-events/main.f90 --compilers gfortran --preprocess
```

The source passes the internal procedure `SingleEvent` to its root finder. As with the MINRES wrapper, callback/executable-memory compatibility is a possible explanation, not a confirmed diagnosis. The Selected [integration/dense-output example](../fpm_catalog/demos/flint.f90) passes analytic checks without exercising event root finding. No FLINT source workaround was applied.

## Auto-Diff

Repository: [zoziha/Auto-Diff](https://github.com/zoziha/Auto-Diff), commit `35e62246675cbe6dcd04ce25a81f7885653feabe`.

The hosted GNU 16 consumer compiled but failed its gradient assertion. The [main program](fpm-candidates/auto-diff/main.f90) evaluates:

```text
y = (a + b*b)*exp(c), with a=2, b=1, c=0
Expected value: 3
Expected gradient with respect to a,b,c: 1, 2, 3
```

The upstream `example/demo1.f90` was then compiled and run locally with GNU Fortran 17.0.0 (20260510). Its first expression printed value `3` but gradients `0,0,0`; its second expression also printed zero gradients. No numerical-source fix was applied, and the package was not admitted to Selected.

Local investigation:

```text
git clone https://github.com/zoziha/Auto-Diff auto-diff-repro
cd auto-diff-repro
git checkout 35e62246675cbe6dcd04ce25a81f7885653feabe
```

Before building, change the manifest's literal `version = "VERSION"` to `version = "0.0.4"`, matching the repository's VERSION file. Then run its `demo1` example with FPM, or compile the modules in dependency order and run the preserved main. The investigation has not established whether the numerical failure is caused by source semantics, finalization behavior, or a compiler issue.

## kronrod

Repository: [jacobwilliams/kronrod](https://github.com/jacobwilliams/kronrod), commit `312278846b6e403fdea410a823d88ef4fb92a3cc`.

The inspected routines are internal to application programs under `app/`; there is no reusable `src` library for a consumer main to import. This is a source-layout mismatch with the precompiled consumer workflow, not an observed compiler failure. Moving the numerical routines into a public module would make that workflow possible. The package's own applications have not been validated for Selected.

## Parff

Repository: [everythingfunctional/parff](https://github.com/everythingfunctional/parff), commit `dbce6a04992fbc1e2d13b6c633480d3cd4bbe35c`.

The [consumer main](fpm-candidates/parff/main.f90) should parse `-321`, verify its integer value, then reject `not a number` and print a useful message. It compiles successfully under GNU 16.2.0, but execution in gVisor terminates with **SIGSEGV / exit code 139**, before printing the parsed value. It was initially excluded from Selected; the successful callback recipe below now admits it.

The [structured build/run result](fpm-candidates/parff/result.json) preserves the commands and diagnostic. Its original GitLab dependencies were explicitly mapped to author-maintained GitHub repositories and pinned before staging; [the package recipe](fpm-candidates/parff/package.json) records the exact source archives used. These are preparation adaptations, not Fortran source fixes.

For a local investigation, check out the pinned Parff source, replace the GitLab dependency URLs with the GitHub URLs in the recipe (including transitive dependencies), pin their exact commits, and build a consumer using the preserved main. The first local attempt encountered Windows build-path/log-file problems in a deeply nested preparation directory. A second run with short dependency paths and minimal FPM manifests **passed natively on Windows with GNU 17.0.0 (20260510)**, printing `Parsed integer: -321`, the expected invalid-input diagnostic, and `PASS parff`. Its [native result](fpm-candidates/parff/native-result.json) records the source commits, command, and output. The Fortran sources were unchanged. This distinguishes the hosted failure from a general inability to run the example; it does not establish the precise compiler/sandbox cause.

Parff's parser combinators use internal-procedure callbacks. This resembles the sandbox behavior observed for the MINRES wrapper and FLINT event root finder, but the exact crash mechanism has not been confirmed. No compiler diagnostics or runtime checks were suppressed to admit it.

**Verified callback recipe:** Compiling the unchanged library and consumer with GNU's `-ftrampoline-impl=heap` passes the ordinary hosted GNU 16/gVisor run and the edited-main cache-reuse check. The sandbox restrictions remain unchanged. This package-specific option avoids executable-stack callback trampolines. The original failed recipe and diagnostics above are retained; [the working recipe](fpm-candidates/parff/heap-recipe.json) records the exact pins and compiler environment. The [public validation](fpm-precompiled-validation.json) records the successful check.

## DASKR

Repository: [davidpfister/daskr](https://github.com/davidpfister/daskr), commit `b43533edc5d6900088a846d802e3a86d0f9a06ad`.

The original source fails GNU 16 compilation because `JROOT` in DDASKR is implicitly a scalar when passed to an array dummy argument. Adding its dimension then reveals scalar `RPAR`/`IPAR` declarations in DRCHEK. After correcting those declarations, the consumer builds but the debug run reports an out-of-bounds access to `dx(2)` in `src/dlinpk.f:868`, where the legacy BLAS dummy is declared `dx(1)`.

The [original build log](fpm-candidates/daskr/initial-build.log), [intermediate runtime result](fpm-candidates/daskr/runtime-before-bounds-fix.json), and a reviewable [source patch](fpm-candidates/daskr/fixes.patch) are retained. The checksum-guarded catalog edits:

- Declare `JROOT(*)` in DDASKR and `RPAR(*)`, `IPAR(*)` in DRCHEK.
- Change the bundled LINPACK/BLAS dummy-array declarations from length one to assumed size, including the final dimensions of matrix dummies. The numerical operations are unchanged.

The corrected source passes locally with GNU 17 and `-fcheck=all`, and passes the hosted GNU 16 consumer and changed-main checks. The [example](../fpm_catalog/demos/daskr.f90) checks `y1'=-y1` and the algebraic constraint `y2=y1**2` against `exp(-t)` and `exp(-2*t)`. Bounds and argument checks remain enabled. Root-finding and Krylov modes were not covered by this example.

To reproduce the initial compiler error, check out the pin and compile `src/ddaskr.f` with current gfortran. To investigate the corrected build, apply `fixes.patch`, create an FPM consumer using the example, and run with the debug profile. The archive pin remains the original upstream source; the patch is recorded separately.

## ffilesystem

Repository: [scivision/ffilesystem](https://github.com/scivision/ffilesystem).

The investigated 6.5.3 pin `c31bd919b323fc423b0f467f819e8b2ae8c3200f` uses `[features]` and `[profiles]` in its FPM manifest. FPM 0.12.0 stops before compilation with `Model error: Key features is not allowed in package file`. The [captured log](fpm-candidates/ffilesystem/initial-build.log) is retained. This is a package-manager version mismatch, not a compiler error.

The catalog uses version **6.4.2**, commit `6387e623aa19325a1078f63fa882eb257518d038`, whose manifest does not require those features. No source patch was applied. Its consumer checks path normalization, directory/file creation, copying, file size, contents, and cleanup inside the job's disposable filesystem. A newer FPM service could reconsider the newer pin.

## NCIO

Repository: [alex-robinson/ncio](https://github.com/alex-robinson/ncio).

The investigated pin `3473c797f6c632c56901255bada2c336f3c9e042` contains the symbolic link `test/main.f90 -> test_ncio.f90`. The strict preparer rejects archive links, even internal ones, with `Package archive contains an unsafe path, link, or special file.` The compiler was not reached at that pin.

The catalog instead uses `d76d39df3dcaa892bff5d2b5b24770f3dc65abaa`, immediately before the test-configuration commit that introduced the link. Its archive passes extraction without changing the preparer. GNU 16 checks a small NetCDF array/metadata round trip using pinned `libnetcdff-dev=4.6.0+really4.5.4+ds-3+b4`, `-I/usr/include`, and `-lnetcdff -lnetcdf`. Native libraries and flags are recorded in the catalog. No NCIO Fortran source patch was required.

## Additional compatible pins

The following preparation differences are recorded so that newer revisions can be reconsidered without weakening the archive or offline-build rules.

| Package | Investigated source | Selected source | Reason |
| --- | --- | --- | --- |
| [HaoZeke/GaussJacobiQuad](https://github.com/HaoZeke/GaussJacobiQuad) | `053096a79fb085c2fac6af04989a44ae67b0e8d0` | `v0.1.0` / `ffb970c68eea0b39b140f80f788c8994547d8bfb` | The current archive contains `python/LICENSE -> ../LICENSE`; v0.2.6 and v0.2.0 also failed the no-links extraction rule. |
| [szaghi/BeFoR64](https://github.com/szaghi/BeFoR64) | `4bf55d6048ee2cd7b477460c3925d6e070d74140` | `v1.1.15` / `1dd004ea296b7e5aca60a9704bab81c610f87cff` | The current archive contains `CONTRIBUTING.md -> docs/guide/contributing.md`; v1.2.3 and v1.2.2 also failed extraction. |
| [geospace-code/h5fortran](https://github.com/geospace-code/h5fortran) | `9c7fe2f404b68ea0836c39f4bea67919c07f25bb` | `v4.10.6` / `9fb7549a2d213c10190ae268edecaac4c4c06d0a` | Current h5fortran and v4.12.0 request the HDF5 metapackage, which the catalog adapter does not handle. The older pin declares explicit HDF5 modules and link libraries. |

GaussJacobiQuad uses exact `libopenblas-dev=0.3.29+ds-3`; its consumer checks the weighted integral of `x**2` with weight `(1-x)*(1+x)` on `[-1,1]` against `4/15`. This verifies the selected Golub-Welsch method at five nodes, not all methods or extreme Jacobi parameters.

H5fortran uses `libhdf5-dev=1.14.5+repack-3`, `-I/usr/include/hdf5/serial`, and `-L/usr/lib/x86_64-linux-gnu/hdf5/serial`. Its source pin is tagged v4.10.6 although its manifest says 4.10.1. The consumer checks an exact matrix and string-attribute round trip. HDF5's Fortran module files and runtime are checked with this GNU 16 image; this does not establish compatibility with arbitrary local installations.

BeFoR64's selected source is tagged v1.1.15 although its manifest says 1.1.3. It pins PENF to `65061235982495b158412b70c05b228af4320d94`, whose archive passes extraction. Its example checks the known Base64 representation of `Fortran` and verifies text and integer-array round trips. An initial demo used `n=` instead of the library's `s=` keyword for text; that consumer error was corrected without changing BeFoR64 sources.

These pins, archive checksums, full dependency records, and adapters are in [the candidate checks](fpm-candidate-checks.json). Reproduce the extraction checks with `fpm_sources.fetch` and `fpm_sources.extract_archive`, as in the earlier archive investigation. No link was followed or skipped during extraction.

## ForCAD

Repository: [gha3mi/forcad](https://github.com/gha3mi/forcad), investigated current commit `790b5a73835d7e594855ba5b3fb5a195c20630b8` (manifest 0.16.1).

The hosted GNU 16.2.0 debug build stops in `forcad_nurbs_curve.F90` with an **internal compiler error in `gfc_resolve_forall`, `fortran/resolve.cc:12853`**. The compiler does not reach the custom main. This is a compiler crash, not evidence that the numerical example returned an incorrect result.

The [original log](fpm-candidates/forcad/initial-build.log) and [exact source/dependency recipe](fpm-candidates/forcad/package.json) are retained. The recipe translates OpenMP, resolves manifest VERSION placeholders, pins the older archive-safe FACE source and compatible fortime revision, and disables desktop PyVista display. Bounds and implicit-interface checks remain enabled. These preparation settings succeeded before compilation failed.

Attempts to find a compatible build also failed:

- **v0.15.0**, `5589e9eaa4dd1a673526d227d8054f5e3d185d58`: [same internal compiler error](fpm-candidates/forcad/v0.15-build.log) in the curve module.
- **v0.10.1**, `7a4cb4601b4a80625a6f0cbe0454ddc4fd3d858f`: [same internal compiler error](fpm-candidates/forcad/v0.10.1-build.log), this time in the volume module. Its API also differs from the intended current-version consumer.
- **Existing serial fallback:** a [one-line guard change](fpm-candidates/forcad/gnu16-fallback.patch) selected the current curve-length routine's existing serial implementation for GNU 16. It [did not eliminate the crash](fpm-candidates/forcad/fallback-build.log). This unsuccessful patch is retained for investigation and is **not applied to any selectable package**. The error's precise trigger is still unconfirmed.

The [intended consumer](fpm-candidates/forcad/main.f90) constructs a quadratic Bezier curve, compares sampled points and curve length with analytic values, and uses the existing pyplot helper for a browser PNG. This main has **not been verified with ForCAD** and is not offered in Selected.

To investigate, stage the original source and locked dependencies from the recipe using `CatalogPreparer`, create an FPM consumer, and run the debug build with the recorded flags. Start without the attempted patch. GNU's diagnostic recommends `-freport-bug` to capture preprocessed source for a compiler bug report. No issue has been sent to the author or GCC developers.

## Strff

Repository: [everythingfunctional/strff](https://github.com/everythingfunctional/strff).

The investigated 4.0.0 source, `ea66eebf0d06ae588fc84be7ed6dd621f2d520cc`, requires `exceptional_numbers` and `iso_varying_string` from GitLab. The operator preparer accepts explicit GitHub sources and audited aliases, rather than arbitrary hosts. The attempted author-account GitHub mirror for `exceptional_numbers` returned HTTP 404, so that revision did not reach compilation. This is a preparation limitation, not a compiler or numerical failure.

The selected source is **3.0.4**, `50e536cb087123f2c72140cb065c398a01fc5121`, also investigated as a dependency of Parff. It has no `exceptional_numbers` dependency. Its GitLab varying-string URL is mapped explicitly to the author's GitHub repository and pinned to `fb7635a6b21c3d50ac7c8c14f7696a70931cb4a6`. That dependency choice is recorded as an operator override. No library source patch was applied and no download restrictions were relaxed.

The consumer checks comma-separated splitting, joining, substring/prefix tests and integer-to-string conversion. Its independent consumer and changed-main cache-reuse checks passed in the hosted GNU 16 sandbox. [Candidate checks](fpm-candidate-checks.json) retain both source revisions, checksums, exact dependencies and adapter settings. The separate Parff parser failure remains documented above; it does not prevent this Strff consumer from working.

## KISS

Repository: [ivan-pi/kiss](https://github.com/ivan-pi/kiss), investigated commit `55f0f7ccb1601a0628a17928b5b6b79f61da2892` (manifest 0.1.0).

The library and its custom conjugate-gradient consumer compile with hosted GNU Fortran 16.2.0 and FPM 0.12.0. Running the consumer under the ordinary gVisor restrictions exits with **139 / SIGSEGV**, before printing a numerical result. The changed-main build reused the compiled library. KISS was initially excluded from Selected; the successful callback recipe below now admits it.

The [consumer](fpm-candidates/kiss/main.f90) solves an eight-variable discrete Poisson system and checks both its residual and its known solution. The [exact recipe](fpm-candidates/kiss/package.json) records the source checksum and native BLAS/LAPACK versions. The [hosted diagnostic](fpm-candidates/kiss/hosted-failure.txt) includes the successful build and failing run commands, outputs and exit codes.

In this source pin, `src/kiss@cg.F90` assigns an internal `matvec_dense` procedure to a procedure pointer. An executable-stack trampoline is a possible explanation for the sandbox failure, but the diagnostic does not establish the cause. No KISS source patch was applied and no sandbox restriction was relaxed. To reproduce, prepare the pinned recipe as an FPM consumer, use the retained main, and compile and run with the recorded GNU 16 debug commands. A local run would be useful for comparison but would not by itself verify hosted compatibility.

**Verified callback recipe:** Compiling the unchanged library and consumer with GNU's `-ftrampoline-impl=heap` passes the ordinary hosted GNU 16/gVisor run and the edited-main cache-reuse check. The sandbox restrictions remain unchanged. This package-specific option avoids executable-stack callback trampolines. The original failed recipe and diagnostics above are retained; [the working recipe](fpm-candidates/kiss/heap-recipe.json) records the exact pins and compiler environment. The [public validation](fpm-precompiled-validation.json) records the successful check.

## Opti example convergence

Repository: [Konrad1991/opti](https://github.com/Konrad1991/opti), investigated commit `6fb22db21bd2338e00690ff3706be61a1f101101`.

The [initial example](fpm-candidates/opti/initial-main.f90) used the default star topology with 40 particles and 400 generations. The hosted build succeeded and the program ran, but its squared distance from the known optimum was approximately `1.776e-5`, exceeding the example's `1e-5` check. See the [initial diagnostic](fpm-candidates/opti/initial-example-result.txt). This was a numerical acceptance failure, not a compilation error or sandbox crash.

The revised example uses the library's adaptive-neighborhood topology (`topo=2`) with the same particle count, generation limit, seed and acceptance threshold. It passed the hosted GNU 16 numerical check and changed-main cache-reuse check. No library source was patched. These results concern this particular objective and work budget; they do not certify convergence for arbitrary functions or establish the cause of the star-topology result.

## FoXy

Repository: [Fortran-FOSS-Programmers/FoXy](https://github.com/Fortran-FOSS-Programmers/FoXy), investigated current v0.5.0 commit `f91a269e98171d4b7cad7fd835c96fccd3e044e7`.

Preparation stops before compilation because the source archive contains `CONTRIBUTING.md -> docs/guide/contributing.md`. The package preparer rejects archive links. The same restriction blocks v0.4.0 and v0.2.9. Older v0.0.8 contains documentation and library-source links; v0.0.1 has no root FPM manifest. The parent of the documentation-infrastructure commit still contains documentation links. Exact pins, checksums, link targets and errors are retained in [the archive checks](fpm-candidates/foxy/archive-checks.json). No archive link was followed, removed or skipped.

The [intended main](fpm-candidates/foxy/main.f90) writes `measurements.xml` itself, then uses FoXy to read three named measurements, query their unit attributes, print their values and compare them with known values. The [sample XML](fpm-candidates/foxy/measurements.xml) is also available for inspection; running the main needs no separately supplied data file. This example follows the investigated API but **has not been compiled or run with FoXy** and is not offered in Selected. The [upstream manifest](fpm-candidates/foxy/fpm.toml) is retained; its dependencies have not been resolved or compiled. An archive-safe upstream revision is needed before the hosted checks can proceed.

## ODEPACK

Repository: [Nicholaswogan/odepack](https://github.com/Nicholaswogan/odepack), source `d5db96093dc14fff54e10575cc586fa85392b078`.

The [initial recipe](fpm-candidates/odepack/package.json) compiled successfully with GNU 16.2.0, but the [consumer](fpm-candidates/odepack/main.f90) crashed during integration with exit **139 / SIGSEGV**. The [initial diagnostic](fpm-candidates/odepack/hosted-failure.txt) preserves the build and run stages. The main's callback is a module procedure; the library's `lsoda_integrate` itself creates internal adapters and passes them to the lower-level solver.

The selected recipe adds **`-ftrampoline-impl=heap`** to `FPM_FFLAGS`. GCC documents this option for placing internal-function trampolines on the executable heap instead of the stack on supported targets, including x86-64 Linux ([GCC code-generation options](https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html)). With this compiler option, the same example passes in the ordinary network-blocked gVisor sandbox, including the edited-main library-reuse check. The sandbox restrictions and ODEPACK sources are unchanged. This result supports the callback-trampoline explanation for this failure; it does not establish the cause of every similar crash in another library.

The example integrates the stiff Robertson reactions, checks finite nonnegative concentrations and mass conservation at five output times, and compares the final state at time 4000 with a reference. The final recipe and measurements are in [candidate checks](fpm-candidate-checks.json) and [validation](fpm-precompiled-validation.json).

## Fastmath accuracy example

Repository: [perazz/fastmath](https://github.com/perazz/fastmath), source `ad0f14c455205c0e6c1b9300cd7f333fafb750e2`.

The [initial main](fpm-candidates/fastmath/initial-main.f90) compiled and ran, but the default cubic logarithm approximation had a maximum absolute error of about `3.642e-3` over the stated interval, exceeding the example's `1e-3` threshold. See the [initial result](fpm-candidates/fastmath/initial-example-result.txt). This was an example-method choice, not a compiler failure.

The selected example uses the supported **quintic logarithm** with the same interval and threshold. It passes hosted GNU 16 checks, with maximum absolute logarithm error about `2.998e-4`. The exponential and inverse-square-root checks also pass. No library source was changed. These error bounds concern the sampled domain in the example, not all possible inputs, and the example makes no performance claim.

## Fortran-FLANN

Repository: [ivan-pi/fortran-flann](https://github.com/ivan-pi/fortran-flann), source `35370c851602d954d1d01d10c9c14ff82dd96496`.

The [initial recipe](fpm-candidates/fortran-flann/initial-recipe.json) requested `libflann-dev=1.9.2+dfsg-2+b2`. Its MPI/HDF5 development dependencies pulled in Debian's default compiler packages, whose configuration failed because `/usr/bin/gfortran` was absent in this compiler image. The [installation log](fpm-candidates/fortran-flann/native-install.log) is retained. This happened before the Fortran bindings were compiled.

The selected recipe installs **`libflann1.9=1.9.2+dfsg-2+b2`** instead. The Fortran bindings already declare their C interfaces and do not need FLANN C++ headers. A checksum-guarded edit to the prepared `fpm.toml` changes `link = "flann"` to `link = ":libflann.so.1.9"`, selecting the runtime library's versioned filename. No Fortran source is patched. The newer patch adapter hashes LF-normalized text so this generated-manifest edit can be reproduced when preparing an exported project on Windows or Unix; existing patch recipes retain their previous strict byte checks and cache keys.

The hosted consumer verifies nearest-neighbor indices and squared distances against direct calculations on a small known point set. Its query, finite-result and edited-main cache-reuse checks pass. The recipe uses GNU/Linux linker syntax; a different local system may need its usual FLANN development package and normal `link = "flann"` setting. The catalog records BSD-3-Clause from the repository's license file, rather than its manifest's BSD-2-Clause label.

## Retesting

Keep the original pin and diagnostic when investigating a fix; record a new pin and new results separately. A source fix should pass both the numerical example and the edited-main cache-reuse check before an entry becomes selectable. A successful local run alone does not establish hosted sandbox compatibility.

## Yaeos

Repository: [ipqa-research/yaeos](https://github.com/ipqa-research/yaeos), commit `e886a2316b7703131d0ed9f13de2edc9f64e477d` (manifest version 4.5.4).

The root archive passes extraction. Preparation then rejects the Forbear dependency, `szaghi/forbear` commit `a31639e80631bdc218e45a7152f007f74dde49ee` (v1.9.1), because `CONTRIBUTING.md` is a symlink to `docs/guide/contributing.md`. The same link exists in investigated versions v1.8.0 and v1.5.0; v0.0.1 has no root FPM manifest. No links were followed or removed and the preparer's restrictions were not relaxed. Other dependencies have not been fully evaluated.

The intended [methane pressure consumer](fpm-candidates/yaeos/main.f90) compares a Peng?Robinson calculation with an independently written formula. **It has not been compiled or run** and is not offered in Selected. The [root manifest](fpm-candidates/yaeos/fpm.toml), [preparation record](fpm-candidates/yaeos/preparation.json), and [dependency archive checks](fpm-candidates/yaeos/dependency-archive-checks.json) retain exact commits, checksums and rejected link paths. This is a playground source-preparation limitation, not a demonstrated error in Yaeos or Forbear.

To reproduce the first rejection without compiling, download the pinned Forbear archive and pass it to `fpm_sources.extract_archive`; the root Yaeos manifest's `forbear` dependency resolves to that commit in the recorded attempt. A compatible upstream source archive without links and with an FPM manifest would allow preparation to continue; it would not by itself establish that the remaining dependencies or numerical demonstration work.

## Sodium

Repository: [freevryheid/sodium](https://github.com/freevryheid/sodium), commit `805225de601cc1f541fc7699d76a748d6eda58ca` (manifest version 0.2.0). The native library recipe pins `libsodium-dev=1.0.18-1+deb13u1`.

The unchanged GNU 16 build fails in `src/crypto_hash_sha256.f`: its interoperable state type uses `c_int8_t`, `c_int32_t` and `c_int64_t` without importing them. A checksum-guarded [import-only patch](fpm-candidates/sodium/imports.patch) gets compilation past that module, but the next failure is `paremeter` instead of `parameter` in `src/crypto_kdf_blake2b.f:12`. The same misspelling appears in four key-derivation source files. These further declarations were not patched, and later compilation or linking problems have not been evaluated.

The [initial build log](fpm-candidates/sodium/initial-build.log), [retry log](fpm-candidates/sodium/import-fix-build.log), [original recipe](fpm-candidates/sodium/initial-recipe.json) and [attempted recipe](fpm-candidates/sodium/attempted-recipe.json) preserve the exact pin, source checksum and native-library settings. The intended [consumer](fpm-candidates/sodium/main.f90) would encrypt and decrypt a short message, check exact recovery and reject a tampered ciphertext. **It has not been compiled or run.** Sodium and its attempted patch are not included in Selected.

To reproduce, prepare the original pinned recipe with `CatalogPreparer`, build its consumer with the ordinary GNU 16 debug command, and inspect the missing-kind diagnostic. For the second diagnostic apply the checksum-guarded edit from the attempted recipe before building. Fixing the import alone does not make this source revision buildable.

## fortran_cubatures

Repository: [willklausler/fortran_cubatures](https://github.com/willklausler/fortran_cubatures). The pinned root archive and numerical source are unchanged. FPM 0.12 rejects its `[features]`/`[profiles]` manifest configuration before compiling. The operator applies a checksum-guarded [manifest-only edit](fpm-candidates/fortran_cubatures/fpm-compatibility.patch) that removes those unsupported profile definitions. The package-specific `FPM_FFLAGS` is `-Wall -Wextra -fcheck=all -fbacktrace`; normal sandbox restrictions and debug/runtime checks remain enabled. This adaptation does not reproduce the upstream profiles' optional sanitizer or release optimization flags.

The [initial recipe](fpm-candidates/fortran_cubatures/initial-recipe.json) and [FPM diagnostic](fpm-candidates/fortran_cubatures/initial-build.log) preserve the unadapted attempt. The working edit is applied to the normalized manifest produced by the source preparer, not to raw upstream TOML formatting. Its exact checksum, replacement, source pin and environment are recorded in the catalog and public validation and accompany project exports. The consumer integrates `x**2*y` on the unit reference triangle and `x*y*z` on the unit reference tetrahedron and compares with exact simplex integrals `1/60` and `1/720`.

## OPTGRA

Repository: [jacobwilliams/optgra](https://github.com/jacobwilliams/optgra). The example minimizes `(x-1)**2+(y-1)**2` subject to `x+y>=3`, with exact optimum `(1.5,1.5)` and objective `0.5`.

The first example mistakenly supplied `[1,1]` as `Consca`, which the API documents as convergence thresholds. It reported success at approximately `(sqrt(2),sqrt(2))`, although that point violates the intended tight constraint check. The [initial main](fpm-candidates/optgra/initial-main.f90), [hosted diagnostic](fpm-candidates/optgra/initial-hosted-failure.txt) and [native output](fpm-candidates/optgra/initial-native-output.txt) retain this example-configuration failure.

The selected example uses `Consca=[1e-7,1e-9]`, with separate derivative deltas `Delcon=[1e-4,1e-4]`, and checks the returned variables, objective and feasibility independently of the solver status. No library source is patched. The source's LICENSE.txt offers GPL version 3 or ESA ESCL 2.4 Weak Copyleft; the catalog records that choice rather than inferring a license from the absent manifest field.

## ForInv

Repository: [gha3mi/forinv](https://github.com/gha3mi/forinv). Its pinned ForSVD dependency calls LAPACK `dgesvd` with its input array directly, despite declaring the array `intent(in)`. LAPACK overwrites that storage. The initial [consumer](fpm-candidates/forinv/initial-main.f90) used the same matrix after `inv`, so its independent Moore?Penrose checks failed. The [hosted diagnostic](fpm-candidates/forinv/initial-hosted-failure.txt) and [source/dependency recipe](fpm-candidates/forinv/package.json) preserve this behavior.

The selected main explicitly makes a separate workspace copy before calling `inv`; residuals and all four Moore?Penrose identities use the preserved original. It also supplies `tol=1e-10` because this API otherwise assumes full rank. The rank-one example has columns `[1,2,3]` and `[2,4,6]`, and checks the known minimum-norm solution `[0.2,0.4]`. This is an example-level workaround, not a fix for the dependency's misleading input contract. Callers of this pin should preserve inputs that they need afterward. No ForInv or ForSVD source is patched.

Manifest version placeholders are rendered as catalog metadata, and ForSVD, kinds, Fortime and FACE use exact recorded source pins. BLAS and LAPACK are pinned native dependencies. These settings travel with exported projects.

## fast_math

Repository: [jalvesz/fast_math](https://github.com/jalvesz/fast_math), commit `a4f93517a2c09c57b6ae74585404ae4457d16716` (manifest 0.1.0). This is distinct from the selected `perazz/fastmath` package.

The library and consumer compile, but the compensated-sum check fails in hosted GNU 16/gVisor. The reproducer sums 10,001 real32 values: `1e8` followed by 10,000 ones. Their exact real64 sum is `100010000`. A native GNU run reports intrinsic sum `100000000`, chunked sum `100010080`, and compensated sum and dot product `100010240`, so both compensated results miss the exact value by `240`, exceeding the example's one-real32-spacing allowance of `8`. The failure was not made to pass by relaxing that threshold or selecting a more favorable input. It does not establish the behavior for every input or compiler.

The [asserting main](fpm-candidates/fast_math/main.f90), [hosted failure](fpm-candidates/fast_math/hosted-failure.txt), [native diagnostic main](fpm-candidates/fast_math/native-diagnostic.f90), [native output](fpm-candidates/fast_math/native-output.txt), and [exact recipe](fpm-candidates/fast_math/package.json) are retained. The diagnostic-only main omits assertions so every result is printed; it is not a successful correctness check. No numerical source patch was attempted. The package remains outside Selected.

To reproduce natively, compile the eight `src/fast_*.f90` modules in dependency order (sum, dotp, rsqrt, log, trigo, tanh, erf, then math) followed by the diagnostic main, using `gfortran -cpp -ffree-line-length-none -g -fcheck=all`, and run the executable. The hosted recipe adds preprocessing and unrestricted free-form line length for this package only. The upstream MIT LICENSE file and source headers clarify its manifest's placeholder license.

## ForSolver dependency preparation

The current FACE dependency archive used by ForUnittest contains a documentation symlink and is rejected by the ordinary preparer. ForSolver's catalog recipe instead locks FACE to `b20893e48518a81c25982ef20cc5a7cf8d31c8d8`, the compatible pin already used by other selected packages, and locks ForDiff to its previously verified source pin. The [dependency preparation record](fpm-candidates/forsolver/dependency-preparation.json) retains the rejected archive checksum and link targets. All final dependencies are pinned in the catalog. No archive entries are skipped and no extraction restrictions are relaxed. The main uses module callbacks and compares three Newton derivative strategies against the exact root of `x**3+x-2` and independent residual checks.

## Forlab

Repository: [zoziha/forlab](https://github.com/zoziha/forlab), commit `416e5612167b6133100bef4cec116322890f66f7` (manifest 1.0.1).

The original quadratic least-squares consumer compiles with hosted GNU 16.2.0 but exits with SIGSEGV while calling `solve` on a rectangular system. A native Windows GNU 17 run reproduces the crash. GDB traces `solve -> svdsolve -> norm1` to `src/forlab.F90:6251`, where `.not. present(p) .or. p == 2` references the absent optional `p` argument. Fortran does not require short-circuit evaluation of `.or.`. The matrix-norm overload contains the same pattern.

The checksum-guarded [source edit](fpm-candidates/forlab/optional-norm.patch) assigns a local power of two, updates it only when `p` is present, and uses that local value in both norm overloads. It preserves the intended default and explicit-power formulas; it does not disable compiler/runtime checks. The final main checks default and explicit vector/matrix norms before fitting five quadratic observations and independently checking coefficients and residuals. Both hosted run and changed-main library reuse pass. The serial library is self-contained and needs no native BLAS/LAPACK packages or MPI for this example.

The [initial main](fpm-candidates/forlab/initial-main.f90), [hosted failure](fpm-candidates/forlab/initial-hosted-failure.txt), [native crash output](fpm-candidates/forlab/initial-native-output.txt), [GDB backtrace](fpm-candidates/forlab/native-backtrace.txt), [native check settings](fpm-candidates/forlab/native-check.json), and [corrected native output](fpm-candidates/forlab/fixed-native-output.txt) are retained. The initial recipe included unnecessary BLAS/LAPACK packages; the final recipe omits them. The exact final patch travels with exported projects. This fixes the demonstrated norm issue, not every optional-argument pattern or numerical routine in the utility module.

## Polynomial_arnoldi

Repository: [loiseaujc/polynomial_arnoldi](https://github.com/loiseaujc/polynomial_arnoldi), commit `83a6625e94504151bf27aea023568a2eec34256b` (manifest 0.1.0).

Preparation resolves the stdlib registry dependency to the generated, pinned stdlib source snapshot and locks SpecialMatrices and its FFTPACK dependency. GNU Fortran 16.2.0 then stops with **an internal compiler error in `gfc_resolve_forall`**, while compiling the unmodified SpecialMatrices dependency's `src/Strang/matvecs.f90`. This is the same compiler failure already worked around in the separately selected SpecialMatrices entry. Catalog source patches currently target their root package, so that entry's edits do not automatically apply when SpecialMatrices appears as another package's dependency. No dependency source was changed for this attempt.

The [locked recipe](fpm-candidates/polynomial_arnoldi/package.json), [compiler diagnostic](fpm-candidates/polynomial_arnoldi/build-failure.txt), and [intended consumer](fpm-candidates/polynomial_arnoldi/main.f90) are retained. The consumer would compare ordinary GMRES and polynomial-preconditioned GMRES against a manufactured solution and residuals, but **it has not compiled or run**. Polynomial_arnoldi remains outside Selected. A dependency-scoped application of the existing guarded SpecialMatrices workaround, or an upstream/compiler-compatible revision, could permit further evaluation; it would not establish that the remaining solver checks pass.

## NAFPack manifest compatibility

NAFPack's source VERSION file identifies `0.1.52`; the operator renders its manifest placeholder accordingly. Its OpenMP metapackage is resolved explicitly, FFTW is pinned as `libfftw3-dev=3.3.10-2+b1`, and the [manifest-only edit](fpm-candidates/nafpack/fpm-compatibility.patch) removes `[features]` and `[profiles]` definitions unsupported by FPM 0.12. It preserves all prepared dependency/native-link settings. `-fopenmp -cpp -I/usr/include -ffree-line-length-none` enables the ordinary build without adopting its unsupported custom profiles. No numerical Fortran source is patched, no runtime check is suppressed, and normal sandbox limits remain in force.

The selected single-precision example checks two exact complex frequency amplitudes in sixteen samples and verifies reconstruction with an inverse transform. The public validation records the exact source pin, manifest edit, native settings and edited-main cache-reuse result.

## FISHPACK and DDE_SOLVER source packaging

Repositories: [jlokimlin/fishpack](https://github.com/jlokimlin/fishpack), commit `9dc7d2e7a847fa6a610752d4e91eda3ef9c6130d`, and [WarrenWeckesser/dde_solver](https://github.com/WarrenWeckesser/dde_solver), commit `90d3389ce5d5733ab2b6e7ed7d2dad273b4d0c6b`.

Neither pinned repository has a root FPM manifest. Their catalog recipes supply minimal manifests and enumerate the exact library sources copied into `playground-library`. FISHPACK excludes its `src/main.f90` smoke program; DDE_SOLVER includes only `dde_solver_m.f90`. Original upstream files and licenses remain in the source tree. The ordinary archive, graph and resource restrictions still apply. A source wrapper requires an exact archive checksum and commit, is selected only by operator-owned catalog settings, and is also reproduced by local catalog execution and exported projects. It does not enable arbitrary non-FPM visitor repositories.

The FISHPACK consumer solves a manufactured two-dimensional Poisson problem with exact solution `sin(pi*x)*sin(pi*y)`, checking finite values, solver status and maximum discretization error below `1e-3` on 32-by-32 intervals. DDE_SOLVER's consumer adapts the author's delayed oscillator test, places callbacks in a module, and checks nine interpolated samples against `sin(t)` over a full period to `1e-7`. The [author's license](fpm-candidates/dde_solver/licenses/LICENSE.txt) accompanies the adapted demo.

Both consumers passed edited-main verification in the ordinary GNU 16.2 gVisor sandbox, with unchanged library artifacts. Their numerical Fortran sources are unpatched. The wrapper adapter preserves the previous adapter identity for existing recipes, so these additions do not invalidate earlier compiled libraries.

## SPHEREPACK

Repository: [jlokimlin/spherepack](https://github.com/jlokimlin/spherepack), commit `e80da29462c5987162a0884baaab7434d0215467`.

The catalog supplies a source-list FPM wrapper and excludes the upstream smoke program. The first GNU 16 build stops because `wrfft(..)` in `src/vector_synthesis_routines.f90:247` is passed to a rank-one FFT workspace argument. A first attempted assumed-shape declaration `wrfft(:)` is incompatible with the upstream assumed-size callers; the [compiler diagnostic](fpm-candidates/spherepack/retry-result.txt) is retained. Using `wrfft(*)` gets past those calls but exposes a second assumed-rank workspace in `src/vector_synthesis_gaussian_grid_saved.f90:1185`, passed to rank-one coefficient routines. The [next diagnostic](fpm-candidates/spherepack/assumed-shape-retry.log) records that failure.

The working [guarded edits](fpm-candidates/spherepack/workspace-rank.patch.json) use rank-one assumed-size declarations for both workspaces. They apply only to the listed build copies, after checking each original file's normalized checksum; original files remain alongside the wrapper. Numerical expressions and algorithms are unchanged. The [unadapted recipe](fpm-candidates/spherepack/initial-recipe.json) and [initial diagnostic](fpm-candidates/spherepack/initial-build.log) preserve the first attempt.

The consumer adapts the author's `examples/helmsph.f90`, solves the spherical Helmholtz problem for `(1+x*y)*exp(z)` on a 19-by-36 Gaussian grid, and checks finite values and maximum absolute error below `1e-10`. It passed hosted GNU 16 edited-main/cache-reuse checks. This verifies the demonstrated scalar problem, not every vector transform. [Upstream license notices](fpm-candidates/spherepack/licenses/LICENSE.md) and the [modernization license](fpm-candidates/spherepack/licenses/LICENSE.mit.md) accompany the adaptation.

## ForSVD and QDUtilLib quadrature

ForSVD, commit `f39bba7afcb048a21947a7a640bdf9a18337f8ac`, uses the same pinned source already present in ForInv's dependency graph. The new standalone consumer checks singular values `[3,2,1]` and Frobenius reconstruction errors `[sqrt(5),1,0]` as the rank increases. It preserves its input because the LAPACK call overwrites its workspace, as noted under ForInv above. Native BLAS/LAPACK and Fortran dependencies are pinned.

QDUtilLib, commit `8a1fa9ca7cf52683c98cc4bcb40f21dc41df6ed5`, provides Legendre and harmonic-oscillator quadrature. The [initial main](fpm-candidates/qdutillib/initial-main.f90) misunderstood the HO weight convention: it summed `w*x**2`, omitting the Gaussian required by these full-function weights. The [failed check](fpm-candidates/qdutillib/initial-result.json) is an example error, not evidence of a library failure. Source inspection of `SRC/Quadrature/Quadrature_m.f90` shows that its HO weights are derived using Gaussian-weighted basis values; the correct integrand here is `x**2*exp(-x**2)`.

The corrected consumer checks `2/9` for the integral of `x**8` over `[-1,1]` and `sqrt(pi)/2` for the Gaussian second moment. Hosted absolute errors were approximately `2.78e-17` and `2.22e-16`. ForSVD and QDUtilLib both passed changed-main verification without rebuilding their libraries. No library source is patched for either package.

## libsparse

Repository: [jvdp1/libsparse](https://github.com/jvdp1/libsparse), commit `3d93e03a0e7e7b66cc791c054dc45eb5d0a9d70a`.

The root FPM manifest enables MKL PARDISO and other optional facilities. After resolving OpenMP explicitly, the hosted GNU 16 build fails at `src/modsparse_mkl.f90:1` because `mkl_pardiso.f90` is absent. That module also includes MKL BLAS, sparse BLAS and LAPACK interfaces. The current GNU catalog image does not supply those development files. The [locked recipe](fpm-candidates/libsparse/package.json), [build failure](fpm-candidates/libsparse/build-failure.log), and [intended consumer](fpm-candidates/libsparse/main.f90) are retained.

The intended example assembles a tridiagonal operator in linked-list storage, converts it to compressed-row storage and checks matrix-vector multiplication against an independent dense calculation. **It has not compiled or run**, so libsparse is not in Selected. Reproduce preparation with `CatalogPreparer` using the saved recipe and its exact root/dependency locks, then build the consumer with ordinary GNU debug flags. Installing suitable MKL interfaces or obtaining an upstream portable configuration would allow further evaluation; neither alone establishes that the consumer passes.

## finite_difference

Repository: [jlr581/finite_difference](https://github.com/jlr581/finite_difference), commit `ef0f351b7a2ae187833d574b8aeea3cabde0a105`.

This non-FPM repository uses an explicit source-list wrapper. The [first build](fpm-candidates/finite_difference/initial-build.log) fails because `data_types.f90` contains integer literals larger than the default integer kind permits. The [initial recipe](fpm-candidates/finite_difference/initial-recipe.json) records that attempt. Building the complete library and consumer with `-fdefault-integer-8` resolves compilation without disabling range checks.

The resulting seven-node derivative example exceeds the ordinary 200000-byte stage-output limit: repeated array-temporary warnings from `hyper_dual.f90:174-177` flood stderr before numerical output is reached. A smaller three-node uneven stencil, with an explicit shape parameter and no Taylor acceleration, has the same problem. A diagnostic attempt to disable only array-temporary warnings through `FPM_FFLAGS` was ineffective under this FPM debug configuration; the saved final recipe does **not** include that option. No service limit was increased and no runtime check is disabled in that recipe.

The [final locked recipe](fpm-candidates/finite_difference/package.json), [three-node consumer](fpm-candidates/finite_difference/main.f90), [original seven-node consumer](fpm-candidates/finite_difference/initial-main.f90), and [hosted failure](fpm-candidates/finite_difference/hosted-failure.json) preserve reproduction details. The failure record keeps the stage limit, exit code and representative warnings; repetitive stderr is abbreviated. Both builds succeeded, but the sandbox killed the runs at the output limit, so **no numerical accuracy result is established** and the package remains outside Selected. A source change that avoids repeated argument temporaries, or a compatible debug configuration, needs a fresh numerical and cache-reuse check.

## DAQP-fortran and SQPOPT

The investigated DAQP source is [jacobwilliams/daqp-fortran](https://github.com/jacobwilliams/daqp-fortran), commit `318bfb6c55e6992c136a0bb5bf89df7b4c0ba177` (release `0.1.1`). Its archive contains the symbolic link `compare/src/daqp_test_utils.f90 -> ../../test/daqp_test_utils.f90`. The ordinary preparer rejects archive links before extraction. Release `0.1.0`, commit `2e06d6f315390d9b6d9dbce0200dd0af6c10b775`, has the same link. The [archive checks](fpm-candidates/daqp-fortran/archive-checks.json) preserve exact commits, archive checksums and rejected paths. No link was followed, removed or substituted.

The [locked DAQP recipe](fpm-candidates/daqp-fortran/package.json), [upstream manifest](fpm-candidates/daqp-fortran/fpm.toml), [preparation failure](fpm-candidates/daqp-fortran/preparation.json), and [intended consumer](fpm-candidates/daqp-fortran/main.f90) are retained. The consumer would minimize `(x-1)**2+(y-1)**2` subject to nonnegativity and `x+y>=3`, checking the exact optimizer `(1.5,1.5)` and objective `0.5`. **It has not compiled or run.**

The investigated SQPOPT source is [jacobwilliams/sqpopt](https://github.com/jacobwilliams/sqpopt), commit `53b81010c5109a6219585763ad04289dbdede196`. Its root archive passes preparation. Dependency resolution downloads LSQR, LUSOL, FMIN and QDLDL successfully, then encounters the same DAQP `0.1.1` archive rejection. The [SQPOPT recipe](fpm-candidates/sqpopt/package.json) locks the root and all five dependencies, including the rejected DAQP archive; the [preparation record](fpm-candidates/sqpopt/preparation.json) records only repositories reached successfully. No compiler was invoked for this package.

The [intended SQPOPT consumer](fpm-candidates/sqpopt/main.f90) adapts the author's `example/hs71.f90`, moving callbacks into a module and adding finite-value, feasibility, objective and known-solution checks for Hock-Schittkowski problem 71. The [upstream license](fpm-candidates/sqpopt/LICENSE) accompanies the adaptation. **The adapted consumer has not compiled or run.** Neither DAQP nor SQPOPT is in Selected; this is a playground archive-preparation limitation, not a demonstrated numerical or compiler defect in either library.

To reproduce, use `Preparer` with the saved recipe's root/dependency checksum locks and its intended main. SQPOPT reaches the rejected dependency after the five successful records shown in its diagnostic. The DAQP rejection can also be reproduced by downloading the recorded archive with `fpm_sources.fetch` and passing it to `fpm_sources.extract_archive`. An upstream archive replacing the comparison-source link with an ordinary file would permit further evaluation, but would not establish numerical or sandbox compatibility by itself.

## QDLDL-fortran and LUSOL

[QDLDL-fortran](https://github.com/jacobwilliams/qdldl-fortran) is pinned to `8ebdd7fa1075bfb89115d0955806b0996b6b29d5`. Its consumer assembles a four-by-four quasi-definite KKT matrix, solves it with natural, reverse Cuthill-McKee and AMD orderings, and checks a manufactured solution, independent dense residuals and inertia `(2,2,0)`. Solution errors were at most about `4.44e-16`, and residuals at most `8.88e-16`. This is not a claim that its nonpivoting factorization supports arbitrary indefinite matrices. The [verified output](fpm-candidates/qdldl-fortran/verified-output.txt) is retained.

[LUSOL](https://github.com/jacobwilliams/lusol) is pinned to `2d95174d44ec9bf9dabbbd07652c84c11fe56d71`. Its example calls the low-level public routines `lu1fac`, `lu6sol` and `lu8rpc` using the library's 64-bit index kind. It checks a sparse tridiagonal solve, replaces column two without refactorizing the matrix, and checks the updated solve against the original manufactured solution and an independent dense residual. Both solves had maximum solution error about `4.44e-16` and zero residual at the displayed precision; see [output](fpm-candidates/lusol/verified-output.txt).

Both unmodified libraries passed hosted GNU 16 debug builds and changed-main/cache-reuse checks. Neither needs a native system library or an operator source patch.

## Carlson elliptic integrals

Repository: [jacobwilliams/carlson-elliptic-integrals](https://github.com/jacobwilliams/carlson-elliptic-integrals), commit `5f25a59a555b7029505aac71a8341d5851f8abed`.

The consumer computes a one-metre pendulum's period at initial angles 0, 30, 90 and 150 degrees. It evaluates `RF(0,1-sin(theta/2)**2,1)` and independently computes the defining complete elliptic integral using composite Simpson quadrature with 4096 subintervals. It also checks `RF(1,1,1)=1`, status codes and finite values. The largest displayed quadrature disagreement was about `1.55e-15`; the [verified output](fpm-candidates/carlson-elliptic-integrals/verified-output.txt) includes the periods and ratios to the small-angle approximation. The unpatched library passed the ordinary GNU 16 debug and cache-reuse checks.

## fortran-bessels

Repository: [perazz/fortran-bessels](https://github.com/perazz/fortran-bessels), commit `7bf8d6b144b00d4201a782ca65f6ae14a84d49a1`.

The consumer is deliberately limited to `besseli0`, `besseli1`, `besselk0` and `besselk1` for positive real arguments. It checks four independent reference constants at `x=1` and the modified-Bessel Wronskian identity `x*(I0*K1+I1*K0)=1` at five points from `0.25` to `8`. The largest displayed identity error was about `4.44e-16`; see [output](fpm-candidates/fortran-bessels/verified-output.txt).

The pinned README documents known noninteger-order Y/Hankel limitations. Passing this consumer does not validate those paths, all exported procedures, arbitrary argument ranges or performance claims. The library and consumer use the normal GNU 16 debug configuration, without `-ffast-math` or a source patch, and passed changed-main/cache-reuse checks.

## Dynamics

Repository: [jchristopherson/dynamics](https://github.com/jchristopherson/dynamics), commit `580d04859a25126d3261e44b3fbec5111835e3a4`.

The [initial preparation](fpm-candidates/dynamics/initial-preparation.json) encountered an OpenMP metapackage before an explicit mapping was supplied. The final catalog recipe resolves OpenMP with `-fopenmp`, pins BLAS/LAPACK/ARPACK, and locks all eight dependency repositories. The [initial recipe](fpm-candidates/dynamics/initial-package.json) preserves the pre-mapping attempt; the final settings are in the selected catalog and public verification report.

A subsequent attempt hit the operator uploader's [stdin buffer limit](fpm-candidates/dynamics/initial-upload-error.txt) before compilation. The precompile script now drains the source payload in bounded 64 KiB chunks. This does not change the sandbox worker, source/archive limits, visitor resource limits, compiler options or existing library cache identities. The successful prebuild demonstrates the transport fix with the actual prepared dependency bundle.

The consumer computes the complete complex frequency response of `x''+0.2*x'+4*x=cos(omega*t)` at eight angular frequencies, using `frequency_response` and a module callback. It checks the response against `1/(4-omega**2+i*0.2*omega)`, including the resonant frequency. The [verified output](fpm-candidates/dynamics/verified-output.txt) includes amplitudes and analytic errors. No Fortran source is patched. The hosted debug and changed-main/cache-reuse checks passed; verification covers this proportional-damping example, not the library's entire dynamics, controls or finite-element API.

## diffstruc

Repository: [nedtaylor/diffstruc](https://github.com/nedtaylor/diffstruc), commit `88565f8e01792706edc0bd7e70dde957c26122a4`.

The consumer adapts the array setup and forward-mode calls in the author's `test/test_functions.f90`. It compares both forward and reverse gradients of `x1*x2**2+x1**2` at `(1.25,-2)` with the independent analytic gradient `(6.5,-5)`. BLAS/LAPACK and the coreutils dependency are pinned in the catalog recipe. The library is unmodified.

The [initial driver](fpm-candidates/diffstruc/initial-main.f90) retained direction `(0,1)` after its forward-mode loop. Reverse accumulation also applies that direction mask, so the [initial check](fpm-candidates/diffstruc/initial-result.json) failed. This was a driver error, not an established library defect. Restoring direction `(1,1)` before reverse mode gives the expected complete gradient. The corrected demo passed ordinary GNU 16 debug and changed-main/cache-reuse checks; see [verified output](fpm-candidates/diffstruc/verified-output.txt). The author's [MIT license](fpm-candidates/diffstruc/licenses/LICENSE) accompanies the adaptation. These checks do not establish arbitrary-order differentiation or all array-operation paths.

## DNAOAD-FPM

Repository: [fpenunuri/DNAOAD-FPM](https://github.com/fpenunuri/DNAOAD-FPM), commit `f7f328e89b208a99797d64f4a41e97ba91b85962`.

The dual-number initialization follows the author's `app/ex1.f90`. Our consumer evaluates `exp(z)+sin(z)` at `z=0.4` and `z=0.4+0.2i` and checks every derivative from order zero through five against analytic complex values, including finite-error checks. Five is this precompiled library's default maximum order; changing only the user's main cannot increase that compiled configuration. Higher configured orders require a fresh library build. The unpatched library passed hosted GNU 16 debug and edited-main reuse checks; [output](fpm-candidates/dnaoad-fpm/verified-output.txt) and [MIT license](fpm-candidates/dnaoad-fpm/licenses/LICENSE) are retained. Multivariate Hessian/Jacobian routines are not covered by this demo.

## SEISCOPE optimization toolbox

Repository: [ofmla/seiscope_opt_toolbox_w_ctypes](https://github.com/ofmla/seiscope_opt_toolbox_w_ctypes), commit `74a25c29d13c506e16f8025eb13a2cf396dc23c0`.

The Fortran library works independently of its Python wrapper. The consumer adapts the author's `app/LBFGS/test_LBFGS.f90`, preserves its BSD notice, bounds the reverse-communication loop and checks convergence status, proximity to `(1,1)`, an independently evaluated Rosenbrock objective and gradient. The [initial run](fpm-candidates/seiscope-optimization/initial-result.json) failed a bounds check in `descent_LBFGS`: its caller passed the uninitialized local integer `l` as the workspace extent.

The [guarded edit](fpm-candidates/seiscope-optimization/memory-length.patch.json) changes that actual argument to `optim%l`, the configured memory length already used to allocate and update the arrays. It changes no numerical formula and suppresses no runtime check. The corrected library passed GNU 16 debug and changed-main/cache-reuse checks; see [output](fpm-candidates/seiscope-optimization/verified-output.txt). The [wrapper MIT license](fpm-candidates/seiscope-optimization/licenses/LICENSE.md) and [original demo with its BSD notice](fpm-candidates/seiscope-optimization/licenses/test_LBFGS.f90) are retained. Other optimizers and bound-constrained paths have not been validated by this example.

## GSLIB 2.0

Repository: [exepulveda/gslib2.0](https://github.com/exepulveda/gslib2.0), commit `5c021000eb3da8703ced3ee9be145d6c0ecb2608`.

The original root manifest's name `gslib2.0` fails package-name validation. The catalog-only adapter renders it as `gslib` for this locked repository. Public preparation continues rejecting invalid package names; previous adapter identities and all existing library recipes remain supported. The [initial recipe](fpm-candidates/gslib/initial-package.json) records this name correction before the other compatibility settings.

The [first compilation](fpm-candidates/gslib/initial-build.log) failed at implicitly typed constants in `acorni.f90`. The [manifest edit](fpm-candidates/gslib/implicit-typing.patch.json) explicitly enables legacy implicit typing and external procedures. Compilation then reached a [rank mismatch](fpm-candidates/gslib/implicit-typing-build.log) in `nscore.f90`: its first sorting call supplies scalar placeholders for unused array arguments, while a later call supplies an array in the same position. The final [guarded edits](fpm-candidates/gslib/compatibility.patch.json) declare those placeholders as work arrays of length `nd`. No algorithm or arithmetic expression is changed, no argument-mismatch flag is added, and normal debug runtime checks remain enabled.

The self-contained consumer calls `cova3` and `ksol` to assemble and solve ordinary-kriging systems from observations of value 1 at x=0 and value 3 at x=2. It checks exponential covariances, closed-form weights, independent dense residuals, nonnegative variances and interpolation at the observation locations. The numerical and changed-main/cache-reuse checks passed; see [output](fpm-candidates/gslib/verified-output.txt). It needs no input file. This verifies the demonstrated covariance/solver path, not the complete simulation and command-line application suite. Both the [modernization MIT license](fpm-candidates/gslib/licenses/LICENSE) and [original GSLIB redistribution notice](fpm-candidates/gslib/licenses/LICENSE_original.txt) are retained.

## rational-approximation

Repository: [edvinolo/rational-approximation](https://github.com/edvinolo/rational-approximation), commit `4c9a04c7f6d0e85c613b486b6cd39a28e880f0f6`.

The pinned repository has no root LICENSE or COPYING file, and its [manifest](fpm-candidates/rational-approximation/fpm.toml) declares the placeholder `license = "license"`. The [source identity](fpm-candidates/rational-approximation/source-review.json), [README](fpm-candidates/rational-approximation/README.md) and [review](fpm-candidates/rational-approximation/license-review.txt) are retained. No compilation or redistribution of its library was performed, and it is outside Selected. An explicit upstream license is needed before further evaluation for distribution. Its registry stdlib dependency and preprocessing configuration will also need a pinned, reproducible preparation recipe; their compatibility has not yet been established.

## Featom

Repository: [atomic-solvers/featom](https://github.com/atomic-solvers/featom), commit `87872a3266ceeee61a7244e6ecd134dc3bda790f`.

The consumer adapts the setup from the author's `test/test_coulomb_schroed.f90` for the one-electron hydrogen Coulomb potential. It uses eight radial elements, polynomial order 20, 43 quadrature points per element and a radial cutoff of 100 atomic units. This yields 159 finite-element degrees of freedom. The six states with principal quantum number n<=3 are compared with the independent exact energies `-1/(2*n**2)` Hartree, with finite-value checks. The largest observed error was about `1.17e-12` Hartree, below the demo's `1e-7` acceptance tolerance.

The library source is unmodified; native BLAS/LAPACK versions are pinned. The ordinary hosted GNU 16 debug and changed-main/cache-reuse checks passed. The demo runs in memory and does not write the larger eigenfunction output file used by the upstream test. These checks establish the demonstrated nonrelativistic Coulomb calculation, not every relativistic Dirac, Hartree-Fock or self-consistent DFT path. The [MIT license](fpm-candidates/featom/licenses/LICENSE) accompanies the adaptation. Numerical output is retained with the public verification report.

## JAMS Fortran

Repository: [mcuntz/jams_fortran](https://github.com/mcuntz/jams_fortran), commit `687a5dd08b7239466547f333ccb68463ba5137ad`.

The intended scope was a subset of the numerical modules, initially Laplace inversion and sensitivity analysis. The ordinary bounded download of the pinned GitHub archive exceeds the 16 MiB compressed-download limit before extraction. A subset build would still require obtaining the complete archive under the current preparer. No compiler was invoked, and no complete archive SHA-256 is available because the transfer was stopped at the limit. The [preparation record](fpm-candidates/jams-fortran/preparation.json) retains the exact source revision, URL identity and limiting phase. This is a source-packaging restriction, not a demonstrated numerical or compiler defect.

JAMS is outside Selected. A smaller upstream source revision or source repository would permit a fresh attempt through the existing GitHub preparer. The preparation record also lists the largest Git tree blobs: two bundled NetCDF source archives total about 14.3 MiB, and two remapping test datasets are about 7.2 MiB each. These blob sizes are not compressed-archive measurements; the proposed Laplace/sensitivity subset would not use those files. No archive or resource limit was raised, and no partial archive was used to construct a library.

## FURY

Repository: [szaghi/FURY](https://github.com/szaghi/FURY), commit `093e4d558ae089107464eb4ea7adec4f1178b907`.

The root archive contains the documentation symlink `CONTRIBUTING.md -> docs/guide/contributing.md`, which the strict archive preparer rejects. The five most recent releases were checked as well: v0.8.4 has that same link, and v0.8.0 through v0.8.3 contain `doc/README-FURY.md -> ../README.md`. The [HEAD preparation record](fpm-candidates/fury/preparation.json), [tag commits, checksums and link paths](fpm-candidates/fury/tag-archive-checks.json), and [upstream manifest](fpm-candidates/fury/fpm.toml) are retained. Only the regular manifest member was read for inspection; no link was extracted, followed or substituted.

Compilation and dependency preparation were not reached. FURY is outside Selected, so no kinetic-energy or unit-conversion result is established. Replacing the documentation symlinks with ordinary files in an upstream archive would permit further evaluation. The ordinary archive checks remain unchanged.

## econ-toolchain

Repository: [renatomatz/econ-toolchain](https://github.com/renatomatz/econ-toolchain), commit `301d1659ba3d34973195985c552ca6fcfe2d9f29`.

The consumer adapts the calling conventions in the author's `test/markov_test.f90` and `test/tauchen_test.f90`. It first solves a nonuniform two-state chain with exact stationary probabilities `(2/3,1/3)`, checking finite values, the analytic answer and an independent matrix residual. It then discretizes a zero-mean AR(1) process with persistence 0.8 and innovation standard deviation 0.1 into 31 states. Probability normalization, nonnegativity, equilibrium residual, symmetry and approximate variance are checked. The computed variance was `0.0277451680`, compared with the continuous-process value `0.0277777778`; this finite-grid/truncation approximation is not expected to be exact. Both equilibrium residuals were below `1.2e-14`. See [verified output](fpm-candidates/econ-toolchain/verified-output.txt).

The conventions matter: `markov_steady_state` multiplies a probability column by a column-stochastic matrix, whereas `tauchen` constructs a row-stochastic matrix. The demo transposes Tauchen's result explicitly. The upstream two-state test uses a symmetric matrix that does not reveal this distinction. No numerical library source is patched.

The [initial preparation](fpm-candidates/econ-toolchain/initial-preparation.json) stopped at stdlib's manifest `VERSION` placeholder. The [initial recipe](fpm-candidates/econ-toolchain/initial-package.json) records that attempt. Final preparation renders the pinned stdlib manifest version as `0.8.1`, the value in its upstream VERSION file, and locks both stdlib and simulated-annealing to existing catalog source revisions. OpenBLAS packages are pinned. `-fcoarray=single` permits compilation of the package's coarray-containing modules; this does not enable multi-image execution in FPM mode. Normal debug checks remain enabled.

The complete library and both dependencies passed ordinary hosted GNU 16 debug and changed-main/cache-reuse checks. An edited main rebuilt only the main and executable in about 1.77 seconds. Logical library artifacts occupy about 341.6 MiB, including the stdlib dependency and FPM flag variants; this is not compressed storage or a billing measurement. The [MIT license](fpm-candidates/econ-toolchain/licenses/LICENCE) accompanies the adaptation. Verification covers these Markov-chain routines, not every optimization, simulation or coarray path in the package.
