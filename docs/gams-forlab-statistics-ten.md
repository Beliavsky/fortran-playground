# Ten checked Forlab statistics and matrix drivers

Ten independent Forlab consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. The cached library was reused; only main.f90 and playground-main were compiled. The [verification report](gams-forlab-statistics-ten-validation.json) records normalized UTF-8/LF source hashes, exact pins, timings and full output. GAMS coverage remains unfinished.

## Precision and acceptance

The pinned Forlab module exports RPRE=4. These drivers import wp=>RPRE and explicitly verify 32-bit real storage; this is native REAL32, not REAL64. Independent references use REAL64 arithmetic on the actual input data or analytic formulas. Ordinary statistics and matrix checks require finite results and abs(actual-reference)<=3e-5*max(1,abs(reference)). Normal PDF and chi-square PDF/CDF checks instead require relative error <=3e-5 with a 1e-20 reference floor, retaining sensitivity to small positive probabilities. These bounded checks are not a high-precision or performance benchmark.

| Driver | GAMS | Independent checks |
| --- | --- | --- |
| Location and dispersion | L1a1b | 96 data sets: mean, sample/population variance and standard deviation |
| Covariance matrices | L1c1b | 96 three-column data sets plus separate two-vector calls, both normalization choices |
| Population shape moments | L1a1c | 90 data sets: centered third/fourth moments, population skewness and non-excess kurtosis |
| Normal density | L5a1n | 189 values, scalar/vector APIs, three locations and three scales |
| Even-degree chi-square | L5a1c | 24 positive inputs: PDF/CDF against finite exponential/factorial formulas |
| Cholesky factors | D2b1b | Seven SPD matrices with known lower-triangular factors and reconstruction |
| Symmetric eigenpairs | D4a1 | Seven known Householder-rotated spectra, dense residuals and orthogonality |
| Tall SVD | D6 | Five known tall factorizations, status, singular values, orthogonality and reconstruction |
| Dense inverses | D2a1 | Seven nonsymmetric diagonally dominant matrices, left/right inverse identities |
| Polynomial differences | H1 | 48 cubic grids: first, second and third forward-difference quotients |

## Statistics and distributions

Data families use dyadic values and three affine transformations, with n=2..33 for location/dispersion/covariance and n=4..33 for shape moments. Covariance references explicitly center each actual column and form cross-products in REAL64. Sample normalization divides by n-1; population normalization divides by n. Only flag=1 population skewness and non-excess kurtosis are verified; bias-adjusted flag=0, constant arrays, missing values and singleton normalization are excluded.

Normal PDF cases use mu=-1,0,1; sigma=1/2,1,2; and 21 standardized offsets -5..5. References use exp(-z*z/2)/(sigma*sqrt(2*pi)). Chi-square cases use degrees of freedom 2,4,6,8 and x=1/8,1/2,1,2,4,8. Setting k=degrees/2 and t=x/2 gives PDF=t**(k-1)*exp(-t)/(2*(k-1)!) and CDF=1-exp(-t)*sum_{j=0}^{k-1} t**j/j!. This oracle does not call an incomplete-gamma library. Boundary x=0, odd degrees, invalid sigma and extreme tails are excluded.

## Matrices and differences

Cholesky inputs are formed from independently constructed dyadic lower-triangular factors for n=2..8; both the returned factor and product are checked. Symmetric eigenproblems use a local analytic Householder matrix Q and alternating-sign distinct diagonal eigenvalues: A=Q*diag(d)*transpose(Q). Every residual and column inner product is checked, as is the known eigenvalue set without prescribing vector signs or ordering.

Tall SVD inputs have m=n+2,n=2..6 and known orthonormal columns scaled by distinct positive singular values. Both thin-factor orthogonality conditions, status, known singular values and reconstruction are checked. Wide/rank-deficient cases and optional-mode state behavior are excluded. Inverse cases cover n=2..8, exercising the direct 2x2/3x3 and larger LU paths, with both inverse identities checked. Singular and ill-conditioned matrices are excluded.

