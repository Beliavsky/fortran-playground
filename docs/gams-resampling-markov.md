# Checked GAMS resampling and Markov-model drivers

These L4 and M drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only their main programs and executables were compiled. GAMS categories are not exhausted.

## Jackknife uncertainty: FJsample (L4)

The driver checks five real datasets of sizes 2, 6, 4, 6 and 8, including constant values, negative values and a symmetric zero-mean sample. Each full-sample mean and leave-one-out mean returned by `Complement` is compared with separately enumerated scalar sums. For the sample mean, `jackError` must return `sqrt(s^2/n)`, where `s^2` is the unbiased sample variance, and zero bias.

A second estimator squares the full and resampled means. Its uncertainty is checked against the direct leave-one-out jackknife sum, and its returned bias against the analytic identity `-s^2/(n*(n-1))`. All values must be finite; maximum absolute errors must be at most `1e-11`. This nonlinear check makes the bias convention observable: the package returns **full estimate minus mean resampled estimate**, without an `n-1` multiplier. Conventional estimated jackknife bias would be `-(n-1)*package_bias`; a conventionally bias-corrected estimate would be `full_estimate+(n-1)*package_bias`. The driver checks the documented package result rather than relabeling it as that conventional bias.

The pinned author main was reviewed for the public calling sequence. Bootstrap, complex data, higher-order complements, general estimator accuracy and statistical coverage are not verified. L4 remains broad pending a suitable finer taxonomy match.

## Stationary Markov models: econ-toolchain (M)

Three two-state chains use transition pairs `(a,b)=(0.1,0.2)`, `(0.7,0.6)` and `(0.02,0.03)`. Their exact stationary probabilities are `[b,a]/(a+b)`. A three-state rank-one chain must recover `[0.1,0.3,0.6]`. The iteration must report convergence and return finite nonnegative probabilities, unit total probability and a stationary equation residual at most `1e-11`.

`tauchen` discretizes three Gaussian AR(1) processes on 31 nodes spanning three stationary standard deviations. The tested `(mean,rho,innovation_sigma)` triples are `(0,0,0.2)`, `(1.5,0.8,0.1)` and `(-0.7,-0.5,0.3)`. Grid locations are checked against the specified mean and stationary variance. Each of 2883 transition probabilities is compared with an independent conditional normal CDF integral over midpoint cells, with infinite endpoint tails. The reference uses intrinsic `erf`; the package uses `erfc`. This checks the discretization formula, indexing and tails, rather than independently certifying the compiler's special functions.

Rows must be nonnegative and sum to one. The driver explicitly transposes the row-stochastic Tauchen matrix for the column-stochastic `markov_steady_state` API, checks stationary residuals and the symmetric stationary mean, and compares the zero-correlation equilibrium with the independently computed identical row distribution. Every check uses an absolute tolerance of `1e-11`; the iteration tolerance is `1e-14` with a 10000-iteration limit. These deterministic tests do not verify random sampling, nonergodic chains, arbitrary-parameter convergence or the continuous process's full stationary distribution.

## Pinned evidence and actual output

The [verification report](gams-resampling-markov-validation.json) records source hashes and actual sandbox output. These independent API consumers have their own MIT notice; upstream package terms remain separate. Loading a link selects the checked driver without submitting a job.

### econ-markov-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=econ-toolchain&example=gams-econ-markov-reference) / [Driver source](../fpm_catalog/gams-drivers/econ-markov-reference.f90) / [Pinned procedure](https://github.com/renatomatz/econ-toolchain/blob/301d1659ba3d34973195985c552ca6fcfe2d9f29/src/dist.f90#L62)

[Pinned author example/test](https://github.com/renatomatz/econ-toolchain/blob/301d1659ba3d34973195985c552ca6fcfe2d9f29/test/markov_test.f90)

[Pinned author example/test](https://github.com/renatomatz/econ-toolchain/blob/301d1659ba3d34973195985c552ca6fcfe2d9f29/test/tauchen_test.f90)

```text
a,b=  0.100  0.200 equilibrium=  0.666667  0.333333
a,b=  0.700  0.600 equilibrium=  0.461538  0.538462
a,b=  0.020  0.030 equilibrium=  0.600000  0.400000
Three-state reset equilibrium:  0.100000  0.300000  0.600000
AR rho= 0.00 mean= -0.00 maximum probability error=  1.11E-16
AR rho= 0.80 mean=  1.50 maximum probability error=  1.33E-15
AR rho=-0.50 mean= -0.70 maximum probability error=  2.22E-16
PASS econ-markov-reference
```

### fjsample-jackknife-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fjsample&example=gams-fjsample-jackknife-reference) / [Driver source](../fpm_catalog/gams-drivers/fjsample-jackknife-reference.f90) / [Pinned procedure](https://github.com/RJaBi/FJsample/blob/8563d2653d1a9d80a355b2064f4b153559698915/src/jack.f90#L21)

[Pinned author example/test](https://github.com/RJaBi/FJsample/blob/8563d2653d1a9d80a355b2064f4b153559698915/app/main.f90)

```text
n= 2 mean=   2.0000 standard error=  1.000000
  squared mean standard error=   4.000000 package bias=  -1.000000
n= 6 mean=   5.0000 standard error=  1.414214
  squared mean standard error=  13.877752 package bias=  -0.400000
n= 4 mean=   7.0000 standard error=  0.000000
  squared mean standard error=   0.000000 package bias=   0.000000
n= 6 mean=  -9.0000 standard error=  2.828427
  squared mean standard error=  49.862531 package bias=  -1.600000
n= 8 mean=   0.0000 standard error=  1.035098
  squared mean standard error=   0.306632 package bias=  -0.153061
PASS fjsample-jackknife-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers econ-markov-reference fjsample-jackknife-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining classes without checked drivers.
