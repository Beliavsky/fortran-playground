# Checked GAMS gridded surface-interpolation drivers

Both examples demonstrate [E2a: Interpolation on multivariate gridded data](https://gams.nist.gov/cgi-bin/serve.cgi/Class/E2a). They use the same nonuniform rectangular grid and datasets. The B-spline driver adds a polynomial surface with analytic partial derivatives. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Shared grid and surfaces

```text
x = [-1, -0.6, 0, 0.3, 1, 2]
y = [-2, -0.75, 0, 0.5, 1.5]
case 1: f(x,y) = 1 + 2*x - 3*y + 0.5*x*y
case 2: f(x,y) = x**2 + 2*y**2 + x*y
```

Data have shape `(6,5)`, with `f(i,j)` corresponding to `(x(i),y(j))`. The different grid lengths and nonuniform spacing make coordinate orientation and interval selection visible. Every initialization and evaluation must report success, and every returned value must be finite.

For each case, the drivers first check all 30 original grid nodes. They then sample each of the 20 cells on a 5-by-5 fractional grid, including cell edges and corners, for 500 cell evaluations. Shared boundary points are intentionally visited in neighboring cells; this is a check count, not 500 distinct locations.

## Independent bilinear references

Let `s,t` be the fractional coordinates in a cell. Both examples compare to the explicit four-corner formula:

```text
(1-s)*(1-t)*f(i,j) + s*(1-t)*f(i+1,j)
  + (1-s)*t*f(i,j+1) + s*t*f(i+1,j+1)
```

They also check that sampled values remain between the minimum and maximum of the four corners. Node errors, formula errors and bound violations must be at most `1e-11` in absolute value. Case 1 must additionally reproduce its analytic bilinear surface to `1e-11` at all sampled cell points.

Case 2 is curved: bilinear interpolation generally does not equal the generating quadratic surface between nodes. Its independent reference is the four-corner formula, not an assertion of exact quadratic reproduction. No analytic-surface error is printed for that case.

finterp uses `linear_interp_2d%initialize/evaluate`. bspline-fortran uses `bspline_2d` with orders `(2,2)`, which gives linear pieces in each coordinate. The local corner bounds concern these bilinear configurations; they do not establish shape preservation of higher-order tensor splines.

## Bicubic reproduction and partial derivatives

The B-spline example then reinitializes with orders `(4,4)` (cubic degree in each coordinate) and values of:

```text
p(x,y) = 1 + x**2 + 2*y**2 + x**3*y - x*y**3 + 0.5*x**2*y**2
px      = 2*x + 3*x**2*y - y**3 + x*y**2
py      = 4*y + x**3 - 3*x*y**2 + x**2*y
pxy     = 3*x**2 - 3*y**2 + 2*x*y
```

It evaluates the value, x partial, y partial and mixed xy partial at 121 points on an 11-by-11 query grid spanning the full domain, including boundaries. This gives 484 evaluations. Each scaled error `abs(computed-reference)/max(1,abs(reference))` must be at most `1e-10`. The derivative requests use `(idx,idy)=(0,0),(1,0),(0,1),(1,1)`.

All drivers use real64. These finite deterministic examples do not validate extrapolation, missing data, arbitrary knots, all derivative orders, scattered data or general interpolation error estimates. They are not a performance ranking.

## Sources and playground links

| Driver | Pinned procedure and author test |
| --- | --- |
| [Load finterp-bilinear-surface](https://beliavsky.github.io/fortran-playground/fpm/?package=finterp&example=gams-finterp-bilinear-surface) / [Source](../fpm_catalog/gams-drivers/finterp-bilinear-surface.f90) | [Procedure](https://github.com/jacobwilliams/finterp/blob/95aaceaf86f5d4d49328b783c5dff9b006b0bfc9/src/linear_interpolation_module.F90#L764) / [Author test](https://github.com/jacobwilliams/finterp/blob/95aaceaf86f5d4d49328b783c5dff9b006b0bfc9/test/test.f90) |
| [Load bspline-tensor-surface](https://beliavsky.github.io/fortran-playground/fpm/?package=bspline-fortran&example=gams-bspline-tensor-surface) / [Source](../fpm_catalog/gams-drivers/bspline-tensor-surface.f90) | [Procedure](https://github.com/jacobwilliams/bspline-fortran/blob/047c724451aeee7f883c0d5acba3f7bd22a5de01/src/bspline_oo_module.f90#L1322) / [Author test](https://github.com/jacobwilliams/bspline-fortran/blob/047c724451aeee7f883c0d5acba3f7bd22a5de01/test/test_oo.f90) |

The programs adapt author API patterns and retain the package license notices, including the B-spline NIST/CMLIB notice. They appear in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

Both passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-surfaces-validation.json) records hashes, pins and saved output.

### finterp-bilinear-surface

```text
Surface case 1 evaluations=530
Node / bilinear formula / corner bound errors:   0.0000E+00   8.8818E-16   0.0000E+00
Analytic bilinear surface error:   1.7764E-15
Surface case 2 evaluations=530
Node / bilinear formula / corner bound errors:   0.0000E+00   1.7764E-15   0.0000E+00
PASS finterp-bilinear-surface
```

### bspline-tensor-surface

```text
Surface case 1 evaluations=530
Node / bilinear formula / corner bound errors:   1.7764E-15   1.7764E-15   1.7764E-15
Analytic bilinear surface error:   1.7764E-15
Surface case 2 evaluations=530
Node / bilinear formula / corner bound errors:   1.7764E-15   3.5527E-15   1.1102E-16
Bicubic value/partial evaluations=484
Scaled polynomial errors (value, dx, dy, dxdy):   6.0655E-16   5.3291E-15   2.5962E-15   3.7748E-15
PASS bspline-tensor-surface
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers finterp-bilinear-surface bspline-tensor-surface
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
