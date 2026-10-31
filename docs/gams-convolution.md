# Checked GAMS discrete-convolution drivers

Both examples demonstrate [J2: Convolutions](https://gams.nist.gov/cgi-bin/serve.cgi/Class/J2). They check the results with a direct summation independent of the library implementation. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Signals, kernels and reference

The signal length is 37. Case 1 is an impulse at one-based sample 10. Case 2 is `sin(0.2*i)+(-1)**i*0.1*i`, for `i=1,...,37`. Both drivers test kernel lengths `[1,2,3,4,5,8,16,17]`. For length 1 the kernel is `[1]`; otherwise `h(j)=(-1)**j/(j+1)`. The asymmetric odd and even kernels check orientation and alignment, which a symmetric smoothing kernel could hide. Reusing the filter object also checks kernel replacement across lengths.

A separate real64 nested loop constructs full linear convolution, with zero extension outside the inputs:

```text
full(i+j-1) += x(i)*h(j), for i=1,...,N and j=1,...,M
size(full) = N+M-1
```

All outputs must have the expected lengths and finite values. The scaled output error is `max(abs(computed-reference))/max(1,max(abs(reference)))`.

## spectrum: full and central results

The spectrum driver uses real64 inputs and checks the default full result against the direct sum. Swapping signal and kernel must give the same full convolution. It separately checks the sum identity `sum(full)=sum(x)*sum(h)`, using scaled error at most `1e-11`.

For `SPCTRM_CENTRAL_CONVOLUTION`, the pinned implementation returns the length of the longer input. In these cases the length is 37. The selected segment starts at one-based index `floor(M/2)+1` of the direct full result, where M is the shorter input length. This states the even-kernel alignment explicitly. Both input orders are tested for the central result too. Central results include boundary effects from zero extension; they are not the same as a valid-overlap convolution.

All four output comparisons per signal/kernel case use tolerance `1e-11`. There are 16 signal/kernel combinations and 64 library calls. The driver does not require plotting or the author example plotting dependencies.

## fastconv: valid overlap and native precision

The default `conv1d_t` is the padded optimized implementation. The driver calls `set_kernel` and explicitly sets `preserve_shape=.false.`. The output length is `N-M+1`, and the reference is the one-based slice `full(M:N)`. The library reverses the supplied kernel internally; the caller supplies the mathematical kernel in its natural order.

At this pin fastconv uses real32. The driver rounds the signal and kernel to real32 before calling it, then converts those actual arguments to real64 for independent accumulation. It compares all 16 outputs with scaled tolerance `2e-6`. This avoids treating input rounding as a library calculation error and does not imply real64 output precision.

### Known shape-preserving boundary limitation

The shape-preserving mode is excluded for a source-confirmed reason. At the reviewed pin, `apply` allocates the output without initializing it; the padded and reference convolution paths assign only the valid interior slice when `preserve_shape=.true.`. Boundary entries remain undefined. The author README example also prints an uninitialized boundary value. The checked driver uses valid overlap and does not read those entries.

Sources: [allocation and apply](https://github.com/gronki/fastconv/blob/3aaa2432a291df07a10fc5dade0dcd66d7a06dd0/src/conv1d/conv1d.f90), [padded path](https://github.com/gronki/fastconv/blob/3aaa2432a291df07a10fc5dade0dcd66d7a06dd0/src/conv1d/pad.F90), [reference path](https://github.com/gronki/fastconv/blob/3aaa2432a291df07a10fc5dade0dcd66d7a06dd0/src/conv1d/ref.F90), [author README](https://github.com/gronki/fastconv/blob/3aaa2432a291df07a10fc5dade0dcd66d7a06dd0/README.md). These links identify the pinned implementation; no claim is made about later revisions.

## Scope and sources

The examples cover selected real-valued 1D operations, not empty inputs, kernels longer than the fastconv signal, multidimensional convolution, deconvolution, arbitrary padding policies or performance benchmarks. The precision and output conventions differ, so these are not a direct speed or accuracy ranking.

| Driver | Pinned procedure and author usage |
| --- | --- |
| [Load spectrum-convolution-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=spectrum&example=gams-spectrum-convolution-reference) / [Source](../fpm_catalog/gams-drivers/spectrum-convolution-reference.f90) | [Procedure](https://github.com/jchristopherson/spectrum/blob/5af0d5a85eccf971aa6e0fc72b1c7439c3cef536/src/spectrum_convolve.f90#L41) / [Author usage](https://github.com/jchristopherson/spectrum/blob/5af0d5a85eccf971aa6e0fc72b1c7439c3cef536/examples/gaussian_filter_example.f90) |
| [Load fastconv-convolution-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=fastconv&example=gams-fastconv-convolution-reference) / [Source](../fpm_catalog/gams-drivers/fastconv-convolution-reference.f90) | [Procedure](https://github.com/gronki/fastconv/blob/3aaa2432a291df07a10fc5dade0dcd66d7a06dd0/src/conv1d/conv1d.f90#L139) / [Author usage](https://github.com/gronki/fastconv/blob/3aaa2432a291df07a10fc5dade0dcd66d7a06dd0/README.md) |

The drivers adapt author API patterns and retain license notices. The fastconv reference is its README usage pattern, with the correct real32 kind import and the valid mode explicitly selected. These examples appear in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

Both passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-convolution-validation.json) records hashes, pins and saved output.

### spectrum-convolution-reference

```text
Signal 1 kernel 1 full/central lengths:  37  37
Scaled full / swapped / central / swapped central / sum errors:   1.920E-16   1.920E-16   1.920E-16   1.920E-16   3.331E-16
Signal 1 kernel 2 full/central lengths:  38  37
Scaled full / swapped / central / swapped central / sum errors:   1.636E-16   1.636E-16   1.636E-16   1.636E-16   1.388E-16
Signal 1 kernel 3 full/central lengths:  39  37
Scaled full / swapped / central / swapped central / sum errors:   1.110E-16   1.110E-16   1.110E-16   1.110E-16   1.110E-16
Signal 1 kernel 4 full/central lengths:  40  37
Scaled full / swapped / central / swapped central / sum errors:   5.551E-17   5.551E-17   5.551E-17   5.551E-17   1.388E-16
Signal 1 kernel 5 full/central lengths:  41  37
Scaled full / swapped / central / swapped central / sum errors:   1.164E-16   1.164E-16   1.164E-16   1.164E-16   0.000E+00
Signal 1 kernel 8 full/central lengths:  44  37
Scaled full / swapped / central / swapped central / sum errors:   1.388E-16   1.388E-16   1.388E-16   1.388E-16   5.551E-17
Signal 1 kernel 16 full/central lengths:  52  37
Scaled full / swapped / central / swapped central / sum errors:   1.110E-16   1.110E-16   1.110E-16   1.110E-16   5.551E-17
Signal 1 kernel 17 full/central lengths:  53  37
Scaled full / swapped / central / swapped central / sum errors:   1.665E-16   1.665E-16   1.665E-16   1.665E-16   1.110E-16
Signal 2 kernel 1 full/central lengths:  37  37
Scaled full / swapped / central / swapped central / sum errors:   6.064E-16   6.064E-16   6.064E-16   6.064E-16   0.000E+00
Signal 2 kernel 2 full/central lengths:  38  37
Scaled full / swapped / central / swapped central / sum errors:   2.825E-16   2.825E-16   2.825E-16   2.825E-16   6.911E-15
Signal 2 kernel 3 full/central lengths:  39  37
Scaled full / swapped / central / swapped central / sum errors:   7.549E-16   7.549E-16   7.549E-16   7.549E-16   4.441E-15
Signal 2 kernel 4 full/central lengths:  40  37
Scaled full / swapped / central / swapped central / sum errors:   1.883E-16   1.883E-16   1.883E-16   1.883E-16   6.273E-15
Signal 2 kernel 5 full/central lengths:  41  37
Scaled full / swapped / central / swapped central / sum errors:   3.793E-16   3.793E-16   3.793E-16   3.793E-16   1.110E-15
Signal 2 kernel 8 full/central lengths:  44  37
Scaled full / swapped / central / swapped central / sum errors:   3.449E-16   3.449E-16   3.449E-16   3.449E-16   1.021E-14
Signal 2 kernel 16 full/central lengths:  52  37
Scaled full / swapped / central / swapped central / sum errors:   4.468E-16   4.468E-16   4.468E-16   4.468E-16   1.310E-14
Signal 2 kernel 17 full/central lengths:  53  37
Scaled full / swapped / central / swapped central / sum errors:   4.430E-16   4.430E-16   4.430E-16   4.430E-16   1.832E-15
PASS spectrum-convolution-reference
```

### fastconv-convolution-reference

```text
Signal 1 kernel 1 valid length=37 scaled direct-reference error=   0.000E+00
Signal 1 kernel 2 valid length=36 scaled direct-reference error=   0.000E+00
Signal 1 kernel 3 valid length=35 scaled direct-reference error=   0.000E+00
Signal 1 kernel 4 valid length=34 scaled direct-reference error=   0.000E+00
Signal 1 kernel 5 valid length=33 scaled direct-reference error=   0.000E+00
Signal 1 kernel 8 valid length=30 scaled direct-reference error=   0.000E+00
Signal 1 kernel 16 valid length=22 scaled direct-reference error=   0.000E+00
Signal 1 kernel 17 valid length=21 scaled direct-reference error=   0.000E+00
Signal 2 kernel 1 valid length=37 scaled direct-reference error=   0.000E+00
Signal 2 kernel 2 valid length=36 scaled direct-reference error=   5.226E-08
Signal 2 kernel 3 valid length=35 scaled direct-reference error=   4.057E-08
Signal 2 kernel 4 valid length=34 scaled direct-reference error=   8.097E-08
Signal 2 kernel 5 valid length=33 scaled direct-reference error=   6.966E-08
Signal 2 kernel 8 valid length=30 scaled direct-reference error=   1.014E-07
Signal 2 kernel 16 valid length=22 scaled direct-reference error=   7.548E-08
Signal 2 kernel 17 valid length=21 scaled direct-reference error=   9.450E-08
PASS fastconv-convolution-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers spectrum-convolution-reference fastconv-convolution-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
