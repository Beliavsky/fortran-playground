# Stdlib PCA: executable exceeds the hosted limit

The retained analytic-pca.f90 consumer uses stdlib commit 58eb9133966c2797e0593281169ef57c43eccc1d with GNU Fortran 16.2.0 and FPM 0.12.0, reusing the existing compiled library. Its source compiles, but linking stops with `ld terminated with signal 25 [File size limit exceeded]` under the existing 16 MiB sandbox file limit. The complete hosted result, pin and normalized source hash are saved in analytic-pca-result.json.

This is a service-limit result, not evidence that PCA returned incorrect answers. No program run or successful PCA verification occurred. The source intends to check 24 rotated full-rank datasets, SVD/covariance methods, analytic means/axes/singular values/variances, truncation, projections and reconstruction. Those intended assertions are not claimed as checked results. L13b remains source-supported for this procedure. This does not alter the separate retained forpca numerical failure.

The exact source remains available for local investigation. Its MIT driver license is [here](../../../fpm_catalog/gams-drivers/licenses/pca-ordering-ten-drivers-MIT.txt); the header retains the original relative license reference from the submitted driver location. No backend limit was relaxed and no upstream numerical source was patched.