Forward-difference cases sample p(t)=t**3+2*t*t-3*t+1 at lengths 5..20 and h=1/8,1/4,1/2. First quotient references are 3*t*t+4*t-3+(3*t+2)*h+h*h; second quotients are 6*(t+h)+4; third quotients are 6. These exact polynomial identities check all returned entries and lengths. This does not verify a general derivative error estimator or numerical quadrature.

## Retained unsuccessful probes

The [saved probes](gams-candidates/forlab-statistics/README.md) include exact sources, normalized hashes, pins and full hosted results. The median/percentile consumer built but crashed with SIGSEGV on the first median call at n=1; the cause is undiagnosed. Its combined procedure record has no checked driver, and unreached percentile calls or larger medians are not promoted.

The initial chi-square consumer named a variable shape, hiding the SHAPE intrinsic in an unused helper; renaming it corrected that consumer compile error. The corrected driver passed stricter relative checks. A combined diff/cumsum consumer built and passed its first-difference quotients, then failed cumulative reconstruction: 4.458984375 instead of 4.486328125. The pinned cumsum sorts values before accumulation, so it does not produce input-order prefixes. That combined record has no checked driver. The published diff-only consumer separately verifies all three orders on all 48 grids and makes no cumsum claim. No upstream numerical code was patched.

## Provenance

Pinned public interfaces and implementations were reviewed directly. The pinned example directory contains clustering, interpolation and random-generation consumers, rather than author examples of these exact calls; author_example is therefore null for these independently authored drivers. All ten drivers use the MIT consumer license and copy no implementation bodies. Classifications follow the [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html). Loading an example does not submit a job. See the [coverage report](gams-coverage.md) for remaining work.

## Driver details

### forlab-location-dispersion-reference (L1a1b)

Independent API consumer. 96 finite REAL32 data sets n=2..33 and three dyadic affine families. Mean, sample/population variance and standard deviation checked against explicit REAL64 centered sums. Singleton, empty and missing-value conventions excluded.

### forlab-covariance-matrices-reference (L1c1b)

Independent API consumer. 96 finite REAL32 three-column data sets n=2..33. Sample/population covariance matrices and separate two-vector covariance checked against explicit REAL64 centered cross-products. Other normalization options and missing data excluded.

### forlab-polynomial-differences-reference (H1)

Independent API consumer. 48 dyadic uniform-grid cubic samples, lengths 5..20 and h=1/8,1/4,1/2. First, second and third forward difference quotients checked with exact polynomial formulas. Does not verify cumsum (separate retained failed probe), general derivative-error estimation or numerical quadrature.

### forlab-population-shape-moments-reference (L1a1c)

Independent API consumer. 90 nonconstant finite REAL32 data sets n=4..33, three affine families. Population skewness and non-excess kurtosis (flag=1) checked against explicit REAL64 centered third/fourth moments. Bias-adjusted flag=0, constant arrays and missing data are not verified.

### forlab-normal-density-reference (L5a1n)

Independent API consumer. 189 normal PDF comparisons: mu=-1,0,1; sigma=1/2,1,2; 21 standardized dyadic offsets -5..5. Scalar/vector APIs checked against the independent exponential formula in REAL64. CDFs, tails beyond this range and invalid sigma excluded. Relative comparisons use reference floor 1e-20, rather than a unit absolute floor.

### forlab-even-chi-square-reference (L5a1c)

Independent API consumer. 24 strictly positive chi-square inputs for even degrees of freedom 2,4,6,8 and x=1/8,1/2,1,2,4,8. PDF and CDF checked with finite exponential/factorial formulas, not another incomplete-gamma API. Boundary x=0 and odd degrees excluded. Relative comparisons use reference floor 1e-20, rather than a unit absolute floor.

### forlab-cholesky-factors-reference (D2b1b)

Independent API consumer. Seven REAL32 SPD matrices n=2..8 constructed from known nonsingular lower-triangular dyadic factors. Returned factor and A=L*transpose(L) reconstruction checked against REAL64 references. Nonpositive-definite inputs excluded.

### forlab-symmetric-eigenpairs-reference (D4a1)

