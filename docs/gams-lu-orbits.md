# Checked LU solves and orbital state conversions

These D2a1 and P drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing libraries were reused; only mains and executables were compiled. The [verification report](gams-lu-orbits-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## linalg dense real LU (D2a1)

The driver makes 96 nonsingular square factorizations: sizes [1,2,3,5,8,13], four matrix families, scales 1e-6 and 1e6, and original/reversed row order. The families are nonsymmetric strictly row-diagonally-dominant, upper triangular, lower triangular, and a cyclic permutation with nonzero weights. Reversing rows and the permutation fixtures exercise row pivoting; 48 factorizations actually perform swaps. These are modest manufactured systems, not an ill-conditioned accuracy benchmark.

Three exact solution vectors are supplied independently: ones, alternating signed i/8, and i*(n+1-i)/4. Right-hand sides are built with scalar loops over the original dense matrix. Each is solved with the vector overload; all three are also solved together with the matrix overload. There are 384 solve calls and 3,072 known solution entries. Agreement between overloads alone is insufficient: both must match the manufactured solutions and satisfy independently recomputed scalar residuals.

Packed factors, extracted L/U, and P are requested simultaneously. Pivots must have the sequential LAPACK range i..n. The driver independently applies those row swaps to an index vector and requires the returned P to encode exactly that permutation. It checks unit lower-triangular L, upper-triangular U, and each scalar entry of P*A=L*U. The dense input, right-hand sides and packed factors must remain unchanged by the applicable factor/solve calls. The packed factor, pivot and solution arrays must have expected shapes; all successful numerical outputs must be finite.

Acceptance bounds are 2e-12 for all three measures: max abs(x-x_exact)/(1+abs(x_exact)); max absolute factorization discrepancy divided by max abs(A); and max abs(A*x-b)/(norm_inf(A)*norm_inf(x)+norm_inf(b)). The printed maxima are 4.0219e-16, 2.8115e-16 and 2.3570e-16 respectively. No solver-to-solver reference is used.

Eight additional singular factorizations use sizes [1,2,5,8] with all-zero matrices and identity matrices whose last row duplicates the first. At size one, both patterns necessarily use zero. The documented diagnostic is NaN in every returned factor/permutation entry and zero in every pivot entry, rather than a status argument. All eight diagnostics are checked; no solve is attempted with these invalid factors. Complex/sparse/transpose solves, malformed dimensions, ill-conditioned error bounds and performance remain unverified.

## Fortran Astrodynamics Toolkit orbital elements to state (P)

The driver makes 864 conversions. Eccentricities [0,0.2,0.7,1,1.5] cover circular, elliptic, parabolic and hyperbolic conics. Inclinations are [0,0.3,pi/2,pi-0.4,pi], including equatorial, polar and retrograde configurations. Node angles are [0,1.2] and periapsis angles [0,0.7], except that undefined nodes at inclination 0/pi and undefined periapses for circles use only canonical zero. The routine singularity convention is therefore respected without claiming a test of its near-singular thresholds.

True anomalies [-1.2,0,0.8,2] are used at three (mu,p) scale pairs: (1,2), (398600.4418,7000), and (1e6,2e5), in consistent units. Every fixture requires 1+e*cos(nu)>0; hyperbolic points stay inside the physical branch. Inertial position and velocity are checked against independently implemented geometric rotations: start with the planar conic state, then apply z(periapsis), x(inclination), and z(node) separately to each vector. The library uses a combined rotation matrix; this driver does not call its rotation or inverse-conversion utilities. There are 5,184 Cartesian component references.

The following physical relations supply another 6,912 scalar invariant/direction checks (eight per state):

```text
radius = p/(1+e*cos(nu))
h = cross(r,v),       |h|**2 = mu*p
e_vector = cross(v,h)/mu - r/|r|,       |e_vector| = e
energy = |v|**2/2 - mu/|r| = mu*(e**2-1)/(2*p)
radial_speed = dot(r,v)/|r| = sqrt(mu/p)*e*sin(nu)
h/sqrt(mu*p) = [sin(node)*sin(inc), -cos(node)*sin(inc), cos(inc)]
```

All returned components must be finite. Component differences are scaled by p for position and sqrt(mu/p) for velocity. Radius error is scaled by p, eccentricity error by 1+e, energy error by mu/p, and radial speed error by sqrt(mu/p); the angular-momentum relations are dimensionless as written. Each maximum must be at most 5e-12. Saved maxima are 1.1102e-15 for components and 1.9984e-15 for invariants. The checks include parabolic zero energy and both prograde and retrograde angular-momentum direction.

This is not merely a forward/inverse round trip. It verifies the named elements-to-state procedure, rather than orbit propagation, inverse elements, near-singular angle conventions, invalid conics, asymptotic hyperbolic anomalies or every toolkit method. The broad P classification is retained; no astronomy-specific GAMS subclass is invented.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and author examples were reviewed without copying upstream code. Loading a link does not submit a job.

### linalg-lu-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=linalg&example=gams-linalg-lu-reference) / [Driver source](../fpm_catalog/gams-drivers/linalg-lu-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/src/linalg_lu.f90#L18) / [Author test](https://github.com/jchristopherson/linalg/blob/cb8fb7b1c67986591083cac516eb700f47d69b68/examples/linalg_lu_example.f90)

```text
Nonsingular factorizations: 96
Vector/matrix solve calls: 384
Known solution entries: 3072
Singular NaN diagnostics: 8
Factorizations with row swaps: 48
Maximum normalized solution error:   4.0219E-16
Maximum scaled residual:   2.3570E-16
Maximum scaled factorization error:   2.8115E-16
PASS linalg-lu-reference
```

### fat-orbit-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-astrodynamics-toolkit&example=gams-fat-orbit-reference) / [Driver source](../fpm_catalog/gams-drivers/fat-orbit-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/Fortran-Astrodynamics-Toolkit/blob/3cf0a0a8ba2abf8bc4995c6da5b6abae07b45a0a/src/orbital_mechanics_module.f90#L90) / [Author test](https://github.com/jacobwilliams/Fortran-Astrodynamics-Toolkit/blob/3cf0a0a8ba2abf8bc4995c6da5b6abae07b45a0a/test/elements_test.f90)

```text
Orbital state conversions: 864
Cartesian component references: 5184
Scalar invariant/direction checks: 6912
Maximum scaled component error:   1.1102E-15
Maximum scaled invariant error:   1.9984E-15
PASS fat-orbit-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers linalg-lu-reference fat-orbit-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
