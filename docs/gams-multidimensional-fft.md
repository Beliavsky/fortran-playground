# Checked multidimensional complex Fourier transforms

These J1 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-multidimensional-fft-validation.json) retains pins, source hashes and complete output. GAMS categories are not exhausted.

## Independent Fourier references

Each shape uses eight deterministic complex fixtures: zero, a nonzero complex constant, an origin impulse, an off-origin complex impulse, two axis-dependent plane waves with different positive/negative frequencies, mixed signed dyadic data and a general nonperiodic sine/cosine mixture. Off-origin impulses and axis-dependent waves test phase and axis order, which an origin impulse alone cannot distinguish.

For every forward coefficient, independent nested scalar loops sum data(i,j,k)*exp(-2*pi*imaginary_unit*(a*i/nx+b*j/ny+c*k/nz)), with zero-based spatial and frequency indices. The exponential is formed from native sine/cosine values. The 2-D driver uses nz=1. The oracle calls neither FFT library nor another FFT implementation.

Each fixture then tests the inverse using the independently calculated coefficients divided by the total number of points N. The expected inverse is the original complex data. A separate third call applies the inverse to the saved library-forward output divided by N, checking a round trip as additional evidence. The independent inverse input prevents matching forward/inverse errors from being the only test.

All complex results must have finite real and imaginary components. Maximum forward coefficient error divided by 1+sum(abs(original)) must be <= 2e-12. Maximum independent-inverse and roundtrip errors divided by 1+max(abs(original)) must each be <= 2e-12. Parseval checks abs(sum(abs(forward)**2)-N*sum(abs(original)**2))/(1+N*sum(abs(original)**2)) <= 2e-12. Small zero inputs remain well-defined under these scalings.

## dtFFT 2-D CPU/FFTW plans (J1)

Shapes [4,6], [5,7] and [8,8] include unequal axes, prime lengths and a square grid. There are 24 fixtures and 72 execute calls: 984 forward coefficients, 984 independent inverse entries and 984 roundtrip entries, totaling 2,952 complex references. Three estimate-mode plans use the FFTW3 executor on exactly one MPI process. Every exposed MPI/dtFFT status is checked.

The physical input uses Fortran shape [nx,ny], but the Fourier output is a Y-aligned pencil with Fortran shape [ny,nx]. Local starts must be zero and local counts must match these layouts. The harness initially assumed equal physical/spectral shapes; source review and the rectangular-grid counts corrected that assumption. It explicitly transposes the output back to logical x/y order for comparison and transposes independent Fourier input into Y-pencil order for the inverse. Square-grid fixtures retain this same mapping.

Saved maximum normalized forward, independent-inverse, roundtrip and Parseval errors are 1.7516e-15, 5.0619e-15, 2.0015e-16 and 3.8611e-16. A fresh block-scoped plan object is used for each shape; all eight fixtures repeatedly execute that live plan before explicit buffer release and destruction. Recreating a destroyed plan object is not verified by this successful driver.

## 2DECOMP&FFT 3-D generic CPU transforms (J1)

Shapes [4,3,2], [5,4,3] and [6,5,4] exercise unequal axes and mixed factorization sizes with the built-in generic CPU backend. There are 24 fixtures and 72 transform calls: 1,632 forward coefficients, 1,632 independent inverse entries and 1,632 roundtrip entries, totaling 4,896 complex references.

Exactly one MPI process uses a 1-by-1 process grid, physical-X input and spectral-Z output. Both arrays have full logical x/y/z indexing in this one-process configuration, and their shapes are checked. Buffers, FFT state and the decomposition are finalized between shapes. Saved maximum normalized forward, independent-inverse, roundtrip and Parseval errors are 1.6165e-14, 2.0123e-14, 9.0006e-15 and 3.6096e-15.

## Preserved dtFFT plan-recreation failure

A probe that creates, executes and destroys one plan, then creates another shape in that same object, fails with an already-allocated-component runtime error. At the pinned source, destroy releases self%fft but leaves self%fft_mapping allocated; the next create tries to allocate it again. The [retained reproducer](gams-candidates/dtfft-plan-recreate/README.md) includes exact source, pin, normalized hash and full build/run result.

The checked driver keeps the same numeric comparisons and uses fresh plan objects rather than patching private library components or disabling runtime checks. Its block exit releases remaining allocatable components. Repeated execution is verified; general cleanup correctness, destroyed-object recreation and long-running memory behavior are not. No comparison was relaxed.

## Scope, native diagnostics and licenses

Both successful results retain a UCX diagnostic about scandir(/sys/class/net) in stdout. MPI initialization/finalization statuses and the numerical checks nevertheless passed. The complete diagnostic is preserved in the verification report; these runs do not establish distributed communication behavior.

These are one-process, double-precision complex transforms. Multiple MPI processes, distributed scaling, real transforms, GPU execution, other executors, large-size accuracy and performance remain unverified. Pinned implementations and author examples were reviewed without copying their bodies. The independent drivers and preserved probe have their own MIT notice; dtFFT retains GPL-3.0-or-later and 2DECOMP&FFT BSD-3-Clause terms. Loading a driver does not submit a job.

### dtfft-2d-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=dtfft&example=gams-dtfft-2d-reference) / [Driver source](../fpm_catalog/gams-drivers/dtfft-2d-reference.f90) / [Pinned procedure](https://github.com/ShatrovOA/dtFFT/blob/bbfd6746be7482bd8366ccb09a73b72882573984/src/dtfft_plan.F90#L1) / [Author test](https://github.com/ShatrovOA/dtFFT/blob/bbfd6746be7482bd8366ccb09a73b72882573984/tests/fortran/test_c2c_2d_f.F90)

```text
[1793488440.551314] [modal:45   :0]       tcp_iface.c:912  UCX  ERROR scandir(/sys/class/net) failed: No such file or directory
Complex data fixtures: 24
Forward/inverse/roundtrip entries: 2952
Maximum normalized forward error:   1.7516E-15
Maximum normalized independent inverse error:   5.0619E-15
Maximum normalized roundtrip error:   2.0015E-16
Maximum normalized Parseval error:   3.8611E-16
PASS dtfft-2d-reference
```

### decomp-3d-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=2decomp-fft&example=gams-decomp-3d-reference) / [Driver source](../fpm_catalog/gams-drivers/decomp-3d-reference.f90) / [Pinned procedure](https://github.com/2decomp-fft/2decomp-fft/blob/4cb38be477b9457cfa5f5624c8fe09387968b190/src/fft_generic.f90#L1) / [Author test](https://github.com/2decomp-fft/2decomp-fft/blob/4cb38be477b9457cfa5f5624c8fe09387968b190/examples/fft_physical_x/fft_c2c_x.f90)

```text
[1793488376.758771] [modal:39   :0]       tcp_iface.c:912  UCX  ERROR scandir(/sys/class/net) failed: No such file or directory
Complex data fixtures: 24
Forward/inverse/roundtrip entries: 4896
Maximum normalized forward error:   1.6165E-14
Maximum normalized independent inverse error:   2.0123E-14
Maximum normalized roundtrip error:   9.0006E-15
Maximum normalized Parseval error:   3.6096E-15
PASS decomp-3d-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers dtfft-2d-reference decomp-3d-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
