# Checked real QR factorization and automatic differentiation

These D5 and H1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-qr-autodiff-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Rectangular real QR: linalg (D5)

Row counts [1,2,4,6], column counts [1,2,3,5], four matrix patterns and scales [-4,0.5,2] give 192 matrix fixtures. The deterministic base entries are small dyadic fractions with a diagonal shift. Other patterns repeat the first column as the last when possible, set the first column to zero, or set the whole matrix to zero. Thus the fixtures include square, tall and wide matrices and rank-deficient cases; no full-rank assumption or rank estimate is made.

Each fixture is factored without pivoting, with free column pivoting, and with the first input column locked: 576 QR calls. Pivot indices must form a valid permutation; the locked column must remain first. The returned permutation matrix is checked entry by entry against those indices, and the input must remain unchanged. Returned full Q and trapezoidal R must have shapes [m,m] and [m,n] and finite values.

Independent scalar loops check Q*R against A(:,pivot) with maximum absolute error divided by max(1,maxabs(A)) at most 2e-12. They also check every entry of transpose(Q)*Q-I within 5e-12, and entries of R below the diagonal within normalized 1e-12. The driver does not prescribe factor signs or a particular valid ordering of free pivots. These checks verify real factorization and output invariants; they do not verify complex QR, solves, numerical rank estimation, rank-one updates or malformed-dimension behavior. The author QR example was reviewed for registration and pivot conventions; no example code is copied.

## Analytical scalar derivatives, gradients and Jacobians: differentia (H1)

Thirty-three scalar inputs t=i/8 for i=-16..16 exercise three functions: t**5-3*t**3+2*t-7; exp(t)*sin(t)+cos(2*t); and log(t+3)+sqrt(t+3)+1/(t+3). Hand-derived derivatives are 5*t**4-9*t**2+2; exp(t)*(sin(t)+cos(t))-2*sin(2*t); and 1/z+0.5/sqrt(z)-1/z**2 with z=t+3. Both function values and derivatives are checked, giving 99 scalar calls. All logarithm/square-root arguments are positive and bounded away from zero.

At 33 three-variable inputs the coupled scalar x1**2*x2+sin(x3)+exp(x1-x2) is checked against gradient [2*x1*x2+e,x1**2-e,cos(x3)], where e=exp(x1-x2). This adds 33 gradient calls. The input vectors are [i/8,(modulo(i,7)-3)/4,(modulo(i,5)-2)/3].

The vector map [x1*x2+sin(x3),exp(x1)+x2**2-x3,x1/(x3+4)+cos(x2)] has analytical Jacobian rows [x2,x1,cos(x3)], [exp(x1),2*x2,-1], [1/(x3+4),-sin(x2),-x1/(x3+4)**2]. Every vector value and all nine entries are checked first with a temporary workspace and again with one reused dense workspace, giving 66 Jacobian calls. All results must be finite, with error divided by max(1,abs(reference)) at most 2e-12. These are automatic derivatives of dual-number callbacks, not finite differences.

Before the valid evaluations, a length-two gradient output for three inputs and a length-two vector output for the square three-input Jacobian must each return an allocated error. Workspace construction and subsequent valid calls must clear those errors and succeed. Module callbacks avoid nested callback state. Sparse Jacobians, all intrinsic overloads, nonsmooth points, higher derivatives and every failure mode remain unverified. The separate forwarddiff catalog alias and each linalg sibling algorithm require their own matching driver; the QR and AD drivers do not supply execution evidence for them.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream terms remain separate. Author sources were reviewed for interfaces, and no upstream implementation or test code is copied. Loading a link does not submit a job.

### linalg-qr-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-qr-reference) / [Driver source](../fpm_catalog/gams-drivers/linalg-qr-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_qr.f90#L20) / [Author example/test](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/examples/linalg_qr_example.f90)

```text
Real matrix fixtures: 192; QR factorizations: 576
Square/tall/wide, repeated/zero columns, zero matrices; free and locked pivots.
Maximum normalized scalar reconstruction error:   4.4409E-16
Maximum scalar orthogonality error:   6.6613E-16
PASS linalg-qr-reference
```

### differentia-analytic-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=differentia&example=gams-differentia-analytic-reference) / [Driver source](../fpm_catalog/gams-drivers/differentia-analytic-reference.f90) / [Pinned procedure](https://github.com/Nicholaswogan/Differentia/blob/2388e8ecf300a7bbc0904feab47023413464edf9/src/differentia_derivative.f90#L1) / [Author example/test](https://github.com/Nicholaswogan/Differentia/blob/2388e8ecf300a7bbc0904feab47023413464edf9/test/test_differentia.f90)

```text
Scalar / gradient / Jacobian calls:    99   33   66
Dense Jacobians checked with temporary and reused workspace; two dimension guards.
Maximum normalized analytical error:   4.4409E-16
PASS differentia-analytic-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers linalg-qr-reference differentia-analytic-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
