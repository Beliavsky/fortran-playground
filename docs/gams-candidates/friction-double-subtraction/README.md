# Coulomb parameter fit returns twice the known coefficient

At friction revision `8e75dcac26f47417a439adfcbaa24834105d89fe`, the independent
[reproducer](fit-reference.f90) generates 12 exact Coulomb observations with
coefficient 0.375, alternating signed velocities and positive varying normal
loads. Its coefficient is identifiable: with `a_i=sign(v_i)*N_i`, the unique
least-squares estimate is `sum(a_i*F_i)/sum(a_i**2)=0.375`.

The cached GNU Fortran 16.2.0 / FPM 0.12.0 build compiled the consumer and reused
the existing library. `model%fit` returned `0.7499999991182843`, reported residual
convergence, and produced a maximum independently recomputed force error of
`1.499999996473137`. The driver failed its unchanged coefficient tolerance of
`1e-7`. The complete [result](fit-result.json) retains the package/dependency
pins, normalized source hash, compilation and execution output.

The pinned [fit callback](https://github.com/jchristopherson/friction/blob/8e75dcac26f47417a439adfcbaa24834105d89fe/src/friction_core.f90#L205)
returns `model_force - observed_force`, while
[fmdl_fit](https://github.com/jchristopherson/friction/blob/8e75dcac26f47417a439adfcbaa24834105d89fe/src/friction_core.f90#L513)
passes the observed force again as the dependent-data target to
`nonlinear_least_squares`. The pinned fstats dependency uses model predictions
as callback output and computes data-minus-model residuals. Source inspection
therefore explains the observed factor of two: the effective residual is
`2*observed_force - model_force`. This is a source-based diagnosis of this
fixture; no upstream fix or general statement about every friction model is
claimed.

The L8 fitting record remains source-supported, with **no checked driver**.
Algebraic Coulomb/Stribeck evaluations remain separately demonstrated. No
library patch, backend deployment or cached build change was made.

The independent probe has the playground contributors'
[MIT notice](../../../fpm_catalog/gams-drivers/licenses/directions-fitting-drivers-MIT.txt).
Its source header retains the license reference from its original submitted
location; use the link here after downloading this preserved copy. Upstream
package licenses remain separate.
