# Checked numeric expression evaluation and recovery

These N3 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-expression-evaluation-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## Common mathematical references

Each engine checks 14 formulas at all 20 pairs from x=[-2,-0.5,0,0.75,2], y=[-1.5,0,0.5,1.25]: 280 ordinary references. The engines use the same expression strings with variables pgx and pgy. Both use double precision in the checked catalog configuration. All results must be finite and satisfy abs(result-reference)/max(1,abs(reference)) <=2e-12. References use Fortran arithmetic and elementary identities, not agreement between the two libraries.

| Expression (x/y denote pgx/pgy) | Independent reference |
| --- | --- |
| x+2*y | x+2*y |
| (x+2)*(y-3) | (x+2)*(y-3) |
| x**2+3*x*y+y**2 | x*x+3*x*y+y*y |
| sin(x)**2+cos(x)**2 | 1 |
| exp(log(x+4)) | x+4 |
| sqrt((x+4)**2) | x+4, positive on this input grid |
| abs(x-y) | absolute difference |
| sin(x+y)-sin(x)*cos(y)-cos(x)*sin(y) | 0 |
| (x-y)/(x+4) | direct quotient, nonzero denominator |
| x**3-3*x**2*y+3*x*y**2-y**3 | (x-y)**3 |
| log(exp(y/4)) | y/4 |
| 2+3*4 | 14 |
| (2+3)*4 | 20 |
| -(x+y) | -x-y |

The fixtures cover precedence, parentheses, unary negation, powers, changing variables, cancellation and common elementary functions. They do not establish correctness for every accepted expression or extreme numerical range.

## Fortran Function Parser

Each ordinary expression is parsed once and evaluated at all input pairs. Parsing and evaluation must report no error, and supplied variable arrays must remain unchanged. The same parser object is reused with explicit error clearing and destruction between expressions.

Three malformed expressions `pgx+`, `(pgx` and `unknown(pgx)` must set a parse error. Three separately parsed expressions, sqrt(pgx), log(pgx), 1/(pgx-pgx), must set an evaluation error when pgx=-1. Outputs from rejected requests are not used as numeric answers. After each of these six errors, clear/destroy, parse pgx+pgy and evaluate [0.25,-0.5] against -0.25. This gives 286 successful value references, six expected rejected requests and six successful recoveries.

## M_calculator dnum0

Every ordinary evaluation first assigns pgx and pgy through decimal strings formatted with 17 fractional digits in scientific notation. All 560 assignments must return status zero, finite values and absolute assignment error <=1e-14. Every expression evaluation must return status zero. Reassignment on each input pair checks that prior variable values are replaced.

Malformed expressions `(1+2`, `1+@` and `1+*2` must return nonzero status. After each error, pgx+pgy must still evaluate successfully to the last assigned sum, 3.25. This checks recovery and retained variable state without assuming a particular diagnostic message. There are 283 successful value references, three expected rejected requests and three recoveries, plus the 560 assignment checks. Domain-error handling in this engine is not verified by these probes.

## Scope

N3 records numeric expression parsing/evaluation, not symbolic algebra or nonlinear solving. Missing-variable conventions, general grammar completeness, case folding, user-defined functions, all domain errors, NaN/infinity behavior, state isolation between clients and performance remain unverified. Recovery calls intentionally follow the documented explicit reset steps for the parser; no cross-engine error-code equivalence is assumed.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and author examples/tests were reviewed without copying upstream code. Loading a link does not submit a job.

### function-parser-identities

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=fortran_function_parser&example=gams-function-parser-identities) / [Driver source](../fpm_catalog/gams-drivers/function-parser-identities.f90) / [Pinned procedure](https://github.com/jacobwilliams/fortran_function_parser/blob/4c977c925506bea3fb1ee44aac08114c5fa68a71/src/function_parser.F90#L240) / [Author test](https://github.com/jacobwilliams/fortran_function_parser/blob/4c977c925506bea3fb1ee44aac08114c5fa68a71/test/tests.f90)

```text
Independent expression value references: 286
Expected rejected requests: 6; successful recoveries: 6
Maximum normalized expression error:   1.1102E-16
PASS function-parser-identities
```

### m-calculator-identities

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=m_calculator&example=gams-m-calculator-identities) / [Driver source](../fpm_catalog/gams-drivers/m-calculator-identities.f90) / [Pinned procedure](https://github.com/urbanjost/M_calculator/blob/b6bbc08f81eb158a6908a42016059815fe72217d/src/M_calculator.f90#L3021) / [Author test](https://github.com/urbanjost/M_calculator/blob/b6bbc08f81eb158a6908a42016059815fe72217d/example/demo_dnum0.f90)

```text
*expression* error===> *parens_* right parenthesis missing
*expression* error===> *a_2_d_* undeclared variable [@ ]
*expression* error===> first factor or quotient for "*" or "/" missing or null
Checked variable assignments: 560
Independent expression value references: 283
Expected rejected requests: 3; successful recoveries: 3
Maximum normalized expression error:   4.4409E-16
PASS m-calculator-identities
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers function-parser-identities m-calculator-identities
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