Independent API consumer. Seven REAL32 symmetric eigensystems n=2..8 with known Householder-rotated alternating-sign eigenvalues. Dense residuals, orthogonality and order-independent analytic eigenvalues checked; eigenvector signs and ordering are not prescribed.

### forlab-tall-svd-reference (D6)

Independent API consumer. Five REAL32 tall matrices (m=n+2,n=2..6) from known orthonormal Householder columns and positive distinct singular values. Status, analytic singular-value set, thin-factor orthogonality and reconstruction checked. Wide, rank-deficient and optional-mode state behavior excluded.

### forlab-dense-inverses-reference (D2a1)

Independent API consumer. Seven nonsymmetric diagonally dominant REAL32 matrices n=2..8, including direct 2x2/3x3 and larger LU paths. Both left/right inverse products checked against identity using the original dense matrix. Singular and ill-conditioned inputs excluded.

## Provenance and actual output

### forlab-location-dispersion-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-location-dispersion-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-location-dispersion-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L5988) / No pinned author example; API reviewed directly.

```text
Three dyadic affine data families, sizes through 33, independently checked.
Forlab real storage bits: 32
PASS forlab-location-dispersion-reference
```

### forlab-covariance-matrices-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-covariance-matrices-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-covariance-matrices-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L1809) / No pinned author example; API reviewed directly.

```text
Three dyadic affine data families, sizes through 33, independently checked.
Forlab real storage bits: 32
PASS forlab-covariance-matrices-reference
```

### forlab-polynomial-differences-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-polynomial-differences-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-polynomial-differences-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L2673) / No pinned author example; API reviewed directly.

```text
48 cubic grids: first, second and third polynomial forward differences checked.
PASS forlab-polynomial-differences-reference
```

### forlab-population-shape-moments-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-population-shape-moments-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-population-shape-moments-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L7732) / No pinned author example; API reviewed directly.

```text
Three dyadic affine data families, sizes through 33, independently checked.
Forlab real storage bits: 32
PASS forlab-population-shape-moments-reference
```

### forlab-normal-density-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-normal-density-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-normal-density-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L6296) / No pinned author example; API reviewed directly.

```text
189 normal densities; scalar and vector APIs checked.
Forlab real storage bits: 32
PASS forlab-normal-density-reference
```

### forlab-even-chi-square-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-even-chi-square-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-even-chi-square-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L1375) / No pinned author example; API reviewed directly.

```text
24 even-degree chi-square PDF/CDF cases independently checked.
Forlab real storage bits: 32
PASS forlab-even-chi-square-reference
```

### forlab-cholesky-factors-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-cholesky-factors-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-cholesky-factors-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L1595) / No pinned author example; API reviewed directly.

```text
Seven known Cholesky factors and reconstructions checked.
Forlab real storage bits: 32
PASS forlab-cholesky-factors-reference
```

### forlab-symmetric-eigenpairs-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-symmetric-eigenpairs-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-symmetric-eigenpairs-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L2956) / No pinned author example; API reviewed directly.

```text
Seven analytically constructed symmetric eigensystems checked.
Forlab real storage bits: 32
PASS forlab-symmetric-eigenpairs-reference
```

### forlab-tall-svd-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-tall-svd-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-tall-svd-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L8386) / No pinned author example; API reviewed directly.

```text
Five tall SVDs: exact singular values and reconstruction checked.
Forlab real storage bits: 32
PASS forlab-tall-svd-reference
```

### forlab-dense-inverses-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-dense-inverses-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-dense-inverses-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L4293) / No pinned author example; API reviewed directly.

```text
Seven nonsymmetric inverses, left and right identities checked.
Forlab real storage bits: 32
PASS forlab-dense-inverses-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers forlab-location-dispersion-reference forlab-covariance-matrices-reference forlab-polynomial-differences-reference forlab-population-shape-moments-reference forlab-normal-density-reference forlab-even-chi-square-reference forlab-cholesky-factors-reference forlab-symmetric-eigenpairs-reference forlab-tall-svd-reference forlab-dense-inverses-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
