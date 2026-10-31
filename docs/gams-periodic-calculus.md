# Checked polynomial calculus and orthogonal periodic distances

These H1 and P drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-periodic-calculus-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## Formal polynomial gradient, divergence and conservation (H1)

This independent API consumer uses the library's default real precision (real32 in this build) and a single coarray image. It constructs scalar f=xi**p and vector v=xi**q, xi=(x-origin)/length, for p,q=0,1,2. Orders 2 and 4, cell counts [32,64,128], and (origin,length) pairs [(-1.5,1),(0,0.5),(0.75,2)] give 162 field pairs. These translated/scaled intervals exercise the physical derivative factor 1/length rather than just unit-interval formulas.

Every gradient value on the face grid is compared with p*xi**(p-1)/length, and every divergence value on the cell-center grid with q*xi**(q-1)/length. Degree-zero reference derivatives are explicitly zero. Values must be finite and have the expected grid shape; each abs(result-reference)/(1+abs(reference)) must be <= 5e-4. There are 24,354 pointwise derivative references. The saved maximum normalized error is 6.1035e-5.

The same fields check weighted volume integrals of v*grad(f) and f*div(v), and the signed boundary flux f*v. For p+q>0, their analytic values are p/(p+q), q/(p+q), and 1; when both degrees are zero, all three are zero. There are 486 analytic integral references. The maximum absolute discrepancy must be <= 2e-4 for order 4, or <= 2e-4+2/n**2 for order 2. The additional second-order term allows discretization error in the polynomial product quadrature instead of pretending that every cubic integrand is integrated exactly.

The extended Gauss identity requires abs(volume_gradient+volume_divergence-boundary_flux) <= 5e-4 for every pair. The saved maximum integral error is 4.6539e-4 across the mixed order/grid suite, and the maximum conservation residual is 1.0316e-5. Requested order settings are exercised, but convergence order for nonpolynomial fields is not established by these checks. Laplacians, higher dimensions, PDE time integration, and multi-image execution remain unverified.

## RAFFLE periodic distances in orthogonal cells (P)

This uses the pinned RAFFLE v1.0.0 snapshot. Three orthogonal edge-length sets [1,1,1], [1,2,3], and [0.5,1.5,2] are each used directly and after two rigid Cartesian rotations, giving six cell geometries (orthogonal to real32 working precision). Two species contain five fixed fractional atom positions. Each cell has 15 modular query points plus the five exact atom positions; each query is also shifted by fractional integer vectors [0,0,0], [2,-3,1] and [-2,1,3]. Total: 360 queries.

For every query, all five specified-atom distances and the nearest-atom vector lengths from real and fractional outputs are checked: 2,520 distance references. Near-atom exclusion is explicitly disabled so an exact atom query has zero nearest distance. Fractional outputs are independently converted to Cartesian coordinates with scalar sums before their norms are checked. No particular nearest-atom identity is required in a tie; this verifies lengths, rather than all returned-vector direction semantics.

The independent oracle converts the actual rounded real32 inputs to real64, wraps the query into a reference cell with floor, and enumerates all 729 integer image offsets in [-4,4]**3 for each atom. It does not use the library's componentwise nearest-integer wrapping formula. For these orthogonal length ratios, a nearest image lies in this box; omitted images have a larger lower distance bound than a componentwise-near image, with ample margin for the small rotation-rounding errors.

Each distance must be finite and abs(result-reference)/max_cell_edge <= 128*epsilon(float32). This scale accounts for input translation/rounding and real32 Cartesian arithmetic without dividing by a zero self-distance. The saved maximum is 1.3591e-7. Directional options, ignore lists, near-atom exclusion, highly skew lattices, structure generation and performance remain unverified.

## Preserved skew-cell failure

A separate valid skew-cell probe built successfully but returned distance 0.92970967292785645 where an independent image search found 0.31679647220910667. Its lattice rows are [1,0,0], [0.8,0.6,0], [0,0,1], with one atom at the origin and query [0.49,0.49,0]. A periodic image displaced by [-1,0,0] is closer than the componentwise-wrapped image.

The [reproducer](gams-candidates/raffle-skew/README.md) retains the exact source, pin, normalized hash and complete failed result. It tests the specified-atom API; general skew-cell behavior is not promoted by the successful orthogonal driver. The failed probe is not registered as a checked driver. No source patch, relaxed comparison or disabled bounds check was introduced.

## Sources, licenses and actual output

Independent drivers have their own MIT notice; upstream terms remain separate. Formal's original Berkeley Lab terms, including its enhancements clause, remain in the [retained license](fpm-candidates/formal/licenses/LICENSE.txt); the library is not relabeled plain BSD-3-Clause. RAFFLE retains its GPL-3.0 terms. These are independent API consumers, not copies of upstream example bodies. Loading a link does not submit a job.

### formal-polynomial-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=formal&example=gams-formal-polynomial-reference) / [Driver source](../fpm_catalog/gams-drivers/formal-polynomial-reference.f90) / [Pinned procedure](https://github.com/BerkeleyLab/formal/blob/d28eee9b37b4b74abe7f21bb2ccbdfb5c17f3e8a/src/formal/tensors_1D_m.F90#L1) / [Author test](https://github.com/BerkeleyLab/formal/blob/d28eee9b37b4b74abe7f21bb2ccbdfb5c17f3e8a/example/extended-gauss-divergence.F90)

```text
Polynomial field pairs: 162
Pointwise derivative references: 24354
Analytic integral references: 486
Maximum normalized derivative error:   6.1035E-05
Maximum analytic integral error:   4.6539E-04
Maximum conservation residual:   1.0316E-05
PASS formal-polynomial-reference
```

### raffle-orthogonal-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=raffle&example=gams-raffle-orthogonal-reference) / [Driver source](../fpm_catalog/gams-drivers/raffle-orthogonal-reference.f90) / [Pinned procedure](https://github.com/ExeQuantCode/RAFFLE/blob/c152a30a1eaf94965c047bcd1a7edca07873b56f/src/fortran/lib/mod_dist_calcs.f90#L1) / [Author test](https://github.com/ExeQuantCode/RAFFLE/blob/c152a30a1eaf94965c047bcd1a7edca07873b56f/test/test_dist_calcs.f90)

```text
Orthogonal cell queries: 360
Periodic distance references: 2520
Maximum cell-scaled distance error:   1.3591E-07
PASS raffle-orthogonal-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers formal-polynomial-reference raffle-orthogonal-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
