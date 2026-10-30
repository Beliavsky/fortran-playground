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

## M_LA

Repository: [urbanjost/M_LA](https://github.com/urbanjost/M_LA), commit `db59eeab0deab7e84eadf2542ad49c1c719dfb94`.

The [consumer](../fpm_catalog/demos/m_la.f90) checks magic squares of orders 3, 4, 5 and 6, exercising odd, doubly even and singly even construction. Every row, column and both diagonals must have the exact expected sum, and the entries must be a permutation of 1 through n squared. The common sums are 15, 34, 65 and 111. The example follows the calling convention documented beside the upstream `mat_magic` routine; the checks are original. It does not validate every linear algebra routine in M_LA. See the [pinned source and build record](fpm-candidates/m_la/source-review.json), [verified output](fpm-candidates/m_la/verified-output.txt) and [Unlicense](fpm-candidates/m_la/licenses/LICENSE).

## FGLM

Repository: [jordan4ibanez/fglm](https://github.com/jordan4ibanez/fglm), commit `e1b6a5404b3e7a266da33173a07166970c16dd86`.

The [consumer](../fpm_catalog/demos/fglm.f90) checks double-precision vector addition and component multiplication, followed by single-precision homogeneous translation and a 90-degree rotation about z. Expected values are computed independently of the library. FGLM stores its 4-by-4 matrices in column-major order, so the example reshapes the 16-element data array before applying it to a point. Its `constants_f90` dependency is pinned and has its own shared export. See the [source and build record](fpm-candidates/fglm/source-review.json), [verified output](fpm-candidates/fglm/verified-output.txt) and [MIT license](fpm-candidates/fglm/licenses/LICENSE). This is representative vector/matrix coverage, not a validation of every transform.

## FortranDF

Repository: [jaiken17/fortranDF](https://github.com/jaiken17/fortranDF), commit `58300f8ae39d463e729960e960939fb53e2c7de4`.

The [consumer](../fpm_catalog/demos/fortrandf.f90) creates named integer, character and real columns, checks column retrieval, applies a temperature calibration and checks the updated values. The means before and after calibration are 13 and 13.5 degrees Celsius. Character access uses `getch`; `getc` is the complex accessor. The library source is unmodified. Its manifest has a placeholder license field, but the root [LICENSE](fpm-candidates/fortrandf/licenses/LICENSE) supplies BSD-3-Clause terms. See the [source and build record](fpm-candidates/fortrandf/source-review.json) and [verified output](fpm-candidates/fortrandf/verified-output.txt). CSV/file handling and every supported column operation are outside this example's coverage.

## Strith

Repository: [degawa/strith](https://github.com/degawa/strith), commit `da2b1f489a178cb443f636e3f9c89aed6c8702b1`.

The [consumer](../fpm_catalog/demos/strith.f90) formats an all-one int64 bit pattern as unsigned, adds one to the decimal representation of the unsigned 64-bit maximum, checks a subtraction round trip and adds the signed 64-bit minimum and maximum to obtain -1. Its string constructor requires a sign and a fixed-width, zero-padded decimal representation; the example explicitly supplies that representation. This is fixed-capacity decimal-string arithmetic, not unlimited arbitrary precision. No compiler integer overflow is used to obtain the expected answers. The manifest's placeholder license field is supplemented by the root [MIT license](fpm-candidates/strith/licenses/LICENSE). See the [source and build record](fpm-candidates/strith/source-review.json) and [verified output](fpm-candidates/strith/verified-output.txt).

## List

Repository: [grofz/list](https://github.com/grofz/list), commit `77a0c99686406eaa8d4423e778311d63c6940b43`.

The [consumer](../fpm_catalog/demos/list.f90) appends five integer values, checks duplicate counts, sorts them with a module comparator, traverses and checks every element, finds and removes a value, and clears the list. Its compiler-generated callback does not require an executable-stack trampoline. Several upstream methods are explicitly unimplemented, so this example uses the implemented linked-list API and makes no claim about every tree/container operation. The manifest has a placeholder license field; [LICENSE.txt](fpm-candidates/list/licenses/LICENSE.txt) supplies MIT terms. See the [source and build record](fpm-candidates/list/source-review.json) and [verified output](fpm-candidates/list/verified-output.txt).

## Maps

Repository: [degawa/maps](https://github.com/degawa/maps), commit `453d8b146a659c0111652fe0579e2321477c54cd`.

Maps remains outside Selected. Preparation and all pinned dependency downloads passed the ordinary limits. The manifest declares `stdlib = '*'`; the attempted recipe maps it to our existing stdlib revision `58eb9133966c2797e0593281169ef57c43eccc1d`, with its manifest version rendered as 0.8.1. The existing stdlib export was reused without compilation. GNU 16 compilation then stopped in `src/common/proc/toHashValue.f90`: `stdlib_hashmap_wrappers` no longer exports the `other_type` imported by Maps. No library source was patched and no older stdlib version was validated. This establishes an API incompatibility with the tested revision, rather than a claim that Maps cannot work with another stdlib version.

The [source and attempted recipe](fpm-candidates/maps/source-review.json), [original manifest](fpm-candidates/maps/fpm.toml), [build diagnostic](fpm-candidates/maps/build-error.txt), [MIT license](fpm-candidates/maps/licenses/LICENSE) and [attempted word-count driver](fpm-candidates/maps/main.f90) are retained. Since compilation stopped first, the driver's runtime behavior is unverified. A compatible stdlib pin or an upstream migration to its newer hash-map API would permit another attempt.

To prepare the same source graph locally, run this Python code from the repository root with the repository's Python dependencies installed. It creates a new `maps-reproducer` directory; use another directory name for a second attempt.

```python
import json
from pathlib import Path
from fpm_project_run import prepare

case = Path('docs/fpm-candidates/maps')
package = json.loads((case / 'source-review.json').read_text(encoding='utf-8'))
project = Path('maps-reproducer').resolve()
project.mkdir()
(project / 'app').mkdir()
(project / 'app/main.f90').write_bytes((case / 'main.f90').read_bytes())
settings = {'package': package, 'request': {
    'url': 'https://github.com/' + package['repository'],
    'revision': package['revision'], 'workflow': 'consumer', 'action': 'run'}}
prepare(project, settings)
```

Then run `fpm build --profile debug --compiler gfortran` from `maps-reproducer`, with GNU Fortran 16 on PATH, to reproduce the compile error. This is a clean source build, without the hosted shared stdlib archive.

## Friction

Repository: [jchristopherson/friction](https://github.com/jchristopherson/friction), commit `8e75dcac26f47417a439adfcbaa24834105d89fe`.

The [consumer](../fpm_catalog/demos/friction.f90) follows the API conventions in the author's `test/friction_model_tests.f90`. It evaluates Coulomb and Stribeck models at five positive, negative and zero velocities under a 20 N normal load. Independent formulas check the signed forces, and both models must report no internal state. The library's signed-friction convention is printed explicitly; applications must apply their chosen force-balance convention. This does not validate fitting, Lu-Gre, Maxwell or other dynamic internal-state models.

The five dependency revisions are locked, including the existing Diffeq, Linalg, Fstats and Collections source pins. BLAS, LAPACK and ARPACK packages are pinned, and OpenMP is enabled for this build context. Those settings require their own compatible shared exports rather than silently mixing default and OpenMP variants. No numerical source is patched. See the [source/build record](fpm-candidates/friction/source-review.json), [verified output](fpm-candidates/friction/verified-output.txt) and [MIT license](fpm-candidates/friction/licenses/LICENSE). GAMS fitting/ODE mappings describe additional reviewed source procedures, not additional validated demonstrations.

## FEqParse

Repository: [FluidNumerics/feq-parse](https://github.com/FluidNumerics/feq-parse), commit `2e80c5940b128a52c5070a3f56909674fb85a379`.

The [consumer](../fpm_catalog/demos/feq-parse.f90) creates parsers for a three-variable Gaussian and a polynomial. At seven input points it compares double-precision evaluation with direct Fortran formulas, checking finite results and errors below `1e-12`. This exercises variable binding, elementary functions, powers and precedence. The calling convention follows the author's multivariable Gaussian example, with new independent checks. Array evaluation, custom functions and every possible input expression are outside its coverage.

The library source is unmodified and has no external dependencies. Although the manifest says `license = "Other"`, the root [LICENSE](fpm-candidates/feq-parse/licenses/LICENSE) supplies BSD-3-Clause terms. See the [source/build record](fpm-candidates/feq-parse/source-review.json) and [verified output](fpm-candidates/feq-parse/verified-output.txt).

## ForDot

Repository: [gha3mi/fordot](https://github.com/gha3mi/fordot), commit `3966625781a9c1dffe037e3032fa4a0b6f958760`.

The [consumer](../fpm_catalog/demos/fordot.f90) checks methods m1 through m4 against the exact dot product 120, using both ordinary evaluation and three unequal blocks of eight elements. This includes the intrinsic, BLAS, explicit-loop and array-expression implementations. It runs in one process and makes no timing, parallel-scaling or coarray claim.

The manifest's `VERSION` placeholder is rendered as the documented version 0.2.0. Kinds, ForUnitTest and FACE are locked, with the previously accepted FACE revision; unused development tests are not pulled into the consumer. Native BLAS/LAPACK packages and compiler/link flags are recorded. Its compatible dependency exports are shared with ForMatmul. See the [source/build record](fpm-candidates/fordot/source-review.json), [verified output](fpm-candidates/fordot/verified-output.txt) and [BSD-3-Clause license](fpm-candidates/fordot/licenses/LICENSE). No computational source is patched.

## ForMatmul

Repository: [gha3mi/formatmul](https://github.com/gha3mi/formatmul), commit `4b5747d49c27f0df92288e7a61d0e479e34ac78e`.

The [consumer](../fpm_catalog/demos/formatmul.f90) checks methods m1 through m4 for rectangular matrix multiplication, all four transpose combinations and matrix-vector products. A separate scalar-loop reference gives the matrix product with rows `(58,64)` and `(139,154)`. It checks both omitted transpose flags and both flags explicitly false. This is single-process correctness coverage; it does not validate every available kernel or coarray branch. Kinds, ForUnitTest and FACE exports are shared with ForDot, and Fortime has its own pinned export. Native BLAS/LAPACK packages and compiler/link settings are pinned. The source is unmodified; [LICENSE](fpm-candidates/formatmul/licenses/LICENSE) supplies BSD-3-Clause terms.

**Confirmed transpose-flag limitation:** passing only `transA=.false.` or only `transB=.false.` incorrectly selects a transposed branch in `mat_mat_rel`, producing an extent error for the rectangular example. Omitting both flags works, as does explicitly passing both flags. The supplied main therefore passes both flags whenever either is specified. The [two failing probes and successful workaround](fpm-candidates/formatmul/false-transpose-checks.json) include the hosted GNU 16 diagnostics. Their standalone sources are [transA false](fpm-candidates/formatmul/transa-false.f90), [transB false](fpm-candidates/formatmul/transb-false.f90) and [both false](fpm-candidates/formatmul/both-false.f90). They can be tried as edited mains using the same pinned package; no upstream issue was submitted.

The [source/build record](fpm-candidates/formatmul/source-review.json) also retains the initial example hash and links its [initial main](fpm-candidates/formatmul/initial-main.f90). The current [verified output](fpm-candidates/formatmul/verified-output.txt) belongs to the final main with the explicit two-flag workaround. The shared cache checks its current source hash independently.

## Bstrith

Repository: [degawa/bstrith](https://github.com/degawa/bstrith), commit `7ed7730e34c7e1f78f2be9426ccc170f9dcaf57e`.

The [consumer](../fpm_catalog/demos/bstrith.f90) exhaustively checks all 256 eight-bit values. It verifies increment with modulo-256 wraparound, subtraction round trips, XOR with the complement, and every left/right shift amount from one through seven. Expected strings come from independent intrinsic integer operations and binary formatting. The printed examples include `11111111 + 00000001 = 00000000`. This is fixed-width binary-string arithmetic; it does not claim unlimited precision or validate every unequal-length/invalid-input case.

The manifest has a placeholder license field; the root [MIT license](fpm-candidates/bstrith/licenses/LICENSE) supplies the actual terms. The library has no dependencies and its computational source is unmodified. See the [source/build record](fpm-candidates/bstrith/source-review.json) and [verified output](fpm-candidates/bstrith/verified-output.txt).

## HeatFlow

Repository: [ExeQuantCode/HeatFlow](https://github.com/ExeQuantCode/HeatFlow), commit `b0d930caad9160a15f0aeafa238c448f48f28d55`.

The [consumer](../fpm_catalog/demos/heatflow.f90) uses HeatFlow's sparse matrix conversion and BiCG solver (`SRSin`, `linbcg`) for an independent backward-Euler discretization of `u_t = u_xx` on `[0,1]`. It uses zero endpoint temperatures, initial temperature `sin(pi*x)`, 31 interior points, a time step of 0.001 and 50 steps. Every step checks an independent dense matrix residual. The final solution is checked against the exact discrete sine-mode solution to `1e-9` and against `exp(-pi*pi*t)*sin(pi*x)` with a 0.004 discretization-error bound.

The observed continuous-solution error was about 0.001719; the final linear-system residual was below `1e-15`. The example uses the sparse solver's `globe_data%ra` matrix and releases its allocated storage. It does not invoke the complete three-dimensional evolution/Cattaneo executable, its file readers or its material models. Everything in this demonstration runs in memory, with no data files or large output files.

The ordinary FPM library preparation excludes the upstream application main while retaining its modules; no source-subset recipe or computational patch is needed. See the [source/build record](fpm-candidates/heatflow/source-review.json), [verified output](fpm-candidates/heatflow/verified-output.txt) and [GPL-3.0 license](fpm-candidates/heatflow/licenses/LICENSE).

## HR-WENO

Repository: [HugoMVale/HR-WENO](https://github.com/HugoMVale/HR-WENO), commit `2885105a7ba98351fed299b22e9bc0c67a809d2f`.

The [consumer](../fpm_catalog/demos/hrweno.f90) solves periodic linear advection with 64 finite-volume cells, fifth-order WENO reconstruction and third-order TVD Runge-Kutta time integration. Three ghost cells at either end impose the periodic boundary condition; the two boundary fluxes agree exactly. The initial and reference solutions are exact cell averages of a sine wave. At time 0.25, the maximum error was about `4.85e-7`, and the mass remained one to the printed twelve decimal places. This checks a smooth solution, rather than discontinuities, nonuniform grids or all reconstruction orders.

Its stdlib dependency uses the existing pinned generated snapshot and shared compiled export. No numerical source is patched. See the [source/build record](fpm-candidates/hrweno/source-review.json), [verified output](fpm-candidates/hrweno/verified-output.txt) and [licenses](fpm-candidates/hrweno/licenses/).

## Fortran-simplify

Repository: [jaiken17/fortran-simplify](https://github.com/jaiken17/fortran-simplify), commit `f546422216fb88eba97e2a0f4910935efbcdce83`.

The [consumer](../fpm_catalog/demos/fortran-simplify.f90) makes a single call to `perpendicular_distance` for a 251-point sine curve. The reduced curve has 126 points; independent endpoint checks and piecewise-linear interpolation give a maximum vertical error of about `0.000316`, below the supplied tolerance 0.005. The original and reduced curves are plotted together, and the changed-main sandbox returned a visually reviewed `simplified.png`. Its [plot check](fpm-candidates/fortran-simplify/plot-check.json) records the preview hash. The stdlib dependency is shared; the computational source is unmodified.

**Confirmed upstream limitations:** this pin's radial-distance helper computes a dot product rather than squared Euclidean distance. The [radial-distance reproducer](fpm-candidates/fortran-simplify/radial-distance.f90) therefore retains a near-duplicate interior point that should be removed. Separately, initialized local flags in `perpendicular_distance` retain their state between calls. The [repeated-call reproducer](fpm-candidates/fortran-simplify/repeated-perpendicular.f90) first simplifies a straight line, then loses the endpoints and corner of a three-point curve, returning just one point. The supplied example calls this routine only once and includes a visible source comment about these limitations. It is not a workaround for general repeated use.

Both failing checks were run with the same hosted GNU 16 package image. Their [diagnostics](fpm-candidates/fortran-simplify/limitation-checks.json), [source/build record](fpm-candidates/fortran-simplify/source-review.json), [successful example output](fpm-candidates/fortran-simplify/verified-output.txt) and [BSD-3-Clause license](fpm-candidates/fortran-simplify/licenses/LICENSE) are retained. No upstream issue was submitted.

## ECX

Repository: [MilanSkocic/ecx](https://github.com/MilanSkocic/ecx), commit `d30725e3cb9186bc79f81481f3d6fae8d177a7b7`.

The [consumer](../fpm_catalog/demos/ecx.f90) evaluates a 100-ohm resistor and 1-millifarad capacitor at four angular frequencies. It checks both finite real/imaginary parts and their series combination against the direct formula `R - i/(omega*C)`. It prints an impedance table; no experimental data or network access is needed. Other electrochemical and photoelectrochemical models are not validated by this example.

The unmodified source failed because `ecx__pec` uses the kind name `real64` without importing it. A checksum-guarded catalog edit adds only `use, intrinsic :: iso_fortran_env, only: real64` to that module; no formulas are changed. The [original diagnostic](fpm-candidates/ecx/original-build-failure.json) and the exact edit in the [source/build record](fpm-candidates/ecx/source-review.json) make the local change reproducible. Stdlib uses its existing compiled export; CIAAW, CODATA and M_CLI2 revisions are locked. Manifest `VERSION` placeholders are rendered explicitly. See the [verified output](fpm-candidates/ecx/verified-output.txt) and [license files](fpm-candidates/ecx/licenses/).

## Orbs

Repository: [degawa/orbs](https://github.com/degawa/orbs), commit `3cf7fcec19798367f6f5bd26bad861c510449265`.

The [consumer](../fpm_catalog/demos/orbs.f90) combines bitset addition and logical masks to find the next x neighbor of an interleaved two-dimensional Morton key. Every cell of a 4-by-4 grid, including wraparound, is checked against an independent reference using intrinsic integer bit operations. For example, key `0011` has x neighbor `1001`. This checks fixed-width arithmetic and masking; it does not validate every bitset operation or invalid input.

The Bstrith revision is locked to the catalog's accepted pin, and stdlib reuses the compatible compiled export. Source code is unmodified. See the [source/build record](fpm-candidates/orbs/source-review.json), [verified output](fpm-candidates/orbs/verified-output.txt) and [MIT license](fpm-candidates/orbs/licenses/LICENSE).

## ReArrayFX

Repository: [aradi/rearrayfx](https://github.com/aradi/rearrayfx), commit `be1a7b08e43b358c8ed27fa80db7896767eb9f6d`.

The [consumer](../fpm_catalog/demos/rearrayfx.f90) grows a rank-two real array with twice the requested backing capacity. It checks preservation of data when growth fits in spare storage and when a new allocation is required, then checks shrinking and assignment from a plain array. The final 2-by-6 matrix contains the integers 1 through 12 and sums to 78. The upstream module prints a debug message when it allocates backing storage; this output is retained. The block scope invokes the container's finalizer.

This is an educational proof of concept with one real-array type. The example does not claim support for copying containers, all element types or concurrent use. It has no dependencies, and its own small compiled library is exported separately for reuse. See the [source/build record](fpm-candidates/rearrayfx/source-review.json), [verified output](fpm-candidates/rearrayfx/verified-output.txt) and [BSD-2-Clause-Patent license](fpm-candidates/rearrayfx/licenses/LICENSE).

## Athena

Repository: [nedtaylor/athena](https://github.com/nedtaylor/athena), commit `4b81aeac07113628c2c9a476648d5ac2a91b7c91`.

The [consumer](../fpm_catalog/demos/athena.f90) performs deterministic inference with one fully connected layer: three inputs, two outputs, fixed weights and biases, and tanh activation. The result is checked against ordinary Fortran `matmul` and `tanh`. This is a small in-memory example, with no training data, training loop or external service. It does not validate training, automatic differentiation or the many convolutional/graph/network APIs.

The initial build failed because FPM 0.12 does not accept the manifest's newer optional `features` table. A checksum-guarded manifest edit removes the W&B feature declaration. FPM 0.12's dependency scanner also sees the preprocessor-disabled `use wf`; the same manifest edit declares `wf` an external module. The compiler removes that branch when `_WANDB` is not defined. **W&B tracking is unavailable in this recipe.** No mathematical source is changed, and simply adding the W&B macro will not install the missing integration.

Coreutils, Diffstruc and Graphstruc are pinned to the revisions resolved from the author's release tags. BLAS/LAPACK development packages have exact versions. This patched-root recipe retains its own compiled artifacts rather than using complete graph sharing, which currently excludes patched roots; the changed-main test still rebuilds only the main and executable. The [initial diagnostics](fpm-candidates/athena/original-build-failures.json), exact manifest edit in the [source/build record](fpm-candidates/athena/source-review.json), [verified output](fpm-candidates/athena/verified-output.txt) and [MIT license](fpm-candidates/athena/licenses/LICENSE) are retained.

## AMOS F90

Repository: [Euler-37/amosf90](https://github.com/Euler-37/amosf90), commit `b54a4d4a1d8f7c97acd180ed5bbaae8d089a9fa7`.

The [consumer](../fpm_catalog/demos/amosf90.f90) demonstrates functionality beyond the standard Fortran Bessel intrinsics: complex arguments, noninteger orders, and modified Bessel functions. At `z = 1 + 0.5i`, it checks `J_0.3(z)` and `I_0.3(z)` against independent convergent power series using the intrinsic real gamma function. It also checks the closed-form expression `K_0.5(z) = sqrt(pi/(2*z))*exp(-z)`. Every routine must return a successful status with no underflows, finite components and an absolute error below `1e-11`.

The source is unmodified and has no dependencies. Its small compiled library is exported separately for reuse. The upstream README explicitly warns of possible bugs; these checks do not validate every order, argument region, scaled mode, Airy routine or Hankel routine. See the [source/build record](fpm-candidates/amosf90/source-review.json) and [verified output](fpm-candidates/amosf90/verified-output.txt).

The manifest's license value is the placeholder `license`; no license notice was found in the reviewed archive. The catalog records `NOASSERTION`, rather than inferring terms from the original AMOS distribution or from the repository being public. The [license-status record](fpm-candidates/amosf90/license-status.json) preserves this unresolved metadata.

## linalg_fortran

Repository: [Euler-37/linalg_fortran](https://github.com/Euler-37/linalg_fortran), commit `30e7237ab54ca176e1c8dae4be2d9d44800e1f83`.

The [consumer](../fpm_catalog/demos/linalg_fortran.f90) checks the real64 inverse, determinant and symmetric eigenproblem interfaces using a 3-by-3 tridiagonal matrix with diagonal 2 and off-diagonal 1. Independent references give determinant 4 and eigenvalues `2-sqrt(2)`, 2 and `2+sqrt(2)`. The main also checks inverse and eigenpair residuals and eigenvector orthonormality. The observed inverse residual was about `1.11e-16`. Single-precision, complex and other wrappers are not validated by this example.

The original build fails the implicit-interface check at the legacy LAPACK helper `ilaenv`. A checksum-guarded manifest edit explicitly enables `implicit-external` for this package's original Fortran 77 BLAS/LAPACK interfaces. Numerical sources and normal runtime checks are retained. OpenBLAS development packages are pinned to `0.3.29+ds-3`; the patched-root recipe keeps its own compiled artifacts. See the [original diagnostic](fpm-candidates/linalg_fortran/original-build-failure.json), exact edit in the [source/build record](fpm-candidates/linalg_fortran/source-review.json) and [verified output](fpm-candidates/linalg_fortran/verified-output.txt).

This archive also has the placeholder license value `license`, with no license notice found in the reviewed files. Its catalog value is `NOASSERTION`; see the [license-status record](fpm-candidates/linalg_fortran/license-status.json).

## fortran_vector

Repository: [Euler-37/fortran_vector](https://github.com/Euler-37/fortran_vector), commit `95469e2ce1162b0ede3ca3435ebd94ec6b6fee79`.

The [consumer](../fpm_catalog/demos/fortran_vector.f90) starts with capacity two, appends the integers 1 through 8 and a short array containing duplicates, then checks stable duplicate elimination. It exercises removal by value, deletion by position, popping and storage compaction. Independent expected contents are `1 3 5 6 7 8` after editing. The example does not cover invalid indices, popping an empty vector or calling `unique` on an empty vector.

**Confirmed upstream aliasing bug:** the original `unique` passes `this%x_(1)` to `remove`, which compacts that same array and changes the argument value during iteration. The main therefore fails its duplicate-count check. The catalog changes exactly one call to `this%remove(first)`, using the scalar value the routine has already saved. The [original GNU 16 failure](fpm-candidates/fortran_vector/original-unique-failure.json), checksum-guarded edit in the [source/build record](fpm-candidates/fortran_vector/source-review.json), and [successful output](fpm-candidates/fortran_vector/verified-output.txt) are retained. The example source itself is unchanged between the failing and successful runs. No upstream issue was submitted.

Its manifest contains the placeholder license value `license`, and no license notice was found in the reviewed archive. The catalog records `NOASSERTION`; see the [license-status record](fpm-candidates/fortran_vector/license-status.json).

## Scanner

Repository: [freevryheid/scanner](https://github.com/freevryheid/scanner), commit `b0026498c171b615bb3dcfca55a0f20b133e22dc`.

The [consumer](../fpm_catalog/demos/scanner.f90) reconstructs `steps=12;dt=0.25` using the scanner's character API. It checks navigation to delimiters, cursor-preserving lookahead, and rejection of movement before the beginning and beyond the end. Ordinary internal `read` converts the recovered fields, which must equal 12 and 0.25. This illustrates the scanner as a building block for a small parser, rather than a complete configuration-file language.

The numerical source is unmodified. Its stdlib dependency uses the existing pinned generated snapshot and compatible compiled export. See the [source/build record](fpm-candidates/scanner/source-review.json), [verified output](fpm-candidates/scanner/verified-output.txt) and [MIT license](fpm-candidates/scanner/licenses/LICENSE).

## FLAP and StringiFor

Repositories: [szaghi/FLAP](https://github.com/szaghi/FLAP) and [szaghi/StringiFor](https://github.com/szaghi/StringiFor). Both remain deferred at source preparation; no compiler failure is claimed.

The inspected HEAD archives contain a `CONTRIBUTING.md` symlink. The ordinary preparer rejects symlinks in every archive, even documentation links. Earlier root commits—FLAP `17d58bd8c867206baec6f56cbf8156a1afd3cc4a` and StringiFor `019fe9c15a89305b7d2052d9e1bf39ec5f215f7e`—pass extraction, but both explicitly pin FACE `1455c549ae0c1ead96961ca61a73131d8176b6a4`. That dependency archive contains `doc/README-FACE.md -> ../README.md` and is rejected by the same rule. StringiFor's pinned BeFoR64 and PENF archives passed extraction before FACE stopped preparation.

These explicit dependency commits were not silently replaced. The [FLAP record](fpm-candidates/flap/source-review.json) and [StringiFor record](fpm-candidates/stringifor/source-review.json) retain the latest-root rejections, older-root pins, original manifests, available dependency locks, blocked FACE archive checksum and exact link paths. Their folders also retain the upstream license files. A useful next step is a source snapshot with no archive links and dependency pins to snapshots that pass the same rule. Neither package has been advertised as precompiled or working in the sandbox.

## Rojff

Repository: [everythingfunctional/rojff](https://github.com/everythingfunctional/rojff), commit `9f68e5aa4c12b32720d4224f1ac279bfd7d77b93`.

The [consumer](../fpm_catalog/demos/rojff.f90) parses a JSON record containing integer, real and string fields, checks their expected values, and verifies a compact serialization round trip. Missing keys and malformed JSON must return explicit failure values. The source is unmodified; this example does not cover the entire JSON grammar, Unicode handling, every constructor or performance.

The author uses GitLab dependencies. Explicit aliases select their GitHub mirrors, with every source revision and archive checksum locked. The requested Erloff 2.2.0 uses Strff 4.0.0, whose `exceptional_numbers` dependency has no available mirror at the configured GitHub URL. Trying the older Erloff 2.1.3 instead fails compilation because Rojff requires a newer error-list constructor. The accepted recipe retains **Erloff 2.2.0**, uses **Strff 3.1.1**, and pins **ISO varying string 3.0.3**. Its complete consumer, including both error paths, passes with that configuration. No mathematical, JSON or error-handling source is patched.

Rojff and Veggies reference the same compatible ISO varying string and Strff compiled exports. See the [dependency investigation](fpm-candidates/rojff/dependency-investigation.json), [source/build record](fpm-candidates/rojff/source-review.json), [verified output](fpm-candidates/rojff/verified-output.txt) and [MIT license](fpm-candidates/rojff/licenses/LICENSE).

## argparse-f

Repository: [0382/argparse-f](https://github.com/0382/argparse-f), commit `435cc1676d6064162a3c36b91f1aa50d926fdd45`.

The [consumer](../fpm_catalog/demos/argparse-f.f90) exercises the real process command-line API. Because a playground main starts without arguments, it launches its own executable once with a fixed example command line: `-t 4 --scale 0.25 --name demo --verbose`. The child checks integer, double-precision and string values, a logical flag, and an untouched default of 20 iterations. The parent checks successful execution. No input files, custom backend argument handling or internal parser state manipulation are needed.

`has_option` is used for the logical flag, as in the author's example; typed values use their corresponding getters. The checked main does not validate error exits, named/positional arguments, long argument truncation or every parsing rule. The source is unmodified and has no dependencies. See the [source/build record](fpm-candidates/argparse-f/source-review.json), [verified output](fpm-candidates/argparse-f/verified-output.txt) and [MIT license](fpm-candidates/argparse-f/licenses/LICENSE).

## io_utilities

Repository: [arjenmarkus/io_utilities](https://github.com/arjenmarkus/io_utilities), commit `f0551aad0b46aa7aac1c442a3c576ecc90028f72`.

The [consumer](../fpm_catalog/demos/io_utilities.f90) creates a tiny INI-style file inside the sandbox, then uses `keyvars` descriptors and `get_values` to fill target variables. It checks integer 12, double 0.25, a logical value written as `yes`, and a string containing a space. The file includes a section header and a trailing comment, and is deleted after the check. Descriptor section matching remains the default wildcard; section-specific filtering, malformed input and the package's other I/O modules are not validated.

The upstream manifest writes `[[library]]`, an array where FPM requires a single `[library]` table. A checksum-guarded manifest edit corrects that declaration while retaining `source-dir = "src"`. No Fortran source is changed. The original manifest and exact replacement are preserved in the [source/build record](fpm-candidates/io_utilities/source-review.json); see also [verified output](fpm-candidates/io_utilities/verified-output.txt) and the [MIT license](fpm-candidates/io_utilities/licenses/LICENSE).

## uint-fortran

Repository: [ShinobuAmasaki/uint-fortran](https://github.com/ShinobuAmasaki/uint-fortran), commit `487f806c76a5d107c5a8982198bafb295065eba7`.

The [consumer](../fpm_catalog/demos/uint-fortran.f90) checks fixed-width unsigned derived types. It verifies `2147483648 + 3 = 2147483651`, unsigned comparison, 32-bit modular addition and subtraction, conversion of a negative assignment, and the 16-bit upper boundary and wraparound. Expected values use ordinary wider signed integers. The current conversion generic is imported explicitly from `int_m`; the checked source does not rely on the README's older `unsigned_m` re-export behavior.

The library source is unmodified and has no dependencies. These checks do not validate every kind or operation, arbitrary-precision arithmetic, or calls across a C interface. See the [source/build record](fpm-candidates/uint-fortran/source-review.json), [verified output](fpm-candidates/uint-fortran/verified-output.txt) and [MIT license](fpm-candidates/uint-fortran/licenses/LICENSE).

## Veggies

Repository: [everythingfunctional/veggies](https://github.com/everythingfunctional/veggies), commit `8388f5e2633afa3d08cf5c6e7db1eeb0dcab2dc8`.

The [consumer](../fpm_catalog/demos/veggies.f90) defines three specification-style tests for a small user-written Simpson integration formula. Constant, linear and quadratic inputs over `[0,2]` must give 6, 2 and `8/3`, respectively. The framework prints each case description and a three-test passing summary; the main also checks `run_tests`' logical result. Module callbacks avoid internal-procedure trampolines. The Simpson formula is part of the example, not a numerical method supplied by Veggies.

The source is unmodified. Explicit GitLab-to-GitHub aliases and source locks retain ISO varying string 3.0.3 and Strff 3.1.1, sharing compatible compiled exports with Rojff. The demonstration does not cover parallel tests, generators, shrinking or the full assertion API. See the [source/build record](fpm-candidates/veggies/source-review.json), [verified output](fpm-candidates/veggies/verified-output.txt) and [MIT license](fpm-candidates/veggies/licenses/LICENSE.md).

## shunting-yard-fortran

Repository: [14NGiestas/shunting-yard-fortran](https://github.com/14NGiestas/shunting-yard-fortran), commit `ff62d83502bc5fdf77f2750c3538b8634a543b91`.

The [consumer](../fpm_catalog/demos/shunting-yard-fortran.f90) supplies module callbacks for numeric operands and arithmetic, then checks five expressions: `2+3*4 = 14`, `(2+3)*4 = 20`, `2^3^2 = 512`, `sqrt(9) = 3` and `-2+6 = 4`. Thus it exercises precedence, parentheses, right associativity, a unary function and unary minus. The tokenizer dependency has an exact source and archive lock.

**Sandbox compatibility edit:** the original library defines `by_expression` as an internal function of `parse` and passes it as a callback. This layout compiled but crashed with SIGSEGV in the restricted GNU 16 sandbox. The callback uses no host variables. A checksum-guarded edit moves it to module scope, retaining its body and the parsing operations unchanged; all five cases then pass. The [original main](fpm-candidates/shunting-yard-fortran/original-main.f90), [original crash](fpm-candidates/shunting-yard-fortran/original-sandbox-failure.json), and exact edit in the [source/build record](fpm-candidates/shunting-yard-fortran/source-review.json) are retained. No upstream issue was submitted.

The author's README describes this as an experimental parser and documents global token registration, fixed operator precedences and absent syntax validation. The example deliberately uses one parser with valid expressions; it is not a demonstration of concurrent parsers or robust malformed-input handling. See [verified output](fpm-candidates/shunting-yard-fortran/verified-output.txt) and the [MIT license](fpm-candidates/shunting-yard-fortran/licenses/LICENSE).

## fwalk

Repository: [freevryheid/fwalk](https://github.com/freevryheid/fwalk), commit `cc95f3d0c55cd90dc96c536e29c4b07ee813efaa`.

**Deferred during source preparation.** Archive contains symbolic links into its libcwalk Git submodule. Archive extraction rejects links and the submodule implementation is not contained in the archive. Requires an explicit, pinned C-submodule source adapter before an ordinary offline consumer can build. No sandbox build was submitted; no library changes made. The original manifest, license and exact symbolic-link targets are retained in the [source preparation record](fpm-candidates/fwalk/source-review.json). This is a packaging limitation of our preparation path, not an observed Fortran compiler failure.

## sqliteff

Repository: [everythingfunctional/sqliteff](https://github.com/everythingfunctional/sqliteff), commit `9b377c976698a7da671536e5e2539146ab734ca6`.

SQLite wrapper with bundled SQLite 3.30.1 C sources. The checked main opens an in-memory database, creates a table, inserts three values, verifies count and average, reaches SQLITE_DONE and closes resources. It does not cover persistent files, concurrent use, transactions or the complete SQLite API. Explicit GitLab-to-GitHub alias pins ISO varying string; no source edits.

See the [checked main](../fpm_catalog/demos/sqliteff.f90), [source/build record](fpm-candidates/sqliteff/source-review.json) and [verified output](fpm-candidates/sqliteff/verified-output.txt).

## erloff

Repository: [everythingfunctional/erloff](https://github.com/everythingfunctional/erloff), commit `73dfdbf54dafadb42e4705c45824b93917a20965`.

Structured error lists and logging. The checked main collects two fatal validation messages, filters one by OUT_OF_BOUNDS, checks counts and diagnostic text, and prints both messages. The pinned compatible Strff 3.1.1 avoids the unavailable exceptional_numbers mirror requested through Strff 4.0. No library source edits. This does not cover all logging levels, filtering operators or concurrent use.

See the [checked main](../fpm_catalog/demos/erloff.f90), [source/build record](fpm-candidates/erloff/source-review.json) and [verified output](fpm-candidates/erloff/verified-output.txt).

## fortran-tokenizer

Repository: [14NGiestas/fortran-tokenizer](https://github.com/14NGiestas/fortran-tokenizer), commit `11ad73ea6102f86593bf2b372d56bf9fbedaebc7`.

Customizable text tokenization. The checked main uses a module callback to split comma, space and tab-separated fields, verifies all three tokens and checks clearing the list. This is lexical splitting, not expression evaluation. No source edits. Malformed input, every callback combination and token object storage are not covered.

See the [checked main](../fpm_catalog/demos/fortran-tokenizer.f90), [source/build record](fpm-candidates/fortran-tokenizer/source-review.json) and [verified output](fpm-candidates/fortran-tokenizer/verified-output.txt).

## integer_set

Repository: [jordan4ibanez/integer_set](https://github.com/jordan4ibanez/integer_set), commit `85d336319d6593f9768c599835342912ce0b7bb8`.

Simple fixed-width integer sets. The checked main verifies duplicate rejection, removal and sorted contents for 32-bit values, and duplicate rejection for a 64-bit value above the 32-bit range. Membership is checked from public data, not a separate membership API. No source edits. Performance, every boundary and all operations are not validated.

See the [checked main](../fpm_catalog/demos/integer_set.f90), [source/build record](fpm-candidates/integer_set/source-review.json) and [verified output](fpm-candidates/integer_set/verified-output.txt).

## smart-pointers

Repository: [sourceryinstitute/smart-pointers](https://github.com/sourceryinstitute/smart-pointers), commit `35130adc4be4384a14b2369e5edd36d4665cd994`.

Reference-counted resource management. Adapted from the author example: a user type extends sp_smart_pointer_t and implements free. The checked main shares one integer resource, verifies reference counts and shared target, checks no premature cleanup and confirms exactly one cleanup after subroutine return. No source edits. This is not exhaustive compiler finalization conformance testing.

See the [checked main](../fpm_catalog/demos/smart-pointers.f90), [source/build record](fpm-candidates/smart-pointers/source-review.json) and [verified output](fpm-candidates/smart-pointers/verified-output.txt).

## fregex

Repository: [14NGiestas/fregex](https://github.com/14NGiestas/fregex), commit `1e20f084fb33b2b9dda8ca887bafae3c847e08c6`.

**Deferred.** The original PCRE 1 API needs -lpcre. The default Debian 13 (trixie) main amd64 package index contains neither libpcre3 nor libpcre3-dev. PCRE2 is a different API, not a drop-in link substitution. Deferred pending an upstream PCRE2 port or an explicitly maintained native-library recipe. See the [reproducer](fpm-candidates/fregex/main.f90) and [source/build record](fpm-candidates/fregex/source-review.json). No issue was submitted upstream.

## time-f

Repository: [0382/time-f](https://github.com/0382/time-f), commit `f0067d85d32082225d3abecbf8e35cee17fe95c4`.

**Deferred.** Compiles, but the supplied strftime maximum length is ignored. The bounded-buffer probe expects zero for a 19-character date with maxsize=5, and fails. The C binding omits VALUE on size_t maxsize. The tm layout also needs platform ABI review before exposing mktime and timezone-dependent formatting; the source declares only nine integers. Deferred rather than publishing a limited example that hides these issues. See the [reproducer](fpm-candidates/time-f/main.f90) and [source/build record](fpm-candidates/time-f/source-review.json). No issue was submitted upstream.

A separate sandbox probe confirms that the host C `struct tm` occupies **56 bytes**, while `c_sizeof` reports **36 bytes** for the library type. The [ABI check](fpm-candidates/time-f/abi-check.json) retains both probe sources and measurements.

The immediate binding correction to investigate is `integer(c_size_t), value :: maxsize` in `strftime_c`, matching the C `size_t` argument. This alone does not establish that the Fortran `tm` type matches the host C ABI. A portable C shim, or verified platform-specific layout, is needed before accepting `mktime` and timezone-dependent formatting. The saved bounded-buffer probe keeps a 32-character actual allocation while requesting a maximum of five, so it detects the return-value error without deliberately overflowing the allocation.

## rpn-calculator-fortran

Repository: [scivision/rpn-calculator-fortran](https://github.com/scivision/rpn-calculator-fortran), commit `7708e4949f17511d81f4e7dd0271a500f0bc3631`.

Numerical routines from the RPN calculator, called directly without its interactive interface. The checked main verifies a negative cube root, sinc and sech at zero, beta(2,3), modified Bessel I0 at zero, and integer gcd/lcm against known results. A checksum-guarded manifest correction sets source-form=default so .f and .f90 files use their respective forms. No numerical sources are changed. The tests do not establish accuracy over full argument ranges or validate the complete calculator.

See the [checked main](../fpm_catalog/demos/rpn-calculator-fortran.f90), [source/build record](fpm-candidates/rpn-calculator-fortran/source-review.json) and [verified output](fpm-candidates/rpn-calculator-fortran/verified-output.txt).

## nc4fortran

Repository: [geospace-code/nc4fortran](https://github.com/geospace-code/nc4fortran), commit `942ac4f83380acdef463002f555aebf30f3c46ac`.

NetCDF4 array and attribute I/O. The checked main writes a 2-by-3 double-precision array with dimension names and a kelvin units attribute, closes the file, reopens and verifies every value and the attribute, then deletes the sandbox file. Native NetCDF and HDF5 development packages and include/library paths are pinned in the build recipe. No source edits. It does not cover every type/rank, compression, slicing or malformed files.

See the [checked main](../fpm_catalog/demos/nc4fortran.f90), [source/build record](fpm-candidates/nc4fortran/source-review.json) and [verified output](fpm-candidates/nc4fortran/verified-output.txt).

## fundamental_constants

Repository: [vmagnin/fundamental_constants](https://github.com/vmagnin/fundamental_constants), commit `3e18620ab7813fd9f02e8dcf05c48f0ca13f2ec0`.

CODATA physical constants. The checked main imports the explicit 2022 edition, computes the energy of a 500 nm photon in joules and electron volts, and compares it with independent decimal reference values. The source modules are pre-generated; no network request or Python generation is needed to use them. No source edits. This is a check of three constants and one calculation, not revalidation of the complete CODATA tables or uncertainty propagation.

See the [checked main](../fpm_catalog/demos/fundamental_constants.f90), [source/build record](fpm-candidates/fundamental_constants/source-review.json) and [verified output](fpm-candidates/fundamental_constants/verified-output.txt).

## array_range

Repository: [degawa/array_range](https://github.com/degawa/array_range), commit `cd21ccb982e23de9c2df44c12edab44dd84562dc`.

Derived types and constructors for multidimensional array bounds. The checked main reconstructs and round-trips bounds [-1:1,4:5], traverses exactly six elements using stored bounds and verifies their sum of 270. No source edits. It does not cover all dimensions, vector/tensor wrappers, empty arrays or invalid bounds. This is an indexing utility, not a numerical solver.

See the [checked main](../fpm_catalog/demos/array_range.f90), [source/build record](fpm-candidates/array_range/source-review.json) and [verified output](fpm-candidates/array_range/verified-output.txt).

## flibcsv

Repository: [freevryheid/flibcsv](https://github.com/freevryheid/flibcsv), commit `ce19ebe6b08c58f1014527d27f27bdd97b38c835`.

**Parser example passed; publication deferred.** The bounded CSV parser example compiles and passes quoted fields, embedded commas, an empty field and doubled quotes. Deferred before publication: the manifest license is the placeholder "license", no repository license file was found, and the Fortran wrapper has no explicit license notice; only bundled C sources identify LGPL-2.1-or-later. Source review also finds incorrect unused C bindings: entry_buf is a character rather than a C pointer, csv_strerror returns a character rather than a C pointer, and csv_write/csv_write2 omit VALUE on pointer arguments. Author clarification and a binding review are needed before presenting this as a ready-to-use library. See the [checked main](fpm-candidates/flibcsv/main.f90), [sandbox result](fpm-candidates/flibcsv/sandbox-parser-check.json) and [source review](fpm-candidates/flibcsv/source-review.json). No issue was submitted upstream.

## jeyemhex-regex

Repository: [jeyemhex/fortran-regex](https://github.com/jeyemhex/fortran-regex), commit `2ca0043837a86a4f77df494ddad2240c1b70e576`.

Pure Fortran regular expressions by Edward Higgins, distinct from perazz/fortran-regex already selected under fortran-regex. The main checks matching and nonmatching anchored decimal measurements, matched substring, comma/space splitting and replacement. No source edits or native regex library. Pattern whitespace is ignored unless escaped; the author documents missing capture references and other features, so PCRE compatibility and all patterns are not claimed.

See the [checked main](../fpm_catalog/demos/jeyemhex-regex.f90), [source/build record](fpm-candidates/jeyemhex-regex/source-review.json) and [verified output](fpm-candidates/jeyemhex-regex/verified-output.txt).

## fed

Repository: [degawa/fed](https://github.com/degawa/fed), commit `d735aa2b3bd6b20840bcc16ff569e8cfc0492267`.

Programmatic Fortran edit descriptors. The main generates and applies integer, character and fixed-decimal real formats, checks exact aligned output, and verifies a zero-padded integer. The registry stdlib dependency is mapped to a pinned Git source and manifest version; compatible stdlib objects are reused. No Fortran source edits. Arrays, complex values, user-defined I/O and every descriptor/control mode are not covered.

See the [checked main](../fpm_catalog/demos/fed.f90), [source/build record](fpm-candidates/fed/source-review.json) and [verified output](fpm-candidates/fed/verified-output.txt).

## any

Repository: [degawa/any](https://github.com/degawa/any), commit `b9eb5e3fdc8f162ae8f2c5d8d026537ed2397830`.

Type-erased intrinsic values returned through any_type. The checked main returns an integer, a double-precision real and a character value through one function, retrieves each using its matching type, and checks exact values. No source edits. The author documents undefined results for mismatched type/rank conversions; the example does not validate all ranks, kinds, custom extensions or invalid conversions.

See the [checked main](../fpm_catalog/demos/any.f90), [source/build record](fpm-candidates/any/source-review.json) and [verified output](fpm-candidates/any/verified-output.txt).

## for_fifo_queue

Repository: [jordan4ibanez/for_fifo_queue](https://github.com/jordan4ibanez/for_fifo_queue), commit `b04b536589af8cf041b8e5e53484e57147fc746f`.

FIFO container using C allocations and byte copies. The main enqueues four 64-bit C-interoperable integers, verifies count and exact retrieval order, frees every popped allocation with C free, checks empty-pop behavior and destroys the queue. No source edits. The implementation uses GNU LOC and raw byte storage; the example makes no portability claim for arbitrary derived types, pointer-owning values, threading or every compiler.

See the [checked main](../fpm_catalog/demos/for_fifo_queue.f90), [source/build record](fpm-candidates/for_fifo_queue/source-review.json) and [verified output](fpm-candidates/for_fifo_queue/verified-output.txt).

## string-utf-8

UTF-8 string handling using one array element per encoded Unicode code point. The main verifies a round trip, code point count, substring, search and replacement of accented text, and prints the results. No source edits. Combining marks remain separate code points; grapheme segmentation, normalization and malformed-input handling are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/string-utf-8.f90), [source/build record](fpm-candidates/string-utf-8/source-review.json) and [verified output](fpm-candidates/string-utf-8/verified-output.txt).

## fortime

Serial system_clock and CPU timers. The checked main computes the exact sum of integers 1 through 100000, checks finite nonnegative elapsed times and prints the sum and timings. The root manifest VERSION placeholder is replaced with adapter version 0.0.0; the pinned source commit identifies the actual library. FACE is pinned to an already used revision. No Fortran source edits. MPI/OpenMP timers are not enabled or tested; sandbox timings vary and are not benchmark guarantees.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortime.f90), [source/build record](fpm-candidates/fortime/source-review.json) and [verified output](fpm-candidates/fortime/verified-output.txt).

## fassert

Assertions for integer scalars and arrays plus approximate real comparison with an explicit tolerance. The main captures an intentional failed comparison as a logical status and message, checks both, and continues successfully. No source edits; matches the existing Any dependency revision. Not a validation of every type, rank, tolerance convention, custom comparator or test-framework integration.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fassert.f90), [source/build record](fpm-candidates/fassert/source-review.json) and [verified output](fpm-candidates/fassert/verified-output.txt).

## errstat

Error status and message handling. A custom reciprocal routine uses catch_error and set_success. The main checks a successful result, zero rejection with an exact code and message, and a subsequent successful call clearing the error. No source edits. The reciprocal is only a driver, not a mathematical procedure supplied by errstat. Optional omitted-status termination and user-defined task/message repositories are not exercised.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/errstat.f90), [source/build record](fpm-candidates/errstat/source-review.json) and [verified output](fpm-candidates/errstat/verified-output.txt).

## slinked-list

Generic singly linked list for small datasets. The main checks integer and real payloads in insertion order, list size, iteration count, emptying, retained capacity and the value stored after reuse; iterator and list cleanup are explicit. A checksum-guarded compatibility edit removes PURE from node_init, whose result has a polymorphic allocatable component. Constructor allocation and copying are unchanged, and the call sites are impure. This patched root retains its own small archive instead of sharing an unmodified graph export. No display dependency is needed for the custom consumer. Large-data performance, all mutation operations and ownership of pointer-containing derived types are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/slinked-list.f90), [source/build record](fpm-candidates/slinked-list/source-review.json) and [verified output](fpm-candidates/slinked-list/verified-output.txt).

## enclose

String enclosure with automatically matched closing brackets and explicit delimiters. The main checks nested bracket reversal, square brackets, quotation marks, custom opening/closing strings and disabled autoclosing, and prints examples. No source edits; matches the existing FED dependency revision. This is formatting, not parsing or escaping untrusted text.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/enclose.f90), [source/build record](fpm-candidates/enclose/source-review.json) and [verified output](fpm-candidates/enclose/verified-output.txt).

## lookup-table-fortran

Linear lookup tables. An operator-owned FPM manifest wraps the unchanged m_lookup_table.f90 file. The main checks exact interpolation of a linear function, the expected interpolation error for a quadratic, an exact grid value, and clamping below/above the endpoints. No mathematical source edits. The 2D interface, nonuniform spacing options, persistence and all boundary cases are not validated by this example.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/lookup-table-fortran.f90), [source/build record](fpm-candidates/lookup-table-fortran/source-review.json) and [verified output](fpm-candidates/lookup-table-fortran/verified-output.txt).

## rng-fortran

Xoroshiro128+ pseudo-random generator. An FPM wrapper selects unchanged m_random.f90 and uses -fwrapv for its intentional signed-integer wraparound. Two fresh generators replay 10000 seeded uniform draws exactly; the main checks the implementation range [0,1), broad uniform/normal/Poisson(4) moment tolerances, nonnegative counts and unit circle/sphere norms. These are deterministic smoke checks, not statistical quality or cryptographic validation. OpenMP, jump independence, large Poisson rates and all distributions are not covered. A separate hosted reproducer confirms that set_seed does not clear the cached second normal after an odd normal() call; use a fresh generator to restart normal sequences. The selected replay uses fresh objects.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/rng-fortran.f90), [source/build record](fpm-candidates/rng-fortran/source-review.json) and [verified output](fpm-candidates/rng-fortran/verified-output.txt).

See also the [normal-reseeding reproducer](fpm-candidates/rng-fortran/reseed-normal-reproducer.f90) and [hosted result](fpm-candidates/rng-fortran/reseed-normal-result.json).

## fortran-fast-float

Numeric text parsing. FPM 0.12 rejects the upstream features/profiles tables; a checksum-guarded manifest adaptation removes them and supplies the intended -fno-range-check compiler setting explicitly. The Fortran sources are unchanged and development-only benchmark dependencies are not built. The main checks decimal/scientific and Fortran D-exponent parsing, the largest positive signed int64, hexadecimal parsing, invalid-input status and exponent-overflow status. Correct rounding for every input, all formats, underflow, platforms and speed claims are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-fast-float.f90), [source/build record](fpm-candidates/fortran-fast-float/source-review.json) and [verified output](fpm-candidates/fortran-fast-float/verified-output.txt).

The [original manifest failure](fpm-candidates/fortran-fast-float/original-build-failure.json) is retained with the accepted manifest adaptation.

## config-fortran

Documented configuration values. An FPM wrapper selects unchanged m_config.f90. The main creates its own tiny configuration file, overrides integer, logical, string and grouped real defaults, reads a dynamically sized real array, checks every value and clears the configuration. No uploaded data file or external service is required. Command-line parsing, invalid-file diagnostics and all string/array/grouping behavior are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/config-fortran.f90), [source/build record](fpm-candidates/config-fortran/source-review.json) and [verified output](fpm-candidates/config-fortran/verified-output.txt).

## kdtree2

Nearest-neighbor and radius searches. An FPM wrapper selects unchanged src-f90/kdtree2.f90; the archived upstream single-precision setting is retained. The checked main builds a tree for 30 deterministic 2D points, compares four nearest indices and squared distances against an independent direct search, and checks radius-search count, membership, distances and uniqueness. The original Academic Free License 1.1 is retained. No source edits. The implementation has global search state and is not offered as thread-safe; the old interface, C++ code, every dimension and large-scale performance are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/kdtree2.f90), [source/build record](fpm-candidates/kdtree2/source-review.json) and [verified output](fpm-candidates/kdtree2/verified-output.txt).

## penf

Portable numerical kinds, formats and number/string conversions. The latest archive is blocked by a symlink, so this entry uses exactly the older revision already verified as a BeFoR64 dependency. The checked main calls penf_init, verifies integer and real conversion round trips with status checks, zero-padded integer output, real byte size and formatted real output. Sources are unchanged; this adds an independent editable main for the pinned library. Every kind, character encoding, endian platform and invalid conversion is not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/penf.f90), [source/build record](fpm-candidates/penf/source-review.json) and [verified output](fpm-candidates/penf/verified-output.txt).

The [latest-archive rejection](fpm-candidates/penf/latest-archive-rejection.json) is retained with the reason for using the compatible dependency pin.

## differentia

Forward-mode automatic differentiation with dual numbers. The main checks the upstream scalar example against its analytical value and derivative, a two-variable polynomial gradient and a square 2-by-2 Jacobian against exact formulas. GNU heap trampolines support the internal callback procedures in the restricted sandbox. Library sources are unchanged. The author limits jacobian to square problems and documents incomplete intrinsic coverage; sparse interfaces, every overload and all failure modes are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/differentia.f90), [source/build record](fpm-candidates/differentia/source-review.json) and [verified output](fpm-candidates/differentia/verified-output.txt).

## coretran

Scientific utilities. The main sorts repeated and negative integers, builds a k-d tree for 20 deterministic 2D points and compares the nearest point with an independent direct search. The OpenMP metapackage is resolved explicitly and -fopenmp is enabled; the execution sandbox still uses one thread. No source edits. The broad library is compiled, but this driver does not validate all containers, random generators, mathematical utilities or parallel performance.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/coretran.f90), [source/build record](fpm-candidates/coretran/source-review.json) and [verified output](fpm-candidates/coretran/verified-output.txt).

## delaunaysparse

Version 1 multivariate interpolation using sparse Delaunay simplices. Version 2 bundles BQPD with a research-only redistribution notice, so the selected pin uses the earlier MIT-licensed version 1 with its bundled SLATEC/BLAS/LAPACK sources. An FPM wrapper retains fixed/free source forms, legacy implicit typing/interfaces and -fallow-argument-mismatch for the SLATEC scalar-zero/zero-stride BLAS convention. OpenMP is enabled to link the library; the checked driver uses the serial routine. It verifies exact linear-function reproduction at three interior 2D points, zero status codes, valid simplex indices and barycentric weight sums/signs. No numerical source edits. Convex-hull projection/extrapolation, all degenerate inputs, high-dimensional behavior and parallel variants are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/delaunaysparse.f90), [source/build record](fpm-candidates/delaunaysparse/source-review.json) and [verified output](fpm-candidates/delaunaysparse/verified-output.txt).

See the [version-2 investigation](fpm-candidates/delaunaysparse/version-2-investigation.json) and [initial wrapper diagnostics](fpm-candidates/delaunaysparse/original-build-failures.json).

## npy-for-fortran

NumPy NPY writing. An FPM wrapper selects unchanged src/npy.f90. The main writes a 2-by-3 real64 matrix, checks version-2 magic, dtype/order header, exact binary payload and file size, and prints the matrix and header. A separate hosted probe captures the actual file bytes and NumPy independently loads the expected shape, dtype and exact values with pickle disabled. No source edits. The author no longer actively maintains the project. Other kinds/ranks, big-endian platforms and NPZ archive operations are not validated; the browser displays the checked summary rather than offering a general NPY-file download.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/npy-for-fortran.f90), [source/build record](fpm-candidates/npy-for-fortran/source-review.json) and [verified output](fpm-candidates/npy-for-fortran/verified-output.txt).

The [independent NumPy check](fpm-candidates/npy-for-fortran/numpy-check.json) records the shape, dtype, file hash and loaded values.

## ftl

Selected Fortran Template Library instantiations: integer dynamic arrays and ftlString-to-integer hash maps, plus their unmodified support modules. A checksum-guarded adapter adds CPP-disabled module/dependency declarations so FPM 0.12 can discover modules emitted by templates. Original and adapted compiler-preprocessed output match apart from blank lines. Implicit-external checking is left at the upstream convention to avoid a GNU diagnostic in a character-length specification expression. The checked main verifies array growth, contents and pop, map insertion/replacement, presence, lookup and erase, then explicitly deletes both containers. Sources otherwise remain unchanged, and template headers remain in the source archive. Other instantiations, general algorithms, regex and every ownership/finalization case are not offered or validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/ftl.f90), [source/build record](fpm-candidates/ftl/source-review.json) and [verified output](fpm-candidates/ftl/verified-output.txt).

The [preprocessor comparison](fpm-candidates/ftl/scanner-adapter-check.json) verifies that the scanner declarations do not change compiled code. [Initial diagnostics](fpm-candidates/ftl/original-build-failures.json) are retained.

## qnstop

Serial QNSTOP for bound-constrained stochastic and global optimization. An FPM wrapper selects unmodified REAL_PRECISION, ZIGARRAY, QNSTOPS and bundled BLAS/LAPACK sources. Explicit CPP suffix handling lets FPM discover .f95 files. Legacy implicit typing/interfaces and argument-mismatch compatibility retain the upstream calling conventions. The seeded two-variable quadratic example checks normal stopping status, bounds, objective value and distance from its known minimizer. It is an accuracy smoke test, not a general global-optimum guarantee. The parallel QNSTOPP driver, noisy objectives, all stopping rules and performance are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/qnstop.f90), [source/build record](fpm-candidates/qnstop/source-review.json) and [verified output](fpm-candidates/qnstop/verified-output.txt).

## poisfft

Serial FFTW Poisson solvers. An FPM wrapper selects the Fortran library modules, retains upstream template includes, adds CPP-disabled USE declarations for the FPM dependency scanner, declares unused MPI/PFFT modules external for scanning, enables CPP and links Debian FFTW 3.3.10 single/double and thread libraries. MPI/PFFT and C/C++ bindings are not offered. The checked double-precision periodic 1D spectral problem compares its solution with sin(2*pi*x) at 32 points. Other boundary conditions, finite-difference modes, nonuniform grids, higher-dimensional solvers, single precision and parallel execution are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/poisfft.f90), [source/build record](fpm-candidates/poisfft/source-review.json) and [verified output](fpm-candidates/poisfft/verified-output.txt).

## fortran-lmdb

LMDB key-value database bindings with Debian LMDB 0.9.31. A checksum-guarded compatibility edit selects the existing signed-kind fallback rather than GNU unsigned extension kinds, which are unavailable without enabling nondefault unsigned support. The checked consumer creates a small sandbox-local database, inserts and updates a value, verifies committed reads and rollback after an aborted update, deletes the key and checks MDB_NOTFOUND, then closes and removes both database files. No persistent storage is provided. Large mappings, concurrent writers/readers, all cursor interfaces and other platforms are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-lmdb.f90), [source/build record](fpm-candidates/fortran-lmdb/source-review.json) and [verified output](fpm-candidates/fortran-lmdb/verified-output.txt).

## fortran-lua54

Fortran bindings to Lua 5.4, linked with Debian Lua 5.4.7. The manifest library name lua-5.4 is adapted to Linux lua5.4; library sources are unchanged. Adapted from the upstream in-memory string example, the consumer defines a Lua function, passes an integer from Fortran, checks Lua load/call status and function type, verifies the returned integer and closes the state. External scripts, callbacks from Lua to Fortran, arbitrary Lua modules and all bindings are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-lua54.f90), [source/build record](fpm-candidates/fortran-lua54/source-review.json) and [verified output](fpm-candidates/fortran-lua54/verified-output.txt).

## fortran-unix

POSIX/SysV bindings on the playground 64-bit Linux/glibc environment. The source library is unchanged. The manifest features/profiles tables are removed for FPM 0.12 compatibility and their Linux preprocessor flag is supplied explicitly. A 13-byte sandbox-local file is created, its size is checked through c_stat, then c_unlink removes it and Fortran INQUIRE confirms removal. Other operating systems, process creation, networking, IPC, signals, threads and all ABI structures are not validated or promised in the restricted sandbox.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-unix.f90), [source/build record](fpm-candidates/fortran-unix/source-review.json) and [verified output](fpm-candidates/fortran-unix/verified-output.txt).

## vtmop

Serial derivative-free, bound-constrained multiobjective optimization. An FPM wrapper selects the unchanged solver, surrogate and test-function sources with bundled SLATEC support and links system LP64 BLAS/LAPACK rather than recompiling those bundled libraries. OpenMP linking is enabled, but the checked run uses the serial driver and one execution thread; heap trampolines support internal callbacks in the sandbox. Adapted from the author serial driver and CONVEX function, the seeded 3-variable/2-objective example uses a small evaluation budget, checks feasible design bounds, recomputes both quadratic objectives independently and verifies that no returned point dominates another. It requires multiple distinct trade-off points. This checks the finite returned set, not convergence to the exact global Pareto front or comparative performance. Parallel evaluation, checkpoint recovery, every surrogate and other problem classes are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/vtmop.f90), [source/build record](fpm-candidates/vtmop/source-review.json) and [verified output](fpm-candidates/vtmop/verified-output.txt).

## fatode

Selected FATODE explicit Runge-Kutta tangent-linear integrator, linked to native BLAS/LAPACK. The FPM wrapper compiles unchanged TLM/ERK_TLM/ERK_TLM_f90_Integrator.F90; bundled precompiled platform binaries are not used. The example augments exponential decay with a constant rate state and differentiates the initial rate using the tangent-linear model, checking the state, rate, and both sensitivities against analytical formulas. It explicitly selects the supplied analytical Jacobian and enables tangent-variable adaptive error control; the initial default finite-difference Jacobian settings missed the requested sensitivity accuracy. No numerical library edits. Implicit/stiff solvers, adjoint integration, sparse solver variants and all ERK methods are not offered or verified.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fatode.f90), [source/build record](fpm-candidates/fatode/source-review.json) and [verified output](fpm-candidates/fatode/verified-output.txt).

## slicot

Full upstream SLICOT FPM source library, linked to compatible LP64 BLAS/LAPACK with the manifest BLAS metapackage resolved explicitly. Sources are unchanged; legacy compiler compatibility flags retain upstream conventions. The main uses the author slicot module interface for SB03MD, constructs a stable nondiagonal 2-by-2 continuous Lyapunov problem from a known symmetric solution and checks both the independently computed matrix residual and the recovered solution including the solver scale factor. It requests the condition/error estimates but does not validate those estimates independently. Other matrix equations, model reduction, identification, robust control and every library routine are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/slicot.f90), [source/build record](fpm-candidates/slicot/source-review.json) and [verified output](fpm-candidates/slicot/verified-output.txt).

## arpack-ng

Serial classic Fortran ARPACK-NG interfaces, built from unchanged SRC .f files, the documented UTIL support set, and upstream debug/statistics initializers. The wrapper uses native LP64 BLAS/LAPACK and excludes PARPACK/MPI and generated C bindings. The upstream second_NONE timing stub disables ARPACK internal elapsed-time statistics; playground build/run timings still work. Adapted from the author symmetric reverse-communication example, the main computes three smallest eigenpairs of a 20-by-20 symmetric tridiagonal operator, checks convergence status/count, analytical eigenvalues and eigenvector residual norms. A deterministic nonzero initial residual avoids dependence on random initialization. Nonsymmetric/complex modes, shift-invert, generalized problems and parallel execution are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/arpack-ng.f90), [source/build record](fpm-candidates/arpack-ng/source-review.json) and [verified output](fpm-candidates/arpack-ng/verified-output.txt).

## fortran-error-handler

Structured error handling and validation. The upstream FPM library sources are unchanged; unlimited free-form line length accommodates existing long source lines. Adapted from the author example, the main checks a valid bounded integer in a Result object, rejects an out-of-range integer with expected code 105, checks two retained application trace entries, and triggers a custom noncritical warning while execution continues. The example uses fixed values rather than interactive input. All Result ranks/types, critical-error termination, all validation criteria and every trace-propagation path are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-error-handler.f90), [source/build record](fpm-candidates/fortran-error-handler/source-review.json) and [verified output](fpm-candidates/fortran-error-handler/verified-output.txt).

## berkeley-assert

Runtime assertion checks in pure procedures, built with ASSERTIONS=1 so enforcement is enabled in the cached library. A checksum-guarded manifest edit adds the upstream include directory; library sources and headers are unchanged. The main checks preconditions and postconditions around a pure square-root function. A separate sandbox probe compiles successfully, intentionally calls assert(.false.), and verifies nonzero termination with the expected descriptive diagnostic and unchanged library artifacts, demonstrating that checks were not compiled away. Multi-image/coarray callbacks and every macro variant are not validated. Full current upstream license terms, including its enhancement-contribution provision, are retained under LicenseRef-Berkeley-Assert rather than labeling them as an unmodified standard BSD license.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/berkeley-assert.f90), [source/build record](fpm-candidates/berkeley-assert/source-review.json) and [verified output](fpm-candidates/berkeley-assert/verified-output.txt).

## foodie

The current head and tags v0.4.1 and v0.4.0 contain symlinks, including CONTRIBUTING.md and plotting/benchmark assets. The ordinary source preparer rejects links before compilation. No extraction rules were changed, no incomplete package is selected, and no compiler failure is claimed.

See the [pinned archive investigation](fpm-candidates/foodie/source-review.json) and the [saved author oscillator guide](fpm-candidates/foodie/upstream-oscillation-example.md). The proposed driver would compare an oscillator against its exact solution and check error reduction after halving the step.

## fmm3d

The pinned native Fortran library compiles with GNU Fortran 16.2.0, but its Laplace example fails the playground bounds-checked run. Adding the upstream quadrature include directory resolves preparation of Helmholtz sources; adapting two scarray(1) dummy declarations passes the isolated workspace check, but the full run then stops at fexpe(2) with declared extent 1 in lpwrouts.f. A separate local GNU 17 checked run also reports an unallocated disabled dipole buffer argument. The package is deferred under the current checked build profile; these findings do not establish failure with the upstream release build settings.

See the [source/build investigation](fpm-candidates/fmm3d/source-review.json), [draft checked main](fpm-candidates/fmm3d/main.f90), [latest sandbox diagnostic](fpm-candidates/fmm3d/latest-sandbox-failure.json), [workspace patch](fpm-candidates/fmm3d/workspace-compatibility.patch) and [isolated workspace check](fpm-candidates/fmm3d/workspace-check.json). No incomplete FMM3D entry is selected.

## fmm2d

Native Fortran FMM2D source set selected from the upstream makefile with optional C++ fast kernels disabled. OpenMP and portable -O2 are enabled; the visitor sandbox uses one execution thread and retains bounds checks. Checksum-guarded compatibility edits skip zero-point multipole/local evaluations and zero-source neighbor calls before passing one-past-end array elements. The inverse reorder helper declares its arrays with the actual n extent rather than the legacy dummy extent 1. Source and target branches receive matching guards; formulas are unchanged. The checked real Laplace driver evaluates 512 deterministic sources at 16 separate targets and compares with an independent charge-weighted log-distance sum. A separate source-and-target probe also checks all source potentials by direct summation with self-interactions excluded, exercising the source-side guards. The code is classified as a structured kernel-matrix application and Green-function evaluation related to PDEs, not as a complete boundary-value solver. Helmholtz, biharmonic/Stokes, dipoles, gradients/Hessians, every complex/vector interface and parallel speedups are not validated. The small accuracy check is not a performance benchmark.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fmm2d.f90), [source/build record](fpm-candidates/fmm2d/source-review.json) and [verified output](fpm-candidates/fmm2d/verified-output.txt).

The [compatibility patch](fpm-candidates/fmm2d/bounds-compatibility.patch), [original sandbox diagnostics](fpm-candidates/fmm2d/original-sandbox-diagnostics.json), [small reorder reproducer](fpm-candidates/fmm2d/reorder-reproducer.f90) and [additional source/target check](fpm-candidates/fmm2d/source-target-check.json) are saved for review or discussion with the authors.

## fortran-utils

Selected unmodified modules types, utils, lapack, mesh, splines and sorting, wrapped for FPM and linked to compatible LP64 BLAS/LAPACK. HDF5, AMOS/special functions, optimization and other unselected modules are not included. The main reproduces a cubic polynomial with the consistent-boundary cubic spline and checks its value, first derivative and second derivative on a denser grid against exact formulas. It checks exponential-mesh endpoints, monotonicity and the requested last/first spacing ratio, then sorts repeated/negative integers against an exact answer. General nonpolynomial interpolation error, extrapolation, every boundary condition, other sorting interfaces and all utility routines are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-utils.f90), [source/build record](fpm-candidates/fortran-utils/source-review.json) and [verified output](fpm-candidates/fortran-utils/verified-output.txt).

## formal

Mimetic vector-calculus library with pinned Julienne and Assert dependencies. A single-image coarray build is used. The checked consumer adapts the author's extended Gauss-divergence example to f=x**2/2 and v=x on a 64-cell unit interval. It checks the two volume integrals against 1/3 and 1/6, the boundary flux against 1/2, finiteness and the conservation residual using single-precision tolerances. The command-line parsing and shell display calls of the upstream example are omitted. Library numerical sources are unchanged. Other 2D/3D operators, time integration and convergence orders are not validated. Original Berkeley Lab license terms, including the enhancements clause, are retained; this is not labeled plain BSD-3-Clause.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/formal.f90), [source/build record](fpm-candidates/formal/source-review.json) and [verified output](fpm-candidates/formal/verified-output.txt).

## dftatom

Unmodified Fortran library sources selected from the upstream native makefile and wrapped for FPM. The checked example adapts the upstream hydrogen test to Z=1 and computes all six (n,l) states through n=3 on an exponential radial mesh. It requires solver convergence, finite energies and agreement with the analytical nonrelativistic energies -1/(2*n**2) within 1e-7 Hartree. Relativistic Dirac, Poisson and self-consistent density-functional calculations are present in the library but not exercised by this example. C/Python bindings and optional extra integration/interpolation/LAPACK sources are outside the selected native source set.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/dftatom.f90), [source/build record](fpm-candidates/dftatom/source-review.json) and [verified output](fpm-candidates/dftatom/verified-output.txt).

## m-system

Unmodified mixed C/Fortran POSIX system library in the Linux/glibc sandbox. The checked example creates a local directory with owner-only permissions, writes and reads back the integer 42, checks directory and regular-file types, removes both and confirms cleanup. Other system calls, processes, networking, permissions changes and Windows portability are not validated or promised. Upstream development dependencies and applications are not part of the consumer demonstration.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/m-system.f90), [source/build record](fpm-candidates/m-system/source-review.json) and [verified output](fpm-candidates/m-system/verified-output.txt).

## fortran-tcl86

Fortran/C bindings linked to pinned Debian Tcl/Tk 8.6 development libraries. A checksum-guarded include edit selects Debian's tcl8.6/tcl.h path for the C macro wrappers; interfaces and calculation code are unchanged. Adapted from the upstream evaluation example, the consumer creates a Tcl interpreter, evaluates an in-memory sum-of-squares script, checks evaluation status and the integer result against Fortran, then destroys the interpreter. Tk graphical windows, extension modules, Tcl stubs and all bindings are not validated; the browser example requires no graphical display or network.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-tcl86.f90), [source/build record](fpm-candidates/fortran-tcl86/source-review.json) and [verified output](fpm-candidates/fortran-tcl86/verified-output.txt).

## fortranlib

Selected base_types, lib_algebra and lib_array modules, using the pinned revision immediately before the upstream FPM test suite introduced source symlinks. Nine checksum-guarded edits bring lib_array exactly to upstream commit 844611933cba06d71490033e68b355f6f0ff704f, retaining its integration-limit, descending histogram-bin and precision fixes. The other selected modules are unchanged. The ordinary archive policy remains unchanged. A synthetic FPM wrapper uses the already generated Fortran sources, not the Python templates. The checked consumer integrates the affine function 2*x+1 on [0,1], checks linear interpolation at an interior off-grid point, and solves x**2-5*x+6 against the exact roots 2 and 3. Additional checks cover integration limits outside the tabulated range, descending histogram bins and bin-center precision; the expanded example fails with the older unpatched array module and passes with the upstream fixes. GAMS F1 denotes the quadratic solver, not a general iterative root finder. Random sampling, statistics, geometry, HDF5/FITS bindings and other modules are not selected; the example does not validate every routine in the included modules.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortranlib.f90), [source/build record](fpm-candidates/fortranlib/source-review.json) and [verified output](fpm-candidates/fortranlib/verified-output.txt).

The [upstream array fixes](fpm-candidates/fortranlib/upstream-array-fixes.patch) are retained together with the [original failing boundary check](fpm-candidates/fortranlib/original-boundary-failure.json).

## fiats

Pinned Fiats tag 0.12.0 (upstream manifest version 0.11.1), named inference-engine at that revision, with an explicitly pinned compatible Julienne 1.3.1 dependency and Assert 1.7.0. Tag 0.14.0 was tried first but its consumer build cannot find Julienne modules because they are declared only as a development dependency. Single-image coarrays and long free-form lines are enabled. Based on the author's write-read-infer example, the checked consumer constructs a two-input ReLU network with known diagonal weights and biases, evaluates negative, zero and positive input pairs, and compares every output with direct formulas. K is a broad function-approximation classification; training algorithms, gradients, model-file round trips and parallel speedups are not verified. The historical version is explicit in the menu description. The original Berkeley Lab license terms, including the enhancements clause, are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fiats.f90), [source/build record](fpm-candidates/fiats/source-review.json) and [verified output](fpm-candidates/fiats/verified-output.txt).

The [0.14.0 consumer-build failure](fpm-candidates/fiats/0.14.0-consumer-failure.json) explains why the menu explicitly offers the older source revision.

## julienne

Standalone demonstration of the modern Julienne testing framework, with its pinned Assert dependency and single-image coarrays. The numerical source is unchanged. The checked consumer verifies an approximate real comparison and an exact integer sum, then deliberately creates a failed test_diagnosis_t, checks its failure flag and nonempty appended diagnostic and prints it while completing successfully. This demonstrates diagnosis construction and inspection rather than macro assertion termination. The full test harness, automatic test discovery, macro enforcement and multi-image behavior are not validated. Original Berkeley Lab/Sourcery Institute license terms and dependency notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/julienne.f90), [source/build record](fpm-candidates/julienne/source-review.json) and [verified output](fpm-candidates/julienne/verified-output.txt).

## m-process

Unmodified Fortran/C POSIX pipe interfaces in the restricted Linux sandbox. Following the upstream process_open_read example, the consumer opens a local printf command, reads and checks the integers 7 and 11, verifies end of output and requires a successful process_close status. Commands run under the ordinary sandbox restrictions; this does not add network or host-system access. Interactive terminals, graphical subprocesses, arbitrary process behavior, write pipes and Windows portability are not verified.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/m-process.f90), [source/build record](fpm-candidates/m-process/source-review.json) and [verified output](fpm-candidates/m-process/verified-output.txt).

## propack

Historical SciPy PROPACK 2.1 sources, whose repository is archived and explicitly points to rmlarsen/propack for the maintained implementation. The current author archive and tags v2.2/v2.1 exceed the unchanged source download limit, largely due to saved example outputs. The menu explicitly identifies this historical source choice. Only the native double-precision serial routines are wrapped, using the portable RISC modified Gram-Schmidt implementation and compatible system LP64 BLAS/LAPACK. Numerical sources are unchanged. A callback supplies multiplication by a rectangular diagonal matrix with known singular values. The consumer passes a writable convergence-count argument, requests the leading three singular triplets, and checks 12, 11 and 10, both A*v-sigma*u and transpose(A)*u-sigma*v residuals, finite values and unit vector norms. The restarted algorithm, other precisions, arbitrary sparse matrices and parallel performance are not verified.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/propack.f90), [source/build record](fpm-candidates/propack/source-review.json) and [verified output](fpm-candidates/propack/verified-output.txt).

## nufft1d

Original one-dimensional nonuniform Fourier code using the dynamically allocated Fortran 90 interface and bundled Netlib FFT implementation. Forty-nine checksum-guarded edits change legacy extent-one FFT dummy-array declarations to assumed size; every changed array is checked against its containing procedure argument list. No local arrays, transform formulas or global bounds-checking settings are changed. Legacy workspace argument type punning is accepted with the package-specific -fallow-argument-mismatch option. The example evaluates a type-1 transform of 96 deterministic nonuniform points into 32 modes for both exponent signs and compares every complex coefficient with an independent direct sum, including the documented 1/nj normalization. Status and finite values are checked. Types 2/3, the static Fortran 77 interface and every bundled FFT routine are not verified.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/nufft1d.f90), [source/build record](fpm-candidates/nufft1d/source-review.json) and [verified output](fpm-candidates/nufft1d/verified-output.txt).

## nufft2d

Original two-dimensional nonuniform Fourier code using the dynamically allocated Fortran 90 interface and bundled Netlib FFT implementation. Forty-nine checksum-guarded edits change legacy extent-one FFT dummy-array declarations to assumed size after checking that each is a procedure argument; no formulas or local arrays change and bounds checking remains enabled. Legacy workspace argument type punning uses the package-specific -fallow-argument-mismatch option. The example transforms 96 deterministic scattered points onto a 16-by-18 mode grid for both exponent signs, checking status, finite values and all coefficients against an independent direct sum with the documented 1/nj normalization. Types 2/3, the static Fortran 77 interface, every FFT routine and multidimensional performance are not verified.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/nufft2d.f90), [source/build record](fpm-candidates/nufft2d/source-review.json) and [verified output](fpm-candidates/nufft2d/verified-output.txt).

## aotus

Mixed C/Fortran source set selected from the upstream Waf library lists, wrapped for FPM with the bundled Lua 5.4.8 core and libraries, the C dump wrapper and GNU-supported extended/quad precision module variants. Lua command-line interpreter/compiler executables and upstream tests are excluded. Sources are unchanged; the operator-only wrapper now permits explicitly listed locked C files, retaining old adapter identities and the ordinary downloader/archive limits. The consumer creates a small Lua configuration, checks a computed integer, a double-precision scalar, two named nested-table entries and a missing-key default with error bits, closes the state and deletes its file. Broader scripting, dump/reload callbacks, every numeric kind and sandbox-restricted system operations are not verified.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/aotus.f90), [source/build record](fpm-candidates/aotus/source-review.json) and [verified output](fpm-candidates/aotus/verified-output.txt).

## PROPACK maintained author sources

The maintained author repository head and tags v2.2 and v2.1 exceed the unchanged 16 MiB source download limit, before compilation. The repository includes large saved example output matrices. Selected propack instead verifies the explicitly labeled historical SciPy version; it does not establish that the maintained author sources compile in the playground.

See the [recorded archive attempts](fpm-candidates/propack-author/source-review.json).

## fox

The pinned head and tagged releases 4.1.2 and 4.1.1 contain symbolic links and are rejected by the unchanged archive extractor before compilation. No compiler failure is claimed. A safe source distribution or a separately reviewed source-preparation facility is needed before an XML round-trip example can be verified.

See the [pinned preparation evidence](fpm-candidates/fox/preparation-failure.json).

## qcontainers

Explicitly selected C and Fortran library sources are wrapped for FPM. Checksum-guarded edits rename the library string conversion helper to qlibc_f_c_string and update its callers, avoiding the Fortran 2023 intrinsic name collision; container algorithms are unchanged. The unrelated qencode.c utility is excluded: its query parser refers to qstrtrim and qlisttbl routines absent from the archive. The library retains vector, list, set, hash-table and tree-table modules and their vendored C dependencies. The checked consumer exercises vector growth, indexing, replacement, array conversion, pop and clear, and string-keyed map insertion, replacement, lookup, missing-key lookup and clear. Block scope invokes finalizers. Integer payloads are used; general pointer ownership, all container methods and threading are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/qcontainers.f90), [source/build record](fpm-candidates/qcontainers/source-review.json) and [verified output](fpm-candidates/qcontainers/verified-output.txt).

## stdlib-os

Mixed C/Fortran operating-system utilities wrapped for FPM. Two checksum-guarded compatibility edits set the Linux os_name constant and restrict the ISO_C_BINDING import to avoid the Fortran 2023 F_C_STRING name collision. OS_SYSTEM_ID is configured as OS_LINUX. The checked consumer creates nested temporary directories and a 14-byte stream file, checks file size and type, basename/dirname and path normalization, then renames and deletes the file and removes both directories. No external files or user environment are required. This configured recipe and exported project target Linux; Windows branches, processes, user/home lookup and every path utility are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/stdlib-os.f90), [source/build record](fpm-candidates/stdlib-os/source-review.json) and [verified output](fpm-candidates/stdlib-os/verified-output.txt).

## finer

The current source archive and tags v2.3.0 and v2.2.0 contain a CONTRIBUTING.md symbolic link and are rejected by the unchanged source extractor before compilation. No compiler failure is claimed. The current FPM manifest also pins StringiFor; dependencies were not downloaded after root extraction was rejected.

See the [pinned archive and release checks](fpm-candidates/finer/preparation-failure.json).

## m_draw

Upstream mixed C/Fortran FPM library, with a checksum-guarded manifest edit adding its src/inc header directory. The X11 link dependency is retained but the checked main uses the PPM file driver, requiring no display server or Hershey font files. A 20-segment blue parabola is rendered with the PPM driver; the consumer checks P3 magic, image dimensions, color range, every pixel range and the presence of blue curve pixels. The ordinary image collector converts the generated PPM to a bounded PNG browser preview. The SVG driver aborted during font initialization when no Hershey fonts were supplied; no upstream driver code is patched, and the example uses PPM. Interactive drivers, all drawing primitives, software text/font setup and SVG output are not validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/m_draw.f90), [source/build record](fpm-candidates/m_draw/source-review.json) and [verified output](fpm-candidates/m_draw/verified-output.txt).

## fortran-lua53

Upstream Lua 5.3 bindings and source code are unchanged. A checksum-guarded manifest edit links the versioned Debian Lua 5.3 library instead of the unversioned lua name. The native development package is locked to 5.3.6-2+b4. The consumer defines a Lua function in memory, calls it for four integer arguments, independently verifies integer squares and real square roots, checks Lua status and function presence, empties the stack after each call and closes the interpreter. No files or external services are needed. Lua modules, callbacks into Fortran and arbitrary scripts are not comprehensively validated.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-lua53.f90), [source/build record](fpm-candidates/fortran-lua53/source-review.json) and [verified output](fpm-candidates/fortran-lua53/verified-output.txt).

## netcdf-fortran

Selected serial classic-format Fortran sources follow the upstream CMake classic-library source set and use the unchanged public netCDF-C API. The operator-owned FPM wrapper retains original include files and sets HAVE_F2008, HAVE_TS29113_SUPPORT and NO_NETCDF_2 for the GNU 16 Linux environment; no library sources are edited. The native libnetcdf-dev package is locked to 1:4.9.3-1. The consumer writes a 3-by-2 real array and units attribute to a classic dataset, reopens it, checks dimension lengths, attribute and every value, then removes the file. NetCDF-4-specific Fortran interfaces, the old V2 API, parallel I/O and all data types are outside this selected build and verification scope. Source exports require the native netCDF C development library.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/netcdf-fortran.f90), [source/build record](fpm-candidates/netcdf-fortran/source-review.json) and [verified output](fpm-candidates/netcdf-fortran/verified-output.txt).

## shtools

The current source archive and tags v4.14.1 and v4.14.0 exceed the unchanged 16 MiB source download limit. The source preparer stops before extraction or compilation; no compiler failure is claimed. Complete archive checksums are unavailable because bounded downloads are aborted at the limit. A smaller reproducible source distribution or separately reviewed preparation support is needed.

See the [pinned download attempts](fpm-candidates/shtools/preparation-failure.json).

## scifortran

Selected integration subset, explicitly labeled in the menu: SF_INTEGRATE, GAUSS_QUADRATURE and standalone bundled QUADPACK procedures. Original include files remain in their source directories and the operator FPM wrapper compiles only the listed library files. Checksum-guarded edits promote 478 long coefficient literals from E to D exponents in DATA statements and REAL(8) PARAMETER array initializers in two bundled QUADPACK files. Each target array is checked to be REAL(8), and all decimal digits are retained. This avoids evaluating the supplied coefficients at default-real precision before assignment to double precision; formulas and the default-real compiler mode are unchanged. The linked quadrature-fortran BSD-3-Clause notice is restored as comments in GAUSS_QUADRATURE so source exports retain it. The consumer checks the Simpson and trapezoidal integrals of a sampled cubic against 1/4, adaptive integration of exp(x) over [0,1] against e-1 and exp(-x) over [0,infinity) against 1, and rejects nonfinite results. All six finite-interval Gauss-Kronrod rule choices are also checked against e-1. The example uses module callbacks: an initial consumer with internal callbacks segfaulted in the sandbox. Other SciFortran modules, MPI, linear algebra, the SCIFOR umbrella module, multidimensional/vector quadrature and all integration options are outside this selected build and verification scope.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/scifortran.f90), [source/build record](fpm-candidates/scifortran/source-review.json) and [verified output](fpm-candidates/scifortran/verified-output.txt).

## forpy

The existing generated upstream forpy_mod.F90 source is wrapped for FPM without running Fypp or changing the library. It embeds the sandbox Python 3.12 runtime using the linker flags advertised by python3-config --embed --ldflags, with an explicit runtime library search path. The consumer copies a 2-by-3 Fortran real64 array to NumPy, calls numpy.sum and numpy.linalg.norm, verifies both returned scalars independently in Fortran and checks finite values and every API status. Python references are destroyed before finalization. Other Python versions, no-copy array lifetimes, callbacks, Python extension modules and plotting are not validated. Exported projects need Python and NumPy and linker flags appropriate to the local Python installation.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/forpy.f90), [source/build record](fpm-candidates/forpy/source-review.json) and [verified output](fpm-candidates/forpy/verified-output.txt).

