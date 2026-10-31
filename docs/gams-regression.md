# Checked GAMS regression drivers

Both examples demonstrate [L8: Regression](https://gams.nist.gov/cgi-bin/serve.cgi/Class/L8), with different response and error models. They are not interchangeable ordinary linear least-squares examples. GAMS categories are not exhausted; see the [coverage report](gams-coverage.md).

## Orthogonal line fitting with odrpack95

The model is `y=a+b*x`, with unit error weights in both coordinates. This minimizes squared perpendicular distances, unlike vertical-residual ordinary least squares. The driver supplies analytic model derivatives through the public callback interface (`job=20`) and disables printing inside the solver (`iprint=0`).

| Case | x observations | y observations | Initial coefficients |
| --- | --- | --- | --- |
| 1 | `0,1,2,3,4,5` | `1+2*x+[0.1,-0.1,0.1,-0.1,0.1,-0.1]` | `[0,1]` |
| 2 | `10,11,12,13,14,15` | `-3-1.5*x+[0.2,-0.1,0.1,-0.2,0.05,-0.05]` | `[0,-1]` |

Let `xc=x-mean(x)`, `yc=y-mean(y)`, `Sxx=sum(xc**2)`, `Syy=sum(yc**2)` and `Sxy=sum(xc*yc)`. For these nonvertical lines with nonzero cross-moment, the total least-squares references are:

```text
d = sqrt((Syy-Sxx)**2 + 4*Sxy**2)
b = (Syy-Sxx+d)/(2*Sxy)
a = mean(y)-b*mean(x)
minimum orthogonal SSE = (Sxx+Syy-d)/2
```

These formulas handle both signs of slope used here. The driver requires ODR status 1, 2 or 3, finite coefficients and objective, maximum absolute coefficient error at most `1e-5`, and absolute objective error at most `1e-8`. It independently recomputes the objective from original observations as `sum((y-a-b*x)**2)/(1+b**2)`. Covariance estimates, weighted or nonlinear ODR, vertical lines and every stopping condition are outside this example.

## Grouped-binomial logistic regression with lib_statistics

The model is `log(p/(1-p))=beta0+beta1*x`. Each dataset has six groups, 20 trials per group, and three groups at each of two predictor levels. Because there are two model coefficients and two distinct predictor levels, the maximum-likelihood fit matches the aggregated success fraction at each level exactly.

| Case | Predictor levels | Successes in the six groups | Level probabilities |
| --- | --- | --- | --- |
| 1 | `-1,1` | `[3,5,7,13,15,17]` | `1/4,3/4` |
| 2 | `0,2` | `[3,5,7,13,15,17]` | `1/4,3/4` |
| 3 | `-1,1` | `[2,4,6,10,12,14]` | `1/5,3/5` |

Writing the two logits as `l0,l1` and predictor levels as `x0,x1`, the references are `beta1=(l1-l0)/(x1-x0)` and `beta0=l0-beta1*x0`. Cases 1 and 2 check a predictor translation and its effect on intercept and covariance. Case 3 gives a different, asymmetric pair of probabilities. Group proportions vary around their level averages, avoiding a zero residual-variance case.

The driver independently evaluates Pearson chi-square and binomial deviance:

```text
Pearson = sum((s-n*p)**2/(n*p*(1-p)))
Deviance = 2*sum(s*log(s/(n*p)) + (n-s)*log((n-s)/(n*(1-p))))
```

All chosen success counts lie strictly between zero and the number of trials, so the displayed logarithms are well defined. Residual degrees of freedom must be `6-2=4`. The reference Fisher information is `I=sum(n*p*(1-p)*[1,x]^T*[1,x])`, formed from the known probabilities and inverted using the explicit 2-by-2 inverse.

At this pin the API inflates covariance by `max(1,Pearson chi-square/ndf)`, as described in its source header. The driver checks that convention, rather than assuming unscaled binomial covariance. The variance inflation factors are `16/15` for cases 1 and 2 and `25/24` for case 3. Standard-error references are the square roots of the reference covariance diagonal.

Required termination is `ier=0`. Coefficients, probabilities, standard errors, covariance, chi-square and deviance must be finite; fitted probabilities must lie strictly between zero and one and standard errors must be positive. Absolute tolerances are `1e-6` for coefficients, probabilities, chi-square and deviance, and `1e-5` for covariance and standard errors. The covariance tolerance allows the API iterative approximation. Multiple predictors, separation, weighted survey models, zero-trial groups and every error branch are outside this validation.

Both drivers use real64. These are deterministic API and numerical checks, not a comparison of methods for the same statistical model or a speed ranking.

## Sources and playground links

| Driver | Pinned procedure and provenance |
| --- | --- |
| [Load odrpack-line-total-least-squares](https://beliavsky.github.io/fortran-playground/fpm/?package=odrpack95&example=gams-odrpack-line-total-least-squares) / [Source](../fpm_catalog/gams-drivers/odrpack-line-total-least-squares.f90) | [Procedure](https://github.com/HugoMVale/odrpack95/blob/12597b20812a76a4b702f985f6adc82632a18f60/src/odrpack.f90#L15) / [Author example](https://github.com/HugoMVale/odrpack95/blob/12597b20812a76a4b702f985f6adc82632a18f60/example/example1.f90) |
| [Load logistic-grouped-binomial-reference](https://beliavsky.github.io/fortran-playground/fpm/?package=lib_statistics&example=gams-logistic-grouped-binomial-reference) / [Source](../fpm_catalog/gams-drivers/logistic-grouped-binomial-reference.f90) | [Procedure](https://github.com/sebastiandyrda/lib_statistics/blob/056740db259fc3599dca0d8858f04e94845a6769/src/mod_logistic.f90#L36) / Original public-API driver; no upstream test copied |

The odrpack95 driver adapts the author callback pattern and retains its MIT notice. The logistic caller is independently written. Both appear in hosted and main local FPM menus and downloaded projects. Loading a link selects source without submitting a job.

## Recorded results

Both passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing existing package libraries. Only the mains and executables were rebuilt. The [verification report](gams-regression-validation.json) records hashes, pins and saved output.

### odrpack-line-total-least-squares

```text
Line case 1 status=1
Fitted intercept/slope:     1.0397057871     1.9841176852
Exact TLS coefficients:     1.0397058854     1.9841176459
Orthogonal sum of squares / exact:   1.111769E-02   1.111769E-02
Maximum parameter error:  9.8239E-08
Line case 2 status=1
Fitted intercept/slope:    -2.5784469948    -1.5337242404
Exact TLS coefficients:    -2.5784481518    -1.5337241479
Orthogonal sum of squares / exact:   2.619284E-02   2.619284E-02
Maximum parameter error:  1.1570E-06
PASS odrpack-line-total-least-squares
```

### logistic-grouped-binomial-reference

```text
Binomial case 1 residual degrees of freedom=4
Fitted intercept/slope:    0.0000000000    1.0986122887
Exact intercept/slope:     0.0000000000    1.0986122887
Pearson chi-square / deviance:    4.2666666667    4.3611649918
Standard errors:    0.2177322812    0.2177322812
Coefficient / covariance maximum errors:   4.1589E-13   6.1149E-08
Binomial case 2 residual degrees of freedom=4
Fitted intercept/slope:   -1.0986122887    1.0986122887
Exact intercept/slope:    -1.0986122887    1.0986122887
Pearson chi-square / deviance:    4.2666666667    4.3611649918
Standard errors:    0.3079199450    0.2177322812
Coefficient / covariance maximum errors:   4.1611E-13   1.2230E-07
Binomial case 3 residual degrees of freedom=4
Fitted intercept/slope:   -0.4904146264    0.8958797345
Exact intercept/slope:    -0.4904146265    0.8958797346
Pearson chi-square / deviance:    4.1666666664    4.2747769213
Standard errors:    0.2126273155    0.2126273155
Coefficient / covariance maximum errors:   1.0265E-10   8.5153E-07
PASS logistic-grouped-binomial-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers odrpack-line-total-least-squares logistic-grouped-binomial-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required.
