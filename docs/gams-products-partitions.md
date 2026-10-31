# Checked matrix products and graph partition objectives

These D1 and P drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-products-partitions-validation.json) retains source hashes, pins and actual output. GAMS categories are not exhausted.

## ForMatmul matrix products (D1)

Six (rows,inner,columns) shapes [(1,1,1),(1,3,2),(2,1,4),(2,3,5),(5,4,3),(7,5,9)] include rectangular and unit dimensions. Three deterministic input families exercise a zero left matrix, signed dyadic fractions and non-dyadic sine/cosine values with offsets. Scalar triple loops form every reference entry and its sum of absolute products; the oracle calls neither package nor intrinsic MATMUL.

Methods m1 through m4 each test default matrix multiplication and all four explicit paired transpose combinations. Transposed storage represents the same logical matrices, so the reference is identical across those variants. Matrix-vector products use a column of the right-hand matrix, with absent, false and true transpose settings. This gives 360 matrix-matrix calls and 216 matrix-vector calls, checking 6,588 scalar entries.

Output shape and finite values are required. Every abs(result-reference)/(1+sum(abs(a_i*b_i))) must be <= 128*epsilon(rk)*inner_dimension. The saved maximum scaled error is 1.6933e-16. Zero and dyadic fixtures must additionally agree exactly; all products and sums in these small fixtures are representable in the working binary precision. Both input matrices must remain unchanged.

The existing single-false-transpose-flag failures at this pin remain in [the retained probes](fpm-candidates/formatmul/false-transpose-checks.json), with [transA=false](fpm-candidates/formatmul/transa-false.f90) and [transB=false](fpm-candidates/formatmul/transb-false.f90) sources. The checked matrix-matrix calls always supply both transpose flags whenever either is present. The single matrix-vector flag uses its separate API and is checked independently. No library patch or disabled bounds checking is introduced. Methods beyond m4, complex inputs, multiple images, distributed execution and performance remain unverified.

## METIS k-way graph partitions (P)

Three sizes [12,24,48], three connected graph families (cycles, four-column rectangular grids, and three linked cliques), and unit/unequal positive edge weights give 18 graphs. Each graph is partitioned into two and three parts using seeds [1,42,93], for 108 METIS_PartGraphKway calls and 3,024 assigned vertices. Adjacency is symmetric and uses zero-based C numbering.

Every call must return METIS_OK, label every vertex in [0,nparts-1], populate every requested part and keep each part no larger than 1.5*n/nparts. This is a coarse population check, not a proof that every requested imbalance bound is met. The weighted edge-cut objective is independently recomputed once per undirected edge from the original dense upper triangle, rather than the CSR passed to METIS. Each of the 108 exact objectives must equal the returned edgecut. CSR offsets, neighbors and edge weights must remain unchanged. The observed part populations range from 4 to 26 across the suite.

No expected label sequence is imposed: swapping part numbers leaves a valid partition unchanged. The driver does not prove global optimality, heuristic reproducibility, mesh partitioning, nested dissection, vertex-weight constraints, communication-volume objectives or invalid-input handling.

## Preserved METIS option-index failure

The pinned Fortran interface declares UFACTOR at index 18 and NUMBERING at index 19, while the bundled C enum uses 17 and 18. SEED is index 9 in both. A valid cycle-graph probe using the named Fortran NUMBERING=0 and UFACTOR=100 settings builds but prints Input Error: Incorrect numflag. The C code reads 100 as the numbering flag and rejects it.

The [preserved probe](gams-candidates/metis-option-indices/README.md) includes exact source, pin, normalized hash, C-header hash and full result. The successful driver leaves numbering at its default zero, uses the matching SEED constant and passes imbalance through the typed ubvec=[1.1_real_t] argument. It does not hard-code replacement option indices or change library source, CSR checks or objective comparisons. Other option constants are not verified by this workaround.

## Sources, licenses and actual output

Pinned implementations, C declarations and available author tests were reviewed before writing these independent consumers. Their own MIT notice covers the drivers and preserved variants. ForMatmul retains BSD-3-Clause terms; metis-fpm retains its MIT wrapper and Apache-2.0 METIS/GKlib terms. No upstream implementation or test body is copied or relabeled. The METIS record has no pinned author example, so its interface and bundled C source were reviewed directly. Loading a link does not submit a job.

### formatmul-products-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=formatmul&example=gams-formatmul-products-reference) / [Driver source](../fpm_catalog/gams-drivers/formatmul-products-reference.f90) / [Pinned procedure](https://github.com/gha3mi/formatmul/blob/4b5747d49c27f0df92288e7a61d0e479e34ac78e/src/formatmul.f90#L585) / [Author test](https://github.com/gha3mi/formatmul/blob/4b5747d49c27f0df92288e7a61d0e479e34ac78e/test/test1.f90)

```text
Matrix/matrix-vector calls: 576
Independent scalar product entries: 6588
Maximum sum-absolute-product scaled error:   1.6933E-16
PASS formatmul-products-reference
```

### metis-kway-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=metis-fpm&example=gams-metis-kway-reference) / [Driver source](../fpm_catalog/gams-drivers/metis-kway-reference.f90) / [Pinned procedure](https://github.com/gnikit/metis-fpm/blob/5db1dc1e46fd819a53a86fe2170eaf5464bf17c7/src/metis_c_interface.F90#L218) / No pinned author example; API reviewed directly.

```text
K-way graph partitions: 108
Assigned vertices checked: 3024
Independent weighted-cut references: 108
Smallest/largest observed part:      4    26
PASS metis-kway-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers formatmul-products-reference metis-kway-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