## galahad

The current source archive and tags v5.5.3 and v5.5.2 exceed the unchanged 16 MiB source download limit. Preparation stops before extraction or compilation; no compiler failure is claimed. Complete archive checksums are unavailable because bounded downloads are aborted at the limit. A smaller reproducible source distribution or separately reviewed preparation support is needed.

See the [pinned preparation investigation](fpm-candidates/galahad/source-review.json).

## fkb

The upstream CMake neural library source set is wrapped for FPM in REAL64/INT32 mode with single-image coarrays and OpenMP. The deterministic consumer writes and loads a tiny two-dense-layer ReLU network, checks four predictions against independently calculated weights and biases, and verifies saving and reloading the model. K (Approximation) describes the tested neural-network inference. Training, Keras conversion tools, dropout and batch normalization are not verified; no optimization classification is inferred from their presence.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fkb.f90), [source/build record](fpm-candidates/fkb/source-review.json) and [verified output](fpm-candidates/fkb/verified-output.txt).

## ntpoly

The upstream Fortran library source set is wrapped for FPM with pinned MPICH and OpenBLAS native dependencies. The verified example uses exactly one MPI process, serialized MPI thread support and shared-memory/self UCX transports in the restricted sandbox. For a real symmetric positive-definite 2-by-2 matrix with eigenvalues 1 and 9, it checks SquareRoot, InverseSquareRoot and Invert against analytic matrices and independent product residuals, rejecting nonfinite values. D covers matrix functions and D2 covers inversion. Multiple MPI processes, distributed scaling, complex matrices and other solver families are outside this verification scope. Local exports require MPI/OpenBLAS development libraries and locally appropriate compiler/linker flags.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/ntpoly.f90), [source/build record](fpm-candidates/ntpoly/source-review.json) and [verified output](fpm-candidates/ntpoly/verified-output.txt).

