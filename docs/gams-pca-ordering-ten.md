# Ten checked ordering and array-algebra drivers; retained PCA probe

Ten independent stdlib drivers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-pca-ordering-ten-validation.json) saves normalized source hashes, package pins, timings and complete output. GAMS categories are not exhausted.

## Order statistics and associated sorting

select and arg_select each make 2,976 calls: every rank in 186 arrays of lengths 1..31 across six deterministic dyadic families. Independent insertion sorting supplies expected order statistics. Ascending, descending, all-equal, signed, modular and repeated-block inputs exercise ties and pivots. select must preserve the full multiset and produce a valid partial partition. arg_select must preserve values and produce a valid index permutation and partition, including when initial indices are reversed. An arbitrary identity within ties is not prescribed. Empty/invalid ranks and bounded-search options are unverified.

sort_index and sort_adjoint each make 780 calls on lengths 0..64, six families and both sort directions. A separate stable insertion sort supplies complete key order and original-position associations. sort_index actively sorts the keys and returns a permutation; it is not a passive-only argsort. sort_adjoint moves unique dyadic payloads alongside keys. Both check stable ordering within ties in ascending and descending mode, including empty/constant inputs. NaNs, infinities, workspace options and other index/payload kinds remain unverified.

unique has 390 exact sorted-output comparisons, lengths 0..64. An independent bounded-bin membership scan supplies the sorted set without calling any sorting routine. Count, values, finiteness and input preservation are checked, including empty and all-equal inputs. Only sorted_output=true and tolerance=0 are verified; hash-based unsorted mode and approximate grouping are not.

## Adjacent differences and vector products

diff makes 325 comparisons on lengths 0..24 and orders 0..6, plain or with prepend/append arrays for positive orders. The independent reference is the explicit binomial stencil sum sum((-1)**(n-j)*choose(n,j)*x(i+j),j=0..n), rather than another sequence of adjacent differences. Order zero is the identity and inputs too short for a positive order give empty results. Exact bounded dyadic arithmetic, output length, finite values and input preservation are checked. This is an array difference operator, not a step-scaled numerical derivative. Rank-two/dimension options and negative-order policies remain unverified.

cross_product checks 2,154 pairs: nine ordered basis pairs and 2,145 bounded dyadic pairs, including zero and parallel vectors. A Levi-Civita determinant sum independently supplies all components. Antisymmetry and orthogonality to both inputs are also checked exactly. Arbitrary floating conditioning and scale extremes are not covered.

## Outer products, tensor products and diagonals

outer_product checks 224 rectangular rank-one matrices, rows 1..8 and columns 1..7, with four dyadic families including a zero factor. Every entry is checked, together with independent scalar-dot matrix action A*x=a*(b*x), zero adjacent two-by-two minors and sum(A*A)=sum(a*a)*sum(b*b). Complex conjugation semantics are not claimed.

kronecker_product checks 432 products: 144 rectangular shape pairs and three sign/zero families. Independent flattened output indices supply every entry. A separate scalar contraction verifies (A tensor B)*vec(X)=vec(B*X*transpose(A)) using Fortran column-major ordering. This distinguishes block layout from an ordinary matrix product. The bounded dyadic cases use exact comparisons; empty inputs, other kinds and extreme scales remain unverified.

diag makes 84 offset-diagonal constructions for vector lengths 1..12 and offsets -3..3, checking the entire matrix including off-diagonal zeros. There are 168 extractions: embedded vectors and separately filled dense matrices with independent scalar index references. Shape, exact values and finiteness are checked. Rectangular extraction, empty vectors and out-of-range offsets are not covered.

## PCA remains source-supported

A separate analytic PCA consumer was prepared for 24 rotated full-rank datasets, both SVD and covariance methods, and known means, axes, singular values, variances and truncated projections. Its main source compiled, but linking failed with file-size limit signal 25 under the existing 16 MiB hosted limit. No program ran and no PCA numerical assertions were verified. This is a service limit, not evidence of incorrect numerical results.

The [exact source, pin, hash and complete failure](gams-candidates/stdlib-pca/README.md) are retained for local investigation. No checked PCA driver is published, and L13b remains source-supported. The separate retained forpca numerical failure is unchanged. No backend limit was relaxed or numerical source patched; outer_product is the tenth successful example.

