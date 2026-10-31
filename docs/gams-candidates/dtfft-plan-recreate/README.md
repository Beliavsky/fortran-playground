# dtFFT plan recreation failure

At pin `bbfd6746be7482bd8366ccb09a73b72882573984`, a complex FFT plan can be created, executed and destroyed, but the retained GNU Fortran 16.2.0 probe fails when creating the next shape in the same Fortran plan object.

The runtime reports `Attempting to allocate already allocated variable 'self'` at line 2236 of `dtfft_plan.F90`. The [allocation routine](https://github.com/ShatrovOA/dtFFT/blob/bbfd6746be7482bd8366ccb09a73b72882573984/src/dtfft_plan.F90#L2221) unconditionally allocates `self%fft_mapping`; the [destroy routine](https://github.com/ShatrovOA/dtFFT/blob/bbfd6746be7482bd8366ccb09a73b72882573984/src/dtfft_plan.F90#L1169) deallocates `self%fft` but leaves `fft_mapping` allocated. The next allocation therefore fails with runtime checks enabled.

- [Exact probe source](plan-recreate.f90)
- [Pin and normalized source hash](plan-recreate.json)
- [Complete build/run result](plan-recreate-result.json)
- [Successful checked-driver review](../../gams-multidimensional-fft.md)

The successful driver declares a fresh plan object inside a block for each shape. Each object still executes all eight fixtures, including multiple forward/backward calls, and is explicitly destroyed. Leaving the block releases its remaining allocatable components. This verifies repeated execution of a live plan, not recreation of a destroyed object, general cleanup behavior or long-running memory usage. No library patch or disabled runtime checking is used.

The Fourier output is stored as a Y-aligned pencil with reversed Fortran axes. Both the failed probe and successful driver account for this layout; it is not the cause of the recreation failure. Successful runs also retain the native UCX `/sys/class/net` diagnostic, with successful MPI statuses and numeric checks.

This independent probe is a preserved variant covered by the [driver MIT notice](../../../fpm_catalog/gams-drivers/licenses/multidimensional-fft-drivers-MIT.txt); upstream GPL-3.0-or-later terms remain separate.
