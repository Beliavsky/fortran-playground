# Checked oscillator eigenvalues and molecular dispersion

These D4 and Z drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-dispersion-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Bare coupled oscillators: libmbd (D4)

Two oscillators have frequency pairs [1,1] or [0.5,1.5], polarizabilities [0.5,1] or [1,2], separation 2, 3 or 4 bohr, and three unit orientations: [0,0,1], [0.6,0.8,0], [1,2,2]/3. Each of 36 nonperiodic fixtures is translated by [1,-2,0.5] and run both with and without eigenvectors, giving 72 Hamiltonian calls. Bare dipole coupling is used; no atom-specific screening or damping is involved.

In principal coordinates the real 6x6 Hamiltonian splits into three symmetric 2x2 blocks. Their diagonals are a=omega1**2 and b=omega2**2; off-diagonals are c,c,-2*c where c=omega1*omega2*sqrt(alpha1*alpha2)/r**3. Each block has eigenvalues (a+b +/- sqrt((a-b)**2+4*coupling**2))/2. All six sorted eigenvalues are independently computed from these scalar formulas. Maximum error divided by max(1,maxabs(reference)) must be at most 1e-12. The zero-point energy 0.5*sum(sqrt(eigenvalues))-1.5*sum(omega) must agree within absolute 1e-12.

Scalar loops independently assemble the full oriented Hamiltonian and check H*v-lambda*v and eigenvector orthogonality within absolute 1e-12; no signs or basis choices are imposed in degenerate eigenspaces. All outputs must be finite, and library exceptions fail the driver. This checks the internal real Hamiltonian diagonalization, not a general-purpose eigensolver API. Screened/damped physical models, periodic/complex/distributed modes, unstable Hamiltonians and gradients are not verified. The driver is independently written under MIT; the package retains MPL-2.0 terms.

## PBE-D4 two-body dispersion: DFT-D4 (Z)

The author test_pbed4_mb01 supplies the PBE-D4 two-body damping parameters and energy reference -0.018578752883363366 Hartree. Its 16-atom MB16-43/01 geometry is reproduced unchanged from mstore v0.4.0; all 48 coordinate literals were checked against that release. The driver expands the existing catalog consumer with independent finite-difference and rigid-transformation checks. The adapted consumer retains LGPL-3.0-or-later and Apache-2.0 licenses and a geometry attribution notice.

The energy must match within absolute 1e-10 Hartree. All 48 Cartesian gradient components are checked using central differences at step 1e-5 bohr, tolerance 1e-6 Hartree/bohr. Net gradient must vanish within 1e-9. Translation by [1.25,1.25,1.25] bohr and an orthogonal xy rotation with cosine/sine [0.6,0.8] must preserve energy within 1e-11 and transform gradients within 1e-9. Energy and every gradient must be finite; initialization errors fail the driver. There are 99 evaluations: base, 96 displaced, one rotation and one translation.

Z marks a domain-specific molecular dispersion model. This does not verify a generic differentiation API, the physical model against experiment, other molecules, periodic systems, D4S, three-body corrections or Hessians. The published energy is an upstream regression reference, while finite differences and rigid transformations independently check gradient consistency and covariance.

## Checked links and actual output

Loading a link does not submit a job. License texts and attribution accompany the driver sources.

### libmbd-dimer-spectrum

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=libmbd&example=gams-libmbd-dimer-spectrum) / [Driver source](../fpm_catalog/gams-drivers/libmbd-dimer-spectrum.f90) / [Pinned procedure](https://github.com/libmbd/libmbd/blob/77d7ab424d21f43dea9f57734b355ce4ea4d1a42/src/mbd.F90#L1) / [Author example/test](https://github.com/libmbd/libmbd/blob/77d7ab424d21f43dea9f57734b355ce4ea4d1a42/tests/mbd_api_tests.F90)

```text
Bare two-oscillator Hamiltonian calls: 72
Maximum normalized closed-form eigenvalue error:   7.8944E-16
Maximum scalar eigenvector residual:   2.2204E-15
Maximum orthogonality error:   1.5543E-15
PASS libmbd-dimer-spectrum
```

### dftd4-dispersion-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=dftd4&example=gams-dftd4-dispersion-reference) / [Driver source](../fpm_catalog/gams-drivers/dftd4-dispersion-reference.f90) / [Pinned procedure](https://github.com/dftd4/dftd4/blob/1107ea7c7c2131719e306fd57a5f4a1579e2577e/src/dftd4.f90#L1) / [Author example/test](https://github.com/dftd4/dftd4/blob/1107ea7c7c2131719e306fd57a5f4a1579e2577e/test/unit/test_dftd4.f90)

```text
PBE-D4 dispersion energy (Hartree):    -0.01857875288336
Absolute reference error:   3.4694E-18
48 Cartesian derivatives checked by central finite differences (step 1e-5 bohr).
Maximum gradient finite-difference error:   6.9309E-13
Maximum gradient rotation error:   1.0300E-18
PASS dftd4-dispersion-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers libmbd-dimer-spectrum dftd4-dispersion-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
