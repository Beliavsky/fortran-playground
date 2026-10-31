# Checked unsigned arithmetic and operable bitsets

These A1 and N2 drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-unsigned-bitsets-validation.json) retains exact source hashes, pins, build logs and program output. GAMS categories are not exhausted.

## uint-fortran fixed-width integers (A1)

The independent driver checks uint8, uint16 and uint32 against ordinary integer(int64) formulas. Each width uses 24 operand fixtures, including zero, one, powers-of-two boundaries, the signed midpoint and neighbors, the unsigned maximum and neighbors, and fractions of the modulus. Some small-width fixtures coincide; these are 1,728 operand pairs across the three widths, not a claim of distinct values in every fixture.

Each pair checks addition and subtraction modulo 2**width, division when the divisor is nonzero, all six relational operators, and preservation of both operands. Conversions are checked for every outer-loop fixture. Nine negative int64 assignments per width include -1, -128, -256, -257, -65536 and -4294967295; their references use the nonnegative Fortran MODULO result. In total, 17,307 exact checks passed. The int64 oracle safely contains all tested sums, differences and quotients.

The checks exercise carry, borrow, unsigned ordering above the signed boundary, truncating nonnegative integer division and assignment conversion. Multiplication, powers, mixed-kind operators, uint64 and C interoperability remain unverified. This is fixed-width arithmetic, not arbitrary-precision integer validation. The driver does not change library source or compiler overflow settings.

## ORBS bitset operators (N2)

Eleven widths [1,4,8,31,32,63,64,65,127,128,129] cross storage-word boundaries. Each width uses 16 deterministic patterns: zero, all ones, low/high endpoint bits and modularly generated binary strings. Patterns can coincide at small widths. Every ordered pair is tested, giving 2,816 operand pairs.

AND, OR, XOR and ANDNOT references are built one character at a time from logical truth tables. Addition and subtraction use independent base-two schoolbook carry/borrow arithmetic, discarding the final carry/borrow to model fixed width. These references call neither ORBS nor its stdlib/bstrith dependencies. Every input pattern also checks NOT and every shift from 1-width through width-1, including zero. Shift references relocate individual characters and fill vacated positions with zeros; undefined shifts outside the documented range are not attempted.

All 37,760 binary-string references must match exactly and retain their expected width. Pair operations must preserve both operands. Multiword carry/borrow and shifts are exercised, including 65-, 127-, 128- and 129-bit values. Mixed widths, zero-length sets, mutation methods, sorting, formatted I/O and malformed-input handling remain unverified. This driver supports the N2 mapping; it does not automatically promote the sibling A1 mapping for the same procedure record.

## Sources, licenses and actual output

Pinned operator/conversion implementations and available author tests were reviewed. The independently written API consumers have their own MIT notice; upstream terms remain separate. No upstream test bodies are copied. The ORBS record has no pinned author example recorded, so its API source was reviewed directly. Loading a driver does not submit a job.

### uint-arithmetic-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=uint-fortran&example=gams-uint-arithmetic-reference) / [Driver source](../fpm_catalog/gams-drivers/uint-arithmetic-reference.f90) / [Pinned procedure](https://github.com/ShinobuAmasaki/uint-fortran/blob/487f806c76a5d107c5a8982198bafb295065eba7/src/types/uint32_t.f90#L10) / [Author test](https://github.com/ShinobuAmasaki/uint-fortran/blob/487f806c76a5d107c5a8982198bafb295065eba7/test/check-assign-negative_uint32.f90)

```text
Unsigned operand pairs: 1728
Exact integer checks: 17307
PASS uint-arithmetic-reference
```

### orbs-bitwise-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=orbs&example=gams-orbs-bitwise-reference) / [Driver source](../fpm_catalog/gams-drivers/orbs-bitwise-reference.f90) / [Pinned procedure](https://github.com/degawa/orbs/blob/3cf7fcec19798367f6f5bd26bad861c510449265/src/orbs.f90#L1) / No pinned author example; API reviewed directly.

```text
Bitset widths: 11
Operand pairs: 2816
Exact binary-string references: 37760
PASS orbs-bitwise-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers uint-arithmetic-reference orbs-bitwise-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
