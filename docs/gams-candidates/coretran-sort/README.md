# Unverified coretran unstable sorting setting

At revision `204c4707f6680b6d7d1e4da39077d0fd3acfe37e`, the mixed-setting probe compiled with GNU Fortran 16.2.0, then failed a runtime bounds check in `src/core/sm_partition.f90`: explicit `stable=.false.` on 16 equal integer32 values (all 7) accesses element 17 of a 16-element array.

- [Source](default-and-stable.f90)
- [Pinned revision, normalized hash and finding](default-and-stable.json)
- [Complete build/run result](default-and-stable-result.json)

The diagnostic setting numbers are 1=default, 2=stable=false, 3=stable=true. Default and stable=true completed this fixture before the explicit unstable setting failed. The planned full mixed-mode suite did not complete; this evidence does not establish a default-mode failure.

The [published sorting driver](../../gams-graph-sorting.md) uses explicit stable=true on the full input suite, retaining exact sorted-value checks and the cached library's bounds checking. No library source fix was made. Numeric-only arrays do not establish stable ordering of equal-key records. Reproduce using the saved main and pinned package; hashes use UTF-8 normalized to LF. Sources use the [driver-only MIT license](../../../fpm_catalog/gams-drivers/licenses/graph-neighbors-drivers-MIT.txt).
