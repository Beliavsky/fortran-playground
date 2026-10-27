# Discovery package compatibility audit

Tested 2026-10-27 in the hosted Linux sandbox with GNU Fortran 16.2.0 and FPM 0.12.0. Twenty non-precompiled packages were chosen across numerical, string, I/O, and utility categories. This is a diagnostic sample, not an estimate of the entire catalog.

The baseline used **Build only** at the full commits recorded in [the machine-readable results](fpm-discovery-audit.json), under normal service limits. Eleven built successfully; nine of those had no application target. A library can still have examples or tests, or be used by a custom main program.

| Repository | Baseline | Verification with updated worker |
| --- | --- | --- |
| awvwgk/blas-interface | Build passed | |
| gha3mi/forblas | Missing source file | |
| HugoMVale/odrpack95 | Missing OpenBLAS | Build passed with numerical libraries |
| sebastiandyrda/lib_statistics | Build passed | |
| jacobwilliams/odepack | Implicit-interface compilation error | |
| princemahajan/FLINT | Preprocessing required | Build passed with Preprocess enabled |
| arjenmarkus/pointsets | Build passed | |
| wcota/rndgen-fortran | Build passed | |
| everythingfunctional/strff | GitLab dependencies unsupported | |
| Carltoffel/Fortran-String-to-Real | Build passed | |
| 0382/argparse-f | Build passed | |
| davidpfister/subprocess.f | Windows-specific C++ include path | |
| lauvergn/AD_dnSVM | Missing BLAS/LAPACK | Build passed with numerical libraries |
| zoziha/Auto-Diff | Build passed | |
| jacobwilliams/kronrod | Build passed | |
| Euler-37/integrate_fortran | Build passed | |
| geospace-code/h5fortran | HDF5 metapackage unsupported | |
| freevryheid/flibcsv | Build passed | |
| furstj/interpolation | stdlib metapackage unsupported | |
| vmagnin/formidi | Build passed | |

Fourteen distinct packages from this sample now have a successful build verification, including the eleven baseline successes. The three repaired builds used the same revisions as the baseline. These were temporary sandbox jobs; no package libraries were added to the precompiled catalog.

## Changes resulting from the audit

- Newly discovered packages without supplied demo programs default to **Build only**. Selected examples and translated R workflows retain their existing behavior.
- A successful build reports discovered application, example, and compiled-test targets. The page offers action buttons and a target menu. Choosing an action or target never submits a job; users explicitly submit again. Tests are discovered after a Test build.
- Clean GNU 16 and GNU 17 images include OpenBLAS, providing the `blas`, `lapack`, and `openblas` linker libraries. Local users install equivalent libraries themselves.
- **Preprocess** adds the selected compiler's preprocessing flag to the existing FPM debug profile. FLINT was verified with this enabled, so loading that audited entry selects it visibly. Enabling it uses a clean hosted build rather than a precompiled library. The setting is also available as `--preprocess` in the hosted/local FPM runners and is preserved in downloaded projects.
- The preparer retains `openmp = "*"` and `blas = "*"` for FPM to discover offline inside the sandbox. A deterministic program using both was compiled and run successfully. Other metapackages and registry dependencies remain unsupported.
- Catalog descriptions show the tested commit and audit outcome, including verification with the updated worker where applicable. These are historical results; a repository's default branch may change.

## Remaining failures

None of the sampled failures was caused by a timeout, so the resource limits remain unchanged. The six remaining failures need separate work: missing/submodule source (`forblas`), an implicit-interface error (`odepack`), GitLab dependencies (`strff`), a Windows-specific C++ include (`subprocess.f`), and HDF5/stdlib metapackages (`h5fortran` and `interpolation`). Upstream source and interface checks are preserved.

## Publishing and deployment

Push the frontend and catalog changes through GitHub Pages, and redeploy the FPM backend with `xdeploy_fpm.py` to enable preprocessing, target groups, portable metapackages, and numerical libraries. The ordinary source-file playground service needs no redeployment. Restart the local server for local use.

The library recipe identity remains `c5a4381ee9e2eae85215f045`. Existing compiled package libraries are reused. The worker changed, so deployment refreshes worker layers and runs changed-main verification; do not use `--rebuild`.

To repeat the baseline (up to 20 public build jobs, subject to ordinary quotas):

```text
python xfpm_discovery_audit.py
python xfpm_examples.py
```

The script records baseline results. Separate `fix_verifications` record the candidate-worker checks above. Repeating a baseline audit replaces the report; preserve any historical results you want to retain. No audit runs during site builds, catalog browsing, or normal deployment.
