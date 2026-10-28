# Playground topics by package

159 selected packages; 304 distinct playground topics. GitHub topics were retrieved on 2026-10-28.

The playground topics below are editorial suggestions based on the saved package descriptions, categories, and GitHub labels. They describe the package, rather than claiming every feature is exercised by its example main program. They are not author-supplied GitHub topics.

Search defaults to the union of both topic sources. Choose **Topics: GitHub only** to exclude playground topics from matching. Names, descriptions, owners, and categories remain searchable. The two sources are labeled separately on the page.

## Maintaining the topics

Edit [playground-topics.json](../fpm_catalog/playground-topics.json), keyed by package ID. Prefer an existing term for a shared concept, such as `ode`, `quadrature`, `least-squares`, `random-numbers`, or `file-io`; add specific algorithm or format names where useful. Avoid generic `fortran` and `fpm` labels in our list. Add an entry whenever a selected package is added.

Run these commands from the repository root:

```text
python xpackage_topics.py
python xfpm_examples.py
```

The first command validates coverage and regenerates this page; use `--check` to check it without writing. The second updates the public search metadata. Both are offline and require no backend deployment or package recompilation. GitHub metadata refreshes never edit the playground topic file; regenerate this page after refreshing GitHub topics.

## Astronomy and orbits

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [astro-fortran](https://github.com/jacobwilliams/astro-fortran) — Fundamental astronomy models and coordinate transformations refactored from IAU SOFA. | `astronomy`, `coordinate-transformations`, `iau-sofa` | `astrometry`, `astronomy`, `fortran-package-manager` |
| [fortran-astrodynamics-toolkit](https://github.com/jacobwilliams/Fortran-Astrodynamics-Toolkit) — Orbital mechanics, coordinate transformations, and spacecraft trajectory tools. | `astrodynamics`, `coordinate-transformations`, `orbital-mechanics`, `spacecraft-trajectories` | `astrodynamics`, `ephemeris`, `fortran`, `fortran-package-manager`, `gravity-field`, `orbital-mechanics`, `orbital-simulation`, `runge-kutta`, `runge-kutta-adaptive-step-size` |

## Colors

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [forcolormap](https://github.com/vmagnin/forcolormap) — Scientific colormaps mapping scalar values to RGB colors. | `colormaps`, `colors`, `rgb`, `visualization` | `colormaps`, `fortran`, `fortran-package-manager` |
| [m_color](https://github.com/urbanjost/M_color) — Convert color names and RGB, HLS, HSV, and other color models. | `color-conversion`, `colors`, `hls`, `hsv`, `rgb` | `color-conversion`, `color-models`, `fortran`, `fortran-package-manager` |

## Command-line tools

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [argv-fortran](https://github.com/jacobwilliams/argv-fortran) — Read command-line arguments as allocatable strings. | `argument-parsing`, `command-line`, `strings` | `argv`, `fortran`, `fortran-package-manager` |
| [m_attr](https://github.com/urbanjost/M_attr) — Terminal styling markup with a plain-text output mode. | `command-line`, `terminal-styling`, `text-processing` | `ansi-escape-sequences`, `fortran`, `fortran-package-manager`, `terminal` |
| [m_cli2](https://github.com/urbanjost/M_CLI2) — Typed command-line parsing with defaults and help text. | `argument-parsing`, `command-line`, `configuration`, `help-text` | `argument`, `command-line`, `fortran`, `fortran-package-manager`, `parsing` |
| [paramcard](https://github.com/tueda/paramcard) — Named input parameters, defaults, string parsing and configuration summaries. | `configuration`, `defaults`, `input-parameters`, `parsing` | `command-line`, `fortran`, `fortran-library`, `fortran2008` |

## Containers and graphs

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [collections](https://github.com/jchristopherson/collections) — Generic dynamically growing lists and linked lists with polymorphic values. | `containers`, `dynamic-arrays`, `linked-lists`, `polymorphism` | `collection`, `collections`, `fortran`, `generic-collections`, `generic-list`, `linked-list`, `list`, `lists` |
| [daglib](https://github.com/jacobwilliams/daglib) — Directed acyclic graphs and topological ordering of dependencies. | `dependency-ordering`, `directed-acyclic-graphs`, `graphs`, `topological-sort` | `directed-acyclic-graph`, `fortran`, `fortran-package-manager`, `graphviz`, `graphviz-dot-language`, `toposort` |
| [fhash](https://github.com/LKedward/fhash) — Hash tables with generic keys and values. | `containers`, `dictionaries`, `hash-tables`, `polymorphism` | `fortran`, `fortran-package-manager`, `fpm`, `hashmap`, `hashtable` |
| [flist](https://github.com/jacobwilliams/flist) — Linked lists storing values of different types under named keys. | `containers`, `dictionaries`, `linked-lists`, `polymorphism` | `fortran`, `fortran-package-manager`, `linked-list` |
| [graphstruc](https://github.com/nedtaylor/graphstruc) — Derived types for graphs, vertices, edges and adjacency structures. | `adjacency-structures`, `containers`, `graphs` | `fortran`, `fortran-package-manager`, `graph-structures`, `graphs`, `library` |
| [m_list](https://github.com/urbanjost/M_list) — Maintain sorted arrays and small dictionaries through insertion and lookup. | `containers`, `dictionaries`, `searching`, `sorted-arrays` | `fortran-package-manager` |
| [m_sets](https://github.com/urbanjost/M_sets) — Union, intersection, membership, and unique values for arrays. | `arrays`, `searching`, `sets`, `unique-values` | `fortran`, `fortran-package-manager`, `matlab`, `sets` |
| [metis-fpm](https://github.com/gnikit/metis-fpm) — METIS graph partitioning and sparse matrix ordering through a Fortran interface. | `graph-partitioning`, `graphs`, `language-bindings`, `matrix-ordering`, `sparse-matrices` | None supplied |

## Data formats

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [csv-fortran](https://github.com/jacobwilliams/csv-fortran) — Read and write CSV files with typed columns. | `csv`, `file-io`, `serialization`, `tabular-data` | `csv`, `fortran`, `fortran-package-manager` |
| [fortran-messagepack](https://github.com/synthfi/fortran-messagepack) — Serialize and deserialize structured values in the compact MessagePack binary format. | `binary-data`, `messagepack`, `serialization` | `fortran`, `messagepack` |
| [h5fortran](https://github.com/geospace-code/h5fortran) — High-level HDF5 access for numerical arrays, strings and metadata. | `arrays`, `file-io`, `hdf5`, `metadata`, `scientific-data` | `fortran`, `hdf5`, `object-oriented-fortran` |
| [jonquil](https://github.com/toml-f/jonquil) — JSON parsing and serialization compatible with TOML Fortran types. | `json`, `parsing`, `serialization`, `toml` | `fortran-library`, `fortran-package-manager`, `json`, `json-parser`, `serde` |
| [json-fortran](https://github.com/jacobwilliams/json-fortran) — Read, write, and manipulate JSON documents. | `file-io`, `json`, `serialization` | `fortran`, `fortran-package-manager`, `json` |
| [ncio](https://github.com/alex-robinson/ncio) — Convenient NetCDF array input and output with dimensions, attributes and metadata. | `arrays`, `file-io`, `metadata`, `netcdf`, `scientific-data` | None supplied |
| [toml-f](https://github.com/toml-f/toml-f) — Parse and write TOML configuration files. | `configuration`, `file-io`, `parsing`, `toml` | `fortran-library`, `fortran-package-manager`, `serde`, `toml`, `toml-parser` |

## Databases

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran-sqlite3](https://github.com/interkosmos/fortran-sqlite3) — SQLite database bindings for creating tables, executing SQL and reading query results. | `databases`, `language-bindings`, `sql`, `sqlite` | `fortran`, `fortran-package-manager`, `fpm`, `sqlite`, `sqlite3` |

## Dates and times

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [datetime-fortran](https://github.com/wavebitscientific/datetime-fortran) — Date/time objects, durations, and calendar arithmetic. | `calendar-arithmetic`, `date-time`, `durations` | `datetime`, `fortran`, `strftime`, `timedelta` |
| [m_time](https://github.com/urbanjost/M_time) — Calendar arithmetic, Julian dates, and date/time formatting. | `calendar-arithmetic`, `date-time`, `formatting`, `julian-dates` | `calendar`, `date`, `date-formatting`, `datetime`, `fortran`, `fortran-package-manager`, `fpm`, `time` |

## Differential equations

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [daskr](https://github.com/davidpfister/daskr) — Differential-algebraic equation solver with root finding and direct or Krylov linear solvers. | `dae`, `differential-equations`, `iterative-solvers`, `krylov-methods`, `root-finding` | `dae`, `differential-equations`, `fortran`, `fortran-package-manager`, `netlib` |
| [ddeabm](https://github.com/jacobwilliams/ddeabm) — Adaptive Adams-Bashforth-Moulton ODE integration with event finding. | `adams-methods`, `adaptive-methods`, `event-detection`, `initial-value-problems`, `ode` | `adams-bashforth`, `fortran`, `fortran-package-manager`, `ode`, `root-finding`, `slatec` |
| [diffeq](https://github.com/jchristopherson/diffeq) — Adaptive explicit and implicit integrators for ordinary differential and differential-algebraic equations. | `adaptive-methods`, `dae`, `differential-equations`, `implicit-methods`, `ode` | `adams-bashforth-moulton`, `backwards-differentiation-formula`, `bdf`, `differential-algebraic-equations`, `differential-equations`, `esdirk`, `event-detection`, `implicit-runge-kutta`, `index-reduction`, `kennedy-carpenter`, `rosenbrock`, `runge-kutta-methods`, `tsitouras` |
| [dop853](https://github.com/jacobwilliams/dop853) — Adaptive eighth-order Runge-Kutta integration of ordinary differential equations. | `adaptive-methods`, `initial-value-problems`, `ode`, `runge-kutta` | `dop853`, `fortran`, `fortran-package-manager`, `ode`, `runge-kutta` |
| [dvode](https://github.com/jacobwilliams/dvode) — Variable-coefficient multistep ODE solver for stiff and nonstiff systems. | `initial-value-problems`, `multistep-methods`, `ode`, `stiff-equations` | `adams-bashforth`, `fortran`, `fortran-package-manager`, `ode`, `vode` |
| [flint](https://github.com/princemahajan/FLINT) — Adaptive explicit Runge-Kutta ODE integration with dense output and event detection. | `adaptive-methods`, `dense-output`, `event-detection`, `ode`, `runge-kutta` | `differential-equations`, `fortran`, `julia`, `numerical-integration`, `ode`, `ode-events`, `runge-kutta` |
| [odepack](https://github.com/Nicholaswogan/odepack) — Modern thread-safe interfaces to the LSODA and LSODAR initial-value ODE solvers. | `event-detection`, `initial-value-problems`, `ode`, `stiff-equations`, `thread-safe` | `fortran-package-manager`, `ode`, `ode-solver`, `odepack` |
| [rkf45](https://github.com/zoziha/rkf45) — Classic adaptive Runge-Kutta-Fehlberg fourth/fifth-order ODE integration. | `adaptive-methods`, `initial-value-problems`, `ode`, `runge-kutta` | `fehlberg`, `fortran`, `fortran-package-manager`, `fourth-fifth-order`, `ode`, `rkf45`, `runge-kutta` |
| [rklib](https://github.com/jacobwilliams/rklib) — A collection of fixed- and variable-step Runge-Kutta ODE integration methods. | `adaptive-methods`, `initial-value-problems`, `ode`, `runge-kutta` | `differential-equations`, `fortran`, `fortran-package-manager`, `ode`, `ode-solver`, `root-finding`, `runge-kutta`, `runge-kutta-adaptive-step-size`, `runge-kutta-fehlberg` |
| [stiff3](https://github.com/ivan-pi/stiff3) — Adaptive third-order Rosenbrock solver for stiff autonomous ordinary differential equations. | `adaptive-methods`, `ode`, `rosenbrock-methods`, `stiff-equations` | `adaptive`, `differential`, `equation`, `fortran`, `ode`, `solver`, `stiff` |
| [twopnt](https://github.com/perazz/twopnt) — Boundary-value problem solver with adaptive grids and a modern object interface. | `adaptive-grids`, `boundary-value-problems`, `differential-equations` | `boundary-value-problem`, `boundary-value-problems`, `bvp`, `fortran` |

## Differentiation

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [ad_dnsvm](https://github.com/lauvergn/AD_dnSVM) — Forward automatic differentiation of scalars, vectors and matrices through third derivatives. | `arrays`, `automatic-differentiation`, `derivatives`, `differentiation`, `higher-order-derivatives` | `automatic-differentiation`, `fortran` |
| [fordiff](https://github.com/gha3mi/fordiff) — Numerical derivatives using finite differences and complex steps. | `complex-step`, `derivatives`, `differentiation`, `finite-differences` | `complex-step-differentiation`, `derivative`, `differentiation`, `finite-difference`, `fortran`, `fortran-package-manager` |
| [forwarddiff](https://github.com/Nicholaswogan/forwarddiff) — Forward automatic differentiation using dual numbers (Differentia). | `automatic-differentiation`, `derivatives`, `differentiation`, `dual-numbers` | `autodiff`, `autodifferentiation`, `automatic-differentiation`, `differential-equations` |
| [numdiff](https://github.com/jacobwilliams/NumDiff) — Numerical derivatives and sparse Jacobian estimation. | `differentiation`, `finite-differences`, `jacobians`, `sparse-matrices` | `differentiation`, `finite-differences`, `graph-coloring`, `numerical-differentiation`, `numerical-methods`, `optimization`, `sparsity-optimization` |

## Encoding and compression

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [befor64](https://github.com/szaghi/BeFoR64) — Base64 encoding and decoding of text and numerical data. | `base64`, `encoding`, `serialization` | `base64`, `decoding`, `encoding`, `fortran`, `oop` |
| [fortran-zlib](https://github.com/interkosmos/fortran-zlib) — Fortran interfaces to zlib lossless compression and decompression. | `compression`, `language-bindings`, `lossless-compression`, `zlib` | `archiving`, `compression`, `fortran`, `fortran-2018`, `fortran-package-manager`, `zlib` |
| [fortran-zstd](https://github.com/interkosmos/fortran-zstd) — Fortran interfaces to Zstandard lossless data compression. | `compression`, `language-bindings`, `lossless-compression`, `zstandard` | `archiving`, `compression`, `fortran`, `fortran-2018`, `fortran-package-manager`, `zstandard`, `zstd` |
| [fortran_huffman](https://github.com/Euler-37/fortran_huffman) — Huffman coding of byte streams with file compression and decompression. | `compression`, `file-io`, `huffman-coding`, `lossless-compression` | `fortran`, `huffman-compression-algorithm` |

## Error handling

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [ferror](https://github.com/jchristopherson/ferror) — Structured error and warning reporting with configurable handling. | `diagnostics`, `error-handling`, `warnings` | None supplied |

## Expression parsing

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran_function_parser](https://github.com/jacobwilliams/fortran_function_parser) — Parse and evaluate mathematical expressions supplied as strings. | `expression-parsing`, `mathematical-expressions`, `parsing` | `expression-parser`, `fortran`, `function-parser` |
| [m_calculator](https://github.com/urbanjost/M_calculator) — Evaluate mathematical expressions and named variables supplied as text. | `expression-parsing`, `mathematical-expressions`, `parsing` | `expression`, `expression-evaluator`, `fortran`, `fortran-package-manager`, `parse` |

## Files and processes

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [ffilesystem](https://github.com/scivision/ffilesystem) — Portable filesystem and path operations through Fortran, C and C++ interfaces. | `directories`, `file-io`, `filesystem`, `paths`, `portability` | `cpp17`, `filesystem`, `fortran`, `libc`, `path-manipulation` |
| [fmmap](https://github.com/PierUgit/fmmap) — Map files into memory and access their contents as Fortran arrays. | `arrays`, `file-io`, `memory-mapped-files` | `fortran`, `memory-mapped-file` |
| [io-fortran-library](https://github.com/acbbullock/IO-Fortran-Library) — High-level numeric array file I/O, dynamic strings, and numeric/string conversion. | `arrays`, `file-io`, `strings`, `tabular-data`, `type-conversion` | `csv`, `fortran`, `fortran-package-manager`, `input-output`, `modern-fortran` |
| [m_io](https://github.com/urbanjost/M_io) — Convenience routines for reading text files, tables, and paths. | `file-io`, `filesystem`, `paths`, `tabular-data`, `text-files` | `fortran`, `fortran-package-manager`, `io` |
| [popen-fortran](https://github.com/jacobwilliams/popen-fortran) — Capture the text output of a subprocess. | `processes`, `subprocesses`, `text-processing` | `fortran`, `fortran-package-manager`, `popen` |

## Games and puzzles

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [forsudoku](https://github.com/vmagnin/ForSudoku) — Solve Sudoku puzzles and generate new grids with configurable clues. | `constraint-solving`, `puzzles`, `sudoku` | `fortran`, `fortran-package-manager`, `sudoku` |

## General utilities

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fastmath](https://github.com/perazz/fastmath) — Approximate exponential, logarithm and inverse-square-root functions. | `approximate-math`, `elementary-functions`, `exponential-functions`, `logarithms` | `exponential`, `fast-math`, `fortran`, `logarithm`, `rsqrt` |
| [forlab](https://github.com/zoziha/forlab) — MATLAB/NumPy-style numerical utilities, linear algebra, interpolation and statistics. | `interpolation`, `linear-algebra`, `matlab-like`, `numerical-methods`, `statistics` | None supplied |
| [functional-fortran](https://github.com/wavebitscientific/functional-fortran) — Functional array operations including map, filter, fold, and ranges. | `arrays`, `functional-programming`, `map-filter-reduce` | `fortran`, `functional-programming` |
| [kinds](https://github.com/gha3mi/kinds) — Named real and integer kinds with configurable working precision. | `numeric-kinds`, `portability`, `precision` | None supplied |
| [nafpack](https://github.com/Minard-Jules/NAFPack) — Numerical analysis routines for Fourier transforms, linear systems and eigenproblems. | `eigenvalues`, `fourier-transforms`, `linear-systems`, `numerical-methods` | `cmake`, `eigenvalues`, `fft`, `fftw`, `fpm`, `linear-algebra` |
| [stdlib](https://github.com/fortran-lang/stdlib) — General utilities, statistics, strings, sorting, and numerical routines. | `numerical-methods`, `sorting`, `standard-library`, `statistics`, `strings` | `blas`, `fortran`, `fortran-library`, `fortran-package-manager`, `fortran-stdlib`, `hash`, `lapack`, `linear-algebra`, `numerical-methods`, `numpy`, `probability-distribution`, `quadrature`, `rng`, `sorting`, `statistics`, `stdlib`, `strings` |

## Geodesy

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [geodesic-fortran](https://github.com/jacobwilliams/geodesic-fortran) — Distances, bearings and geodetic coordinate transformations on spheres and ellipsoids. | `coordinate-transformations`, `distances`, `ellipsoids`, `geodesics`, `geodesy` | `fortran`, `fortran-package-manager`, `geodesy`, `geodetic-computations`, `vincenty-direct`, `vincenty-formula`, `vincenty-inverse` |
| [maptran3d](https://github.com/geospace-code/maptran3d) — Geographic and Earth-centered Cartesian coordinate transformations. | `cartesian-coordinates`, `coordinate-transformations`, `geodesy`, `geographic-coordinates` | `coordinate-conversions`, `coordinate-transformation`, `fortran2018`, `geodesy`, `modern-fortran` |

## Geometry

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [geompack](https://github.com/jchristopherson/geompack) — Delaunay triangulation of planar point sets. | `delaunay-triangulation`, `geometry`, `meshes`, `point-sets` | `delaunay-triangulation`, `fortran`, `fortran-package-manager`, `geometry`, `triangulation`, `triangulation-delaunay` |

## High precision

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [mpfun2020-var1](https://github.com/jacobwilliams/MPFUN2020-var1) — Thread-safe arbitrary-precision real and complex arithmetic. | `arbitrary-precision`, `complex-arithmetic`, `precision`, `real-arithmetic`, `thread-safe` | `arbitrary-precision` |

## Images

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [cairo-fortran](https://github.com/vmagnin/cairo-fortran) — Cairo bindings for drawing vector graphics into PNG and other output formats. | `drawing`, `images`, `language-bindings`, `png`, `vector-graphics` | `bindings`, `cairo`, `fortran`, `fortran-package-manager` |
| [forimage](https://github.com/gha3mi/forimage) — Create, read, write and transform PNM images and convert color representations. | `color-conversion`, `file-io`, `image-processing`, `images`, `pnm` | `color`, `decimal`, `fortran`, `fortran-package-manager`, `hexadecimal`, `hsl`, `hsv`, `image`, `pbm`, `pgm`, `pnm`, `ppm`, `rgb` |
| [fortran_stb_image](https://github.com/lewisfish/fortran_stb_image) — Read and write PNG and other raster image formats through the stb libraries. | `file-io`, `image-io`, `images`, `language-bindings`, `png` | None supplied |

## Integration

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [dcuhre](https://github.com/Zaneham/dcuhre) — Adaptive multidimensional integration over hyperrectangles with vector integrands and error estimates. | `adaptive-methods`, `cubature`, `error-estimation`, `multidimensional`, `quadrature` | `dcuhre`, `fortran`, `fortran-package-manager`, `integration`, `mathematics`, `multidimensional-integration`, `numerical-integration`, `quadrature` |
| [fortran_cubatures](https://github.com/willklausler/fortran_cubatures) — Gaussian cubature rules for finite-element reference lines, triangles, quadrilaterals, tetrahedra, hexahedra and wedges. | `cubature`, `finite-elements`, `gaussian-quadrature`, `multidimensional`, `quadrature` | `cubature`, `finite-elements`, `fortran`, `fpm`, `numerical-integration`, `quadrature` |
| [gaussjacobiquad](https://github.com/HaoZeke/GaussJacobiQuad) — Gauss-Jacobi quadrature nodes and weights for weighted numerical integration. | `gauss-jacobi`, `gaussian-quadrature`, `quadrature`, `weighted-integrals` | `f2py`, `gauss-jacobi`, `meson`, `numerical-integration`, `quadrature` |
| [integrate_fortran](https://github.com/Euler-37/integrate_fortran) — Gauss-Legendre quadrature for one-dimensional and multidimensional integrals. | `gauss-legendre`, `gaussian-quadrature`, `multidimensional`, `quadrature` | `gauss-legendre-integration`, `numerical-integration`, `quadrature` |
| [quadpack](https://github.com/jacobwilliams/quadpack) — Adaptive numerical integration, including improper and oscillatory integrals. | `adaptive-methods`, `improper-integrals`, `oscillatory-integrals`, `quadrature` | `fortran`, `fortran-package-manager`, `gauss-kronrod`, `gauss-kronrod-quadrature`, `numerical-integration`, `quadpack`, `quadrature`, `quadrature-integration`, `slatec` |
| [quadrature-fortran](https://github.com/jacobwilliams/quadrature-fortran) — Adaptive Gaussian quadrature in one or more dimensions. | `adaptive-methods`, `gaussian-quadrature`, `multidimensional`, `quadrature` | `fortran`, `fortran-package-manager`, `integration`, `numerical-integration`, `quadrature`, `quadrature-integration` |

## Interpolation

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [bspline-fortran](https://github.com/jacobwilliams/bspline-fortran) — One- to six-dimensional B-spline interpolation. | `b-splines`, `interpolation`, `multidimensional`, `splines` | `b-spline`, `extrapolation`, `fortran`, `fortran-package-manager`, `interpolation`, `least-squares-curve-fitting`, `quadrature-integration`, `splines` |
| [finterp](https://github.com/jacobwilliams/finterp) — Multidimensional linear and nearest-neighbor interpolation. | `grids`, `interpolation`, `multidimensional`, `nearest-neighbors` | `fortran`, `fortran-package-manager`, `interpolation`, `linear-interpolation`, `nearest-neighbor-interpolation` |
| [fitpack](https://github.com/perazz/fitpack) — Spline fitting, smoothing, derivatives, and integration of curves and surfaces. | `curve-fitting`, `derivatives`, `interpolation`, `smoothing`, `splines` | `curve-fitting`, `fortran`, `smoothing`, `smoothing-splines`, `spline-approximation`, `spline-curve`, `spline-interpolation`, `splines`, `surface-fitting` |
| [interpolation](https://github.com/furstj/interpolation) — Linear and shape-preserving piecewise cubic interpolation for tabulated data. | `interpolation`, `shape-preserving`, `splines`, `tabulated-data` | `fortran`, `interpolation` |
| [pchip](https://github.com/jacobwilliams/PCHIP) — Shape-preserving piecewise cubic interpolation. | `interpolation`, `shape-preserving`, `splines`, `tabulated-data` | `fortran`, `fortran-package-manager`, `hermite-interpolation`, `interpolation`, `slatec` |
| [regridpack](https://github.com/jacobwilliams/regridpack) — Linear and cubic interpolation between one- to four-dimensional grids. | `grids`, `interpolation`, `multidimensional`, `tabulated-data` | `fortran`, `fortran-package-manager`, `interpolation`, `linear-interpolation`, `regridding`, `spline-interpolation` |
| [splpak](https://github.com/jacobwilliams/splpak) — Least-squares fitting and evaluation of multidimensional cubic splines. | `curve-fitting`, `least-squares`, `multidimensional`, `splines` | `cubic-splines`, `curve-fitting`, `fortran`, `fortran-package-manager`, `interpolation`, `least-squares`, `splines` |

## Linear algebra

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [blas-interface](https://github.com/awvwgk/blas-interface) — Explicit generic Fortran interfaces to BLAS vector and matrix operations. | `blas`, `language-bindings`, `linear-algebra`, `matrix-operations`, `vector-operations` | None supplied |
| [foreig](https://github.com/gha3mi/foreig) — LAPACK interfaces for eigenvalues and eigenvectors of real matrices. | `eigenvalues`, `eigenvectors`, `lapack`, `linear-algebra` | `eig`, `eigenvalues`, `eigenvalues-and-eigenvectors`, `eigenvectors`, `fortran`, `fortran-package-manager`, `lapack`, `mkl` |
| [forinv](https://github.com/gha3mi/forinv) — Matrix inverses and singular-value-decomposition pseudoinverses. | `linear-algebra`, `matrix-inverse`, `pseudoinverse`, `svd` | `fortran`, `fortran-package-manager`, `inverse`, `pseudoinverse`, `svd` |
| [fortran-lapack](https://github.com/perazz/fortran-lapack) — Modern linear algebra: linear systems, eigenvalues, least squares, and matrix factorizations. | `eigenvalues`, `lapack`, `least-squares`, `linear-algebra`, `linear-systems`, `matrix-factorization` | `blas`, `eigenvalues`, `eigenvectors`, `fortran`, `fortran-package-manager`, `lapack`, `lapack95`, `lapacke`, `linear-algebra`, `linear-equations`, `machine-learning`, `matrix-factorization`, `modern-fortran`, `modern-fortran-modules`, `numpy`, `singular-values`, `svd` |
| [fsparse](https://github.com/jalvesz/FSPARSE) — Sparse matrix storage, format conversions and matrix-vector products. | `format-conversion`, `linear-algebra`, `matrix-vector-products`, `sparse-matrices` | `fortran`, `fortran-library`, `fortran-package-manager`, `sparse-matrices` |
| [kiss](https://github.com/ivan-pi/kiss) — Krylov iterative solvers for dense matrices and matrix-free linear operators. | `iterative-solvers`, `krylov-methods`, `linear-algebra`, `linear-systems`, `matrix-free` | None supplied |
| [lightkrylov](https://github.com/nekStab/LightKrylov) — Krylov methods for eigenvalues, linear systems, singular values and matrix exponentials. | `eigenvalues`, `krylov-methods`, `linear-algebra`, `linear-systems`, `matrix-exponentials`, `svd` | None supplied |
| [linalg](https://github.com/jchristopherson/linalg) — Convenient dense and sparse linear algebra interfaces to BLAS, LAPACK and ARPACK. | `arpack`, `blas`, `lapack`, `linear-algebra`, `sparse-matrices` | `blas`, `cholesky-decomposition`, `compressed-row-storage`, `compressed-sparse-row`, `eigenvalues`, `eigenvectors`, `fortran`, `lapack`, `linear-algebra`, `lu-decomposition`, `qr-decomposition`, `singular-value-decomposition`, `sparse-matrix` |
| [lsmr](https://github.com/jacobwilliams/LSMR) — Iterative solution of sparse linear equations and least-squares problems. | `iterative-solvers`, `least-squares`, `linear-algebra`, `linear-systems`, `sparse-matrices` | `fortran`, `fortran-package-manager`, `least-squares`, `linear-algebra`, `linear-equations`, `lsmr`, `sparse-linear-systems` |
| [lsqr](https://github.com/jacobwilliams/LSQR) — Iterative sparse linear systems and least-squares solver using coordinate storage. | `iterative-solvers`, `least-squares`, `linear-algebra`, `linear-systems`, `sparse-matrices` | `conjugate-gradient`, `fortran`, `fortran-package-manager`, `least-squares`, `linear-algebra`, `linear-equations`, `lsqr` |
| [minres](https://github.com/willdickson/minres) — Iterative solution of symmetric sparse systems, including indefinite matrices. | `iterative-solvers`, `linear-algebra`, `linear-systems`, `sparse-matrices`, `symmetric-systems` | None supplied |
| [sparse_fortran](https://github.com/Euler-37/sparse_fortran) — Coordinate and compressed-row sparse matrices with matrix-vector products. | `coordinate-storage`, `csr-storage`, `linear-algebra`, `matrix-vector-products`, `sparse-matrices` | None supplied |
| [specialmatrices](https://github.com/loiseaujc/SpecialMatrices) — Structured diagonal, circulant, Toeplitz, tridiagonal, and other matrices. | `circulant-matrices`, `linear-algebra`, `structured-matrices`, `toeplitz-matrices`, `tridiagonal-matrices` | `linear-algebra`, `sparse-linear-systems`, `sparse-matrix` |
| [y12m](https://github.com/ivan-pi/y12m) — Direct sparse LU factorization with pivoting, reordering and reuse for multiple right-hand sides. | `direct-solvers`, `linear-algebra`, `linear-systems`, `lu-factorization`, `sparse-matrices` | None supplied |

## Machine learning

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran-flann](https://github.com/ivan-pi/fortran-flann) — FLANN interfaces for nearest-neighbor searches and spatial indexing. | `language-bindings`, `machine-learning`, `nearest-neighbors`, `spatial-indexing` | `approximate-nearest-neighbor-search`, `hierarchical-clustering`, `high-dimensional-data`, `kdtree`, `kmeans-clustering`, `nearest-neighbor-search`, `spatial-search` |
| [neural-fortran](https://github.com/modern-fortran/neural-fortran) — Neural networks with dense and convolutional layers and gradient-based training. | `convolutional-networks`, `gradient-based-optimization`, `machine-learning`, `neural-networks` | `cnn`, `deep-learning`, `fortran`, `machine-learning`, `neural-network`, `parallel` |

## Number theory

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran-primes](https://github.com/perazz/fortran-primes) — Generate prime numbers, test primality, and factor integers. | `integer-factorization`, `number-theory`, `prime-numbers` | `factorization`, `fortran`, `fortran-package-manager`, `modern-fortran`, `prime-numbers`, `primes` |
| [rational_number](https://github.com/art-rasa/rational_number) — Exact rational arithmetic with integer numerators and denominators. | `exact-arithmetic`, `number-theory`, `rational-arithmetic` | None supplied |

## Physical constants

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [codata](https://github.com/MilanSkocic/codata) — CODATA physical constants and uncertainties for several published adjustments. | `physical-constants`, `physics`, `uncertainty` | `c`, `codata`, `fortran-language`, `fortran-library`, `fortran-package-manager`, `python`, `science` |

## Physical properties

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [ciaaw](https://github.com/MilanSkocic/ciaaw) — Standard atomic weights, isotopic abundances and nuclide masses for chemistry. | `atomic-weights`, `chemistry`, `isotopes`, `physical-properties` | `chemistry`, `fortran`, `fortran-package-manager`, `isotopes`, `standard-atomic-masses` |
| [iapws](https://github.com/MilanSkocic/iapws) — IAPWS thermodynamic properties of water, including saturation pressure and temperature. | `iapws`, `physical-properties`, `thermodynamics`, `water` | `fortran-language`, `fortran-library`, `fortran-package-manager`, `iapws`, `science`, `water` |

## Plotting

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [pyplot-fortran](https://github.com/jacobwilliams/pyplot-fortran) — Create PNG plots from Fortran through Python and Matplotlib. | `matplotlib`, `plotting`, `png`, `python`, `visualization` | `contour-plot`, `fortran`, `fortran-package-manager`, `matplotlib`, `plot`, `plotting`, `plotting-in-fortran`, `pyplot` |

## Random numbers

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [mersenne-twister-fortran](https://github.com/jacobwilliams/mersenne-twister-fortran) — Reproducible 64-bit Mersenne Twister random number generation. | `mersenne-twister`, `pseudorandom`, `random-numbers`, `reproducibility` | `fortran`, `fortran-package-manager`, `mersenne-twister`, `random-number-generators`, `rng` |
| [pointsets](https://github.com/arjenmarkus/pointsets) — Construct uniform, geometric, random and quasi-random point sets and multidimensional grids. | `grids`, `multidimensional`, `point-sets`, `quasi-random`, `random-numbers` | None supplied |
| [rndgen-fortran](https://github.com/wcota/rndgen-fortran) — Seeded KISS random number generators with multiple independent states and replay. | `kiss-generator`, `pseudorandom`, `random-numbers`, `reproducibility` | `fortran`, `fortran-package-manager`, `fpm`, `kiss-rng`, `random`, `random-number-generator`, `rng` |
| [rngff](https://github.com/Archaeologic-Inc/rngff) — A common object-oriented interface to pseudorandom number generators. | `pseudorandom`, `random-numbers`, `reproducibility` | `random`, `random-number-generator`, `rng` |

## Roots and optimization

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [conmax](https://github.com/jacobwilliams/conmax) — Linear, quadratic and constrained minimax optimization routines. | `constrained-optimization`, `linear-programming`, `minimax`, `optimization`, `quadratic-programming` | `conmax`, `constrained-optimization`, `fortran`, `fortran-package-manager`, `nonlinear-optimization`, `numerical-optimization`, `optimization` |
| [conmin](https://github.com/jacobwilliams/conmin) — Constrained nonlinear minimization using feasible directions and reverse communication. | `constrained-optimization`, `nonlinear-optimization`, `optimization`, `reverse-communication` | `conmin`, `constrained-optimization`, `fortran`, `fortran-package-manager`, `numerical-optimization`, `optimization` |
| [fmin](https://github.com/jacobwilliams/fmin) — Derivative-free minimization of a scalar function on an interval. | `derivative-free`, `minimization`, `optimization`, `scalar-functions` | `brent`, `fortran-package-manager`, `minimization` |
| [forsolver](https://github.com/gha3mi/forsolver) — Linear solvers and Newton-type nonlinear solvers with analytic, finite-difference and complex-step derivatives. | `complex-step`, `finite-differences`, `linear-systems`, `newton-methods`, `nonlinear-equations` | `complex-step-differentiation`, `finite-difference-method`, `fortran`, `fortran-package-manager`, `linear-system-solver`, `newton-method`, `newton-raphson`, `nonlinear-systems`, `quasi-newton-method`, `solver` |
| [fortimize](https://github.com/fedebenelli/ForTimize) — A common interface to optimization algorithms including Nelder-Mead and gradient descent. | `derivative-free`, `gradient-descent`, `nelder-mead`, `optimization` | `fortran`, `fortran-`, `gradient-descent`, `nelder-mead`, `optimization`, `optimization-algorithms` |
| [lbfgsb](https://github.com/jacobwilliams/lbfgsb) — Limited-memory quasi-Newton optimization with variable bounds. | `bound-constraints`, `limited-memory`, `optimization`, `quasi-newton` | `bfgs`, `bfgs-algorithm`, `constrained-optimization`, `fortran`, `fortran-package-manager`, `lbfgsb`, `lbfgsb-solver`, `numerical-optimization` |
| [libdogleg-f](https://github.com/ivan-pi/libdogleg-f) — Fortran interfaces to libdogleg trust-region nonlinear least-squares optimization. | `language-bindings`, `least-squares`, `optimization`, `trust-region` | `c`, `dogleg-method`, `fortran`, `nonlinear-least-squares`, `numerical-optimization` |
| [minpack](https://github.com/jacobwilliams/minpack) — Nonlinear equation solvers and nonlinear least-squares fitting. | `curve-fitting`, `least-squares`, `nonlinear-equations`, `optimization` | None supplied |
| [nlesolver-fortran](https://github.com/jacobwilliams/nlesolver-fortran) — Newton and quasi-Newton solvers for dense or sparse nonlinear equation systems. | `newton-methods`, `nonlinear-equations`, `quasi-newton`, `sparse-matrices` | `broyden-method`, `differential-correction-algorithm`, `fortran`, `fortran-package-manager`, `lsmr`, `lsqr`, `lusol`, `minimum-norm`, `newton-raphson`, `nonlinear-equation-solver`, `nonlinear-equations`, `quasi-newton` |
| [nlopt-f](https://github.com/awvwgk/nlopt-f) — Modern Fortran bindings to NLopt nonlinear optimization algorithms. | `language-bindings`, `nlopt`, `nonlinear-optimization`, `optimization` | None supplied |
| [nonlin](https://github.com/jchristopherson/nonlin) — Object-oriented solvers for nonlinear equations, least squares and optimization. | `least-squares`, `nonlinear-equations`, `optimization`, `root-finding` | `bfgs`, `fortran`, `least-squares`, `levenberg-marquardt`, `nelder-mead`, `newton-raphson-multivariable`, `newtons-method`, `nonlinear-equations`, `optimization`, `polynomials`, `quasi-newton` |
| [optgra](https://github.com/jacobwilliams/optgra) — Constrained optimization designed for nearly linear problems with many constraints. | `constrained-optimization`, `nearly-linear-problems`, `optimization` | `constrained-optimization`, `fortran`, `fortran-package-manager`, `numerical-optimization`, `optimization` |
| [opti](https://github.com/Konrad1991/opti) — Particle swarm optimization with star and adaptive neighborhood topologies. | `global-optimization`, `optimization`, `particle-swarm`, `stochastic-methods` | `numerical-optimization`, `particle-swarm-optimization`, `pso`, `pso-algorithm`, `swarm-intelligence`, `topology` |
| [pikaia](https://github.com/jacobwilliams/pikaia) — Genetic algorithm for global optimization with reproducible random seeds. | `genetic-algorithms`, `global-optimization`, `optimization`, `reproducibility`, `stochastic-methods` | `fortran`, `fortran-package-manager`, `genetic-algorithm`, `numerical-optimization`, `optimization`, `pikaia` |
| [polyroots-fortran](https://github.com/jacobwilliams/polyroots-fortran) — Find all real and complex roots of polynomial equations using several numerical algorithms. | `complex-arithmetic`, `polynomials`, `root-finding` | `companion-matrix`, `eigenvalues`, `fortran`, `fortran-package-manager`, `jenkins-traub`, `laguerre-method`, `nonlinear-equations`, `polynomial-equations`, `polynomial-roots`, `polynomials`, `root-finding` |
| [powellopt](https://github.com/jacobwilliams/PowellOpt) — Powell derivative-free optimization methods including BOBYQA and COBYLA. | `bound-constraints`, `constrained-optimization`, `derivative-free`, `optimization` | `constrained-optimization`, `fortran`, `fortran-package-manager`, `nonlinear-optimization`, `numerical-optimization`, `optimization`, `unconstrained-optimization` |
| [psqp](https://github.com/jacobwilliams/psqp) — Sequential quadratic programming with variable bounds and general nonlinear constraints. | `bound-constraints`, `constrained-optimization`, `optimization`, `sequential-quadratic-programming` | `fortran`, `fortran-package-manager`, `nonlinear-optimization`, `numerical-optimization`, `optimization`, `sqp` |
| [roots-fortran](https://github.com/jacobwilliams/roots-fortran) — Find roots of scalar functions using bracketing and other solvers. | `nonlinear-equations`, `root-finding`, `scalar-functions` | `bisection`, `brent-dekker`, `fortran`, `fortran-package-manager`, `muller`, `muller-s-method`, `regula-falsi`, `root-finding`, `zeroin` |
| [simulated-annealing](https://github.com/jacobwilliams/simulated-annealing) — Stochastic global optimization by simulated annealing with bounds and reproducible seeds. | `bound-constraints`, `global-optimization`, `optimization`, `simulated-annealing`, `stochastic-methods` | `annealing`, `basin-hopping`, `fortran`, `fortran-package-manager`, `minimization`, `optimization`, `python`, `simulated-annealing`, `stochastic-optimization` |
| [slsqp](https://github.com/jacobwilliams/slsqp) — Sequential least-squares optimization with bounds and nonlinear constraints. | `bound-constraints`, `constrained-optimization`, `optimization`, `sequential-quadratic-programming` | `constrained-optimization`, `fortran`, `fortran-package-manager`, `nnls`, `numerical-optimization`, `optimization`, `sqp` |

## Signal processing

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fastconv](https://github.com/gronki/fastconv) — Small-kernel convolution for smoothing one-, two- and three-dimensional arrays. | `arrays`, `convolution`, `multidimensional`, `signal-processing`, `smoothing` | None supplied |
| [peaks](https://github.com/jchristopherson/peaks) — Detect local maxima and minima in sampled signals using a noise threshold. | `peak-detection`, `sampled-data`, `signal-processing` | `fortran`, `peak-detection`, `signal-analysis` |
| [spectrum](https://github.com/jchristopherson/spectrum) — Filtering, spectral estimation, convolution, resampling, and signal analysis. | `convolution`, `filtering`, `resampling`, `signal-processing`, `spectral-analysis` | `cross-spectral-density`, `filter`, `filtering`, `fir-filter`, `fortran`, `gaussian-filter`, `iir-filters`, `numerical-differentiation`, `periodogram`, `power-spectral-density`, `psd`, `total-variation-filter`, `total-variation-regularization`, `transfer-function` |

## Special functions

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [specfun](https://github.com/jacobwilliams/specfun) — Special functions including Bessel, Airy, gamma, and related functions. | `airy-functions`, `bessel-functions`, `gamma-functions`, `special-functions` | `fortran`, `fortran-package-manager`, `scipy`, `special-functions` |
| [specfunc-fullerton](https://github.com/arjenmarkus/specfunc-fullerton) — Fullerton special functions including gamma, Bessel, Airy and exponential integrals. | `airy-functions`, `bessel-functions`, `exponential-integrals`, `gamma-functions`, `special-functions` | `special-functions` |

## Statistics

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fjsample](https://github.com/RJaBi/FJsample) — Jackknife and bootstrap resampling, bias estimates and statistical uncertainties. | `bootstrap`, `jackknife`, `resampling`, `statistics`, `uncertainty` | `bootstrap-resampling`, `fortran`, `fortran-package-manager`, `jackknife-resampling`, `meson-python` |
| [forpca](https://github.com/gha3mi/forpca) — Principal component directions from eigendecomposition or singular value decomposition. | `dimensionality-reduction`, `eigenvalues`, `principal-component-analysis`, `statistics`, `svd` | `fortran`, `fortran-package-manager`, `pca`, `principal-component-analysis` |
| [fortsa](https://github.com/zoziha/fortsa) — Time-series autocorrelations, partial correlations and ARIMA modeling through CTSA. | `arima`, `autocorrelation`, `statistics`, `time-series` | `arima`, `arma`, `bindings`, `fortran`, `fpm`, `time-series`, `time-series-analysis`, `tsa` |
| [fstats](https://github.com/jchristopherson/fstats) — Probability distributions, statistical tests, regression, bootstrap sampling, and MCMC. | `bootstrap`, `hypothesis-testing`, `mcmc`, `probability-distributions`, `regression`, `statistics` | `allan-variance`, `anova`, `bootstrap`, `design-of-experiments`, `distributions`, `experimental-design`, `gauge-r-and-r-study`, `hypothesis-testing`, `interpolation`, `levenberg-marquardt`, `lowess`, `markov-chain-monte-carlo`, `mcmc-sampler`, `missing-data`, `regression`, `sampling-distribution`, `special-functions`, `statistical-testing`, `statistics` |
| [lib_statistics](https://github.com/sebastiandyrda/lib_statistics) — Logistic regression using iteratively reweighted least squares. | `least-squares`, `logistic-regression`, `regression`, `statistics` | None supplied |
| [odrpack95](https://github.com/HugoMVale/odrpack95) — Orthogonal distance regression with errors in both variables and optional parameter bounds. | `bound-constraints`, `errors-in-variables`, `least-squares`, `regression`, `statistics` | `fortran`, `fpm`, `mathematics`, `odr`, `regression`, `statistics` |

## Strings

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran-pcre2](https://github.com/interkosmos/fortran-pcre2) — Perl-compatible regular expressions, capture groups and text matching through PCRE2. | `language-bindings`, `pattern-matching`, `pcre2`, `regular-expressions`, `text-processing` | `fortran`, `fortran-2018`, `fortran-package-manager`, `fpm`, `pcre`, `pcre2`, `regex`, `regexp` |
| [fortran-string-to-real](https://github.com/Carltoffel/Fortran-String-to-Real) — Experimental conversion of valid decimal and scientific-notation strings to real numbers. | `floating-point`, `number-parsing`, `strings`, `type-conversion` | None supplied |
| [iso_varying_string](https://github.com/everythingfunctional/iso_varying_string) — Variable-length strings implementing the ISO varying-string specification. | `strings`, `text-processing`, `variable-length-strings` | `fortran`, `iso`, `strings` |
| [ryu_fortran](https://github.com/St-Maxwell/ryu_fortran) — Ryu conversion of floating-point numbers to short decimal representations. | `floating-point`, `number-formatting`, `strings`, `type-conversion` | `floating-point`, `string` |
| [strff](https://github.com/everythingfunctional/strff) — String splitting, joining, formatting and conversion from intrinsic types. | `formatting`, `strings`, `text-processing`, `type-conversion` | `fortran`, `string-manipulation` |
| [utf8-f](https://github.com/St-Maxwell/utf8-f) — UTF-8 character counting, indexing, slicing and text manipulation. | `strings`, `text-processing`, `unicode`, `utf-8` | `fortran`, `utf-8` |

## Strings and sorting

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran-search-and-sort](https://github.com/jacobwilliams/fortran-search-and-sort) — Generic sorting, searching, and duplicate removal for arrays. | `arrays`, `searching`, `sorting`, `unique-values` | `binary-search`, `fortran`, `quicksort`, `searching-algorithms`, `sorting-algorithms` |
| [m_sort](https://github.com/urbanjost/M_sort) — Shell sort, heapsort, quicksort, and related sorting utilities. | `arrays`, `heapsort`, `quicksort`, `sorting` | `fortran`, `fortran-package-manager`, `fpm`, `sort`, `sorting`, `sorting-algorithms` |
| [m_strings](https://github.com/urbanjost/M_strings) — String manipulation, case conversion, tokenization, and formatting. | `formatting`, `strings`, `text-processing`, `tokenization` | `fortran`, `fortran-package-manager`, `fpm`, `string-manipulation`, `strings` |
| [orderpack](https://github.com/urbanjost/orderpack) — Sorting, ranking, medians, and partial ordering of arrays. | `arrays`, `medians`, `order-statistics`, `ranking`, `sorting` | `fortran`, `fortran-package-manager`, `fpm`, `sort` |
| [stringsort](https://github.com/jacobwilliams/stringsort) — Lexical and natural sorting of character arrays. | `natural-sort`, `sorting`, `strings` | `fortran`, `fortran-package-manager`, `quicksort`, `sorting-algorithms` |

## Testing

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran_test_helper](https://github.com/jchristopherson/fortran_test_helper) — Assertions and random array generators for numerical tests. | `assertions`, `numerical-testing`, `random-numbers`, `unit-testing` | None supplied |
| [m_framework](https://github.com/urbanjost/M_framework) — Unit testing, floating-point comparisons, and diagnostic formatting. | `assertions`, `diagnostics`, `floating-point`, `numerical-testing`, `unit-testing` | `fortran`, `fortran-package-manager`, `fpm`, `unit-testing` |
| [test-drive](https://github.com/fortran-lang/test-drive) — Lightweight unit testing with named tests and assertions. | `assertions`, `unit-testing` | `fortran-library`, `fortran-package-manager`, `testing-framework`, `unit-testing` |

## Text parsing

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [forgex](https://github.com/ShinobuAmasaki/forgex) — Regular expressions with Unicode support and full or substring matching. | `pattern-matching`, `regular-expressions`, `text-processing`, `unicode` | `fortran`, `fortran-package-manager`, `regex`, `regular-expression` |
| [fortran-regex](https://github.com/perazz/fortran-regex) — Search text with a lightweight regular expression engine. | `pattern-matching`, `regular-expressions`, `text-processing` | `fortran`, `regex`, `regex-parser`, `regular-expression`, `regular-expressions` |
| [fortran-shlex](https://github.com/perazz/fortran-shlex) — Split command strings into tokens while respecting quotes. | `command-line`, `parsing`, `quoting`, `tokenization` | `fortran`, `posix`, `regular-expressions`, `shlex`, `shlex-library` |
| [m_match](https://github.com/urbanjost/M_match) — Pattern matching with a compact grep-style regular expression syntax. | `pattern-matching`, `regular-expressions`, `text-processing` | `bre`, `fortran`, `fortran-package-manager`, `regex`, `regular-expressions` |
| [parff](https://github.com/everythingfunctional/parff) — Composable functional parsers for structured text and useful parse errors. | `functional-programming`, `parser-combinators`, `parsing`, `text-processing` | `fortran`, `parser`, `parser-combinators`, `parser-library` |

## Transforms

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fftpack](https://github.com/fortran-lang/fftpack) — Fast Fourier, sine, and cosine transforms. | `cosine-transforms`, `fft`, `fourier-transforms`, `sine-transforms` | `fast-fourier-transform`, `fft`, `fft-library`, `fftpack`, `fortran-library`, `fortran-package-manager` |
| [kissfft-f](https://github.com/zoziha/kissfft-f) — Fortran bindings to the compact KISS FFT library for fast Fourier transforms. | `fft`, `fourier-transforms`, `language-bindings`, `signal-processing` | `fft`, `fortran`, `fortran-package-manager`, `kissfft`, `mesonbuild`, `modern-fortran`, `oop`, `wrapper-api` |

## Units and quantities

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [quaff](https://github.com/everythingfunctional/quaff) — Physical quantities with type-safe arithmetic and automatic unit conversions. | `dimensional-analysis`, `physical-units`, `type-safety`, `unit-conversion` | `fortran`, `units-of-measure` |

## Playground topic index

Counts below refer only to our topics; GitHub-only labels are not included.

| Topic | Packages |
| --- | --- |
| `adams-methods` | 1 |
| `adaptive-grids` | 1 |
| `adaptive-methods` | 10 |
| `adjacency-structures` | 1 |
| `airy-functions` | 2 |
| `approximate-math` | 1 |
| `arbitrary-precision` | 1 |
| `argument-parsing` | 2 |
| `arima` | 1 |
| `arpack` | 1 |
| `arrays` | 11 |
| `assertions` | 3 |
| `astrodynamics` | 1 |
| `astronomy` | 1 |
| `atomic-weights` | 1 |
| `autocorrelation` | 1 |
| `automatic-differentiation` | 2 |
| `b-splines` | 1 |
| `base64` | 1 |
| `bessel-functions` | 2 |
| `binary-data` | 1 |
| `blas` | 2 |
| `bootstrap` | 2 |
| `bound-constraints` | 6 |
| `boundary-value-problems` | 1 |
| `calendar-arithmetic` | 2 |
| `cartesian-coordinates` | 1 |
| `chemistry` | 1 |
| `circulant-matrices` | 1 |
| `color-conversion` | 2 |
| `colormaps` | 1 |
| `colors` | 2 |
| `command-line` | 4 |
| `complex-arithmetic` | 2 |
| `complex-step` | 2 |
| `compression` | 3 |
| `configuration` | 3 |
| `constrained-optimization` | 6 |
| `constraint-solving` | 1 |
| `containers` | 5 |
| `convolution` | 2 |
| `convolutional-networks` | 1 |
| `coordinate-storage` | 1 |
| `coordinate-transformations` | 4 |
| `cosine-transforms` | 1 |
| `csr-storage` | 1 |
| `csv` | 1 |
| `cubature` | 2 |
| `curve-fitting` | 3 |
| `dae` | 2 |
| `databases` | 1 |
| `date-time` | 2 |
| `defaults` | 1 |
| `delaunay-triangulation` | 1 |
| `dense-output` | 1 |
| `dependency-ordering` | 1 |
| `derivative-free` | 3 |
| `derivatives` | 4 |
| `diagnostics` | 2 |
| `dictionaries` | 3 |
| `differential-equations` | 3 |
| `differentiation` | 4 |
| `dimensional-analysis` | 1 |
| `dimensionality-reduction` | 1 |
| `direct-solvers` | 1 |
| `directed-acyclic-graphs` | 1 |
| `directories` | 1 |
| `distances` | 1 |
| `drawing` | 1 |
| `dual-numbers` | 1 |
| `durations` | 1 |
| `dynamic-arrays` | 1 |
| `eigenvalues` | 5 |
| `eigenvectors` | 1 |
| `elementary-functions` | 1 |
| `ellipsoids` | 1 |
| `encoding` | 1 |
| `error-estimation` | 1 |
| `error-handling` | 1 |
| `errors-in-variables` | 1 |
| `event-detection` | 3 |
| `exact-arithmetic` | 1 |
| `exponential-functions` | 1 |
| `exponential-integrals` | 1 |
| `expression-parsing` | 2 |
| `fft` | 2 |
| `file-io` | 12 |
| `filesystem` | 2 |
| `filtering` | 1 |
| `finite-differences` | 3 |
| `finite-elements` | 1 |
| `floating-point` | 3 |
| `format-conversion` | 1 |
| `formatting` | 3 |
| `fourier-transforms` | 3 |
| `functional-programming` | 2 |
| `gamma-functions` | 2 |
| `gauss-jacobi` | 1 |
| `gauss-legendre` | 1 |
| `gaussian-quadrature` | 4 |
| `genetic-algorithms` | 1 |
| `geodesics` | 1 |
| `geodesy` | 2 |
| `geographic-coordinates` | 1 |
| `geometry` | 1 |
| `global-optimization` | 3 |
| `gradient-based-optimization` | 1 |
| `gradient-descent` | 1 |
| `graph-partitioning` | 1 |
| `graphs` | 3 |
| `grids` | 3 |
| `hash-tables` | 1 |
| `hdf5` | 1 |
| `heapsort` | 1 |
| `help-text` | 1 |
| `higher-order-derivatives` | 1 |
| `hls` | 1 |
| `hsv` | 1 |
| `huffman-coding` | 1 |
| `hypothesis-testing` | 1 |
| `iapws` | 1 |
| `iau-sofa` | 1 |
| `image-io` | 1 |
| `image-processing` | 1 |
| `images` | 3 |
| `implicit-methods` | 1 |
| `improper-integrals` | 1 |
| `initial-value-problems` | 6 |
| `input-parameters` | 1 |
| `integer-factorization` | 1 |
| `interpolation` | 7 |
| `isotopes` | 1 |
| `iterative-solvers` | 5 |
| `jackknife` | 1 |
| `jacobians` | 1 |
| `json` | 2 |
| `julian-dates` | 1 |
| `kiss-generator` | 1 |
| `krylov-methods` | 3 |
| `language-bindings` | 12 |
| `lapack` | 3 |
| `least-squares` | 9 |
| `limited-memory` | 1 |
| `linear-algebra` | 15 |
| `linear-programming` | 1 |
| `linear-systems` | 9 |
| `linked-lists` | 2 |
| `logarithms` | 1 |
| `logistic-regression` | 1 |
| `lossless-compression` | 3 |
| `lu-factorization` | 1 |
| `machine-learning` | 2 |
| `map-filter-reduce` | 1 |
| `mathematical-expressions` | 2 |
| `matlab-like` | 1 |
| `matplotlib` | 1 |
| `matrix-exponentials` | 1 |
| `matrix-factorization` | 1 |
| `matrix-free` | 1 |
| `matrix-inverse` | 1 |
| `matrix-operations` | 1 |
| `matrix-ordering` | 1 |
| `matrix-vector-products` | 2 |
| `mcmc` | 1 |
| `medians` | 1 |
| `memory-mapped-files` | 1 |
| `mersenne-twister` | 1 |
| `meshes` | 1 |
| `messagepack` | 1 |
| `metadata` | 2 |
| `minimax` | 1 |
| `minimization` | 1 |
| `multidimensional` | 10 |
| `multistep-methods` | 1 |
| `natural-sort` | 1 |
| `nearest-neighbors` | 2 |
| `nearly-linear-problems` | 1 |
| `nelder-mead` | 1 |
| `netcdf` | 1 |
| `neural-networks` | 1 |
| `newton-methods` | 2 |
| `nlopt` | 1 |
| `nonlinear-equations` | 5 |
| `nonlinear-optimization` | 2 |
| `number-formatting` | 1 |
| `number-parsing` | 1 |
| `number-theory` | 2 |
| `numeric-kinds` | 1 |
| `numerical-methods` | 3 |
| `numerical-testing` | 2 |
| `ode` | 9 |
| `optimization` | 16 |
| `orbital-mechanics` | 1 |
| `order-statistics` | 1 |
| `oscillatory-integrals` | 1 |
| `parser-combinators` | 1 |
| `parsing` | 7 |
| `particle-swarm` | 1 |
| `paths` | 2 |
| `pattern-matching` | 4 |
| `pcre2` | 1 |
| `peak-detection` | 1 |
| `physical-constants` | 1 |
| `physical-properties` | 2 |
| `physical-units` | 1 |
| `physics` | 1 |
| `plotting` | 1 |
| `png` | 3 |
| `pnm` | 1 |
| `point-sets` | 2 |
| `polymorphism` | 3 |
| `polynomials` | 1 |
| `portability` | 2 |
| `precision` | 2 |
| `prime-numbers` | 1 |
| `principal-component-analysis` | 1 |
| `probability-distributions` | 1 |
| `processes` | 1 |
| `pseudoinverse` | 1 |
| `pseudorandom` | 3 |
| `puzzles` | 1 |
| `python` | 1 |
| `quadratic-programming` | 1 |
| `quadrature` | 6 |
| `quasi-newton` | 2 |
| `quasi-random` | 1 |
| `quicksort` | 1 |
| `quoting` | 1 |
| `random-numbers` | 5 |
| `ranking` | 1 |
| `rational-arithmetic` | 1 |
| `real-arithmetic` | 1 |
| `regression` | 3 |
| `regular-expressions` | 4 |
| `reproducibility` | 4 |
| `resampling` | 2 |
| `reverse-communication` | 1 |
| `rgb` | 2 |
| `root-finding` | 4 |
| `rosenbrock-methods` | 1 |
| `runge-kutta` | 4 |
| `sampled-data` | 1 |
| `scalar-functions` | 2 |
| `scientific-data` | 2 |
| `searching` | 3 |
| `sequential-quadratic-programming` | 2 |
| `serialization` | 5 |
| `sets` | 1 |
| `shape-preserving` | 2 |
| `signal-processing` | 4 |
| `simulated-annealing` | 1 |
| `sine-transforms` | 1 |
| `smoothing` | 2 |
| `sorted-arrays` | 1 |
| `sorting` | 5 |
| `spacecraft-trajectories` | 1 |
| `sparse-matrices` | 10 |
| `spatial-indexing` | 1 |
| `special-functions` | 2 |
| `spectral-analysis` | 1 |
| `splines` | 5 |
| `sql` | 1 |
| `sqlite` | 1 |
| `standard-library` | 1 |
| `statistics` | 8 |
| `stiff-equations` | 3 |
| `stochastic-methods` | 3 |
| `strings` | 10 |
| `structured-matrices` | 1 |
| `subprocesses` | 1 |
| `sudoku` | 1 |
| `svd` | 3 |
| `symmetric-systems` | 1 |
| `tabular-data` | 3 |
| `tabulated-data` | 3 |
| `terminal-styling` | 1 |
| `text-files` | 1 |
| `text-processing` | 11 |
| `thermodynamics` | 1 |
| `thread-safe` | 2 |
| `time-series` | 1 |
| `toeplitz-matrices` | 1 |
| `tokenization` | 2 |
| `toml` | 2 |
| `topological-sort` | 1 |
| `tridiagonal-matrices` | 1 |
| `trust-region` | 1 |
| `type-conversion` | 4 |
| `type-safety` | 1 |
| `uncertainty` | 2 |
| `unicode` | 2 |
| `unique-values` | 2 |
| `unit-conversion` | 1 |
| `unit-testing` | 3 |
| `utf-8` | 1 |
| `variable-length-strings` | 1 |
| `vector-graphics` | 1 |
| `vector-operations` | 1 |
| `visualization` | 2 |
| `warnings` | 1 |
| `water` | 1 |
| `weighted-integrals` | 1 |
| `zlib` | 1 |
| `zstandard` | 1 |
