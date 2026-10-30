# Shared precompiled dependencies

Selected GNU Fortran 16 packages can reuse immutable library archives instead of carrying another copy of their dependencies' objects and archives. Both leaf dependencies and multi-level dependency graphs are supported. Other selected packages retain their existing caches until migrated and verified. Custom URLs and other compilers still build from source.

Sharing requires matching source revision and archive checksum, compiler/FPM recipe, preprocessing settings, compiler and linker flags, and pinned native libraries. A different configuration gets a separate dependency build. For example, econ-toolchain's single-image coarray/OpenBLAS configuration does not reuse the default stdlib variant.

The exporter collects existing compiled Fortran and C objects from a verified package image, creates one archive, and copies the dependency's module files, headers, and license notices. It invokes no compiler. File checksums are checked when the immutable dependency image is built. Package builds use a small FPM shim that links that archive; changing the user's main program recompiles the main and links the executable.

Execution sandboxes read dependency files from their image. They do not mount a shared writable cache or download dependencies. Normal request limits and sandbox isolation still apply. The sharing adapter is installed only in opted-in package images, so unrelated packages keep their current build keys and workers.

## Adding another consumer

First add and pin the package and its dependencies in `fpm_catalog.json`, with an example in `fpm_catalog/demos`. For a complete shared library graph, including the selected package's own library, use:

```text
python xshared_graph.py --enable PACKAGE_ID
```

This records all pinned libraries automatically. Nodes are processed from dependencies to dependents, and each nonleaf key includes its exact child build keys. A dependency update therefore invalidates its dependent builds, while independent libraries remain reusable. Diamond-shaped graphs contain one node for each compatible library build. Cycles, unresolved dependencies and paths outside the pinned graph are rejected. Prepared source fingerprints distinguish changes to nonleaf library sources as well as manifest and build settings.

Libraries containing Fortran and C sources are supported, including procedural libraries without Fortran modules. Patched sources and source-subset repackaging are not yet supported by graph mode. Different source revisions or build settings deliberately retain separate variants. Matching leaf exports, including existing stdlib exports, keep their original identities. The graph implementation has its own fingerprint and does not invalidate unrelated packages or existing stdlib consumers.

Hosted build copies use small FPM shims and link the shared archives in dependency order, with dependents before their dependencies. Original sources remain available for local downloads. Only the user's main, a small shim, and the optional plotting helper need package-local objects.

The existing stdlib/leaf-only mode remains available with `python xshared_fpm.py --enable PACKAGE_ID`. Its default shared repository is `fortran-lang/stdlib`; use `--dependencies OWNER/REPOSITORY` to select another pinned leaf dependency. Existing consumers can keep that mode without migrating their caches.

Build and verify the selected package using the Python environment containing Modal:

```text
python xprecompile_fpm.py --packages PACKAGE_ID
```

Alternatively, enable graph sharing and build a batch with one command:

```text
python xprecompile_fpm.py --share-dependencies --packages PACKAGE_ID OTHER_ID
```

With `--share-dependencies` and no `--packages`, the builder opts the entire eligible catalog into graph sharing. This can migrate many images, so a small batch is preferable for an initial check. Patched and repackaged entries keep their existing cache recipes. The flag updates `fpm_catalog.json`; regenerate the page metadata with `python xfpm_examples.py` before committing and publishing. Without the flag, ordinary prebuilds retain the catalog's existing choices.

A matching published dependency image is reused. Otherwise the builder exports a compatible existing package image. On a fresh installation without a compatible donor, it first performs a normal source build to establish that dependency variant. All remaining nodes can export that donor's existing objects. Later consumers reuse the archives. A failed compatibility or integrity check stops publication.

After reviewing the changes, deploy with:

```text
python xdeploy_fpm.py --packages PACKAGE_ID
```

The operator's ignored `.fpm-audit-cache` retains donor references and persistent image-layer inputs. Export transfers use the operator-only Modal Volume `fortran-fpm-shared-libraries`. Neither visitor sandboxes nor prebuild sandboxes mount this Volume. Fork operators use their own Modal account and cache.

## Storage measurements and rollout

The active catalog's logical artifacts total **1,718 MiB**. 14 entries share stdlib variants; 46 more use complete library graphs. Linalg, Spectrum, Nonlin and Diffeq reference the same Linalg export; FGLM exports its constants dependency separately. ForDot and ForMatmul share their compatible Kinds, ForUnitTest and FACE exports. Friction retains a separate OpenMP/native-library build context. HR-WENO, Fortran-simplify, ECX and Orbs reuse the compatible stdlib export. ReArrayFX and AMOS F90 have their own small library exports; Scanner reuses the stdlib export. Rojff and Veggies share compatible ISO varying string and Strff exports. All edited-main examples passed in the ordinary restricted sandbox; only the main and executable were rebuilt. DFT-D4, mctc-lib, multicharge, Jonquil and TOML-F use separate immutable library graph exports. Their exact revisions and build settings determine compatibility; differently pinned TOML-F exports are retained. Different revisions and compiler settings retain separate variants.

[Validation measurements](fpm-precompiled-validation.json) count package-owned objects/modules/archives plus each shared dependency export **once**. A package's `artifact_bytes` excludes its separately listed `shared_dependencies`. Legacy package measurements still include dependencies and FPM flag variants inside their individual build trees.

These are logical artifact sizes, not a measurement of compressed image storage or a monthly bill. Old published package images remain available during rollout, because the public service may still use them until redeployment. The operator export Volume also retains files. Consequently a smaller active catalog does not immediately reclaim all previously stored bytes.

Downloaded local projects retain the original pinned sources and ordinary FPM builds. They do not depend on Modal archives or `/opt/fpm/shared` paths. Existing source patches and native-library requirements remain documented in the catalog.


## Generated gFTL dependencies

The gFTL family uses [checksum-locked generated assets](fpm-generated-sources.md). A source-recipe fingerprint in the FPM preprocessing profile binds the selected files, asset and adapter version to the existing immutable export contract. Old package definitions, leaf identities and graph identities remain unchanged. Unfingerprinted source repackaging remains blocked.

## FTorch native runtime

FTorch contributes about 9.6 MiB of logical compiled library artifacts. Its isolated CPU LibTorch dependency image additionally installs about 924 MB according to APT. Native system libraries are excluded from the artifact total above. LibTorch is installed once for this package image; no installation or Python process runs in visitor jobs, and other package images do not acquire this dependency.
