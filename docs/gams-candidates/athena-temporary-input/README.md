# Reused Athena input marked as a temporary

The [preserved draft](temporary-input.f90) allocated a named `array_type`
feature and reused it for multiple forward calls without changing its default
`is_temporary` flag. The first repeated-forward fixture aborted with
`free(): invalid pointer` and SIGABRT; the
[complete result](temporary-input-result.json) preserves the exact source hash,
Athena/dependency pins, cached-library reuse and backtrace.

The pinned diffstruc dependency initializes
[`is_temporary` to true](https://github.com/nedtaylor/diffstruc/blob/88565f8e01792706edc0bd7e70dde957c26122a4/src/diffstruc/diffstruc_types.f90#L66).
That flag participates in expression-graph operand ownership and cleanup.
The successful consumer marks its allocated, reused feature
`feature(1,1)%is_temporary=.false.` before forward propagation. This is an
input-lifetime correction in the consumer; the weights, activation references,
fixture selection and `2e-6` comparison tolerance are unchanged.

The corrected driver passed 2,304 forward calls across 192 fixed layers and
448 exact replay entries. The result checks these lifetimes and fixtures; it
does not establish general memory safety, all autodifferentiation graph
patterns, training or an upstream-confirmed defect. No cached library or
backend deployment changed.

The independent consumer uses the
[playground MIT notice](../../../fpm_catalog/gams-drivers/licenses/radial-dense-drivers-MIT.txt);
its header retains the relative license path from its original location.
