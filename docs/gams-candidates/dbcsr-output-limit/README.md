# Large DBCSR consumer stopped at the output limit

The [full Cartesian draft](full-cartesian.f90) attempted 288 small matrix
products across three block layouts, four data patterns, four transpose-flag
pairs and six scalar pairs. It compiled with GNU 16, then accumulated array-
temporary diagnostics from the checked library build until the hosted
200,000-byte stage-output limit stopped the process with exit code -9.

The [complete captured result](full-cartesian-result.json) records the service
limit explicitly. It is **not a failed numerical comparison**, and does not
verify all 288 intended products. No PASS marker was reached.

The published driver tests 32 selected products: two irregular layouts, four
patterns and every N/T flag pair, cycling all six scalar pairs across those
fixtures. It also supplies contiguous copied blocks to dbcsr_put_block to
avoid an unnecessary consumer-side temporary. Internal library diagnostics
remain in the successful proof. The scalar reference and original error
tolerance are unchanged; no diagnostics are hidden, backend limits increased
or cached library sources changed.

The independent consumer uses the
[playground MIT notice](../../../fpm_catalog/gams-drivers/licenses/tangents-blocks-drivers-MIT.txt);
its header retains the relative license path from the original location.
