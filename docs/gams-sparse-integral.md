# Checked sparse LU and stored-spline integration drivers

These D2a4 and H2a2b2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing precompiled libraries. Only their main programs and executables were compiled. The [verification report](gams-sparse-integral-validation.json) records source hashes, pins and actual output. GAMS categories are not exhausted.

## Sparse LU and factor reuse: Y12M (D2a4)

The base 10-by-10 matrix has `A(i,i)=4+i/4`, upper diagonal `-0.5`, lower diagonal `-1.25`, and corner entries `A(1,10)=-0.75`, `A(10,1)=0.25`. A second fixture cyclically permutes its rows as `B(i,:)=A(mod(i,10)+1,:)`, removing most diagonal entries. Both matrices are nonsymmetric and use independently packed coordinate triples.

`y12mb` prepares storage, `y12mc` factors once and `y12md` solves four right-hand sides per matrix. Exact solutions are ones, `x_i=(-1)^i*i/4`, zero and the fourth unit vector. Scalar loops form `b=A*x` from a preserved original matrix. Subsequent solves set `iflag(5)=3` to reuse the factors. Every returned status must be zero and every solution finite.

Scaled solution error `max(abs(x-x_exact))/max(1,max(abs(x_exact)))` must be at most `1e-11`. Independently evaluated backward error `||A*x-b||_inf/max(1,||A||_inf*||x||_inf+||b||_inf)` must be at most `1e-12`; the matrix norm is the maximum absolute row sum. Storage capacity is 1000 entries; pivot/storage flags are explicit in the source. Singular matrices, extreme conditioning, insufficient storage and error-code branches are not verified.

## Stored spline integrals: fitpack (H2a2b2)

Four zero-smoothing cubic interpolants represent `1`, `x`, `x^2` and `x^3` on irregular nodes `[-2,-1.7,-1,-0.25,0,0.4,1,1.6,2]`. Fit/evaluation statuses must succeed. Each polynomial is reproduced at 17 evenly spaced points, including off-knot locations, within `1e-11` absolute error, with finite outputs.

For each polynomial, six integration intervals are checked: `[-2,2]`, `[-0.7,1.3]`, `[-2,-0.25]`, `[0.4,2]`, `[1.3,-0.7]` and `[0.2,0.2]`. Exact references use `x^(degree+1)/(degree+1)`. Three additional calls check `[-2,0.15]`, `[0.15,2]` and `[-2,2]`, with analytic references for the parts and an additivity check. All 36 integral calls must be finite and agree within `1e-11`, including reversed and zero-width intervals. Curves are destroyed after each case. This verifies integration of the represented spline, not adaptive callback quadrature, extrapolation or smoothing approximation accuracy.

## Checked links and actual output

These independently written API consumers have their own MIT notice. Author examples/tests were reviewed for usage; upstream package licenses remain separate. Loading a link selects source without submitting a job.

### y12m-sparse-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=y12m&example=gams-y12m-sparse-reference) / [Driver source](../fpm_catalog/gams-drivers/y12m-sparse-reference.f90) / [Pinned procedure](https://github.com/ivan-pi/y12m/blob/5245418ed3f87c72bff4660432212328640a6322/src/y12m.f90#L91) / [Author example/test](https://github.com/ivan-pi/y12m/blob/5245418ed3f87c72bff4660432212328640a6322/test/test_y12mc_errors.F90)

```text
Matrix 1, RHS 1 solution error=  2.22E-16 backward error=  6.58E-17
Matrix 1, RHS 2 solution error=  8.88E-17 backward error=  4.55E-17
Matrix 1, RHS 3 solution error=  0.00E+00 backward error=  0.00E+00
Matrix 1, RHS 4 solution error=  4.43E-17 backward error=  1.75E-17
One sparse LU factorization reused for four right-hand sides.
Matrix 2, RHS 1 solution error=  2.22E-16 backward error=  1.32E-16
Matrix 2, RHS 2 solution error=  1.78E-16 backward error=  9.11E-17
Matrix 2, RHS 3 solution error=  0.00E+00 backward error=  0.00E+00
Matrix 2, RHS 4 solution error=  0.00E+00 backward error=  0.00E+00
One sparse LU factorization reused for four right-hand sides.
PASS y12m-sparse-reference
```

### fitpack-spline-integral

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fitpack&example=gams-fitpack-spline-integral) / [Driver source](../fpm_catalog/gams-drivers/fitpack-spline-integral.f90) / [Pinned procedure](https://github.com/perazz/fitpack/blob/1907c7bad9f5c4557970e906bdd4909eb52b2d4c/src/fitpack_curves.f90#L105) / [Author example/test](https://github.com/perazz/fitpack/blob/1907c7bad9f5c4557970e906bdd4909eb52b2d4c/examples/example_curve.f90)

```text
Polynomial degree 0 maximum integral error=  2.22E-16
Polynomial degree 1 maximum integral error=  4.44E-16
Polynomial degree 2 maximum integral error=  8.88E-16
Polynomial degree 3 maximum integral error=  8.88E-16
36 integrals checked, including reversed/zero intervals and off-knot partition additivity.
PASS fitpack-spline-integral
```

## Rejected forpca variance probe

Five observations have means `[10,-4]` and orthogonal centered columns `[-4,-2,0,2,4]` and `[1,-2,2,-2,1]`. Their unbiased covariance is exactly `diag(10,3.5)`, so principal variances are `[10,3.5]` and explained percentages `[74.074074...,25.925926...]`.

SVD mode returned `[100,12.25]` and percentages `[89.086860...,10.913140...]`. The independent eigenvalue check fails. The sandbox compiled the probe and reused the package library: this is a numerical output failure, not a service limit.

The [pinned source](https://github.com/gha3mi/forpca/blob/d5d87badc4c25c647b3618f22560e712728d8165/src/forpca.f90#L135) takes an SVD of the covariance matrix, then sets `latent=S**2/(ncol-1)`. Covariance singular values already equal its nonnegative eigenvalues; squaring them again explains this two-variable result. This is a source-based diagnosis, not an upstream-confirmed fix. The ordinary catalog demo checks a principal direction and an independently formed rank-one reconstruction, which do not certify latent variances or explained percentages.

[Probe source](gams-candidates/forpca/covariance-variances.f90) / [Actual sandbox result](gams-candidates/forpca/covariance-variances-result.json)

The failed probe is absent from the checked-driver manifest and menus. The L13b and D6 procedure mappings remain source-supported. Eigen mode, score/reconstruction outputs and any corrected upstream version need separate verification. No package patch or library rebuild was performed.

## Maintenance

```text
python xverify_gams_drivers.py --drivers y12m-sparse-reference fitpack-spline-integral
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. Publishing these drivers needs no backend redeployment or package library rebuild. The [coverage report](gams-coverage.md) lists remaining work.
