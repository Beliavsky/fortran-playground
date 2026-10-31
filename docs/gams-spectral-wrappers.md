# Checked real spectra: forsvd and foreig

These D6 and D4a1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-spectral-wrappers-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## forsvd: reduced real SVD (D6)

The shapes [1,1], [2,3], [3,2], [3,3], [4,2], [2,5], four spectra, signed scales -4, 0.5, 2 and identity/Householder factors give 144 matrix fixtures. Each is solved using the default method, explicit gesvd and explicit gesdd: 432 decompositions. Some degenerate settings coincide; the count is fixtures, not distinct matrices.

Let k=min(m,n). Before calling the library, construct A=L(:,1:k)*diag(d)*R(:,1:k)T. L and R are identity or Q=I-2*v*vT/(vT*v), v=[1,...,dimension]. Before signed scaling, spectra are [k,...,1], all twos, rank one [3,0,...,0], and all zeros. Exact singular values are abs(scale) times these descending nonnegative values. These are the same matrix fixtures as the [linalg SVD review](gams-dense-spectra.md).

Caller storage is U(m,m), VT(n,n), S(k), matching the pinned author test and wrapper leading dimensions. Only the returned reduced factors U(:,1:k), VT(1:k,:) are checked. Extra rows/columns are not claimed to be full null-space bases. Finite singular values must be nonnegative, descending and within normalized error 2e-12 of the prescribed spectrum. Independent scalar loops check A=U*diag(S)*VT (normalized tolerance 5e-12), reduced column/row orthogonality (absolute 5e-12), and A*A^T*u=s**2*u / A^T*A*v=s**2*v (normalized 1e-11). Value and reconstruction errors use max(1,maxabs(d)); squared-operator residuals use its square.

The driver passes a fresh input copy for every call: the pinned wrapper declares INTENT(IN) but passes the array directly to destructive LAPACK routines. Input preservation is therefore not claimed. This consumer workaround does not correct the upstream declaration. Default and explicit GESVD calls intentionally exercise both dispatch paths; agreement between methods is not used as the reference.

## foreig: real symmetric eigenproblem (D4a1)

Sizes 1,2,3,5, four spectra, signed scales -4, 0.5, 2 and identity/Householder factors give 96 fixtures and 96 explicit method=syev calls. Before scaling, diagonal spectra are d_i=2*i-n-1, all twos, d_i=i-1, and all zeros. Construct A=Q*diag(d)*Q^T and independently sort d for exact ascending eigenvalues. The eigenvalue normalization is max(1,maxabs(d)). Repeated spectra, negative eigenvalues and zero matrices allow arbitrary valid eigenspace bases.

Finite poison 1000+17*i+31*j replaces every lower-triangle entry of the input. The symmetric reference remains separate; this checks that SYEV uses the upper triangle. The input including poison must remain unchanged. Returned values and vectors must have the expected shape and be finite. Maximum normalized eigenvalue error must be <=2e-12; independent scalar A*v-lambda*v residuals must be <=5e-12 after normalization. Orthonormality uses absolute tolerance 5e-12. These use the same spectral fixtures as linalg, with the opposite unused triangle poisoned.

## Scope

Neither wrapper exposes LAPACK INFO; no status-code check is possible. Independent answer/factor identities determine success. Workspace-query internals, malformed inputs, complex overloads, severe ill conditioning, full SVD null spaces, low-rank image compression, nonsymmetric/generalized eigenproblems and performance are not verified. No backend changes or library patches were made.

## Checked links and actual output

These independently written API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and author tests were reviewed for interfaces, without copying upstream code. Loading a link does not submit a job.

### forsvd-spectrum-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forsvd&example=gams-forsvd-spectrum-reference) / [Driver source](../fpm_catalog/gams-drivers/forsvd-spectrum-reference.f90) / [Pinned procedure](https://github.com/gha3mi/forsvd/blob/f39bba7afcb048a21947a7a640bdf9a18337f8ac/src/forsvd.f90#L57) / [Author test](https://github.com/gha3mi/forsvd/blob/f39bba7afcb048a21947a7a640bdf9a18337f8ac/test/test1.f90)

```text
Known-spectrum rectangular matrices: 144; SVD calls: 432
Default/GESVD/GESDD; reduced factors, distinct/repeated/rank-one/zero spectra.
Maximum normalized singular-value error:   4.4409E-16
Maximum normalized scalar reconstruction error:   3.3307E-16
Maximum scalar orthogonality error:   9.9920E-16
Maximum normalized scalar singular-vector residual:   6.9081E-16
PASS forsvd-spectrum-reference
```

### foreig-symmetric-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=foreig&example=gams-foreig-symmetric-reference) / [Driver source](../fpm_catalog/gams-drivers/foreig-symmetric-reference.f90) / [Pinned procedure](https://github.com/gha3mi/foreig/blob/8fcfcab03e5d7cf5eda8c51c7a1e97fe52954c39/src/foreig.f90#L11) / [Author test](https://github.com/gha3mi/foreig/blob/8fcfcab03e5d7cf5eda8c51c7a1e97fe52954c39/test/test1.f90)

```text
Known-spectrum symmetric matrices: 96; eigen calls: 96
Upper triangle with unused-lower-half poison; SYEV eigenvalues and eigenvectors.
Maximum normalized eigenvalue error:   1.1102E-15
Maximum normalized scalar eigenvector residual:   9.9920E-16
Maximum scalar orthogonality error:   1.1102E-15
PASS foreig-symmetric-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers forsvd-spectrum-reference foreig-symmetric-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
