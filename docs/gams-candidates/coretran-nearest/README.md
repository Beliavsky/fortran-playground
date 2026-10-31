# Unverified coretran nearest-neighbor search

At revision `204c4707f6680b6d7d1e4da39077d0fd3acfe37e`, the probe compiled with GNU Fortran 16.2.0 using the cached OpenMP-enabled library and one execution thread. For two-dimensional modular data with 31 points in original order, query 15 returns squared distance 0.07390715705352345 versus the independently scanned minimum 0.048195228517966246.

- [Source](nearest-direct-reference.f90)
- [Pinned revision, normalized hash and finding](nearest-direct-reference.json)
- [Complete build/run result](nearest-direct-reference-result.json)

Coordinates are x_i=mod(7*i,101)/101, y_i=mod(13*i,103)/103. The query is [(mod(11*15,31)-5)/17,(mod(7*15,29)-4)/13]. No particular tied index is required: returned distance itself is wrong. The probe stops at the first mismatch, so its planned 60-tree/2,472-query suite did not complete.

No nearest-neighbor GAMS driver is published. The separate checked sorting driver does not verify this procedure. To reproduce, run the saved main with the pinned package and its saved library settings. Hashes use UTF-8 normalized to LF; the source uses the [driver-only MIT license](../../../fpm_catalog/gams-drivers/licenses/graph-neighbors-drivers-MIT.txt).
