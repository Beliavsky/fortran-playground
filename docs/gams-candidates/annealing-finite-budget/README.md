# Finite-schedule annealing can converge to a nonglobal point

The [one-loop draft](one-loop.f90) uses temperature 20, cooling factor 0.85,
`ns=20`, `nt=10`, `neps=4`, termination tolerance `1e-9` and a 300,000-callback
cap. All recorded two-dimensional cases and the recorded three-dimensional
amplitude-one cases passed their known-minimum checks. For the three-dimensional
shifted Rastrigin case with amplitude 10 and seed pair `(1,2)`, the solver
returned status 0 but an independently evaluated objective about `0.994959`,
with maximum coordinate error about `0.994959`. The exact global minimum is
zero at the shift vector. The consumer correctly rejected this result.

The [slower draft](slow-one-loop.f90), with cooling factor 0.9 and a
600,000-callback cap, reached the same nonglobal point for that case. Its answer
tolerances were unchanged. Complete saved results are in
[one-loop-result.json](one-loop-result.json) and
[slow-one-loop-result.json](slow-one-loop-result.json), with exact sources,
pins and cached GNU 16 library reuse.

These results illustrate stochastic finite-budget search and objective-stability
termination; they do not establish an implementation defect or a certified
global minimum. No evaluation cap was reached in the failing case. The published
checked driver is explicitly restricted to the six two-dimensional fixtures
(both amplitudes and all three original seed pairs), retaining the slower
schedule and unchanged accuracy checks. Three-dimensional global search remains
unverified. No seeds were replaced to turn failures into successes.

The independent probes use the
[playground MIT notice](../../../fpm_catalog/gams-drivers/licenses/directions-fitting-drivers-MIT.txt);
source headers retain the relative reference from their submitted location.
