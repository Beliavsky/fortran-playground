# Checked higher-order complex derivatives and polynomial Hessians

These H1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-higher-ad-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Complex univariate derivatives through order five: DNAOAD-FPM

Fifteen sample points combine real parts [-1,-0.25,0,0.5,1] and imaginary parts [-0.5,0,0.25]. At every point, requested derivative order ranges from zero through five. Each dual variable is initialized with the sample as its value, unit first derivative when present, and zero higher seed derivatives. The pinned configuration supports at least order five and at least 15 decimal digits of real precision. All resulting expressions must retain the requested order.

Three scaled transcendental cases use exp(a*z)+sin(b*z), with (a,b)=[(0.5,-2),(1,0.5),(2,1)]. The k-th exact derivative is a**k*exp(a*z) plus b**k times the sine/cosine cycle sin(b*z), cos(b*z), -sin(b*z), -cos(b*z). This yields 945 derivative references across all sample points and requested orders, including each expression's value.

The composed expression exp(z*z+z) tests nonlinear chain rules. Let u=2*z+1. Its k-th derivative is exp(z*z+z) times the finite polynomial sum over j=0..floor(k/2) of k!/(j!*(k-2*j)!)*u**(k-2*j). These independently computed factors give another 315 references. The degree-five polynomial z**5-2*z**3+3*z+1 is evaluated through repeated dual multiplications; exact derivatives use scalar coefficients and falling factorials, adding 315 references. Zero input values and derivatives above the degree of individual terms are included.

There are 450 dual expressions and 1,575 exact complex references. Every actual real and imaginary component must be finite. Complex absolute error divided by max(1,abs(reference)) must be at most 2e-11. This verifies complex analytic univariate derivatives at the recorded points and requested orders, including product/chain rules. It does not verify orders beyond five, multivariate derivatives, nonanalytic operations, singular branches, malformed input or performance.

## Forward/reverse gradients and Hessians: diffstruc

The independent three-variable polynomial is f(x)=x1**3+x1*x2+x2*x3**2+x3**2. Its gradient is [3*x1**2+x2,x1+x3**2,2*(x2+1)*x3]. The symmetric Hessian has rows [6*x1,1,0], [1,0,2*x3], [0,2*x3,2*(x2+1)]. Five exactly representable dyadic points are [0.5,-1,2], [-0.75,0.5,1.25], [0,0,0], [2,-0.5,-1], [1,2,-2]. The fixtures exercise repeated appearances of inputs, mixed terms, vanishing derivatives and nonzero off-diagonal Hessian entries.

At each point six forward passes use the three coordinate basis directions, [1,-2,0.5], [-0.5,0,2], and [0,0,0]. Every directional derivative must equal the independent gradient dot direction. The full [1,1,1] direction mask is restored before reverse accumulation. One reverse pass checks the gradient of f, and three reverse passes through the coordinate forward-derivative graphs check every Hessian entry. Gradient buffers are reset for every reverse pass, and Hessian symmetry is checked separately.

There are 30 forward calls, 20 reverse calls and 95 exact scalar references: five values, 30 directional derivatives, 15 reverse-gradient components and 45 Hessian entries. Expression, derivative and gradient pointers must be associated before access, and actual values must be finite. Scalar errors divided by max(1,abs(reference)) must be at most 1e-5 at the package's REAL32 precision; absolute Hessian symmetry error must also be at most 1e-5. The references are hand-derived formulas, so agreement between AD modes alone cannot pass the driver.

All graphs are retained for the lifetime of this short standalone process. Graph disposal, long-lived graph reuse, memory scaling, arbitrary expressions/intrinsics, nonsmooth functions and performance are not verified. The example demonstrates the recorded forward/reverse calls and Hessian calculation, not a general graph-lifecycle prescription.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream terms remain separate. Author sources were reviewed for interfaces, and no upstream implementation or example code is copied. Loading a link does not submit a job.

### dnaoad-higher-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=dnaoad-fpm&example=gams-dnaoad-higher-reference) / [Driver source](../fpm_catalog/gams-drivers/dnaoad-higher-reference.f90) / [Pinned procedure](https://github.com/fpenunuri/DNAOAD-FPM/blob/f7f328e89b208a99797d64f4a41e97ba91b85962/src/dualzn_mod.f90#L7) / [Author example/test](https://github.com/fpenunuri/DNAOAD-FPM/blob/f7f328e89b208a99797d64f4a41e97ba91b85962/app/ex1.f90)

```text
Dual expressions at 15 real/complex points and requested orders 0..5: 450; derivative references: 1575
Scaled exp/sin / composed exp / polynomial derivatives:    945   315   315
Maximum normalized complex derivative error:   3.9205E-15
PASS dnaoad-higher-reference
```

### diffstruc-hessian-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=diffstruc&example=gams-diffstruc-hessian-reference) / [Driver source](../fpm_catalog/gams-drivers/diffstruc-hessian-reference.f90) / [Pinned procedure](https://github.com/nedtaylor/diffstruc/blob/88565f8e01792706edc0bd7e70dde957c26122a4/src/diffstruc/diffstruc_types_sub.f90#L505) / [Author example/test](https://github.com/nedtaylor/diffstruc/blob/88565f8e01792706edc0bd7e70dde957c26122a4/test/test_functions.f90)

```text
Three-variable polynomial points: 5; forward calls: 30; reverse calls: 20
Exact values, directional derivatives, gradient and Hessian entries: 95
Maximum normalized REAL32 reference error:   0.0000E+00
PASS diffstruc-hessian-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers dnaoad-higher-reference diffstruc-hessian-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
