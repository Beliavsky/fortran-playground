# QNSTOP active-bound accuracy probes

Pinned package: `39e8273247f586fca8305ef3d8e879b27b6512d0`, GNU Fortran 16.2.0, one serial process. The existing library was reused. These failed probes are not checked drivers.

The independently written probe sources retain the [driver MIT notice](../../../fpm_catalog/gams-drivers/licenses/matrix-roots-box-drivers-MIT.txt); upstream package licenses remain separate.

Both sources first solve three interior quadratics, then a face-minimum problem:

```text
f(x) = (x1-3)**2 + 2*(x2+0.5)**2
-2 <= x1,x2 <= 2
exact constrained minimizer = [2,-0.5], exact minimum = 1
```

The first source uses 500 iterations; the second uses 2,000. Both use mode G, a 32-point design, tau=1, gain=10 and the fixed GNU intrinsic seed specified in the source. Each run returns status 1 (normal iteration-limit termination) but the face fixture's maximum coordinate error is approximately **0.17212**, exceeding the required **0.03**. Its normalized objective gap is approximately 0.059249. More iterations did not resolve the position error in this configuration.

- [500-iteration source](box-500-iterations.f90) / [actual result](box-500-result.json)
- [2,000-iteration source](box-2000-iterations.f90) / [actual result](box-2000-result.json)

Each JSON retains the source hash, pin, compiler, successful build and actual failed run. The sources stop at face fixture 4. Their corner fixture 5 and three-variable fixture 6 were not reached and must not be described as tested by these runs.

The published checked driver separately verifies four interior problems, including a three-variable case, with the original accuracy thresholds. It does not verify active-bound accuracy. These observations concern the recorded fixtures and settings; they do not establish a general failure of the optimization algorithm. No numerical library source has been changed.

To reproduce a failed probe, load QNSTOP in the FPM playground with a custom main, replace the main with the retained source and compile/run using GNU Fortran 16. The probe intentionally terminates with `ERROR STOP projected box minimum`. See the [checked-driver review](../../gams-matrix-roots-box.md).
