# Returned objective sign after two annealing loops

The [preserved two-loop consumer](two-loops.f90) sets the valid `n_resets=2`
option for simulated-annealing revision
`a2fa094d1ee39525c7e081cfd67866975e9e1dc5`. On the first two-dimensional
amplitude-one Rastrigin fixture, its independently recomputed nonnegative
objective is `1.50725e-12`, but the discrepancy from the returned objective is
`3.01445e-12`. The consumer rejects this using its unchanged `2e-12` normalized
identity tolerance; see the [complete result](two-loops-result.json).

The discrepancy is consistent with an extra sign conversion. Source inspection
shows minimization stores an internally negated objective, while the
[termination branch](https://github.com/jacobwilliams/simulated-annealing/blob/a2fa094d1ee39525c7e081cfd67866975e9e1dc5/src/simulated_annealing.F90#L663)
converts `fopt` back to the external sign within each main-loop run. The next
run retains that converted `fopt`. This explains why the objective can be
converted again when the second run does not replace it. The saved transcript
prints the independent value and discrepancy, not the signed returned value,
so this diagnosis relies on the pinned source as well as the numerical result.

The successful checked driver uses exactly one main-loop run. It still checks
returned objective agreement using the original tolerance and does not claim
multi-loop correctness. No library patch or upstream-confirmed fix is claimed.

The independent consumer uses the
[playground MIT notice](../../../fpm_catalog/gams-drivers/licenses/directions-fitting-drivers-MIT.txt);
its source header retains the relative reference from its original location.
