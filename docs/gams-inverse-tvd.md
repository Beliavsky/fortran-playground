# Checked matrix inversion and TVD ODE integration

These D2 and I1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-inverse-tvd-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Known-factor inverses and determinants: linalg_fortran (D2)

Matrices have dimensions 1,2,3,4,5,8 and are constructed as `A=s*L*D*U`. L and U are unit bidiagonal matrices with subdiagonal ell in [-0.5,0.25] and superdiagonal up in [-0.25,0.5]. Diagonal entries are `d(k)=(-1)**(k+1)*(k+1)`, with s in [0.5,1,8]. Scalar loops form A. These 72 base matrices and 60 first/last-row swaps give 132 nonsingular cases.

The independent inverse follows from the finite triangular factors: `Ainv(i,j)=sum((-up)**(k-i)*(-ell)**(k-j)/(s*d(k)),k=max(i,j)..n)`. The determinant is `s**n*product(d)`. A row swap negates the determinant and swaps the corresponding inverse columns. No package linear algebra supplies the references. Dimensions 2,3,4 exercise specialized determinant formulas, while 1,5,8 exercise its general LU branch.

The package inverts a working copy in place and must return true. Finite inverse entries must agree within normalized max-norm error 2e-12. Independent scalar loops check both A*Ainv and Ainv*A against the identity with maximum entrywise residual 5e-12. Finite determinants must match the factor/permutation reference with relative error at most 2e-12. Two exactly rank-deficient matrices, a 2x2 proportional-row matrix and a 3x3 diagonal matrix with a zero entry, must return zero determinant and false inverse status. These two examples do not establish general near-singularity detection. Ill-conditioned, nonsquare, empty, complex and real32 inputs are outside this driver.

## TVD Runge-Kutta ODE integration: HR-WENO (I1)

The driver solves three equations from t=0 to 1: `u1'= -u1`, `u2'= -2*u2`, `u3'=2*t`, with initial values [1,2,0]. Exact continuous solutions are exp(-t), 2*exp(-2*t) and t*t. Orders p=1,2,3 each use N=8,16,32,64 dyadic steps: 12 independent runs.

For the two decay components, an independent discrete reference is `u_j(1)=j*P_p(-j/N)**N`, with stability polynomial `P_p(z)=sum(z**k/k!,k=0..p)`. The nonautonomous component must equal 1-1/N for Euler and 1 for orders 2 and 3, checking stage-time usage. All three values must match the discrete references within 2e-12. Every single-step return time is checked within 1e-14; final state must be 2 and the function-evaluation count p*N.

Errors of the decay components against the continuous exponential solutions must decrease with each step halving. Coarse/fine error ratios must lie between 0.7*2**p and 1.5*2**p. On N=64 the maximum errors must be below 0.01, 0.0001 and 0.000001 for orders 1,2,3, respectively. Actual errors are included below.

This driver explicitly uses documented single-step mode, itask=2, to reach the prescribed dyadic times. The pinned source has a TODO about adjusting the final step in ordinary interval mode; that mode is not verified here. No matching standalone author ODE driver is recorded. Spatial WENO reconstruction, the separate multistep integrator, stiffness, backward integration, TVD behavior for shocks and performance are outside this example.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### linalg-inverse-factor-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg_fortran&example=gams-linalg-inverse-factor-reference) / [Driver source](../fpm_catalog/gams-drivers/linalg-inverse-factor-reference.f90) / [Pinned procedure](https://github.com/Euler-37/linalg_fortran/blob/30e7237ab54ca176e1c8dae4be2d9d44800e1f83/src/linalg_fortran.f90#L489) / [Author example/test](https://github.com/Euler-37/linalg_fortran/blob/30e7237ab54ca176e1c8dae4be2d9d44800e1f83/test/check.f90)

```text
132 scaled/permuted known-factor matrices, dimensions 1,2,3,4,5,8; two singular rejections.
Maximum inverse error / max(1,maxabs(reference)):   2.1274E-16
Maximum independently accumulated left/right inverse residual:   3.6082E-16
Maximum determinant relative error:   0.0000E+00
PASS linalg-inverse-factor-reference
```

### hrweno-tvd-ode-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=hrweno&example=gams-hrweno-tvd-ode-reference) / [Driver source](../fpm_catalog/gams-drivers/hrweno-tvd-ode-reference.f90) / [Pinned procedure](https://github.com/HugoMVale/HR-WENO/blob/2885105a7ba98351fed299b22e9bc0c67a809d2f/src/hrweno_tvdode.f90#L97)

```text
Order=1 steps=8 continuous error=  7.0445E-02
Order=1 steps=16 continuous error=  3.4536E-02
Order=1 steps=32 continuous error=  1.7093E-02
Order=1 steps=64 continuous error=  8.5025E-03
Order=2 steps=8 continuous error=  6.8852E-03
Order=2 steps=16 continuous error=  1.5529E-03
Order=2 steps=32 continuous error=  3.6962E-04
Order=2 steps=64 continuous error=  9.0215E-05
Order=3 steps=8 continuous error=  4.3052E-04
Order=3 steps=16 continuous error=  4.8694E-05
Order=3 steps=32 continuous error=  5.7894E-06
Order=3 steps=64 continuous error=  7.0578E-07
Maximum error against independent discrete references:   4.4409E-16
12 ODE runs: orders 1..3, exponential decay, nonautonomous forcing and grid convergence.
PASS hrweno-tvd-ode-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers linalg-inverse-factor-reference hrweno-tvd-ode-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