NTPoly uses a single MPI process. Its UCX runtime prints a network-discovery diagnostic about the sandbox?s unavailable `/sys/class/net`; the checked program exits successfully and passes all analytic and residual checks. The [runtime probe](fpm-candidates/ntpoly/mpi-runtime-probe.txt) and verified output retain this diagnostic. EigenExa remains disabled; its external-module declaration only accommodates FPM dependency scanning of a guarded `USE`.

## mpifx

The upstream CMake library source list is generated with Fypp 3.2, with every generated file checksum locked in the recipe. The example exercises communicator initialization, real-vector broadcast, real and integer all-reduce and in-place maximum reduction on exactly one MPI process, checking API statuses and returned data. MPICH is pinned and UCX transports are limited to self/shared memory. This illustrates typed communication APIs, not parallel execution or speedup; point-to-point messaging, multiple processes and other wrappers are outside verification scope. Classification R covers the tested service routines.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/mpifx.f90), [source/build record](fpm-candidates/mpifx/source-review.json) and [verified output](fpm-candidates/mpifx/verified-output.txt).

## scalapackfx

The upstream CMake library source list is generated with Fypp 3.2 and exact generated-output checksums. The example uses a 1-by-1 BLACS grid and pinned MPICH, ScaLAPACK and OpenBLAS native libraries. It computes eigenvalues and eigenvectors of a symmetric 3-by-3 tridiagonal matrix using scalafx_psyev, checks eigenvalues against 2-sqrt(2), 2 and 2+sqrt(2), and independently checks eigenpair residuals and orthogonality. All entries must be finite. D4a1 (ordinary real symmetric eigenproblems) applies to the tested eigensolver. This is a one-process API example, not a distributed-performance demonstration; other solvers, generalized eigenproblems and multiple processes are not verified.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/scalapackfx.f90), [source/build record](fpm-candidates/scalapackfx/source-review.json) and [verified output](fpm-candidates/scalapackfx/verified-output.txt).

