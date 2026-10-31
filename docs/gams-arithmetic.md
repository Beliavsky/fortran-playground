# Checked GAMS arithmetic, representation and bit-operation drivers

These drivers cover specific configurations in A1 (Integer), A2 (Rational) and A6 (Change of representation), plus A3c/A4c arbitrary-precision real/complex arithmetic and N2 bit manipulation. The class-page links load the matching programs; the broader A page identifies the narrower demonstration. Arithmetic and the other GAMS sections are not exhausted.

## Exact rational addition: A2

`rational_number:ratNumAdd` is called for all operand pairs with numerators -4..4 and denominators 1..6, with simplification both disabled and enabled: 5832 calls. Each result has a positive denominator and is compared by exact int64 cross-products against `(p*s+r*q)/(q*s)`. All selected values and intermediate products fit comfortably within their integer kinds. Positive sums with simplification enabled must also equal the canonical numerator/denominator obtained by independently enumerating divisors.

**Pinned representation limitation:** the `math:gcDenom` dependency returns zero when either operand is nonpositive. Thus negative or zero numerators can remain unreduced even when `simplify=.true.`. For example, `-1/3 + -1/6` is returned as `-9/18`, an exact representation of `-1/2`. The driver checks the value and does not claim canonical negative/zero representations. Zero denominators, integer overflow, real-to-rational conversion and other rational operations are outside this example.

## Decimal-string integer arithmetic: A1

`strith` signed addition and subtraction are compared with native integer arithmetic for every ordered operand pair in -20..20: 3362 operations. Five additional identities exercise decimal values beyond int64: adding one to thirty nines, borrowing across thirty zeroes, both subtraction orders for adjacent 20-digit integers, and cancellation of opposite 30-digit values. The expected decimal strings are explicit; no native integer is overflowed to construct a reference.

The driver uses the pinned string constructor's explicit sign and fixed-width zero padding. This is fixed-capacity decimal arithmetic, not unlimited arbitrary precision. Capacity overflow, all comparison operators and the separate unsigned-formatting interface are not verified. This A1 driver does not mark the same procedure's A6 mapping verified.

## Binary64 decimal round trips: A6

`ryu:d2shortest` converts 132 finite IEEE binary64 bit patterns. Eleven exponent fields (0, 1, 2, 10, 511, 1022, 1023, 1024, 1535, 2045, 2046), six mantissas (0, 1, 2, 2^51-1, 2^51, 2^52-1), and both signs include signed zeros, subnormal/normal boundaries and the largest finite value. Intrinsic formatted input must recover the identical 64 bits; numerical equality alone would miss negative zero. The driver separately requires the author API's `0.0` and `-0.0` spellings.

This verifies selected finite round trips with gfortran's reader, not all binary64 patterns, correctness of every reader, NaN/infinity spellings or mathematical shortest-length optimality. The new driver is independently written. Its MIT license covers the driver; the upstream package's unspecified licensing metadata remains unchanged.

## Arbitrary-precision real addition: A3c

`MPFUN2020-var1` is used with 120 requested decimal digits and explicit word precision on all constructors. Six additions are compared by exact multiprecision equality with explicit decimal integer or dyadic-fraction references. They include `10^80+1` in both operand orders, its negative counterpart, exact cancellation, `123456789012345678901234567890 + 987654321098765432109876543210 = 1111111110111111111011111111100`, and `0.125+0.375=0.5`. The long integer reference is supplied explicitly rather than computed through another package operation.

The integer cases fit exactly within the requested precision. Ordinary binary64 arithmetic cannot retain the unit added to `10^80`. The example checks addition at one precision, not general accuracy, all exponent ranges, rounding behavior, other operations or performance. A small input helper appends `.0` to integer strings because the author's parser requires a decimal point. No binary64 conversion of the long decimal operands is used.

## Arbitrary-precision complex addition: A4c

Five MPFUN complex additions are checked by comparing both real and imaginary components exactly against explicit decimal references. The main cancellation problem is `(10^80,-10^80) + (-(10^80-1),10^80+2) = (1,2)`. Further cases reverse the signs, retain unit increments in both large components, add dyadic fractions and cancel to complex zero. The same 120-digit precision and decimal-point helper are used. These are independent mathematical identities and API consumers, not copied author quadrature programs. Multiplication, division, transcendental functions and all-input accuracy are outside the verification.

## Binary-string bit manipulation: N2

`bstrith` is checked against native integer references with 5120 exact string comparisons. For every 8-bit value 0..255, the driver checks left/right shifts by 1..7, complement, XOR with `10100101`, and modular increment/decrement. It also checks addition and subtraction for all 256 ordered pairs of 4-bit operands. References use intrinsic `ISHFT`, `IAND`, `IEOR` and bounded integer arithmetic modulo 16 or 256; subtraction is checked directly rather than just as the inverse of the package's addition.

