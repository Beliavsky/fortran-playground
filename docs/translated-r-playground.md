# Translated R packages in the FPM playground

Choose **Collection → Translated R packages** in the [online FPM playground](https://beliavsky.github.io/fortran-playground/fpm/?collection=translated-r), or in the main local FPM page. The collection contains 596 experimental translations from [Fortran-from-R-packages](https://github.com/Beliavsky/Fortran-from-R-packages). The general Fortran catalog remains the default.

Search names, descriptions, and keywords, or filter by subject category. A package may belong to several categories. Select a package and click **Load package** to fill in its repository, pinned commit, and package directory. Loading a selection submits no job and initially selects the package's own programs and tests. **Browse pinned source** opens that package's documentation, examples, and source at the selected commit.

- **Compile and Run** builds and runs the package's application. If several applications exist, select a reported target and submit again. Packages with only FPM examples may need **My main program** or **Test** instead: this interface does not currently invoke `fpm run --example`.
- **Build only** checks that the package builds without running an application.
- **Test** runs the package's tests, optionally selecting a target.
- **My main program** lets you write a main that uses the package's modules. Consult its source documentation for module and procedure names. Your editor contents are preserved when loading a translated package.

Every translated package is downloaded and built from scratch. None is precompiled. Selection retrieves only the requested package directory and recursively required sibling directories, rather than downloading all 596 packages. Files are checked against Git blob hashes from trees at the pinned commit. GitHub dependencies outside the collection use the normal preparation rules. Downloaded FPM projects preserve the selected directory and revision for local builds.

Catalog inclusion means **available to attempt**, not verified in the playground or numerically equivalent to R. Upstream coverage and numerical validation vary; consult package documentation. Playground results indicate what that particular build or run did. The catalog records a fixed snapshot; future upstream changes appear after an explicit catalog refresh.

## Online limits

The collection uses the existing FPM service, compilers, quotas, and sandbox limits: 180 seconds to build and 30 seconds total to run/test. Source preparation retains its 60-second deadline, 32 MiB combined download budget, and 64 MiB expanded-source limit. Large packages, unavailable native libraries, unsupported dependencies, or GitHub API limits can prevent a job from running. Precompilation of the general catalog is independent of this collection. Its metadata is fetched only when selected.

## Local use

Install FPM, a Fortran compiler, and the preparation dependency, then start the shared interface:

```text
python -m pip install tomli-w==1.2.0
python xfortran_serve.py --workspace . --fpm
```

Choose **Translated R packages**. Builds use your installed compiler; GNU 16 is not bundled or required. Each submission uses a fresh temporary source/build tree, which is removed afterward. There is no persistent local package cache yet. Local execution has no hosted build/run time limits or quotas, although source preparation remains bounded and GitHub downloads require network access. Install native libraries required by individual packages yourself.

The secondary **Local FPM projects** page remains available for packages already on disk, normal incremental FPM builds, and compiler comparison.

The hosted command-line runner also accepts the package directory:

```text
python xplayground_run.py --fpm https://github.com/Beliavsky/Fortran-from-R-packages --subdirectory Metrics --action run
python xplayground_run.py --fpm https://github.com/Beliavsky/Fortran-from-R-packages --subdirectory Metrics --main main.f90
```

Add `--revision COMMIT` to reproduce a catalog snapshot; omitting it resolves the current HEAD.

## Maintenance and deployment

Refresh the discovery catalog explicitly with `python xtranslated_r_catalog.py`, optionally adding `--revision COMMIT`. This reads upstream manifests and generates `site/fpm/translated-r.json`; it performs no compilation. Normal site generation does not contact that repository or refresh this snapshot.

Publish the frontend through the normal Pages workflow and redeploy the separate FPM service with `python xdeploy_fpm.py` in the Python environment containing the Modal SDK. No translated packages are added to its precompilation list. Existing general-catalog library keys are preserved.

Deployment checks that `/api/health` advertises translated R support. If deployment fails before the API is replaced, the previous service stays active. The page detects an older API, explains that the backend must be updated, and keeps general-package workflows usable. Reload the page after deployment completes.