## easy-plplot

The existing upstream FPM package is compiled against pinned PLplot native libraries and the Cairo file driver. The main plots sine and cosine over [0,2*pi] using the pngcairo device, checks that the output file exists and is nontrivial, and the restricted sandbox must return a valid PNG preview for browser display. GUI devices, animation, interactive windows and other plotting routines are outside verification scope. Q describes the tested graphics functionality.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/easy-plplot.f90), [source/build record](fpm-candidates/easy-plplot/source-review.json) and [verified output](fpm-candidates/easy-plplot/verified-output.txt).

The MpiFx and ScalapackFx checks use one MPI process. As for NTPoly, UCX prints a diagnostic about the sandbox?s unavailable `/sys/class/net`; successful numerical/data checks and exit status are recorded alongside the unfiltered diagnostic. The generated-source checksums were also reproduced on Linux/Python 3.12. The initial ScalapackFx and easy_plplot consumer mistakes and their corrections are retained in each package?s source-review record; upstream library sources were not patched.

## gftl

gFTL is a header/template library, not a standalone compiled library. The catalog supplies a small integer-vector instantiation using the upstream v2 template, then verifies growth to 100 elements, retrieval of every stored square, and the independent sum 338350. Audited generated include files are committed as checksum-locked assets, with original m4 input hashes; generation follows the pinned CMake rules while omitting diagnostic line markers. GNU m4 on Windows and Linux reproduces identical assets. N4 covers the tested storage container. Other template/container configurations are not verified.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/gftl.f90), [source/build record](fpm-candidates/gftl/source-review.json) and [verified output](fpm-candidates/gftl/verified-output.txt).

