# Checked differential-algebraic IVPs and complex FFT plans

These I1a2 and J1a2 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-dae-fft-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## DASKR index-one DAEs (I1a2)

Two three-state differential-algebraic systems have independent closed-form states and derivatives. With tau=t-t0, the first combines triangular exponential dynamics and a nonlinear algebraic constraint:

```text
u = A*exp(-a*tau)
v = B*exp(-b*tau) + c*A*(exp(-a*tau)-exp(-b*tau))/(b-a)
w = u+v*v
G = [u_prime+a*u, v_prime+b*v-c*u, w-u-v*v] = 0
```

The rate pairs (a,b) are (0.5,20) and (1,100), with c=0.75. Initial differential states (A,B) are (1,0.25) and (-0.5,2). Both rates are positive and unequal. This family is integrated forward only; reverse stiff exponential growth is outside the checked scope. The second, nonautonomous family is:

```text
u = tau*tau+C
v = tau**3/3+C*tau+D
w = sin(tau)+u*v
G = [u_prime-2*tau, v_prime-u, w-sin(tau)-u*v] = 0
```

For parameter p=1 or 2, C=A*p and D=B/p use the same two initial-state pairs above. This polynomial family is integrated in both time directions. Both families use t0=-0.5 or 0.75, so residuals must honor a nonzero time origin. Consistent initial states and derivatives are supplied from the closed forms; automatic correction of inconsistent initial data is not tested.

Each configuration is run with a numerical Jacobian and with a supplied dense Jacobian, independently checked against the closed form. The user callback supplies dG/dy+cj*dG/dy_prime, including algebraic rows. Its actual invocation is counted and required in user-Jacobian mode; it must not run in numerical-Jacobian mode. Only the dense direct linear-solver path is used. INFO(5) selects the Jacobian mode, while INFO(2) selects scalar or vector tolerances. Scalar RTol=1e-10 and ATol=1e-12 become componentwise [1,2,4] times those values in vector mode.

There are 32 exponential and 64 polynomial trajectories, 96 total. The BDF history is retained between eight requested relative times: [0.01,0.02,0.04,0.08,0.16,0.32,0.64,1], negated for backward polynomial runs. This gives 768 checkpoints and 4,608 analytic state/derivative entries. Forty-eight trajectories actually use the supplied Jacobian. Every output must have IDID 2 or 3, finite time/state/derivative values, and a reached time agreeing with the requested checkpoint within 32*epsilon*max(1,abs(tout)); an arbitrary positive return is insufficient.

State and derivative errors use abs(result-reference)/(1+abs(reference)), bounded by 5e-7 and 5e-6 respectively. The algebraic constraint uses the absolute residual divided by one plus the magnitudes of its state/product terms, bounded by 5e-9. The complete DAE residual is recomputed at every checkpoint, with each row scaled by one plus the magnitudes of its contributing terms, bounded by 2e-6. Saved maxima are 4.6001e-10 for state, 1.6290e-7 for derivative, 6.9436e-11 for constraint and 1.0779e-8 for residual. These global solution checks have a different meaning from requested local tolerances.

Krylov solves and preconditioners, banded storage, roots/events, inconsistent-data initialization, higher-index DAEs, invalid requests and performance remain unverified. Neither another solver nor mere agreement between Jacobian modes serves as the oracle.

## NAFPack single-precision radix-two FFT plans (J1a2)

Lengths [2,4,8,16,32,64,128], explicit RADIX2_DIT and RADIX2_DIF algorithms, four input patterns and scales [1/16,1,16] give 168 plan fixtures. Patterns are a shifted complex impulse, complex DC, a two-tone complex signal, and deterministic modular real/imaginary components. At the smallest lengths the tones alias naturally; the direct reference uses the actual discrete samples.

Each plan is executed with both ITERATIVE and recursive implementations, using explicit classic loops. Each implementation is called twice on the same unchanged input and must reproduce exactly its previous output. The plan is destroyed before the shared transform object creates its next plan. Totals are 672 calls and 24,384 coefficient comparisons, including repetitions.

The independent oracle converts the already-rounded single-precision input samples to real64 and computes all bins with scalar complex sums:

```text
F(k) = sum(j=0..n-1) x(j)*exp(-2*pi*i*k*j/n), k=0..n-1
```

Every returned real and imaginary component must be finite, and both input arrays must remain unchanged. The maximum coefficient discrepancy divided by sum(abs(input)) must be no greater than 64*epsilon(float32). Parseval independently requires abs(sum(abs(F)**2)/n - sum(abs(x)**2))/sum(abs(x)**2) <= 128*epsilon(float32). These L1/energy scales remain meaningful at bins whose exact Fourier amplitude is zero. Saved maxima are 5.1072e-7 for the L1-scaled coefficient discrepancy and 1.0004e-7 for relative Parseval error.

This checks the forward sign, frequency ordering, amplitude normalization, direct coefficient values and repeated plan usage without depending on an inverse transform to undo matching errors. Other radices, mixed/split transforms, automatic algorithm choice, inverse transforms, other precisions, multidimensional APIs, parallel loop methods and performance remain unverified.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and author examples were reviewed without copying upstream code. Loading a link does not submit a job.

### daskr-dae-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=daskr&example=gams-daskr-dae-reference) / [Driver source](../fpm_catalog/gams-drivers/daskr-dae-reference.f90) / [Pinned procedure](https://github.com/davidpfister/daskr/blob/b43533edc5d6900088a846d802e3a86d0f9a06ad/src/ddaskr.f#L1) / [Author test](https://github.com/davidpfister/daskr/blob/b43533edc5d6900088a846d802e3a86d0f9a06ad/examples/web/dweb.f)

```text
DAE trajectories: 96
Requested checkpoints: 768
Analytic state/derivative entries: 4608
Trajectories using user Jacobians: 48
Maximum normalized state error:   4.6001E-10
Maximum normalized derivative error:   1.6290E-07
Maximum normalized constraint error:   6.9436E-11
Maximum scaled residual:   1.0779E-08
PASS daskr-dae-reference
```

### nafpack-fft-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nafpack&example=gams-nafpack-fft-reference) / [Driver source](../fpm_catalog/gams-drivers/nafpack-fft-reference.f90) / [Pinned procedure](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/src/Fourier_Transform/NAFPack_Fourier_Transform.f90#L37) / [Author test](https://github.com/Minard-Jules/NAFPack/blob/9b1e9a98f8c28853a48e152605f84c994c271f45/test/Fourier_Transform/test_Fourier_Transform_fft_complex.f90)

```text
Plan fixtures: 168
FFT calls including repetitions: 672
Direct coefficient references: 24384
Maximum L1-scaled coefficient error:   5.1072E-07
Maximum relative Parseval error:   1.0004E-07
PASS nafpack-fft-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers daskr-dae-reference nafpack-fft-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
