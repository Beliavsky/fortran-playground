# Checked delay equations and numerical Lua embedding

These I and S drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-delay-embedding-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Analytic delayed solutions: dde_solver (I)

Twelve problems solve `y'(t)=r*y(t-tau)` with constant history H through t=4*tau. Delays tau=[0.25,1,2], rates r=[0.5,1] and histories H=[1,-2] cover all combinations. The independent method-of-steps reference on this interval is:

```text
y(t) = H * (1 + r*t + r**2*max(0,t-tau)**2/2
                 + r**3*max(0,t-2*tau)**3/6
                 + r**4*max(0,t-3*tau)**4/24)
```

Differentiating each interval verifies the delayed equation; higher terms vanish on the tested interval. Three further oscillators solve `y'(t)=-w*y(t-tau)` with history sin(w*t) and tau=pi/(2*w), for w=[0.5,1,2]. The exact solution remains sin(w*t), because the delayed sine is -cos(w*t). Each run samples 65 times from 0 to 4*tau, including all delay knots and interior points: 975 dense-output references in total.

Every solve must return flag zero. Dense output must have shape [65,1], be finite and agree within error divided by max(1,abs(reference)) at most 2e-7. Requested relative/absolute solver tolerances are 1e-10 and 1e-12. Solver and interpolation arrays are released between runs. Module callbacks and independently written fixtures follow the interfaces reviewed in the author delay-oscillator example. No upstream implementation or test code is copied.

Only scalar retarded equations with one constant positive delay are checked. State-dependent, neutral or multiple delays, events, derivative interpolation, stiffness and every error path are outside this example. The broad I mapping is intentional; ordinary ODE subclasses do not fully describe delayed problems.

## Numeric results and state recovery: fortran-lua54 (S)

An in-memory Lua script independently defines factorial, sum of squares, a signed quadratic and a two-argument Euclidean norm. Fortran checks factorials 0!..20!, sums of squares for n=0..64 against n*(n+1)*(2*n+1)/6, and `(n-3)*(n+2)` for n=-20..20. All returned values must have the Lua integer type and agree exactly with native integer references.

Five real calls check known Pythagorean triples, including a negative argument and the zero vector. Returned values must be numeric and finite, with absolute error at most 1e-12. Every function lookup, protected call, result count and stack cleanup is checked. A negative factorial input must produce LUA_ERRRUN and its supplied diagnostic. A malformed definition must produce LUA_ERRSYNTAX and a nonempty diagnostic. Clearing those error objects must leave the existing functions usable: a subsequent factorial(6) must return 720. This yields 128 successful integer calls and five real calls, plus two expected error paths. The state is closed after all checks.

The author in-memory example was reviewed for API usage; the script and reference fixtures are independently written. No external scripts are needed. This S driver checks the numeric language boundary and recovery, not all Lua semantics or bindings. Arbitrary modules, userdata, callbacks from Lua to Fortran, concurrent states and a separate Lua 5.3 package are not verified.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### dde-method-steps-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=dde_solver&example=gams-dde-method-steps-reference) / [Driver source](../fpm_catalog/gams-drivers/dde-method-steps-reference.f90) / [Pinned procedure](https://github.com/WarrenWeckesser/dde_solver/blob/90d3389ce5d5733ab2b6e7ed7d2dad273b4d0c6b/dde_solver_m.f90#L376) / [Author example/test](https://github.com/WarrenWeckesser/dde_solver/blob/90d3389ce5d5733ab2b6e7ed7d2dad273b4d0c6b/tests/delay_oscillator/delay_oscillator.f90)

```text
Oscillator=F delay=  0.25000 rate=  0.50 error=  2.8831E-16
Oscillator=F delay=  0.25000 rate=  0.50 error=  2.8831E-16
Oscillator=F delay=  0.25000 rate=  1.00 error=  6.0123E-16
Oscillator=F delay=  0.25000 rate=  1.00 error=  2.1911E-16
Oscillator=F delay=  1.00000 rate=  0.50 error=  8.2731E-16
Oscillator=F delay=  1.00000 rate=  0.50 error=  4.4186E-16
Oscillator=F delay=  1.00000 rate=  1.00 error=  6.9849E-16
Oscillator=F delay=  1.00000 rate=  1.00 error=  4.9003E-16
Oscillator=F delay=  2.00000 rate=  0.50 error=  6.9849E-16
Oscillator=F delay=  2.00000 rate=  0.50 error=  4.9003E-16
Oscillator=F delay=  2.00000 rate=  1.00 error=  1.0487E-15
Oscillator=F delay=  2.00000 rate=  1.00 error=  6.3159E-16
Oscillator=T delay=  3.14159 rate=  0.50 error=  1.8426E-12
Oscillator=T delay=  1.57080 rate=  1.00 error=  1.8426E-12
Oscillator=T delay=  0.78540 rate=  2.00 error=  1.8426E-12
15 delayed solves, 975 dense-output references: method-of-steps polynomials and sinusoidal oscillators.
Maximum error / max(1,abs(reference)):   1.8426E-12
Constant positive delays, signed history scaling, delay knots and interior samples checked.
PASS dde-method-steps-reference
```

### lua-numeric-embedding-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lua54&example=gams-lua-numeric-embedding-reference) / [Driver source](../fpm_catalog/gams-drivers/lua-numeric-embedding-reference.f90) / [Pinned procedure](https://github.com/interkosmos/fortran-lua54/blob/b3582591bc82d003ef3933d0772c131509667f49/src/lua.f90#L1) / [Author example/test](https://github.com/interkosmos/fortran-lua54/blob/b3582591bc82d003ef3933d0772c131509667f49/examples/string.f90)

```text
128 exact integer calls: factorials through 20!, sums of squares, signed polynomials and error recovery.
Five real Pythagorean norm calls, maximum absolute error:   0.0000E+00
Return types, stack balance, expected runtime/syntax diagnostics and subsequent state reuse checked.
PASS lua-numeric-embedding-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers dde-method-steps-reference lua-numeric-embedding-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
