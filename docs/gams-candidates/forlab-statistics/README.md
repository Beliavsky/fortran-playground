# Retained Forlab statistics probes

Both saved sources have normalized UTF-8/LF SHA256 hashes, exact pins and full hosted results.

The median/percentile probe built successfully but crashed with SIGSEGV (exit 139), before output, at its first median call with n=1. The pinned median calls sort(x); the cause of the crash is not diagnosed. The combined procedure record has no checked driver. This probe does not establish behavior for larger medians or the percentile calls that were not reached. A separately verified polynomial forward-difference example replaces it.

The first chi-square consumer used a local variable called shape, which hid the SHAPE intrinsic in an unused matrix-check helper and caused compilation to fail. Renaming the local variable gamma_shape fixes this consumer error. The corrected probability consumer also uses a stricter relative comparison with a 1e-20 reference floor, so tiny PDF/CDF values remain checked. No numerical assertion was relaxed or upstream numerical source patched.

The first polynomial-difference probe also tried cumulative reconstruction. It built, passed the first-difference quotient checks, then returned 4.458984375 instead of 4.486328125 when reconstructing the first original value after the initial condition. Its source and complete numerical-failure result are retained. In src/forlab.F90:1908, cumsum calls sort(x,1) before accumulating; the sorted-prefix semantics do not reconstruct input-order prefixes. The combined procedure record has no checked driver. The published diff-only consumer removes that separate API and independently checks all three forward-difference orders on all 48 grids. No cumsum success is inferred from it.
