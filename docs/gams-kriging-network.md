# Checked kriging and neural-network drivers

These L13 and K drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-kriging-network-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Ordinary kriging: GSLIB (L13)

Two observations at x=0 and x=2 have values 1 and 3. Seven query positions `[-1,0,0.5,1,1.5,2,3]` exercise interpolation and extrapolation with three covariance models: spherical, exponential and Gaussian. Nugget is zero, sill is one and the model parameter is 3. For separation h, the independent references are `max(0,1-1.5*t+0.5*t**3)` with t=h/3 (zero for t>=1), `exp(-h)` and `exp(-h*h/3)`. These formulas follow the implemented parameter convention, rather than assuming a common practical-range definition.

The covariance routine cova3 uses **real32**, while ksol solves the packed symmetric system in **real64**. Six standalone distances per model and all query covariances must agree with analytic formulas within 2e-7. For r=C(2), c1=C(abs(x)) and c2=C(abs(x-2)), the independent solution is `w1=(1+(c1-c2)/(1-r))/2`, `w2=1-w1`, `mu=c1-w1-r*w2`. All 21 solves must agree with these weights for rounded covariances and have an independently accumulated system residual within 1e-11.

Against fully analytic covariances, weight errors must stay within 5e-7 and prediction/variance errors within 1e-6. Predictions are `w1+3*w2`; variances are `1-w1*c1-w2*c2-mu`. Finite results, nonnegative variances (tolerance 1e-11), unit weight sums, constant-field reproduction, endpoint interpolation and midpoint/reflection symmetry are required. This is an independent API consumer; no matching author driver is recorded. GSLIB source-evidence hashes use UTF-8/LF normalization. Anisotropy, nugget effects, nested structures, large/singular systems and robust pivoting are not verified. This L13 example does not verify the separate E2 mapping.

## Known dense-network evaluation: FKB (K)

An independently specified 2-input, 3-hidden-unit, 2-output network uses ReLU hidden activation and linear outputs. Fixed small dyadic weights and biases make independent scalar forward calculations straightforward. The full integer input grid [-2,2] squared supplies 25 cases, including negative, positive and exactly zero hidden preactivations.

The driver loads its model, saves it and reloads a second network. Both versions must report the expected dimensions and match independent scalar calculations with finite outputs within 1e-12: 50 predictions and 100 scalar outputs. The two temporary model files are removed on success. Author loading/saving tests were reviewed for the file format. This broad K demonstration verifies forward evaluation and serialization, not training or approximation quality. Gradients, dropout, batch normalization, Keras conversion and parallel performance are outside its verified scope.

## Checked links and actual output

These independently written drivers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### gslib-kriging-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=gslib&example=gams-gslib-kriging-reference) / [Driver source](../fpm_catalog/gams-drivers/gslib-kriging-reference.f90) / [Pinned procedure](https://github.com/exepulveda/gslib2.0/blob/5c021000eb3da8703ced3ee9be145d6c0ecb2608/src/legacy/gslib/cova3.f90#L1)

```text
Model=1 x= -1.0 estimate=  1.3913044 variance=  0.8977456
Model=1 x=  0.0 estimate=  1.0000000 variance=  0.0000000
Model=1 x=  0.5 estimate=  1.4836957 variance=  0.3957201
Model=1 x=  1.0 estimate=  2.0000000 variance=  0.5370370
Model=1 x=  1.5 estimate=  2.5163043 variance=  0.3957201
Model=1 x=  2.0 estimate=  3.0000000 variance=  0.0000000
Model=1 x=  3.0 estimate=  2.6086956 variance=  0.8977456
Model=2 x= -1.0 estimate=  1.6321205 variance=  1.0914913
Model=2 x=  0.0 estimate=  1.0000000 variance=  0.0000000
Model=2 x=  0.5 estimate=  1.5565906 variance=  0.6530051
Model=2 x=  1.0 estimate=  2.0000000 variance=  0.8319087
Model=2 x=  1.5 estimate=  2.4434094 variance=  0.6530051
Model=2 x=  2.0 estimate=  3.0000000 variance=  0.0000000
Model=2 x=  3.0 estimate=  2.3678795 variance=  1.0914913
Model=3 x= -1.0 estimate=  1.0945931 variance=  0.5636428
Model=3 x=  0.0 estimate=  1.0000000 variance=  0.0000000
Model=3 x=  0.5 estimate=  1.3920748 variance=  0.1033103
Model=3 x=  1.0 estimate=  2.0000000 variance=  0.1987360
Model=3 x=  1.5 estimate=  2.6079252 variance=  0.1033103
Model=3 x=  2.0 estimate=  3.0000000 variance=  0.0000000
Model=3 x=  3.0 estimate=  2.9054069 variance=  0.5636428
Three covariance kernels and 21 two-observation ordinary kriging systems checked.
PASS gslib-kriging-reference
```

### fkb-network-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fkb&example=gams-fkb-network-reference) / [Driver source](../fpm_catalog/gams-drivers/fkb-network-reference.f90) / [Pinned procedure](https://github.com/scientific-computing/FKB/blob/a1c97d4d66431df87662b59fe8e8a24feaf28a3a/src/lib/mod_network.F90#L163) / [Author example/test](https://github.com/scientific-computing/FKB/blob/a1c97d4d66431df87662b59fe8e8a24feaf28a3a/src/tests/test_keras.F90)

```text
Input= -2 -2 outputs=    -3.00000     1.50000
Input= -2 -1 outputs=    -5.50000     2.18750
Input= -2  0 outputs=    -6.50000     2.50000
Input= -2  1 outputs=    -6.87500     3.06250
Input= -2  2 outputs=    -6.62500     5.50000
Input= -1 -2 outputs=     0.00000     0.50000
Input= -1 -1 outputs=    -2.50000     1.18750
Input= -1  0 outputs=    -4.50000     1.75000
Input= -1  1 outputs=    -4.62500     3.06250
Input= -1  2 outputs=    -4.37500     5.50000
Input=  0 -2 outputs=     3.00000    -0.50000
Input=  0 -1 outputs=     0.50000     0.18750
Input=  0  0 outputs=    -2.00000     0.87500
Input=  0  1 outputs=    -2.37500     3.06250
Input=  0  2 outputs=    -2.12500     5.50000
Input=  1 -2 outputs=     5.00000    -1.12500
Input=  1 -1 outputs=     3.00000    -0.62500
Input=  1  0 outputs=     1.12500     0.25000
Input=  1  1 outputs=    -0.12500     3.06250
Input=  1  2 outputs=     0.12500     5.50000
Input=  2 -2 outputs=     6.00000    -1.37500
Input=  2 -1 outputs=     4.00000    -0.87500
Input=  2  0 outputs=     2.37500     0.75000
Input=  2  1 outputs=     1.12500     3.50000
Input=  2  2 outputs=     1.37500     5.87500
25 two-output predictions checked against scalar references for original and saved/reloaded networks.
PASS fkb-network-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers gslib-kriging-reference fkb-network-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
