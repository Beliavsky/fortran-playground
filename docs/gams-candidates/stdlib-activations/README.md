# Stdlib activation-gradient failures

Both exact submitted consumers use stdlib commit 58eb9133966c2797e0593281169ef57c43eccc1d, GNU Fortran 16.2.0 and FPM 0.12.0 in the restricted hosted sandbox. Existing libraries were reused. Each source compiles and runs but fails its independent derivative assertion. JSON records preserve full stdout/stderr, stages, pin and normalized UTF-8/LF source hash. Reference tables were produced with mpmath 1.3.0 at 80 digits and confirmed at 120 digits.

At x=-6:

| API | Actual derivative | Independent derivative |
| --- | ---: | ---: |
| gelu_grad | -6.3628744084007051e-8 | -3.5468709453902015e-8 |
| silu_grad | -1.2320303571493932e-2 | -1.2326432591525513e-2 |

For GELU=x*Phi(x), differentiation gives Phi(x)+x*phi(x). The pinned implementation in src/stdlib_specialfunctions_activations.f90:152 uses x/sqrt(2), missing 1/sqrt(pi) in the exponential term.

For SiLU=x*sigmoid(x), differentiation gives sigmoid(x)+x*sigmoid(x)*(1-sigmoid(x)). The pinned implementation at line 275 uses exp(x) for the leading term instead of sigmoid(x). As a source-level illustration (not an additional hosted run), at x=0 that expression is 1 whereas the derivative is 0.5.

The published GELU/SiLU drivers verify function values only, using unchanged high-precision references and tolerances. The gradient APIs retain separate source-reviewed records without checked drivers. No stdlib numerical source was patched. Passing function values does not promote these gradients. The upstream author GELU test covers values/approximation; the SiLU gradient test repeats the implementation expression, so it is not an independent oracle for this issue.

The retained probes use the same [MIT driver license](../../../fpm_catalog/gams-drivers/licenses/activations-ten-drivers-MIT.txt); their headers retain the original relative license path from the submitted source location. The [reference table](../../gams-activations-ten-references.json) includes the independent derivative values.
