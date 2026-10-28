# Shared precompiled dependencies

Selected GNU Fortran 16 packages can reuse an immutable dependency archive instead of carrying another copy of its objects and library archives. This currently covers stdlib and its catalog consumers. Other selected packages retain their existing caches. Custom URLs and other compilers still build from source.

Sharing requires matching source revision and archive checksum, compiler/FPM recipe, preprocessing settings, compiler and linker flags, and pinned native libraries. A different configuration gets a separate dependency build. For example, econ-toolchain's single-image coarray/OpenBLAS configuration does not reuse the default stdlib variant.

The exporter collects existing compiled Fortran and C objects from a verified package image, creates one archive, and copies the dependency's module files, headers, and license notices. It invokes no compiler. File checksums are checked when the immutable dependency image is built. Package builds use a small FPM shim that links that archive; changing the user's main program recompiles the main and links the executable.

Execution sandboxes read dependency files from their image. They do not mount a shared writable cache or download dependencies. Normal request limits and sandbox isolation still apply. The sharing adapter is installed only in opted-in package images, so unrelated packages keep their current build keys and workers.

## Adding another consumer

First add and pin the package and its dependencies in `fpm_catalog.json`, with an example in `fpm_catalog/demos`. Then opt it into sharing:

```text
python xshared_fpm.py --enable PACKAGE_ID
```

The default shared repository is `fortran-lang/stdlib`. Use `--dependencies OWNER/REPOSITORY` to select another pinned leaf dependency. The initial implementation supports leaf libraries containing Fortran and C sources; it rejects dependencies that themselves depend on another FPM package, patched dependency sources, and source-subset repackaging. It does not assume two independently configured builds are binary compatible.

Build and verify the selected package using the Python environment containing Modal:

```text
python xprecompile_fpm.py --packages PACKAGE_ID
```

A matching published dependency image is reused. Otherwise the builder exports a compatible existing package image. On a fresh installation without a compatible donor, it first performs a normal source build to establish that dependency variant. Later consumers reuse it. A failed compatibility or integrity check stops publication.

After reviewing the changes, deploy with:

```text
python xdeploy_fpm.py --packages PACKAGE_ID
```

The operator's ignored `.fpm-audit-cache` retains donor references and persistent image-layer inputs. Export transfers use the operator-only Modal Volume `fortran-fpm-shared-libraries`. Neither visitor sandboxes nor prebuild sandboxes mount this Volume. Fork operators use their own Modal account and cache.

## Storage measurements and rollout

The verified migration of nine catalog entries reduced active logical artifacts from **3,983 MiB to 1,180 MiB**, including 3 separately configured stdlib exports counted once each. Econ-toolchain's package-owned artifacts fell from **341.6 MiB to 3.6 MiB**; its shared stdlib archive is accounted for separately. All nine edited-main examples passed in the ordinary restricted sandbox.

[Validation measurements](fpm-precompiled-validation.json) count package-owned objects/modules/archives plus each shared dependency export **once**. A package's `artifact_bytes` excludes its separately listed `shared_dependencies`. Legacy package measurements still include dependencies and FPM flag variants inside their individual build trees.

These are logical artifact sizes, not a measurement of compressed image storage or a monthly bill. Old published package images remain available during rollout, because the public service may still use them until redeployment. The operator export Volume also retains files. Consequently a smaller active catalog does not immediately reclaim all previously stored bytes.

Downloaded local projects retain the original pinned sources and ordinary FPM builds. They do not depend on Modal archives or `/opt/fpm/shared` paths. Existing source patches and native-library requirements remain documented in the catalog.
