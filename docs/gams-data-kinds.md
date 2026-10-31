# Checked numeric parsing, FIFO storage and machine-kind drivers

These N3, N4 and R1 examples passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their main programs and executables were compiled. The [verification report](gams-data-kinds-validation.json) records source hashes, pinned revisions and actual output. GAMS categories are not exhausted.

## Numeric text parsing: fortran-fast-float (N3)

The driver checks 129 decimal strings representing `i/8`, `i=-64..64`, written with three fractional digits. Every expected value is exactly representable in binary64. Eight decimal int64 values and seven int32 values include signed minima, maxima, negative values and zero. References use native integer values; the signed minimum is formed without an out-of-range positive literal.

Further successful calls check binary `11111111=255`, hexadecimal `7FFFFFFF=huge(int32)`, Fortran `1.25D-1=0.125`, and the halfway decimal `9007199254740993`, which must round to even binary64 value `9007199254740992`. Every successful call must return OK and its exact reference value; the 129 dyadic floating results must also be finite.

Two invalid prefixes must return INVALID_INPUT. Exponent overflow `1e999`, positive and negative int64 overflow, and positive int32 overflow must return OUT_OF_RANGE. There are 148 successful calls and six invalid/overflow calls: 154 in total. Correct rounding for every decimal, underflow, NaN/Inf conventions, complete-token consumption, alternate decimal separators and parser speed are not certified. Existing package manifest adaptations and compiler settings were unchanged.

## Copied-record FIFO model: for_fifo_queue (N4)

Each C-interoperable payload contains two int64 fields: serial number `j` and checksum `j*j-7*j`. An independent array model tracks enqueue/dequeue order. Three cycles each push 40 records, pop 17, push 13, then drain the queue: 159 primary records. Every push overwrites the caller's original storage afterwards, so later retrieval also checks byte-copy semantics. Counts and empty state are compared with the model after every operation.

A second queue holds a sentinel record throughout the three cycles, then returns it unchanged, giving 160 checked records in total. Empty pops must return false and a null pointer. All popped C allocations are released with C `free`, and both fully drained queues are destroyed. The 16-byte payload keeps the library's following pointer header aligned in this sandbox. Pointer-owning values, arbitrary payload alignment, out-of-memory behavior, concurrency and leak-sanitizer coverage are outside this example.

## Portable kinds and machine inquiries: PENF (R1)

The driver checks I1P/I2P/I4P/I8P against ISO int8/int16/int32/int64 and R4P/R8P against ISO real32/real64 in this GNU environment. Public bit/byte constants and `byte_size` must report the corresponding widths. Integer and real maxima are checked against native inquiry values; smallR4P/smallR8P must equal the least positive **normal** values from TINY, not subnormal minima.

The bytes of int32 pattern `0x01020304` independently determine the observed little/big endian code. Repeated `penf_init` must preserve that code and report initialization complete. A runtime experiment repeatedly halves a perturbation until adding half of it to one becomes indistinguishable from one. Volatile real32 and real64 variables keep the arithmetic observable. Measured perturbations must equal EPSILON and iteration counts plus one must equal DIGITS, giving 24 and 53 significand bits here.

Compiler inquiries check the public environment on this sandbox; cross-platform portability and other rounding modes are not established. Quadruple precision, signed-minimum constants, ZeroR constants, character kinds, format strings and numeric/string conversions are outside this driver. In particular this R1 evidence does not verify PENF's separate N3 mapping.

## Checked links and actual output

These independently written API consumers have their own MIT notice. Author examples were reviewed for usage; upstream package licenses remain separate. Loading a link selects source without submitting a job.

### fast-float-parsing-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-fast-float&example=gams-fast-float-parsing-reference) / [Driver source](../fpm_catalog/gams-drivers/fast-float-parsing-reference.f90) / [Pinned procedure](https://github.com/perazz/fortran-fast-float/blob/195e47d90874cb1ff38598d80a7e4919c49b89d8/src/fast_float_module.F90#L1) / [Author example/test](https://github.com/perazz/fortran-fast-float/blob/195e47d90874cb1ff38598d80a7e4919c49b89d8/test/check.f90)

```text
129 exact binary-fraction decimals and 15 signed decimal integers checked.
Binary/hex integers, D exponent and a binary64 halfway case checked.
Six invalid/overflow outcomes checked; 154 parser calls in total.
PASS fast-float-parsing-reference
```

### fifo-storage-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=for_fifo_queue&example=gams-fifo-storage-reference) / [Driver source](../fpm_catalog/gams-drivers/fifo-storage-reference.f90) / [Pinned procedure](https://github.com/jordan4ibanez/for_fifo_queue/blob/b04b536589af8cf041b8e5e53484e57147fc746f/src/fifo_queue.f90#L1) / [Author example/test](https://github.com/jordan4ibanez/for_fifo_queue/blob/b04b536589af8cf041b8e5e53484e57147fc746f/test/tutorial.f90)

```text
Cycle 1: 53 cumulative copied records checked; queue drained.
Cycle 2: 106 cumulative copied records checked; queue drained.
Cycle 3: 159 cumulative copied records checked; queue drained.
160 records checked: interleaved FIFO order, copied values, empty/refill behavior, independent queues.
PASS fifo-storage-reference
```

### penf-machine-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=penf&example=gams-penf-machine-reference) / [Driver source](../fpm_catalog/gams-drivers/penf-machine-reference.f90) / [Pinned procedure](https://github.com/szaghi/PENF/blob/65061235982495b158412b70c05b228af4320d94/src/lib/penf.F90#L1) / [Author example/test](https://github.com/szaghi/PENF/blob/65061235982495b158412b70c05b228af4320d94/src/tests/penf/penf-doctest-3.f90)

```text
Integer storage bits:   8  16  32  64
R4P significand bits=24 measured epsilon=  1.1921E-07
R8P significand bits=53 measured epsilon=  2.2204E-16
Endian code=1 (verified from the bytes of 0x01020304).
PASS penf-machine-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers fast-float-parsing-reference fifo-storage-reference penf-machine-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
