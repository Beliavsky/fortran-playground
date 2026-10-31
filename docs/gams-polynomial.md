# Checked GAMS polynomial-root drivers

These three examples demonstrate [F1a: Polynomial equations](https://gams.nist.gov/cgi-bin/serve.cgi/Class/F1a) using polyroots-fortran. Two newly reviewed procedures, `rpoly` and `cpolyroots`, have their own pinned evidence and entries in the numerical-review ledger. The three APIs are demonstrated separately. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Algorithms and input conventions

| Procedure | Coefficients | Method | Required status |
| --- | --- | --- | --- |
| `polyroots` | Real | Real companion-matrix eigenvalues through LAPACK | `info=0` |
| `rpoly` | Real | Jenkins-Traub all-roots solver | `istat=0`; partial results are not accepted |
| `cpolyroots` | Complex | Complex companion-matrix eigenvalues through LAPACK | `info=0` |

All three take coefficients in decreasing powers and run with real64 arithmetic. The real APIs return separate real/imaginary arrays; the driver combines them only after checking successful status. The complex API returns complex roots.

## Known distinct roots

| Case | Polynomial | Expected roots | APIs checked |
| --- | --- | --- | --- |
| 1 | `x**3-6*x**2+11*x-6` | `1,2,3` | All three |
| 2 | `x*(x+2)*((x-1)**2+4) = x**4+x**2+10*x` | `-2,0,1+2i,1-2i` | All three |
| 3 | Product of the three complex factors `(x-r)` listed here | `1+i,-2+0.5i,0.25-i` | `cpolyroots` |

The last case has coefficients `[1, 0.75-0.5i, -1.25-0.125i, 2.125-2.125i]`. The driver constructs them by multiplying the known factors. All components are simple binary fractions; the reference roots are specified independently of the solver.

Each case is repeated after multiplying every coefficient by `1`, `1e80` and `1e-80`. This leaves the mathematical roots unchanged. The two real drivers each perform six solver calls, and the complex driver performs nine. These scales test selected coefficient-scaling behavior without approaching the representable extremes of real64.

## Order-independent matching and residual checks

Every returned root must have finite real and imaginary parts. For each distinct expected root, the driver chooses the nearest unused computed root and marks it used. Its scaled distance `abs(computed-expected)/max(1,abs(expected))` must be at most `1e-9`. This checks one-to-one coverage without assuming returned order. The simple matching is appropriate for these well-separated roots; it is not a general clustered-root assignment algorithm.

Each computed root is also substituted into the original scaled coefficient array using complex Horner evaluation. The normalized residual is:

```text
eta(z) = abs(p(z)) / sum_k(abs(a_k)*abs(z)**(n-k))
```

Here `a_0,...,a_n` are the coefficients in decreasing powers. The denominator is accumulated with a separate real Horner recurrence. Every normalized residual must be finite and at most `2e-12`. For the exact zero root with zero constant coefficient, both numerator and denominator are zero; that specific case is recorded as zero residual. A zero denominator with a nonzero numerator is rejected.

A small polynomial residual alone does not establish accurate individual roots of an ill-conditioned polynomial, which is why the known-root check is separate. Repeated roots, tightly clustered roots, high degrees, every overload, root polishing and invalid inputs are outside this validation. These examples do not rank the methods by general accuracy or speed.

## Sources and playground links

| Driver | Pinned procedure and author test |
| --- | --- |
| [Load polyroots-real-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=polyroots-fortran&example=gams-polyroots-real-reference) / [Source](../fpm_catalog/gams-drivers/polyroots-real-reference.f90) | [Procedure](https://github.com/jacobwilliams/polyroots-fortran/blob/165ed6fbec98cc23d9ed4784fbc4708adb5e0bcf/src/polyroots_module.F90#L2676) / [Author test](https://github.com/jacobwilliams/polyroots-fortran/blob/165ed6fbec98cc23d9ed4784fbc4708adb5e0bcf/test/polyroots_test.f90) |
| [Load rpoly-real-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=polyroots-fortran&example=gams-rpoly-real-reference) / [Source](../fpm_catalog/gams-drivers/rpoly-real-reference.f90) | [Procedure](https://github.com/jacobwilliams/polyroots-fortran/blob/165ed6fbec98cc23d9ed4784fbc4708adb5e0bcf/src/polyroots_module.F90#L93) / [Author test](https://github.com/jacobwilliams/polyroots-fortran/blob/165ed6fbec98cc23d9ed4784fbc4708adb5e0bcf/test/polyroots_test.f90) |
| [Load cpolyroots-complex-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=polyroots-fortran&example=gams-cpolyroots-complex-reference) / [Source](../fpm_catalog/gams-drivers/cpolyroots-complex-reference.f90) | [Procedure](https://github.com/jacobwilliams/polyroots-fortran/blob/165ed6fbec98cc23d9ed4784fbc4708adb5e0bcf/src/polyroots_module.F90#L2764) / [Author test](https://github.com/jacobwilliams/polyroots-fortran/blob/165ed6fbec98cc23d9ed4784fbc4708adb5e0bcf/test/polyroots_test.f90) |

The programs adapt author API patterns and retain the full upstream license notices. They appear as separate examples in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing polyroots-fortran library. Only the mains and executables were rebuilt. The [verification report](gams-polynomial-validation.json) records hashes, pins and full output, including each computed root. The summaries below retain the case, scale and maximum errors.

### polyroots-real-reference

```text
Polynomial case 1 coefficient scale=  1.00E+00
Max scaled root error / normalized residual:   1.9984E-15   1.4803E-16
Polynomial case 1 coefficient scale=  1.00E+80
Max scaled root error / normalized residual:   1.9984E-15   1.7552E-16
Polynomial case 1 coefficient scale=  1.00E-80
Max scaled root error / normalized residual:   1.9984E-15   2.1848E-16
Polynomial case 2 coefficient scale=  1.00E+00
Max scaled root error / normalized residual:   2.2204E-16   2.7352E-16
Polynomial case 2 coefficient scale=  1.00E+80
Max scaled root error / normalized residual:   2.2204E-16   3.1594E-16
Polynomial case 2 coefficient scale=  1.00E-80
Max scaled root error / normalized residual:   2.2204E-16   2.2472E-16
PASS polyroots-real-reference
```

### rpoly-real-reference

```text
Polynomial case 1 coefficient scale=  1.00E+00
Max scaled root error / normalized residual:   1.4803E-16   1.4803E-17
Polynomial case 1 coefficient scale=  1.00E+80
Max scaled root error / normalized residual:   3.3307E-16   4.3880E-17
Polynomial case 1 coefficient scale=  1.00E-80
Max scaled root error / normalized residual:   3.3307E-16   5.6180E-17
Polynomial case 2 coefficient scale=  1.00E+00
Max scaled root error / normalized residual:   0.0000E+00   0.0000E+00
Polynomial case 2 coefficient scale=  1.00E+80
Max scaled root error / normalized residual:   1.9860E-16   3.3730E-16
Polynomial case 2 coefficient scale=  1.00E-80
Max scaled root error / normalized residual:   0.0000E+00   3.1989E-17
PASS rpoly-real-reference
```

### cpolyroots-complex-reference

```text
Polynomial case 1 coefficient scale=  1.00E+00
Max scaled root error / normalized residual:   2.9336E-15   2.2613E-16
Polynomial case 1 coefficient scale=  1.00E+80
Max scaled root error / normalized residual:   2.9336E-15   2.2353E-16
Polynomial case 1 coefficient scale=  1.00E-80
Max scaled root error / normalized residual:   2.9336E-15   1.9209E-16
Polynomial case 2 coefficient scale=  1.00E+00
Max scaled root error / normalized residual:   3.1402E-16   4.6917E-16
Polynomial case 2 coefficient scale=  1.00E+80
Max scaled root error / normalized residual:   3.1402E-16   4.7649E-16
Polynomial case 2 coefficient scale=  1.00E-80
Max scaled root error / normalized residual:   3.1402E-16   4.7555E-16
Polynomial case 3 coefficient scale=  1.00E+00
Max scaled root error / normalized residual:   1.5165E-15   1.5009E-15
Polynomial case 3 coefficient scale=  1.00E+80
Max scaled root error / normalized residual:   1.5165E-15   1.3931E-15
Polynomial case 3 coefficient scale=  1.00E-80
Max scaled root error / normalized residual:   1.5165E-15   1.3456E-15
PASS cpolyroots-complex-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers polyroots-real-reference rpoly-real-reference cpolyroots-complex-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
