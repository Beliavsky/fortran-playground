# Checked decimal conversion and planar Delaunay meshes

These A6 and P drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-conversion-triangulation-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## fortran-string-to-real str2real (A6)

Eight mantissas (0, 1, 25, 12345, 9876543, .125, 12.5, 0.000125) use both signs. Each is tested without an exponent and with E/e and explicit signed exponents [-100,-12,-1,0,1,12,100]. These give 240 strings. Four additional long-mantissa cases include a positive 16-digit integer, a negative 15-digit integer and positive/negative 24-fractional-digit decimals: 244 conversions in total. Every tested string is at most 28 characters.

Each conversion has two independent references: the numeric mantissa multiplied by 10**integer_exponent, and compiler formatted READ of the same string. Long decimal reference literals are rounded by the compiler independently of str2real. Results and READ references must be finite. Nonzero values must satisfy relative error <=5e-14 against both references, including small normal values near 1e-104. Zero inputs must return exactly zero; a signed-zero convention is not required. Unlike normalization by max(1,abs(reference)), this relative criterion does not make the small-number checks trivial.

The library does not validate malformed strings. These valid-input checks do not establish malformed-input handling, every length/digit boundary, D exponents, whitespace conventions, overflow, underflow/subnormals, correctly rounded conversion or performance. Numerical agreement within tolerance is not a bitwise-rounding claim.

## GEOMPACK r8tris2: rectangle with interior points (P)

Three layouts have 5,9,13 points: square corners (-1,-1), (1,-1), (1,1), (-1,1) and the first 1,5,9 points from the fixed interior list:

```text
(0,0), (-0.7,-0.2), (0.2,-0.6), (0.65,0.1), (-0.1,0.7),
(-0.45,0.45), (0.45,0.55), (-0.55,-0.65), (0.55,-0.45)
```

Positive scales 0.5,2,8, translations (0,0) and (-3,5), and original/reversed input order give 36 triangulations. The known hull always has four vertices, so Euler references are T=2*n-6 triangles and E=3*n-7 distinct edges. Every input vertex must be used. Triangle vertices must be in range and distinct triangles must not repeat the same vertex set. Input coordinates must be finite and restored exactly after the routine returns.

All 432 triangles must be counterclockwise with twice-area >1e-14*scale**2. Their summed area must match 4*scale**2 with normalized error <=5e-12, using max(1,4*scale**2) as denominator. Undirected edges must have incidence one or two, exactly four edges must be boundary edges, and distinct edge count must equal the Euler reference. Every positive neighbor must refer to a different in-range triangle sharing the reversed edge, with a reciprocal neighbor link. Negative boundary links must form one closed four-edge cycle without repetition.

For every triangle and nonincident point p, independently form a=v1-p, b=v2-p, c=v3-p and the incircle determinant D=dot(a,a)*cross(b,c)-dot(b,b)*cross(a,c)+dot(c,c)*cross(a,b). Counterclockwise orientation makes D positive for an interior circumcircle point. All 3,360 tests require D/max(1,scale**4) <=1e-10. This checks the Delaunay empty-circumcircle condition without using another triangulation library.

No particular triangle sequence or diagonal choice is required. Cocircular ambiguities can have multiple valid solutions. Duplicate points, entirely collinear or nearly coincident sets, arbitrary hulls, extreme coordinate scales, three-dimensional meshes and performance remain unverified.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and author tests were reviewed without copying upstream code. Loading a link does not submit a job.

### str2real-decimal-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-string-to-real&example=gams-str2real-decimal-reference) / [Driver source](../fpm_catalog/gams-drivers/str2real-decimal-reference.f90) / [Pinned procedure](https://github.com/Carltoffel/Fortran-String-to-Real/blob/76fb9e4203c6ce73c31bed85b69af920893b033e/src/str2real_m.f90#L27) / [Author test](https://github.com/Carltoffel/Fortran-String-to-Real/blob/76fb9e4203c6ce73c31bed85b69af920893b033e/test/test.f90)

```text
Valid decimal conversions: 244
Two independent references per conversion: arithmetic and formatted READ.
Both signs; plain decimals; E/e with signed exponents -100..100; long mantissas.
Maximum relative arithmetic-reference error:   3.3683E-16
Maximum relative formatted-READ error:   1.6243E-16
PASS str2real-decimal-reference
```

### geompack-delaunay-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=geompack&example=gams-geompack-delaunay-reference) / [Driver source](../fpm_catalog/gams-drivers/geompack-delaunay-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/geompack/blob/b7a327ca3a13507859c42dd6fba50af0bb5d5c6a/src/r8tris2.f90#L1) / [Author test](https://github.com/jchristopherson/geompack/blob/b7a327ca3a13507859c42dd6fba50af0bb5d5c6a/test/geompack_test_routines.f90)

```text
Planar triangulations: 36; checked triangles: 432
Independent empty-circumcircle tests: 3360
Known hull/area; all vertices; edge incidence; reciprocal neighbors; boundary cycle; restored coordinates.
Maximum normalized area error:   2.2204E-16
Maximum positive normalized incircle determinant:   0.0000E+00
PASS geompack-delaunay-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers str2real-decimal-reference geompack-delaunay-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
