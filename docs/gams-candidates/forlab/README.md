# Unverified forlab underdetermined least-squares solve

At revision `416e5612167b6133100bef4cec116322890f66f7`, the probe compiled with GNU Fortran 16.2.0 using the cached native single-precision package library. The wide matrix A=[[-4,0,0],[0,-8,0]], b=[-1,-6] returned a nonfinite solution instead of the known minimum-norm answer [0.25,0.75,0]. Floating-point invalid/divide-by-zero flags were reported. The existing unrelated guarded optional-norm fix was retained; no new library changes were made.

- [Probe source](wide-least-squares.f90)
- [Pinned revision, normalized source hash and finding](wide-least-squares.json)
- [Complete build/run result](wide-least-squares-result.json)

The probe stops at the first mismatch; its planned full fixture count was not completed. The source hash uses UTF-8 normalized to LF. The source uses the [driver-only MIT license](../../../fpm_catalog/gams-drivers/licenses/geodesy-forlab-drivers-MIT.txt).

The [published driver](../../gams-geodesy-forlab.md) verifies only tall, full-column-rank systems. To reproduce, submit the saved probe as a custom main using the pinned package, keeping its native RPRE configuration and original acceptance thresholds.
