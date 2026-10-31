# Checked physical quantities and zonal spherical harmonics

These A and J drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-quantities-spherical-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Typed quantity arithmetic: quaff (A)

Six signed/zero length values [-8,-0.125,0,0.25,3,1000] test meters, centimeters, millimeters, feet and inches. Independent scalar references use 100 cm/m, 1000 mm/m, 0.3048 m/ft and 0.0254 m/in, including the 12 inches/foot relationship. Both construction from non-SI units and conversion from meters are checked.

Addition, subtraction, unary negation, scalar multiplication/division, division of two lengths, absolute value and sums of quantity arrays are compared with direct scalar formulas. For positive durations [0.25,1,10] seconds, typed length/time produces a speed checked in m/s and ft/s; multiplying the speed by time must recover the original signed length. Seconds/minutes/hours conversions use independent factors 60 and 3600. There are 180 numeric references.

All results must be finite and have error divided by max(1,abs(reference)) at most 2e-12. These are numerical checks of valid typed expressions. The driver does not attempt invalid dimensional expressions, test their compiler diagnostics, or verify all quantity types. Parsing, string formatting, overflow and extreme conversion scales are outside this example. The author length tests were reviewed for usage; these fixtures are independently specified. The broad A assignment describes arithmetic with physical quantities rather than a narrower numerical algorithm.

## Independent zonal analysis and synthesis: Spherepack (J)

Gaussian grids have latitude/longitude sizes [9,16], [13,24] and [17,32]. For each grid, the five zonal fields P0..P4 and a mixture with amplitudes [1,-2,0.5,0.25,-0.75] give six fixtures, or 18 in total. For z equal to the radial unit-vector z coordinate, the independent Legendre formulas are `1`, `z`, `(3*z*z-1)/2`, `(5*z**3-3*z)/2` and `(35*z**4-30*z*z+3)/8`.

Spherepack uses normalized associated Legendre functions and a half-weight for m=0. Thus a zonal field with amplitude c_l has real coefficient `a(1,l+1)=2*sqrt(2/(2*l+1))*c_l`. Every tested valid coefficient must agree with this reference: all other real coefficients and all imaginary coefficients vanish. The checks exclude the longitude Nyquist order and invalid triangular storage. Absolute coefficient error must be at most 2e-11.

Synthesis is first checked after analysis, then the analyzed coefficients are erased and replaced with the independent exact amplitudes. This second synthesis must reproduce the polynomial field independently of the analysis output, so a compensating normalization error cannot pass solely through a round trip. All synthesized fields must be finite with absolute error at most 2e-11. There are 18 analyses and 36 syntheses, exercising repeated workspace use and three grid sizes.

The author spherical Helmholtz example was reviewed for object construction and coordinates; this is an independently written transform driver, not a reuse of that PDE example. Nonzero nonzonal modes, vector transforms, Nyquist behavior, PDE/Helmholtz routines, unresolved-grid aliasing and performance are not verified. The separate I2 solver mapping remains source-supported by this dedicated-driver evidence.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### quaff-quantity-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=quaff&example=gams-quaff-quantity-reference) / [Driver source](../fpm_catalog/gams-drivers/quaff-quantity-reference.f90) / [Pinned procedure](https://github.com/everythingfunctional/quaff/blob/f26da3d854045b79102d27bdb4e9f9b072444272/src/quaff/length_m.f90#L60) / [Author example/test](https://github.com/everythingfunctional/quaff/blob/f26da3d854045b79102d27bdb4e9f9b072444272/test/length_test.f90)

```text
180 numeric references: signed/zero lengths, five units, time conversions and typed arithmetic.
Length/time speed and speed*time length checked against scalar SI formulas.
Maximum error / max(1,abs(reference)):   1.8481E-16
PASS quaff-quantity-reference
```

### spherepack-zonal-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=spherepack&example=gams-spherepack-zonal-reference) / [Driver source](../fpm_catalog/gams-drivers/spherepack-zonal-reference.f90) / [Pinned procedure](https://github.com/jlokimlin/spherepack/blob/e80da29462c5987162a0884baaab7434d0215467/src/type_GaussianSphere.f90#L183) / [Author example/test](https://github.com/jlokimlin/spherepack/blob/e80da29462c5987162a0884baaab7434d0215467/examples/helmsph.f90)

```text
18 zonal harmonic fixtures: degrees 0..4 and a mixed field on three Gaussian grids.
Maximum normalized-basis coefficient error:   1.7487E-15
Maximum analysis/synthesis round-trip error:   2.6645E-15
Maximum independent coefficient-injection synthesis error:   1.1102E-15
PASS spherepack-zonal-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers quaff-quantity-reference spherepack-zonal-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
