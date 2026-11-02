# Ten checked ordering and Runge-Kutta drivers

Ten independent consumers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the hosted sandbox. Existing ORDERPACK and rklib libraries were reused; only main.f90 and playground-main were compiled. The [verification report](gams-ordering-runge-ten-validation.json) records normalized UTF-8/LF source hashes, exact pins, timings and full output. GAMS coverage remains unfinished.

## ORDERPACK: six distinct operations

Each driver tests 325 finite REAL64 data sets: sizes 1..65, each with five deterministic patterns (unsorted duplicate-rich data, sorted repeated values, reverse repeated values, constant values, and distinct values). All are exact dyadics. The independent reference is a local insertion sort, a direct first-occurrence scan or direct counting; no second library routine supplies the oracle. Every applicable partial prefix is tested. Empty arrays, NaNs, infinities, integer and character overloads are excluded.

| Operation | GAMS | Independent checks |
| --- | --- | --- |
| Partial sort (psort) | N6a2b | Every requested prefix equals the reference prefix; the complete multiset is preserved |
| Partial ranks (prank) | N6a1b | Every prefix contains valid, distinct indices selecting the reference values; tie stability is not assumed |
| Stable unique (unique) | L2c | First-occurrence scan checks both the distinct count and retained order; undocumented tail entries are ignored |
| Multiplicities (occurrences) | L1a1d | Every count agrees with direct equality counting in the original data |
| Inverse unique ranks | N6a1b | Each original entry receives its ascending dense rank among distinct values; the public alias rank_decreasing does not mean descending sorting |
| Median conventions | L1a1a | median averages the central pair; medianval and medianloc select the lower middle for even sizes |

REAL64 median comparisons are exact here because all central values and their averages are dyadic and comfortably representable. These tests establish the demonstrated conventions and bounded data cases, not performance, asymptotic complexity or robustness to nonfinite inputs.

## Four Runge-Kutta methods (I1a1a)

The explicit midpoint (order 2), rk3 (order 3), Spiteri-Ruuth rkssp54 (order 4) and rk5 (order 5) drivers each integrate a five-state nonstiff system. Closed forms are exp(-t), cos(t), -sin(t), 1/(1+exp(-t)), and t*t+1/4. These exercise exponential decay, a coupled oscillator, nonlinear logistic growth and explicitly time-dependent polynomial forcing. Module callbacks use the direct solver objects.

Each method is checked at ten checkpoints on [0,2] for h=0.1, 0.05 and 0.025. Every state must be finite, the status must succeed, decay must stay positive and logistic growth must stay in (0,1). The maximum absolute state error must be <=2*h**p at every checkpoint. The time-dependent polynomial state has a separate 1e-11 absolute tolerance. RHS callback counts must be positive.

A separate convergence assertion compares the maximum checkpoint error between successive step sizes: each ratio must lie in [0.7*2**p,1.4*2**p]. Actual errors, ratios and RHS counts are printed. These are accuracy checks for this smooth bounded system, not a speed comparison, an SSP-property or stability-region proof, nor verification of adaptive control, backward integration or stiff systems.

## Retained unsuccessful probes

The first median consumer treated medianloc as a function; correcting it to call medianloc(x,loc) resolved that consumer compile error without changing numerical assertions. The combined order-statistics probe found an actual orderloc mismatch for [-1.25,-2.75,1.5,0]: the third ordered value should be 0, but the routine returned index 3/value 1.5. Original and diagnostic probes, normalized hashes, pins and full outputs are [retained](gams-candidates/orderpack-statistics/README.md). Its procedure record has no checked driver; the other two order-statistic APIs were not reached for that failing case. No upstream source or assertion was changed to promote the failed routine. Inverse unique ranks are a separate verified replacement.

## Provenance and scope

