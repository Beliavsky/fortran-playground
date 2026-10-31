# Checked complex circuits, elementary functions and beta identities

These A4, C4 and C7 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only their mains and executables were compiled. The [verification report](gams-circuits-beta-validation.json) records pins, source hashes and actual output. GAMS categories are not exhausted.

## Complex RLC impedance: ECX (A4)

The public z API computes resistor, capacitor and inductor impedances for 12 parameter sets: R in [1,10,100] ohms, C in [0.001,0.01] farads and L in [0.01,0.1] henries. Each set uses 17 angular frequencies 2**k, k=-8..8, plus its resonance frequency 1/sqrt(L*C). All 36 array calls must return status zero and the success message. The API requires three parameter entries even for these one-parameter elements; unused entries are zero.

All 648 element impedances must be finite and agree with independent real/imaginary formulas: R, -i/(omega*C) and i*omega*L. At each of the 216 frequency cases the driver also constructs series RLC and parallel RC combinations. Series impedance is checked against `R+i*(omega*L-1/(omega*C))`. Parallel RC is checked against `R/(1+t*t)-i*R*t/(1+t*t)`, t=omega*R*C. Complex error divided by max(1,abs(reference)) must be at most 2e-13.

At resonance, the series imaginary part must vanish and magnitude equal R within 1e-12*max(1,R). Circuit composition is supplied by the driver; these checks do not establish a general package circuit solver. A4 describes the complex arithmetic interface, not an electrochemistry-specific taxonomy class. Nonideal elements, nonlinear kinetics, parameter estimation and exceptional inputs are outside this example.

## Real sinc and sech: RPN calculator library (C4)

There are 129 equally spaced arguments -8..8 in steps of 0.125, plus +/-1e-10 and +/-1e-6: 133 real arguments. The sinc reference is the independently accumulated 64-term series `sum((-x*x)**k/(2*k+1)!,k=0..63)`, evaluated by term recurrence without calling sin. Absolute error must stay within 5e-13. For sech, the reference is `2*a/(1+a*a)`, a=exp(-abs(x)), avoiding the package cosh implementation; absolute error must stay within 5e-14.

Finite outputs, exact unit values at zero, even symmetry, the sech range (0,1] and scalar/array consistency are required. Available author tests were reviewed for public-module usage; they are not matching sinc/sech drivers. This real C4 driver does not verify the separate C2 cube-root mapping, complex overloads, extreme inputs or the interactive calculator.

## Real beta: RPN calculator library (C7)

The 128 positive argument pairs comprise all integers x,y=1..8 and all half-integers x,y=0.5..7.5. Integer references are `B(i,j)=(i-1)!*(j-1)!/(i+j-1)!`. Half-integer references use `B(n+1/2,m+1/2)=pi*(2*n)!*(2*m)!/(4**(n+m)*n!*m!*(n+m)!)` for n,m=0..7. Factorials through 15! are formed exactly in int64 and converted before products; the references do not call gamma or beta.

For each pair, B(x,y), B(y,x), B(x+1,y) and B(x,y+1) are checked against the closed form and the two identities `B(x+1,y)=x/(x+y)*B(x,y)` and `B(x,y+1)=y/(x+y)*B(x,y)`, using the independent reference on the right. All 512 evaluations must be finite, positive and within relative error 2e-13. No matching author beta driver is recorded. The separate C10 Bessel mapping, complex beta, poles, large arguments and gamma-product overflow are not verified.

## Checked links and actual output

These independent API consumers have their own MIT notice; upstream package licenses remain separate. Loading a link does not submit a job.

### ecx-rlc-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=ecx&example=gams-ecx-rlc-reference) / [Driver source](../fpm_catalog/gams-drivers/ecx-rlc-reference.f90) / [Pinned procedure](https://github.com/MilanSkocic/ecx/blob/d30725e3cb9186bc79f81481f3d6fae8d177a7b7/src/ecx_api.f90#L1) / [Author example/test](https://github.com/MilanSkocic/ecx/blob/d30725e3cb9186bc79f81481f3d6fae8d177a7b7/example/example.f90)

```text
12 RLC parameter sets, 216 frequency cases, 648 element impedances checked.
Series RLC resonance and parallel RC real/imaginary formulas checked.
Maximum complex error / max(1,abs(reference)):   4.2172E-16
PASS ecx-rlc-reference
```

### rpn-sinc-sech-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran&example=gams-rpn-sinc-sech-reference) / [Driver source](../fpm_catalog/gams-drivers/rpn-sinc-sech-reference.f90) / [Pinned procedure](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/src/funcs.f90#L1) / [Author example/test](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/test/test.f90)

```text
133 real arguments: -8..8 step 0.125, plus signed near-zero values.
Maximum sinc absolute error versus 64-term power series:   8.2434E-15
Maximum sech absolute error versus exponential formula:   1.1102E-16
Zero values, even symmetry, sech range and scalar/array consistency checked.
PASS rpn-sinc-sech-reference
```

### rpn-beta-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=rpn-calculator-fortran&example=gams-rpn-beta-reference) / [Driver source](../fpm_catalog/gams-drivers/rpn-beta-reference.f90) / [Pinned procedure](https://github.com/scivision/rpn-calculator-fortran/blob/7708e4949f17511d81f4e7dd0271a500f0bc3631/src/specfun/gamma.f90#L1)

```text
128 positive integer/half-integer pairs; 512 beta evaluations checked.
Independent factorial identities, symmetry and both one-step recurrences checked.
Maximum relative error against closed-form references:   4.4409E-16
PASS rpn-beta-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers ecx-rlc-reference rpn-sinc-sech-reference rpn-beta-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
