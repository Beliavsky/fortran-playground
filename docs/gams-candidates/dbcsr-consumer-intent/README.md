# Read-only matrix handle in an early DBCSR consumer

The [preserved draft](read-only-handle.f90) declared its matrix-unpacking handle
`intent(in)`, then passed its matrix to `dbcsr_get_block_p`, whose matrix dummy
requires a definable argument. GNU 16 therefore could not resolve that generic
call. This is a **consumer interface error**, not a failed multiplication or an
upstream defect.

The successful driver declares the unpacking handle `intent(inout)`. Its
matrices, multiplication flags, scalar reference and error tolerance are
unchanged. The [failed build result](read-only-handle-result.json) preserves
the exact source hash, package pin and compiler diagnostics. No library source
or cached build was changed.

The independent source uses the
[playground MIT notice](../../../fpm_catalog/gams-drivers/licenses/tangents-blocks-drivers-MIT.txt);
its header retains the relative license path from the original submitted location.
