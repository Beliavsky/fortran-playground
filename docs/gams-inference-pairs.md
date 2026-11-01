# Checked Fiats and ennuf fixed-network inference

Both K drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-inference-pairs-validation.json) retains pins, source hashes and complete output. GAMS categories are not exhausted. K is the maintained broad function-approximation class; these examples verify fixed network evaluation, not training or approximation quality on a scientific dataset.

## Fiats irregular multilayer networks (K)

The independent consumer constructs four architectures [1,2,1], [2,3,2], [3,2,1] and [2,4,3,2]. These have one or two hidden layers and changing widths, so active input/output slices differ between layers. Combining them with ReLU, sigmoid and swish activations, two parameter patterns and zero/nonzero biases gives 48 fixed networks. The pinned Fiats 0.12.0 package and its compatible Julienne/Assert dependencies are reused; this driver does not change the historical version offered.

At connection l, W_ij=(2*i-3*j+l)/8 and b_i=(i-2*l)/8 in the dyadic pattern, while denominators are 7 and 9 in the non-dyadic pattern. The zero-bias setting zeroes active biases. Native coefficients have decimal precision 6 (real32 in this image); the oracle widens the actual stored coefficients to real64. Padded matrix/bias slots are filled with sentinel 17 and must not affect the result. Tensor input/output ranges are left at their default [0,1] maps, which act as identity maps here, including the selected inputs outside that interval.

Each network evaluates 11 inputs: zero, every coordinate basis vector, then deterministic mixed signed dyadic vectors x_j=(modulo(sample*(2*j+1),17)-8)/8. A scalar real64 oracle propagates the active widths connection by connection, evaluating ReLU as max(0,z), sigmoid with a sign-stable exponential formula, and swish as z*sigmoid(z). The activation is applied at the output layer too, as required by this pinned API; a linear output is not assumed. No MATMUL or another network implementation supplies the reference.

All 792 output entries must be finite with the requested output width and absolute discrepancy divided by 1+abs(reference) <=5e-6. After the other inputs, each network receives zero again and all 72 replay entries must match the first result exactly. There are 576 total inference calls; the largest normalized oracle discrepancy was 3.46692e-8. Nonidentity range maps, model-file round trips, the other Fiats activations, training, derivatives, parallel scaling and dataset approximation quality remain unverified.

## ennuf generic dense/activation pipelines (K)

The independent consumer directly calls the cached Fortran neural_net_mod dense and activation_function routines. The same four width architectures are composed with ReLU, leaky ReLU (alpha=0.125), sigmoid, tanh and softmax. Optional biases are present or absent, parameter patterns are dyadic or non-dyadic, and channel counts are [1,2,5]. Channel rows are independent feature vectors transformed by shared weights, rather than summed together. The routines execute in Fortran; no Python inference or external model conversion runs in the sandbox.

Weight and bias formulas match the Fiats suite, rounded first to native real32. Each configuration has 11 inputs: zero, coordinate bases scaled in channel c by c/(channels+1), then mixed inputs x_cj=(modulo(sample*(2*j+1)+3*c,17)-8)/8. There are 2,640 pipeline batches, each with two or three dense/activation stages, giving 5,940 calls to each primitive. Unlike many network conventions, the selected activation also follows the final dense stage in these explicit consumer pipelines.

A real64 scalar oracle evaluates each channel and layer from the actual stored coefficients. It uses elementary pointwise activation formulas; its tanh uses the logistic identity, and its softmax subtracts the row maximum before exponentiation. This stabilization is in the reference, not a patch to the library implementation, which uses unshifted exponentials. Selected logits are moderate; extreme-logit stability is not checked. The reference retains real64 intermediates across layers so that native real32 rounding differences accumulate in the comparison.

