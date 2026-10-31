# Unverified dynamics harmonic-response configurations

At package revision `580d04859a25126d3261e44b3fbec5111835e3a4`, both probes compile with GNU Fortran 16.2.0 and reuse the cached package library, but fail their independent static-response reference. No library patch or relaxed tolerance is included.

- [Non-unit-mass source](nonunit-mass.f90), [source hash and finding](nonunit-mass.json), [complete result](nonunit-mass-result.json): n=1, M=2, K=2 at frequency zero fails X=F/K.
- [Coupled-unit-mass source](coupled-unit-mass.f90), [source hash and finding](coupled-unit-mass.json), [complete result](coupled-unit-mass-result.json): n=2, M=I, K=Q*diag(1,4)*Q^T with a nontrivial Householder Q fails the static solution.

The probes stop at the first mismatch. Their planned full fixture counts were not completed. SHA-256 values use UTF-8 source normalized to LF. Sources use the same [driver-only MIT license](../../../fpm_catalog/gams-drivers/licenses/diagonal-response-drivers-MIT.txt).

The [published review](../../gams-diagonal-response.md) restricts successful verification to unit mass and diagonal stiffness. A correct response in that configuration does not establish correctness for these broader cases. To reproduce a probe, use its source as a custom main with the pinned dynamics package; keep the same 1e-10 response threshold.
