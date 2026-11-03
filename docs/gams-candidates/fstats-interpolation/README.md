# Retained Fstats interpolation probes

The exact consumers, normalized UTF-8/LF SHA256 hashes, package revisions and full hosted GNU 16 results accompany both probes. The independent drivers use the MIT license in `fpm_catalog/gams-drivers/licenses/fstats-fitting-ten-drivers-MIT.txt`; upstream terms remain separate.

## Clamped cubic spline: numerical mismatch

The irregular knots are [-2,-0.75,0,0.5,2]. The first cubic is x^3/8-x^2/2+3x/4+1, with exact derivatives supplied at both endpoints. At the first interior query x=-1.875 the expected value is -2.988037109375 and the actual result is -2.9875673877949618. This is far outside the stated tolerance. The probe built and reused the cached library but failed at its first interior value assertion; later variants were not established.

The pinned `src/interpolation/fstats_interp.f90` lines 862-870 assign the next interval width to a2 and previous width to a4. The standard spline second-derivative equation uses the previous width for the lower diagonal and next for the upper. This is a source-supported possible cause, not a verified repair. No library source was patched. The candidate is absent from the checked-driver menu and replaced by a separate bivariate normal density driver.

## Hermite: object reinitialization

The first polynomial completed, but initialization for the second degree stopped at line 954 with an already-allocated allocation error. `hi_init` releases the raw input arrays; `hi_set_up_table` allocates divided-difference arrays without first releasing them. This establishes a reinitialization failure, not a failure of all Hermite interpolation. The published replacement creates and releases a fresh object for each polynomial, retains the same value/derivative assertions and covers all five degrees. It does not claim repeated initialization is fixed or supported.
