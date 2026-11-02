# Quadrature-fortran: retained failed nested-integrator consumers

The exact independent 2D and 3D consumers both compiled successfully in the hosted GNU Fortran 16.2.0 sandbox (FPM 0.12.0, cached libraries reused), then stopped with SIGSEGV/process exit 139 before printing a numerical result. The source revision is 1d208fc59569a97b1c2abf9c45f7c352dcc7b318. Each adjacent result JSON saves the source path, normalized UTF-8/LF SHA256, pin and complete hosted build/run response.

These are execution failures, not compilation failures, observed numerical mismatches, or reported time/size limits. The source implementations at src/quadrature_module.F90:533..615 assign pointers to internal wrapper procedures, which is a possible compatibility issue to investigate; this is not an established diagnosis. No numerical source or sandbox configuration was changed. Both procedure mappings remain source-supported with no checked driver, and the working one-dimensional consumer remains separate.

The intended reference integrals are products of elementary monomial antiderivatives on rectangular boxes. The proposed numerical assertions were never reached successfully. The two examples are excluded from playground menus and replaced in this batch by independently checked Fullerton beta-function examples.
