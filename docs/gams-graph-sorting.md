# Checked dependency ordering and numeric sorting

These P and N6 drivers passed the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0. Existing package libraries were reused; only mains and executables were compiled. The [verification report](gams-graph-sorting-validation.json) retains pins, source hashes and actual output. GAMS categories are not exhausted.

## DAGLIB topological ordering (P)

Five vertices have ten possible dependency edges under a fixed topological order. All 1,024 edge subsets are tested under labels [1,2,3,4,5] and [5,4,3,2,1], giving 2,048 acyclic graph fixtures. This is exhaustive for these two fixed orders, not every labeled five-vertex DAG. Some fixtures coincide. Edgeless graphs, disconnected components and isolated vertices are included. Each graph is sorted twice without rebuilding between sorts.

Every successful sort must return status zero and an allocated permutation of the complete vertex set. A separately built dependency matrix supplies the reference: every prerequisite must precede its dependent vertex. No particular order of unrelated vertices is required. Graph destruction must reset its reported vertex count.

Self-loops, two-vertex cycles and three-vertex cycles are each sorted twice. All six calls must return status -1 and leave the output unallocated. After each cyclic graph, the same object is explicitly rebuilt as the chain 1 -> 2 -> 3 and sorted twice. Totals are 2,051 acyclic fixtures, 4,102 successful sorts, 20,492 independent dependency-precedence checks and six expected cyclic rejections. Recovery uses explicit set_vertices rebuilding; arbitrary edge mutation is not verified.

Zero-vertex graphs, invalid vertex indices, every labeled DAG, large recursion depths, metadata/Graphviz export, other traversal methods and performance remain unverified. The existing broad P graph-algorithm assignment is retained.

## coretran in-place numeric sorting (N6)

The public driver explicitly requests stable=.true. for every sort. All permutations through length seven give 5,913 fixtures. Another 84 use six patterns at lengths [0,1,2,3,4,7,8,15,16,31,32,63,64,127]: ascending, descending, constant, three repeated keys, alternating signed magnitudes and a repeated modular pattern. Total: 5,997 fixtures and 23,988 typed calls.

Each fixture is independently insertion-sorted before invoking the library. Integer32 values are used directly; integer64 keys are integer_value*10**10+3 to include magnitudes beyond integer32. Real32/real64 keys divide the integer values by eight, giving exactly representable inputs. All four returned arrays must exactly equal the corresponding independently sorted values. The fixtures match the [ORDERPACK ranking reference](gams-ranking-magic.md), but this driver exercises in-place sorting rather than sorting indices.

Equal numeric keys carry no auxiliary record labels, so the checks do not establish stability of equal-key records despite the requested stable mode. Default/unstable sorting, NaNs, indirect sorting, every coretran utility and performance remain unverified. The existing OpenMP build is reused unchanged; the execution sandbox uses one thread.

## Failed coretran probes

Both failures built successfully and retain their exact sources, normalized hashes, pinned revision and full results:

- [Nearest-neighbor probe](gams-candidates/coretran-nearest/README.md): a valid two-dimensional 31-point query returned squared distance 0.07390715705352345 instead of the direct minimum 0.048195228517966246. No nearest-neighbor GAMS driver is published.
- [Mixed sorting settings](gams-candidates/coretran-sort/README.md): explicit stable=.false. on 16 equal integer32 values (all 7) accesses element 17 beyond bound 16 in sm_partition.f90. Default and stable=true settings had reached this fixture successfully before the unstable call failed. The full mixed-mode suite did not complete; this does not establish a default-mode failure.

The checked sorting driver narrows the algorithm setting, keeping the full input suite and exact value checks. No source patch, relaxed comparison or disabled bounds checking is used. The sorting proof does not verify the separately mapped nearest-neighbor capability.

## Checked links and actual output

Independent API consumers have their own MIT notice; upstream terms remain separate. Pinned sources and author tests were reviewed without copying upstream code. Loading a link does not submit a job.

### daglib-order-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=daglib&example=gams-daglib-order-reference) / [Driver source](../fpm_catalog/gams-drivers/daglib-order-reference.f90) / [Pinned procedure](https://github.com/jacobwilliams/daglib/blob/68fa83ebfd33fd6521327918b1d8e5084250a8ff/src/dag_module.F90#L85) / [Author test](https://github.com/jacobwilliams/daglib/blob/68fa83ebfd33fd6521327918b1d8e5084250a8ff/test/dag_example.f90)

```text
Acyclic graph fixtures: 2051; valid topological sorts: 4102
Independent dependency precedence checks: 20492
Expected cyclic rejections: 6
Permutation integrity, repeated sorting, explicit cycle status and object recovery.
PASS daglib-order-reference
```

### coretran-sort-reference

[Load driver](https://beliavsky.github.io/fortran-playground/fpm/?package=coretran&example=gams-coretran-sort-reference) / [Driver source](../fpm_catalog/gams-drivers/coretran-sort-reference.f90) / [Pinned procedure](https://github.com/leonfoks/coretran/blob/204c4707f6680b6d7d1e4da39077d0fd3acfe37e/src/sorting/m_sort.f90#L1) / [Author test](https://github.com/leonfoks/coretran/blob/204c4707f6680b6d7d1e4da39077d0fd3acfe37e/test/m_tests.f90)

```text
Exhaustive permutations through length seven: 5913
Total sorting fixtures: 5997; typed sorting calls: 23988
Integer32/64 and real32/64; explicit stable=true only.
Independent insertion-sort values; empty input, repeated keys and boundary sizes.
PASS coretran-sort-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers daglib-order-reference coretran-sort-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Verification requires Modal authentication and `.fpm-audit-cache/precompiled.json`. No backend redeployment or package library rebuild is required. The [coverage report](gams-coverage.md) lists remaining work.
