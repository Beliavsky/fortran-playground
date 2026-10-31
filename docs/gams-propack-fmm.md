# Checked partial SVD and Laplace kernel applications

These D6 and D1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-propack-fmm-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## Historical PROPACK leading singular triplets (D6)

This uses the catalog's explicitly labeled historical SciPy PROPACK 2.1 snapshot, not a claim to test the current maintained PROPACK release. Its native serial double-precision DLANSVD and existing LP64 BLAS/LAPACK recipe are reused unchanged. Pinned DLANSVD/DLANBPRO sources and API documentation were reviewed directly; the procedure record has no pinned author example.

The driver constructs matrices with known distinct nonzero singular values s*[r,r-1,...,1], r=min(m,n). Column counts are [8,12,20], row counts are n-3, n, and n+3, and scales s are [1/8,1,8]. Each rectangular diagonal core is used directly or transformed by chained adjacent-plane rotations of its rows and columns. Orthogonal rotations preserve the prescribed spectrum and make the rotated operator dense. All matrices have full rank min(m,n); wide/tall null spaces do not establish rank-deficient-SVD behavior.

For each matrix the leading one and three singular triplets are requested separately. This gives 108 calls and 216 checked leading triplets. KMAX=r, TOLIN=1e-12, and the exact operator norm s*r is supplied as the norm estimate. A writable K is checked after return, along with INFO=0. The initial left vector is A times a vector of ones, giving a deterministic nonzero start inside the column space; the default random-start path is not tested.

The callback implements both A*x and transpose(A)*x with scalar loops, counts both directions, and must leave the stored matrix unchanged. Both directions must actually be invoked by the solver. Residuals are subsequently recomputed with separate loops over a saved copy rather than calling the operator callback as the oracle. Every returned leading singular value must match its known descending reference. Both A*v-sigma*u and transpose(A)*u-sigma*v residual norms must be small, and all returned left/right vector pairs must have identity Gram matrices. Signs of singular vectors are unrestricted.

Singular values and vectors must be finite, and returned bound estimates must be finite and nonnegative. Singular-value discrepancies and two-sided Euclidean residual norms are divided by the known operator norm; their maxima must not exceed 2e-9. Every Gram entry error must also be at most 2e-9. Saved maxima are 1.8808e-15 for singular values, 3.4320e-14 for triplet residuals and 1.2801e-13 for orthogonality.

The checks do not establish sharpness of the reported error bounds, restarted DLANSVD variants, repeated/zero singular values, arbitrary sparse-matrix adapters, other precisions, malformed requests or performance. No comparison with another SVD solver is used as the reference.

## FMM2D real Laplace target potentials (D1)

The named procedure applies the structured kernel matrix K(i,j)=log(norm(target_i-source_j)) to a real charge vector. This driver verifies that matrix application under D1. Although the procedure also has a source-supported I2 relationship to Green functions/PDEs, it does not solve a boundary-value problem; the D1 driver must not promote I2 to a checked PDE-solver claim.

Source counts [1,7,64,257,1024], two geometries, three charge patterns, requested precisions [1e-6,1e-10], and original/reversed source order give 120 calls. Each call has 24 separate targets, giving 2,880 direct target references. Source/target coincidence is explicitly rejected in fixture construction.

One geometry uses deterministic modular points in the unit square. The second concentrates the same points into two small clusters near (0,0) and (0.75,0.75). Targets include points within the broad source region, near the small cluster, and farther away. Charge patterns are positive, alternating signed weights, and a centered neutral distribution. The singleton neutral case has exactly zero charge. Reversing sources also reverses charges so the physical field is preserved; both orders are independently checked against direct sums.

For each target, independent scalar loops compute sum_j q(j)*log(distance), and a cancellation-aware scale sum_j abs(q(j)*log(distance)). The maximum absolute discrepancy divided by max(1e-12,that scale) must be at most 2e-5 for eps=1e-6 and 2e-8 for eps=1e-10. The floor handles the zero-charge fixture. Scaling by unsigned contributions avoids a meaningless relative error when the total potential nearly cancels. Every potential must be finite, IER must be zero, and source coordinates, charges and targets must remain unchanged.

Saved maximum cancellation-scaled errors are 5.6386e-12 and 2.8739e-13 respectively. This does not promise those errors on arbitrary inputs or prove that a particular multipole interaction path was selected: small fixtures may use direct interactions internally. These are correctness examples, not a large-scale speedup benchmark.

The precompiled native Fortran recipe retains its existing checksum-guarded array/empty-interaction compatibility edits, OpenMP build and one-thread sandbox execution. No kernel formulas, bounds checking, sandbox limits or library artifacts were changed for this batch. Source self-potentials, dipoles, gradients/Hessians, other kernels, vector interfaces, complete PDE solves and parallel performance remain unverified by this driver.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Loading a link does not submit a job.

### propack-spectrum-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=propack&example=gams-propack-spectrum-reference) / [Driver source](../fpm_catalog/gams-drivers/propack-spectrum-reference.f90) / [Pinned procedure](https://github.com/scipy/PROPACK/blob/36f95269ecee6ae42af0c00707b3c3cf3f869a35/double/dlansvd.F#L1) / No pinned author example; API reviewed directly.

```text
Partial SVD calls: 108
Checked leading triplets: 216
Maximum operator-scaled singular-value error:   1.8808E-15
Maximum operator-scaled triplet residual:   3.4320E-14
Maximum orthogonality error:   1.2801E-13
PASS propack-spectrum-reference
```

### fmm2d-laplace-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fmm2d&example=gams-fmm2d-laplace-reference) / [Driver source](../fpm_catalog/gams-drivers/fmm2d-laplace-reference.f90) / [Pinned procedure](https://github.com/flatironinstitute/fmm2d/blob/7e7509ecd6ebe31b9292cb00825410b478f44808/src/laplace/rfmm2dwrap.f#L1) / [Author test](https://github.com/flatironinstitute/fmm2d/blob/7e7509ecd6ebe31b9292cb00825410b478f44808/test/laplace/test_rfmm2d.f)

```text
FMM potential calls: 120
Direct target references: 2880
Maximum cancellation-scaled error at eps=1e-6:   5.6386E-12
Maximum cancellation-scaled error at eps=1e-10:   2.8739E-13
PASS fmm2d-laplace-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers propack-spectrum-reference fmm2d-laplace-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
