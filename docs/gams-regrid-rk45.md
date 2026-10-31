# Checked regridding and adaptive RK45

These E1a and I1a1a drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-regrid-rk45-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## REGRIDPACK: one-dimensional linear/cubic interpolation (E1a)

Grid sizes 4,7,12 use x_i=-2+5*t_i or -2+5*t_i**2, t_i=(i-1)/(n-1). Each target grid includes original nodes, quarter/half/three-quarter points of every interval and a repeated final endpoint: 4*n-2 targets. Signed function scales are -2, 0.5, 3.

Linear interpolation checks monomials of degrees 0..1; cubic interpolation checks degrees 0..3, directly against scale*target**degree. These give 108 calls. Another 18 linear calls use quadratic source values and independent interval-location loops with (1-f)*y_i+f*y_(i+1) as the reference. This separately checks piecewise-linear behavior on nonaffine data. Every successful result must be finite, return status zero and preserve source coordinates, source values and target coordinates. Maximum value error divided by max(1,maxabs(reference)) must be <=2e-12.

Eight deliberately rejected requests check size mismatch (10), unsupported interpolation mode (6), insufficient source nodes for linear/cubic methods (2), targets below/above the source interval (3), repeated source coordinates (4) and descending targets (4). Failed output arrays are not inspected. A final cubic affine recovery call checks two known values within absolute error 1e-12. In total there are 127 successful calls and 3,614 analytical value checks, plus eight rejected requests. Multidimensional overloads, low-level caller workspaces, arbitrary-function accuracy, unsorted-target support and extrapolation are not verified; extrapolation is deliberately rejected.

## diffeq: Dormand-Prince RK45 (I1a1a)

Three two-component analytical IVPs, rates r=0.5,2, forward/backward integration over [0,2], and absolute/relative tolerance pairs 1e-8 and 1e-10 give 24 runs. Each requests 17 equally spaced times, giving 408 checked solution points. With s=r*t, exact solutions are:

- Exponentials: y=[exp(s),2*exp(-s)], with RHS r*[y1,-y2].
- Polynomial: y=[1+s+s**2,2-s+0.5*s**3], with RHS r*[1+2*s,-1+1.5*s**2].
- Oscillator: y=[cos(s)+0.25*sin(s),-sin(s)+0.25*cos(s)], with RHS r*[y2,-y1].

Every run starts from the analytical value at its first time. The same solver object is reused with explicit clear_buffer calls. Maximum step size is 0.3. Callback parameters carry family/rate and an evaluation counter through the polymorphic args interface; callbacks must occur without changing family/rate. Input times and initial conditions must remain unchanged. Output shape must be [17,3], all entries finite, and returned times must match every requested time within 1e-13.

At each requested time, maximum component error divided by max(1,maxabs(exact_solution)) must be <=50*requested_tolerance. For the oscillator, absolute error in y1**2+y2**2=1.0625 must be <=100*requested_tolerance. These checks use analytical answers, not agreement between time directions or tolerance settings. The tolerances are acceptance limits, not rigorous global error bounds.

Stiff problems, event detection, continuation without resetting the buffer, all interpolant queries, malformed inputs and performance remain unverified. The upstream plotted Duffing example was reviewed for interface usage; this independent driver uses analytical models and has no plotting dependency.

## Checked links and actual output

The independently written API consumers have their own MIT notice. Upstream terms remain separate; no upstream code was copied. Loading a link does not submit a job.

### regridpack-polynomial-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=regridpack&example=gams-regridpack-polynomial-reference) / [Driver source](../fpm_catalog/gams-drivers/regridpack-polynomial-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/regridpack/blob/e47346d9244ab93f70367f16364d73217fbc0451/src/regridpack_module.f90#L22) / No pinned author example; API reviewed directly.

```text
Successful regrids: 127; analytical value checks: 3614
Expected rejected requests: 8
Uniform/nonuniform grids; linear/cubic monomials and piecewise-linear references.
Maximum normalized interpolation error:   4.4409E-16
PASS regridpack-polynomial-reference
```

### diffeq-rk45-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=diffeq&example=gams-diffeq-rk45-reference) / [Driver source](../fpm_catalog/gams-drivers/diffeq-rk45-reference.f90) / [Pinned procedure](https://github.com/jchristopherson/diffeq/blob/989b320179c23aaff4bfe72994c90e9034f50c74/src/singlestep/explicit/diffeq_rk45.f90#L32) / [Author test](https://github.com/jchristopherson/diffeq/blob/989b320179c23aaff4bfe72994c90e9034f50c74/examples/rk45_example.f90)

```text
Analytical IVP runs: 24; requested solution points: 408
RHS callback evaluations: 5616
Exponential/polynomial/oscillator; two rates, both directions and two tolerances.
Maximum normalized solution error:   1.6661E-08
PASS diffeq-rk45-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers regridpack-polynomial-reference diffeq-rk45-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