## gftl-shared

The catalog builds an explicitly selected subset: v1 Integer32, Integer64, default Integer, Real64, String and Unlimited vectors; StringString and Integer32Real64 maps; and v2 Integer32, Real64, String and Unlimited vectors. The consumer inserts and retrieves eight vector elements and eight map entries and verifies their sum 204. Generated v2 vector wrappers apply the upstream CMake substitutions; the original templates and Apache-2.0 notices remain intact. N4 covers container storage and N5 covers key lookup. Other upstream instantiations, sets, queues and stacks are outside this selected build and test scope. Compatible dependencies are shared through immutable exports; a source-recipe fingerprint in the FPM preprocessing profile binds generated assets and source selection to the dependency identity.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/gftl-shared.f90), [source/build record](fpm-candidates/gftl-shared/source-review.json) and [verified output](fpm-candidates/gftl-shared/verified-output.txt).

## yafyaml

The upstream YAML library is wrapped for FPM with pinned gFTL and the selected gFTL-shared containers. The checked main writes a tiny local configuration, parses an integer, a boolean, a string and an integer sequence, checks every returned value and verifies that an absent key is reported missing. Input files are removed afterwards. N1 covers configuration input and N3 covers parsing character data. The upstream parser supports a subset of YAML; full YAML conformance, all schemas and malformed-input recovery are not claimed. Source-recipe-tagged immutable dependency exports retain compatible gFTL builds.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/yafyaml.f90), [source/build record](fpm-candidates/yafyaml/source-review.json) and [verified output](fpm-candidates/yafyaml/verified-output.txt).

