# Complex GGEV: retained consumer normalization error

The original independent consumer compiled but stopped at its first Euclidean unit-norm assertion. This was a driver error: generalized eigenvectors use GGEV scaling, max(abs(real(v))+abs(aimag(v)))=1, unlike GEEV Euclidean normalization. The original exact source and full hosted result are saved with the stdlib pin and normalized UTF-8/LF SHA256 in [the result record](euclidean-norm-consumer-result.json).

The corrected published consumer changes only the two norm assertions; prescribed eigenvalues, both left/right residual equations, finite checks and exact input-preservation checks remain unchanged. No upstream numerical source was patched. This error does not establish a package numerical failure or sandbox limit. The final hosted result is in [the batch verification report](../../gams-grids-spectra-ten-validation.json).
