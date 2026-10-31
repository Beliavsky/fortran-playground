# Checked GAMS random-generator drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [L6a21](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L6a21) | Uniform pseudorandom generation | MT19937-64; rngff combined LCG |
| [L6c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L6c) | Random-number support, demonstrated by seeding | stdlib `random_seed` with `dist_rand` |

These deterministic sequence and API checks do not certify statistical quality or cryptographic suitability. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Mersenne Twister reference sequence

The MT19937-64 driver seeds two generators with integer seed 5489. It checks 15 raw 64-bit outputs at positions 1 through 10, 312, 313, 624, 625 and 1000 against independent C++11 `std::mt19937_64` output. The boundary positions exercise generator state refills. For all 1000 draws, the real64 output must equal `real(shiftr(bits,11),real64)*2**(-53)` exactly, be finite and lie in `[0,1)`. Reseeding must replay all 1000 values exactly.

The [reference source](../fpm_catalog/gams-drivers/references/mt19937_64_reference.cpp) and [reference output](../fpm_catalog/gams-drivers/references/mt19937_64_reference.txt) are stored in the repository. Output was generated with g++ (GCC) 17.0.0 20260510 (experimental), rather than copied from an upstream output table. The constants are embedded in the Fortran driver; running it requires no C++ compiler.

To regenerate the independent reference:

```text
g++ -std=c++11 fpm_catalog/gams-drivers/references/mt19937_64_reference.cpp -o mt-reference
./mt-reference
```

## Combined linear congruential generator

The rngff driver starts with seeds `[12345,67890]`. It independently evaluates `state=modulo([40014,40692]*state,[2147483563,2147483399])` using int64 arithmetic, whose products fit safely, rather than the package's int32 Schrage update. For 1000 draws, both states and the combined uniform value must match exactly; a second identically seeded object must replay every draw. Values must be finite in `[0,1)`.

At the pinned revision the real64 overload widens a real32 draw. The reference explicitly reproduces that rounding; returning a real64 value does not provide real64 random precision. This behavior is printed by the example.

## stdlib distribution seeding

The stdlib driver uses `stdlib_random:random_seed` and `dist_rand(0_int64)`. This controls stdlib's distribution stream, separately from intrinsic `random_number`. Seed 1234567 must reproduce all 1024 integer draws exactly and return the same opaque `get` value. That value is neither treated as an echo of the original seed nor as a complete running-state checkpoint. For the second selected seed, 1234568, the sequence must differ. This last check concerns these two seeds, rather than proving distinct streams for every pair of seeds. No probabilistic moment thresholds are used.

## Sources and playground links

| Driver | Class | Pinned procedure and author example |
| --- | --- | --- |
| [Load mt19937-64-reference-sequence](https://beliavsky.github.io/fortran-playground/fpm/?package=mersenne-twister-fortran&example=gams-mt19937-64-reference-sequence) / [Source](../fpm_catalog/gams-drivers/mt19937-64-reference-sequence.f90) | L6a21 | [Procedure](https://github.com/jacobwilliams/mersenne-twister-fortran/blob/1e3e364f4c022eab3fcd5d07b10a2c2be77a822b/src/mt19937-64.f90#L63) / [Author example](https://github.com/jacobwilliams/mersenne-twister-fortran/blob/1e3e364f4c022eab3fcd5d07b10a2c2be77a822b/test/mt19937_64_test.f90) |
| [Load rngff-lcg-reference-sequence](https://beliavsky.github.io/fortran-playground/fpm/?package=rngff&example=gams-rngff-lcg-reference-sequence) / [Source](../fpm_catalog/gams-drivers/rngff-lcg-reference-sequence.f90) | L6a21 | [Procedure](https://github.com/Archaeologic-Inc/rngff/blob/8eccd1479f35159922a85db25a39bcd58a0c3faa/src/rngff/linear_congruential_m.f90#L14) / [Author example](https://github.com/Archaeologic-Inc/rngff/blob/8eccd1479f35159922a85db25a39bcd58a0c3faa/test/lcg_test.f90) |
| [Load stdlib-seed-replay](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-seed-replay) / [Source](../fpm_catalog/gams-drivers/stdlib-seed-replay.f90) | L6c | [Procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_random.f90#L28) / [Author example](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_random_seed.f90) |

The drivers adapt author API patterns and retain license notices. They appear in hosted and main local FPM example menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-random-validation.json) records source hashes, pins and saved output. These checks establish neither a performance ranking nor cross-version sequence guarantees for APIs that do not promise them.

### mt19937-64-reference-sequence

```text
Reference output    1: C96D191CF6F6AEA6
Reference output    2: 401F7AC78BC80F1C
Reference output    3: B5EE8CB6ABE457F8
Reference output    4: F258D22D4DB91392
Reference output    5: 04EEF2B4B5D860CC
Reference output    6: 67A7AABE10D172D6
Reference output    7: 40565D50E72B4021
Reference output    8: 05D07B7D1E8DE386
Reference output    9: 8548DEA130821ACC
Reference output   10: 583C502C832E0A3A
Reference output  312: 13038D24C91C1BB8
Reference output  313: 5E0B18C0F57393B1
Reference output  624: D7C295AFC52A1C17
Reference output  625: AB1BF7646B530A67
Reference output 1000: 8D7573457A93F389
Exact uniform conversion/replay checks: 1000
First five uniform draws:   0.786820954868  0.250480340688  0.710671228979  0.946667800961  0.019271058196
PASS mt19937-64-reference-sequence
```

### rngff-lcg-reference-sequence

```text
Exact modular-state/output/replay checks: 1000
Final two-seed state:      540593668    1220816231
First five uniform draws:   0.943597376347  0.908318877220  0.146687835455  0.514701962471  0.405809640884
The real64 overload returns widened real32 draws.
PASS rngff-lcg-reference-sequence
```

### stdlib-seed-replay

```text
Exact integer replay checks: 1024
Opaque get output for the selected seed: 3DCE10B4AF53B7F1
First five integer draws (hexadecimal bit patterns):
  1 2959604F2E0091F3
  2 8DA1B0157235CF1A
  3 FCA57AAE79999882
  4 F12CE7489A216233
  5 1D3ED398D3C7CA3D
The second selected seed changed the sequence.
This seeds stdlib distributions; intrinsic RANDOM_NUMBER has its own seed API.
PASS stdlib-seed-replay
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers mt19937-64-reference-sequence rngff-lcg-reference-sequence stdlib-seed-replay
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