Pinned public APIs and implementation files, ORDERPACK author tests and rklib author order tests were reviewed. Consumers are independently authored MIT examples; no upstream numerical or test body was copied or patched. GAMS classifications follow the [Netlib taxonomy](https://netlib.org/misc/gams.html): active/passive real internal sorting, data subsets, frequency, location and one-step ODE methods. Loading a driver does not submit a job. The [coverage report](gams-coverage.md) tracks remaining work.

## Driver details

### orderpack-partial-sort-reference (N6a2b)

Independent API consumer. 325 finite REAL64 data sets, n=1..65 and five patterns: repeated unsorted, sorted, reverse, constant and distinct dyadics. All partial sorted prefixes and complete multiset preservation checked. NaNs, infinities, empty inputs and other kinds excluded.

### orderpack-partial-ranks-reference (N6a1b)

Independent API consumer. 325 finite REAL64 data sets, n=1..65 and five patterns: repeated unsorted, sorted, reverse, constant and distinct dyadics. Every requested prefix: valid distinct indices and independently sorted values; tie stability not required. NaNs, infinities, empty inputs and other kinds excluded.

### orderpack-stable-unique-reference (L2c)

Independent API consumer. 325 finite REAL64 data sets, n=1..65 and five patterns: repeated unsorted, sorted, reverse, constant and distinct dyadics. Stable duplicate removal compared with a first-occurrence scan; only the documented first nu entries are checked. NaNs, infinities, empty inputs and other kinds excluded.

### orderpack-multiplicities-reference (L1a1d)

Independent API consumer. 325 finite REAL64 data sets, n=1..65 and five patterns: repeated unsorted, sorted, reverse, constant and distinct dyadics. Per-element multiplicities compared with independent direct counting. NaNs, infinities, empty inputs and other kinds excluded.

### orderpack-inverse-unique-ranks-reference (N6a1b)

Independent API consumer. 325 finite REAL64 data sets n=1..65 and five patterns. Despite its public alias, rank_decreasing maps each original entry to its ascending dense rank among distinct values; direct counting of distinct smaller values independently verifies every rank, including ties. No descending-sort or stable-permutation claim.

### orderpack-median-conventions-reference (L1a1a)

Independent API consumer. 325 finite REAL64 data sets, n=1..65 and five patterns: repeated unsorted, sorted, reverse, constant and distinct dyadics. Arithmetic central-pair median versus lower-middle medianval/medianloc conventions; odd and even sizes checked. NaNs, infinities, empty inputs and other kinds excluded.

### rklib-midpoint-exact-ivp-reference (I1a1a)

Independent API consumer. Fixed-step midpoint method (order 2) on five REAL64 states: exponential decay, harmonic oscillator pair, nonlinear logistic and explicitly time-dependent polynomial forcing. Ten checkpoints on [0,2] for each of h=0.1,0.05,0.025, with exact solutions, status, finite/bounded states and two expected step-halving ratios. Nonstiff smooth system only; not an SSP, stability-region, adaptive, backward-integration or performance claim.

### rklib-rk3-exact-ivp-reference (I1a1a)

Independent API consumer. Fixed-step rk3 method (order 3) on five REAL64 states: exponential decay, harmonic oscillator pair, nonlinear logistic and explicitly time-dependent polynomial forcing. Ten checkpoints on [0,2] for each of h=0.1,0.05,0.025, with exact solutions, status, finite/bounded states and two expected step-halving ratios. Nonstiff smooth system only; not an SSP, stability-region, adaptive, backward-integration or performance claim.

### rklib-rkssp54-exact-ivp-reference (I1a1a)

Independent API consumer. Fixed-step rkssp54 method (order 4) on five REAL64 states: exponential decay, harmonic oscillator pair, nonlinear logistic and explicitly time-dependent polynomial forcing. Ten checkpoints on [0,2] for each of h=0.1,0.05,0.025, with exact solutions, status, finite/bounded states and two expected step-halving ratios. Nonstiff smooth system only; not an SSP, stability-region, adaptive, backward-integration or performance claim.

### rklib-rk5-exact-ivp-reference (I1a1a)

Independent API consumer. Fixed-step rk5 method (order 5) on five REAL64 states: exponential decay, harmonic oscillator pair, nonlinear logistic and explicitly time-dependent polynomial forcing. Ten checkpoints on [0,2] for each of h=0.1,0.05,0.025, with exact solutions, status, finite/bounded states and two expected step-halving ratios. Nonstiff smooth system only; not an SSP, stability-region, adaptive, backward-integration or performance claim.

## Provenance and actual output

### orderpack-partial-sort-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=orderpack&example=gams-orderpack-partial-sort-reference) / [Driver source](../fpm_catalog/gams-drivers/orderpack-partial-sort-reference.f90) / [Pinned procedure](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/src/M_orderpack.f90#L1) / [Author test](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/test/test_suite_M_orderpack.f90)

```text
Checked finite REAL64 data sets: 325
All partial sorted prefixes and complete multiset preservation checked.
PASS orderpack-partial-sort-reference
```

### orderpack-partial-ranks-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=orderpack&example=gams-orderpack-partial-ranks-reference) / [Driver source](../fpm_catalog/gams-drivers/orderpack-partial-ranks-reference.f90) / [Pinned procedure](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/src/M_orderpack.f90#L1) / [Author test](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/test/test_suite_M_orderpack.f90)

```text
Checked finite REAL64 data sets: 325
Every requested prefix: valid distinct indices and independently sorted values; tie stability not required.
PASS orderpack-partial-ranks-reference
```

### orderpack-stable-unique-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=orderpack&example=gams-orderpack-stable-unique-reference) / [Driver source](../fpm_catalog/gams-drivers/orderpack-stable-unique-reference.f90) / [Pinned procedure](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/src/M_orderpack.f90#L1) / [Author test](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/test/test_suite_M_orderpack.f90)

```text
Checked finite REAL64 data sets: 325
Stable duplicate removal compared with a first-occurrence scan; only the documented first nu entries are checked.
PASS orderpack-stable-unique-reference
```

### orderpack-multiplicities-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=orderpack&example=gams-orderpack-multiplicities-reference) / [Driver source](../fpm_catalog/gams-drivers/orderpack-multiplicities-reference.f90) / [Pinned procedure](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/src/M_orderpack.f90#L1) / [Author test](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/test/test_suite_M_orderpack.f90)

```text
Checked finite REAL64 data sets: 325
Per-element multiplicities compared with independent direct counting.
PASS orderpack-multiplicities-reference
```

### orderpack-inverse-unique-ranks-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=orderpack&example=gams-orderpack-inverse-unique-ranks-reference) / [Driver source](../fpm_catalog/gams-drivers/orderpack-inverse-unique-ranks-reference.f90) / [Pinned procedure](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/src/M_orderpack.f90#L11) / [Author test](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/test/test_suite_M_orderpack.f90)

```text
Checked finite REAL64 data sets: 325
Ascending dense ranks among distinct values checked, preserving original positions.
PASS orderpack-inverse-unique-ranks-reference
```

### orderpack-median-conventions-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=orderpack&example=gams-orderpack-median-conventions-reference) / [Driver source](../fpm_catalog/gams-drivers/orderpack-median-conventions-reference.f90) / [Pinned procedure](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/src/M_orderpack.f90#L1) / [Author test](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/test/test_suite_M_orderpack.f90)

```text
Checked finite REAL64 data sets: 325
Arithmetic central-pair median versus lower-middle medianval/medianloc conventions; odd and even sizes checked.
PASS orderpack-median-conventions-reference
```

### rklib-midpoint-exact-ivp-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rklib&example=gams-rklib-midpoint-exact-ivp-reference) / [Driver source](../fpm_catalog/gams-drivers/rklib-midpoint-exact-ivp-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/src/rklib_fixed_classes.inc#L10) / [Author test](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/test/rk_test_order.F90)

```text
Step  0.1000: maximum state error   3.1244E-03, RHS calls 42
Step  0.0500: maximum state error   7.7006E-04, RHS calls 82
Step  0.0250: maximum state error   1.9102E-04, RHS calls 172
Step-halving error ratio:      4.05729
Step-halving error ratio:      4.03135
Decay, oscillator, nonlinear logistic and nonautonomous polynomial states checked.
PASS rklib-midpoint-exact-ivp-reference
```

### rklib-rk3-exact-ivp-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rklib&example=gams-rklib-rk3-exact-ivp-reference) / [Driver source](../fpm_catalog/gams-drivers/rklib-rk3-exact-ivp-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/src/rklib_fixed_classes.inc#L31) / [Author test](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/test/rk_test_order.F90)

```text
Step  0.1000: maximum state error   7.8290E-05, RHS calls 63
Step  0.0500: maximum state error   9.6372E-06, RHS calls 123
Step  0.0250: maximum state error   1.1946E-06, RHS calls 258
Step-halving error ratio:      8.12371
Step-halving error ratio:      8.06755
Decay, oscillator, nonlinear logistic and nonautonomous polynomial states checked.
PASS rklib-rk3-exact-ivp-reference
```

### rklib-rkssp54-exact-ivp-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rklib&example=gams-rklib-rkssp54-exact-ivp-reference) / [Driver source](../fpm_catalog/gams-drivers/rklib-rkssp54-exact-ivp-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/src/rklib_fixed_classes.inc#L87) / [Author test](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/test/rk_test_order.F90)

```text
Step  0.1000: maximum state error   7.2036E-07, RHS calls 105
Step  0.0500: maximum state error   4.4444E-08, RHS calls 205
Step  0.0250: maximum state error   2.7587E-09, RHS calls 430
Step-halving error ratio:     16.20815
Step-halving error ratio:     16.11077
Decay, oscillator, nonlinear logistic and nonautonomous polynomial states checked.
PASS rklib-rkssp54-exact-ivp-reference
```

### rklib-rk5-exact-ivp-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rklib&example=gams-rklib-rk5-exact-ivp-reference) / [Driver source](../fpm_catalog/gams-drivers/rklib-rk5-exact-ivp-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/src/rklib_fixed_classes.inc#L101) / [Author test](https://github.com/jacobwilliams/rklib/blob/e3d51f9e8a2e6756612e8e53687ab2d4b67dfb76/test/rk_test_order.F90)

```text
Step  0.1000: maximum state error   2.6153E-08, RHS calls 126
Step  0.0500: maximum state error   8.0406E-10, RHS calls 246
Step  0.0250: maximum state error   2.4901E-11, RHS calls 516
Step-halving error ratio:     32.52645
Step-halving error ratio:     32.28979
Decay, oscillator, nonlinear logistic and nonautonomous polynomial states checked.
PASS rklib-rk5-exact-ivp-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers orderpack-partial-sort-reference orderpack-partial-ranks-reference orderpack-stable-unique-reference orderpack-multiplicities-reference orderpack-inverse-unique-ranks-reference orderpack-median-conventions-reference rklib-midpoint-exact-ivp-reference rklib-rk3-exact-ivp-reference rklib-rkssp54-exact-ivp-reference rklib-rk5-exact-ivp-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
