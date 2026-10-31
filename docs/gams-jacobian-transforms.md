# Checked user-Jacobian exact fits and rigid transforms

These G1b1b and D1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-jacobian-transforms-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## nonlin: exact nonlinear least squares with user Jacobian (G1b1b)

Five observations at t=[-1,-0.5,0,0.5,1] follow y=A*exp(B*t). Amplitudes A=0.5,2 and exponents B=-1,0.25,1 use four starts each: amplitude 0.5*A or 1.5*A, exponent B-0.5 or B+0.5. There are 24 fits. Residuals are x1*exp(x2*t)-A*exp(B*t), with user Jacobian columns exp(x2*t) and x1*t*exp(x2*t). These are the exact-fit subset of the [MINPACK lmder1 fixtures](gams-jacobian-roots.md), with known parameters [A,B] and minimum sum of squared residuals zero.

The helper is explicitly configured with both residual and Jacobian callbacks. All 240 starting Jacobian entries are checked against central differences using h=1e-5*max(1,abs(x_j)); maximum entry error divided by max(1,maxabs(analytical_column)) must be <=2e-7. Both callbacks must actually be used during every solve. The solver uses initial step bound factor 1, maximum 2,000 function evaluations, and function/variable/gradient tolerances 1e-12.

At least one normal convergence flag is required, but is not sufficient. Returned parameters/residuals must be finite; residuals must agree with an independent final evaluation within 1e-11. Maximum parameter error divided by max(1,maxabs(exact_parameters)) must be <=2e-7. Sum of squared residuals must be <=1e-10, each residual <=1e-8, and maxabs(J^T*r) <=1e-6. This verifies user-Jacobian mode only: the sibling G1b1a finite-difference configuration and bound-constrained solver type are not promoted.

## Failed broader least-squares probes

The [candidate directory](gams-candidates/nonlin-least-squares/README.md) retains two failed probe sources, normalized hashes and complete results:

- Default step bound factor 100: the exact fit A=0.5, B=1 from [0.25,0.5] returns unchanged parameters with converge_on_chng true; normalized parameter error is 0.5.
- Step bound factor 1: all 24 exact fits complete, but the first nonzero-residual fixture returns unchanged starting parameters with the same convergence flag. Its known minimizer is [log(2),1]; normalized parameter error is 0.7.

No library fix or relaxed answer tolerance is included. The public driver specifies step factor 1 and verifies only the exact exponential family. Nonzero-residual minima, the default step setting, arbitrary starts, finite-difference mode and global convergence remain unverified.

## fglm: components and homogeneous transforms (D1)

Twenty-four deterministic pairs of vec3d objects give 48 double-precision vector additions/component products and 144 coordinate references. With i=1..24, a=[i/8,(i-12)/4,(-1)**i/2] and b=[(25-i)/4,-i/8,mod(i,5)-2]. Outputs must be finite, agree with scalar component formulas within absolute 1e-13, and preserve both inputs. Multiplication here is componentwise, not a dot product.

Single-precision mat4f transformations use nine angles [-2*pi,-pi,-pi/2,-pi/3,0,pi/6,pi/2,pi,2*pi], four translations [0,0,0], [1,-2,0.5], [-4,0,2], [0.25,0.5,-0.75], and both call orders. Every matrix starts from explicit identity. Translate then rotate produces T*R; rotate then translate produces R*T. There are 72 matrices and 216 transformed homogeneous vectors: points [1,2,3,1], [-2,0.5,0,1], and direction [1,-1,2,0]. The zero homogeneous coordinate independently checks translation invariance of directions. All 864 output coordinates are compared to direct formulas.

Reference sine/cosine values are computed in double precision from the actual single-precision input angle. Coordinates use Rz(x,y)=[cos*x-sin*y,sin*x+cos*y] and the appropriate translation order. Maximum coordinate error divided by max(1,maxabs(reference_vector)) must be <=2e-6. Every matrix/output must be finite. Scalar checks of R^T*R=I give 648 orthogonality entries, and 72 determinants must equal one; both use absolute tolerance 2e-6. Arbitrary 3D rotation axes, other vector overloads, projection matrices and performance remain unverified.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and the nonlin author example were reviewed without copying upstream code. Loading a link does not submit a job.

### nonlin-lsq-jacobian-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nonlin&example=gams-nonlin-lsq-jacobian-reference) / [Driver source](../fpm_catalog/gams-drivers/nonlin-lsq-jacobian-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/src/nonlin_least_squares.f90#L141) / [Author test](https://github.com/jchristopherson/nonlin/blob/2133d067886ea6eca0552ebca9ed7bb8a262e5b8/examples/nonlin_least_squares_example.f90)

```text
Total / exact-fit solves:    24   24
Analytical Jacobian entries checked by central differences at starting points: 240
Maximum normalized parameter error:   2.2204E-16
Maximum normalized Jacobian finite-difference error:   4.1373E-11
Maximum absolute J-transpose-residual component:   5.7772E-15
PASS nonlin-lsq-jacobian-reference
```

### fglm-transform-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fglm&example=gams-fglm-transform-reference) / [Driver source](../fpm_catalog/gams-drivers/fglm-transform-reference.f90) / [Pinned procedure](https://github.com/jordan4ibanez/fglm/blob/e1b6a5404b3e7a266da33173a07166970c16dd86/src/matrix_4f.f90#L267) / No pinned author example; API reviewed directly.

```text
Double-precision vector operations: 48
Single-precision rigid transforms: 72; coordinate references: 864
Both composition orders; points and directions; orthogonality and determinant.
Maximum vector component error:   0.0000E+00
Maximum normalized transform error:   1.0066E-07
PASS fglm-transform-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers nonlin-lsq-jacobian-reference fglm-transform-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
