# Random-array helper requested-bound failure

The pinned public create_random_array documentation calls xmin/xmax the minimum/maximum range. With explicit bounds [0,1] and a fixed intrinsic seed, this GNU 16 consumer returns values above 1. The build succeeds and reuses the cached library; the program fails its independent requested-range assertion. This is retained unsupported behavior, not a checked GAMS driver or a changed library.

Source review of src/fth_arrays.f90 shows tol * (low + (high + one - low) * x), where tol is REAL32 0.99. For [0,1], that maps intrinsic draws to approximately [0,1.98), rather than [0,1]. There is no package-source patch in this change.

Package pin: 1557b1485d8a5b042862042552f1e1a34552ca5e.
Normalized UTF-8/LF source SHA256: 68e08acdb200b12e375b51830e26d1acd34a27ab7d04453918b0d0cd91e549b6.

[Exact source](driver.f90) / [Full service result](result.json)