## Classification and provenance

The [Netlib GAMS taxonomy](https://netlib.org/misc/gams.html) supplies broad searching N5 for order-statistic selection and sorting N6 for active/associated sorting and sorted unique sets. D1a11 covers other vector operations (array differences and cross products), D1b1 covers matrix initialization, D1b6 covers rank-one multiplication, and broad D1b covers tensor-product matrix operations. A finer passive-only sorting or numerical-derivative label would misdescribe these demonstrated interfaces.

Pinned public APIs, implementations and author tests were reviewed. The checked drivers are independent MIT consumers; upstream implementation and test bodies were not copied, and upstream license terms remain separate. These are bounded correctness checks, not timing benchmarks. Loading a driver does not submit a job.

### stdlib-select-reference (N5)

Independent API consumer; pinned sources and author tests reviewed. Every rank of 186 REAL64 arrays (lengths 1..31, six deterministic dyadic families): 2,976 calls against independent insertion-sort order statistics. Includes ascending, descending, all-equal, signed, modular and repeated-block values. Check partial partition and complete multiset preservation. Broad N5 classification describes order-statistic searching, without claiming a full sort. Empty/invalid ranks, bounded-search options, NaNs, other types/kinds and performance unverified.

### stdlib-arg-select-reference (N5)

Independent API consumer; pinned sources and author tests reviewed. Every rank of 186 REAL64 arrays (lengths 1..31, six deterministic dyadic families): 2,976 calls against independent insertion-sort order statistics. Includes ascending, descending, all-equal, signed, modular and repeated-block values. Check returned index, index permutation, partial partition and unchanged values; initial index permutations include reverse order. Tie identity is not prescribed. Broad N5 classification describes order-statistic searching, without claiming a full sort. Empty/invalid ranks, bounded-search options, NaNs, other types/kinds and performance unverified.

### stdlib-sort-index-reference (N6)

Independent API consumer; pinned sources and author tests reviewed. 780 REAL64 sorting calls: lengths 0..64, six finite dyadic families, ascending/descending. Independent stable insertion sort supplies all keys and original-position associations, including empty and duplicate-heavy inputs. sort_index actively sorts keys and returns the original permutation; it is not a passive-only argsort. Broad N6 avoids implying a passive-only interface. NaNs/infinities, workspace options, other payload/index kinds and performance unverified.

### stdlib-sort-adjoint-reference (N6)

Independent API consumer; pinned sources and author tests reviewed. 780 REAL64 sorting calls: lengths 0..64, six finite dyadic families, ascending/descending. Independent stable insertion sort supplies all keys and original-position associations, including empty and duplicate-heavy inputs. Unique dyadic payloads verify the corresponding permutation and stability. Broad N6 avoids implying a passive-only interface. NaNs/infinities, workspace options, other payload/index kinds and performance unverified.

### stdlib-unique-reference (N6)

Independent API consumer; pinned sources and author tests reviewed. 390 exact sorted REAL64 unique-set comparisons, lengths 0..64 and six duplicate-containing dyadic families. Independent bounded-bin membership scan supplies the sorted set without calling a sorting API. Checks count, values, finiteness and input preservation; empty/constant inputs included. sorted_output=true and tolerance=0 only; hash-based unsorted mode, approximate equality, nonfinite values, other types and performance unverified.

### stdlib-differences-reference (D1a11)

Independent API consumer; pinned sources and author tests reviewed. 325 REAL64 adjacent-difference calls on lengths 0..24, orders 0..6, plain and (for positive orders) with prepend/append arrays. Independent binomial stencil sum supplies each answer rather than repeated differencing. Exact bounded dyadic arithmetic, output size, finite values and input preservation checked; includes empty/short inputs and order zero identity. D1a11 describes an array difference operator, not a step-scaled derivative approximation. Rank-two/dimension options, negative orders, other kinds and performance unverified.

### stdlib-cross-product-reference (D1a11)

Independent API consumer; pinned sources and author tests reviewed. 2,154 REAL64 vector pairs: nine ordered basis pairs and 2,145 bounded dyadic pairs, including zero/parallel cases. Independent Levi-Civita determinant sum, antisymmetry and both orthogonality identities checked exactly; finite results required. Other kinds, overflow/underflow extremes, arbitrary floating conditioning and performance unverified.

### stdlib-kronecker-reference (D1b)

Independent API consumer; pinned sources and author tests reviewed. 432 REAL64 Kronecker products over 144 rectangular shape pairs and three sign/zero families. Independent flattened output-index formulas check every entry, and scalar contractions check (A tensor B)*vec(X)=vec(B*X*transpose(A)) in Fortran column-major order. Exact bounded dyadic arithmetic and finite values. Broad D1b avoids confusing tensor products with an ordinary matrix-multiplication API. Empty inputs, other kinds, extreme scales and performance unverified.

### stdlib-diagonals-reference (D1b1)

Independent API consumer; pinned sources and author tests reviewed. 84 REAL64 diagonal constructions for lengths 1..12 and offsets -3..3, each with full zero/off-diagonal entry checks. 168 independent extractions: embedded vectors plus separately filled dense matrices. Exact bounded dyadic references, finite values and shape checks. D1b1 describes matrix initialization; extraction is a checked companion operation. Rectangular extraction, empty vectors, out-of-range offsets, other kinds and performance unverified.

### stdlib-outer-product-reference (D1b6)

Independent API consumer; pinned sources and author tests reviewed. 224 REAL64 rectangular outer products: rows 1..8, columns 1..7 and four bounded dyadic families including a zero factor. Check every entry, independent scalar-dot rank-one matrix action, vanishing adjacent two-by-two minors, Frobenius identity, shape and finite results exactly. Complex conjugation, other kinds, empty inputs, extreme scales and performance unverified.

## Provenance and actual output

### stdlib-select-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-select-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-select-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_selection.f90#L2350) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_selection.f90)

```text
Every rank on 186 finite duplicate-containing arrays versus independent insertion sort: 2976
PASS stdlib-select-reference
```

### stdlib-arg-select-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-arg-select-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-arg-select-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_selection.f90#L5022) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_selection.f90)

```text
Every rank on 186 finite duplicate-containing arrays versus independent insertion sort: 2976
PASS stdlib-arg-select-reference
```

### stdlib-sort-index-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-sort-index-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-sort-index-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_sorting.F90#L1830) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_sorting.F90)

```text
Stable ascending/descending key and association comparisons, lengths 0..64: 780
PASS stdlib-sort-index-reference
```

### stdlib-sort-adjoint-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-sort-adjoint-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-sort-adjoint-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_sorting.F90#L1743) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_sorting.F90)

```text
Stable ascending/descending key and association comparisons, lengths 0..64: 780
PASS stdlib-sort-adjoint-reference
```

### stdlib-unique-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-unique-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-unique-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_sorting.F90#L2015) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_sorting_unique.f90)

```text
Sorted unique sets versus independent bin membership, including empty arrays: 390
PASS stdlib-unique-reference
```

### stdlib-differences-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-differences-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-differences-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_math.F90#L653) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_stdlib_math.F90)

```text
Array differences versus independent binomial stencils, orders 0..6, with/without padding: 325
PASS stdlib-differences-reference
```

### stdlib-cross-product-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-cross-product-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-cross-product-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L517) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg.f90)

```text
Cross products versus Levi-Civita determinant sums, antisymmetry and orthogonality: 2154
PASS stdlib-cross-product-reference
```

### stdlib-kronecker-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-kronecker-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-kronecker-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L475) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg.f90)

```text
Rectangular tensor products versus independent index and column-major vec identities: 432
PASS stdlib-kronecker-reference
```

### stdlib-diagonals-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-diagonals-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-diagonals-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L241) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg.f90)

```text
Offset diagonal construction calls=84, independent/embedded extractions=168
PASS stdlib-diagonals-reference
```

### stdlib-outer-product-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-outer-product-reference) / [Driver source](../fpm_catalog/gams-drivers/stdlib-outer-product-reference.f90) / [Pinned procedure](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/src/stdlib_linalg.f90#L435) / [Author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_linalg.f90)

```text
Rectangular rank-one products: entries, independent matrix action, minors and Frobenius identity: 224
PASS stdlib-outer-product-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-select-reference stdlib-arg-select-reference stdlib-sort-index-reference stdlib-sort-adjoint-reference stdlib-unique-reference stdlib-differences-reference stdlib-cross-product-reference stdlib-kronecker-reference stdlib-diagonals-reference stdlib-outer-product-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
