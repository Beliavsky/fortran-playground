# Ten checked data-handling drivers

Ten independently written API consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. All reused existing package libraries and compiled only their mains and executables. The [verification report](gams-data-ten-validation.json) retains pins, normalized source hashes, compiler/build details and complete output. These extend GAMS N data-handling coverage. Numerical records with known failures are not relabeled as verified. GAMS categories are not exhausted.

## Editable integer vectors (fortran_vector, N4)

Twelve traces begin with capacities 1..5 and append 96 scalar values modulo 19, then six four-element batches modulo 23. A separate plain-array state model checks every active value after each append, removal of the fixed value zero, twelve positional deletions, cut, pop-to-empty and clear/reinitialize. There are 2,622 checked operations and 143,017 element references. Removal arguments do not alias the container storage. Unique, sorting, invalid indices and self-aliased remove arguments remain unverified.

## Integer sets (integer_set, N4)

Eight traces apply 240 deterministic edits to paired 32-bit and 64-bit sets. Keys lie in [-50,50]; 64-bit payloads add 5,000,000,000. A Boolean membership array independently tracks duplicate insertion and present/absent removal. Every check rejects duplicate elements and compares complete membership. The 32-bit set is also sorted and must be strictly ascending. Clear/reuse precedes explicit destruction. There are 1,944 paired membership checks and 218,354 stored-value references. 64-bit sorting, integer extrema and reuse after destroy remain unverified.

## Heterogeneous linked lists (slinked-list, N4)

Twenty cycles use lengths 1+modulo(17*cycle,61) and rotate integer, default-real and fixed-width character values. An independent formula checks all 601 elements, dynamic types and insertion order. Emptying retains capacity; later appends replace values/types in existing nodes. Maximum previous length supplies the capacity reference. Iterator exhaustion and explicit finalization are checked. Empty-list iterators, mutation during iteration, arbitrary pointer lifetimes and memory-leak behavior remain unverified.

## Scanner cursor semantics (scanner, N3)

Sixty-four generated printable-ASCII strings of lengths 1..64 are compared with direct string indexing. The consumer checks 3,232 cursor positions through forward/backward traversal, immutable peek/peek_back, remaining count, failed end advances, oversized clamped moves and forward jump_to searches. The jump reference starts after the current position. Empty input, Unicode semantics, reverse jumps and negative movement counts remain unverified.

## Token fields and callbacks (fortran-tokenizer, N3)

Sixty-four constructed records contain named fields separated by space, comma, semicolon, tab and newline. Separators repeat and occur at both ends; fields starting with ! are ignored. The expected 423 retained strings are saved while constructing the input, rather than parsed by a second tokenizer. Stored procedure-pointer callbacks and optional callback arguments alternate across records. Empty input and clearing every returned list are checked. Default validator, quoting/escaping and Unicode lexical rules remain unverified.

## Delimiter enclosure (enclose, N3)

All 820 strings through width three over ()[]{}<>x are checked with a separate SELECT CASE bracket-pair involution. The reverse closing sequence must match get_closing_brackets. Three trimmed ASCII payloads give 2,460 fixtures for automatic enclosure, literal repeated delimiters and explicit END closures. Empty delimiters and payloads are included. Arbitrary trailing-blank preservation and UTF-8 delimiter semantics remain unverified.

## Growable matrices (rearrayfx, N4)

Sixteen traces combine row counts [1,2,3,4] and overprovision factors [1,1.5,2,3]. The column schedule [1,3,2,7,4,12,1,5] gives 128 explicit allocations through spare capacity and new backing storage. The active prefix shared with the preceding view must survive before new values are assigned. Explicit dyadic values and a final shape-changing 2-by-3 array assignment supply 2,096 scalar references. Inactive capacity, zero sizes, container-object copying, row-changing preservation and memory-leak behavior remain unverified. Library allocation debug messages are retained in the saved output.

## UTF-8 code points (string-utf-8, N3)

