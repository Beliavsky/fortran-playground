# Retained interoperability driver probes

These are consumer/API reference errors, not demonstrated upstream defects. The final checked drivers retain the original scope after correcting them.

## erloff-filter-reference

The INPUTS and OUT_OF_BOUNDS tags are message_type_t objects, not integers; corrected the local variable declaration/import.

Package: `erloff` at `73dfdbf54dafadb42e4705c45824b93917a20965`.
Normalized UTF-8/LF source SHA256: `f973de6fdc1e123544b86f47eb8f11225e26a3798525b13e5e49253c68c79d6c`.

[Exact source](erloff-filter-reference.f90) · [Full service result](erloff-filter-reference.json)

## npy-payload-reference

The valid Python tuple in the NPY shape header has a trailing comma. The independent header check now accepts both legal two-dimensional tuple spellings, with and without this comma.

Package: `npy-for-fortran` at `b76d22c6ece4e820d31d71825b2f774d060cd288`.
Normalized UTF-8/LF source SHA256: `8388ac3586e76f2acdce5f4182cd24d1b162041091d5eed09b5848877aee0a2f`.

[Exact source](npy-payload-reference.f90) · [Full service result](npy-payload-reference.json)
