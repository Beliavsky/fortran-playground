# fortran-lapack eigenproblem and SVD link-limit probes

These probes reproduce the [previously documented high-level link limit](../../gams-linear-algebra.md#observed-high-level-link-limit). Two independent real-spectrum drivers compiled their main with GNU Fortran 16.2.0 / FPM 0.12.0 and reused the cached fortran-lapack library at commit `e5e45fdd5a38bfab06d1f703f12b787937aa33bb`. Both then failed while linking the executable:

```text
collect2: fatal error: ld terminated with signal 25 [File size limit exceeded]
```

No program run occurred, so this is a sandbox artifact-size limitation, not evidence of an incorrect eigenvalue or singular value. The existing package demo exercises a different procedure and remains independently verified. We have not established which linked objects/debug sections cause this excess, nor changed the sandbox limit or package recipe in this batch.

- [Eigenproblem source](lapack-eigen-reference.f90) / [actual result](lapack-eigen-reference-result.json)
- [SVD source](lapack-svd-reference.f90) / [actual result](lapack-svd-reference-result.json)

The saved records include the normalized source hash, package pin, compiler and actual stages. These independent consumers have the accompanying [MIT notice](../../../fpm_catalog/gams-drivers/licenses/lapack-spectra-drivers-MIT.txt). No upstream source was copied. Their planned numerical checks were not reached and are not counted as verified. Public drivers for corresponding linalg procedures are separate tests with separate execution evidence; see the [review](../../gams-dense-spectra.md).
