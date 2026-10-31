# Checked diagonal solves and uncoupled harmonic responses

These D2 and I1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-diagonal-response-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## SpecialMatrices: nonsingular real diagonal systems (D2)

Sizes 1,2,7,32, three diagonal patterns and scales -4,0.125,8 give 36 fixtures. Before scaling the diagonals are d_i=i, d_i=(-1)**i*(1+mod(i,3)), or d_i=2**(mod(i,7)-3). All entries are nonzero. Four known solution columns use x_i,c=(2*i-3*c)/8 for c=1,2,3, and zero for c=4. Construct b_i,c=d_i*x_i,c before calling the library.

Each fixture calls solve once with the four-column matrix and four times with individual vectors: 180 solves and 3,024 solution-coordinate comparisons. Returned shapes and finite values are required. Maximum coordinate error divided by max(1,maxabs(reference_column)) must be <=2e-13. Scalar residuals abs(d_i*x_i-b_i)/max(1,abs(b_i),abs(d_i*reference_i)) must also be <=2e-13 for both overloads. The right-hand sides, constructor diagonal and dense views of the structured matrix must remain unchanged.

The D2 assignment is deliberately broad; this driver verifies only real diagonal solve overloads. Other matrix structures, singular diagonals, invalid sizes, complex arithmetic and performance are not verified.

## dynamics: unit-mass, diagonal-stiffness response (I1)

This is a steady-state harmonic response of second-order ODEs, not an initial-value integration. Sizes n=1,2,3 use M=I and K=diag(1**2,...,n**2). Damping is C=alpha*M+beta*K, alpha=0.1,0.4 and beta=0,0.05. Two complex force patterns give 24 fixtures, each at angular frequencies [0,0.5,1,1.5,2,2.5,3,4] rad/s. There are 384 complex-coordinate comparisons, including damped resonances and static frequency zero.

For physical coordinate i and force pattern p=1,2, F_i(w)=i*(1+0.1*w)+imaginary_unit*p*(0.25*i-0.2*w). The closed-form reference is X_i=F_i/(i**2-w**2+imaginary_unit*w*(alpha+beta*i**2)). Both real and imaginary parts contribute to the complex absolute error. At each frequency, maximum coordinate error divided by max(1,maxabs(reference_response)) must be <=1e-10. Responses must have shape [8,n], be finite and return unchanged frequency values. Optional natural frequencies must match [1,...,n] within 1e-12. The polymorphic force callback must be invoked exactly eight times without changing its pattern.

## Failed broader response probes

**Non-unit mass and coupled systems are not verified.** Both probes built successfully but disagreed with independent static solutions at the pinned revision. The failed sources, hashes, package revision and complete build/run results are retained in [the candidate directory](gams-candidates/dynamics/README.md). The successful driver keeps the original 1e-10 threshold; it narrows the matrices rather than relaxing accuracy.

- With n=1, M=2, K=2, alpha=0.1, beta=0 and force pattern 1, frequency zero gave normalized response error 0.5153882032 against X=F/K.
- With n=2, M=I, Q=I-2*v*vT/(vT*v), v=[1,2], and K=Q*diag(1,4)*Q^T, the corresponding static error was 0.5625.

These are response failures, not compiler failures. No library fix is included. The published I1 driver demonstrates only the explicitly uncoupled unit-mass configuration; sparse/modal-truncated methods, arbitrary mass normalization, coupling, transient integration, invalid inputs and performance remain unverified.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and the dynamics author example were reviewed without copying upstream code. Loading a link does not submit a job.

### specialmatrices-diagonal-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=specialmatrices&example=gams-specialmatrices-diagonal-reference) / [Driver source](../fpm_catalog/gams-drivers/specialmatrices-diagonal-reference.f90) / [Pinned procedure](https://github.com/loiseaujc/SpecialMatrices/blob/2f53a4b51afbeb2efd2b60eb379283f978359d2f/src/Diagonal/specialmatrices_diagonal.f90#L191) / No pinned author example; API reviewed directly.

```text
Nonsingular diagonal fixtures: 36; solve calls: 180
Known solution coordinate checks: 3024
One four-column RHS and four vector RHS calls; signed diagonals and zero RHS.
Maximum normalized solution error:   0.0000E+00
Maximum normalized scalar residual:   0.0000E+00
PASS specialmatrices-diagonal-reference
```

### dynamics-response-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=dynamics&example=gams-dynamics-response-reference) / [Driver source](../fpm_catalog/gams-drivers/dynamics-response-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/dynamics/blob/580d04859a25126d3261e44b3fbec5111835e3a4/src/frequency/dynamics_frequency_response.f90#L119) / [Author test](https://github.com/jchristopherson/dynamics/blob/580d04859a25126d3261e44b3fbec5111835e3a4/examples/frf_example_1.f90)

```text
Harmonic response fixtures: 24; complex coordinate checks: 384
Unit mass, diagonal stiffness only; broader failed probes retained separately.
Maximum normalized response error:   0.0000E+00
PASS dynamics-response-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers specialmatrices-diagonal-reference dynamics-response-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
