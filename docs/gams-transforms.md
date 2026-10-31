# Checked GAMS transform drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [J1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1) | One-/two-dimensional nonuniform type-1 Fourier transforms | NUFFT `nufft1d1f90`; NUFFT2D `nufft2d1f90` |
| [J1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a1) | One-dimensional real-input forward Fourier transforms | spectrum `rfft` |
| [J1a2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a2) | One-dimensional complex Fourier transforms | FFTPACK `fft, ifft`; KISS FFT `fft%perform` |
| [J1a3](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a3) | One-dimensional sine and cosine transforms | FFTPACK `dct(type=2), idct(type=2)` |

The real, complex and cosine transforms use the deepest recorded categories for those configurations. The nonuniform examples retain broader J1. They do not exhaust integral transforms: additional multidimensional configurations, transform types, convolution, Laplace and Hilbert transforms are separate opportunities.

## Nonuniform Fourier sums

The NUFFT driver checks 24 type-1 transforms of 80 nonuniform sources into 15, 16, 31 and 32 modes, with three deterministic strength patterns and both exponent signs. Every coefficient is checked against scalar trigonometric sums with the documented `1/nj` normalization. See the [spatial and nonuniform-transform review](gams-spatial-nufft.md) for tolerances, the zero-mode check and the retained package build patches.

The two-dimensional NUFFT2D driver checks 144 transforms and all 22,416 coefficients against direct sums, with both signs, two tolerances and even/odd grids. See the [quadrature-moment and 2D-transform review](gams-moments-nufft2d.md) for its input patterns, normalization, acceptance checks and limits.

## Real-input FFT checks

The spectrum driver checks 42 forward transforms against scalar trigonometric sums and Parseval energy, including ten odd/even lengths, four deterministic signals per length and explicit zero padding/truncation. Its scaled tolerance is `1e-11`. Inverse transforms are not verified by this driver; see the [reference details and length-convention limitation](gams-fourier-geometry.md).

## Complex FFT checks

The shared input is `x(j)=(j+1)/8 + i*(-1)**j/4`, for zero-based `j`, at lengths 7 and 8. Its components are exactly representable in both single and double precision. Each driver independently sums the negative-exponent DFT in real64 and compares every complex frequency bin. It also checks finite values, inverse recovery after dividing by `N`, and Parseval's identity `sum(abs(X)**2)/N = sum(abs(x)**2)`.

FFTPACK uses its double-precision `rk` kind and limits forward, inverse and relative energy errors to `1e-11`. The pinned KISS FFT binding uses C `float`: forward error must be at most `1e-5`, inverse error at most `1e-6` and relative energy error at most `1e-6`. The precision difference is explicit, rather than interpreting it as an algorithm ranking. KISS forward and inverse plans are each initialized once per length and finalized on block exit.

## Cosine transform checks

The DCT-II driver uses the real input `(j+1)/8` at lengths 7 and 8. In this FFTPACK API, the forward convention is `X(k)=4*sum_j x(j)*cos(pi*(j+1/2)*k/N)`. The inverse is unnormalized: divide `idct(dct(x,type=2),type=2)` by `4*N`. The driver independently evaluates the cosine sum and requires both forward and recovered-input errors at most `1e-11`, with finite outputs. Other libraries may use different normalization conventions.

A round trip alone could hide matching sign or scaling mistakes; independent forward references check the documented convention. These short deterministic cases do not establish accuracy or performance for all transform sizes.

## Sources and playground links

