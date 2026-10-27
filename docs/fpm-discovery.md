# FPM discovery catalog

The **Selected Fortran packages** collection is the default. **All Fortran packages** is currently disabled in the online and main local FPM pages. Its catalog and implementation are retained for future use. **Translated R packages** remains a separate collection, and the external Fortran packages list link remains available.

## Restoring the All collection

Set `enableAllFpmPackages: true` in `site/config.mjs`, then commit and publish the site. The same setting applies to the main local FPM page. No Modal redeployment or package precompilation is needed.

While the setting is false, All is absent from the menu and cross-collection search suggestions. Old `?collection=all` links open Selected, and the broad catalog is not fetched by the browser. The saved data, audit results, refresh scripts, generated asset, and local static-file route remain intact. Tests cover both the disabled default and the restored collection.

The retained All collection combines the [Fortran packages list](https://beliavsky.github.io/Fortran-packages-list/) with the selected catalog. It is a discovery list, not a registry or a set of verified builds. The remaining sections describe its retained maintenance and behavior when enabled.

The broader snapshot is stored in `fpm_catalog/all-packages.json`. It records the source list's SHA-256, retrieval time, repository descriptions, categories, GitHub topics, and root-manifest check results. Only leading repository links in the source list become entries; links inside descriptions remain references. Repositories are deduplicated case-insensitively, retaining all their categories. Selected packages retain their audited revisions, examples, dependency pins, and build recipes in the combined site asset.

## Refreshing the list

Run from the repository root with Python 3.12 or later:

```text
python xall_packages.py
python xfpm_examples.py
```

The first command refreshes the upstream list, checks new repositories for a parseable root `fpm.toml`, and reads their public GitHub topic labels. Existing manifest checks and topics are reused; entries with an unknown manifest status are retried. To refresh checks and topics for every entry:

```text
python xall_packages.py --recheck
python xfpm_examples.py
```

Commit `fpm_catalog/all-packages.json` and `site/fpm/all-packages.json`, then push to publish through GitHub Pages. Site builds generate assets from the saved snapshot without contacting GitHub. Neither command compiles packages, redeploys Modal, nor changes the precompiled catalog. Refreshing topics for the selected catalog still uses `xgithub_topics.py`.

## What users can expect

The broader catalog downloads only when **All Fortran packages** is opened. Search is entirely local to the browser. A package with a valid root manifest can be loaded using the existing GitHub URL execution path. Its default branch is resolved when submitted; results report the actual commit. Selected entries use their pinned revisions and can reuse existing precompiled GNU 16 libraries for custom main programs. Other entries build from scratch, with the usual quotas, dependency restrictions, and service limits.

Manifest availability is a snapshot, not proof that a build succeeds. Missing or invalid root manifests, and unsuccessful manifest checks, disable **Load package** while keeping source links available. Topic-fetch failures preserve previous labels when available. Packages needing registry dependencies, unavailable native libraries, or larger resources may still fail. No bulk build or additional precompilation is performed.

The main local FPM page uses the same catalog and UI. Restart an older local server after updating so it can serve `site/fpm/all-packages.json`; future catalog-only updates need no server code changes. Local jobs compile from scratch using installed FPM and compilers.

New discovery entries without supplied main programs default to **Build only**. Successful builds report discovered targets so users can choose an application or example explicitly. The catalog includes saved [compatibility audit results](fpm-discovery-audit.md) for a 20-package sample; site generation merges these results without running the audit again.
