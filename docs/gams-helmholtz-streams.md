# Checked spherical Helmholtz inversion and xoroshiro streams

Both independent drivers passed GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. The existing package libraries were reused; only driver mains and executables compiled. The [verification report](gams-helmholtz-streams-validation.json) preserves package pins, source hashes, commands and output. GAMS categories are not exhausted.

## Spherepack Helmholtz and Poisson equations (I2)

The driver solves (Delta_S - lambda) u = f on the unit sphere with the public Sphere%invert_helmholtz API. Ten exact real spherical harmonics are supplied as Cartesian fields: 1; x, y, z; xy, xz, yz, (3*z*z-1)/2, x*x-y*y; and (5*z**3-3*z)/2. Their degrees are 0, 1, 1, 1, 2, 2, 2, 2, 2 and 3. For each mode the surface Laplacian eigenvalue is -l*(l+1), giving the right-hand side directly without finite differences or another solver. A mixed field uses amplitudes [1,-0.5,0.25,0.75,-1,0.5,-0.25,0.125,0.625,-0.375].

Both GaussianSphere and RegularSphere use grids [9,16], [13,24] and [17,32] in latitude/longitude counts. Shifts lambda=[0,0.25,1,3.5] exercise the Poisson branch and three invertible Helmholtz operators. At lambda=0 the constant-only fixture is skipped and the mixed field loses its constant component: the compatible solution has a zero-constant gauge. No arbitrary constant offset is removed after solving, so the returned gauge is checked too.

There are 258 solves and 86,000 grid-point references. Every returned value must be finite and max(abs(solution-exact))/(1+max(abs(exact))) must be <=2e-11. The largest observed discrepancy was 3.11709e-15. Nonzero nonzonal modes are now checked for this PDE interface, separately from the older zonal scalar-transform driver. The test uses the existing catalog recipe with its previously documented vector-workspace rank fixes; it adds no library patch. Resonant negative shifts, inhomogeneous geometry, variable coefficients, vector PDEs and convergence outside these band-limited fields remain unverified.

## rng_fortran uniform bitstream and seed/jump API (L6a21)

The pinned generator is xoroshiro128+(24,16,37). Five nonzero 128-bit seed pairs cover small integers, all-one/signed-boundary words, the package default words and mixed hexadecimal patterns. Each is tested without jumping, with set_seed default jumping, and with two explicit jump calls after do_jump=.false. Fifteen integer states and fifteen matching uniform states are interleaved for 4,096 outputs each. The test makes 61,440 calls to each output API, checks 120 exact integer prefix words, and checks all uniform values are finite, in [0,1), and exactly the upper 52 bits of their corresponding integer output divided by 2**52.

The [Python oracle](../fpm_catalog/gams-drivers/references/xoroshiro_vectors.py) uses unbounded nonnegative integers with explicit 64-bit masking and produces [saved vectors](../fpm_catalog/gams-drivers/references/xoroshiro-vectors.json). For jump references it constructs the 128-column GF(2) transition map and squares it 64 times to obtain T**(2**64). It does not import the package, use its jump-polynomial constants, or iterate 2**64 times. Two applications supply the double-jump fixture. The small-power transition-matrix checks in the test suite compare this machinery with direct repeated transitions.

Thirty independent rolling hashes cover all integer and 52-bit uniform streams, with multiplier 65599 modulo 2**31-1. Fortran signed words are interpreted as unsigned by accounting for 2**64 modulo that prime (=4); rolling arithmetic itself cannot overflow int64. Each stream is restarted and its eight-word prefix is checked again (120 entries). Reference source/data hashes are recorded with the driver. The cached package keeps its existing -fwrapv setting for intentional signed integer wraparound; this is evidence for the GNU 16 build, not a cross-compiler portability guarantee.

Exact bitstream and algebraic jump agreement do not certify statistical quality, cryptographic suitability or independence under thread scheduling. Parallel collection APIs and every possible seed are unverified. The all-zero absorbing state is deliberately excluded. The known cached-normal reseeding defect remains unresolved; this driver calls no normal sampler and does not claim to fix it.

## Sources, licenses and output

Pinned implementations, interfaces and author examples were reviewed. These are independently written API consumers; upstream implementation and example bodies are not copied. The new consumers and Python oracle have their own MIT notice; upstream Spherepack UCAR/MIT and rng_fortran GPL terms remain separate. Loading an example does not submit a job.

### spherepack-helmholtz-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=spherepack&example=gams-spherepack-helmholtz-reference) / [Driver source](../fpm_catalog/gams-drivers/spherepack-helmholtz-reference.f90) / [Pinned procedure](https://github.com/jlokimlin/spherepack/blob/e80da29462c5987162a0884baaab7434d0215467/src/type_Sphere.f90#L748) / [Author test](https://github.com/jlokimlin/spherepack/blob/e80da29462c5987162a0884baaab7434d0215467/examples/helmsph.f90)

```text
Helmholtz/Poisson solves: 258; grid-point references: 86000
Maximum normalized analytic solution error:    3.11709E-15
Gaussian/regular grids; zonal/nonzonal harmonics through degree 3; four nonnegative shifts.
Zero-shift solutions use a zero-constant gauge; resonant shifts and vector PDEs unverified.
PASS spherepack-helmholtz-reference
```

### rng-xoroshiro-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rng-fortran&example=gams-rng-xoroshiro-reference) / [Driver source](../fpm_catalog/gams-drivers/rng-xoroshiro-reference.f90) / [Pinned procedure](https://github.com/jannisteunissen/rng_fortran/blob/5ead95f436323d07fc82acc3613f66550947f256/m_random.f90#L1) / [Author test](https://github.com/jannisteunissen/rng_fortran/blob/5ead95f436323d07fc82acc3613f66550947f256/example.f90)

```text
15 interleaved streams: five nonzero seeds, no jump/default jump/two explicit jumps.
61440 integer and 61440 uniform draws; 120 exact prefixes; 30 independent rolling hashes.
Exact seeded restart entries: 120
Jump references use a GF(2) matrix raised to 2**64, not the package jump polynomial.
Bitstream/API agreement only; statistical quality, thread scheduling and normal reseeding unverified.
PASS rng-xoroshiro-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers spherepack-helmholtz-reference rng-xoroshiro-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
