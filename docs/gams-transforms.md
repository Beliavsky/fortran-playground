# Checked GAMS transform drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [J1a2](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a2) | One-dimensional complex Fourier transforms | FFTPACK `fft, ifft`; KISS FFT `fft%perform` |
| [J1a3](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J1a3) | One-dimensional sine and cosine transforms | FFTPACK `dct(type=2), idct(type=2)` |

These are the deepest categories in the recorded GAMS taxonomy for the demonstrated complex and cosine transforms. They do not exhaust integral transforms: multidimensional transforms, convolution, Laplace and Hilbert transforms are separate opportunities.

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

The programs adapt author API patterns and retain license notices. They appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only each main and executable were rebuilt. The [verification report](gams-transforms-validation.json) records hashes, source pins and saved output.

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

## Maintenance

```text
python xverify_gams_drivers.py --drivers fftpack-complex-transform kissfft-f-complex-transform fftpack-cosine-transform
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
