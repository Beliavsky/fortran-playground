# Nonlin least-squares probes that fail independent answer checks

Package revision: `2133d067886ea6eca0552ebca9ed7bb8a262e5b8`. Both probes compile with GNU Fortran 16.2.0 and reuse the package library. They supply analytical residual Jacobians. The solver reports convergence on parameter change while returning the initial parameters in the failed fixtures.

- [Default step bound source](default-step-bound.f90), [hash/finding](default-step-bound.json), [complete result](default-step-bound-result.json): with step factor 100, exact exponential fit A=0.5, B=1 from [0.25,0.5] fails the known [0.5,1] parameter reference.
- [Step-one nonzero-residual source](nonzero-residual-step-one.f90), [hash/finding](nonzero-residual-step-one.json), [complete result](nonzero-residual-step-one-result.json): with step factor 1, the 24 exact fits complete, but the first noisy fixture fails. Its residual is exp(x1)-2+t*(x2**3-1)+rho*noise for t=[-2,-1,0,1,2], noise=[1,-2,2,-2,1], rho=-0.5. Orthogonality gives exact minimizer [log(2),1] and minimum squared residual 14*rho**2=3.5. The returned initial point is [log(2)-0.7,0.5].

Sources stop at the first mismatch, so their planned 40-fit suites did not complete. Hashes use UTF-8 source normalized to LF. Sources use the [driver-only MIT license](../../../fpm_catalog/gams-drivers/licenses/jacobian-transforms-drivers-MIT.txt).

The [published driver](../../gams-jacobian-transforms.md) retains the original answer tolerances and verifies only the exact exponential family with explicit step factor 1. No upstream code or stopping criteria were patched. Reproduce a probe as a custom main with the pinned package and its saved solver settings. A normal convergence flag alone does not establish a correct minimum.
