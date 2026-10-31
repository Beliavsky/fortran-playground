# Checked spatial search, scattered interpolation and nonuniform Fourier drivers

These N5, E2 and J1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing precompiled packages. Only their mains and executables were compiled. The [verification report](gams-spatial-nufft-validation.json) records source hashes, package pins and actual output. GAMS categories are not exhausted.

## Exhaustive neighbor references: kdtree2 (N5)

The 48 three-dimensional points have coordinates `[mod(7*i,53),mod(11*i,59),mod(13*i,61)]/64`. Queries are `[13,29,41]/64`, the origin and point 17 itself. Both storage rearrangement modes are tested with sorted results. Each query requests its 1, 5 and all 48 nearest neighbors, and squared radii 0, 0.125 and 4: 36 search calls in total.

Independent real64 scalar sums evaluate all squared distances from the actual input coordinates. An independent insertion sort supplies the nearest-distance references; tied indexes may appear in either order. Result indexes must be valid and unique, their distances finite and within `1e-6` of their references, and nearest distances must match the sorted prefix. Radius counts, every index, squared distance and the complete returned membership set are checked against exhaustive search. Zero radius checks exact self-membership; radius 4 includes all points in these fixtures.

The archived single-precision setting is retained. These dyadic fixtures and real64 references make its precision explicit. The tree is destroyed after each storage mode. Global library search state is not thread-safe; concurrent searches, arbitrary dimensions, insufficient result capacity and large-data performance are not verified. This N5 driver does not separately verify the package's broader P mapping.

## Three-dimensional scattered interpolation: DelaunaySparse (E2)

Ten irregular points comprise four bounding tetrahedron vertices and six interior convex combinations. Six further convex combinations supply strictly interior query points. Three fields are supplied together: constant 1, affine `2*x-3*y+0.5*z+1`, and squared radius `x^2+y^2+z^2`. The serial routine must return status zero, finite weights and finite field values.

Each returned tetrahedron must have four distinct valid vertex indexes and absolute edge determinant at least `1e-10`. Weights must be nonnegative within tolerance and sum to one. Scalar weighted sums of preserved original vertices must reconstruct the original query, and weighted vertex fields must match all three interpolated channels, within `1e-10` absolute error. The constant and affine fields must also agree with their direct analytic values at the query. The squared-radius channel is checked as piecewise-linear interpolation, not exact nonlinear-function recovery.

The routine rescales coordinates in place, so references use saved inputs. This uses the existing MIT-licensed version-1 package and serial entry point. It does not verify the empty-circumsphere property, convex-hull extrapolation, all degenerate configurations or the parallel variant.

## Nonuniform Fourier sums: NUFFT1D (J1)

Eighty nodes `0.95*(pi*sin(0.37*j)+0.01*cos(0.11*j))` lie strictly inside `[-pi,pi]`. Mode counts 15, 16, 31 and 32 exercise odd/even ranges `-ms/2:(ms-1)/2`. Three strength patterns are a single complex source, all ones, and mixed dyadic complex values. Both exponent signs give 24 calls and 564 checked complex coefficients.

The type-1 reference is `F_k=sum_j c_j*exp(sign*i*k*x_j)/nj`, evaluated independently by scalar real and imaginary trigonometric sums. All statuses must be zero and all outputs finite. The maximum complex coefficient error divided by `max(1,sum(abs(c))/nj)` must be at most `1e-8`, with requested library accuracy `1e-10`. The zero mode is separately compared with `sum(c)/nj`. These tolerances check usage and normalization, not a rigorous error guarantee for arbitrary signals.

The cached package retains its existing checksum-guarded legacy FFT dummy-array declaration fixes and package-specific `-fallow-argument-mismatch` option. No transform formulas, library patches or build settings were changed for this driver. Types 2/3, the static F77 entry point, other dimensions and performance are not verified. J1 remains the broader recorded classification for this nonuniform configuration.

## Checked links and actual output

These independent API consumers have their own MIT notice. Author examples were reviewed for usage; upstream package licenses remain separate. Loading a link selects source without submitting a job.

### kdtree-neighbor-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=kdtree2&example=gams-kdtree-neighbor-reference) / [Driver source](../fpm_catalog/gams-drivers/kdtree-neighbor-reference.f90) / [Pinned procedure](https://github.com/jmhodges/kdtree2/blob/dc757acec3162948cb228c2e0457d10134ec1edc/src-f90/kdtree2.f90#L1) / [Author example/test](https://github.com/jmhodges/kdtree2/blob/dc757acec3162948cb228c2e0457d10134ec1edc/src-f90/kdtree2_test.f90)

