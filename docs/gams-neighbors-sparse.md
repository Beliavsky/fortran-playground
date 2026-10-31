# Checked nearest-neighbor searches and sparse products

These N5 and D1b4 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-neighbors-sparse-validation.json) retains pins, source hashes and complete actual output. GAMS categories are not exhausted.

## fortran-flann exact k-nearest neighbors (N5)

The driver constructs 60 single KD-tree indexes: point counts [1,2,8,31,64], dimensions two and three, three data patterns, and original/reversed point order. Patterns are deterministic modular coordinates, collinear points, and duplicate coordinate pairs. For each tree there are 20 off-data queries followed by every source point as a self-query, giving 2,472 query points. The modular two-dimensional family includes the 31-point query that failed the separate coretran probe; this verifies FLANN, not coretran.

Each query batch is searched three times, with k=1, min(3,n), and n, including repeated k settings for the smallest sets. There are 180 batched calls and 96,072 returned neighbors. Euclidean search explicitly requests checks=-1 (unlimited/exact search). Source and query arrays are single precision. The independent oracle converts those already-rounded input values to real64, directly calculates every squared Euclidean distance, and insertion-sorts those distances.

For every returned neighbor, the zero-based index must be in range, distinct within the returned list, and consistent with its reported squared distance. The indexed direct distance must equal the corresponding kth sorted reference within 32*epsilon(float32)*max(1,reference_distance). This accounts for native single-precision distance accumulation; it is not an approximate-search accuracy claim. Tied points may have any index order. Status must be zero; distances must be finite and both source and query arrays unchanged. The native index is finalized while its target array still exists.

Other metrics, approximate searches, radius queries, empty data, malformed requests, high dimensions and performance remain unverified. The pinned wrapper prints diagnostic lines on each search; the short transcript below shows only the final five summary lines. Complete diagnostics remain in the verification report.

## sparse_fortran COO/CSR products (D1b4)

Five row counts crossed with five column counts, each from [1,2,3,8,17], provide square, tall and wide matrices. Five patterns are used: all zero, diagonal, tridiagonal, modular sparse with an explicitly empty row/column, and dense. Both API orders are initialized from the same dense matrix. That gives 250 matrix/order fixtures and 500 independently initialized sparse objects. The pinned [CSR product source](https://github.com/Euler-37/sparse_fortran/blob/600f586a1ed099a22054ed283225787de36a31c1/src/sparse_csr_fortran.f90#L173) supplements the COO procedure evidence.

This API gives order a computational meaning: C computes A*x, while non-C order (F here) computes transpose(A)*x. The author example also demonstrates the latter convention. Three right-hand sides are used: ones, alternating signed i/8, and i*(n_input+1-i)/4. Each format is checked separately against scalar loops over the original dense matrix, rather than merely agreeing with the other format. Totals are 1,500 products and 9,300 checked result entries.

All nonzero fixture entries are small binary fractions, at least 1/8 in magnitude. Products and sums are exactly representable at these sizes, so returned values must equal the scalar references exactly. Output sizes and finiteness and dense-input preservation are checked. Zero matrices and empty rows/columns exercise empty storage segments. A fresh object is used for each initialization.

Zero dimensions, near-zero entry dropping (the initializer uses a 1e-15 threshold), coordinate-list initialization, repeated initialization of an existing object, incremental insertion/deletion, invalid shapes and performance remain unverified. Storage conversion is outside this multiplication proof.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and author examples were reviewed without copying upstream code. Loading a link does not submit a job.

### flann-knn-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-flann&example=gams-flann-knn-reference) / [Driver source](../fpm_catalog/gams-drivers/flann-knn-reference.f90) / [Pinned procedure](https://github.com/ivan-pi/fortran-flann/blob/35370c851602d954d1d01d10c9c14ff82dd96496/src/flann.f90#L91) / [Author test](https://github.com/ivan-pi/fortran-flann/blob/35370c851602d954d1d01d10c9c14ff82dd96496/example/flann_demo.f90)

```text
Trees: 60
Query points: 2472
Batched exact searches: 180
Checked returned neighbors: 96072
PASS flann-knn-reference
```

### sparse-matvec-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=sparse_fortran&example=gams-sparse-matvec-reference) / [Driver source](../fpm_catalog/gams-drivers/sparse-matvec-reference.f90) / [Pinned procedure](https://github.com/Euler-37/sparse_fortran/blob/600f586a1ed099a22054ed283225787de36a31c1/src/sparse_coo_fortran.f90#L193) / [Author test](https://github.com/Euler-37/sparse_fortran/blob/600f586a1ed099a22054ed283225787de36a31c1/app/main.f90)

```text
Matrix/order fixtures: 250
COO/CSR products: 1500
Checked result entries: 9300
PASS sparse-matvec-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers flann-knn-reference sparse-matvec-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
