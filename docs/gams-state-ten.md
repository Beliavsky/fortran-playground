# Ten checked configuration, state and reference drivers

Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. All reused existing package libraries and compiled only mains and executables. The [verification report](gams-state-ten-validation.json) preserves pins, source hashes and complete output. The [retained probes](gams-candidates/state-ten-first-probes/README.md) distinguish consumer/API corrections from unsupported package behavior. GAMS categories are not exhausted.

## Array bounds (array_range, R)

The driver checks 784 nonempty rank-2 arrays: both lower origins range from -3 to 3 and both extents from 1 to 4. The descriptor constructor receives actual intrinsic bounds, but exact expected endpoints come independently from the allocation parameters. All 3,136 bound entries and 4,900 visited elements are checked; traversal sums use closed-form arithmetic-progression formulas rather than another traversal. Zero extents, malformed bound arrays and scalar/vector/tensor aggregate constructors remain unverified.

## Typed values and owned arrays (any, N4)

Thirty-two fresh groups contain an INT32 scalar, dyadic REAL64 scalar, logical, nonempty character string, integer vector and REAL64 matrix. Vectors have lengths 1..32 and matrices shape [2,length]. Original input arrays are overwritten after wrapping; extraction must recover the earlier exact values and shape, establishing owned copies for these cases. All 1,712 scalar/array references pass. Type-bound assignment is used; the initial attempted module-level assignment import was a consumer error.

Empty values are deliberately outside the successful scope. After fixing the import, the empty-string fixture segfaulted; a second probe with nonempty strings and empty arrays segfaulted at array extraction. Exact mains/results are retained. The published driver uses nonempty inputs and does not fix these GNU 16 compiler/library interactions. Reassigning populated buffers, type mismatches, container copying and all ranks/kinds remain unverified.

## Format descriptors (fed, N1)

There are 550 exact full-record comparisons against independently constructed native Fortran format strings. Integer widths 1..12 combine minimum digits 0..min(width,6) and five signed/zero/large values. Fixed-point widths 4..18 in steps of two combine decimal places 0..4 and five exact binary values. Five concatenated integer/character/real formats are also checked. Overflow fields and trailing output blanks remain part of the comparison.

The oracle follows reviewed FED normalization: a zero minimum omits .m (it is not native Iw.0 zero suppression), and real width is raised to at least d+2. The first incorrect native-format assumptions are retained as consumer reference errors, not package defects. Exponential, complex, user-defined, locale and cross-compiler rounding behavior remain unverified.

## INI scalar/default values (io_utilities, N1)

Thirty-six self-contained INI files check 180 exact references for signed integers, dyadic reals, text, absent-key defaults and all six reviewed true spellings. They contain a section header and inline comments, but descriptors use wildcard sections. Expected values come from the file-generation parameters. Files are deleted inside the sandbox. False spellings, section-specific matching, malformed input and CLI filename overrides remain unverified.

## Nested configuration and dynamic arrays (config-fortran, N1)

Twenty-four fresh configurations/files check integer, REAL64, logical and text values, solver%dt nested keys, a retained default and dynamic arrays of lengths 1..8. Exact expected eighths are written and independently compared after reading; CFG_get_size must match the requested length. There are 228 scalar/array references. Each object is explicitly cleared. Repeated reads into the same configuration, malformed files, unknown keys and CLI inputs remain unverified.

## Mixed dictionaries and deletion (fdict, N4)

Eight 49-key dictionaries store integer, dyadic REAL64, text and three-element integer-array values. Reverse-order lookups must match independent formulas; source arrays are overwritten after insertion to check ownership. Every even key is then deleted, and selected odd survivors plus the base key are checked before explicit destruction. There are 488 typed lookups. The character assign overload has no success keyword; correcting that consumer error preserves the numeric/array status checks. Missing/type-mismatched lookups, duplicate-key policy, dictionary copying and every hash collision remain unverified.

## C-backed vector and map state (qcontainers, N4)

Eight traces perform 96 vector appends each, periodic indexed replacements, FIFO removal to empty, and hash-map insertion/replacement across 17 keys. A plain array and indexed membership/value tables supply 51,080 exact value/presence references. Absent map keys, vector clear, map clear/reuse and scope finalization are checked.

Appending to the cleared vector is excluded: the retained probe reports success but returns an incorrect payload, and source review shows qvector_clear resets the C element size to zero. The successful driver does not append afterward or patch the library. Map clear/reuse still passes. Payloads are integers; iterators, object copying, all ownership paths, memory leaks and thread safety remain unverified.

## SQLite transactions and queries (sqliteff, N1)

An in-memory database receives 64 prepared/bound inserts for keys -32..31 and values key/8. Each insertion checks SQLITE_DONE and statement reset. After commit, an update and sentinel-row insertion are rolled back. Five exact aggregate references (count, sum, average, minimum and maximum) verify restoration. Deleting keys divisible by three leaves 43 rows; ordered key/value pairs must match an independent integer loop, followed by SQLITE_DONE. All statements are finalized and the database closed. Disk persistence, concurrent transactions, text/NULL, error recovery and general N5 searching are outside this N1 driver.