## pflogger

The serial pFlogger library uses pinned gFTL, selected gFTL-shared containers and yaFyaml. The checked consumer writes YAML configuration, logs four severity levels to a file, and verifies that only the two expected warning/error records were accepted. MPI logging is outside this build scope. Three additional upstream v2 map instantiations are supplied as a separate checksum-locked generated asset, leaving the existing vector asset unchanged. Root COPYRIGHT identifies Apache-2.0; the historical license PDFs are retained alongside it. R covers logging service routines.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/pflogger.f90), [source/build record](fpm-candidates/pflogger/source-review.json) and [verified output](fpm-candidates/pflogger/verified-output.txt).

## flook

The procedural flook interface embeds the repository-bundled Lua 5.3.5 and Aotus bridge. The FPM wrapper selects the upstream procedural library and bundled C sources, excludes standalone Lua interpreters and the alternative Fortran 2003 interface, and links the system math/dynamic-loading libraries. The checked consumer passes parameters to Lua, executes a short script, retrieves its real and integer results and independently checks 14 and 21. The bundled versions have their own build context; they do not replace the separately catalogued Aotus package. MPL-2.0 and the bundled Aotus/Lua notices are retained. S covers language interoperability.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/flook.f90), [source/build record](fpm-candidates/flook/source-review.json) and [verified output](fpm-candidates/flook/verified-output.txt).