| Driver | Class | Pinned procedure and author example |
| --- | --- | --- |
| [Load fftpack-complex-transform](https://beliavsky.github.io/fortran-playground/fpm/?package=fftpack&example=gams-fftpack-complex-transform) · [Source](../fpm_catalog/gams-drivers/fftpack-complex-transform.f90) | J1a2 | [Procedure](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/src/fftpack.f90#L222) · [Author example/test](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/test/test_fftpack_fft.f90) |
| [Load kissfft-f-complex-transform](https://beliavsky.github.io/fortran-playground/fpm/?package=kissfft-f&example=gams-kissfft-f-complex-transform) · [Source](../fpm_catalog/gams-drivers/kissfft-f-complex-transform.f90) | J1a2 | [Procedure](https://github.com/zoziha/kissfft-f/blob/b89c5e1d0aff9993db79200fc94a467948ff3923/src/kissfft-f.f90#L11) · [Author example/test](https://github.com/zoziha/kissfft-f/blob/b89c5e1d0aff9993db79200fc94a467948ff3923/example/fft.f90) |
| [Load fftpack-cosine-transform](https://beliavsky.github.io/fortran-playground/fpm/?package=fftpack&example=gams-fftpack-cosine-transform) · [Source](../fpm_catalog/gams-drivers/fftpack-cosine-transform.f90) | J1a3 | [Procedure](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/src/fftpack_dct.f90#L6) · [Author example/test](https://github.com/fortran-lang/fftpack/blob/0fffe7c05a918363a7cc12ae138a695afd115f36/test/test_fftpack_dct.f90) |
| [Load spectrum-real-dft-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=spectrum&example=gams-spectrum-real-dft-reference) · [Source](../fpm_catalog/gams-drivers/spectrum-real-dft-reference.f90) | J1a1 | [Procedure](https://github.com/jchristopherson/spectrum/blob/5af0d5a85eccf971aa6e0fc72b1c7439c3cef536/src/spectrum_fft.f90#L48) · [Author example/test](https://github.com/jchristopherson/spectrum/blob/5af0d5a85eccf971aa6e0fc72b1c7439c3cef536/test/spectrum_fft_tests.f90) |
| [Load nufft1d-sum-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=nufft1d&example=gams-nufft1d-sum-reference) · [Source](../fpm_catalog/gams-drivers/nufft1d-sum-reference.f90) | J1 | [Procedure](https://github.com/zgimbutas/nufft1d/blob/42a04333f882f474b0674936cae049899784f56e/nufft1df90.f#L1) · [Author example/test](https://github.com/zgimbutas/nufft1d/blob/42a04333f882f474b0674936cae049899784f56e/nufft1d_demof90.f) |
| [Load nufft2d-direct-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=nufft2d&example=gams-nufft2d-direct-reference) · [Source](../fpm_catalog/gams-drivers/nufft2d-direct-reference.f90) | J1 | [Procedure](https://github.com/zgimbutas/nufft2d/blob/8353c5fb20cd0a8fe6821fae18355e303ed23ed3/nufft2df90.f#L1) · [Author example/test](https://github.com/zgimbutas/nufft2d/blob/8353c5fb20cd0a8fe6821fae18355e303ed23ed3/nufft2d_demof90.f) |

The programs record API provenance and license notices; the independently written spectrum and NUFFT drivers have their own MIT notices. They appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All 6 passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only each main and executable were rebuilt. The verification reports record hashes, source pins and saved output: [gams-fourier-geometry-validation.json](gams-fourier-geometry-validation.json), [gams-moments-nufft2d-validation.json](gams-moments-nufft2d-validation.json), [gams-spatial-nufft-validation.json](gams-spatial-nufft-validation.json), [gams-transforms-validation.json](gams-transforms-validation.json).

### fftpack-complex-transform

```text
Transform length: 7
Maximum forward error against direct sum:   5.0241E-15
Maximum normalized inverse error:   1.2413E-16
Relative Parseval energy error:   1.6918E-16
Transform length: 8
Maximum forward error against direct sum:   3.8858E-15
Maximum normalized inverse error:   5.5511E-17
Relative Parseval energy error:   0.0000E+00
PASS fftpack-complex-transform
```

### kissfft-f-complex-transform

```text
Transform length: 7
Maximum forward error against direct sum:   1.6075E-07
Maximum normalized inverse error:   7.6160E-08
Relative Parseval energy error:   1.7055E-08
Transform length: 8
Maximum forward error against direct sum:   4.7503E-08
Maximum normalized inverse error:   0.0000E+00
Relative Parseval energy error:   7.4352E-09
PASS kissfft-f-complex-transform
```

### fftpack-cosine-transform

```text
Transform length: 7
Maximum forward error against direct sum:   4.3854E-15
Maximum normalized inverse error:   2.2204E-16
Transform length: 8
Maximum forward error against direct sum:   2.3537E-14
Maximum normalized inverse error:   2.7756E-17
PASS fftpack-cosine-transform
```

### spectrum-real-dft-reference

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

### nufft1d-sum-reference

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

### nufft2d-direct-reference

```text
Two-dimensional type-1 NUFFT calls: 144; direct coefficient comparisons: 22416
Even/odd grids, both signs, two tolerances; scattered, coincident, near-boundary and zero-strength data.
Maximum normalized direct-sum error:   1.3607E-08
PASS nufft2d-direct-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fftpack-complex-transform kissfft-f-complex-transform fftpack-cosine-transform spectrum-real-dft-reference nufft1d-sum-reference nufft2d-direct-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
