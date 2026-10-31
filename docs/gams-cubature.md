# Checked GAMS cubature and quadrature-rule drivers

| Class | Configuration | Procedures |
| --- | --- | --- |
| [H2b1a1](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2b1a1) | Automatic multidimensional integration over hyperrectangles | DCUHRE |
| [H2c](https://gams.nist.gov/cgi-bin/serve.cgi/Class/H2c) | Integration service routines: nodes and weights | `gauss_jacobi`; `cubature` |

A rule generator returns nodes and weights; the driver forms its own weighted sums. An adaptive integrator selects subdivisions and evaluates callbacks to meet a requested tolerance. The classifications preserve this distinction. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Adaptive box integrals

DCUHRE integrates two components together: `sum(x**2)` and `exp(sum(x))`. The boxes are `[0,1]^2` and `[-1,0] x [0,2] x [1,2]`. Their references follow from separation into one-dimensional antiderivatives:

```text
Integral sum(x**2) = sum_j ((b_j**3-a_j**3)/3 * product_{i!=j}(b_i-a_i))
Integral exp(sum(x)) = product_j (exp(b_j)-exp(a_j))
```

| Box | Quadratic reference | Exponential reference |
| --- | --- | --- |
| Unit square | `2/3` | `(e-1)**2` |
| Shifted 3D box | `8` | `(1-exp(-1))*(exp(2)-1)*(exp(2)-exp(1))` |

The driver uses real64, default local rule (`key=0`), no restart, absolute tolerance `1e-10`, relative tolerance `1e-9`, a maximum of 20000 evaluations and workspace length 10000. A module callback supplies both components. It requires `ifail=0`, a positive evaluation count within budget, finite results and finite nonnegative error estimates within the requested criterion. Independently computed scaled analytic errors must be at most `1e-8`.

These are smooth finite-domain examples. Error estimates are inspected, but are not proved to bound true errors for arbitrary integrands. Singularities, oscillatory integrands, restarts and all local-rule choices are not validated.

## Gauss-Jacobi moments and weight convention

The GaussJacobiQuad driver generates four-point rules with both `recurrence` and `gw` methods for `(alpha,beta)=(0,0)` and `(1,0)`. The convention is `weight(x)=(1-x)**alpha*(1+x)**beta` on `[-1,1]`. Thus the cases use weight `1` and `1-x`; the asymmetric second case also checks the sign convention.

For each of the four rules, the driver checks all monomials `x**k`, `k=0,...,7`, for 32 moment checks. Let `m(k)=2/(k+1)` for even `k`, and `m(k)=0` for odd `k`. Exact references are `m(k)` for weight 1 and `m(k)-m(k+1)` for weight `1-x`. Every node must be finite and strictly inside `(-1,1)`; weights must be finite and positive. Maximum scaled moment error is `1e-11`. The driver prints the nodes and weights.

This checks selected orders and moderate parameters; it does not establish accuracy for high-order rules, parameters near -1, or large alpha/beta.

## Reference-element cubature moments

The fortran_cubatures driver adapts the author monomial-test pattern. It checks positive finite weights, finite nodes inside the reference element, and the following polynomial spaces:

| Element | Domain | Requested degree | Moments checked |
| --- | --- | --- | ---: |
| Triangle | `x,y>=0`, `x+y<=1` | Total degree 5 | 21 |
| Tetrahedron | `x,y,z>=0`, `x+y+z<=1` | Total degree 4 | 35 |
| Quadrilateral | `[-1,1]^2` | Degree 5 in each coordinate | 36 |

For a unit d-simplex, the exact monomial integral is `product(e_i!)/(d+sum(e_i))!`. The driver evaluates these small factorials directly. Square references are products of the one-dimensional moments `m(k)` above. Constant moments also check the measures `1/2`, `1/6` and `4`. All 92 scaled moment errors must be at most `1e-12`. Other elements, degrees, physical-element coordinate mappings and finite-element assembly are outside this example.

All three use scaled error `abs(computed-reference)/max(1,abs(reference))`. The small deterministic problems do not constitute a general accuracy or performance comparison.

## Sources and playground links

| Driver | Pinned procedure and author example |
| --- | --- |
| [Load dcuhre-box-integrals](https://beliavsky.github.io/fortran-playground/fpm/?package=dcuhre&example=gams-dcuhre-box-integrals) / [Source](../fpm_catalog/gams-drivers/dcuhre-box-integrals.f90) | [Procedure](https://github.com/Zaneham/dcuhre/blob/da8becb7f5313c1d7387066ef2106be9e156e20c/src/dcuhre.f#L1) / [Author example](https://github.com/Zaneham/dcuhre/blob/da8becb7f5313c1d7387066ef2106be9e156e20c/test/dtest1.f) |
| [Load gauss-jacobi-polynomial-moments](https://beliavsky.github.io/fortran-playground/fpm/?package=gaussjacobiquad&example=gams-gauss-jacobi-polynomial-moments) / [Source](../fpm_catalog/gams-drivers/gauss-jacobi-polynomial-moments.f90) | [Procedure](https://github.com/HaoZeke/GaussJacobiQuad/blob/ffb970c68eea0b39b140f80f788c8994547d8bfb/src/GaussJacobiQuad.f90#L45) / [Author example](https://github.com/HaoZeke/GaussJacobiQuad/blob/ffb970c68eea0b39b140f80f788c8994547d8bfb/app/gjp_quad.f90) |
| [Load cubatures-simplex-moments](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran_cubatures&example=gams-cubatures-simplex-moments) / [Source](../fpm_catalog/gams-drivers/cubatures-simplex-moments.f90) | [Procedure](https://github.com/willklausler/fortran_cubatures/blob/aca04975d09aed329fd4210defd7052926dc01c1/src/cubatures.f90#L100) / [Author example](https://github.com/willklausler/fortran_cubatures/blob/aca04975d09aed329fd4210defd7052926dc01c1/test/test_cubatures.f90) |

The programs adapt author API patterns and retain license notices. DCUHRE retains the pinned ACM non-commercial terms; the two rule-generator examples retain their MIT notices. They appear in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

All three passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-cubature-validation.json) records hashes, pins and saved output.

### dcuhre-box-integrals

```text
Dimensions=2 evaluations=195
Integral / analytic value / estimated error / scaled analytic error
   6.6666666667E-01   6.6666666667E-01   5.3808589798E-15   1.1102230246E-16
   2.9524924420E+00   2.9524924420E+00   3.4203775530E-15   3.0082326615E-16
Dimensions=3 evaluations=635
Integral / analytic value / estimated error / scaled analytic error
   8.0000000000E+00   8.0000000000E+00   1.1139457705E-14   0.0000000000E+00
   1.8863639844E+01   1.8863639844E+01   7.5642426791E-09   1.8419318894E-13
PASS dcuhre-box-integrals
```

### gauss-jacobi-polynomial-moments

```text
recurrence alpha= 0.0 maximum scaled moment error=  2.2204E-16
Nodes:    -0.8611363116  -0.3399810436   0.3399810436   0.8611363116
Weights:   0.3478548451   0.6521451549   0.6521451549   0.3478548451
recurrence alpha= 1.0 maximum scaled moment error=  5.5511E-16
Nodes:    -0.8857916078  -0.4463139727   0.1671808647   0.7204802713
Weights:   0.5420276537   0.8138582720   0.5193901904   0.1247238838
gw alpha= 0.0 maximum scaled moment error=  5.5511E-16
Nodes:    -0.8611363116  -0.3399810436   0.3399810436   0.8611363116
Weights:   0.3478548451   0.6521451549   0.6521451549   0.3478548451
gw alpha= 1.0 maximum scaled moment error=  3.8858E-16
Nodes:    -0.8857916078  -0.4463139727   0.1671808647   0.7204802713
Weights:   0.5420276537   0.8138582720   0.5193901904   0.1247238838
PASS gauss-jacobi-polynomial-moments
```

### cubatures-simplex-moments

```text
triangle degree=5 points=7 moments=21
Maximum scaled moment error:  2.7756E-17
tetrahedron degree=4 points=27 moments=35
Maximum scaled moment error:  2.7756E-17
quadrilateral degree=5 points=9 moments=36
Maximum scaled moment error:  6.6613E-16
PASS cubatures-simplex-moments
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers dcuhre-box-integrals gauss-jacobi-polynomial-moments cubatures-simplex-moments
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
