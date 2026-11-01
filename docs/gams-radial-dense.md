# Checked radial eigenstates and dense-layer inference

These I1 and K drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-radial-dense-validation.json) retains pins, source hashes and complete output. GAMS categories are not exhausted.

## dftatom nonrelativistic Coulomb eigenstates (I1)

The independent consumer solves the radial eigenproblem for V(r)=-Z/r with nuclear charges Z=[1,2,4]. All six (n,l) states through n=3 are tested on meshes with 3,000 and 4,500 intervals, giving 36 eigenproblems. The library exponential mesh runs from 1e-8/Z to 100/Z with a largest/smallest interval ratio of 1e6. Initial energy is -0.4*Z**2/n**2, bracket [-Z**2,0], energy tolerance 1e-11*Z**2 and iteration limit 100. The nonrelativistic mode is selected and Coulomb-tail perturbation corrections are enabled.

The exact energy is -Z**2/(2*n**2) Hartree. See the [MIT hydrogen lecture](https://ocw.mit.edu/courses/5-61-physical-chemistry-fall-2007/c2078ff25c61c136e67ceb6fd8eb9b34_lecture21to22.pdf) for Coulomb energies and radial eigenstates. The wavefunction normalization convention used here is the generalized-Laguerre form in [Gonzalez et al., equations (1.2)-(1.4)](https://arxiv.org/html/1505.06274v3). In atomic units, rho=2*Z*r/n and P=r*R_nl=C*r*exp(-rho/2)*rho**l*L_(n-l-1)^(2*l+1)(rho), with C=sqrt((2*Z/n)**3*(n-l-1)!/(2*n*(n+l)!)). The reference Q is the direct derivative dP/dr.

Only polynomial degrees 0,1,2 are needed. The driver evaluates their elementary formulas and derivatives directly; the convention is documented by [NIST DLMF 18.5.12](https://dlmf.nist.gov/18.5.E12). No special-function library or numerical differencing supplies the reference. One common sign aligns P and Q with the analytic state, since an eigenfunction phase is arbitrary. Every one of the 135,036 P entries and 135,036 Q entries is compared, including zeros and tails.

The driver independently integrates P**2, r*P**2 and P**2/r with scalar trapezoidal sums on the physical nonuniform mesh. It checks normalization one, mean radius (3*n**2-l*(l+1))/(2*Z), and mean inverse radius Z/n**2. Moments are divided by the independently computed norm; the norm is also checked separately. These moment formulas also follow by integrating the explicit degree-at-most-two polynomials. The library normalization quadrature is not reused.

Solver status must be zero, and energy/P/Q must be finite. Absolute energy discrepancy divided by Z**2 must be <=1e-7. Maximum P discrepancy divided by sqrt(Z) must be <=2e-5; maximum Q discrepancy divided by Z**1.5 must be <=5e-5. Trapezoidal norm discrepancy must be <=2e-5. Radius discrepancy times Z/(1+n**2) and inverse-radius discrepancy divided by Z must each be <=2e-5. Finite-domain tails and quadrature discretization are part of this acceptance test; it is not a rigorous continuous error bound.

Saved maxima for energy, P, Q, norm, radius and inverse-radius checks were 4.76529e-11, 9.19163e-10, 1.20398e-5, 3.53696e-6, 2.11486e-9 and 9.09494e-11. The trapezoidal norm discrepancy decreases from about 3.537e-6 on the 3,000-interval mesh to 1.572e-6 on the finer mesh; it should not be read as an error in the library normalization routine. Q errors are larger than P errors and remain subject to their separately stated bound. Dirac eigenstates, general potentials, higher states, Poisson and self-consistent density-functional calculations remain unverified. The maintained I1 mapping is broad, not a claim to verify every radial solver mode.

## Athena fixed dense-layer forward evaluation (K)

The independent consumer creates 192 fixed layers: input widths [1,2,3,5], output widths [1,2,4], activations [none,relu,tanh,sigmoid], bias on/off and two parameter patterns. With one-based indices, weights W_ij=(2*i-3*j+1)/8 and biases b_i=(2*i-3)/8 in the dyadic pattern; denominators are 7 and 9 in the non-dyadic pattern. Values are first rounded to the cached library real32 precision; the oracle uses these actual stored coefficients widened to real64. Randomly initialized weights are overwritten completely.

Each layer evaluates 11 inputs: zero, every coordinate basis vector, then deterministic mixed signed dyadic vectors. Zero/basis inputs expose bias handling and individual weight columns. The mixed vectors use x_j=(modulo(sample*(2*j+1),17)-8)/8. A scalar real64 loop forms z_i=b_i+sum_j(W_ij*x_j), omitting bias when disabled. Reference activations are z, max(0,z), 2/(1+exp(-2*z))-1 and a sign-stable sigmoid expression. No MATMUL or another network package supplies the oracle.

There are 4,928 independent output entries. Every output must have the requested dimension and be finite, with error divided by 1+abs(reference) <=2e-6. After the other inputs, the initial zero feature is evaluated again and all 448 output entries must match their original values exactly, giving 2,304 total forward calls. The maximum normalized real64-oracle discrepancy was 5.77239e-8. This verifies forward evaluation of known functions, not how well a trained network approximates an external dataset. K remains the broad approximation class.

The input array is deliberately persistent and marked is_temporary=.false. after allocation. An [earlier draft](gams-candidates/athena-temporary-input/README.md) left the default temporary ownership flag in place and aborted during repeated forward calls. Its exact source, dependency pins and failed result are retained. Correcting the consumer flag preserved all weights, fixtures and tolerances; no library source was patched. Training, automatic derivatives, batch inference, graph networks, serialization and general memory safety remain unverified.

## Sources, licenses and actual output

Pinned APIs, implementations and author tests were reviewed before writing the independent consumers. No upstream implementation or test bodies are copied. The drivers have their own MIT notice; upstream dftatom and Athena license terms remain separate. Loading a driver does not submit a job.

### dftatom-hydrogen-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=dftatom&example=gams-dftatom-hydrogen-reference) / [Driver source](../fpm_catalog/gams-drivers/dftatom-hydrogen-reference.f90) / [Pinned procedure](https://github.com/certik/dftatom/blob/e49b3042de6e2471afe5eea992c9ba50dac08f95/src/reigen.f90#L1) / [Author test](https://github.com/certik/dftatom/blob/e49b3042de6e2471afe5eea992c9ba50dac08f95/tests/hydrogen/hydrogen.f90)

```text
Case Z,mesh,n,l and six errors:      1  3000     1     0   2.171E-11   9.504E-11   1.204E-05   3.537E-06   7.696E-11   5.373E-11
Case Z,mesh,n,l and six errors:      1  3000     2     0   2.637E-11   3.242E-10   4.257E-06   3.537E-06   5.302E-10   5.208E-11
Case Z,mesh,n,l and six errors:      1  3000     2     1   8.325E-12   1.624E-10   4.719E-11   3.537E-06   1.841E-10   1.621E-11
Case Z,mesh,n,l and six errors:      1  3000     3     0   4.765E-11   9.192E-10   2.317E-06   3.537E-06   2.115E-09   9.095E-11
Case Z,mesh,n,l and six errors:      1  3000     3     1   2.604E-11   6.062E-10   1.374E-10   3.537E-06   1.190E-09   4.860E-11
Case Z,mesh,n,l and six errors:      1  3000     3     2   6.144E-12   2.419E-10   4.210E-11   3.537E-06   3.026E-10   1.172E-11
Case Z,mesh,n,l and six errors:      1  4500     1     0   5.142E-12   1.943E-11   5.226E-06   1.572E-06   1.664E-11   1.341E-11
Case Z,mesh,n,l and six errors:      1  4500     2     0   5.229E-12   6.474E-11   1.848E-06   1.572E-06   1.072E-10   1.100E-11
Case Z,mesh,n,l and six errors:      1  4500     2     1   1.649E-12   3.214E-11   9.322E-12   1.572E-06   3.660E-11   3.243E-12
Case Z,mesh,n,l and six errors:      1  4500     3     0   1.229E-12   2.745E-10   1.006E-06   1.572E-06   6.493E-10   4.669E-11
Case Z,mesh,n,l and six errors:      1  4500     3     1   5.143E-12   1.202E-10   2.722E-11   1.572E-06   2.369E-10   9.819E-12
Case Z,mesh,n,l and six errors:      1  4500     3     2   1.217E-12   4.792E-11   9.130E-12   1.572E-06   6.031E-11   2.359E-12
Case Z,mesh,n,l and six errors:      2  3000     1     0   2.171E-11   9.504E-11   1.204E-05   3.537E-06   7.696E-11   5.373E-11
Case Z,mesh,n,l and six errors:      2  3000     2     0   2.637E-11   3.242E-10   4.257E-06   3.537E-06   5.302E-10   5.208E-11
Case Z,mesh,n,l and six errors:      2  3000     2     1   8.325E-12   1.624E-10   4.719E-11   3.537E-06   1.841E-10   1.621E-11
Case Z,mesh,n,l and six errors:      2  3000     3     0   4.765E-11   9.192E-10   2.317E-06   3.537E-06   2.115E-09   9.095E-11
Case Z,mesh,n,l and six errors:      2  3000     3     1   2.604E-11   6.062E-10   1.374E-10   3.537E-06   1.190E-09   4.860E-11
Case Z,mesh,n,l and six errors:      2  3000     3     2   6.144E-12   2.419E-10   4.210E-11   3.537E-06   3.026E-10   1.172E-11
Case Z,mesh,n,l and six errors:      2  4500     1     0   5.142E-12   1.943E-11   5.226E-06   1.572E-06   1.664E-11   1.341E-11
Case Z,mesh,n,l and six errors:      2  4500     2     0   5.229E-12   6.474E-11   1.848E-06   1.572E-06   1.072E-10   1.100E-11
Case Z,mesh,n,l and six errors:      2  4500     2     1   1.649E-12   3.214E-11   9.322E-12   1.572E-06   3.660E-11   3.243E-12
Case Z,mesh,n,l and six errors:      2  4500     3     0   1.229E-12   2.745E-10   1.006E-06   1.572E-06   6.493E-10   4.669E-11
Case Z,mesh,n,l and six errors:      2  4500     3     1   5.143E-12   1.202E-10   2.722E-11   1.572E-06   2.369E-10   9.819E-12
Case Z,mesh,n,l and six errors:      2  4500     3     2   1.217E-12   4.792E-11   9.130E-12   1.572E-06   6.031E-11   2.359E-12
Case Z,mesh,n,l and six errors:      4  3000     1     0   2.171E-11   9.504E-11   1.204E-05   3.537E-06   7.696E-11   5.373E-11
Case Z,mesh,n,l and six errors:      4  3000     2     0   2.637E-11   3.242E-10   4.257E-06   3.537E-06   5.302E-10   5.208E-11
Case Z,mesh,n,l and six errors:      4  3000     2     1   8.325E-12   1.624E-10   4.719E-11   3.537E-06   1.841E-10   1.621E-11
Case Z,mesh,n,l and six errors:      4  3000     3     0   4.765E-11   9.192E-10   2.317E-06   3.537E-06   2.115E-09   9.095E-11
Case Z,mesh,n,l and six errors:      4  3000     3     1   2.604E-11   6.062E-10   1.374E-10   3.537E-06   1.190E-09   4.860E-11
Case Z,mesh,n,l and six errors:      4  3000     3     2   6.144E-12   2.419E-10   4.210E-11   3.537E-06   3.026E-10   1.172E-11
Case Z,mesh,n,l and six errors:      4  4500     1     0   5.142E-12   1.943E-11   5.226E-06   1.572E-06   1.664E-11   1.341E-11
Case Z,mesh,n,l and six errors:      4  4500     2     0   5.229E-12   6.474E-11   1.848E-06   1.572E-06   1.072E-10   1.100E-11
Case Z,mesh,n,l and six errors:      4  4500     2     1   1.649E-12   3.214E-11   9.322E-12   1.572E-06   3.660E-11   3.243E-12
Case Z,mesh,n,l and six errors:      4  4500     3     0   1.229E-12   2.745E-10   1.006E-06   1.572E-06   6.493E-10   4.669E-11
Case Z,mesh,n,l and six errors:      4  4500     3     1   5.143E-12   1.202E-10   2.722E-11   1.572E-06   2.369E-10   9.819E-12
Case Z,mesh,n,l and six errors:      4  4500     3     2   1.217E-12   4.792E-11   9.130E-12   1.572E-06   6.031E-11   2.359E-12
Radial eigenproblems: 36; P references and Q references each: 135036
Max energy, P, Q, normalization, radius and inverse-radius errors:    4.76529E-11   9.19163E-10   1.20398E-05   3.53696E-06   2.11486E-09   9.09494E-11
Nonrelativistic Coulomb states only; Dirac, general potentials and self-consistent DFT unverified.
PASS dftatom-hydrogen-reference
```

### athena-dense-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=athena&example=gams-athena-dense-reference) / [Driver source](../fpm_catalog/gams-drivers/athena-dense-reference.f90) / [Pinned procedure](https://github.com/nedtaylor/athena/blob/4b81aeac07113628c2c9a476648d5ac2a91b7c91/src/athena/athena_full_layer.f90#L839) / [Author test](https://github.com/nedtaylor/athena/blob/4b81aeac07113628c2c9a476648d5ac2a91b7c91/test/test_full_layer.f90)

```text
Fixed dense layers: 192; forward calls: 2304
Independent output references: 4928; exact replay entries: 448
Maximum normalized output error against real64 scalar oracle:    5.77239E-08
Four activations, bias on/off, rectangular weights, zero/basis/mixed inputs and repeated forward checked.
Inference only; training, automatic derivatives, batch inference and approximation quality unverified.
PASS athena-dense-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers dftatom-hydrogen-reference athena-dense-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
