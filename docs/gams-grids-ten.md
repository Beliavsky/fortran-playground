# Ten checked stdlib grid and numerical utility drivers

Ten independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. Existing stdlib libraries were reused; only mains and executables were compiled. The [verification report](gams-grids-ten-validation.json) saves normalized UTF-8/LF source hashes, pins, timings and complete output. GAMS categories are not exhausted.

## Independent references and tested scope

These drivers cover numerical setup and checking utilities, rather than ten new solvers. The [reference tables](gams-grids-ten-references.json) save logarithmic-grid values, an exact rational tolerance truth table and an independent pi constant. The reference generator uses mpmath 1.3.0 at 80 digits, confirmed at 120 digits to absolute difference below 1e-65, for powers and pi. No upstream implementation or author-test body was copied; pinned public APIs, implementations and linked author examples were reviewed.

- **Greatest common divisor (B):** all 6,561 signed INT64 pairs -40..40, with exhaustive common-divisor enumeration rather than Euclid, plus four large exact cases. The zero-zero convention is checked. The minimum representable integer and overflow are excluded.
- **Linear grids (D1a11):** 2,916 REAL64 and 2,916 COMPLEX128 grids, with independent convex endpoint weights. Lengths -2..33 cover empty and singleton behavior; a singleton returns the end. Default length 100 is also checked.
- **Logarithmic grids (D1a11):** 60 grids with 372 high-precision references for positive bases 2, 4, 10 and 0.5, ascending/descending/constant exponents and lengths 1, 2, 3, 8 and 17. Empty/negative lengths and default base/length are checked separately. Complex and negative bases are excluded.
- **Stepped ranges (D1a11):** 867 bounded REAL64 dyadic ranges checked by repeated addition, and 17 single-argument INT64 ranges. Endpoints are inclusive when reached; positive step magnitudes are directed toward descending endpoints as documented by this API. Explicit zero/negative steps are excluded.
- **Cartesian grids (D1b1):** 42 rectangular sizes with both xy and ij layouts checked by coordinate lookup. Only the rank-two API is claimed.
- **Clipping (A3a):** 1,935 value/bound combinations, scalar and elemental calls, plus five INT64 values at 10^12 scale. Bounds are ordered, including equal bounds. Nonfinite values and reversed bounds are excluded.
- **Tolerance comparisons (R2):** 289 exact rational truth-table pairs with explicit relative tolerance 1/8 and absolute tolerance 1/16; scalar/elemental symmetry, REAL64 and COMPLEX128 matrix all_close, and NaN policy. The complex policy is componentwise, not a complex-modulus tolerance. Default tolerances and infinities are excluded.
- **Complex phase (C4a):** eight exact axis/diagonal directions at 25 powers-of-two scales, checked in radians, degrees and multiples of pi (600 references). Origin, signed-zero branch cuts and general off-diagonal angles are excluded.
- **Angle units (R):** 145 degree/radian values from -1080 to 1080 degrees, checked independently in each direction; round trips are secondary. This is unit conversion, not huge-angle reduction or a trigonometric accuracy claim.
- **Vector exchange (D1a5):** lengths 0..64 for REAL64, COMPLEX128 and INT64, checked after one and two swaps, plus disjoint strided slices and unchanged untouched elements. Aliasing and other overloads are excluded.

All comparisons require finite real results where applicable. Real checks use scaled absolute tolerance 3e-13; integer, truth-table and exchange checks are exact. These are bounded test sets, not blanket claims for all overloads, inputs or performance.

## Classification and provenance

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies B (number theory), A3a (standard precision arithmetic), C4a (trigonometric and inverse trigonometric functions), D1a5 (copy/exchange), D1a11 (other vector operations), D1b1 (matrix initialization), R2 (error checking) and broad R (service routines). Grid constructors do not claim interpolation or integration; the angle converter uses broad service classification. Loading any example does not submit a job.

These are independent MIT consumers; upstream package license terms remain separate. No upstream numerical source was patched. The [coverage report](gams-coverage.md) records remaining work.

## Driver details

### stdlib-gcd-reference (B)

Independent API consumer; pinned sources reviewed. INT64 greatest common divisors for all signed pairs -40..40, using exhaustive common-divisor enumeration rather than Euclid; zero-zero convention and four large exact cases. Minimum representable integers and overflow are not tested.

### stdlib-linear-grids-reference (D1a11)

Independent API consumer; pinned sources reviewed. REAL64 and COMPLEX128 linear grids for 81 endpoint pairs and lengths -2..33, checked by independent convex endpoint weights; singleton returns the end and nonpositive lengths are empty. Default length 100 also checked. No overflow or other kinds claimed.

### stdlib-logarithmic-grids-reference (D1a11)

Independent API consumer; pinned sources reviewed. 60 REAL64 logarithmic grids, four positive bases (2,4,10,0.5), ascending/descending/constant exponents and lengths 1,2,3,8,17; 372 stored 80/120-digit independent references. Empty/negative lengths and default length/base also checked. No complex bases or negative-base domains claimed.

### stdlib-stepped-ranges-reference (D1a11)

