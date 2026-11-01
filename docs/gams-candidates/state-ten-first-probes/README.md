# Retained probes from the state/data batch

These failed consumers are kept with exact source hashes, pinned package revisions and full GNU 16 service results. None is presented as a successful verification.

- **any-values-reference**: the first import of module-level assignment was a consumer error; assignment is type-bound. After correcting it, empty-string extraction segfaulted. A separate nonempty-string/empty-array probe then segfaulted at array extraction. The successful driver checks fresh nonempty buffers only; those runtime failures remain unresolved.
- **fed-format-reference**: the initial oracle treated minimum digits zero as native Iw.0. FED instead omits .m and prints zero normally. A later oracle ignored FED's minimum real width d+2. Both were incorrect consumer assumptions; the successful native-format oracle now follows these reviewed normalization rules.
- **fdict-values-reference**: the character assign overload does not accept success=. Removing that unsupported keyword corrected the consumer compilation failure; numeric/array status checks remain.
- **qcontainers-state-reference**: the cleared vector reported successful append/get but returned an incorrect payload. Source review finds qvector_clear resets the C element size to zero. The successful driver checks vector clear and hash-map clear/reuse, but does not append to the cleared vector or claim a library fix.
- **shunting-yard-reference**: registering unary minus also places the minus token in a shared right-associative list. The resulting binary expression 1-1-1 returns 1 instead of -1. The successful binary-expression driver omits unary registration; that combination remains unverified and the failure is not fixed.

Each subdirectory retains the first consumer/result; runtime and width-policy subdirectories retain diagnostic intermediate consumers. Consumers can expose an API misunderstanding, a compiler/library interaction or an implementation limitation; a failed run alone is not proof that an entire package is incorrect.
