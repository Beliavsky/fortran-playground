# Fullerton beta CDF: retained consumer literal error

The first generated CDF consumer failed compilation because exact zero/one reference constants were emitted as `0_wp` and `1_wp`, integer literals in an otherwise REAL64 array constructor. The exact source and complete hosted response are saved with the pin and normalized UTF-8/LF SHA256 in [the result record](integer-literal-consumer-result.json).

The corrected published consumer changes only these reference literals to `0._wp` and `1._wp`. It retains all 252 exact binomial-tail comparisons, boundedness and monotonicity checks. This was a consumer generation error, not an upstream numerical failure or sandbox limit. No upstream source was patched; the final result is in [the batch report](../../gams-transforms-structures-ten-validation.json).
