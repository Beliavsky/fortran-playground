# Complex underdetermined LSTSQ failure

Pinned stdlib revision: `58eb9133966c2797e0593281169ef57c43eccc1d`.
The original and diagnostic consumers compiled with hosted GNU Fortran 16.2.0
and FPM 0.12.0 using the cached library, then returned an API error before any
solution comparison. The first problem has `m=2, n=4`.

The diagnostic prints:

```text
Shape m,n: 2 4
[lstsq] returned Value Error: invalid problem size a= [2 4 4] , b= [2 1 1]
```

The exact [initial source](lstsq-initial.f90) and [complete result](lstsq-initial-result.json),
and [diagnostic source](lstsq-diagnostic.f90) and [complete result](lstsq-diagnostic-result.json),
include normalized UTF-8/LF source hashes and the package pin. The only diagnostic
change prints the shape and the API's error state. Neither probe produced a
numerical solution; this is an API failure, not evidence of an inaccurate answer
or a sandbox timeout.

Source-level diagnosis: `stdlib_linalg_least_squares.f90` sets `ldb=size(b,1)`
(the observation count `m`, line 1017) and passes it to `gelsd` (line 1114), even
when the solution workspace has length `n`. The
[LAPACK ZGELSD specification](https://www.netlib.org/lapack/explore-html/d9/d67/group__gelsd_ga7da8d56f14942ae8cb9e0d681f6c4e20.html)
requires `LDB >= max(1,M,N)`. This leading-dimension mismatch is a source-level
explanation consistent with the observed error for `m<n`; no patched version was
tested and no upstream numerical source was changed.

The published `stdlib-complex-minimum-norm-pinv-reference` driver solves the same
45 manufactured full-row-rank problems using `MATMUL(PINV(A),b)`. Its known
solution, consistency, stationarity and explicit null-space orthogonality checks
passed. It does not promote the failed LSTSQ procedure, which remains a separate
source-supported record without a checked driver.

The retained sources use the [MIT driver license](../../../fpm_catalog/gams-drivers/licenses/statistics-rank-ten-drivers-MIT.txt).
Their headers retain the relative license path from the originally submitted
driver location. Upstream package license terms remain separate.