All 35,200 layer-output entries, including 10,560 final-layer entries, must be finite and agree within normalized discrepancy 5e-6. Softmax outputs must be positive and each channel row must sum to one within 2e-6. The largest normalized scalar-reference discrepancy was 5.25551e-8 and the largest softmax sum error 1.19209e-7. Channel mixing, wrong optional-bias handling or width ordering would change these explicit per-channel references.

## ennuf cached generated model

The consumer also calls the existing ennuf_example_mod model, whose audited [generated asset](../fpm_catalog/generated/ennuf-2555a7f1560ef3cb7cf707221fa5bb1b5334ee6f.json) is already part of the package build. Its closed-form scalar function is y=2*max(x1+2*x2+0.5,0)-3*max(-x1+0.5*x2-0.25,0)+1. Hidden units are ReLU, and the final output is linear. This is a fixed illustrative model, not a trained scientific surrogate.

Both coordinates independently range over [-2,-1,-0.5,-0.25,0,0.25,0.5,1,2], giving 81 generated model evaluations. The grid includes positive/negative inputs, exact hidden-unit threshold values and all four combinations of active/inactive ReLU units. Region counts are [21,29,14,17] in order neither active, first only, second only, both active; exact-zero preactivations count as inactive. Each finite output is checked against the closed form using the same normalized 5e-6 tolerance. The observed discrepancy was zero for this dyadic grid.

The generated asset hash remains 6f7fc6b3b9943943fd294017179004dfc37567dfdd637aabed2d0908dbdb9a7b, matching the package recipe. No new model generation or library rebuild is required. External TensorFlow/PyTorch conversion, arbitrary generated models, convolution/pooling/skip layers, extreme softmax logits, training and dataset approximation quality remain unverified.

## Sources, licenses and actual output

Pinned APIs, implementations and author examples were reviewed before writing these independent API consumers. No upstream implementation or example bodies are copied. The drivers have their own MIT notice; the Berkeley Lab Fiats terms and ennuf BSD/Crown notices remain separate and unchanged. Loading a driver does not submit a job.

### fiats-inference-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fiats&example=gams-fiats-inference-reference) / [Driver source](../fpm_catalog/gams-drivers/fiats-inference-reference.f90) / [Pinned procedure](https://github.com/BerkeleyLab/fiats/blob/7d564b86389460555d6f7d9b7a6b5198588af9df/src/inference_engine/inference_engine_m_.f90#L1) / [Author test](https://github.com/BerkeleyLab/fiats/blob/7d564b86389460555d6f7d9b7a6b5198588af9df/example/write-read-infer.F90)

```text
Fiats fixed networks: 48; inference calls: 576
Independent output references: 792; exact replay entries: 72
Native decimal precision: 6
Maximum normalized multilayer error:    3.46692E-08
ReLU/sigmoid/swish apply to every connection, including output; default ranges are identity.
Fixed inference only; training, derivatives, model I/O and nonidentity ranges unverified.
PASS fiats-inference-reference
```

### ennuf-inference-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=ennuf&example=gams-ennuf-inference-reference) / [Driver source](../fpm_catalog/gams-drivers/ennuf-inference-reference.f90) / [Pinned procedure](https://github.com/MetOffice/ennuf/blob/2555a7f1560ef3cb7cf707221fa5bb1b5334ee6f/src/ennuf/_internal/fortran/neural_net_mod.f90#L1) / [Author test](https://github.com/MetOffice/ennuf/blob/2555a7f1560ef3cb7cf707221fa5bb1b5334ee6f/test/testennuf/example_models/pytorch_simple_mlp.py)

```text
Ennuf pipeline batches: 2640; dense and activation calls each: 5940
All-stage reference entries: 35200; final-layer entries included: 10560
Generated-model evaluations: 81; four ReLU-region counts:     21    29    14    17
Max normalized pipeline error, softmax sum error and generated-model error:    5.25551E-08   1.19209E-07   0.00000E+00
Fixed REAL32 inference only; conversion, convolution, training and extreme softmax logits unverified.
PASS ennuf-inference-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fiats-inference-reference ennuf-inference-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
