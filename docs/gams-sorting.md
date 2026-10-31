# Class-specific playground links and checked stdlib sorting

On a GAMS class page, **Try in playground** opens a checked driver matching that class when one is available. An exact-class driver is preferred; a driver in a descendant class is used otherwise. Class membership follows the explicit GAMS hierarchy. Package/owner pages retain their general package links. If no matching driver exists, a class card labels the fallback **Open default example**, rather than implying that the default program demonstrates the current class.

The stdlib link on [N6: Sorting](https://beliavsky.github.io/fortran-playground/gams/N6/) now opens the [checked sorting example](https://beliavsky.github.io/fortran-playground/fpm/?package=stdlib&example=gams-stdlib-sorting-reference). Loading the link selects code without submitting a job.

## Checked sorting operations

The driver uses `stdlib_sorting:sort` on int32 and real64 arrays. It checks exact ascending and descending answers for small arrays with negative and repeated values, integer-sort idempotence, and empty/singleton arrays. A separate 64-element integer case uses values `modulo(37*i,17)-8`; its sorted reference is constructed from counts in the known range -8 through 8, independently of another sorting routine.

The real values are finite, exactly representable binary fractions. NaN ordering, signed-zero distinctions, stability and all other sorting interfaces are outside this driver. Author API patterns are adapted with the stdlib MIT notice retained.

[Driver source](../fpm_catalog/gams-drivers/stdlib-sorting-reference.f90) / [Pinned author test](https://github.com/fortran-lang/stdlib/blob/58eb9133966c2797e0593281169ef57c43eccc1d/test/test_sorting.F90) / [Verification report](gams-sorting-validation.json)

The driver passed in the restricted GNU Fortran 16.2.0 sandbox with FPM 0.12.0, reusing the existing stdlib library. Only the main and executable were compiled. The example appears in both hosted and main local FPM menus.

```text
Ascending integers:   -3   -3   -1    0    1    2    5    5
Descending integers:    5    5    2    1    0   -1   -3   -3
Ascending real values:   -3.000   -1.250   -1.250    0.000    0.500    2.000    2.500
Sorted 64 repeated integers against a histogram reference.
Empty and singleton arrays checked.
PASS stdlib-sorting-reference
```

## Maintenance

```text
python xverify_gams_drivers.py --drivers stdlib-sorting-reference
python xpackage_gams.py
python xfpm_examples.py
python xsite.py
```

Publishing the updated Pages build is sufficient; no backend redeployment or package library rebuild is required.
