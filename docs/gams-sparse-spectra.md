# Checked sparse column updates and symmetric spectra

These D2a4 and D4a1 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-sparse-spectra-validation.json) retains pins, source hashes and complete output. GAMS categories are not exhausted.

## LUSOL factorization, single update and transpose solves (D2a4)

Sizes [2,3,5,8], two nonsymmetric banded families, scales [0.25,2], and original/first-last-row-swapped matrices give 32 sparse LU factorizations. The base diagonal is 4+i/n, with lower/upper bands -0.5 and -1; the second family adds bands 0.25 and -0.125. Row swaps exercise pivot permutations without changing the system condition.

Each factorization is used before and after one replacement of column one. The new unpermuted column has off-diagonal entries 0.125*sin(i+2) and diagonal 6+1/8, then receives the same scale and row permutation. The consumer uses the public 64-bit index kind and the parameter defaults documented by the EZ wrapper. Workspace capacity is 10,000 entries. These small fixtures do not test workspace exhaustion.

Three exact solution patterns (constant, alternating with varying magnitude, and a shifted sine) each supply a normal and transpose system at both states. All 384 solves check 1,728 known solution entries. Scalar dense loops form right-hand sides and true residuals, calling no package matrix multiply. Solve modes 5 and 6 use their documented, different output arrays. Factorization, update and solve statuses must all be zero; solutions and update diagnostics must be finite.

Both max(abs(x-x_exact))/(1+max(abs(x_exact))) and max(abs(A*x-b))/(1+max(abs(b))) must be <= 5e-12, with A transposed for mode 6. Saved maxima are 2.2204e-16 and 5.1194e-16. Singular/rectangular systems, rank-changing updates, other pivot policies and multiple replacements on one factorization remain unverified.

## Preserved repeated-update accuracy probe

A two-update probe exceeded the same 5e-12 bounds after replacing columns one and eight in an 8-by-8 fixture: normalized solution error 1.0743406164692715e-11 and true residual 8.7795268635037098e-12. Successful statuses alone therefore do not establish the requested accuracy. The [retained probe](gams-candidates/lusol-drop-tolerance/README.md) includes exact source, pin, normalized hash and full result. This is not an established algorithm defect or diagnosis of a drop-tolerance problem.

The successful driver restricts its scope to one replacement and keeps the original solver settings and comparison bounds. It does not claim repeated-update accuracy. No library patch, relaxed comparison or disabled bounds checking was introduced.

## ScaLAPACKFX prescribed symmetric spectra (D4a1)

Exactly one MPI process uses a 1-by-1 BLACS grid. Sizes [2,3,5,8], three prescribed spectra, diagonal/Givens-rotated bases, scales [0.125,4], shifts [-2,0.75], lower/upper storage and block sizes [1,2] give 384 eigensystems and 1,728 eigenvalue references. Both input and eigenvector local shapes must be n-by-n.

The three base spectra are i-(n+1)/2, 1+i*i/n, and floor((i-1)/2)-1, with indices i=1..n. The third includes repeated eigenvalues; combinations of scale and shift include positive, negative and mixed spectra. Two sweeps of elementary adjacent-column Givens rotations build the nontrivial orthogonal basis Q. Scalar sums construct A=Q*diag(lambda)*transpose(Q); sorted eigenvalues are known from the scaled/shifted input spectrum.

The unused half of A is filled with quiet NaNs before scalafx_psyev(jobz=V,uplo=L/U), checking that each triangle-storage choice uses the intended entries. Descriptor and eigensolver statuses must be zero, and all returned eigenvalues/eigenvectors finite. The maximum eigenvalue error divided by 1+max(abs(expected)) must be <= 5e-12. Scalar loops check every eigenpair residual divided by 1+norm_infinity(A), and every entry of transpose(V)*V-I, each within 5e-12. Eigenvector signs and bases inside repeated-eigenvalue subspaces are deliberately not prescribed.

Saved maximum normalized eigenvalue, eigenpair and orthogonality errors are 1.0151e-15, 6.4223e-16 and 2.2204e-15. Matrices/descriptors are recreated for every storage/block choice. Generalized or complex eigensystems, multiple MPI processes, distributed scaling, large/ill-conditioned matrices and performance remain unverified.

## Sources, diagnostics and licenses

Pinned implementations and author tests were reviewed before writing these independent API consumers. The drivers and preserved probe have their own MIT notice; upstream LUSOL and ScaLAPACKFX terms remain separate. No upstream implementation or test bodies are copied or relabeled. The successful ScaLAPACKFX run retains a native UCX scandir(/sys/class/net) diagnostic in stdout; BLACS setup, solver statuses and numeric checks passed, without establishing distributed communication behavior. Loading a link does not submit a job.

### lusol-update-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=lusol&example=gams-lusol-update-reference) / [Driver source](../fpm_catalog/gams-drivers/lusol-update-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/lusol/blob/2d95174d44ec9bf9dabbbd07652c84c11fe56d71/src/lusol.f90#L101) / [Author test](https://github.com/jacobwilliams/lusol/blob/2d95174d44ec9bf9dabbbd07652c84c11fe56d71/test/lusol_test.f90)

```text
Sparse LU factorizations: 32
Single column replacements: 32
Normal/transpose solves: 384
Known solution entries: 1728
Maximum normalized solution error:   2.2204E-16
Maximum normalized true residual:   5.1194E-16
PASS lusol-update-reference
```

### scalapackfx-eigen-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=scalapackfx&example=gams-scalapackfx-eigen-reference) / [Driver source](../fpm_catalog/gams-drivers/scalapackfx-eigen-reference.f90) / [Pinned procedure](https://github.com/dftbplus/scalapackfx/blob/570cbf45836ed05cf791bc3f404f4f10929e5017/lib/scalapackfx.fpp#L1) / [Author test](https://github.com/dftbplus/scalapackfx/blob/570cbf45836ed05cf791bc3f404f4f10929e5017/test/test_diag.f90)

```text
[1793489440.169304] [modal:39   :0]       tcp_iface.c:912  UCX  ERROR scandir(/sys/class/net) failed: No such file or directory
Symmetric eigensystems: 384
Prescribed eigenvalue references: 1728
Maximum normalized eigenvalue error:   1.0151E-15
Maximum normalized eigenpair residual:   6.4223E-16
Maximum orthogonality residual:   2.2204E-15
PASS scalapackfx-eigen-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers lusol-update-reference scalapackfx-eigen-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
