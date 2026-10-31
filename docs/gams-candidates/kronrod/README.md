# Kronrod Gauss-order-one probe

The pinned package `312278846b6e403fdea410a823d88ef4fb92a3cc` exposes its original internal rule-generation procedures through the checksum-guarded `playground_kronrod` catalog wrapper. The author main normally generates orders 7 through 87. This candidate deliberately starts with Gauss order 1 to test the small-order branch.

The GNU Fortran 16.2.0 / FPM 0.12.0 sandbox compiled this main, reused the existing package library, and stopped at its first constant-moment check. The generated symmetric three-node Kronrod rule summed to approximately **1.156959262120**, rather than the exact integral **2** on [-1,1]. The normalized error was approximately 0.42152, beyond the original 1e-40 acceptance threshold. No later moment or order in this candidate was reached.

[Source](order-one-moments.f90) and [actual result](order-one-result.json) retain the normalized source hash, package pin, compiler, stages and cache reuse. Its independent API consumer has the same [MIT notice](../../../fpm_catalog/gams-drivers/licenses/rules-differences-drivers-MIT.txt) as the public driver; upstream terms remain separate.

The public driver separately passed Gauss orders 2,3,4,5,6,7,10 with the original 1e-40 tolerance. It does not count order 1 as verified. This is an observed failure of the pinned wrapped configuration; its implementation cause has not been established. No upstream numerical code or tolerance was changed. See the [checked review](../../gams-rules-differences.md).
