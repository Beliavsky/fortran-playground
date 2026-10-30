# Checked GAMS one-dimensional interpolation drivers

These consumer programs connect specific interpolation procedures to [E1a: polynomial splines (piecewise polynomials)](https://gams.nist.gov/cgi-bin/serve.cgi/Class/E1a). This GAMS class covers both piecewise linear and piecewise cubic methods; the procedure records and driver settings distinguish them. The examples do not exercise higher-dimensional APIs.

| Package | Shared-data method | Additional check |
| --- | --- | --- |
| finterp | `linear_interp_1d%evaluate`, piecewise linear | Agreement with an independent piecewise-linear reference |
| PCHIP | `dpchim` slopes and `dpchfe` values, shape-preserving cubic Hermite | Sampled monotonicity and local bounds; agreement with the linear method is not required |
| bspline-fortran | `bspline_1d`, order 2 (degree 1) | Piecewise-linear reference, then a separate order-4 cubic/derivative reproduction check |

## Shared data and checks

All drivers use the nonuniform grid `x=[0,0.25,0.5,1,2,3]`. Case 1 tabulates the affine function `f(x)=2*x-1`; case 2 uses steep monotone values `[0,0.01,0.02,0.9,0.95,1]`.

The programs check successful initialization/evaluation and finite outputs. They require interpolation at all six original nodes within `1e-12`. At 21 sample positions in each interval, including its endpoints, they check that the output stays between that interval's two data values and does not decrease, allowing `1e-12` rounding tolerance. This is a finite sampling check, rather than a proof of shape preservation for arbitrary data.

For affine data, every sampled value must agree with `2*x-1` within `1e-12`. The finterp and order-2 B-spline drivers also require agreement with the independently constructed piecewise-linear values within `1e-12`. PCHIP prints its difference from that reference without treating the difference as an error: the cubic interpolant generally takes different interior values. The drivers make no extrapolation requests. Each shared case performs 111 value evaluations: six original nodes plus five intervals with 21 samples each.

## Cubic B-spline reproduction

The B-spline driver separately interpolates `p(x)=1-2*x+0.5*x**2+x**3` with order 4, meaning cubic polynomial pieces. At 101 positions on `[0,3]`, it compares values with `p(x)` and first derivatives with `-2+x+3*x**2`, each within `1e-10`. This checks polynomial reproduction and the derivative evaluation API. It does not claim that general cubic B-spline interpolation preserves monotone shape.

## Sources and playground links

| Driver | Pinned procedure and author example |
| --- | --- |
| [Load finterp-shape-interpolation](https://beliavsky.github.io/fortran-playground/fpm/?package=finterp&example=gams-finterp-shape-interpolation) · [Source](../fpm_catalog/gams-drivers/finterp-shape-interpolation.f90) | [Procedure](https://github.com/jacobwilliams/finterp/blob/95aaceaf86f5d4d49328b783c5dff9b006b0bfc9/src/linear_interpolation_module.F90#L67) · [Author example/test](https://github.com/jacobwilliams/finterp/blob/95aaceaf86f5d4d49328b783c5dff9b006b0bfc9/test/test.f90) |
| [Load pchip-shape-interpolation](https://beliavsky.github.io/fortran-playground/fpm/?package=pchip&example=gams-pchip-shape-interpolation) · [Source](../fpm_catalog/gams-drivers/pchip-shape-interpolation.f90) | [Procedure](https://github.com/jacobwilliams/PCHIP/blob/8f5350565072622a2344dd0ec75193832b31eb10/src/pchip_module.f90#L2216) · [Author example/test](https://github.com/jacobwilliams/PCHIP/blob/8f5350565072622a2344dd0ec75193832b31eb10/test/pchip_test.f90) |
| [Load bspline-fortran-shape-interpolation](https://beliavsky.github.io/fortran-playground/fpm/?package=bspline-fortran&example=gams-bspline-fortran-shape-interpolation) · [Source](../fpm_catalog/gams-drivers/bspline-fortran-shape-interpolation.f90) | [Procedure](https://github.com/jacobwilliams/bspline-fortran/blob/047c724451aeee7f883c0d5acba3f7bd22a5de01/src/bspline_oo_module.f90#L63) · [Author example/test](https://github.com/jacobwilliams/bspline-fortran/blob/047c724451aeee7f883c0d5acba3f7bd22a5de01/test/test_oo.f90) |

The programs adapt author API patterns and retain the package license notices. They use shared deterministic data instead of the larger author test harnesses. The drivers appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only each main and executable were rebuilt. The [verification report](gams-interpolation-validation.json) records source hashes, pins and saved output. Zero printed error means agreement at working precision. These small examples establish checked usage, rather than general accuracy or speed rankings.

### finterp-shape-interpolation

```text
Case: affine data f(x)=2*x-1
  Interval midpoint       Interpolated value
        0.12500000000000       -0.75000000000000
        0.37500000000000       -0.25000000000000
        0.75000000000000        0.50000000000000
        1.50000000000000        2.00000000000000
        2.50000000000000        4.00000000000000
Maximum node error:   0.0000E+00
Maximum affine reproduction error:   8.8818E-16
Maximum difference from piecewise linear:   8.8818E-16
Maximum sampled local bound violation:   0.0000E+00
Maximum sampled decrease:   0.0000E+00
Evaluator calls: 111
Case: steep monotone data
  Interval midpoint       Interpolated value
        0.12500000000000        0.00500000000000
        0.37500000000000        0.01500000000000
        0.75000000000000        0.46000000000000
        1.50000000000000        0.92500000000000
        2.50000000000000        0.97500000000000
Maximum node error:   0.0000E+00
Maximum difference from piecewise linear:   2.2204E-16
Maximum sampled local bound violation:   0.0000E+00
Maximum sampled decrease:   0.0000E+00
Evaluator calls: 111
PASS finterp-shape-interpolation
```

### pchip-shape-interpolation

```text
Case: affine data f(x)=2*x-1
  Interval midpoint       Interpolated value
        0.12500000000000       -0.75000000000000
        0.37500000000000       -0.25000000000000
        0.75000000000000        0.50000000000000
        1.50000000000000        2.00000000000000
        2.50000000000000        4.00000000000000
Maximum node error:   0.0000E+00
Maximum affine reproduction error:   0.0000E+00
Maximum difference from piecewise linear:   4.4409E-16
Maximum sampled local bound violation:   0.0000E+00
Maximum sampled decrease:   0.0000E+00
Evaluator calls: 111
Case: steep monotone data
  Interval midpoint       Interpolated value
        0.12500000000000        0.00500000000000
        0.37500000000000        0.01404017857143
        0.75000000000000        0.45762951940035
        1.50000000000000        0.93233024691358
        2.50000000000000        0.97500000000000
Maximum node error:   0.0000E+00
Maximum difference from piecewise linear:   8.1693E-02
Maximum sampled local bound violation:   0.0000E+00
Maximum sampled decrease:   0.0000E+00
Evaluator calls: 111
PASS pchip-shape-interpolation
```

### bspline-fortran-shape-interpolation

```text
Case: affine data f(x)=2*x-1
  Interval midpoint       Interpolated value
        0.12500000000000       -0.75000000000000
        0.37500000000000       -0.25000000000000
        0.75000000000000        0.50000000000000
        1.50000000000000        2.00000000000000
        2.50000000000000        4.00000000000000
Maximum node error:   0.0000E+00
Maximum affine reproduction error:   8.8818E-16
Maximum difference from piecewise linear:   8.8818E-16
Maximum sampled local bound violation:   0.0000E+00
Maximum sampled decrease:   0.0000E+00
Evaluator calls: 111
Case: steep monotone data
  Interval midpoint       Interpolated value
        0.12500000000000        0.00500000000000
        0.37500000000000        0.01500000000000
        0.75000000000000        0.46000000000000
        1.50000000000000        0.92500000000000
        2.50000000000000        0.97500000000000
Maximum node error:   1.1102E-16
Maximum difference from piecewise linear:   2.2204E-16
Maximum sampled local bound violation:   1.1102E-16
Maximum sampled decrease:   0.0000E+00
Evaluator calls: 111
Cubic reproduction maximum error:   7.1054E-15
Cubic first derivative maximum error:   7.1054E-15
PASS bspline-fortran-shape-interpolation
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers finterp-shape-interpolation pchip-shape-interpolation bspline-fortran-shape-interpolation
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