This demonstrates N2 with valid fixed-width strings. Out-of-range shifts, malformed inputs and wider strings are outside the driver. The same procedure's A1 mapping remains source-supported until it has a separately recorded matching driver.

## Sources, links and recorded results

All 6 passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only the mains and executables were compiled. The [verification report](gams-arithmetic-validation.json) records source hashes and output. The drivers are independently written API consumers; author tests were inspected where available, and no upstream implementation or test code was copied. Their shared MIT notice applies to these new drivers, with upstream package terms recorded separately in the catalog. Loading the links selects code without submitting a job. The programs are available in hosted and main local FPM menus.

### rational-addition-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rational_number&example=gams-rational-addition-reference) / [Driver source](../fpm_catalog/gams-drivers/rational-addition-reference.f90) / [Pinned procedure](https://github.com/art-rasa/rational_number/blob/b6ff702a0f51b950798f2a31c5bd81ae0c15385a/src/rational_number.f90#L144)

```text
1/3 + 1/6 = 1/2
-1/3 - 1/6 = -9/18 (same value as -1/2)
Exact additions checked with simplify off/on: 5832
Pinned simplifier does not reduce negative/zero numerators; value checks allow this.
PASS rational-addition-reference
```

### strith-integer-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=strith&example=gams-strith-integer-reference) / [Driver source](../fpm_catalog/gams-drivers/strith-integer-reference.f90) / [Pinned procedure](https://github.com/degawa/strith/blob/da2b1f489a178cb443f636e3f9c89aed6c8702b1/src/type/strint.f90#L172)

```text
Thirty nines plus one: 1000000000000000000000000000000
Checked 3362 small signed additions/subtractions and 5 large decimal identities.
Fixed-capacity decimal integers; capacity overflow is outside this example.
PASS strith-integer-reference
```

### ryu-binary64-roundtrip

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=ryu_fortran&example=gams-ryu-binary64-roundtrip) / [Driver source](../fpm_catalog/gams-drivers/ryu-binary64-roundtrip.f90) / [Pinned procedure](https://github.com/St-Maxwell/ryu_fortran/blob/6c508144398d58143618c5598d816f20c40ac053/src/real64_to_shortest.f90#L640)

```text
Smallest subnormal: 4.9E-324
Smallest normal: 2.2250738585072014E-308
Largest finite: 1.7976931348623157E308
Negative zero: -0.0
Finite binary64 values recovered with identical bits: 132
NaN/infinity spelling, all bit patterns and shortest-length optimality are outside this example.
PASS ryu-binary64-roundtrip
```

### mpfun-real-addition

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=mpfun2020-var1&example=gams-mpfun-real-addition) / [Driver source](../fpm_catalog/gams-drivers/mpfun-real-addition.f90) / [Pinned procedure](https://github.com/jacobwilliams/MPFUN2020-var1/blob/f2191ad80d811cd5e309d83ffad9b2607d27aabc/src/mpfung1.f90#L862)

```text
Exact decimal identity: 10^80 + 1 = 1 followed by 79 zeroes and 1.
Also checked operand order, negative addition, cancellation and an explicit 31-digit sum.
Computed dyadic sum 0.125 + 0.375:
5.0000000e-1                  
Checked additions: 6; requested decimal precision: 120
PASS mpfun-real-addition
```

### mpfun-complex-addition

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=mpfun2020-var1&example=gams-mpfun-complex-addition) / [Driver source](../fpm_catalog/gams-drivers/mpfun-complex-addition.f90) / [Pinned procedure](https://github.com/jacobwilliams/MPFUN2020-var1/blob/f2191ad80d811cd5e309d83ffad9b2607d27aabc/src/mpfung1.f90#L942)

```text
(10^80,-10^80) + (-(10^80-1),10^80+2), recovered components:
1.0000000e0                   
2.0000000e0                   
Exact complex sums checked: 5; requested decimal precision: 120
Checked both components; multiplication and transcendental functions are outside this driver.
PASS mpfun-complex-addition
```

### bstrith-bit-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=bstrith&example=gams-bstrith-bit-reference) / [Driver source](../fpm_catalog/gams-drivers/bstrith-bit-reference.f90) / [Pinned procedure](https://github.com/degawa/bstrith/blob/7ed7730e34c7e1f78f2be9426ccc170f9dcaf57e/src/arithmetic/basic/add/add.f90#L1)

```text
10100101 shifted left by 2: 10010100
10100101 XOR 11110000: 01010101
Independent bit/arithmetic checks passed: 5120
Shift distances 1..7 for every 8-bit value; all pairs of 4-bit arithmetic operands.
Out-of-range shifts, malformed strings and wider strings are outside this example.
PASS bstrith-bit-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers rational-addition-reference strith-integer-reference ryu-binary64-roundtrip
python xverify_gams_drivers.py --drivers mpfun-real-addition mpfun-complex-addition bstrith-bit-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. See the [coverage report](gams-coverage.md) and [mapping evidence queue](gams-mapping-evidence.md) for remaining work.