## ogpf

The checked example computes a Gaussian grid and uses the upstream contour interface to generate a PNG. A checksum-guarded catalog patch selects the headless pngcairo terminal instead of the upstream window terminal; the numerical and plotting procedures are unchanged. GNUplot is pinned as a native build dependency. The sandbox must return a browser-viewable PNG, and its preview is reviewed. MIT licensing is stated in both LICENSE and the upstream FPM manifest. Q covers graphics.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/ogpf.f90), [source/build record](fpm-candidates/ogpf/source-review.json) and [verified output](fpm-candidates/ogpf/verified-output.txt).

## vtkfortran

The current archive and tags v3.0.0, v2.0.10 and v2.0.9 contain a CONTRIBUTING.md symbolic link. The unchanged archive extractor rejects links before compilation. No compiler failure is claimed. A safe upstream source distribution is required before the proposed mesh-file example can be verified.

See the [source review and checked release pins](fpm-candidates/vtkfortran/source-review.json).

## fgsl

FGSL wraps GSL numerical routines. Broad classifications follow the exported interfaces for special functions, linear algebra, interpolation, root finding, optimization, integration/differentiation, ODEs, transforms, fitting and statistics. The checked consumer adapts the author's QAGS example and independently verifies the integral of log(x)/sqrt(x) on [0,1] against -4, status and error estimate. The procedure mapping covers adaptive one-dimensional finite-interval quadrature; other numerical interfaces are not runtime-verified by this example. Upstream Autoconf probes generated the complete configuration on GNU/Linux LP64 with GSL 2.8. An audited asset stages that header as config.inc; checksum-guarded edits change only its include filename in Fortran and C. The C support object and pinned system GSL libraries are linked. Local exports include the asset and patches; this configuration targets GNU/Linux LP64, and another ABI or GSL version requires regeneration against its local tools. GPL-2.0-or-later notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fgsl.f90), [source/build record](fpm-candidates/fgsl/source-review.json) and [verified output](fpm-candidates/fgsl/verified-output.txt).

## fdict

The current upstream Fypp templates produce fdict_types, variable and dictionary modules. Fypp 3.2 generates a checksum-locked asset with standard integer/real/complex/logical kinds, arrays through rank five, iso_fortran_env, optional extended kinds disabled and the upstream CMake default of non-pure interfaces. No CMake or Fypp runs in visitor preparation. The checked consumer stores and retrieves integer, real64, string and integer-array values, checks each returned value and frees the dictionary. N4 covers container storage and N5 covers key lookup. Earlier v0.7.1 preparation failed on missing generated includes; the current template generation resolves that blocker without downloading release assets or weakening archive checks. MPL-2.0 notices remain intact.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fdict.f90), [source/build record](fpm-candidates/fdict/source-review.json) and [verified output](fpm-candidates/fdict/verified-output.txt).

## flibcpp

The upstream SWIG-generated Fortran modules and C++ wrappers are built together; SWIG is not run. The upstream CMake configuration supplies only a small version-definition source. FPM 0.12 ignores .cxx, so the catalog stages unchanged wrapper contents as .cpp and preserves all original source files. The checked consumer verifies a sorted seven-element array, an existing-key position and a missing-key result. N5 and N6 classify searching and sorting, while S identifies the interoperability utility. Upstream vector, map, set, string and random facilities are included but not exercised by this consumer. MIT notices and the Apache-2.0 CMake helper notice remain intact. Local exports need compatible C++ and Fortran compilers.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/flibcpp.f90), [source/build record](fpm-candidates/flibcpp/source-review.json) and [verified output](fpm-candidates/flibcpp/verified-output.txt).

## libmbd

The serial Fortran library and Fortran-written C interface are selected from the upstream CMake target and linked with pinned OpenBLAS. MPI/ScaLAPACK and ELSI are disabled. An audited version module uses an explicitly identified 0.0.0 plus pinned-commit suffix for the Git archive, rather than claiming a release version. The checked main adapts the author's argon-dimer tests at four angstrom separation, verifies dispersion energy and gradient norm against upstream reference values, checks finite results and equal/opposite gradients, and checks library exceptions. D4 covers the Hamiltonian diagonalization used by the many-body dispersion calculation; Z denotes the domain-specific physical model, not a general-purpose eigensolver interface. Other molecules, periodic systems, distributed runs and all available models are outside this consumer verification scope. MPL-2.0 notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/libmbd.f90), [source/build record](fpm-candidates/libmbd/source-review.json) and [verified output](fpm-candidates/libmbd/verified-output.txt).

## dtfft

The CPU-only Fortran target is configured upstream with FFTW enabled, MPICH, input checks, and no C/C++/Python API, GPU, compression or OpenMP support. Its complete generated configuration header and source selection are checksum-locked. The checked main initializes exactly one MPI process with self/shared-memory UCX transports, transforms an 8-by-8 complex impulse, independently checks that every forward coefficient equals one, then verifies inverse reconstruction after normalization. J1 covers the multidimensional Fourier transform. Multiple processes, distributed performance and other FFT executors are not verified by this example. Local exports require compatible MPICH and FFTW development libraries and locally appropriate include/link flags. GPL-3.0-or-later notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/dtfft.f90), [source/build record](fpm-candidates/dtfft/source-review.json) and [verified output](fpm-candidates/dtfft/verified-output.txt).

MPICH/UCX emits a diagnostic about the sandbox lacking /sys/class/net even with self/shared-memory transports selected. It is nonfatal in this verified single-process run; both FFT checks pass with zero maximum error. Multi-process operation is not claimed.

## psblas

Adding the four existing MINRES implementations fixes the earlier undefined-symbol link failure. All 813 library sources and the checked main compile with GNU Fortran 16.2.0, and direct execution as nobody succeeds: solution [1,2,3], three CG iterations, maximum residual 1.7764e-15. However, FPM 0.12 remains CPU-active after producing the executable, without completing its build or writing compile_commands.json. A disposable checkpoint clone also starts another library build rather than providing a completed reusable cache. The operator stopped the original job after observing the post-link stall; this was not a Fortran compiler or numerical failure and not the public service timeout. Ordinary edited-main cache reuse remains unverified, so PSBLAS is not selected.

Investigate FPM post-link processing and stable flag/dependency-cache handling for this large source graph, then finish the standard prebuild and ordinary restricted-sandbox edited-main verification. The temporary checkpoint is not a published or verified library.

See the [pinned investigation](fpm-candidates/psblas/source-review.json), [direct solve](fpm-candidates/psblas/direct-run.json), [build tail](fpm-candidates/psblas/post-link-build.log), and [previous link failure](fpm-candidates/psblas/previous-link-failure.json).

## dbcsr

The upstream CMake-selected serial CPU library is rendered with Fypp 3.2, with exact generated-output hashes. Simple USE lists emitted from Python sets are sorted for reproducibility across Python versions and platforms; numerical algorithms are unchanged. MPI, OpenMP, GPU, LIBXS and LIBXSMM are disabled, and the library links pinned OpenBLAS. The diagnostic filename macro uses __FILE__. The checked main creates two 4-by-4 block-sparse matrices, multiplies them through dbcsr_multiply, reconstructs the result and independently compares it with MATMUL, requiring finite entries and a small maximum error. D1 covers matrix operations. Parallel scaling, accelerators and tensor operations are outside this verification scope. GPL-2.0-or-later notices are retained. The wrapper repeats the base-hooks USE list so FPM can order dependencies hidden in the original include. Its manifest permits legacy implicit external BLAS/LAPACK calls; runtime and bounds checks remain enabled.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/dbcsr.f90), [source/build record](fpm-candidates/dbcsr/source-review.json) and [verified output](fpm-candidates/dbcsr/verified-output.txt).

## 2decomp-fft

The upstream CMake-selected CPU library uses the built-in generic Fourier transform backend, double precision and pinned MPICH. OpenMP is disabled. The example adapts the author-provided complex FFT example, initializes exactly one MPI process with self/shared-memory UCX transports, transforms an 8-by-6-by-4 complex impulse, independently checks that all forward coefficients equal one, and verifies inverse reconstruction after normalization. J1 covers the multidimensional Fourier transform. Multiple MPI processes and distributed performance are not verified. Local exports need compatible MPI development libraries and locally appropriate include/link flags. BSD-3-Clause notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/2decomp-fft.f90), [source/build record](fpm-candidates/2decomp-fft/source-review.json) and [verified output](fpm-candidates/2decomp-fft/verified-output.txt).

## ennuf

The pinned upstream neural_net_mod module is compiled with an audited, generated fixed-weight model: two inputs, two ReLU hidden units and one output in REAL32. Operator generation uses the author Model/Dense/Activation API and NumPy 2.2.6; neither TensorFlow, PyTorch nor Python inference runs in visitor jobs. The generator sorts the imported layer routine names for reproducibility; network operations are unchanged. Four inputs exercise positive and clipped hidden units and predictions are checked against independently evaluated weights and biases, including negative and positive outputs and finiteness. K covers inference as approximation; no least-squares fitting or training classification is inferred. The sample network is illustrative, not a trained scientific model. Other network layers, external model conversion and training are not verified. BSD-3-Clause and Crown copyright notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/ennuf.f90), [source/build record](fpm-candidates/ennuf/source-review.json) and [verified output](fpm-candidates/ennuf/verified-output.txt).

## ddpcm

The pinned ddCOSMO library and original fixed-form Lebedev quadrature source are wrapped for FPM with extension-based source form and legacy external interfaces. OpenMP directives are inactive in this serial profile and OpenBLAS supplies dense linear algebra. The checked consumer adapts the author main and formaldehyde input, embedding its four-atom coordinates, radii, charges and solver settings. It compares solvation energy and all force components against the author reference output, requires finite values and checks zero net force. Full-sized dummy arrays replace the unused one-element placeholders in the example while leaving library numerical routines unchanged. D2 identifies the Jacobi/DIIS linear-system solution used by cosmo; Z denotes the physical solvation model. Other molecules, solvent parameters, quantum densities and parallel performance are outside this verification scope. LGPL notices and author reference requests remain in the source tree.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/ddpcm.f90), [source/build record](fpm-candidates/ddpcm/source-review.json) and [verified output](fpm-candidates/ddpcm/verified-output.txt).

## paramonte

The reviewed 128 MiB operator allowance passes source staging and prepared-bundle extraction. After checksum-guarded submodule compatibility edits and serial external-module declarations, FPM 0.12 accepts the model and GNU Fortran 16.2.0 starts compilation. The build stops around 24% at pm_sampling_base.F90 because USE pm_sysPath appears inside pm_sampling_base.imp.F90 and the required pm_syspath.mod has not been built. This is a remaining FPM dependency-ordering issue involving a preprocessor include, not the former source-size rejection. Runtime and edited-main cache reuse remain unverified.

Review preprocessing of the staged Fortran includes before FPM dependency discovery, or an operator-only CMake build/import adapter, while preserving source pins, explicit serial settings, public limits and existing cache keys. Then repeat compilation, the checked normal-sampling/CDF consumer and edited-main cache reuse. The draft is not a verified catalog entry.

The [source/build record](fpm-candidates/paramonte/source-review.json) includes the pinned 128 MiB exception and staged compatibility work. The [attempt diagnostics](fpm-candidates/paramonte/build-attempts.json), [draft recipe](fpm-candidates/paramonte/catalog-draft.json) and [unverified driver](fpm-candidates/paramonte/main.f90) are retained for a future retry.

## libnegf

The pinned GitHub archive contains six symbolic links in test directories. The unchanged source extractor rejects links before compilation. This does not establish a compiler or numerical failure.

Obtain a pinned regular-file source distribution or review narrowly scoped safe handling of internal test links; then configure its MPI and BLAS/LAPACK requirements and verify a small author-derived transport example.

See the [pinned source and preparation record](fpm-candidates/libnegf/source-review.json).

## dftd4

The original FPM library and pinned mctc-lib, multicharge, Jonquil and TOML-F dependencies are compiled with GNU Fortran 16.2.0 and pinned OpenBLAS. Jonquil and mctc-lib request different TOML-F tags; the operator recipe resolves both to the mctc-lib-requested 0.4.2 commit, checksummed in the dependency lock. The checked consumer adapts the upstream test_pbed4_mb01 reference and embeds MB16-43/01 geometry from mstore v0.4.0, retaining its Apache-2.0 attribution. PBE-D4 two-body energy is compared with -0.018578752883363366 Hartree to 1e-10 Hartree. It also checks finite results, zero net force, translation invariance and one analytical gradient component against a central finite difference with step 1e-5 bohr and tolerance 1e-6. Z denotes the physical dispersion model; no general-purpose differentiation or linear-system interface is inferred from its internal calculations. Other molecules, periodic systems, D4S, three-body terms and all gradients are outside this consumer verification scope. No numerical library source edits are applied; all dependencies use immutable shared archive exports. LGPL-3.0-or-later and dependency notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/dftd4.f90), [source/build record](fpm-candidates/dftd4/source-review.json) and [verified output](fpm-candidates/dftd4/verified-output.txt).

## elpa

