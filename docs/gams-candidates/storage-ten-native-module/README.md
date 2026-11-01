# Retained nc4fortran native-module consumer probe

Consumer preparation failure: the package exports nc4fortran but the immutable consumer manifest does not expose the external netcdf Fortran module to FPM dependency discovery. The source never compiled or ran; this is not a numerical or upstream I/O defect. The corrected consumer uses ISO_C_BINDING interfaces to the already-linked native NetCDF C API for independent indexed reads.

Package pin: 942ac4f83380acdef463002f555aebf30f3c46ac.

Normalized UTF-8/LF source SHA256: 61ab51faef568a56d2e0b23c5145af6105ba9f94f2d13010e2a3e5488bda57cc.

[Exact source](driver.f90) / [Full service result](result.json)
