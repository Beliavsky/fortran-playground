# Checked GAMS number-theory drivers

Both currently selected packages in [B: Number theory](https://beliavsky.github.io/fortran-playground/gams/B/) now have class-specific checked drivers. Their primary class-page links load these drivers, rather than the package defaults. B has no finer classes in the recorded GAMS taxonomy; this does not exhaust the packages, their input domains or number theory.

## Prime enumeration and primality

`fortran-primes` uses `prime_numbers:primes` and `is_prime`. The driver checks 1021 int32 operands from -20 through 1000 against an independent trial-division function. It compares the complete ordered list through 1000 against independently generated primes and also checks the known count 168 and sum 76127. It checks the bounded range [100,200], an upper bound below two, and a reversed range.

Eight int64 cases include negative/zero/unit operands, 2, 2147483647, 10000000019, 10000000020 and 10000000021. Each is independently checked by trial division. The reference tests every divisor through the square root, using `d <= n/d` to avoid squaring overflow. The example adapts the author test API patterns; it does not compare with the package's own tables or another API from the same implementation.

These checks do not establish correctness over the full int32/int64 domains. Factorization, next-prime queries and large enumeration workloads are outside this driver. The upstream MIT license and the pinned source's additional Primes.jl/CC BY-NC notices are retained.

**Pinned API limitation:** an initial driver timed out after reaching the int64 case `3215031751` (the composite `151*751*28351`). The [failing source](gams-candidates/fortran-primes/large-int64-primality.f90), [sandbox result](gams-candidates/fortran-primes/large-int64-primality-result.json), [minimal reproducer](gams-candidates/fortran-primes/signed-int32-boundary.f90) and [isolated result](gams-candidates/fortran-primes/signed-int32-boundary-result.json) are retained. Source inspection shows that the `n<2**32` branch narrows `n` to signed int32; the modular-exponentiation loop then arithmetically shifts a negative exponent. The checked driver excludes this known failing case and explicitly notes the limitation. The B mapping remains justified by the demonstrated number-theory operations, without a claim of full-domain primality correctness.

## Greatest common divisors and least common multiples

`rpn-calculator-fortran` exposes `rat:gcd` and `lcm` independently of its interactive calculator. The driver checks every ordered pair of nonnegative operands from 0 through 64: 4225 GCD calls and 4224 LCM calls. Its GCD reference enumerates common divisors; its LCM reference searches successive multiples of the larger operand. Neither reference calls a package routine or uses the package's Euclidean-GCD/LCM formula. Results are exact integer comparisons.

**Pinned API limitation:** `lcm(0,0)` evaluates `0/gcd(0,0)` and therefore divides by zero. The driver excludes that call and states the restriction in its output. The implementation returns `gcd(0,0)=0`, which is checked as an API convention. LCM with exactly one zero operand is checked in both orders. Negative-operand sign conventions, overflow and the calculator's other numerical functions are outside this driver. The upstream MIT notice is retained.

## Sources, links and recorded results

Both passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing package libraries. Only the mains and executables were compiled. The [verification report](gams-number-theory-validation.json) records source hashes and output. Loading the links selects code without submitting a job; the examples appear in hosted and main local FPM menus.

### primes-trial-division

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-primes&example=gams-primes-trial-division) / [Driver source](../fpm_catalog/gams-drivers/primes-trial-division.f90) / [Pinned procedure](https://github.com/perazz/fortran-primes/blob/817abbf15c2565d2b92c35546d9e18152eb02e2c/src/prime_numbers.f90#L40)

[Pinned author test](https://github.com/perazz/fortran-primes/blob/817abbf15c2565d2b92c35546d9e18152eb02e2c/test/test_primes.f90)

```text
Primes through 1000: count = 168; sum = 76127
Primes in [100,200]: 101 103 107 109 113 127 131 137 139 149 151 157 163 167 173 179 181 191 193 197 199
is_prime(-2) = F
is_prime(0) = F
is_prime(1) = F
is_prime(2) = T
is_prime(2147483647) = T
is_prime(10000000019) = T
is_prime(10000000020) = F
is_prime(10000000021) = F
Checked 1021 int32 cases, 8 int64 cases, and enumerated prime lists.
PASS primes-trial-division
```

### rpn-gcd-lcm-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran&example=gams-rpn-gcd-lcm-reference) / [Driver source](../fpm_catalog/gams-drivers/rpn-gcd-lcm-reference.f90) / [Pinned procedure](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/src/rat.f90#L1)

```text
gcd(48,18) = 6
lcm(48,18) = 144
Checked 4225 GCD and 4224 LCM cases for operands 0 through 64.
Zero operands checked; lcm(0,0), negative signs and overflow are outside this example.
PASS rpn-gcd-lcm-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers primes-trial-division rpn-gcd-lcm-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. Other GAMS sections still have source-supported and uncertain mappings; see the [coverage report](gams-coverage.md) and [mapping evidence queue](gams-mapping-evidence.md).
