# LUSOL repeated-update accuracy probe

At pin `2d95174d44ec9bf9dabbbd07652c84c11fe56d71`, the retained GNU Fortran 16.2.0 probe builds and reports successful factorization/update/solve statuses, but exceeds its proposed `5e-12` normalized solution/residual bound after two column replacements. This is an accuracy-threshold result, **not an established algorithm defect or diagnosis of a drop-tolerance problem**.

The first failing fixture has dimension 8, the first banded matrix family, scale 0.25, no row permutation, and the constant exact solution. After replacing columns 1 and 8 successively, the normal solve returns a maximum normalized solution error of `1.0743406164692715e-11` and normalized true residual `8.7795268635037098e-12`. The independent right-hand side and residual use scalar dense sums. The public EZ-wrapper parameter defaults, including its drop and pivot tolerances, are retained in this probe.

- [Exact probe source](drop-reference.f90)
- [Pin and normalized source hash](drop-reference.json)
- [Complete build/run result](drop-reference-result.json)
- [Successful single-update driver review](../../gams-sparse-spectra.md)

The checked driver uses one column replacement per fresh factorization, retaining the same matrices, solver settings, normal/transpose references and `5e-12` comparison bounds. It verifies the original and once-updated systems; it does not claim repeated-update accuracy. No library patch, relaxed comparison or disabled bounds checking is introduced. Further investigation should distinguish parameter sensitivity and accumulated update error before attributing the result to a defect.

The independent probe is a preserved variant covered by the [driver MIT notice](../../../fpm_catalog/gams-drivers/licenses/sparse-spectra-drivers-MIT.txt); upstream terms remain separate.
