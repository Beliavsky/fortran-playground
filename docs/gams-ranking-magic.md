# Checked sorting indices and magic-square construction

These N6 and D1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-ranking-magic-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## ORDERPACK rank: indices that sort data (N6)

Every permutation of lengths 1..7 gives 5,913 exhaustive fixtures. Another 84 fixtures use six patterns at sizes [0,1,2,3,4,7,8,15,16,31,32,63,64,127]: ascending signed values, descending values, a constant, three repeated keys, alternating signed magnitudes and mod(37*i+11,17)-8. Each fixture exercises integer32, real32, real64 and character overloads, giving 5,997 fixtures and 23,988 rank calls. Some degenerate patterns coincide; fixture counts are not counts of distinct data arrays.

Real keys are integer values divided by eight, exactly representable in both floating-point kinds. Character keys are four-digit, zero-padded decimal strings of integer_value+512, so their lexical ordering agrees with integer ordering. This is a controlled character fixture, not a test of language-specific collation.

Independent insertion-sort loops compute expected sorted integer values before calling ORDERPACK. Each returned index must be in range and each original index must occur exactly once. Original values indexed by the result must match the reference sequence exactly. This checks all four overloads against the independent reference, not against each other. All four source arrays must remain unchanged. Empty arrays are exercised without reading undefined output elements.

Tied keys may have any valid index order; stable tie ordering is not required or claimed. NaNs, infinities, signed-zero conventions, arbitrary character encodings, mismatched output lengths, other ORDERPACK procedures and performance remain unverified. This N6 mapping concerns sorting indices, not statistical rank inference.

## M_LA mat_magic: normal magic squares (D1)

Orders 1 and 3..32 include 16 odd, eight doubly-even and seven singly-even orders. Order two is excluded because no normal magic square of that order exists. Each order is constructed twice with compact leading dimension n and twice with padded leading dimension n+3: 124 calls. Storage is reset to a finite sentinel before each call; padded rows must remain untouched.

All outputs must be finite. Active entries must be exactly integer-valued and form a permutation of 1..n**2. Exact int64 scalar sums verify every row, column and both principal diagonals against n*(n**2+1)/2. These checks do not depend on the constructor algorithm or a preferred square arrangement. Across all calls there are 45,744 entry checks and 4,456 exact line-sum checks. Repeated construction checks valid results after storage reuse without imposing a particular arrangement on valid squares.

The D1 mapping covers this matrix constructor only. Other M_LA utilities, unsupported orders, invalid leading dimensions and performance remain unverified.

## Checked links and actual output

These independently written API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and the ORDERPACK author example were reviewed without copying upstream code. Loading a link does not submit a job.

### orderpack-ranking-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=orderpack&example=gams-orderpack-ranking-reference) / [Driver source](../fpm_catalog/gams-drivers/orderpack-ranking-reference.f90) / [Pinned procedure](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/src/M_orderpack.f90#L7) / [Author test](https://github.com/urbanjost/orderpack/blob/9696eee2670beae1601ae59e125ff9f10e6c88a7/example/demo_rank.f90)

```text
Exhaustive permutations through length seven: 5913
Total ranking fixtures: 5997; overload calls: 23988
Integer32, real32, real64 and character keys; empty input, ties and boundary sizes.
Independent insertion-order reference; permutation integrity and input preservation.
PASS orderpack-ranking-reference
```

### m-la-magic-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=m_la&example=gams-m-la-magic-reference) / [Driver source](../fpm_catalog/gams-drivers/m-la-magic-reference.f90) / [Pinned procedure](https://github.com/urbanjost/M_LA/blob/db59eeab0deab7e84eadf2542ad49c1c719dfb94/src/M_LA.f90#L1561) / No pinned author example; API reviewed directly.

```text
Magic-square calls: 124
Entry checks: 45744; exact line-sum checks: 4456
Orders 1 and 3..32; odd/doubly-even/singly-even; compact/padded storage; repeated calls.
PASS m-la-magic-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers orderpack-ranking-reference m-la-magic-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
