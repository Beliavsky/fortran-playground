# Retained API probes

Each saved source is paired with its normalized UTF-8/LF SHA256, exact package pin and complete hosted result.

Five roots-fortran root_scalar convenience-wrapper probes built successfully with cached-library reuse but crashed with SIGSEGV (exit 139) before numerical output. The pinned implementation creates an internal func_wrapper callback; a callback/trampoline sandbox incompatibility is a possibility, not an established diagnosis. Published drivers instead use direct solver objects and module callbacks. Their results do not verify the convenience wrapper.

The first circulant eig probe omitted allocation of caller-owned outputs. It built but stopped with an array-bound mismatch before numerical checks. This is a consumer API error; the corrected consumer allocates w(n) and v(n,n). The public interface declares lambda(:) and right(:,:), not allocatable outputs. No library source was changed.

The TOMS 748 direct-object probe also failed after building, returning a nonzero solver status with IEEE_OVERFLOW_FLAG. Its original and diagnostic consumers and complete results are retained separately. This path remains source-reviewed without a checked driver; Brent-Q is tested as a separate replacement. The diagnostic output identifies the exact first failing family and root. No assertion was relaxed.
