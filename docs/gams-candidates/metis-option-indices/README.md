# METIS Fortran/C option-index mismatch

At metis-fpm pin `5db1dc1e46fd819a53a86fe2170eaf5464bf17c7`, the Fortran wrapper and its bundled C header disagree about some indices into the options array:

| Option | Fortran index | Bundled C index |
| --- | ---: | ---: |
| UFACTOR | 18 | 17 |
| NUMBERING | 19 | 18 |

The [Fortran declarations](https://github.com/gnikit/metis-fpm/blob/5db1dc1e46fd819a53a86fe2170eaf5464bf17c7/src/metis_c_interface.F90#L42) place NO2HOP at index 10, while the [bundled C enum](https://github.com/gnikit/metis-fpm/blob/5db1dc1e46fd819a53a86fe2170eaf5464bf17c7/src/metis/include/metis.h#L264) places it later. SEED is index 9 in both and is not affected.

The retained GNU Fortran 16.2.0 probe sets the named Fortran NUMBERING option to zero and UFACTOR to 100. The C implementation reads the latter value as NUMBERING=100, prints `Input Error: Incorrect numflag.`, and returns an input-error status. The first graph is a valid 12-vertex undirected cycle with unit weights, requesting two parts.

- [Exact probe source](option-indices.f90)
- [Pin and normalized source hash](option-indices.json)
- [Complete build/run result](option-indices-result.json)
- [Successful checked-driver review](../../gams-products-partitions.md)

The successful driver keeps default zero-based numbering, uses the typed `ubvec=[1.1_real_t]` argument for imbalance, and sets only the matching SEED option. It retains the same graph/objective checks and does not patch the library, substitute hard-coded option indices or relax comparisons. Other option constants are not thereby verified. The failed probe is not registered as a checked driver.

This independent probe is a preserved variant covered by the [driver MIT notice](../../../fpm_catalog/gams-drivers/licenses/products-partitions-drivers-MIT.txt); upstream wrapper/METIS/GKlib terms remain separate.
