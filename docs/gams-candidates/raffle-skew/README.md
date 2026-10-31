# RAFFLE v1.0.0 skew-cell periodic-distance failure

The pinned GNU Fortran 16.2.0 cached-library probe built successfully but failed its independent periodic-image minimum check. The library is RAFFLE commit `c152a30a1eaf94965c047bcd1a7edca07873b56f` (the catalog's v1.0.0 snapshot).

A single atom is at fractional origin. The lattice rows are `[1,0,0]`, `[0.8,0.6,0]`, `[0,0,1]`, and the query is `[0.49,0.49,0]` in fractional coordinates. The library returns **0.92970967292785645**. Independent real64 enumeration of translations from -2 through 2 in all three axes, using the actual rounded real32 inputs, gives **0.31679647220910667**. Translation `[-1,0,0]` realizes that smaller distance.

The finite image search suffices here: the lattice's smallest singular value is about sqrt(0.2), so an image outside the searched box has distance greater than 1, already larger than the exhibited 0.317 candidate. Componentwise fractional wrapping does not generally minimize Cartesian length in a skew lattice. This probe tests `get_min_dist_between_point_and_atom`; it does not separately execute every other skew-cell distance API.

- [Exact probe source](skew-image-reference.f90)
- [Pin and normalized source hash](skew-image-reference.json)
- [Complete failed build/run result](skew-image-reference-result.json)
- [Successful orthogonal-cell driver review](../../gams-periodic-calculus.md)

The published driver keeps orthogonal and rigidly rotated orthogonal cells, including the complete image-enumeration oracle. It does not claim general skew-cell correctness. No upstream source patch, relaxed comparison or disabled bounds checking was used. The failed probe is not registered as a checked driver. Independent probe code has its own [MIT notice](../../../fpm_catalog/gams-drivers/licenses/periodic-calculus-drivers-MIT.txt); upstream GPL terms remain separate.
