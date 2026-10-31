# HR-WENO k=2 accuracy-threshold probe

At pin `2885105a7ba98351fed299b22e9bc0c67a809d2f`, this independent periodic-advection consumer built with GNU Fortran 16.2.0 but exceeded its proposed cell-average accuracy bound. This is **not an established algorithm defect**: finite-volume spatial and time discretizations introduce error, and a convergence study is needed to assess the k=2 configuration fairly.

The first failing fixture has 64 cells, k=2 reconstruction, Fourier mode 1, velocity -1.5, phase origin 0, mean 1.25 and amplitude 0.2. The maximum cell error is `1.4202932710161154e-3`; the proposed bound is `4.0000000500000000e-4`. Exact averages are evaluated at the integrator's returned time, not at the requested output time. The fixed-step API advances past the requested time and does not interpolate back to it.

- [Exact probe source](advection-reference.f90)
- [Pin and normalized source hash](advection-reference.json)
- [Complete build/run result](advection-reference-result.json)
- [Successful k=3 driver review](../../gams-sparse-advection.md)

The published driver tests only k=3, retaining the same analytic reference, mass check and accuracy bounds. k=2 is not claimed verified by that driver. No library source patch, relaxed error threshold or disabled bounds checking was introduced. The probe is not registered as a checked driver. A suitable follow-up is to compare k=2 errors on successively refined meshes, including the extrema of smooth waves, before choosing an accuracy requirement for it.

The independent probe is a preserved variant covered by the [driver MIT notice](../../../fpm_catalog/gams-drivers/licenses/sparse-advection-drivers-MIT.txt); upstream terms remain separate.
