# SciFortran integration checks

The selected build uses `SF_INTEGRATE`, `GAUSS_QUADRATURE` and the standalone QUADPACK procedures at commit `ca4a55f49cfdf7a94e388bc3475a5db574d5de99`. It does not provide the complete SciFortran library or its `SCIFOR` umbrella module.

The unpatched module-callback consumer compiled with GNU Fortran 16.2.0, then printed `Error return code IER = 2` and stopped without reaching its `PASS` marker. Its process exit code was zero. The catalog verifier correctly rejected that result. See [the recorded diagnostic](unpatched-module-callback.json).

Long coefficients in the bundled QUADPACK files use `E` exponents, which give them default-real precision before assignment to `real(8)` arrays. The [patch](precision.patch) changes 478 such literals in DATA statements and PARAMETER array initializers to `D` exponents. It retains every decimal digit, changes no formulas, and does not change the compiler's default-real mode. The [audit](precision-audit.json) identifies every changed literal, containing procedure, target arrays and original file checksum.

To reproduce with a GNU compiler on Linux, use a checkout at that commit, copy the [checked main](../../../fpm_catalog/demos/scifortran.f90) to `main.f90`, and run:

```sh
mkdir -p check-build
gfortran -g -fcheck=all -cpp -ffree-line-length-none -Jcheck-build \
  -Isrc/SF_INTEGRATE -Isrc/quadpack \
  src/SF_INTEGRATE/GAUSS_QUADRATURE.f90 \
  src/SF_INTEGRATE/SF_INTEGRATE.f90 src/quadpack/quadpack_*.f90 \
  main.f90 -o check-build/integration
./check-build/integration
```

Apply `precision.patch` from this directory to the SciFortran checkout using `git apply`, then compile and run again. The patched consumer verifies sampled Simpson/trapezoidal rules, finite and infinite adaptive quadrature, and all six finite-interval Gauss–Kronrod rule choices against analytic answers. See [verified output](verified-output.txt).

An earlier main using internal procedures as callbacks segfaulted in the sandbox. The selected main uses module procedures; this observation does not establish that internal callbacks fail on ordinary local systems. See [the initial sandbox diagnostic](scifortran-internal-callback-failure.json).

The source export also restores the BSD-3-Clause license notice linked by `GAUSS_QUADRATURE`; its [provenance](license-provenance.json) records the license reference separately from the SciFortran source pin.
