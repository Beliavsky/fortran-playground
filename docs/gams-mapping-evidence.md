# Evidence for GAMS package mappings

This report assesses each package/class pair, including inherited parent classes. A checked package default does not verify every classification.

- **Verified:** a checked driver demonstrates a recorded procedure in this class or a descendant. Only the driver's tested configuration is verified.
- **Source-supported:** a named procedure has pinned source evidence for this class, but no matching checked GAMS driver has been recorded.
- **Uncertain:** the discovery classification has no matching procedure-level evidence in our records. This is a review queue, not a finding that the package lacks the capability.

When a driver cannot be created, inspect the pinned implementation and author examples. Narrow or remove a classification that is unsupported; do not substitute an unrelated default example as evidence. Record missing dependencies, sandbox limits and upstream defects separately in the procedure or package review notes. A sandbox failure alone does not disprove an algorithm.

Counts refer to package/class pairs and include parents: 285 verified, 466 source-supported, 246 uncertain.

## Mappings requiring source review

Inspect these discovery assignments before making a specific algorithm claim. Their existing classifications remain visible, explicitly marked uncertain, until reviewed.

| Package | Class | Description |
| --- | --- | --- |
| [argv-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/argv-fortran/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [argv-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/argv-fortran/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [argv-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/argv-fortran/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [astro-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/astro-fortran/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [befor64](https://beliavsky.github.io/fortran-playground/gams/packages/befor64/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [befor64](https://beliavsky.github.io/fortran-playground/gams/packages/befor64/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [blas-interface](https://beliavsky.github.io/fortran-playground/gams/packages/blas-interface/) | [D2](https://beliavsky.github.io/fortran-playground/gams/D2/) | Solution of systems of linear equations (including inversion, LU and related decompositions) |
| [cairo-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/cairo-fortran/) | [Q](https://beliavsky.github.io/fortran-playground/gams/Q/) | Graphics |
| [ciaaw](https://beliavsky.github.io/fortran-playground/gams/packages/ciaaw/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [codata](https://beliavsky.github.io/fortran-playground/gams/packages/codata/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [collections](https://beliavsky.github.io/fortran-playground/gams/packages/collections/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [collections](https://beliavsky.github.io/fortran-playground/gams/packages/collections/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [conmax](https://beliavsky.github.io/fortran-playground/gams/packages/conmax/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [conmax](https://beliavsky.github.io/fortran-playground/gams/packages/conmax/) | [K2](https://beliavsky.github.io/fortran-playground/gams/K2/) | Minimax (L-infinity) approximation |
| [csv-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/csv-fortran/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [csv-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/csv-fortran/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [daglib](https://beliavsky.github.io/fortran-playground/gams/packages/daglib/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [daglib](https://beliavsky.github.io/fortran-playground/gams/packages/daglib/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [datetime-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/datetime-fortran/) | [R](https://beliavsky.github.io/fortran-playground/gams/R/) | Service routines |
| [ddpcm](https://beliavsky.github.io/fortran-playground/gams/packages/ddpcm/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [ecx](https://beliavsky.github.io/fortran-playground/gams/packages/ecx/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [fastconv](https://beliavsky.github.io/fortran-playground/gams/packages/fastconv/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [fastconv](https://beliavsky.github.io/fortran-playground/gams/packages/fastconv/) | [K5](https://beliavsky.github.io/fortran-playground/gams/K5/) | Smoothing |
| [feq-parse](https://beliavsky.github.io/fortran-playground/gams/packages/feq-parse/) | [C](https://beliavsky.github.io/fortran-playground/gams/C/) | Elementary and special functions |
| [ferror](https://beliavsky.github.io/fortran-playground/gams/packages/ferror/) | [R](https://beliavsky.github.io/fortran-playground/gams/R/) | Service routines |
| [ferror](https://beliavsky.github.io/fortran-playground/gams/packages/ferror/) | [R3](https://beliavsky.github.io/fortran-playground/gams/R3/) | Error handling |
| [ffilesystem](https://beliavsky.github.io/fortran-playground/gams/packages/ffilesystem/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [ffilesystem](https://beliavsky.github.io/fortran-playground/gams/packages/ffilesystem/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [fgsl](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/) | [C](https://beliavsky.github.io/fortran-playground/gams/C/) | Elementary and special functions |
| [fgsl](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/) | [D](https://beliavsky.github.io/fortran-playground/gams/D/) | Linear Algebra |
| [fgsl](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/) | [E](https://beliavsky.github.io/fortran-playground/gams/E/) | Interpolation |
| [fgsl](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/) | [F](https://beliavsky.github.io/fortran-playground/gams/F/) | Solution of nonlinear equations |
| [fgsl](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/) | [G](https://beliavsky.github.io/fortran-playground/gams/G/) | Optimization |
| [fgsl](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/) | [I](https://beliavsky.github.io/fortran-playground/gams/I/) | Differential and integral equations |
| [fgsl](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/) | [J](https://beliavsky.github.io/fortran-playground/gams/J/) | Integral transforms |
| [fgsl](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [fgsl](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/) | [L](https://beliavsky.github.io/fortran-playground/gams/L/) | Statistics, probability |
| [fhash](https://beliavsky.github.io/fortran-playground/gams/packages/fhash/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fhash](https://beliavsky.github.io/fortran-playground/gams/packages/fhash/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [fhash](https://beliavsky.github.io/fortran-playground/gams/packages/fhash/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [fitpack](https://beliavsky.github.io/fortran-playground/gams/packages/fitpack/) | [E2](https://beliavsky.github.io/fortran-playground/gams/E2/) | Multivariate data (surface fitting) |
| [fitpack](https://beliavsky.github.io/fortran-playground/gams/packages/fitpack/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [fitpack](https://beliavsky.github.io/fortran-playground/gams/packages/fitpack/) | [K1](https://beliavsky.github.io/fortran-playground/gams/K1/) | Least squares (L-2) approximation |
| [fitpack](https://beliavsky.github.io/fortran-playground/gams/packages/fitpack/) | [K5](https://beliavsky.github.io/fortran-playground/gams/K5/) | Smoothing |
| [fjsample](https://beliavsky.github.io/fortran-playground/gams/packages/fjsample/) | [L1](https://beliavsky.github.io/fortran-playground/gams/L1/) | Data summarization |
| [fjsample](https://beliavsky.github.io/fortran-playground/gams/packages/fjsample/) | [L2](https://beliavsky.github.io/fortran-playground/gams/L2/) | Data manipulation |
| [flibcpp](https://beliavsky.github.io/fortran-playground/gams/packages/flibcpp/) | [S](https://beliavsky.github.io/fortran-playground/gams/S/) | Software development tools |
| [flist](https://beliavsky.github.io/fortran-playground/gams/packages/flist/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [flist](https://beliavsky.github.io/fortran-playground/gams/packages/flist/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [flist](https://beliavsky.github.io/fortran-playground/gams/packages/flist/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [fmmap](https://beliavsky.github.io/fortran-playground/gams/packages/fmmap/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fmmap](https://beliavsky.github.io/fortran-playground/gams/packages/fmmap/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [fmmap](https://beliavsky.github.io/fortran-playground/gams/packages/fmmap/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [forcolormap](https://beliavsky.github.io/fortran-playground/gams/packages/forcolormap/) | [Q](https://beliavsky.github.io/fortran-playground/gams/Q/) | Graphics |
| [forgex](https://beliavsky.github.io/fortran-playground/gams/packages/forgex/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [forgex](https://beliavsky.github.io/fortran-playground/gams/packages/forgex/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [forgex](https://beliavsky.github.io/fortran-playground/gams/packages/forgex/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [forimage](https://beliavsky.github.io/fortran-playground/gams/packages/forimage/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [forimage](https://beliavsky.github.io/fortran-playground/gams/packages/forimage/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [forimage](https://beliavsky.github.io/fortran-playground/gams/packages/forimage/) | [Q](https://beliavsky.github.io/fortran-playground/gams/Q/) | Graphics |
| [forinv](https://beliavsky.github.io/fortran-playground/gams/packages/forinv/) | [D2](https://beliavsky.github.io/fortran-playground/gams/D2/) | Solution of systems of linear equations (including inversion, LU and related decompositions) |
| [forinv](https://beliavsky.github.io/fortran-playground/gams/packages/forinv/) | [D6](https://beliavsky.github.io/fortran-playground/gams/D6/) | Singular value decomposition |
| [forlab](https://beliavsky.github.io/fortran-playground/gams/packages/forlab/) | [D1](https://beliavsky.github.io/fortran-playground/gams/D1/) | Elementary vector and matrix operations |
| [forlab](https://beliavsky.github.io/fortran-playground/gams/packages/forlab/) | [D2](https://beliavsky.github.io/fortran-playground/gams/D2/) | Solution of systems of linear equations (including inversion, LU and related decompositions) |
| [forlab](https://beliavsky.github.io/fortran-playground/gams/packages/forlab/) | [E](https://beliavsky.github.io/fortran-playground/gams/E/) | Interpolation |
| [forlab](https://beliavsky.github.io/fortran-playground/gams/packages/forlab/) | [E1](https://beliavsky.github.io/fortran-playground/gams/E1/) | Univariate data (curve fitting) |
| [forlab](https://beliavsky.github.io/fortran-playground/gams/packages/forlab/) | [L](https://beliavsky.github.io/fortran-playground/gams/L/) | Statistics, probability |
| [forlab](https://beliavsky.github.io/fortran-playground/gams/packages/forlab/) | [L1](https://beliavsky.github.io/fortran-playground/gams/L1/) | Data summarization |
| [forpca](https://beliavsky.github.io/fortran-playground/gams/packages/forpca/) | [D4](https://beliavsky.github.io/fortran-playground/gams/D4/) | Eigenvalues, eigenvectors |
| [forsolver](https://beliavsky.github.io/fortran-playground/gams/packages/forsolver/) | [D](https://beliavsky.github.io/fortran-playground/gams/D/) | Linear Algebra |
| [forsolver](https://beliavsky.github.io/fortran-playground/gams/packages/forsolver/) | [D2](https://beliavsky.github.io/fortran-playground/gams/D2/) | Solution of systems of linear equations (including inversion, LU and related decompositions) |
| [forsolver](https://beliavsky.github.io/fortran-playground/gams/packages/forsolver/) | [F2](https://beliavsky.github.io/fortran-playground/gams/F2/) | System of equations |
| [forsolver](https://beliavsky.github.io/fortran-playground/gams/packages/forsolver/) | [H](https://beliavsky.github.io/fortran-playground/gams/H/) | Differentiation, integration |
| [forsolver](https://beliavsky.github.io/fortran-playground/gams/packages/forsolver/) | [H1](https://beliavsky.github.io/fortran-playground/gams/H1/) | Numerical differentiation |
| [forsudoku](https://beliavsky.github.io/fortran-playground/gams/packages/forsudoku/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [fortran-astrodynamics-toolkit](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-astrodynamics-toolkit/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [fortran-flann](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-flann/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [fortran-flann](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-flann/) | [P](https://beliavsky.github.io/fortran-playground/gams/P/) | Computational geometry |
| [fortran-messagepack](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-messagepack/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran-messagepack](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-messagepack/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [fortran-pcre2](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-pcre2/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran-pcre2](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-pcre2/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [fortran-pcre2](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-pcre2/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [fortran-regex](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-regex/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran-regex](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-regex/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [fortran-regex](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-regex/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [fortran-search-and-sort](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-search-and-sort/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran-search-and-sort](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-search-and-sort/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [fortran-search-and-sort](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-search-and-sort/) | [N6](https://beliavsky.github.io/fortran-playground/gams/N6/) | Sorting |
| [fortran-shlex](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-shlex/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran-shlex](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-shlex/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [fortran-sqlite3](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-sqlite3/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran-sqlite3](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-sqlite3/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [fortran-sqlite3](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-sqlite3/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [fortran-string-to-real](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-string-to-real/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran-string-to-real](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-string-to-real/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [fortran-zlib](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-zlib/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran-zlib](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-zlib/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [fortran-zstd](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-zstd/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran-zstd](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-zstd/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [fortran_function_parser](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_function_parser/) | [C](https://beliavsky.github.io/fortran-playground/gams/C/) | Elementary and special functions |
| [fortran_huffman](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_huffman/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran_huffman](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_huffman/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [fortran_stb_image](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_stb_image/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortran_stb_image](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_stb_image/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [fortran_stb_image](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_stb_image/) | [Q](https://beliavsky.github.io/fortran-playground/gams/Q/) | Graphics |
| [fortran_test_helper](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_test_helper/) | [S](https://beliavsky.github.io/fortran-playground/gams/S/) | Software development tools |
| [fortran_test_helper](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_test_helper/) | [S3](https://beliavsky.github.io/fortran-playground/gams/S3/) | Dynamic program analysis tools |
| [fortrandf](https://beliavsky.github.io/fortran-playground/gams/packages/fortrandf/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [fortrandf](https://beliavsky.github.io/fortran-playground/gams/packages/fortrandf/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [fortsa](https://beliavsky.github.io/fortran-playground/gams/packages/fortsa/) | [L11](https://beliavsky.github.io/fortran-playground/gams/L11/) | Correlation analysis |
| [fstats](https://beliavsky.github.io/fortran-playground/gams/packages/fstats/) | [L2](https://beliavsky.github.io/fortran-playground/gams/L2/) | Data manipulation |
| [fstats](https://beliavsky.github.io/fortran-playground/gams/packages/fstats/) | [L4](https://beliavsky.github.io/fortran-playground/gams/L4/) | Elementary data analysis |
| [fstats](https://beliavsky.github.io/fortran-playground/gams/packages/fstats/) | [L5](https://beliavsky.github.io/fortran-playground/gams/L5/) | Function evaluation |
| [fstats](https://beliavsky.github.io/fortran-playground/gams/packages/fstats/) | [L6](https://beliavsky.github.io/fortran-playground/gams/L6/) | Random number generation |
| [fstats](https://beliavsky.github.io/fortran-playground/gams/packages/fstats/) | [L8](https://beliavsky.github.io/fortran-playground/gams/L8/) | Regression |
| [fstats](https://beliavsky.github.io/fortran-playground/gams/packages/fstats/) | [M](https://beliavsky.github.io/fortran-playground/gams/M/) | Simulation, stochastic modeling |
| [fstats](https://beliavsky.github.io/fortran-playground/gams/packages/fstats/) | [M1](https://beliavsky.github.io/fortran-playground/gams/M1/) | Simulation |
| [functional-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/functional-fortran/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [functional-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/functional-fortran/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [functional-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/functional-fortran/) | [S](https://beliavsky.github.io/fortran-playground/gams/S/) | Software development tools |
| [graphstruc](https://beliavsky.github.io/fortran-playground/gams/packages/graphstruc/) | [P](https://beliavsky.github.io/fortran-playground/gams/P/) | Computational geometry |
| [h5fortran](https://beliavsky.github.io/fortran-playground/gams/packages/h5fortran/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [h5fortran](https://beliavsky.github.io/fortran-playground/gams/packages/h5fortran/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [iapws](https://beliavsky.github.io/fortran-playground/gams/packages/iapws/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [io-fortran-library](https://beliavsky.github.io/fortran-playground/gams/packages/io-fortran-library/) | [A](https://beliavsky.github.io/fortran-playground/gams/A/) | Arithmetic, error analysis |
| [io-fortran-library](https://beliavsky.github.io/fortran-playground/gams/packages/io-fortran-library/) | [A6](https://beliavsky.github.io/fortran-playground/gams/A6/) | Change of representation |
| [io-fortran-library](https://beliavsky.github.io/fortran-playground/gams/packages/io-fortran-library/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [iso_varying_string](https://beliavsky.github.io/fortran-playground/gams/packages/iso_varying_string/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [iso_varying_string](https://beliavsky.github.io/fortran-playground/gams/packages/iso_varying_string/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [jonquil](https://beliavsky.github.io/fortran-playground/gams/packages/jonquil/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [jonquil](https://beliavsky.github.io/fortran-playground/gams/packages/jonquil/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [jonquil](https://beliavsky.github.io/fortran-playground/gams/packages/jonquil/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [json-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/json-fortran/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [json-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/json-fortran/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [json-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/json-fortran/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [kinds](https://beliavsky.github.io/fortran-playground/gams/packages/kinds/) | [A](https://beliavsky.github.io/fortran-playground/gams/A/) | Arithmetic, error analysis |
| [kinds](https://beliavsky.github.io/fortran-playground/gams/packages/kinds/) | [R](https://beliavsky.github.io/fortran-playground/gams/R/) | Service routines |
| [lib_statistics](https://beliavsky.github.io/fortran-playground/gams/packages/lib_statistics/) | [L9](https://beliavsky.github.io/fortran-playground/gams/L9/) | Categorical data analysis |
| [libdogleg-f](https://beliavsky.github.io/fortran-playground/gams/packages/libdogleg-f/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [libdogleg-f](https://beliavsky.github.io/fortran-playground/gams/packages/libdogleg-f/) | [K1](https://beliavsky.github.io/fortran-playground/gams/K1/) | Least squares (L-2) approximation |
| [libmbd](https://beliavsky.github.io/fortran-playground/gams/packages/libmbd/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [lightkrylov](https://beliavsky.github.io/fortran-playground/gams/packages/lightkrylov/) | [D4](https://beliavsky.github.io/fortran-playground/gams/D4/) | Eigenvalues, eigenvectors |
| [lightkrylov](https://beliavsky.github.io/fortran-playground/gams/packages/lightkrylov/) | [D6](https://beliavsky.github.io/fortran-playground/gams/D6/) | Singular value decomposition |
| [linalg](https://beliavsky.github.io/fortran-playground/gams/packages/linalg/) | [D1](https://beliavsky.github.io/fortran-playground/gams/D1/) | Elementary vector and matrix operations |
| [linalg](https://beliavsky.github.io/fortran-playground/gams/packages/linalg/) | [D3](https://beliavsky.github.io/fortran-playground/gams/D3/) | Determinants |
| [list](https://beliavsky.github.io/fortran-playground/gams/packages/list/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [list](https://beliavsky.github.io/fortran-playground/gams/packages/list/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [list](https://beliavsky.github.io/fortran-playground/gams/packages/list/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [list](https://beliavsky.github.io/fortran-playground/gams/packages/list/) | [N6](https://beliavsky.github.io/fortran-playground/gams/N6/) | Sorting |
| [lsmr](https://beliavsky.github.io/fortran-playground/gams/packages/lsmr/) | [D2](https://beliavsky.github.io/fortran-playground/gams/D2/) | Solution of systems of linear equations (including inversion, LU and related decompositions) |
| [lsmr](https://beliavsky.github.io/fortran-playground/gams/packages/lsmr/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [lsmr](https://beliavsky.github.io/fortran-playground/gams/packages/lsmr/) | [K1](https://beliavsky.github.io/fortran-playground/gams/K1/) | Least squares (L-2) approximation |
| [lsqr](https://beliavsky.github.io/fortran-playground/gams/packages/lsqr/) | [D2](https://beliavsky.github.io/fortran-playground/gams/D2/) | Solution of systems of linear equations (including inversion, LU and related decompositions) |
| [lsqr](https://beliavsky.github.io/fortran-playground/gams/packages/lsqr/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [lsqr](https://beliavsky.github.io/fortran-playground/gams/packages/lsqr/) | [K1](https://beliavsky.github.io/fortran-playground/gams/K1/) | Least squares (L-2) approximation |
| [m_attr](https://beliavsky.github.io/fortran-playground/gams/packages/m_attr/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [m_attr](https://beliavsky.github.io/fortran-playground/gams/packages/m_attr/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [m_attr](https://beliavsky.github.io/fortran-playground/gams/packages/m_attr/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [m_calculator](https://beliavsky.github.io/fortran-playground/gams/packages/m_calculator/) | [C](https://beliavsky.github.io/fortran-playground/gams/C/) | Elementary and special functions |
| [m_cli2](https://beliavsky.github.io/fortran-playground/gams/packages/m_cli2/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [m_cli2](https://beliavsky.github.io/fortran-playground/gams/packages/m_cli2/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [m_cli2](https://beliavsky.github.io/fortran-playground/gams/packages/m_cli2/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [m_color](https://beliavsky.github.io/fortran-playground/gams/packages/m_color/) | [Q](https://beliavsky.github.io/fortran-playground/gams/Q/) | Graphics |
| [m_framework](https://beliavsky.github.io/fortran-playground/gams/packages/m_framework/) | [S](https://beliavsky.github.io/fortran-playground/gams/S/) | Software development tools |
| [m_framework](https://beliavsky.github.io/fortran-playground/gams/packages/m_framework/) | [S3](https://beliavsky.github.io/fortran-playground/gams/S3/) | Dynamic program analysis tools |
| [m_io](https://beliavsky.github.io/fortran-playground/gams/packages/m_io/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [m_io](https://beliavsky.github.io/fortran-playground/gams/packages/m_io/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [m_list](https://beliavsky.github.io/fortran-playground/gams/packages/m_list/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [m_list](https://beliavsky.github.io/fortran-playground/gams/packages/m_list/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [m_list](https://beliavsky.github.io/fortran-playground/gams/packages/m_list/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [m_match](https://beliavsky.github.io/fortran-playground/gams/packages/m_match/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [m_match](https://beliavsky.github.io/fortran-playground/gams/packages/m_match/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [m_match](https://beliavsky.github.io/fortran-playground/gams/packages/m_match/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [m_sets](https://beliavsky.github.io/fortran-playground/gams/packages/m_sets/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [m_sets](https://beliavsky.github.io/fortran-playground/gams/packages/m_sets/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [m_sort](https://beliavsky.github.io/fortran-playground/gams/packages/m_sort/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [m_sort](https://beliavsky.github.io/fortran-playground/gams/packages/m_sort/) | [N6](https://beliavsky.github.io/fortran-playground/gams/N6/) | Sorting |
| [m_strings](https://beliavsky.github.io/fortran-playground/gams/packages/m_strings/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [m_strings](https://beliavsky.github.io/fortran-playground/gams/packages/m_strings/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [m_time](https://beliavsky.github.io/fortran-playground/gams/packages/m_time/) | [R](https://beliavsky.github.io/fortran-playground/gams/R/) | Service routines |
| [metis-fpm](https://beliavsky.github.io/fortran-playground/gams/packages/metis-fpm/) | [D](https://beliavsky.github.io/fortran-playground/gams/D/) | Linear Algebra |
| [minpack](https://beliavsky.github.io/fortran-playground/gams/packages/minpack/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [minpack](https://beliavsky.github.io/fortran-playground/gams/packages/minpack/) | [K1](https://beliavsky.github.io/fortran-playground/gams/K1/) | Least squares (L-2) approximation |
| [nafpack](https://beliavsky.github.io/fortran-playground/gams/packages/nafpack/) | [D](https://beliavsky.github.io/fortran-playground/gams/D/) | Linear Algebra |
| [nafpack](https://beliavsky.github.io/fortran-playground/gams/packages/nafpack/) | [D2](https://beliavsky.github.io/fortran-playground/gams/D2/) | Solution of systems of linear equations (including inversion, LU and related decompositions) |
| [nafpack](https://beliavsky.github.io/fortran-playground/gams/packages/nafpack/) | [D4](https://beliavsky.github.io/fortran-playground/gams/D4/) | Eigenvalues, eigenvectors |
| [ncio](https://beliavsky.github.io/fortran-playground/gams/packages/ncio/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [ncio](https://beliavsky.github.io/fortran-playground/gams/packages/ncio/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [neural-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/neural-fortran/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [nonlin](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [nonlin](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/) | [K1](https://beliavsky.github.io/fortran-playground/gams/K1/) | Least squares (L-2) approximation |
| [odrpack95](https://beliavsky.github.io/fortran-playground/gams/packages/odrpack95/) | [G](https://beliavsky.github.io/fortran-playground/gams/G/) | Optimization |
| [odrpack95](https://beliavsky.github.io/fortran-playground/gams/packages/odrpack95/) | [G2](https://beliavsky.github.io/fortran-playground/gams/G2/) | Constrained |
| [odrpack95](https://beliavsky.github.io/fortran-playground/gams/packages/odrpack95/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [odrpack95](https://beliavsky.github.io/fortran-playground/gams/packages/odrpack95/) | [K1](https://beliavsky.github.io/fortran-playground/gams/K1/) | Least squares (L-2) approximation |
| [orderpack](https://beliavsky.github.io/fortran-playground/gams/packages/orderpack/) | [L](https://beliavsky.github.io/fortran-playground/gams/L/) | Statistics, probability |
| [orderpack](https://beliavsky.github.io/fortran-playground/gams/packages/orderpack/) | [L1](https://beliavsky.github.io/fortran-playground/gams/L1/) | Data summarization |
| [paramcard](https://beliavsky.github.io/fortran-playground/gams/packages/paramcard/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [paramcard](https://beliavsky.github.io/fortran-playground/gams/packages/paramcard/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [paramcard](https://beliavsky.github.io/fortran-playground/gams/packages/paramcard/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [parff](https://beliavsky.github.io/fortran-playground/gams/packages/parff/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [parff](https://beliavsky.github.io/fortran-playground/gams/packages/parff/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [peaks](https://beliavsky.github.io/fortran-playground/gams/packages/peaks/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [peaks](https://beliavsky.github.io/fortran-playground/gams/packages/peaks/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [pfunit](https://beliavsky.github.io/fortran-playground/gams/packages/pfunit/) | [S](https://beliavsky.github.io/fortran-playground/gams/S/) | Software development tools |
| [pointsets](https://beliavsky.github.io/fortran-playground/gams/packages/pointsets/) | [P](https://beliavsky.github.io/fortran-playground/gams/P/) | Computational geometry |
| [popen-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/popen-fortran/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [popen-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/popen-fortran/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [popen-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/popen-fortran/) | [S](https://beliavsky.github.io/fortran-playground/gams/S/) | Software development tools |
| [pyplot-fortran](https://beliavsky.github.io/fortran-playground/gams/packages/pyplot-fortran/) | [Q](https://beliavsky.github.io/fortran-playground/gams/Q/) | Graphics |
| [quaff](https://beliavsky.github.io/fortran-playground/gams/packages/quaff/) | [Z](https://beliavsky.github.io/fortran-playground/gams/Z/) | Other |
| [regridpack](https://beliavsky.github.io/fortran-playground/gams/packages/regridpack/) | [E2](https://beliavsky.github.io/fortran-playground/gams/E2/) | Multivariate data (surface fitting) |
| [ryu_fortran](https://beliavsky.github.io/fortran-playground/gams/packages/ryu_fortran/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [ryu_fortran](https://beliavsky.github.io/fortran-playground/gams/packages/ryu_fortran/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [specfun](https://beliavsky.github.io/fortran-playground/gams/packages/specfun/) | [C7](https://beliavsky.github.io/fortran-playground/gams/C7/) | Gamma |
| [specfun](https://beliavsky.github.io/fortran-playground/gams/packages/specfun/) | [C10](https://beliavsky.github.io/fortran-playground/gams/C10/) | Bessel functions |
| [specfunc-fullerton](https://beliavsky.github.io/fortran-playground/gams/packages/specfunc-fullerton/) | [C5](https://beliavsky.github.io/fortran-playground/gams/C5/) | Exponential and logarithmic integrals |
| [specfunc-fullerton](https://beliavsky.github.io/fortran-playground/gams/packages/specfunc-fullerton/) | [C10](https://beliavsky.github.io/fortran-playground/gams/C10/) | Bessel functions |
| [specialmatrices](https://beliavsky.github.io/fortran-playground/gams/packages/specialmatrices/) | [D1](https://beliavsky.github.io/fortran-playground/gams/D1/) | Elementary vector and matrix operations |
| [specialmatrices](https://beliavsky.github.io/fortran-playground/gams/packages/specialmatrices/) | [D3](https://beliavsky.github.io/fortran-playground/gams/D3/) | Determinants |
| [spectrum](https://beliavsky.github.io/fortran-playground/gams/packages/spectrum/) | [K](https://beliavsky.github.io/fortran-playground/gams/K/) | Approximation |
| [spectrum](https://beliavsky.github.io/fortran-playground/gams/packages/spectrum/) | [K5](https://beliavsky.github.io/fortran-playground/gams/K5/) | Smoothing |
| [spectrum](https://beliavsky.github.io/fortran-playground/gams/packages/spectrum/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [stdlib](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/) | [A](https://beliavsky.github.io/fortran-playground/gams/A/) | Arithmetic, error analysis |
| [stdlib](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/) | [C](https://beliavsky.github.io/fortran-playground/gams/C/) | Elementary and special functions |
| [stdlib](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/) | [D1](https://beliavsky.github.io/fortran-playground/gams/D1/) | Elementary vector and matrix operations |
| [stdlib](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [stdlib](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/) | [N4](https://beliavsky.github.io/fortran-playground/gams/N4/) | Storage management (e.g., stacks, heaps, trees) |
| [stdlib](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/) | [N5](https://beliavsky.github.io/fortran-playground/gams/N5/) | Searching |
| [stdlib](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/) | [R](https://beliavsky.github.io/fortran-playground/gams/R/) | Service routines |
| [stdlib](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/) | [R3](https://beliavsky.github.io/fortran-playground/gams/R3/) | Error handling |
| [strff](https://beliavsky.github.io/fortran-playground/gams/packages/strff/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [strff](https://beliavsky.github.io/fortran-playground/gams/packages/strff/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [stringsort](https://beliavsky.github.io/fortran-playground/gams/packages/stringsort/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [stringsort](https://beliavsky.github.io/fortran-playground/gams/packages/stringsort/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [stringsort](https://beliavsky.github.io/fortran-playground/gams/packages/stringsort/) | [N6](https://beliavsky.github.io/fortran-playground/gams/N6/) | Sorting |
| [test-drive](https://beliavsky.github.io/fortran-playground/gams/packages/test-drive/) | [S](https://beliavsky.github.io/fortran-playground/gams/S/) | Software development tools |
| [test-drive](https://beliavsky.github.io/fortran-playground/gams/packages/test-drive/) | [S3](https://beliavsky.github.io/fortran-playground/gams/S3/) | Dynamic program analysis tools |
| [toml-f](https://beliavsky.github.io/fortran-playground/gams/packages/toml-f/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [toml-f](https://beliavsky.github.io/fortran-playground/gams/packages/toml-f/) | [N1](https://beliavsky.github.io/fortran-playground/gams/N1/) | Input, output |
| [toml-f](https://beliavsky.github.io/fortran-playground/gams/packages/toml-f/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |
| [tsunami](https://beliavsky.github.io/fortran-playground/gams/packages/tsunami/) | [I](https://beliavsky.github.io/fortran-playground/gams/I/) | Differential and integral equations |
| [tsunami](https://beliavsky.github.io/fortran-playground/gams/packages/tsunami/) | [I2](https://beliavsky.github.io/fortran-playground/gams/I2/) | Partial differential equations |
| [utf8-f](https://beliavsky.github.io/fortran-playground/gams/packages/utf8-f/) | [N](https://beliavsky.github.io/fortran-playground/gams/N/) | Data handling |
| [utf8-f](https://beliavsky.github.io/fortran-playground/gams/packages/utf8-f/) | [N3](https://beliavsky.github.io/fortran-playground/gams/N3/) | Character manipulation |

## Procedure evidence and remaining driver work

Statuses below apply to each recorded procedure/class pair. A driver for a different class of the same procedure does not verify this pair. Follow the procedure link for pinned source, author examples and limitations.

| Package / procedure | Class | Evidence |
| --- | --- | --- |
| [2decomp-fft / 2decomp-fft-c2c](https://beliavsky.github.io/fortran-playground/gams/packages/2decomp-fft/#2decomp-fft-c2c) | J1 | source-supported |
| [ad_dnsvm / ad-dnsvm-get-dns](https://beliavsky.github.io/fortran-playground/gams/packages/ad_dnsvm/#ad-dnsvm-get-dns) | H1 | verified |
| [amosf90 / amosf90-bessel](https://beliavsky.github.io/fortran-playground/gams/packages/amosf90/#amosf90-bessel) | C10 | verified |
| [any / any-values](https://beliavsky.github.io/fortran-playground/gams/packages/any/#any-values) | N4 | source-supported |
| [aotus / aotus-config](https://beliavsky.github.io/fortran-playground/gams/packages/aotus/#aotus-config) | N1 | source-supported |
| [argparse-f / argparse-f-options](https://beliavsky.github.io/fortran-playground/gams/packages/argparse-f/#argparse-f-options) | N3 | source-supported |
| [arpack-ng / arpack-eigenpairs](https://beliavsky.github.io/fortran-playground/gams/packages/arpack-ng/#arpack-eigenpairs) | D4a1 | verified |
| [array_range / array-range-bounds](https://beliavsky.github.io/fortran-playground/gams/packages/array_range/#array-range-bounds) | R | source-supported |
| [astro-fortran / astro-fortran-g2icrs](https://beliavsky.github.io/fortran-playground/gams/packages/astro-fortran/#astro-fortran-g2icrs) | P | source-supported |
| [athena / athena-dense](https://beliavsky.github.io/fortran-playground/gams/packages/athena/#athena-dense) | K | source-supported |
| [berkeley-assert / assert-contracts](https://beliavsky.github.io/fortran-playground/gams/packages/berkeley-assert/#assert-contracts) | S3 | source-supported |
| [berkeley-assert / assert-contracts](https://beliavsky.github.io/fortran-playground/gams/packages/berkeley-assert/#assert-contracts) | R2 | source-supported |
| [blas-interface / blas-interface-blas-gemm](https://beliavsky.github.io/fortran-playground/gams/packages/blas-interface/#blas-interface-blas-gemm) | D1b6 | verified |
| [bspline-fortran / bspline-fortran-bspline-1d](https://beliavsky.github.io/fortran-playground/gams/packages/bspline-fortran/#bspline-fortran-bspline-1d) | E1a | verified |
| [bspline-fortran / bspline-fortran-bspline-2d](https://beliavsky.github.io/fortran-playground/gams/packages/bspline-fortran/#bspline-fortran-bspline-2d) | E2a | verified |
| [bstrith / bstrith-operations](https://beliavsky.github.io/fortran-playground/gams/packages/bstrith/#bstrith-operations) | A1 | source-supported |
| [bstrith / bstrith-operations](https://beliavsky.github.io/fortran-playground/gams/packages/bstrith/#bstrith-operations) | N2 | verified |
| [carlson-elliptic-integrals / carlson-elliptic-integrals-api](https://beliavsky.github.io/fortran-playground/gams/packages/carlson-elliptic-integrals/#carlson-elliptic-integrals-api) | C14 | verified |
| [config-fortran / configuration-values](https://beliavsky.github.io/fortran-playground/gams/packages/config-fortran/#configuration-values) | N1 | source-supported |
| [config-fortran / configuration-values](https://beliavsky.github.io/fortran-playground/gams/packages/config-fortran/#configuration-values) | N3 | source-supported |
| [conmax / conmax-slnpro](https://beliavsky.github.io/fortran-playground/gams/packages/conmax/#conmax-slnpro) | G2a | verified |
| [conmin / conmin-conmin-class](https://beliavsky.github.io/fortran-playground/gams/packages/conmin/#conmin-conmin-class) | G2h3b1b | source-supported |
| [coretran / coretran-neighbor](https://beliavsky.github.io/fortran-playground/gams/packages/coretran/#coretran-neighbor) | P | source-supported |
| [coretran / coretran-neighbor](https://beliavsky.github.io/fortran-playground/gams/packages/coretran/#coretran-neighbor) | N5 | source-supported |
| [coretran / coretran-sort](https://beliavsky.github.io/fortran-playground/gams/packages/coretran/#coretran-sort) | N6 | source-supported |
| [daglib / daglib-toposort](https://beliavsky.github.io/fortran-playground/gams/packages/daglib/#daglib-toposort) | P | source-supported |
| [daskr / daskr-ddaskr](https://beliavsky.github.io/fortran-playground/gams/packages/daskr/#daskr-ddaskr) | I1a2 | source-supported |
| [dbcsr / dbcsr-block-multiply](https://beliavsky.github.io/fortran-playground/gams/packages/dbcsr/#dbcsr-block-multiply) | D1 | source-supported |
| [dcuhre / dcuhre-dcuhre](https://beliavsky.github.io/fortran-playground/gams/packages/dcuhre/#dcuhre-dcuhre) | H2b1a1 | verified |
| [dde_solver / dde-solver-api](https://beliavsky.github.io/fortran-playground/gams/packages/dde_solver/#dde-solver-api) | I | source-supported |
| [ddeabm / ddeabm-ddeabm-class](https://beliavsky.github.io/fortran-playground/gams/packages/ddeabm/#ddeabm-ddeabm-class) | I1a1b | verified |
| [ddpcm / ddpcm-solvation](https://beliavsky.github.io/fortran-playground/gams/packages/ddpcm/#ddpcm-solvation) | D2 | source-supported |
| [delaunaysparse / delaunay-interpolation](https://beliavsky.github.io/fortran-playground/gams/packages/delaunaysparse/#delaunay-interpolation) | E2 | source-supported |
| [dftatom / dftatom-radial](https://beliavsky.github.io/fortran-playground/gams/packages/dftatom/#dftatom-radial) | I1 | source-supported |
| [dftd4 / dftd4-dispersion](https://beliavsky.github.io/fortran-playground/gams/packages/dftd4/#dftd4-dispersion) | Z | source-supported |
| [diffeq / diffeq-runge-kutta-45](https://beliavsky.github.io/fortran-playground/gams/packages/diffeq/#diffeq-runge-kutta-45) | I1a1a | source-supported |
| [differentia / differentia-ad](https://beliavsky.github.io/fortran-playground/gams/packages/differentia/#differentia-ad) | H1 | source-supported |
| [diffstruc / diffstruc-api](https://beliavsky.github.io/fortran-playground/gams/packages/diffstruc/#diffstruc-api) | H1 | source-supported |
| [dnaoad-fpm / dnaoad-fpm-api](https://beliavsky.github.io/fortran-playground/gams/packages/dnaoad-fpm/#dnaoad-fpm-api) | H1 | source-supported |
| [dop853 / dop853-dop853-class](https://beliavsky.github.io/fortran-playground/gams/packages/dop853/#dop853-dop853-class) | I1a1a | verified |
| [dtfft / dtfft-cpu-c2c](https://beliavsky.github.io/fortran-playground/gams/packages/dtfft/#dtfft-cpu-c2c) | J1 | source-supported |
| [dvode / dvode-dvode-t](https://beliavsky.github.io/fortran-playground/gams/packages/dvode/#dvode-dvode-t) | I1a2 | verified |
| [dynamics / dynamics-api](https://beliavsky.github.io/fortran-playground/gams/packages/dynamics/#dynamics-api) | I1 | source-supported |
| [easy-plplot / easy-plplot-png](https://beliavsky.github.io/fortran-playground/gams/packages/easy-plplot/#easy-plplot-png) | Q | source-supported |
| [econ-toolchain / econ-toolchain-api](https://beliavsky.github.io/fortran-playground/gams/packages/econ-toolchain/#econ-toolchain-api) | M | verified |
| [ecx / ecx-impedance](https://beliavsky.github.io/fortran-playground/gams/packages/ecx/#ecx-impedance) | A4 | source-supported |
| [enclose / enclose-strings](https://beliavsky.github.io/fortran-playground/gams/packages/enclose/#enclose-strings) | N3 | source-supported |
| [ennuf / ennuf-inference](https://beliavsky.github.io/fortran-playground/gams/packages/ennuf/#ennuf-inference) | K | source-supported |
| [erloff / erloff-errors](https://beliavsky.github.io/fortran-playground/gams/packages/erloff/#erloff-errors) | R | source-supported |
| [errstat / error-status](https://beliavsky.github.io/fortran-playground/gams/packages/errstat/#error-status) | R3 | source-supported |
| [fassert / assert-values](https://beliavsky.github.io/fortran-playground/gams/packages/fassert/#assert-values) | S3 | source-supported |
| [fassert / assert-values](https://beliavsky.github.io/fortran-playground/gams/packages/fassert/#assert-values) | R2 | source-supported |
| [fastconv / fastconv-conv1d-t](https://beliavsky.github.io/fortran-playground/gams/packages/fastconv/#fastconv-conv1d-t) | J2 | verified |
| [fastmath / fastmath-fexp](https://beliavsky.github.io/fortran-playground/gams/packages/fastmath/#fastmath-fexp) | C4b | source-supported |
| [fastmath / fastmath-frsqrt](https://beliavsky.github.io/fortran-playground/gams/packages/fastmath/#fastmath-frsqrt) | C2 | source-supported |
| [fatode / fatode-tangent](https://beliavsky.github.io/fortran-playground/gams/packages/fatode/#fatode-tangent) | I1 | source-supported |
| [fdict / fdict-dictionary](https://beliavsky.github.io/fortran-playground/gams/packages/fdict/#fdict-dictionary) | N4 | source-supported |
| [fdict / fdict-dictionary](https://beliavsky.github.io/fortran-playground/gams/packages/fdict/#fdict-dictionary) | N5 | source-supported |
| [featom / featom-api](https://beliavsky.github.io/fortran-playground/gams/packages/featom/#featom-api) | I1b | verified |
| [fed / fed-format](https://beliavsky.github.io/fortran-playground/gams/packages/fed/#fed-format) | N1 | source-supported |
| [fed / fed-format](https://beliavsky.github.io/fortran-playground/gams/packages/fed/#fed-format) | N3 | source-supported |
| [feq-parse / feq-parse-evaluate](https://beliavsky.github.io/fortran-playground/gams/packages/feq-parse/#feq-parse-evaluate) | N3 | source-supported |
| [fftpack / fftpack-dct2](https://beliavsky.github.io/fortran-playground/gams/packages/fftpack/#fftpack-dct2) | J1a3 | verified |
| [fftpack / fftpack-fft](https://beliavsky.github.io/fortran-playground/gams/packages/fftpack/#fftpack-fft) | J1a2 | verified |
| [fglm / fglm-api](https://beliavsky.github.io/fortran-playground/gams/packages/fglm/#fglm-api) | D1 | source-supported |
| [fgsl / fgsl-qags](https://beliavsky.github.io/fortran-playground/gams/packages/fgsl/#fgsl-qags) | H2a1a1 | source-supported |
| [fiats / fiats-inference](https://beliavsky.github.io/fortran-playground/gams/packages/fiats/#fiats-inference) | K | source-supported |
| [finterp / finterp-linear-interp-1d](https://beliavsky.github.io/fortran-playground/gams/packages/finterp/#finterp-linear-interp-1d) | E1a | verified |
| [finterp / finterp-linear-interp-2d](https://beliavsky.github.io/fortran-playground/gams/packages/finterp/#finterp-linear-interp-2d) | E2a | verified |
| [fishpack / fishpack-api](https://beliavsky.github.io/fortran-playground/gams/packages/fishpack/#fishpack-api) | I2 | source-supported |
| [fitpack / fitpack-curve-derivative](https://beliavsky.github.io/fortran-playground/gams/packages/fitpack/#fitpack-curve-derivative) | H1 | source-supported |
| [fitpack / fitpack-fitpack-curve](https://beliavsky.github.io/fortran-playground/gams/packages/fitpack/#fitpack-fitpack-curve) | E1a | source-supported |
| [fitpack / fitpack-integral](https://beliavsky.github.io/fortran-playground/gams/packages/fitpack/#fitpack-integral) | H2a2b2 | source-supported |
| [fjsample / fjsample-jackerror](https://beliavsky.github.io/fortran-playground/gams/packages/fjsample/#fjsample-jackerror) | L4 | verified |
| [fkb / fkb-inference](https://beliavsky.github.io/fortran-playground/gams/packages/fkb/#fkb-inference) | K | source-supported |
| [flibcpp / flibcpp-sort-search](https://beliavsky.github.io/fortran-playground/gams/packages/flibcpp/#flibcpp-sort-search) | N5 | source-supported |
| [flibcpp / flibcpp-sort-search](https://beliavsky.github.io/fortran-playground/gams/packages/flibcpp/#flibcpp-sort-search) | N6 | source-supported |
| [flint / flint-erk-class](https://beliavsky.github.io/fortran-playground/gams/packages/flint/#flint-erk-class) | I1a1a | source-supported |
| [flook / flook-lua](https://beliavsky.github.io/fortran-playground/gams/packages/flook/#flook-lua) | S | source-supported |
| [fmin / fmin-scalar](https://beliavsky.github.io/fortran-playground/gams/packages/fmin/#fmin-scalar) | G1a1a | verified |
| [fmm2d / fmm2d-potentials](https://beliavsky.github.io/fortran-playground/gams/packages/fmm2d/#fmm2d-potentials) | D1 | source-supported |
| [fmm2d / fmm2d-potentials](https://beliavsky.github.io/fortran-playground/gams/packages/fmm2d/#fmm2d-potentials) | I2 | source-supported |
| [for_fifo_queue / fifo-queue-values](https://beliavsky.github.io/fortran-playground/gams/packages/for_fifo_queue/#fifo-queue-values) | N4 | source-supported |
| [fordiff / fordiff-derivative](https://beliavsky.github.io/fortran-playground/gams/packages/fordiff/#fordiff-derivative) | H1 | verified |
| [fordot / fordot-products](https://beliavsky.github.io/fortran-playground/gams/packages/fordot/#fordot-products) | D1 | source-supported |
| [foreig / foreig-eig](https://beliavsky.github.io/fortran-playground/gams/packages/foreig/#foreig-eig) | D4a1 | source-supported |
| [forinv / forinv-inv](https://beliavsky.github.io/fortran-playground/gams/packages/forinv/#forinv-inv) | D9c | verified |
| [forlab / forlab-solve](https://beliavsky.github.io/fortran-playground/gams/packages/forlab/#forlab-solve) | D9a1 | source-supported |
| [formal / formal-divergence](https://beliavsky.github.io/fortran-playground/gams/packages/formal/#formal-divergence) | H1 | source-supported |
| [formal / formal-divergence](https://beliavsky.github.io/fortran-playground/gams/packages/formal/#formal-divergence) | H2 | source-supported |
| [formal / formal-divergence](https://beliavsky.github.io/fortran-playground/gams/packages/formal/#formal-divergence) | I2 | source-supported |
| [formatmul / formatmul-products](https://beliavsky.github.io/fortran-playground/gams/packages/formatmul/#formatmul-products) | D1 | source-supported |
| [forpca / forpca-pca](https://beliavsky.github.io/fortran-playground/gams/packages/forpca/#forpca-pca) | D6 | source-supported |
| [forpca / forpca-pca](https://beliavsky.github.io/fortran-playground/gams/packages/forpca/#forpca-pca) | L13b | source-supported |
| [forpy / forpy-embedding](https://beliavsky.github.io/fortran-playground/gams/packages/forpy/#forpy-embedding) | S | source-supported |
| [forsolver / forsolver-nlsolver](https://beliavsky.github.io/fortran-playground/gams/packages/forsolver/#forsolver-nlsolver) | F1b | source-supported |
| [forsvd / forsvd-api](https://beliavsky.github.io/fortran-playground/gams/packages/forsvd/#forsvd-api) | D6 | source-supported |
| [fortime / serial-timers](https://beliavsky.github.io/fortran-playground/gams/packages/fortime/#serial-timers) | R | source-supported |
| [fortimize / fortimize-gradient-descent](https://beliavsky.github.io/fortran-playground/gams/packages/fortimize/#fortimize-gradient-descent) | G1b | source-supported |
| [fortimize / fortimize-nelder-mead](https://beliavsky.github.io/fortran-playground/gams/packages/fortimize/#fortimize-nelder-mead) | G1b | source-supported |
| [fortran-astrodynamics-toolkit / fortran-astrodynamics-toolkit-orbital-elements-to-rv](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-astrodynamics-toolkit/#fortran-astrodynamics-toolkit-orbital-elements-to-rv) | P | source-supported |
| [fortran-bessels / fortran-bessels-api](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-bessels/#fortran-bessels-api) | C10b1 | verified |
| [fortran-curl / fortran-curl-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-curl/#fortran-curl-demo-api) | N3 | source-supported |
| [fortran-error-handler / error-validation](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-error-handler/#error-validation) | R2 | source-supported |
| [fortran-error-handler / error-validation](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-error-handler/#error-validation) | R3 | source-supported |
| [fortran-fast-float / numeric-parsing](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-fast-float/#numeric-parsing) | N3 | source-supported |
| [fortran-flann / fortran-flann-knn-search](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-flann/#fortran-flann-knn-search) | N5 | source-supported |
| [fortran-lapack / fortran-lapack-eigh](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lapack/#fortran-lapack-eigh) | D4a1 | source-supported |
| [fortran-lapack / fortran-lapack-gesvd](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lapack/#fortran-lapack-gesvd) | D6 | verified |
| [fortran-lapack / fortran-lapack-lstsq](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lapack/#fortran-lapack-lstsq) | D9a1 | verified |
| [fortran-lapack / fortran-lapack-qr](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lapack/#fortran-lapack-qr) | D5 | verified |
| [fortran-lapack / fortran-lapack-solve](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lapack/#fortran-lapack-solve) | D2a1 | verified |
| [fortran-lapack / fortran-lapack-svd](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lapack/#fortran-lapack-svd) | D6 | source-supported |
| [fortran-lapack / fortran-lapack-syev](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lapack/#fortran-lapack-syev) | D4a1 | verified |
| [fortran-lmdb / lmdb-transactions](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lmdb/#lmdb-transactions) | N4 | source-supported |
| [fortran-lmdb / lmdb-transactions](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lmdb/#lmdb-transactions) | N5 | source-supported |
| [fortran-lua53 / lua53-interface](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lua53/#lua53-interface) | S | source-supported |
| [fortran-lua54 / lua-call](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-lua54/#lua-call) | S | source-supported |
| [fortran-modbus / fortran-modbus-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-modbus/#fortran-modbus-demo-api) | N2 | source-supported |
| [fortran-primes / fortran-primes-is-prime](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-primes/#fortran-primes-is-prime) | B | verified |
| [fortran-sdl2 / fortran-sdl2-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-sdl2/#fortran-sdl2-demo-api) | Q | source-supported |
| [fortran-simplify / fortran-simplify-perpendicular](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-simplify/#fortran-simplify-perpendicular) | P | source-supported |
| [fortran-simplify / fortran-simplify-perpendicular](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-simplify/#fortran-simplify-perpendicular) | K | source-supported |
| [fortran-string-to-real / fortran-string-to-real-str2real](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-string-to-real/#fortran-string-to-real-str2real) | A6 | source-supported |
| [fortran-tcl86 / tcl-evaluate](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-tcl86/#tcl-evaluate) | S | source-supported |
| [fortran-tokenizer / tokenizer-fields](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-tokenizer/#tokenizer-fields) | N3 | source-supported |
| [fortran-unix / unix-files](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-unix/#unix-files) | N1 | source-supported |
| [fortran-utils / fortran-utils-splines](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-utils/#fortran-utils-splines) | E1 | source-supported |
| [fortran-utils / fortran-utils-splines](https://beliavsky.github.io/fortran-playground/gams/packages/fortran-utils/#fortran-utils-splines) | N6 | source-supported |
| [fortran_cubatures / fortran-cubatures-cubature](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_cubatures/#fortran-cubatures-cubature) | H2c | verified |
| [fortran_function_parser / fortran-function-parser-evaluate](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_function_parser/#fortran-function-parser-evaluate) | N3 | source-supported |
| [fortran_test_helper / fortran-test-helper-create-r64-array](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_test_helper/#fortran-test-helper-create-r64-array) | L6a21 | source-supported |
| [fortran_vector / fortran-vector-storage](https://beliavsky.github.io/fortran-playground/gams/packages/fortran_vector/#fortran-vector-storage) | N4 | source-supported |
| [fortranlib / fortranlib-numerics](https://beliavsky.github.io/fortran-playground/gams/packages/fortranlib/#fortranlib-numerics) | E1 | source-supported |
| [fortranlib / fortranlib-numerics](https://beliavsky.github.io/fortran-playground/gams/packages/fortranlib/#fortranlib-numerics) | F1 | source-supported |
| [fortranlib / fortranlib-numerics](https://beliavsky.github.io/fortran-playground/gams/packages/fortranlib/#fortranlib-numerics) | H2 | source-supported |
| [fortsa / fortsa-acvf](https://beliavsky.github.io/fortran-playground/gams/packages/fortsa/#fortsa-acvf) | L10a2a | verified |
| [forwarddiff / forwarddiff-derivative](https://beliavsky.github.io/fortran-playground/gams/packages/forwarddiff/#forwarddiff-derivative) | H1 | source-supported |
| [friction / friction-fit](https://beliavsky.github.io/fortran-playground/gams/packages/friction/#friction-fit) | L8 | source-supported |
| [friction / friction-internal-state](https://beliavsky.github.io/fortran-playground/gams/packages/friction/#friction-internal-state) | I1 | source-supported |
| [fsparse / fsparse-dense2coo](https://beliavsky.github.io/fortran-playground/gams/packages/fsparse/#fsparse-dense2coo) | D1b9 | source-supported |
| [fsparse / fsparse-matvec](https://beliavsky.github.io/fortran-playground/gams/packages/fsparse/#fsparse-matvec) | D1b4 | verified |
| [fstats / fstats-mean](https://beliavsky.github.io/fortran-playground/gams/packages/fstats/#fstats-mean) | L1a1a | verified |
| [fstats / fstats-variance](https://beliavsky.github.io/fortran-playground/gams/packages/fstats/#fstats-variance) | L1a1b | verified |
| [ftl / ftl-containers](https://beliavsky.github.io/fortran-playground/gams/packages/ftl/#ftl-containers) | N4 | source-supported |
| [ftl / ftl-containers](https://beliavsky.github.io/fortran-playground/gams/packages/ftl/#ftl-containers) | N5 | source-supported |
| [ftorch / ftorch-inference](https://beliavsky.github.io/fortran-playground/gams/packages/ftorch/#ftorch-inference) | K | source-supported |
| [fundamental_constants / fundamental-codata](https://beliavsky.github.io/fortran-playground/gams/packages/fundamental_constants/#fundamental-codata) | R | source-supported |
| [fycollections / fycollections-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/fycollections/#fycollections-demo-api) | N4 | source-supported |
| [fycollections / fycollections-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/fycollections/#fycollections-demo-api) | N5 | source-supported |
| [gaussjacobiquad / gaussjacobiquad-gauss-jacobi](https://beliavsky.github.io/fortran-playground/gams/packages/gaussjacobiquad/#gaussjacobiquad-gauss-jacobi) | H2c | verified |
| [geodesic-fortran / geodesic-fortran-inverse](https://beliavsky.github.io/fortran-playground/gams/packages/geodesic-fortran/#geodesic-fortran-inverse) | P | source-supported |
| [geompack / geompack-r8tris2](https://beliavsky.github.io/fortran-playground/gams/packages/geompack/#geompack-r8tris2) | P | source-supported |
| [gftl / gftl-vector](https://beliavsky.github.io/fortran-playground/gams/packages/gftl/#gftl-vector) | N4 | source-supported |
| [gftl-shared / gftl-shared-containers](https://beliavsky.github.io/fortran-playground/gams/packages/gftl-shared/#gftl-shared-containers) | N4 | source-supported |
| [gftl-shared / gftl-shared-containers](https://beliavsky.github.io/fortran-playground/gams/packages/gftl-shared/#gftl-shared-containers) | N5 | source-supported |
| [graphstruc / graphstruc-add-vertex](https://beliavsky.github.io/fortran-playground/gams/packages/graphstruc/#graphstruc-add-vertex) | N4 | source-supported |
| [gslib / gslib-api](https://beliavsky.github.io/fortran-playground/gams/packages/gslib/#gslib-api) | E2 | source-supported |
| [gslib / gslib-api](https://beliavsky.github.io/fortran-playground/gams/packages/gslib/#gslib-api) | L13 | source-supported |
| [gtk-fortran / gtk-fortran-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/gtk-fortran/#gtk-fortran-demo-api) | Q | source-supported |
| [heatflow / heatflow-evolution](https://beliavsky.github.io/fortran-playground/gams/packages/heatflow/#heatflow-evolution) | I2 | source-supported |
| [heatflow / heatflow-sparse](https://beliavsky.github.io/fortran-playground/gams/packages/heatflow/#heatflow-sparse) | D2 | source-supported |
| [hrweno / hrweno-reconstruction](https://beliavsky.github.io/fortran-playground/gams/packages/hrweno/#hrweno-reconstruction) | I2 | source-supported |
| [hrweno / hrweno-tvd](https://beliavsky.github.io/fortran-playground/gams/packages/hrweno/#hrweno-tvd) | I1 | source-supported |
| [integer_set / integer-set-storage](https://beliavsky.github.io/fortran-playground/gams/packages/integer_set/#integer-set-storage) | N4 | source-supported |
| [integrate_fortran / integrate-fortran-gauss-leg-nd](https://beliavsky.github.io/fortran-playground/gams/packages/integrate_fortran/#integrate-fortran-gauss-leg-nd) | H2b1a2 | verified |
| [interpolation / interpolation-interp1](https://beliavsky.github.io/fortran-playground/gams/packages/interpolation/#interpolation-interp1) | E1a | source-supported |
| [io-fortran-library / io-fortran-library-to-file](https://beliavsky.github.io/fortran-playground/gams/packages/io-fortran-library/#io-fortran-library-to-file) | N1 | source-supported |
| [io_utilities / io-utilities-keyvars](https://beliavsky.github.io/fortran-playground/gams/packages/io_utilities/#io-utilities-keyvars) | N1 | source-supported |
| [jeyemhex-regex / jeyemhex-regex-strings](https://beliavsky.github.io/fortran-playground/gams/packages/jeyemhex-regex/#jeyemhex-regex-strings) | N3 | source-supported |
| [jeyemhex-regex / jeyemhex-regex-strings](https://beliavsky.github.io/fortran-playground/gams/packages/jeyemhex-regex/#jeyemhex-regex-strings) | N5 | source-supported |
| [julienne / julienne-diagnosis](https://beliavsky.github.io/fortran-playground/gams/packages/julienne/#julienne-diagnosis) | S3 | source-supported |
| [julienne / julienne-diagnosis](https://beliavsky.github.io/fortran-playground/gams/packages/julienne/#julienne-diagnosis) | R2 | source-supported |
| [kdtree2 / spatial-neighbors](https://beliavsky.github.io/fortran-playground/gams/packages/kdtree2/#spatial-neighbors) | P | source-supported |
| [kdtree2 / spatial-neighbors](https://beliavsky.github.io/fortran-playground/gams/packages/kdtree2/#spatial-neighbors) | N5 | source-supported |
| [kiss / kiss-cg-dense](https://beliavsky.github.io/fortran-playground/gams/packages/kiss/#kiss-cg-dense) | D2b1b | verified |
| [kissfft-f / kissfft-f-perform](https://beliavsky.github.io/fortran-playground/gams/packages/kissfft-f/#kissfft-f-perform) | J1a2 | verified |
| [kronrod / kronrod-rule](https://beliavsky.github.io/fortran-playground/gams/packages/kronrod/#kronrod-rule) | H2c | source-supported |
| [lbfgsb / lbfgsb-setulb](https://beliavsky.github.io/fortran-playground/gams/packages/lbfgsb/#lbfgsb-setulb) | G2h1a2 | verified |
| [lib_statistics / lib-statistics-logistic](https://beliavsky.github.io/fortran-playground/gams/packages/lib_statistics/#lib-statistics-logistic) | L8 | verified |
| [libdogleg-f / libdogleg-dense](https://beliavsky.github.io/fortran-playground/gams/packages/libdogleg-f/#libdogleg-dense) | G1b1b | verified |
| [libmbd / libmbd-dispersion](https://beliavsky.github.io/fortran-playground/gams/packages/libmbd/#libmbd-dispersion) | D4 | source-supported |
| [lightkrylov / lightkrylov-gmres](https://beliavsky.github.io/fortran-playground/gams/packages/lightkrylov/#lightkrylov-gmres) | D2 | source-supported |
| [linalg / linalg-eigen](https://beliavsky.github.io/fortran-playground/gams/packages/linalg/#linalg-eigen) | D4a1 | source-supported |
| [linalg / linalg-lu-factor](https://beliavsky.github.io/fortran-playground/gams/packages/linalg/#linalg-lu-factor) | D2a1 | source-supported |
| [linalg / linalg-qr-factor](https://beliavsky.github.io/fortran-playground/gams/packages/linalg/#linalg-qr-factor) | D5 | source-supported |
| [linalg / linalg-solve-least-squares](https://beliavsky.github.io/fortran-playground/gams/packages/linalg/#linalg-solve-least-squares) | D9a1 | source-supported |
| [linalg / linalg-svd](https://beliavsky.github.io/fortran-playground/gams/packages/linalg/#linalg-svd) | D6 | source-supported |
| [linalg_fortran / linalg-fortran-eigen](https://beliavsky.github.io/fortran-playground/gams/packages/linalg_fortran/#linalg-fortran-eigen) | D4a1 | verified |
| [linalg_fortran / linalg-fortran-inverse](https://beliavsky.github.io/fortran-playground/gams/packages/linalg_fortran/#linalg-fortran-inverse) | D2 | source-supported |
| [lookup-table-fortran / lookup-interpolation](https://beliavsky.github.io/fortran-playground/gams/packages/lookup-table-fortran/#lookup-interpolation) | E1a | source-supported |
| [lookup-table-fortran / lookup-interpolation](https://beliavsky.github.io/fortran-playground/gams/packages/lookup-table-fortran/#lookup-interpolation) | E3 | source-supported |
| [lsmr / lsmr-lsmr](https://beliavsky.github.io/fortran-playground/gams/packages/lsmr/#lsmr-lsmr) | D9a1 | source-supported |
| [lsqr / lsqr-lsqr-solver-ez](https://beliavsky.github.io/fortran-playground/gams/packages/lsqr/#lsqr-lsqr-solver-ez) | D9a1 | source-supported |
| [lusol / lusol-api](https://beliavsky.github.io/fortran-playground/gams/packages/lusol/#lusol-api) | D2a4 | source-supported |
| [m-process / m-process-pipe](https://beliavsky.github.io/fortran-playground/gams/packages/m-process/#m-process-pipe) | S | source-supported |
| [m-system / m-system-files](https://beliavsky.github.io/fortran-playground/gams/packages/m-system/#m-system-files) | N1 | source-supported |
| [m_calculator / m-calculator-dnum0](https://beliavsky.github.io/fortran-playground/gams/packages/m_calculator/#m-calculator-dnum0) | N3 | source-supported |
| [m_cli / m-cli-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/m_cli/#m-cli-demo-api) | N1 | source-supported |
| [m_cli / m-cli-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/m_cli/#m-cli-demo-api) | N3 | source-supported |
| [m_draw / m-draw-raster](https://beliavsky.github.io/fortran-playground/gams/packages/m_draw/#m-draw-raster) | Q | source-supported |
| [m_history / m-history-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/m_history/#m-history-demo-api) | N1 | source-supported |
| [m_history / m-history-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/m_history/#m-history-demo-api) | N3 | source-supported |
| [m_la / m-la-api](https://beliavsky.github.io/fortran-playground/gams/packages/m_la/#m-la-api) | D1 | source-supported |
| [maptran3d / maptran3d-geodetic2ecef](https://beliavsky.github.io/fortran-playground/gams/packages/maptran3d/#maptran3d-geodetic2ecef) | P | source-supported |
| [mersenne-twister-fortran / mersenne-twister-fortran-genrand64-real2](https://beliavsky.github.io/fortran-playground/gams/packages/mersenne-twister-fortran/#mersenne-twister-fortran-genrand64-real2) | L6a21 | verified |
| [metis-fpm / metis-fpm-metis-partgraphkway](https://beliavsky.github.io/fortran-playground/gams/packages/metis-fpm/#metis-fpm-metis-partgraphkway) | P | source-supported |
| [minpack / minpack-hybrd1](https://beliavsky.github.io/fortran-playground/gams/packages/minpack/#minpack-hybrd1) | F2 | verified |
| [minpack / minpack-lmder1](https://beliavsky.github.io/fortran-playground/gams/packages/minpack/#minpack-lmder1) | G1b1b | source-supported |
| [minpack / minpack-lmdif1](https://beliavsky.github.io/fortran-playground/gams/packages/minpack/#minpack-lmdif1) | G1b1a | verified |
| [minres / minres-minres-solver](https://beliavsky.github.io/fortran-playground/gams/packages/minres/#minres-minres-solver) | D2b4 | verified |
| [mpfun2020-var1 / mpfun2020-var1-mpcmplx](https://beliavsky.github.io/fortran-playground/gams/packages/mpfun2020-var1/#mpfun2020-var1-mpcmplx) | A4c | verified |
| [mpfun2020-var1 / mpfun2020-var1-mpreal](https://beliavsky.github.io/fortran-playground/gams/packages/mpfun2020-var1/#mpfun2020-var1-mpreal) | A3c | verified |
| [mpifx / mpifx-collectives](https://beliavsky.github.io/fortran-playground/gams/packages/mpifx/#mpifx-collectives) | R | source-supported |
| [nafpack / nafpack-execute-fft-plan-sp](https://beliavsky.github.io/fortran-playground/gams/packages/nafpack/#nafpack-execute-fft-plan-sp) | J1a2 | source-supported |
| [nc4fortran / nc4fortran-io](https://beliavsky.github.io/fortran-playground/gams/packages/nc4fortran/#nc4fortran-io) | N1 | source-supported |
| [netcdf-fortran / netcdf-classic-io](https://beliavsky.github.io/fortran-playground/gams/packages/netcdf-fortran/#netcdf-classic-io) | N1 | source-supported |
| [neural-fortran / neural-network-train](https://beliavsky.github.io/fortran-playground/gams/packages/neural-fortran/#neural-network-train) | G1b | source-supported |
| [nlesolver-fortran / nlesolver-fortran-nlesolver-type](https://beliavsky.github.io/fortran-playground/gams/packages/nlesolver-fortran/#nlesolver-fortran-nlesolver-type) | F2 | verified |
| [nlopt-f / nlopt-lbfgs](https://beliavsky.github.io/fortran-playground/gams/packages/nlopt-f/#nlopt-lbfgs) | G1b1b | verified |
| [nlopt-f / nlopt-lbfgs-bounds](https://beliavsky.github.io/fortran-playground/gams/packages/nlopt-f/#nlopt-lbfgs-bounds) | G2h1a2 | verified |
| [nonlin / nonlin-bfgs](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/#nonlin-bfgs) | G1b1a | source-supported |
| [nonlin / nonlin-bfgs](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/#nonlin-bfgs) | G1b1b | verified |
| [nonlin / nonlin-brent-solver](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/#nonlin-brent-solver) | F1b | verified |
| [nonlin / nonlin-least-squares](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/#nonlin-least-squares) | G1b1a | source-supported |
| [nonlin / nonlin-least-squares](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/#nonlin-least-squares) | G1b1b | source-supported |
| [nonlin / nonlin-nelder-mead](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/#nonlin-nelder-mead) | G1b1a | verified |
| [nonlin / nonlin-newton-1var](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/#nonlin-newton-1var) | F1b | verified |
| [nonlin / nonlin-newton-solver](https://beliavsky.github.io/fortran-playground/gams/packages/nonlin/#nonlin-newton-solver) | F2 | verified |
| [npy-for-fortran / npy-matrix](https://beliavsky.github.io/fortran-playground/gams/packages/npy-for-fortran/#npy-matrix) | N1 | source-supported |
| [ntpoly / ntpoly-inversion](https://beliavsky.github.io/fortran-playground/gams/packages/ntpoly/#ntpoly-inversion) | D2 | source-supported |
| [ntpoly / ntpoly-matrix-square-roots](https://beliavsky.github.io/fortran-playground/gams/packages/ntpoly/#ntpoly-matrix-square-roots) | D | source-supported |
| [nufft1d / nufft1d-transform](https://beliavsky.github.io/fortran-playground/gams/packages/nufft1d/#nufft1d-transform) | J1 | source-supported |
| [nufft2d / nufft2d-transform](https://beliavsky.github.io/fortran-playground/gams/packages/nufft2d/#nufft2d-transform) | J1 | source-supported |
| [numdiff / numdiff-compute-derivative](https://beliavsky.github.io/fortran-playground/gams/packages/numdiff/#numdiff-compute-derivative) | H1 | verified |
| [odepack / odepack-lsoda-class](https://beliavsky.github.io/fortran-playground/gams/packages/odepack/#odepack-lsoda-class) | I1a2 | verified |
| [odrpack95 / odrpack95-odr](https://beliavsky.github.io/fortran-playground/gams/packages/odrpack95/#odrpack95-odr) | L8 | verified |
| [ogpf / ogpf-contour](https://beliavsky.github.io/fortran-playground/gams/packages/ogpf/#ogpf-contour) | Q | source-supported |
| [optgra / optgra-optgra](https://beliavsky.github.io/fortran-playground/gams/packages/optgra/#optgra-optgra) | G2h3b1b | source-supported |
| [opti / opti-optimizer](https://beliavsky.github.io/fortran-playground/gams/packages/opti/#opti-optimizer) | G2i | source-supported |
| [orbs / orbs-bitsets](https://beliavsky.github.io/fortran-playground/gams/packages/orbs/#orbs-bitsets) | A1 | source-supported |
| [orbs / orbs-bitsets](https://beliavsky.github.io/fortran-playground/gams/packages/orbs/#orbs-bitsets) | N2 | source-supported |
| [orderpack / orderpack-rank](https://beliavsky.github.io/fortran-playground/gams/packages/orderpack/#orderpack-rank) | N6 | source-supported |
| [pchip / pchip-dpchim](https://beliavsky.github.io/fortran-playground/gams/packages/pchip/#pchip-dpchim) | E1a | verified |
| [penf / numerical-portability](https://beliavsky.github.io/fortran-playground/gams/packages/penf/#numerical-portability) | R1 | source-supported |
| [penf / numerical-portability](https://beliavsky.github.io/fortran-playground/gams/packages/penf/#numerical-portability) | N3 | source-supported |
| [pflogger / pflogger-logging](https://beliavsky.github.io/fortran-playground/gams/packages/pflogger/#pflogger-logging) | R | source-supported |
| [pikaia / pikaia-pikaia-class](https://beliavsky.github.io/fortran-playground/gams/packages/pikaia/#pikaia-pikaia-class) | G2i | verified |
| [plplot / plplot-demo-api](https://beliavsky.github.io/fortran-playground/gams/packages/plplot/#plplot-demo-api) | Q | source-supported |
| [pointsets / pointsets-arithmetic-spacing](https://beliavsky.github.io/fortran-playground/gams/packages/pointsets/#pointsets-arithmetic-spacing) | R | source-supported |
| [pointsets / pointsets-random-spacing](https://beliavsky.github.io/fortran-playground/gams/packages/pointsets/#pointsets-random-spacing) | L6a21 | source-supported |
| [poisfft / poisfft-periodic](https://beliavsky.github.io/fortran-playground/gams/packages/poisfft/#poisfft-periodic) | I2 | source-supported |
| [polyroots-fortran / polyroots-fortran-cpolyroots](https://beliavsky.github.io/fortran-playground/gams/packages/polyroots-fortran/#polyroots-fortran-cpolyroots) | F1a | verified |
| [polyroots-fortran / polyroots-fortran-polyroots](https://beliavsky.github.io/fortran-playground/gams/packages/polyroots-fortran/#polyroots-fortran-polyroots) | F1a | verified |
| [polyroots-fortran / polyroots-fortran-rpoly](https://beliavsky.github.io/fortran-playground/gams/packages/polyroots-fortran/#polyroots-fortran-rpoly) | F1a | verified |
| [powellopt / powellopt-bobyqa](https://beliavsky.github.io/fortran-playground/gams/packages/powellopt/#powellopt-bobyqa) | G2h1a1 | verified |
| [propack / propack-partial-svd](https://beliavsky.github.io/fortran-playground/gams/packages/propack/#propack-partial-svd) | D6 | source-supported |
| [psqp / psqp-psqpn](https://beliavsky.github.io/fortran-playground/gams/packages/psqp/#psqp-psqpn) | G2h3b1b | source-supported |
| [qcontainers / qcontainers-storage](https://beliavsky.github.io/fortran-playground/gams/packages/qcontainers/#qcontainers-storage) | N4 | source-supported |
| [qcontainers / qcontainers-storage](https://beliavsky.github.io/fortran-playground/gams/packages/qcontainers/#qcontainers-storage) | N5 | source-supported |
| [qdldl-fortran / qdldl-fortran-api](https://beliavsky.github.io/fortran-playground/gams/packages/qdldl-fortran/#qdldl-fortran-api) | D2b4 | verified |
| [qdutillib / qdutillib-api](https://beliavsky.github.io/fortran-playground/gams/packages/qdutillib/#qdutillib-api) | H2c | source-supported |
| [qnstop / qnstop-bounded](https://beliavsky.github.io/fortran-playground/gams/packages/qnstop/#qnstop-bounded) | G2 | source-supported |
| [quadpack / quadpack-dqag](https://beliavsky.github.io/fortran-playground/gams/packages/quadpack/#quadpack-dqag) | H2a1a1 | verified |
| [quadpack / quadpack-dqags](https://beliavsky.github.io/fortran-playground/gams/packages/quadpack/#quadpack-dqags) | H2a2a1 | verified |
| [quadrature-fortran / quadrature-fortran-integration-class-1d](https://beliavsky.github.io/fortran-playground/gams/packages/quadrature-fortran/#quadrature-fortran-integration-class-1d) | H2a1a1 | verified |
| [quaff / quaff-length-t](https://beliavsky.github.io/fortran-playground/gams/packages/quaff/#quaff-length-t) | A | source-supported |
| [raffle / raffle-periodic-distance](https://beliavsky.github.io/fortran-playground/gams/packages/raffle/#raffle-periodic-distance) | P | source-supported |
| [rational_number / rational-number-ratnumadd](https://beliavsky.github.io/fortran-playground/gams/packages/rational_number/#rational-number-ratnumadd) | A2 | verified |
| [rearrayfx / rearrayfx-storage](https://beliavsky.github.io/fortran-playground/gams/packages/rearrayfx/#rearrayfx-storage) | N4 | source-supported |
| [regridpack / regridpack-regrid](https://beliavsky.github.io/fortran-playground/gams/packages/regridpack/#regridpack-regrid) | E1a | source-supported |
| [rkf45 / rkf45-rkf45](https://beliavsky.github.io/fortran-playground/gams/packages/rkf45/#rkf45-rkf45) | I1a1a | source-supported |
| [rklib / rklib-rk4](https://beliavsky.github.io/fortran-playground/gams/packages/rklib/#rklib-rk4) | I1a1a | verified |
| [rndgen-fortran / rndgen-fortran-rnd](https://beliavsky.github.io/fortran-playground/gams/packages/rndgen-fortran/#rndgen-fortran-rnd) | L6a21 | source-supported |
| [rng-fortran / rng-distributions](https://beliavsky.github.io/fortran-playground/gams/packages/rng-fortran/#rng-distributions) | L6 | source-supported |
| [rng-fortran / rng-uniform](https://beliavsky.github.io/fortran-playground/gams/packages/rng-fortran/#rng-uniform) | L6a21 | source-supported |
| [rng-fortran / rng-uniform](https://beliavsky.github.io/fortran-playground/gams/packages/rng-fortran/#rng-uniform) | L6c | source-supported |
| [rngff / rngff-linear-congruential-t](https://beliavsky.github.io/fortran-playground/gams/packages/rngff/#rngff-linear-congruential-t) | L6a21 | verified |
| [rojff / rojff-json](https://beliavsky.github.io/fortran-playground/gams/packages/rojff/#rojff-json) | N1 | source-supported |
| [rojff / rojff-json](https://beliavsky.github.io/fortran-playground/gams/packages/rojff/#rojff-json) | N3 | source-supported |
| [roots-fortran / roots-fortran-brent](https://beliavsky.github.io/fortran-playground/gams/packages/roots-fortran/#roots-fortran-brent) | F1b | verified |
| [rpn-calculator-fortran / rpn-elementary](https://beliavsky.github.io/fortran-playground/gams/packages/rpn-calculator-fortran/#rpn-elementary) | C2 | source-supported |
| [rpn-calculator-fortran / rpn-elementary](https://beliavsky.github.io/fortran-playground/gams/packages/rpn-calculator-fortran/#rpn-elementary) | C4 | source-supported |
| [rpn-calculator-fortran / rpn-integer](https://beliavsky.github.io/fortran-playground/gams/packages/rpn-calculator-fortran/#rpn-integer) | B | verified |
| [rpn-calculator-fortran / rpn-special](https://beliavsky.github.io/fortran-playground/gams/packages/rpn-calculator-fortran/#rpn-special) | C7 | source-supported |
| [rpn-calculator-fortran / rpn-special](https://beliavsky.github.io/fortran-playground/gams/packages/rpn-calculator-fortran/#rpn-special) | C10 | source-supported |
| [ryu_fortran / ryu-fortran-d2shortest](https://beliavsky.github.io/fortran-playground/gams/packages/ryu_fortran/#ryu-fortran-d2shortest) | A6 | verified |
| [scalapackfx / scalapackfx-symmetric-eigenproblem](https://beliavsky.github.io/fortran-playground/gams/packages/scalapackfx/#scalapackfx-symmetric-eigenproblem) | D4a1 | source-supported |
| [scanner / scanner-text](https://beliavsky.github.io/fortran-playground/gams/packages/scanner/#scanner-text) | N3 | source-supported |
| [scifortran / scifortran-integration](https://beliavsky.github.io/fortran-playground/gams/packages/scifortran/#scifortran-integration) | H2 | source-supported |
| [seiscope-optimization / seiscope-optimization-api](https://beliavsky.github.io/fortran-playground/gams/packages/seiscope-optimization/#seiscope-optimization-api) | G1b1b | source-supported |
| [shunting-yard-fortran / shunting-yard-parser](https://beliavsky.github.io/fortran-playground/gams/packages/shunting-yard-fortran/#shunting-yard-parser) | N3 | source-supported |
| [simulated-annealing / simulated-annealing-simulated-annealing-type](https://beliavsky.github.io/fortran-playground/gams/packages/simulated-annealing/#simulated-annealing-simulated-annealing-type) | G2i | source-supported |
| [slicot / slicot-lyapunov](https://beliavsky.github.io/fortran-playground/gams/packages/slicot/#slicot-lyapunov) | D8 | verified |
| [slicot / slicot-sb04md](https://beliavsky.github.io/fortran-playground/gams/packages/slicot/#slicot-sb04md) | D8 | verified |
| [slicot / slicot-sb04qd](https://beliavsky.github.io/fortran-playground/gams/packages/slicot/#slicot-sb04qd) | D8 | verified |
| [slinked-list / linked-list-values](https://beliavsky.github.io/fortran-playground/gams/packages/slinked-list/#linked-list-values) | N4 | source-supported |
| [slsqp / slsqp-slsqp-solver](https://beliavsky.github.io/fortran-playground/gams/packages/slsqp/#slsqp-slsqp-solver) | G2h3b1b | verified |
| [smart-pointers / smart-pointer-lifetime](https://beliavsky.github.io/fortran-playground/gams/packages/smart-pointers/#smart-pointer-lifetime) | R | source-supported |
| [sparse_fortran / sparse-fortran-matmul](https://beliavsky.github.io/fortran-playground/gams/packages/sparse_fortran/#sparse-fortran-matmul) | D1b4 | source-supported |
| [specfun / specfun-bernob](https://beliavsky.github.io/fortran-playground/gams/packages/specfun/#specfun-bernob) | C19 | verified |
| [specfunc-fullerton / specfunc-fullerton-digamma](https://beliavsky.github.io/fortran-playground/gams/packages/specfunc-fullerton/#specfunc-fullerton-digamma) | C7c | verified |
| [specfunc-fullerton / specfunc-fullerton-fgamma](https://beliavsky.github.io/fortran-playground/gams/packages/specfunc-fullerton/#specfunc-fullerton-fgamma) | C7a | verified |
| [specialmatrices / specialmatrices-solve](https://beliavsky.github.io/fortran-playground/gams/packages/specialmatrices/#specialmatrices-solve) | D2 | source-supported |
| [spectrum / spectrum-convolve](https://beliavsky.github.io/fortran-playground/gams/packages/spectrum/#spectrum-convolve) | J2 | verified |
| [spectrum / spectrum-rfft](https://beliavsky.github.io/fortran-playground/gams/packages/spectrum/#spectrum-rfft) | J1a1 | source-supported |
| [spherepack / spherepack-api](https://beliavsky.github.io/fortran-playground/gams/packages/spherepack/#spherepack-api) | I2 | source-supported |
| [spherepack / spherepack-scalar-transform](https://beliavsky.github.io/fortran-playground/gams/packages/spherepack/#spherepack-scalar-transform) | J | source-supported |
| [splpak / splpak-splpak-type](https://beliavsky.github.io/fortran-playground/gams/packages/splpak/#splpak-splpak-type) | K1 | verified |
| [sqliteff / sqliteff-database](https://beliavsky.github.io/fortran-playground/gams/packages/sqliteff/#sqliteff-database) | N1 | source-supported |
| [sqliteff / sqliteff-database](https://beliavsky.github.io/fortran-playground/gams/packages/sqliteff/#sqliteff-database) | N5 | source-supported |
| [stdlib / stdlib-lstsq](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/#stdlib-lstsq) | D9a1 | verified |
| [stdlib / stdlib-mean](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/#stdlib-mean) | L1a1a | verified |
| [stdlib / stdlib-random-seed](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/#stdlib-random-seed) | L6c | verified |
| [stdlib / stdlib-solve](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/#stdlib-solve) | D2a1 | verified |
| [stdlib / stdlib-sort](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/#stdlib-sort) | N6 | verified |
| [stdlib / stdlib-var](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib/#stdlib-var) | L1a1b | verified |
| [stdlib-os / stdlib-os-files](https://beliavsky.github.io/fortran-playground/gams/packages/stdlib-os/#stdlib-os-files) | N1 | source-supported |
| [stiff3 / stiff3-stiff3](https://beliavsky.github.io/fortran-playground/gams/packages/stiff3/#stiff3-stiff3) | I1a2 | verified |
| [string-utf-8 / utf8-strings](https://beliavsky.github.io/fortran-playground/gams/packages/string-utf-8/#utf8-strings) | N3 | source-supported |
| [string-utf-8 / utf8-strings](https://beliavsky.github.io/fortran-playground/gams/packages/string-utf-8/#utf8-strings) | N5 | source-supported |
| [strith / strith-api](https://beliavsky.github.io/fortran-playground/gams/packages/strith/#strith-api) | A1 | verified |
| [strith / strith-api](https://beliavsky.github.io/fortran-playground/gams/packages/strith/#strith-api) | A6 | source-supported |
| [tsunami / tsunami-periodic-differences](https://beliavsky.github.io/fortran-playground/gams/packages/tsunami/#tsunami-periodic-differences) | H1 | source-supported |
| [twopnt / twopnt-solve](https://beliavsky.github.io/fortran-playground/gams/packages/twopnt/#twopnt-solve) | I1b | source-supported |
| [uint-fortran / uint-fortran-arithmetic](https://beliavsky.github.io/fortran-playground/gams/packages/uint-fortran/#uint-fortran-arithmetic) | A1 | source-supported |
| [veggies / veggies-tests](https://beliavsky.github.io/fortran-playground/gams/packages/veggies/#veggies-tests) | S3 | source-supported |
| [vtmop / vtmop-tradeoffs](https://beliavsky.github.io/fortran-playground/gams/packages/vtmop/#vtmop-tradeoffs) | G2 | source-supported |
| [y12m / y12m-y12mc](https://beliavsky.github.io/fortran-playground/gams/packages/y12m/#y12m-y12mc) | D2a4 | source-supported |
| [yafyaml / yafyaml-configuration](https://beliavsky.github.io/fortran-playground/gams/packages/yafyaml/#yafyaml-configuration) | N1 | source-supported |
| [yafyaml / yafyaml-configuration](https://beliavsky.github.io/fortran-playground/gams/packages/yafyaml/#yafyaml-configuration) | N3 | source-supported |

## Maintenance

Regenerate with `python xpackage_gams.py`; check with `python xpackage_gams.py --check`. The report and catalog labels use the same class-specific evidence rule. Saved successful driver verification is required before a driver enters the manifest.