The declared GitHub mirror archive and both probed 2026.02 release tags contain symbolic links, including a parent-directory link under fdep/test_project and GPU/test source links. The unchanged extractor rejects them before configuration or compilation. No compiler or eigensolver failure is established.

Obtain a pinned regular-file source distribution or separately review safe handling of these links; then configure the documented non-MPI CPU build and check eigenvalues, residuals and orthogonality.

See the [pinned preparation record](fpm-candidates/elpa/source-review.json).

## progress

The pinned main archive and release tags v1.3.0 and v1.2.0 exceed the unchanged 16 MiB compressed download limit. Downloads stop before complete archive validation, configuration or compilation; no complete archive hash or compiler failure is claimed.

Obtain a smaller upstream source distribution or separately review a narrowly pinned operator download allowance. Then build the required BML dependency and adapt a small numerical example for sandbox verification.

See the [pinned preparation record](fpm-candidates/progress/source-review.json).

## ftorch

The original FTorch Fortran and C++ sources are wrapped for FPM, using pinned Debian CPU LibTorch 2.6.0+dfsg-7, the C++20 mode, C++11 ABI and include/definition settings from the upstream CMake target. The operator C++ flag setting is restricted to a current, unshared source-package recipe; public requests cannot set it and previous cache keys are preserved. The self-contained consumer embeds a reproducibly generated 1,766-byte TorchScript model as hexadecimal text, writes tiny.pt in the sandbox and calls the author tensor/model API in REAL64. Two different five-element inputs exercise y=2*x+1, with each output checked independently for finiteness and absolute error below 1e-12. The second call also verifies that the input tensor observes updated Fortran storage. No Python or model download runs in visitor jobs. This is an illustrative affine inference model, not a trained scientific predictor. K covers inference as function approximation; no training or optimization classification is inferred. GPU use, training, autograd, parallel execution and arbitrary external models are not verified. FTorch MIT notices and native Debian dependency notices are retained. APT estimates about 924 MB of additional native dependencies in the isolated FTorch image; these are separate from the catalog logical library-artifact total.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/ftorch.f90), [source/build record](fpm-candidates/ftorch/source-review.json) and [verified output](fpm-candidates/ftorch/verified-output.txt).

## fortjson

The pinned GitLab source compiles with GNU Fortran 16.2.0 and -fcheck=all; all 38 upstream CMake/CTest tests pass in a network-disabled gVisor operator probe. It is not selected because catalog source preparation and project export currently require GitHub sources or explicitly mapped GitHub mirrors; no usable mirror was found. This is an integration limitation, not a compiler failure. The library writes JSON; a JSON-reading demonstration would be inappropriate.

Separately implement pinned GitLab archive preparation and exported-project support, or obtain an author-maintained GitHub mirror. Then add a JSON-writing consumer and verify ordinary restricted-sandbox edited-main reuse.

See the [pinned investigation](fpm-candidates/fortjson/source-review.json).

## parquet-fortran

The pinned source archive extracts safely. Its documented full Parquet interface requires Apache Arrow >=24.0.0, including libarrow, libarrow-compute and libparquet, and C++20. None of those development packages has a candidate in the current Debian trixie image repositories. The manifest also requires FPM >=0.13 for features/profiles, while the playground uses 0.12, and references a TOML-F fork. Native dependency installation was not attempted from an unpinned external repository; compilation and runtime are not verified. No upstream compiler or Parquet round-trip failure is claimed.

Prepare a separately reviewed, pinned Arrow/Parquet native dependency image and locked TOML-F fork, adapt the library manifest for the supported FPM version, and verify a small write/read round trip plus edited-main reuse. Do not substitute an unrelated Arrow-free utility demo for the promised Parquet interface.

See the [pinned investigation](fpm-candidates/parquet-fortran/source-review.json).

## gpf

The pinned root archive and release tags v3.0.0 and v2.0.0 exceed the unchanged 16 MiB compressed source download limit. Bounded downloads stop before complete archive validation, extraction or compilation; no complete archive hash or compiler failure is claimed. The proposed M_units/M_math example and native dependencies therefore remain unverified.

Obtain a smaller reproducible author source distribution or separately review a narrowly pinned operator source-download allowance. Then audit the native dependencies and check unit conversions and numerical routines; retain all relevant per-file MIT/public-domain notices.

See the [pinned investigation](fpm-candidates/gpf/source-review.json).

## tsunami

Only the author serial Chapter 4 mod_diff and mod_initial modules are wrapped; their contents are unchanged. The main follows the chapter shallow-water time-stepping equations on a 100-cell periodic grid for 200 steps. It checks the centered difference against a discrete sine derivative, the upwind difference against an independently indexed periodic reference, Gaussian peak/symmetry, finite water height/velocity, positive total depth, nontrivial evolution, and conservation of integrated elevation. The example uses REAL32, with REAL64 accumulation of mass. I2 classifies the demonstrated PDE calculation; H1 classifies diff_centered/diff_upwind as numerical differentiation. This is an educational finite-difference demonstration, not validation of a production tsunami model. Other chapters, coarrays and parallel scaling are not verified. MIT notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/tsunami.f90), [source/build record](fpm-candidates/tsunami/source-review.json) and [verified output](fpm-candidates/tsunami/verified-output.txt).

## pfunit

The pinned serial pFUnit configuration disables MPI, OpenMP, robust/forked runners and Hamcrest, and uses the author-supported MAX_ASSERT_RANK=2 option (scalars, vectors and matrices) to retain the existing 2 MiB generated-source asset limit. The author CMake configuration supplies source selections and compiler-kind definitions; overload_template.py generates the assertions. fArgParse and its gFTL-shared/gFTL submodules are pinned at the exact upstream gitlinks, with only the required shared container instantiations generated. The FPM scanner sees a NAG-only f90_unix_proc USE even on GNU, so that inactive branch is declared external; inactive robust/Hamcrest interfaces are likewise excluded without altering original library code. A plain Fortran main constructs three TestMethod cases in a TestSuite and checks scalar, vector and matrix assertions through TestRunner/SerialContext, requiring exactly three runs and zero errors/failures. No visitor-side Python, CMake or annotation generation is needed. Higher assertion ranks, matcher DSLs, MPI, OpenMP and process-forking runners are not offered by this configuration. S denotes software testing; no numerical solver classification is inferred. Apache-2.0 and dependency notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

An intentional negative-control run changes the expected scalar result to 5 for 2+2: pFUnit reports exactly one failure, the main exits unsuccessfully, and the library is reused. See the [negative-control record](fpm-candidates/pfunit/negative-control.json).

See the [checked main](../fpm_catalog/demos/pfunit.f90), [source/build record](fpm-candidates/pfunit/source-review.json) and [verified output](fpm-candidates/pfunit/verified-output.txt).

## numerical-methods-fortran

The unchanged quadrature module compiles locally, but rectangle, trapezoidal and Simpson all return 1.111111164 for the integral of 1 on [0,1] with n=10 (expected 1). Each uses step=(b-a)/(n-1) while iterating n intervals. The checked constant-integrand reproducer exits unsuccessfully. Other modules have not been validated; no full-package or GNU 16 sandbox verification is claimed.

Ask the author to correct the quadrature interval count, then check polynomial integrals, Newton solves and an ODE example before catalog/cache verification.

See the [pinned investigation](fpm-candidates/numerical-methods-fortran/source-review.json).

## aenet

The pinned main archive and release tags v2.0.5, v2.0.4 and v2.0.3 exceed the unchanged 16 MiB compressed source download limit. Bounded downloads stopped before complete archive validation, extraction, configuration or compilation; no complete archive hash or compiler failure is claimed.

Obtain a smaller pinned author source distribution or separately review a narrowly pinned operator download allowance, then check a tiny energy/force example and cache reuse.

See the [pinned investigation](fpm-candidates/aenet/source-review.json).

## raffle

RAFFLE is pinned to release v1.0.0 because current main and v1.1.1 exceed the unchanged 16 MiB archive limit. The native FPM library is unchanged. The checked main adapts test/test_dist_calcs.f90: a two-atom silicon primitive cell and three equivalent fractional points exercise get_min_dist_between_point_and_atom and get_min_dist. Both distances must be finite and agree with sqrt(3)*0.428 within 3e-6 in REAL32. P denotes the demonstrated periodic geometry; no optimization, structure-prediction accuracy, trained model, or full upstream test-suite validation is claimed. GPL-3.0 notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/raffle.f90), [source/build record](fpm-candidates/raffle/source-review.json) and [verified output](fpm-candidates/raffle/verified-output.txt).

## plplot

The unmodified PLplot 5.15.0 modern Fortran binding modules are compiled with GNU Fortran 16 against Debian libplplot 5.15.0+dfsg2-15+b1. The author CMake precision template is configured with c_double to match the native double-precision C core; the generated include is checksum-locked. Original included parameter/interface sources and LGPL notices are retained. The checked main follows the author plinit/plenv/pllab/plline/plend API, checks finite sine samples and known extrema, requests the headless pngcairo driver at 800x500, and verifies the generated PNG signature and nontrivial size. The sandbox must return a browser-viewable PNG, which is visually reviewed. Q covers graphics. Native C/Cairo libraries and fonts are installed only in this package image; no precompiled Debian Fortran module files are used by the consumer. Interactive windows, other output drivers and the full upstream example/test suite are not verified.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/plplot.f90), [source/build record](fpm-candidates/plplot/source-review.json) and [verified output](fpm-candidates/plplot/verified-output.txt).

## fortran-curl

Release 0.8.0 is pinned because its documented libcurl minimum is 8.10.0, compatible with the pinned Debian libcurl 8.14.1-2+deb13u7; current main requires 8.20.0. The original FPM library and C helpers are unchanged. The example adapts examples/url/url.f90 and checks successful URL parsing plus exact host, path, port and query strings, changes the path and checks the reconstructed URL. The C URL handle is released and cleared by the caller, following the 0.8 cleanup semantics. N3 describes parsing/constructing character data. No network request is made; sandbox internet access remains disabled. HTTP transfers, authentication, mail protocols and other libcurl facilities are not runtime-verified. ISC notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-curl.f90), [source/build record](fpm-candidates/fortran-curl/source-review.json) and [verified output](fpm-candidates/fortran-curl/verified-output.txt).

## m_history

The unmodified M_history redo editor records two commands in its scratch history file. The self-contained main supplies editing directives through the optional lun argument, recalls line 1, changes 290 to 300 and checks the result, then recalls line 2 and verifies that its original text remains unchanged. No shell command is executed and no interactive terminal is required. The main follows the author application in using a 1024-character buffer. An initial 120-character buffer triggered an upstream bounds error at cin(1:255); that diagnostic is retained separately, and shorter buffers are not verified/supported by this catalog example. N1/N3 cover command input and character editing; no numerical-method classification is inferred. MIT library notices and the public-domain author application notice are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/m_history.f90), [source/build record](fpm-candidates/m_history/source-review.json) and [verified output](fpm-candidates/m_history/verified-output.txt).

M_history input-buffer limitation: the checked main uses the author example's 1024-character buffer. A 120-character buffer failed an upstream substring bounds check; see [diagnostic and reproducer](fpm-candidates/m_history/short-buffer-failure.txt).

## m_cli

The original M_CLI FPM library is unchanged. The checked consumer adapts the author example/demo3.f90, translating a prototype command into NAMELIST text and checking integer, real, logical, character and three-element real array defaults before using the scaled sum. No stdin or program arguments are required; the editable prototype supplies the defaults. Actual command-line overrides, help/error paths and interactive examples are not runtime-verified here. N1/N3 cover command input and character parsing; no numerical-method classification is inferred. Public-domain/Unlicense notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/m_cli.f90), [source/build record](fpm-candidates/m_cli/source-review.json) and [verified output](fpm-candidates/m_cli/verified-output.txt).

## fortran-modbus

The original Fortran 2018 FPM bindings are compiled against pinned Debian libmodbus 3.1.11-2. The consumer checks positive, negative and zero single-precision values through the ABCD, BADC, CDAB and DCBA register conversion APIs and prints register words in hexadecimal. These are offline operations, with no socket, serial port or Modbus device. N2 covers bit/byte representation; the catalog does not claim verified device communication. The author test/test_modbus.f90 documents context use but is not used as a device test. ISC notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-modbus.f90), [source/build record](fpm-candidates/fortran-modbus/source-review.json) and [verified output](fpm-candidates/fortran-modbus/verified-output.txt).

## gtk-fortran

The original gtk-fortran 4.8.0 FPM manifest is unchanged and builds the core bindings and high-level helper modules. GNU 16 compilation initially stopped in gtk-hl-dialog.f90 because f_c_string was resolved as a function rather than the legacy subroutine alias. Eleven checksum-guarded call-name replacements use the equivalent convert_f_string generic already provided by gtk_sup, matching current upstream spelling; arguments and implementations are unchanged. The unpatched diagnostic is retained. This release targets GTK 4.18.4/GLib 2.84.1 and is linked against pinned Debian GTK 4.18.6, with Cairo 1.18.4. The example adapts the author Cairo drawing API to an image surface, checks Cairo statuses and PNG signature/size, and draws curves, circles and text without gtk_init, a window or a display server. The returned browser preview is visually reviewed. Q covers graphics. Desktop widgets, events, interactive GUI sessions and the full upstream tests are not runtime-verified. GPL-3.0-or-later with GCC Runtime Library Exception 3.1 notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/gtk-fortran.f90), [source/build record](fpm-candidates/gtk-fortran/source-review.json) and [verified output](fpm-candidates/gtk-fortran/verified-output.txt).

## fycollections

The original FyCollections backend and author examples/list/type_intlist.fpp and type_stringlist.fpp are generated with Fypp 3.2 without changing their algorithms. Six generated Fortran files, checksums of all template/license inputs, and xgenerate_fycollections.py retain a reproducible recipe. The package supplies the author IntList and StringList specializations, not automatic runtime generation for arbitrary user types. Its operator FPM wrapper uses version 0.0.0 to identify no inferred upstream release; the source is pinned by commit. The checked main adapts the author integer/string list examples and checks append, insertion, retrieval, successful/missing searches, integer deletion and allocatable-list finalization. N4/N5 cover storage containers and searching. Pointer/array list specializations and the complete upstream tests are not verified. BSD-2-Clause notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fycollections.f90), [source/build record](fpm-candidates/fycollections/source-review.json) and [verified output](fpm-candidates/fycollections/verified-output.txt).

## fortran-sdl2

The original FPM library and Fortran bindings are unchanged. The image pins SDL 2.32.4, SDL2_image 2.8.8, SDL2_mixer 2.8.1, SDL2_ttf 2.24.0 and GL/GLU development libraries; native link flags are recorded in the catalog build environment. The checked main creates a 640x360 32-bit software surface, fills a background and three bars, checks source pixels, saves a PNG, reloads it through the package IMG_Load API, and checks dimensions plus the file signature/size. The pinned bindings omit IMG_SavePNG, so the main includes only that standard C function declaration. No image encoder or drawing algorithm is substituted for SDL. No video subsystem, window, display server, hardware renderer, audio device or event loop is needed. The returned browser preview is visually reviewed. Q covers graphics. Interactive rendering, audio, fonts and OpenGL/GLU routines are compiled/linked facilities but not runtime-verified by this consumer. ISC notices are retained.

The pinned library and checked consumer passed with GNU Fortran 16.2.0 and FPM 0.12.0. An edited main also passed in the restricted sandbox, rebuilding only the main and executable.

See the [checked main](../fpm_catalog/demos/fortran-sdl2.f90), [source/build record](fpm-candidates/fortran-sdl2/source-review.json) and [verified output](fpm-candidates/fortran-sdl2/verified-output.txt).