Thirty-three fixtures of lengths 0..32 use integer code points [65,233,8364,119070,769,32] and an independent arithmetic UTF-8 encoder. They cover one-to-four-byte encodings, a combining mark and space. Direct construction supplies byte references for round trips, positive substrings of up to three code points, first single-code-point searches, expanding replacement of U+00E9 by U+20AC plus x, and deletion. There are 825 exact checks across 528 original code points. Malformed encoding, normalization, grapheme clusters, negative substring semantics and multi-code-point search remain unverified.

## C++ sorting and binary search (flibcpp, N6)

The 780 original-pattern arrays combine lengths 0..64, four patterns and INT32/INT64/REAL64 wrappers. Patterns are ascending, descending, duplicated modular values and alternating signs. Scalar insertion sort gives the independent reference. INT64 values add 5,000,000,000 and REAL64 values are exact eighths. All 24,960 sorted entries and 31,980 queries over keys -20..20 are checked. Duplicate hits require a valid matching index; absence requires zero. First-occurrence semantics, NaNs, custom comparators, strided arrays, ordering stability and large-size index limits remain unverified. This is class-specific N6 evidence and does not automatically verify every N5 capability.

## Modbus register encoding (fortran-modbus, N2)

The consumer checks 264 finite binary32 patterns in ABCD, BADC, CDAB and DCBA order. Eight explicit IEEE patterns include signed zeros, normal/subnormal minima, a largest finite value and an asymmetric pattern; 256 further signed patterns vary exponents and mantissas. Expected register words come directly from bit positions and a permutation table, with explicit signed Fortran 16-bit carrier conversion.

