# Retained ORDERPACK probes

Exact sources, normalized UTF-8/LF SHA256 hashes, package pins and full hosted results accompany each probe.

The first median consumer incorrectly used `medianloc(x)` as a function. The pinned API is the subroutine `call medianloc(x,loc)`. This consumer compile error was corrected; the full 325-case consumer then passed without changing assertions or library source.

The combined order-statistics consumer built but failed numerically in `orderloc` for n=4, pattern=1, k=3. The independent data are [-1.25,-2.75,1.5,0], with sorted reference [-2.75,-1.25,0,1.5]. Expected value 0; actual index 3 selects 1.5. The diagnostic source and complete output reproduce this mismatch. The pinned small-n branch in src/M_orderpack__indnth.f90:153-171 does not shift IHIGT(1) into IHIGT(2) when the fourth value lies between the first and second ordered elements. No numerical source was patched.

The combined procedure record has no checked driver. `orderval` and `orderval_special` were not reached for this failing case; this probe establishes no success or failure for them over the full case set. A separate, independently checked inverse-unique-ranking consumer replaces it in the published batch.
