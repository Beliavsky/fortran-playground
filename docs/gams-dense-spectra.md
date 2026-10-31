# Checked dense real eigenproblems and singular-value decompositions

These D4a1 and D6 linalg drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-dense-spectra-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Known real symmetric eigenvalues: linalg (D4a1)

Ninety-six fixtures combine dimensions 1,2,3,5; four prescribed spectra; signed scales [-4,0.5,2]; and identity or Householder mixing. The unscaled spectra are 2*i-n-1, constant 2, i-1, and all zero. A Householder factor Q=I-2*v*transpose(v)/dot(v,v), with v=[1,2,...,n], supplies an independently known orthogonal basis. Scalar loops construct A=Q*diag(d)*transpose(Q), so the sorted prescribed d are the exact mathematical eigenvalues of each fixture. Repeated eigenvalues, singular matrices, indefinite matrices and zero matrices are included.

Each fixture is evaluated with eigenvalues only and with eigenvectors: 192 calls. The API uses the lower triangle. To check this contract, every unused upper-triangle entry is replaced with a large, finite, asymmetric sentinel before the call; residual references retain the full symmetric A. Both calls must preserve that input, return correctly shaped finite outputs, and match sorted prescribed eigenvalues with maximum error divided by max(1,maxabs(d)) at most 2e-12. Scalar loops check A*v-lambda*v within normalized 5e-12 and transpose(V)*V-I within absolute 5e-12. No signs or particular bases are prescribed in repeated eigenspaces.

This verifies the real symmetric standard eigenproblem. Generalized, nonsymmetric, complex and sparse overloads, malformed inputs, large matrices, difficult conditioning and performance are not verified. The API has no returned status in this invocation; acceptance is based on answers, shapes, preservation and finite-value checks.

## Known rectangular singular values: linalg (D6)

Six shapes [1,1], [2,3], [3,2], [3,3], [4,2], [2,5] combine with four prescribed spectra, signed scales [-4,0.5,2], and identity/Householder factors: 144 fixtures. For k=min(m,n), spectra are k-i+1, constant 2, [3,0,...,0], and all zero. Independent scalar loops construct A=L(:,1:k)*diag(d)*transpose(R(:,1:k)) using known orthogonal factors; its prescribed singular values are abs(d), already in descending order.

Each matrix is evaluated in full-factor, values-only, U-only and VT-only modes: 576 calls. The driver checks output shapes, finite values, unchanged input, descending nonnegative singular values and error divided by max(1,maxabs(d)) at most 2e-12. When both factors are returned, scalar sums reconstruct every entry of U*diag(s)*VT within normalized 5e-12. Every returned U column and VT row must be orthonormal within 5e-12.

Independent scalar products additionally check (A*transpose(A))*u=s**2*u and (transpose(A)*A)*v=s**2*v for every returned vector, including one-sided modes and full-storage null vectors with zero reference eigenvalue. Maximum residual divided by max(1,maxabs(d))**2 must be at most 1e-11. These checks avoid arbitrary vector signs and basis choices for repeated or zero singular values. Complex decompositions, invalid inputs, large/ill-conditioned cases and performance are outside the verified scope.

## Reproduced fortran-lapack link-size limit

Initial high-level fortran-lapack eigh and svd consumers compiled their mains but failed during linking with process signal 25 and "File size limit exceeded". This reproduces the [previously documented high-level link limit](gams-linear-algebra.md#observed-high-level-link-limit); it is not a numerical result. The new sources and actual failures are saved in the [candidate notes](gams-candidates/fortran-lapack/README.md). Neither probe ran, and neither high-level procedure receives a checked-driver designation. Existing lower-level fortran-lapack syev/gesvd demonstrations and their independent evidence remain separate. No sandbox limit, backend or package recipe was changed. The public linalg drivers above are separate consumers with successful execution evidence.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream terms remain separate. Author sources were reviewed for interfaces, and no upstream implementation or test code is copied. Loading a link does not submit a job.

### linalg-eigen-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-eigen-reference) / [Driver source](../fpm_catalog/gams-drivers/linalg-eigen-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_eigen.f90#L17) / [Author example/test](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/tests/test_eigen.f90)

```text
Known-spectrum symmetric matrices: 96; eigen calls: 192
Lower triangle with unused-upper-half poison; eigenvalues only and eigenvectors.
Maximum normalized eigenvalue error:   4.4409E-16
Maximum normalized scalar eigenvector residual:   6.1062E-16
Maximum scalar orthogonality error:   1.1102E-15
PASS linalg-eigen-reference
```

### linalg-svd-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-svd-reference) / [Driver source](../fpm_catalog/gams-drivers/linalg-svd-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_svd.f90#L12) / [Author example/test](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/tests/test_svd.f90)

```text
Known-spectrum rectangular matrices: 144; SVD calls: 576
Full/values-only/U-only/VT-only; distinct/repeated/rank-one/zero spectra at signed scales.
Maximum normalized singular-value error:   4.4409E-16
Maximum normalized scalar reconstruction error:   3.3307E-16
Maximum scalar orthogonality error:   8.8818E-16
Maximum normalized scalar singular-vector residual:   6.9081E-16
PASS linalg-svd-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers linalg-eigen-reference linalg-svd-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