There are 1,056 independent setter and 1,056 independent getter comparisons. Setters must produce reference words; getters receive independently assembled words and must reproduce exact bits. This prevents compensating encoder/decoder errors from passing a paired round trip. The [libmodbus 3.1.11 source contract](https://raw.githubusercontent.com/stephane/libmodbus/v3.1.11/src/modbus-data.c) was reviewed alongside the pinned Fortran binding; the existing cached system package is libmodbus-dev 3.1.11-2. NaN payloads, infinities, network I/O, physical devices and other floating formats remain unverified.

## Provenance, licenses and actual output

Pinned public APIs, implementations and available author examples were reviewed. These are independently written MIT API consumers; no upstream implementation or example bodies are copied. Upstream package/system-library terms remain separate and unchanged. Loading a driver does not submit a job. No failed probes occurred in this ten-driver batch.

### vector-edits-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran_vector&example=gams-vector-edits-reference) / [Driver source](../fpm_catalog/gams-drivers/vector-edits-reference.f90) / [Pinned procedure](https://github.com/Euler-37/fortran_vector/blob/95469e2ce1162b0ede3ca3435ebd94ec6b6fee79/src/fortran_vector.f90#L78) / [Author test](https://github.com/Euler-37/fortran_vector/blob/95469e2ce1162b0ede3ca3435ebd94ec6b6fee79/test/check.f90)

```text
12 vector edit traces; checked operations: 2622; element references: 143017
Scalar/batch append, growth, fixed-value removal, positional delete, cut, pop-to-empty and reinitialization.
Unique, sorting, invalid indices and self-aliased remove arguments unverified.
PASS vector-edits-reference
```

### integer-set-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=integer_set&example=gams-integer-set-reference) / [Driver source](../fpm_catalog/gams-drivers/integer-set-reference.f90) / [Pinned procedure](https://github.com/jordan4ibanez/integer_set/blob/85d336319d6593f9768c599835342912ce0b7bb8/src/integer32_set.f90#L1) / No pinned author example; API reviewed directly.

```text
Eight paired 32/64-bit set traces; membership checks: 1944; values checked: 218354
Boolean-domain oracle; duplicate insertion, absent/present removal, clear/reuse and 32-bit sorting.
64-bit values exceed 32-bit range; 64-bit sorting, extreme integer bounds and destroy reuse unverified.
PASS integer-set-reference
```

### linked-list-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=slinked-list&example=gams-linked-list-reference) / [Driver source](../fpm_catalog/gams-drivers/linked-list-reference.f90) / [Pinned procedure](https://github.com/zoziha/slinked-list/blob/aa04fcb392466e52277200d7380913fe071fe620/src/sll_linked_list.f90#L1) / [Author test](https://github.com/zoziha/slinked-list/blob/aa04fcb392466e52277200d7380913fe071fe620/example/example_reuse.f90)

```text
20 heterogeneous list growth/reuse cycles; typed element references: 601
Integer/real/character order, dynamic type replacement, retained capacity and iterator exhaustion.
Empty-list iterator construction, mutation during iteration and pointer lifetime misuse unverified.
PASS linked-list-reference
```

### scanner-cursor-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=scanner&example=gams-scanner-cursor-reference) / [Driver source](../fpm_catalog/gams-drivers/scanner-cursor-reference.f90) / [Pinned procedure](https://github.com/freevryheid/scanner/blob/b0026498c171b615bb3dcfca55a0f20b133e22dc/src/scanner.f90#L41) / [Author test](https://github.com/freevryheid/scanner/blob/b0026498c171b615bb3dcfca55a0f20b133e22dc/app/main.f90)

```text
64 nonempty ASCII records; checked cursor positions: 3232
Exact character oracle; traversal, peek immutability, boundaries, clamped moves and forward jumps.
Empty input, Unicode character semantics, negative move counts and reverse jumps unverified.
PASS scanner-cursor-reference
```

### tokenizer-fields-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-tokenizer&example=gams-tokenizer-fields-reference) / [Driver source](../fpm_catalog/gams-drivers/tokenizer-fields-reference.f90) / [Pinned procedure](https://github.com/14NGiestas/fortran-tokenizer/blob/11ad73ea6102f86593bf2b372d56bf9fbedaebc7/src/tokenizer.f90#L1) / No pinned author example; API reviewed directly.

```text
64 generated records plus empty input; exact retained field references: 423
Five delimiters, repeated/leading/trailing separators, ignore rules and stored/argument callbacks.
Custom delimiter rules only; quoting, escaping, Unicode lexical rules and default validator unverified.
PASS tokenizer-fields-reference
```

### enclose-delimiters-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=enclose&example=gams-enclose-delimiters-reference) / [Driver source](../fpm_catalog/gams-drivers/enclose-delimiters-reference.f90) / [Pinned procedure](https://github.com/degawa/enclose/blob/d3ea2ea989296bf855f4cb07ea8db601020805f2/src/enclose.f90#L1) / [Author test](https://github.com/degawa/enclose/blob/d3ea2ea989296bf855f4cb07ea8db601020805f2/example/demo.f90)

```text
2460 payload/delimiter fixtures; 820 independently mapped closing strings.
All combinations through width 3 of paired brackets and an ordinary symbol; empty inputs included.
Automatic, repeated literal and explicit closing delimiters; UTF-8 delimiter semantics unverified.
PASS enclose-delimiters-reference
```

### rearray-growth-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rearrayfx&example=gams-rearray-growth-reference) / [Driver source](../fpm_catalog/gams-drivers/rearray-growth-reference.f90) / [Pinned procedure](https://github.com/aradi/rearrayfx/blob/be1a7b08e43b358c8ed27fa80db7896767eb9f6d/src/rearrayfx.f90#L33) / [Author test](https://github.com/aradi/rearrayfx/blob/be1a7b08e43b358c8ed27fa80db7896767eb9f6d/app/main.f90)

```text
 Debug: reallocating to size           1
 Debug: reallocating to size           3
 Debug: reallocating to size           7
 Debug: reallocating to size          12
 Debug: reallocating to size           1
 Debug: reallocating to size           4
 Debug: reallocating to size          10
 Debug: reallocating to size          18
 Debug: reallocating to size           2
 Debug: reallocating to size           6
 Debug: reallocating to size          14
 Debug: reallocating to size           3
 Debug: reallocating to size          21
 Debug: reallocating to size           2
 Debug: reallocating to size           6
 Debug: reallocating to size          14
 Debug: reallocating to size          24
 Debug: reallocating to size           3
 Debug: reallocating to size           9
 Debug: reallocating to size          21
 Debug: reallocating to size          36
 Debug: reallocating to size           4
 Debug: reallocating to size          12
 Debug: reallocating to size          28
 Debug: reallocating to size           6
 Debug: reallocating to size          42
 Debug: reallocating to size           3
 Debug: reallocating to size           9
 Debug: reallocating to size          21
 Debug: reallocating to size          36
 Debug: reallocating to size           4
 Debug: reallocating to size          13
 Debug: reallocating to size          31
 Debug: reallocating to size          54
 Debug: reallocating to size           6
 Debug: reallocating to size          18
 Debug: reallocating to size          42
 Debug: reallocating to size           9
 Debug: reallocating to size          63
 Debug: reallocating to size           4
 Debug: reallocating to size          12
 Debug: reallocating to size          28
 Debug: reallocating to size          48
 Debug: reallocating to size           6
 Debug: reallocating to size          18
 Debug: reallocating to size          42
 Debug: reallocating to size          72
 Debug: reallocating to size           8
 Debug: reallocating to size          24
 Debug: reallocating to size          56
 Debug: reallocating to size          12
 Debug: reallocating to size          84
16 growth/shrink traces; 128 explicit allocations; scalar references: 2096
Four row counts and spare-capacity factors; active prefix preservation and shape-changing array assignment.
Inactive storage, zero-sized views, copying container objects and row-changing prefix semantics unverified.
PASS rearray-growth-reference
```

### utf8-codepoints-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=string-utf-8&example=gams-utf8-codepoints-reference) / [Driver source](../fpm_catalog/gams-drivers/utf8-codepoints-reference.f90) / [Pinned procedure](https://github.com/guntherwillems/fortran-string-utf-8/blob/69751115936d5a89439555ddeb1d57537a562e64/src/string_utf_8.f90#L1) / [Author test](https://github.com/guntherwillems/fortran-string-utf-8/blob/69751115936d5a89439555ddeb1d57537a562e64/app/example.f90)

```text
33 valid UTF-8 fixtures; exact checks: 825; original code points: 528
One/two/three/four-byte code points and combining marks; substrings, single-code-point search and replace/delete.
Code points, not grapheme clusters; malformed UTF-8, normalization and multi-code-point search unverified.
PASS utf8-codepoints-reference
```

### flibcpp-sort-search-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=flibcpp&example=gams-flibcpp-sort-search-reference) / [Driver source](../fpm_catalog/gams-drivers/flibcpp-sort-search-reference.f90) / [Pinned procedure](https://github.com/swig-fortran/flibcpp/blob/334b2250230afbb419402ca2f1c0649c3b12a693/src/flc_algorithm.f90#L1) / [Author test](https://github.com/swig-fortran/flibcpp/blob/334b2250230afbb419402ca2f1c0649c3b12a693/example/sort.f90)

```text
780 typed array fixtures; 24960 sorted element references; 31980 present/absent search queries.
Lengths 0..64, duplicate and signed values; INT32, large INT64 and exact dyadic REAL64.
Search checks a valid duplicate match; NaNs, custom comparators and strided arrays unverified.
PASS flibcpp-sort-search-reference
```

### modbus-registers-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-modbus&example=gams-modbus-registers-reference) / [Driver source](../fpm_catalog/gams-drivers/modbus-registers-reference.f90) / [Pinned procedure](https://github.com/interkosmos/fortran-modbus/blob/1e99906209fbbcdd1f1bf2064a92325cf4bb05fa/src/modbus.F90#L1) / [Author test](https://github.com/interkosmos/fortran-modbus/blob/1e99906209fbbcdd1f1bf2064a92325cf4bb05fa/test/test_modbus.f90)

```text
264 finite binary32 patterns x four byte/word orders: 1056 independent setter and getter checks each.
Reference register words built from explicit IEEE bits; signed zero, subnormal and extreme finite values.
Offline conversions only; NaN payloads, infinities, network I/O and physical devices unverified.
PASS modbus-registers-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers vector-edits-reference integer-set-reference linked-list-reference scanner-cursor-reference tokenizer-fields-reference enclose-delimiters-reference rearray-growth-reference utf8-codepoints-reference flibcpp-sort-search-reference modbus-registers-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
