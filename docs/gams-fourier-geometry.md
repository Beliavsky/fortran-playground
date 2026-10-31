# Checked GAMS real Fourier and geodesic drivers

These J1a1 and P examples passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only their mains and executables were compiled. The [verification report](gams-fourier-geometry-validation.json) records source hashes, pinned revisions and actual output. GAMS categories are not exhausted.

## Real-input Fourier transforms: spectrum (J1a1)

The driver checks `rfft` on four deterministic signals at each length `3,4,5,6,7,8,11,12,15,16`: a shifted unit impulse, the constant 2, a mixed dyadic sequence, and `1+2*cos(theta)-0.5*sin(theta)`. Two further calls check explicit zero padding from five to eight samples and truncation from five to three, for 42 forward transforms.

Every complex coefficient in the returned half spectrum is compared with independent scalar cosine/sine sums for the unnormalized forward DFT `sum_j x_j*exp(-2*pi*i*k*j/n)`. The maximum complex coefficient error divided by `max(1,sum(abs(x)))` must be at most `1e-11`. The half-spectrum length must equal `floor(n/2)+1`; real and imaginary parts must be finite. DC, and Nyquist for even n, must have imaginary part at most `1e-11`. Parseval energy weights the DC and even-n Nyquist coefficients once and the other positive-frequency coefficients twice; its scaled error must also be at most `1e-11`.

The author FFT tests were reviewed for the public API and conventions. This independently written driver verifies forward transforms only. The pinned `irfft` implementation infers the full length from half-spectrum length parity, which cannot distinguish both original parities. Its optional length parameter adjusts the input half-spectrum rather than explicitly naming the original real length. Inverse reconstruction needs separate review and is not certified by this driver. Windows, STFT and performance are also outside this example.

## Direct and inverse geodesics: geodesic-fortran (P)

Six spherical routes cover northern and southern latitudes, a dateline crossing, high latitudes and an equatorial quarter circle. Independent haversine distances and analytic initial bearings supply references. Three WGS84 equatorial arcs use the exact reference `a*abs(delta_longitude)` in radians, including eastward wrapping and westward travel. Three WGS84 meridian paths span latitudes `[-40,20]`, `[30,70]` and `[80,85]` degrees. They use independent composite Simpson integration of the meridional radius of curvature `a*(1-e2)/(1-e2*sin(latitude)^2)^(3/2)`. Results with 2048 and 4096 panels must agree within `1e-7` metres; the finer integral supplies the distance reference. Refinement agreement is an empirical check, not a formal quadrature error bound.

The sphere radius and WGS84 semimajor axis are 6378137 metres; ellipsoidal flattening is `1/298.257223563`. Across all 12 cases inverse distances must agree within `1e-6` metres and initial bearings within `1e-9` degrees. Direct calculations use independently computed distances and bearings, not inverse outputs; endpoints must agree within `1e-9` degrees. Longitude and bearing differences are compared modulo 360 degrees. Used outputs must be finite. General oblique ellipsoidal paths, exact antipodal/coincident degeneracies, reduced lengths, geodesic scales and areas are not verified. Only the requested distance, bearing and endpoint outputs are inspected.

## Checked links and output

The source files are independent API consumers with their own MIT notice; upstream package licenses remain separate. Loading these links selects checked source without submitting a job.

### spectrum-real-dft-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=spectrum&example=gams-spectrum-real-dft-reference) / [Driver source](../fpm_catalog/gams-drivers/spectrum-real-dft-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/spectrum/blob/5af0d5a85eccf971aa6e0fc72b1c7439c3cef536/src/spectrum_fft.f90#L48)

[Pinned author example/test](https://github.com/jchristopherson/spectrum/blob/5af0d5a85eccf971aa6e0fc72b1c7439c3cef536/test/spectrum_fft_tests.f90)

```text
Four signals checked at length 3 (direct DFT and Parseval)
Four signals checked at length 4 (direct DFT and Parseval)
Four signals checked at length 5 (direct DFT and Parseval)
Four signals checked at length 6 (direct DFT and Parseval)
Four signals checked at length 7 (direct DFT and Parseval)
Four signals checked at length 8 (direct DFT and Parseval)
Four signals checked at length 11 (direct DFT and Parseval)
Four signals checked at length 12 (direct DFT and Parseval)
Four signals checked at length 15 (direct DFT and Parseval)
Four signals checked at length 16 (direct DFT and Parseval)
42 forward real transforms checked, including explicit zero padding and truncation.
PASS spectrum-real-dft-reference
```

### geodesic-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=geodesic-fortran&example=gams-geodesic-reference) / [Driver source](../fpm_catalog/gams-drivers/geodesic-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/geodesic-fortran/blob/b16eaf6622baabee7dfb75b99b78e42eaa878440/src/geodesic_module.F90#L556)

[Pinned author example/test](https://github.com/jacobwilliams/geodesic-fortran/blob/b16eaf6622baabee7dfb75b99b78e42eaa878440/test/direct_inverse_test.f90)

```text
Distance (m):     6890979.843127 reference error:   0.0E+00
Distance (m):     5793495.553489 reference error:   0.0E+00
Distance (m):     2772664.682562 reference error:   0.0E+00
Distance (m):    11131949.079327 reference error:   1.9E-09
Distance (m):    10018754.171395 reference error:   0.0E+00
Distance (m):     8199555.438446 reference error:   2.8E-09
Distance (m):    10018754.171395 reference error:   0.0E+00
Distance (m):     2226389.815865 reference error:   0.0E+00
Distance (m):     6679169.447596 reference error:   0.0E+00
Distance (m):     6641895.284522 reference error:   1.9E-09
Distance (m):     4448867.329830 reference error:   5.6E-09
Distance (m):      558370.268729 reference error:   3.5E-10
PASS geodesic-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers spectrum-real-dft-reference geodesic-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. See also the [sparse conversion review](gams-linear-algebra.md#sparse-storage-conversion) and [remaining coverage](gams-coverage.md).
