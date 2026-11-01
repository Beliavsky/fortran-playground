# Checked KISS streams and normalized random spacing

These L6a21 and L6 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-random-references-validation.json) retains pins, source hashes and complete output. GAMS categories are not exhausted. These are sequence/construction checks and selected-seed law smoke checks, not statistical-quality certification.

## rndgen-fortran KISS streams (L6a21)

Seven interleaved generators use seeds [0,1,-1,12345,-67890,294727492,2147483646]. Each yields 4,096 draws, for 28,672 outputs. Every draw must be finite in [0,1), lie exactly on the 31-bit grid k/2**31, and reproduce on reset. The first eight decoded integers per stream, 56 entries, must match independent constants exactly. A rolling modular checksum over every stream must also match its independent reference. Checksums compactly check the long streams; they are not a collision-free comparison of every entry to a stored reference.

The [reference generator](../fpm_catalog/gams-drivers/references/kiss_vectors.py) uses unbounded Python integers and explicit modulo-2**32 arithmetic, rather than Fortran signed overflow. The seed shuffle interprets its modular product as signed int32 before taking its absolute value and clamping it to [1,2147483646]. Four Park-Miller seed steps use direct multiplication modulo 2**31-1 rather than the library Schrage decomposition; one initial KISS draw is discarded. The reference implements the reviewed mathematical KISS convention, not an independent statistical randomness oracle. No upstream implementation or test bodies were copied.

The KISS state combines a linear-congruential component, a three-shift xor component and two multiply-with-carry components. Explicitly wrapping the combined sum to 32 bits and discarding its low bit produces k. For each 4,096-entry stream, checksum starts at zero and updates as (65599*checksum+k) modulo 2147483647; its int64 products fit safely. Stored [vectors](../fpm_catalog/gams-drivers/references/kiss-vectors.json) and embedded Fortran constants are checked by running the generator without --write. The Fortran consumer requires no Python installation.

The consumer additionally saves an opaque in-memory state after each reset replay, generates 257 more values, restores the state and checks all of them exactly: 1,799 continuation entries. Interleaving checks these objects do not contaminate one another, not that streams are statistically independent. Positive and negative seeds with equal absolute value intentionally share a stream. All 56 prefixes, seven long-stream checksums, 28,672 reset replay entries and 1,799 continuation entries passed.

The upstream implementation relies on signed int32 overflow in several updates. This result checks the cached GNU 16 wraparound behavior; it does not establish standard-conforming integer overflow, other-compiler behavior, generator period, statistical quality or cryptographic suitability. The minimum int32 seed, file serialization and integer/ranged-real convenience APIs remain unverified.

## Pointsets normalized random increments (L6)

The pinned random_spacing routine draws n intrinsic uniform values, discards the first, accumulates the remaining positive increments, and rescales the cumulative sequence to the requested interval. For n>=2 its mathematical construction is x_i=a+(b-a)*sum(U_2,...,U_i)/sum(U_2,...,U_n), with x_1=a and x_n=b. It does not sort uniform points or use exponential spacings. The former L6a21 procedure mapping has been broadened to L6 random-number generation: the returned coordinates are not uniform draws or uniform order statistics.

Seven sizes [0,1,2,3,9,33,129], intervals [0,1], [-3.5,2.25], [0.25,0.25] and seeds [42,1729,314159] give 63 fixtures. GNU random seed arrays contain seed+37*i. A separately seeded intrinsic draw supplies the same raw inputs to a real64 sum-and-ratio oracle, while the cached package works in real32. This isolates the construction from the intrinsic generator: it does not independently verify the generator itself.

For the 45 nontrivial-size fixtures, all 1,584 coordinates are checked against the oracle within normalized tolerance 8*n*epsilon(real32), using normalizer 1+max(abs(a),abs(b)). Finite values, nondecreasing order and endpoints are checked. All 18 empty/singleton fixtures must leave their input unchanged, including the singleton sentinel -99. They consume no random draws; larger arrays consume exactly n. The next intrinsic random value and exact full-result seeded replay verify this behavior. The maximum normalized coordinate error was 2.84632e-7.

With three points on [0,1], the only interior coordinate is R=U/(U+V) for independent uniform increments U,V. For 0<=r<=1/2, P(R<=r)=r/(2*(1-r)); for 1/2<=r<=1 it is 1-(1-r)/(2*r). The two expressions follow from integrating the area U<=r*V/(1-r) in the unit square. Consequently the CDF values at 1/4 and 3/4 are 1/6 and 5/6, and symmetry gives mean 1/2. A single uniform interior point would instead have CDF 1/4 and 3/4 there.

Each of the three seeds supplies 20,000 three-point sets, for 60,000 law samples. The empirical CDFs must be within 0.015 of 1/6 and 5/6, the empirical mean within 0.015 of 1/2, and the quarter-point CDF must differ from 1/4 by at least 0.04. Observed quarter-point CDFs were 0.16425, 0.16510 and 0.16585; the largest CDF discrepancy was 0.00271667. These fixed-seed smoke checks distinguish this construction from uniform order statistics without certifying the full distribution or statistical quality of an RNG.

Reversed intervals, rare all-zero increment sums, other precisions, other pointsets generators and cross-compiler intrinsic RNG sequences remain unverified. No library patch, backend redeployment or cached package rebuild is required by either driver.

## Sources, licenses and actual output

Pinned APIs/implementations and author examples were reviewed before writing the independent consumers and reference arithmetic. Drivers and reference generator have their own MIT notice; upstream rndgen-fortran and pointsets license terms remain separate. Loading a driver does not submit a job.

### rndgen-kiss-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rndgen-fortran&example=gams-rndgen-kiss-reference) / [Driver source](../fpm_catalog/gams-drivers/rndgen-kiss-reference.f90) / [Pinned procedure](https://github.com/wcota/rndgen-fortran/blob/3fa553608324913eed6cb178b398e7f661e4f63a/src/rndgen.f90#L59) / [Author test](https://github.com/wcota/rndgen-fortran/blob/3fa553608324913eed6cb178b398e7f661e4f63a/example/simple.f90)

```text
Interleaved streams: 7; uniform outputs: 28672
Exact independent prefix entries: 56; whole-stream checksums: 7
Exact reset replays: 28672; saved-state continuations: 1799
GNU 16 wraparound convention checked; no statistical-quality or cross-compiler guarantee.
PASS rndgen-kiss-reference
```

### pointsets-random-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=pointsets&example=gams-pointsets-random-reference) / [Driver source](../fpm_catalog/gams-drivers/pointsets-random-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/pointsets/blob/a1c381777f893d656018366cfabfa4cc7531e4dd/src/pointsets.f90#L88) / [Author test](https://github.com/arjenmarkus/pointsets/blob/a1c381777f893d656018366cfabfa4cc7531e4dd/test/pointsets/test_pointsets.f90)

```text
Seed       42; empirical CDF at 1/4,3/4 and mean:    0.1642500   0.8330500   0.5016029
Seed     1729; empirical CDF at 1/4,3/4 and mean:    0.1651000   0.8360500   0.4986118
Seed   314159; empirical CDF at 1/4,3/4 and mean:    0.1658500   0.8328500   0.4993280
Spacing fixtures: 63; reference coordinates: 1584; no-op fixtures: 18
Three-point law samples: 60000; seed groups: 3
Max normalized coordinate and CDF errors:    2.84632E-07   2.71667E-03
Normalized uniform increments are not uniform order statistics; no randomness certification.
PASS pointsets-random-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers rndgen-kiss-reference pointsets-random-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