```text
Rearrange=F, query 1: nearest and complete radius sets checked.
Rearrange=F, query 2: nearest and complete radius sets checked.
Rearrange=F, query 3: nearest and complete radius sets checked.
Rearrange=T, query 1: nearest and complete radius sets checked.
Rearrange=T, query 2: nearest and complete radius sets checked.
Rearrange=T, query 3: nearest and complete radius sets checked.
36 searches checked against exhaustive real64 distances; upstream tree uses single precision.
PASS kdtree-neighbor-reference
```

### delaunay-affine-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=delaunaysparse&example=gams-delaunay-affine-reference) / [Driver source](../fpm_catalog/gams-drivers/delaunay-affine-reference.f90) / [Pinned procedure](https://github.com/vtopt/DelaunaySparse/blob/f3ffef04e24281aa42a0e5ec81f5c68f6bb5fb01/src/delsparse.f90#L1) / [Author example/test](https://github.com/vtopt/DelaunaySparse/blob/f3ffef04e24281aa42a0e5ec81f5c68f6bb5fb01/src/test_install.f90)

```text
Query 1: affine=  1.013889 piecewise linear squared radius=  1.036414
Query 2: affine=  0.865385 piecewise linear squared radius=  0.917917
Query 3: affine=  0.786765 piecewise linear squared radius=  0.932968
Query 4: affine=  0.738095 piecewise linear squared radius=  0.942286
Query 5: affine=  0.705000 piecewise linear squared radius=  0.948621
Query 6: affine=  0.681034 piecewise linear squared radius=  0.953209
Six 3D queries checked: affine reproduction, simplex geometry, and three-channel weighted interpolation.
PASS delaunay-affine-reference
```

### nufft1d-sum-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nufft1d&example=gams-nufft1d-sum-reference) / [Driver source](../fpm_catalog/gams-drivers/nufft1d-sum-reference.f90) / [Pinned procedure](https://github.com/zgimbutas/nufft1d/blob/42a04333f882f474b0674936cae049899784f56e/nufft1df90.f#L1) / [Author example/test](https://github.com/zgimbutas/nufft1d/blob/42a04333f882f474b0674936cae049899784f56e/nufft1d_demof90.f)

```text
Modes=15 signal=1 sign=-1 scaled error=  5.15E-13
Modes=15 signal=1 sign= 1 scaled error=  5.15E-13
Modes=15 signal=2 sign=-1 scaled error=  1.26E-12
Modes=15 signal=2 sign= 1 scaled error=  1.26E-12
Modes=15 signal=3 sign=-1 scaled error=  2.23E-12
Modes=15 signal=3 sign= 1 scaled error=  2.23E-12
Modes=16 signal=1 sign=-1 scaled error=  2.62E-12
Modes=16 signal=1 sign= 1 scaled error=  2.62E-12
Modes=16 signal=2 sign=-1 scaled error=  2.92E-11
Modes=16 signal=2 sign= 1 scaled error=  2.92E-11
Modes=16 signal=3 sign=-1 scaled error=  7.13E-12
Modes=16 signal=3 sign= 1 scaled error=  1.07E-11
Modes=31 signal=1 sign=-1 scaled error=  1.23E-12
Modes=31 signal=1 sign= 1 scaled error=  1.23E-12
Modes=31 signal=2 sign=-1 scaled error=  1.11E-11
Modes=31 signal=2 sign= 1 scaled error=  1.11E-11
Modes=31 signal=3 sign=-1 scaled error=  9.18E-12
Modes=31 signal=3 sign= 1 scaled error=  9.18E-12
Modes=32 signal=1 sign=-1 scaled error=  2.62E-12
Modes=32 signal=1 sign= 1 scaled error=  2.62E-12
Modes=32 signal=2 sign=-1 scaled error=  2.33E-11
Modes=32 signal=2 sign= 1 scaled error=  2.33E-11
Modes=32 signal=3 sign=-1 scaled error=  5.30E-12
Modes=32 signal=3 sign= 1 scaled error=  6.34E-12
24 type-1 transforms checked against scalar Fourier sums, including odd/even mode counts and both signs.
PASS nufft1d-sum-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers kdtree-neighbor-reference delaunay-affine-reference nufft1d-sum-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
