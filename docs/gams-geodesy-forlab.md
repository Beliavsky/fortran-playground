# Checked WGS84 coordinates and overdetermined least squares

These P and D9a1 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-geodesy-forlab-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## maptran3d: WGS84 forward/inverse coordinates (P)

The reference ellipsoid uses a=6378137 meters and flattening f=1/298.257223563. Let e2=f*(2-f), b=a*(1-f) and N=a/sqrt(1-e2*sin(latitude)**2). Independent Cartesian references are X=(N+h)*cos(latitude)*cos(longitude), Y=(N+h)*cos(latitude)*sin(longitude), Z=(N*(1-e2)+h)*sin(latitude). These are ellipsoid geometry formulas, not another call to the conversion library.

Seven latitudes [-89,-60,-30,0,30,60,89] degrees, six longitudes [-180,-90,-23,0,74,180] degrees and heights [-100,0,1000,100000] meters give 168 points. Both explicit degree and radian interfaces give 336 cases. Each forward result must be finite, preserve its geodetic inputs and agree with the reference within 5e-6 meters in every Cartesian component.

The inverse receives the independently constructed Cartesian reference, rather than the library forward result. Returned coordinates must be finite. Angular error must be <=2e-7 degrees and height error <=5e-3 meters. Longitude differences are wrapped with atan2(sin(delta),cos(delta)), so -180 and +180 are equivalent. Another eight forward calls check both exact poles at heights 0 and 1000 meters in both angle units against [0,0,+/-(b+h)]. There are 680 conversion calls in total.

Inverse conversion at the poles, where longitude is not unique, is not verified. The origin, custom ellipsoids, extreme heights, invalid coordinates and performance are also outside this scope. The broad P classification is retained; no detailed astronomy or geodesy class is invented.

## forlab: tall real single-precision least squares (D9a1)

The catalog uses forlab RPRE with 32-bit real storage. Shapes [2,1], [3,2], [5,3], signed scales -4,0.5,2, identity/Householder factors and two residual settings give 36 full-column-rank fixtures. Three vector right-hand sides each give 108 solver calls. Eighteen fixtures have prescribed nonzero residuals. These are the tall subset of the [shared least-squares fixtures](gams-least-interpolation.md).

Construct A=L(:,1:n)*diag(scale*[1,...,n])*R^T, where orthogonal factors are identity or Q=I-2*v*vT/(vT*v), v=[1,...,dimension]. For right-hand side c=1,2,3, set z_i=(2*i-c)/4 and x_reference=R*z. Construct b=A*x_reference+noise with noise zero or 0.25*c*L(:,n+1). Orthogonality gives the unique least-squares solution, residual -noise and its exact squared norm independently of forlab.

Solutions must have the expected shape and be finite. Maximum coordinate error scaled by max(1,maxabs(reference_solution)) must be <=3e-5. Prescribed residual error scaled by max(1,maxabs(b)) must be <=5e-5. The normal-equation residual A^T*(A*x-b), scaled by max(1,maxabs(b))*max(1,maxabs(A)), must be <=1e-4. The prescribed squared residual norm has normalized tolerance 2e-4. Source matrices and right-hand sides must remain unchanged. These explicit tolerances match the native single-precision configuration; no double-precision library build is substituted. The existing unrelated checksum-guarded optional-norm argument fix is reused unchanged.

## Failed underdetermined probe

**Wide systems are not verified.** The full-row-rank matrix A=[[-4,0,0],[0,-8,0]] and b=[-1,-6] have exact minimum-norm solution [0.25,0.75,0], but the pinned solver returned nonfinite values. The build passed. The [candidate source, hash and full result](gams-candidates/forlab/README.md) are retained. The published driver keeps its original accuracy thresholds and narrows the shapes; it does not fix the library or promote this failed configuration. Square-system LU, rank deficiency, matrix right-hand sides, invalid inputs and performance remain unverified.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and maptran3d author tests were reviewed without copying upstream code. Loading a link does not submit a job.

### maptran-wgs84-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=maptran3d&example=gams-maptran-wgs84-reference) / [Driver source](../fpm_catalog/gams-drivers/maptran-wgs84-reference.f90) / [Pinned procedure](https://github.com/geospace-code/maptran3d/blob/4ccc2479ae79a58b34d8e491013cfa2f60f65867/src/ecef.f90#L80) / [Author test](https://github.com/geospace-code/maptran3d/blob/4ccc2479ae79a58b34d8e491013cfa2f60f65867/test/test_mod.f90)

```text
Degree/radian geodetic cases: 336; conversion calls: 680
Additional exact forward polar-axis calls: 8
Maximum ECEF error (meters):   1.4261E-09
Maximum inverse angular error (degrees):   1.1916E-11
Maximum inverse height error (meters):   1.0523E-09
PASS maptran-wgs84-reference
```

### forlab-least-squares-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=forlab&example=gams-forlab-least-squares-reference) / [Driver source](../fpm_catalog/gams-drivers/forlab-least-squares-reference.f90) / [Pinned procedure](https://github.com/zoziha/forlab/blob/416e5612167b6133100bef4cec116322890f66f7/src/forlab.F90#L7796) / No pinned author example; API reviewed directly.

```text
Full-rank least-squares fixtures: 36; solver calls: 108
Overdetermined fixtures with prescribed nonzero residuals: 18
Overdetermined only; three vector RHS calls per fixture; native catalog RPRE.
Maximum normalized solution error:   4.1723E-07
Maximum normalized prescribed-residual error:   2.1397E-07
Maximum normalized normal-equation residual:   3.3833E-07
Forlab real storage bits: 32
PASS forlab-least-squares-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers maptran-wgs84-reference forlab-least-squares-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