## Integer expression parsing (shunting-yard-fortran, N3)

The driver supplies independently written integer operand/binary callbacks and checks 437 valid bounded expressions against direct arithmetic. Seventy-two combinations of a=1..6, b=1..4, c=1..3 each generate six precedence/parenthesis/subtraction/division templates. Five fixed cases check right-associative powers, grouped powers, mixed precedence, binary negation as 0-x and ignored spaces. All expected division results are exact integers and powers stay safely bounded.

Unary registration is intentionally absent. The retained registered-unary-minus probe evaluates 1-1-1 as 1 instead of -1: register_unary adds the minus token to a shared right-associative list that is also consulted for binary operators. The binary-only consumer passes without a library change. Unary/real-function behavior, malformed syntax, overflow, registration isolation and arbitrary callback types remain unverified.

## Exact SI constants and photon energies (fundamental_constants, R)

The selected Planck constant, speed of light and elementary charge match the defining decimal values in the [NIST 2022 CODATA listing](https://physics.nist.gov/cuu/Constants/Table/allascii.txt). The independent [Python Fraction oracle](../fpm_catalog/gams-drivers/references/photon_vectors.py) uses exact rational arithmetic to generate [saved energy vectors](../fpm_catalog/gams-drivers/references/photon-vectors.json); no package imports supply the reference. Source/data hashes are recorded with the driver.

Twelve integer wavelengths [1,2,10,121,250,400,500,656,800,1064,10000,1000000] nm give 24 joule/electron-volt energy references. The native REAL64 computation must agree within relative tolerance 2e-15; its observed maximum was 2.22045e-16. This checks three exact constant values and their use in unit conversion, not the entire collection or the accuracy of constants with experimental uncertainty.

## Provenance and actual output

Pinned APIs, implementations and available author examples were reviewed. These are independent MIT consumers; upstream implementation/example bodies are not copied and upstream licenses remain separate. Exact failed sources/results are retained with hashes and pins. No unsupported probe is promoted to successful verification, and loading an example does not submit a job.

### array-bounds-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=array_range&example=gams-array-bounds-reference) / [Driver source](../fpm_catalog/gams-drivers/array-bounds-reference.f90) / [Pinned procedure](https://github.com/degawa/array_range/blob/cd21ccb982e23de9c2df44c12edab44dd84562dc/src/type/array2d_range_type.f90#L1) / No pinned author example; API reviewed directly.

```text
784 nonempty rank-2 arrays; 3136 bound entries and 4900 traversed elements checked.
Negative/zero/positive origins, asymmetric shapes and independent arithmetic-progression sums.
Zero extents, invalid bound arrays and vector/tensor aggregate constructors unverified.
PASS array-bounds-reference
```

### any-values-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=any&example=gams-any-values-reference) / [Driver source](../fpm_catalog/gams-drivers/any-values-reference.f90) / [Pinned procedure](https://github.com/degawa/any/blob/b9eb5e3fdc8f162ae8f2c5d8d026537ed2397830/src/any_t.f90#L1) / [Author test](https://github.com/degawa/any/blob/b9eb5e3fdc8f162ae8f2c5d8d026537ed2397830/example/demo.f90)

```text
32 fresh typed-value groups; 1712 scalar/array value references on nonempty inputs.
INT32, dyadic REAL64, logical and character scalars; owned rank-1/rank-2 array copies.
Empty values, populated-buffer reassignment, type mismatches and arbitrary ranks/kinds unverified.
PASS any-values-reference
```

### fed-format-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fed&example=gams-fed-format-reference) / [Driver source](../fpm_catalog/gams-drivers/fed-format-reference.f90) / [Pinned procedure](https://github.com/degawa/fed/blob/d735aa2b3bd6b20840bcc16ff569e8cfc0492267/src/fed.f90#L1) / [Author test](https://github.com/degawa/fed/blob/d735aa2b3bd6b20840bcc16ff569e8cfc0492267/example/integer.f90)

```text
Exact comparisons against independently constructed native Fortran formats: 550
Integer widths/minimum digits, fixed-point decimals, overflow fields and concatenated columns.
Exponential/complex/user-defined descriptors, locale and cross-compiler rounding unverified.
PASS fed-format-reference
```

### keyvars-config-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=io_utilities&example=gams-keyvars-config-reference) / [Driver source](../fpm_catalog/gams-drivers/keyvars-config-reference.f90) / [Pinned procedure](https://github.com/arjenmarkus/io_utilities/blob/f0551aad0b46aa7aac1c442a3c576ecc90028f72/src/keyvars.f90#L45) / [Author test](https://github.com/arjenmarkus/io_utilities/blob/f0551aad0b46aa7aac1c442a3c576ecc90028f72/test/test_keyvars.f90)

```text
36 generated INI files; 180 exact scalar/default references.
Signed integer/dyadic real values, six true spellings, comments, string values and absent-key defaults.
Wildcard sections only; malformed input, false spellings, section-specific matching and CLI overrides unverified.
PASS keyvars-config-reference
```

### config-file-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=config-fortran&example=gams-config-file-reference) / [Driver source](../fpm_catalog/gams-drivers/config-file-reference.f90) / [Pinned procedure](https://github.com/jannisteunissen/config_fortran/blob/106354774b2e6138161952f434c69e7913fa2000/m_config.f90#L1) / [Author test](https://github.com/jannisteunissen/config_fortran/blob/106354774b2e6138161952f434c69e7913fa2000/example_1.f90)

```text
24 fresh configuration/file fixtures; exact scalar and array references: 228
Integer, dyadic real, logical, text, nested keys, dynamic arrays and retained defaults.
Valid generated inputs only; malformed files, unknown keys, repeated reads and CLI input unverified.
PASS config-file-reference
```

### fdict-values-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fdict&example=gams-fdict-values-reference) / [Driver source](../fpm_catalog/gams-drivers/fdict-values-reference.f90) / [Pinned procedure](https://github.com/zerothi/fdict/blob/6ac903d4c0c524d45b948281a18b9656936c0197/src/dictionary.fypp#L1) / [Author test](https://github.com/zerothi/fdict/blob/6ac903d4c0c524d45b948281a18b9656936c0197/README.md)

```text
Eight 49-key dictionaries; exact typed lookup references: 488
Integer/REAL64/text/array values, owned array copies, reverse lookup order and deletion survivors.
Missing/type-mismatched lookups, duplicate-key policy, dictionary copying and all hash collisions unverified.
PASS fdict-values-reference
```

### qcontainers-state-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=qcontainers&example=gams-qcontainers-state-reference) / [Driver source](../fpm_catalog/gams-drivers/qcontainers-state-reference.f90) / [Pinned procedure](https://github.com/darmar-lt/qcontainers/blob/bb1423dded02588898530c3ac7aa709e3f4eb5c3/qcontainers_f/qvector.F90#L1) / [Author test](https://github.com/darmar-lt/qcontainers/blob/bb1423dded02588898530c3ac7aa709e3f4eb5c3/tests/test_vector.f90)

```text
Eight vector/map traces; exact value/presence references: 51080
C-backed growth, indexed edits, FIFO removal, map replacement/presence, vector clear and map clear/reuse.
Vector append-after-clear has a retained failure; iterator order, copying and thread safety unverified.
PASS qcontainers-state-reference
```

### sqlite-transactions-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=sqliteff&example=gams-sqlite-transactions-reference) / [Driver source](../fpm_catalog/gams-drivers/sqlite-transactions-reference.f90) / [Pinned procedure](https://github.com/everythingfunctional/sqliteff/blob/9b377c976698a7da671536e5e2539146ab734ca6/src/sqliteff.f90#L1) / No pinned author example; API reviewed directly.

```text
64 prepared/bound inserts; rollback restores five exact aggregates; 43 ordered rows after deletion.
In-memory database, commit/rollback, statement reset/finalize and independent integer/dyadic references.
Disk persistence, concurrent transactions, text/NULL values and database error recovery unverified.
PASS sqlite-transactions-reference
```

### shunting-yard-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=shunting-yard-fortran&example=gams-shunting-yard-reference) / [Driver source](../fpm_catalog/gams-drivers/shunting-yard-reference.f90) / [Pinned procedure](https://github.com/14NGiestas/shunting-yard-fortran/blob/ff62d83502bc5fdf77f2750c3538b8634a543b91/src/parser.f90#L105) / [Author test](https://github.com/14NGiestas/shunting-yard-fortran/blob/ff62d83502bc5fdf77f2750c3538b8634a543b91/app/main.f90)

```text
437 exact integer expression references; six generated templates and five precedence/associativity fixtures.
Nested parentheses, binary subtraction, exact integer division, right-associative powers and ignored spaces.
Valid bounded integers only; unary registration, syntax errors, real functions and overflow unverified.
PASS shunting-yard-reference
```

### codata-photon-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fundamental_constants&example=gams-codata-photon-reference) / [Driver source](../fpm_catalog/gams-drivers/codata-photon-reference.f90) / [Pinned procedure](https://github.com/vmagnin/fundamental_constants/blob/3e18620ab7813fd9f02e8dcf05c48f0ca13f2ec0/src/CODATA_2022_constants.f90#L1) / No pinned author example; API reviewed directly.

```text
Three exact SI constant literals and 24 rational-derived photon-energy references.
Maximum relative photon-energy discrepancy:    2.22045E-16
Wavelengths 1..1000000 nm; joules and electron volts checked with independent Python Fraction vectors.
Selected exact constants only; uncertain CODATA values and the complete constants collection unverified.
PASS codata-photon-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers array-bounds-reference any-values-reference fed-format-reference keyvars-config-reference config-file-reference fdict-values-reference qcontainers-state-reference sqlite-transactions-reference shunting-yard-reference codata-photon-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
