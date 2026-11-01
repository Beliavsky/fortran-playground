# Invalid loop-count setting in an early consumer

The [preserved draft](zero-loops.f90) incorrectly set `n_resets=0`, treating it
as a number of additional restarts. At pinned simulated-annealing revision
`a2fa094d1ee39525c7e081cfd67866975e9e1dc5`, the
[type documentation](https://github.com/jacobwilliams/simulated-annealing/blob/a2fa094d1ee39525c7e081cfd67866975e9e1dc5/src/simulated_annealing.F90#L90)
defines it as the number of main-loop runs, which must be at least one.

Zero skips the optimization loop. The consumer rejected the return, which
retained internal status 99. This is a **consumer configuration error**, not
evidence that annealing failed on a valid problem. The published driver uses
`n_resets=1` and keeps its answer tolerances unchanged. Its known-minimum
early-stop option is disabled, so the reference answer is used only for
independent validation.

The [raw failed result](zero-loops-result.json) records the exact source hash,
package pin, cached-library reuse and output. The independent consumer uses
the [playground MIT notice](../../../fpm_catalog/gams-drivers/licenses/directions-fitting-drivers-MIT.txt);
its source header retains the relative reference from its original location.
