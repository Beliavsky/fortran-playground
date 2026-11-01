# Ten checked storage, configuration and binding drivers

Ten independent consumers passed GNU Fortran 16.2.0 with FPM 0.12.0 in the restricted hosted sandbox. Each reused the existing package library and compiled only the main and executable. The [verification report](gams-storage-ten-validation.json) preserves pins, normalized source hashes, timings and complete output. GAMS categories are not exhausted.

## Independent references and limits

Dense undirected graph adjacency indices, vertex features and degrees are compared with plain-array oracles. The smart-pointer consumer owns integer arrays and checks nested alias counts, shared mutation, cleanup counts and a closed-form cleanup checksum. The gFTL vector/map traces check every prefix in reverse against integer/dyadic formulas.

The regex consumer enumerates every nonempty string of length at most four over 01a. and checks two pattern languages with an independently written character-state grammar. This is bounded coverage of these patterns, not a general regex conformance suite. Offline URL components and path updates are checked against generated exact strings; no network request is made.

LMDB transactions are compared with 64 formula-generated key/value states after commit, rollback, and committed replacements/deletions. Lua configuration values are checked against closed forms, including missing-key defaults and status flags. Logging must produce exactly the expected ordered warning/error text while filtering debug/info records.

NetCDF4 wrapper files are cross-read with native NetCDF C indexed calls and checked against explicit axis-dependent formulas, reversed C axis order, zero-based indices and metadata. The [Unidata variable API](https://docs.unidata.ucar.edu/netcdf-c/current/group__variables.html) and [dimension API](https://docs.unidata.ucar.edu/netcdf-c/current/group__dimensions.html) document the C signatures. Classic NetCDF additionally checks CDF-1 magic and full/indexed reads after one-cell updates. These APIs share the native NetCDF library, so this does not establish independent file-format implementation compatibility. Checks are for the pinned GNU/Linux builds.

The [retained native-module probe](gams-candidates/storage-ten-native-module/README.md) failed during FPM dependency discovery because the external netcdf Fortran module was not exposed by this consumer setup. It never compiled or ran and is not an upstream I/O defect. The successful C API consumer needs no manifest or library changes.

### graphstruc (N4)

Independent API consumer; pinned sources and available author examples reviewed. Twelve fresh dense undirected graphs with 3..14 vertices. Every incremental adjacency edge index, final degree, vertex id/owned feature and edge weight is compared with plain-array/formula references. No self-loops or duplicate edges; sparse/directed storage, removal and graph algorithms unverified.

### smart-pointers (R)

Independent API consumer; pinned sources and available author examples reviewed. 64 owned integer-array resources with nested aliases. Counts 1/2/3/2/1, target association, shared mutation, no premature cleanup and exactly-once cleanup/checksum on subroutine exit. Reassignment, cycles, explicit release, arrays of pointers, leaks and other compiler finalization behavior unverified.

### nc4fortran (N1)

Independent API consumer; pinned sources and available author examples reviewed. 24 REAL64 matrix NetCDF4 files written by the wrapper. Native NetCDF C API checks named dimension lengths, reversed C axis order and all 210 indexed values using zero-based C indices; wrapper full reads check the same 210 formula values and units. Both APIs share the underlying NetCDF library; compression, other kinds/ranks and external implementations unverified.

### jeyemhex-regex (N3)

Independent API consumer; pinned sources and available author examples reviewed. Exhaustive 340 strings of lengths 1..4 over 01a., each checked against decimal and identifier patterns using an independent character-state grammar: 680 comparisons. Empty strings, malformed patterns, captures, splitting/replacement and full regex compatibility unverified.

### fortran-lmdb (N4)

Independent API consumer; pinned sources and available author examples reviewed. 64 fixed-width text keys/values: committed inserts, aborted replacement of every value, then committed updates and deletion of keys divisible by three. Reverse-order reads compare all 192 key states with independent integer formulas and MDB_NOTFOUND. Concurrent transactions, persistence across processes, cursors, duplicate keys and large maps unverified.

### aotus (N1)

Independent API consumer; pinned sources and available author examples reviewed. 32 fresh Lua configuration files with computed triangular integers, signed dyadic reals and nested table entries; five independent value/default references each, table lengths and missing-key status bits. Malformed scripts, wrong types, callbacks, dump/reload and general Lua operations unverified.

### gftl-shared (N4)

Independent API consumer; pinned sources and available author examples reviewed. Twelve 64-insertion integer-vector/integer-to-REAL64-map traces. Every stored prefix is read in reverse and compared with independent key/value formulas: 49,920 references, including negative keys and signed dyadic values. Duplicate insertion, erase, iterators, clear/reuse, other instantiations and thread safety unverified.

### pflogger (R)

Independent API consumer; pinned sources and available author examples reviewed. 128 serial calls through a DEBUG logger and WARNING file handler. Exact ordered text oracle requires all 32 WARNING and 32 ERROR records and excludes 64 DEBUG/INFO records. Explicit free/finalize flushes the file before reading. Other severity levels, handler combinations, MPI, repeated initialization and error recovery unverified.

### fortran-curl (N3)

Independent API consumer; pinned sources and available author examples reviewed. 64 generated HTTPS URLs checked against independently generated host, explicit port, path, query and reconstructed URL after a path change: 320 exact references. Offline only. Encoding, normalization, missing components, invalid URLs, credentials and network transfers unverified.

### netcdf-fortran (N1)

Independent API consumer; pinned sources and available author examples reviewed. 24 classic REAL32 matrix files: native CDF-1 magic, dimension names/lengths, units, full and one-cell reads compared with independent formulas after overwriting the last cell with -999.5. 420 exact value references. Reader/writer share the NetCDF library; external implementations, all type/rank combinations, unlimited dimensions and parallel I/O unverified.

## Provenance and actual output

Pinned APIs, implementations and available author examples were reviewed. These independent MIT consumers do not copy upstream implementation/example bodies; upstream license terms remain separate. Only each recorded class and tested scope is verified. Loading an example does not submit a job.

### graph-storage-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=graphstruc&example=gams-graph-storage-reference) / [Driver source](../fpm_catalog/gams-drivers/graph-storage-reference.f90) / [Pinned procedure](https://github.com/nedtaylor/graphstruc/blob/51e18bedd638b935be8b9ac744b2e9f9e79213e7/src/graphstruc/graphstruc_types.f90#L103) / [Author test](https://github.com/nedtaylor/graphstruc/blob/51e18bedd638b935be8b9ac744b2e9f9e79213e7/example/example.f90)

```text
12 dense undirected graphs; every adjacency index, degree, feature and edge weight
PASS graph-storage-reference
```

### smart-lifetime-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=smart-pointers&example=gams-smart-lifetime-reference) / [Driver source](../fpm_catalog/gams-drivers/smart-lifetime-reference.f90) / [Pinned procedure](https://github.com/sourceryinstitute/smart-pointers/blob/35130adc4be4384a14b2369e5edd36d4665cd994/src/smart_pointer/sp_smart_pointer_m.f90#L1) / [Author test](https://github.com/sourceryinstitute/smart-pointers/blob/35130adc4be4384a14b2369e5edd36d4665cd994/example/user_object_smart_pointer.f90)

```text
64 owned-array lifetimes; nested aliases, shared mutation and exactly-once cleanup
PASS smart-lifetime-reference
```

### nc4-layout-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=nc4fortran&example=gams-nc4-layout-reference) / [Driver source](../fpm_catalog/gams-drivers/nc4-layout-reference.f90) / [Pinned procedure](https://github.com/geospace-code/nc4fortran/blob/942ac4f83380acdef463002f555aebf30f3c46ac/src/interface.f90#L1) / [Author test](https://github.com/geospace-code/nc4fortran/blob/942ac4f83380acdef463002f555aebf30f3c46ac/test/test_array.f90)

```text
24 NetCDF4 datasets; native indexed values and wrapper values each: 210
PASS nc4-layout-reference
```

### regex-language-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=jeyemhex-regex&example=gams-regex-language-reference) / [Driver source](../fpm_catalog/gams-drivers/regex-language-reference.f90) / [Pinned procedure](https://github.com/jeyemhex/fortran-regex/blob/2ca0043837a86a4f77df494ddad2240c1b70e576/src/regex.f90#L1) / [Author test](https://github.com/jeyemhex/fortran-regex/blob/2ca0043837a86a4f77df494ddad2240c1b70e576/example/re_example.f90)

```text
340 exhaustive strings; independent decimal/identifier grammar comparisons: 680
PASS regex-language-reference
```

### lmdb-rollback-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lmdb&example=gams-lmdb-rollback-reference) / [Driver source](../fpm_catalog/gams-drivers/lmdb-rollback-reference.f90) / [Pinned procedure](https://github.com/interkosmos/fortran-lmdb/blob/34bb1dc10e11fd470e4643135fa31fccacef7cd7/src/lmdb.F90#L1) / [Author test](https://github.com/interkosmos/fortran-lmdb/blob/34bb1dc10e11fd470e4643135fa31fccacef7cd7/test/test_lmdb.f90)

```text
192 key-state references: committed inserts, full rollback, updates and 21 deletions
PASS lmdb-rollback-reference
```

### aotus-config-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=aotus&example=gams-aotus-config-reference) / [Driver source](../fpm_catalog/gams-drivers/aotus-config-reference.f90) / [Pinned procedure](https://github.com/apes-suite/aotus/blob/2c1ec4d4629a4915929e82e873ceebf623648877/source/aotus_module.f90#L1) / [Author test](https://github.com/apes-suite/aotus/blob/2c1ec4d4629a4915929e82e873ceebf623648877/sample/aotus_sample.f90)

```text
32 Lua configurations; exact computed scalar/table values and missing defaults
PASS aotus-config-reference
```

### gftl-container-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=gftl-shared&example=gams-gftl-container-reference) / [Driver source](../fpm_catalog/gams-drivers/gftl-container-reference.f90) / [Pinned procedure](https://github.com/Goddard-Fortran-Ecosystem/gFTL-shared/blob/8009755e846560fbb389c01d76e013ddf14a7f98/src/v1/Integer32Vector.F90#L1) / [Author test](https://github.com/Goddard-Fortran-Ecosystem/gFTL-shared/blob/8009755e846560fbb389c01d76e013ddf14a7f98/src/v1/demo.F90)

```text
12 vector/map traces of 64 insertions; every prefix and reverse-order lookup checked
PASS gftl-container-reference
```

### log-filter-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=pflogger&example=gams-log-filter-reference) / [Driver source](../fpm_catalog/gams-drivers/log-filter-reference.f90) / [Pinned procedure](https://github.com/Goddard-Fortran-Ecosystem/pFlogger/blob/472c2261d0713c130aa4b2c90bfaf571586dec96/src/LoggerManager.F90#L1) / [Author test](https://github.com/Goddard-Fortran-Ecosystem/pFlogger/blob/472c2261d0713c130aa4b2c90bfaf571586dec96/examples/serial/complex.F90)

```text
128 log calls; exact 64 ordered warning/error records, debug/info filtered
PASS log-filter-reference
```

### curl-url-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-curl&example=gams-curl-url-reference) / [Driver source](../fpm_catalog/gams-drivers/curl-url-reference.f90) / [Pinned procedure](https://github.com/interkosmos/fortran-curl/blob/f29cc78fdc7701bc221a82af9bbd9ed04ef52158/src/curl_urlapi.f90#L1) / [Author test](https://github.com/interkosmos/fortran-curl/blob/f29cc78fdc7701bc221a82af9bbd9ed04ef52158/examples/url/url.f90)

```text
64 offline URLs; 320 exact component/reconstruction references
PASS curl-url-reference
```

### netcdf-slices-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=netcdf-fortran&example=gams-netcdf-slices-reference) / [Driver source](../fpm_catalog/gams-drivers/netcdf-slices-reference.f90) / [Pinned procedure](https://github.com/Unidata/netcdf-fortran/blob/48d67b73cb2a671d6d27075eb7e53085d5f9538a/fortran/netcdf.F90#L1) / [Author test](https://github.com/Unidata/netcdf-fortran/blob/48d67b73cb2a671d6d27075eb7e53085d5f9538a/examples/F90/simple_xy_wr.F90)

```text
24 classic files; exact full/indexed values after one-cell update: 420
PASS netcdf-slices-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers graph-storage-reference smart-lifetime-reference nc4-layout-reference regex-language-reference lmdb-rollback-reference aotus-config-reference gftl-container-reference log-filter-reference curl-url-reference netcdf-slices-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
