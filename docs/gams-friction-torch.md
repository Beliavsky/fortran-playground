# Checked LuGre state integration and FTorch tensor inference

Both independent consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox, reusing the existing package libraries and compiling only mains and executables. The [verification report](gams-friction-torch-validation.json) retains pins, source hashes and full output. GAMS categories are not exhausted.

## LuGre internal-state histories (I1)

This driver uses the public lugre_model%state and evaluate APIs and the cached diffeq runge_kutta_23 integrator. A new procedure record, friction-lugre-state, distinguishes them from the private friction_core internal_state_odes/internal_var_fit_fcn fitting callbacks. Those private callbacks and parameter fitting remain unverified; the separate Coulomb-fit failure is not fixed or hidden.

For fixed velocity v and normal load N, the model is z_prime=v-a*z, where a=abs(v)/g(v), and g(v)=N/stiffness*(mu_c+(mu_s-mu_c)/(1+(abs(v)/v_s)**shape)). The exact segment solution is z(t)=v/a+(z0-v/a)*exp(-a*t) when a>0. At rest, a=v=0 and z remains constant. The force reference is stiffness*z+damping*z_prime+viscous_damping*v. These closed-form expressions provide the state, derivative and force references without a second numerical integrator.

Four parameter sets indexed by p=1..4 use mu_s=0.5+p/16, mu_c=0.25+p/32, v_s=0.125, stiffness=8+p, damping=p/8, viscous_damping=p/16 and shape=p. Base loads are [2,5,11], initial bristle states [-1/16,0,1/16], and both velocity orientations are tested. Every history has velocities [0.125,-0.25,0,0.0625] (or their negatives), durations [0.25,0.125,0.375,0.5] and segment load multipliers [1,1.25,1.5,1.75]. States are continuous at segment boundaries, while velocities and loads change.

There are 72 histories, 288 integrated segments and 1,440 requested output times. Every numerical endpoint continues into the next segment, but the closed-form reference propagates its own exact endpoint, so numerical state errors are not reset by the oracle. At each output the driver checks the state, evaluates the model derivative at the exact reference state, and compares the force at the numerical state with the analytical force. Derivative checks are algebraic API checks; integration accuracy is established separately by the state histories.

The integrator uses relative/absolute tolerances 1e-11 and maximum step duration/8, with five requested times per segment. Returned times, dimensions, finiteness, callback use and initial-state immutability are checked. Normalized tolerances are 2e-8 for state, 2e-13 for derivative and 2e-7 for force. Observed maxima were 1.18833e-11, 4.33973e-17 and 1.13208e-10, respectively, with 80,598 integration callback evaluations. The force denominator is 1+abs(numerical force); state/derivative denominators use 1+abs(reference).

This is a prescribed-velocity, positive-load constitutive test, not a coupled mass/spring/contact simulation. Continuously varying velocity/load, zero normal force, model fitting and private fitting/interpolation callbacks remain unverified. The author LuGre example was reviewed for public API usage; its plotting and coupled-mechanics application are not copied.

## FTorch affine model and tensor layouts (K)

The consumer reuses the existing playground-owned 1,766-byte embedded TorchScript fixture as data. It computes the fixed elementwise function y=2*x+1. The model archive SHA256 is 13b09124005d3c931b04a5da83624973b3f78b231a579217932469ab8179077c, identical to the ordinary FTorch demo. It is written to a local sandbox file and loaded once; no download, Python inference, model conversion or new generation occurs during a run. The separate FTorch/LibTorch system-library footprint is unchanged.

Ten configurations cover REAL32 and REAL64 at rank 1 ([7]), rank 2 ([2,3]) and rank 3 ([2,3,4]). Rank 2 also uses permute_dims=[2,1] with a [3,2] output; rank 3 uses [2,3,1] with a [3,4,2] output. Permutations apply only to input tensors, so expected output indices are explicitly transposed/permuted rather than using two compensating layout changes. The driver checks input tensor rank, shape, stride and dtype against the requested Fortran layout.

Each configuration constructs input/output tensors once, updates the same Fortran input buffer in place for 12 batches and repeats the first batch as a thirteenth call. Signed input values are (modulo(sample*index_code,37)-18)/8, where index_code is i, i+7*j or i+7*j+11*k. Distinct axis weights make permutations observable. Output buffers are overwritten with a sentinel before every call, and input buffers must remain unchanged. All predictions must be finite and exactly match the independent scalar dyadic function; first/replay outputs must also match exactly.

All 130 forward calls and 1,742 scalar output references passed with zero discrepancy. This checks a fixed affine model, CPU tensor aliasing/layout and repeated inference. It does not verify a trained scientific model, nonlinear layers, gradients, training, GPU execution, arbitrary external archives or all supported ranks/dtypes. These limits are explicit even though the model is classified under broad K.

## Sources, licenses and output

Pinned interfaces, implementations and author examples were reviewed. The consumers are independently written and have their own MIT notice; the existing tiny model is reused as data, and upstream package notices remain unchanged. No upstream example or implementation body is copied. Loading a driver does not submit a job.

### friction-lugre-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=friction&example=gams-friction-lugre-reference) / [Driver source](../fpm_catalog/gams-drivers/friction-lugre-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/friction/blob/8e75dcac26f47417a439adfcbaa24834105d89fe/src/models/friction_lugre.f90#L161) / [Author test](https://github.com/jchristopherson/friction/blob/8e75dcac26f47417a439adfcbaa24834105d89fe/examples/lugre_example.f90)

```text
LuGre constant-velocity segments: 288; state/derivative/force references each: 1440
Numerical integration callback evaluations: 80598
Max normalized state, derivative and force errors:    1.18833E-11   4.33973E-17   1.13208E-10
72 histories; velocity reversals, rest, changing loads and nonzero initial bristle states.
Public LuGre state integration only; private fitting callbacks and parameter fitting unverified.
PASS friction-lugre-reference
```

### ftorch-affine-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=ftorch&example=gams-ftorch-affine-reference) / [Driver source](../fpm_catalog/gams-drivers/ftorch-affine-reference.f90) / [Pinned procedure](https://github.com/Cambridge-ICCS/FTorch/blob/b1b1bb3b9138642ac51d55608e7f3af9070c43f1/src/ftorch_model.f90#L1) / [Author test](https://github.com/Cambridge-ICCS/FTorch/blob/b1b1bb3b9138642ac51d55608e7f3af9070c43f1/examples/02_SimpleNet/simplenet_infer_fortran.f90)

```text
10 tensor configurations: REAL32/REAL64, ranks 1/2/3, identity and asymmetric axis permutations.
CPU forward calls: 130; exact scalar output references: 1742
Maximum absolute affine prediction error:    0.00000E+00
In-place input updates and exact replay; input rank/shape/stride/dtype and input immutability checked.
Existing y=2*x+1 fixture only; nonlinear networks, training, gradients and GPU execution unverified.
PASS ftorch-affine-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers friction-lugre-reference ftorch-affine-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