Independent API consumer; pinned sources reviewed. 867 REAL64 dyadic ranges checked by independent repeated addition including descending endpoints and a final partial step. The upper endpoint is included when reached; step magnitude is directed toward the end. Also checks 17 single-argument INT64 ranges. Zero/negative explicit steps and large allocations are excluded.

### stdlib-cartesian-grids-reference (D1b1)

Independent API consumer; pinned sources reviewed. REAL64 Cartesian grids for all 42 rectangular sizes nx=1..7, ny=1..6, both default xy and explicit ij layouts, using coordinate lookup references. Coordinates and inputs are exact dyadics; no rank-three/four or invalid shape behavior claimed.

### stdlib-bounded-clipping-reference (A3a)

Independent API consumer; pinned sources reviewed. REAL64 elemental clipping over 129 dyadic values and 15 valid bound pairs, including equal bounds; independent branch references and vector/scalar checks. Also checks INT64 clipping at 10^12 scale. Reversed bounds and nonfinite values excluded.

### stdlib-tolerance-comparison-reference (R2)

Independent API consumer; pinned sources reviewed. 289 exact rational truth-table pairs with explicit dyadic relative/absolute tolerances, symmetry, scalar and elemental REAL64 comparisons, plus rank-two REAL64/COMPLEX128 all_close and explicit NaN policy. Complex comparison is componentwise; infinities and implicit default tolerances excluded.

### stdlib-complex-phase-reference (C4a)

Independent API consumer; pinned sources reviewed. COMPLEX128 phase in radians, degrees and multiples of pi for eight exact axis/diagonal directions at 25 powers-of-two scales; known quadrant fractions of an independently stored pi constant. Origin, signed-zero branch cuts, nonfinite values and general off-diagonal angles excluded.

### stdlib-angle-units-reference (R)

Independent API consumer; pinned sources reviewed. REAL64 degree/radian conversion for 145 values -1080..1080 by 15 degrees, checked independently in both directions against a stored 80/120-digit pi constant. Round trips are secondary, not the oracle. No huge-angle reduction or trigonometric accuracy claimed. Classified broadly as service routines, not an inverse-trigonometric solver.

### stdlib-vector-exchange-reference (D1a5)

Independent API consumer; pinned sources reviewed. Elemental exchange for disjoint REAL64, COMPLEX128 and INT64 vectors of lengths 0..64, checked against saved inputs after one and two exchanges. Also checks disjoint strided slices. Aliasing, character/string and derived-type overloads excluded.

## Provenance and actual output

### stdlib-gcd-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-gcd-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-gcd-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L75) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_gcd.f90)

```text
Exhaustive signed GCD pairs: 6561; large exact cases: 4
PASS stdlib-gcd-reference
```

### stdlib-linear-grids-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-linear-grids-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-linear-grids-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L82) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_linspace_complex.f90)

```text
Independent linear grids: 2916 real and complex; default length: 100
PASS stdlib-linear-grids-reference
```

### stdlib-logarithmic-grids-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-logarithmic-grids-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-logarithmic-grids-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L217) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_logspace_int.f90)

```text
Independent logarithmic-grid references: 372
PASS stdlib-logarithmic-grids-reference
```

### stdlib-stepped-ranges-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-stepped-ranges-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-stepped-ranges-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L14) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_math_arange.f90)

```text
Independent dyadic stepped ranges: 867; INT64 ranges: 17
PASS stdlib-stepped-ranges-reference
```

### stdlib-cartesian-grids-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-cartesian-grids-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-cartesian-grids-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L983) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_meshgrid.f90)

```text
Independent Cartesian rectangles: 42; xy and ij layouts
PASS stdlib-cartesian-grids-reference
```

### stdlib-bounded-clipping-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-bounded-clipping-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-bounded-clipping-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L1070) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_clip_real.f90)

```text
Independent clipping references: 1935; large integers: 5
PASS stdlib-bounded-clipping-reference
```

### stdlib-tolerance-comparison-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-tolerance-comparison-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-tolerance-comparison-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L539) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_math_is_close.f90)

```text
Exact rational tolerance pairs: 289; matrix, componentwise complex and NaN policies checked
PASS stdlib-tolerance-comparison-reference
```

### stdlib-complex-phase-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-complex-phase-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-complex-phase-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L1106) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_math_arg.f90)

```text
Independent quadrant phase references: 600 (radians, degrees, pi units)
PASS stdlib-complex-phase-reference
```

### stdlib-angle-units-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-angle-units-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-angle-units-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L523) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_math_deg2rad.f90)

```text
Independent degree/radian conversions: 145 angles in each direction
PASS stdlib-angle-units-reference
```

### stdlib-vector-exchange-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-vector-exchange-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-vector-exchange-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.f90#L1251) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/example/example_math_swap.F90)

```text
Vector exchange: lengths 0..64, three kinds, inverse exchange and disjoint strided slices
PASS stdlib-vector-exchange-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-gcd-reference stdlib-linear-grids-reference stdlib-logarithmic-grids-reference stdlib-stepped-ranges-reference stdlib-cartesian-grids-reference stdlib-bounded-clipping-reference stdlib-tolerance-comparison-reference stdlib-complex-phase-reference stdlib-angle-units-reference stdlib-vector-exchange-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
