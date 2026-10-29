# Playground topics by package

222 selected packages; 446 distinct playground topics. GitHub topics were retrieved on 2026-10-28.

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

## Arrays

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [array_range](https://github.com/degawa/array_range) — Derived types for managing one-, two- and three-dimensional array bounds. | `array-bounds`, `array-indexing`, `multidimensional-arrays` | None supplied |

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
| [argparse-f](https://github.com/0382/argparse-f) — Object-oriented parsing of typed command-line options, defaults and named arguments. | `argument-parsing`, `command-line-options`, `command-line-parsing` | `argparse`, `command-line`, `fortran`, `modern-fortran`, `oop` |
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
| [fortran_vector](https://github.com/Euler-37/fortran_vector) — Growable integer vectors with insertion, removal and duplicate elimination. | `containers`, `duplicate-removal`, `dynamic-arrays`, `integer-vectors` | None supplied |
| [graphstruc](https://github.com/nedtaylor/graphstruc) — Derived types for graphs, vertices, edges and adjacency structures. | `adjacency-structures`, `containers`, `graphs` | `fortran`, `fortran-package-manager`, `graph-structures`, `graphs`, `library` |
| [list](https://github.com/grofz/list) — Linked lists and tree containers with insertion, searching and sorting operations. | `containers`, `linked-lists`, `searching`, `sorting` | `fortran`, `generics`, `linked-lists`, `red-black-tree` |
| [m_list](https://github.com/urbanjost/M_list) — Maintain sorted arrays and small dictionaries through insertion and lookup. | `containers`, `dictionaries`, `searching`, `sorted-arrays` | `fortran-package-manager` |
| [m_sets](https://github.com/urbanjost/M_sets) — Union, intersection, membership, and unique values for arrays. | `arrays`, `searching`, `sets`, `unique-values` | `fortran`, `fortran-package-manager`, `matlab`, `sets` |
| [metis-fpm](https://github.com/gnikit/metis-fpm) — METIS graph partitioning and sparse matrix ordering through a Fortran interface. | `graph-partitioning`, `graphs`, `language-bindings`, `matrix-ordering`, `sparse-matrices` | None supplied |
| [orbs](https://github.com/degawa/orbs) — Arithmetic, logical and shift operators for stdlib-backed bitsets. | `binary-arithmetic`, `bit-operations`, `bitsets`, `morton-codes` | `bitset`, `bitsets`, `fortran`, `fortran-library`, `fortran-package-manager`, `modern-fortran`, `standard-library`, `wrapper` |
| [rearrayfx](https://github.com/aradi/rearrayfx) — Educational growable real arrays with spare capacity to reduce reallocations. | `containers`, `dynamic-arrays`, `growable-arrays`, `storage-management` | None supplied |

## Data formats

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [csv-fortran](https://github.com/jacobwilliams/csv-fortran) — Read and write CSV files with typed columns. | `csv`, `file-io`, `serialization`, `tabular-data` | `csv`, `fortran`, `fortran-package-manager` |
| [fortran-messagepack](https://github.com/synthfi/fortran-messagepack) — Serialize and deserialize structured values in the compact MessagePack binary format. | `binary-data`, `messagepack`, `serialization` | `fortran`, `messagepack` |
| [fortrandf](https://github.com/jaiken17/fortranDF) — In-memory data frames with named columns of different intrinsic types. | `containers`, `data-frames`, `heterogeneous-data`, `tabular-data` | `dataframe`, `fortran`, `fortran-package-manager` |
| [h5fortran](https://github.com/geospace-code/h5fortran) — High-level HDF5 access for numerical arrays, strings and metadata. | `arrays`, `file-io`, `hdf5`, `metadata`, `scientific-data` | `fortran`, `hdf5`, `object-oriented-fortran` |
| [jonquil](https://github.com/toml-f/jonquil) — JSON parsing and serialization compatible with TOML Fortran types. | `json`, `parsing`, `serialization`, `toml` | `fortran-library`, `fortran-package-manager`, `json`, `json-parser`, `serde` |
| [json-fortran](https://github.com/jacobwilliams/json-fortran) — Read, write, and manipulate JSON documents. | `file-io`, `json`, `serialization` | `fortran`, `fortran-package-manager`, `json` |
| [nc4fortran](https://github.com/geospace-code/nc4fortran) — Object-oriented NetCDF4 input and output for arrays, scalars and attributes. | `array-io`, `metadata`, `netcdf`, `scientific-data` | `netcdf4`, `object-oriented-fortran` |
| [ncio](https://github.com/alex-robinson/ncio) — Convenient NetCDF array input and output with dimensions, attributes and metadata. | `arrays`, `file-io`, `metadata`, `netcdf`, `scientific-data` | None supplied |
| [rojff](https://github.com/everythingfunctional/rojff) — Construct, parse and serialize JSON values with explicit error handling. | `error-handling`, `json`, `json-parsing`, `serialization` | `fortran`, `json`, `json-parser` |
| [toml-f](https://github.com/toml-f/toml-f) — Parse and write TOML configuration files. | `configuration`, `file-io`, `parsing`, `toml` | `fortran-library`, `fortran-package-manager`, `serde`, `toml`, `toml-parser` |

## Data structures

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [any](https://github.com/degawa/any) — Wrap intrinsic scalar and array values behind a common return type. | `array-containers`, `generic-values`, `polymorphism`, `type-erasure` | `fortran`, `fortran-library`, `fortran-package-manager`, `modern-fortran`, `object-oriented-programming`, `operator-overloading`, `user-defined-type` |
| [for_fifo_queue](https://github.com/jordan4ibanez/for_fifo_queue) — FIFO queue using C storage for fixed-size values. | `c-interoperability`, `data-structures`, `fifo`, `queues` | None supplied |
| [integer_set](https://github.com/jordan4ibanez/integer_set) — Simple 32-bit and 64-bit integer sets with insertion, removal and sorting. | `data-structures`, `integer-arithmetic`, `sets` | None supplied |
| [slinked-list](https://github.com/zoziha/slinked-list) — Generic singly linked list with reusable storage for small datasets. | `containers`, `data-structures`, `linked-lists`, `polymorphism` | `fortran`, `fortran-package-manager`, `linked-list`, `singly-linked-list` |

## Databases

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran-sqlite3](https://github.com/interkosmos/fortran-sqlite3) — SQLite database bindings for creating tables, executing SQL and reading query results. | `databases`, `language-bindings`, `sql`, `sqlite` | `fortran`, `fortran-package-manager`, `fpm`, `sqlite`, `sqlite3` |
| [sqliteff](https://github.com/everythingfunctional/sqliteff) — Thin SQLite bindings for database creation, SQL queries and typed result access. | `c-interoperability`, `database`, `sql`, `sqlite` | `database`, `fortran`, `sqlite`, `sqlite3` |

## Dates and times

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [datetime-fortran](https://github.com/wavebitscientific/datetime-fortran) — Date/time objects, durations, and calendar arithmetic. | `calendar-arithmetic`, `date-time`, `durations` | `datetime`, `fortran`, `strftime`, `timedelta` |
| [m_time](https://github.com/urbanjost/M_time) — Calendar arithmetic, Julian dates, and date/time formatting. | `calendar-arithmetic`, `date-time`, `formatting`, `julian-dates` | `calendar`, `date`, `date-formatting`, `datetime`, `fortran`, `fortran-package-manager`, `fpm`, `time` |

## Differential equations

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [daskr](https://github.com/davidpfister/daskr) — Differential-algebraic equation solver with root finding and direct or Krylov linear solvers. | `dae`, `differential-equations`, `iterative-solvers`, `krylov-methods`, `root-finding` | `dae`, `differential-equations`, `fortran`, `fortran-package-manager`, `netlib` |
| [dde_solver](https://github.com/WarrenWeckesser/dde_solver) — Adaptive integration and interpolation for delay differential equations. | `adaptive-methods`, `delay-differential-equations`, `initial-value-problems`, `interpolation` | `delay-differential-equations`, `differential-equations`, `fortran` |
| [ddeabm](https://github.com/jacobwilliams/ddeabm) — Adaptive Adams-Bashforth-Moulton ODE integration with event finding. | `adams-methods`, `adaptive-methods`, `event-detection`, `initial-value-problems`, `ode` | `adams-bashforth`, `fortran`, `fortran-package-manager`, `ode`, `root-finding`, `slatec` |
| [diffeq](https://github.com/jchristopherson/diffeq) — Adaptive explicit and implicit integrators for ordinary differential and differential-algebraic equations. | `adaptive-methods`, `dae`, `differential-equations`, `implicit-methods`, `ode` | `adams-bashforth-moulton`, `backwards-differentiation-formula`, `bdf`, `differential-algebraic-equations`, `differential-equations`, `esdirk`, `event-detection`, `implicit-runge-kutta`, `index-reduction`, `kennedy-carpenter`, `rosenbrock`, `runge-kutta-methods`, `tsitouras` |
| [dop853](https://github.com/jacobwilliams/dop853) — Adaptive eighth-order Runge-Kutta integration of ordinary differential equations. | `adaptive-methods`, `initial-value-problems`, `ode`, `runge-kutta` | `dop853`, `fortran`, `fortran-package-manager`, `ode`, `runge-kutta` |
| [dvode](https://github.com/jacobwilliams/dvode) — Variable-coefficient multistep ODE solver for stiff and nonstiff systems. | `initial-value-problems`, `multistep-methods`, `ode`, `stiff-equations` | `adams-bashforth`, `fortran`, `fortran-package-manager`, `ode`, `vode` |
| [fishpack](https://github.com/jlokimlin/fishpack) — Finite-difference solvers for separable elliptic partial differential equations. | `finite-differences`, `helmholtz-equation`, `partial-differential-equations`, `poisson-equation` | None supplied |
| [flint](https://github.com/princemahajan/FLINT) — Adaptive explicit Runge-Kutta ODE integration with dense output and event detection. | `adaptive-methods`, `dense-output`, `event-detection`, `ode`, `runge-kutta` | `differential-equations`, `fortran`, `julia`, `numerical-integration`, `ode`, `ode-events`, `runge-kutta` |
| [heatflow](https://github.com/ExeQuantCode/HeatFlow) — Finite-difference models of Fourier and Cattaneo heat transport. | `cattaneo-model`, `finite-differences`, `heat-equation`, `heat-transfer`, `sparse-linear-systems` | `cattaneo`, `finite-difference`, `finite-difference-time-domain`, `fourier`, `heat-flow`, `heating`, `modelling` |
| [hrweno](https://github.com/HugoMVale/HR-WENO) — High-resolution WENO reconstruction and TVD integration for conservation equations. | `conservation-laws`, `finite-volumes`, `partial-differential-equations`, `runge-kutta`, `tvd`, `weno` | `fortran`, `fpm`, `high-resolution`, `hyperbolic-equations`, `partial-differential-equations`, `pde`, `reconstruction`, `weno-schemes` |
| [odepack](https://github.com/Nicholaswogan/odepack) — Modern thread-safe interfaces to the LSODA and LSODAR initial-value ODE solvers. | `event-detection`, `initial-value-problems`, `ode`, `stiff-equations`, `thread-safe` | `fortran-package-manager`, `ode`, `ode-solver`, `odepack` |
| [rkf45](https://github.com/zoziha/rkf45) — Classic adaptive Runge-Kutta-Fehlberg fourth/fifth-order ODE integration. | `adaptive-methods`, `initial-value-problems`, `ode`, `runge-kutta` | `fehlberg`, `fortran`, `fortran-package-manager`, `fourth-fifth-order`, `ode`, `rkf45`, `runge-kutta` |
| [rklib](https://github.com/jacobwilliams/rklib) — A collection of fixed- and variable-step Runge-Kutta ODE integration methods. | `adaptive-methods`, `initial-value-problems`, `ode`, `runge-kutta` | `differential-equations`, `fortran`, `fortran-package-manager`, `ode`, `ode-solver`, `root-finding`, `runge-kutta`, `runge-kutta-adaptive-step-size`, `runge-kutta-fehlberg` |
| [stiff3](https://github.com/ivan-pi/stiff3) — Adaptive third-order Rosenbrock solver for stiff autonomous ordinary differential equations. | `adaptive-methods`, `ode`, `rosenbrock-methods`, `stiff-equations` | `adaptive`, `differential`, `equation`, `fortran`, `ode`, `solver`, `stiff` |
| [twopnt](https://github.com/perazz/twopnt) — Boundary-value problem solver with adaptive grids and a modern object interface. | `adaptive-grids`, `boundary-value-problems`, `differential-equations` | `boundary-value-problem`, `boundary-value-problems`, `bvp`, `fortran` |

## Differentiation

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [ad_dnsvm](https://github.com/lauvergn/AD_dnSVM) — Forward automatic differentiation of scalars, vectors and matrices through third derivatives. | `arrays`, `automatic-differentiation`, `derivatives`, `differentiation`, `higher-order-derivatives` | `automatic-differentiation`, `fortran` |
| [diffstruc](https://github.com/nedtaylor/diffstruc) — Forward and reverse automatic differentiation with array computation graphs. | `automatic-differentiation`, `derivatives`, `forward-mode`, `gradients`, `reverse-mode` | `automatic-differentiation`, `backpropagation`, `differentiation`, `fortran`, `fortran-package-manager`, `forward-mode`, `library`, `partial-differentiation`, `reverse-mode` |
| [dnaoad-fpm](https://github.com/fpenunuri/DNAOAD-FPM) — Complex dual numbers for derivatives through configurable order. | `automatic-differentiation`, `complex-arithmetic`, `dual-numbers`, `higher-order-derivatives` | None supplied |
| [fordiff](https://github.com/gha3mi/fordiff) — Numerical derivatives using finite differences and complex steps. | `complex-step`, `derivatives`, `differentiation`, `finite-differences` | `complex-step-differentiation`, `derivative`, `differentiation`, `finite-difference`, `fortran`, `fortran-package-manager` |
| [forwarddiff](https://github.com/Nicholaswogan/forwarddiff) — Forward automatic differentiation using dual numbers (Differentia). | `automatic-differentiation`, `derivatives`, `differentiation`, `dual-numbers` | `autodiff`, `autodifferentiation`, `automatic-differentiation`, `differential-equations` |
| [numdiff](https://github.com/jacobwilliams/NumDiff) — Numerical derivatives and sparse Jacobian estimation. | `differentiation`, `finite-differences`, `jacobians`, `sparse-matrices` | `differentiation`, `finite-differences`, `graph-coloring`, `numerical-differentiation`, `numerical-methods`, `optimization`, `sparsity-optimization` |

## Dynamics and control

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [dynamics](https://github.com/jchristopherson/dynamics) — Frequency response, vibration analysis, modal analysis and dynamic-system calculations. | `control-systems`, `damping`, `frequency-response`, `modal-analysis`, `vibration` | `denavit-hartenberg`, `frequency-analysis`, `frequency-response`, `frf-fitting`, `geometric-algorithms`, `kinematics`, `modal-analysis`, `parallel-linkage`, `poincare-map`, `quaternions`, `rotation-matrix`, `serial-linkage`, `structural-dynamics`, `system-identification` |
| [friction](https://github.com/jchristopherson/friction) — Coulomb, Stribeck and dynamic friction models for contacting bodies. | `constitutive-models`, `contact-mechanics`, `coulomb-friction`, `friction`, `stribeck-friction` | `coulomb`, `friction`, `generalized-maxwell-slip`, `lu-gre`, `maxwell`, `stribeck-friction` |

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
| [erloff](https://github.com/everythingfunctional/erloff) — Structured error lists and logging with message types and call context. | `diagnostics`, `error-handling`, `logging` | `error-handling`, `fortran`, `logging` |
| [errstat](https://github.com/degawa/errstat) — Return and inspect structured error statuses and messages. | `diagnostics`, `error-handling`, `status-codes` | `error-handling`, `fortran`, `fortran-package-manager` |
| [ferror](https://github.com/jchristopherson/ferror) — Structured error and warning reporting with configurable handling. | `diagnostics`, `error-handling`, `warnings` | None supplied |

## Expression parsing

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [feq-parse](https://github.com/FluidNumerics/feq-parse) — Evaluate mathematical expressions supplied as strings at scalar or array inputs. | `array-evaluation`, `expression-parsing`, `function-evaluation`, `mathematical-expressions` | `equation-parser`, `fortran`, `hpc`, `self-ecosystem` |
| [fortran-tokenizer](https://github.com/14NGiestas/fortran-tokenizer) — Customizable tokenization with validation and ignore callbacks. | `parsing`, `text-processing`, `tokenization` | `fortran`, `fortran-package-manager`, `parsers`, `strings`, `tokenizer` |
| [fortran_function_parser](https://github.com/jacobwilliams/fortran_function_parser) — Parse and evaluate mathematical expressions supplied as strings. | `expression-parsing`, `mathematical-expressions`, `parsing` | `expression-parser`, `fortran`, `function-parser` |
| [m_calculator](https://github.com/urbanjost/M_calculator) — Evaluate mathematical expressions and named variables supplied as text. | `expression-parsing`, `mathematical-expressions`, `parsing` | `expression`, `expression-evaluator`, `fortran`, `fortran-package-manager`, `parse` |
| [shunting-yard-fortran](https://github.com/14NGiestas/shunting-yard-fortran) — Experimental expression parser with token callbacks and fixed operator precedences. | `expression-parsing`, `operator-precedence`, `shunting-yard-algorithm`, `tokenization` | `fortran`, `fortran-package-manager`, `modern-fortran`, `parsing`, `shunting-yard-algorithm` |

## Files and processes

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [ffilesystem](https://github.com/scivision/ffilesystem) — Portable filesystem and path operations through Fortran, C and C++ interfaces. | `directories`, `file-io`, `filesystem`, `paths`, `portability` | `cpp17`, `filesystem`, `fortran`, `libc`, `path-manipulation` |
| [fmmap](https://github.com/PierUgit/fmmap) — Map files into memory and access their contents as Fortran arrays. | `arrays`, `file-io`, `memory-mapped-files` | `fortran`, `memory-mapped-file` |
| [io-fortran-library](https://github.com/acbbullock/IO-Fortran-Library) — High-level numeric array file I/O, dynamic strings, and numeric/string conversion. | `arrays`, `file-io`, `strings`, `tabular-data`, `type-conversion` | `csv`, `fortran`, `fortran-package-manager`, `input-output`, `modern-fortran` |
| [io_utilities](https://github.com/arjenmarkus/io_utilities) — INI configuration files, command parsing, progress reporting and formatted output. | `configuration-files`, `file-io`, `formatted-output`, `ini-files` | None supplied |
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
| [uint-fortran](https://github.com/ShinobuAmasaki/uint-fortran) — Unsigned integer derived types with arithmetic, comparisons and conversions. | `c-interoperability`, `integer-arithmetic`, `modular-arithmetic`, `unsigned-integers` | `fortran`, `unsigned-integers` |

## Geodesy

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [geodesic-fortran](https://github.com/jacobwilliams/geodesic-fortran) — Distances, bearings and geodetic coordinate transformations on spheres and ellipsoids. | `coordinate-transformations`, `distances`, `ellipsoids`, `geodesics`, `geodesy` | `fortran`, `fortran-package-manager`, `geodesy`, `geodetic-computations`, `vincenty-direct`, `vincenty-formula`, `vincenty-inverse` |
| [maptran3d](https://github.com/geospace-code/maptran3d) — Geographic and Earth-centered Cartesian coordinate transformations. | `cartesian-coordinates`, `coordinate-transformations`, `geodesy`, `geographic-coordinates` | `coordinate-conversions`, `coordinate-transformation`, `fortran2018`, `geodesy`, `modern-fortran` |

## Geometry

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran-simplify](https://github.com/jaiken17/fortran-simplify) — Reduce the number of polyline points using geometric simplification algorithms. | `computational-geometry`, `curve-approximation`, `polyline-simplification` | `fortran`, `fortran-package-manager`, `noise-reduction`, `polyline`, `polyline-simplification` |
| [geompack](https://github.com/jchristopherson/geompack) — Delaunay triangulation of planar point sets. | `delaunay-triangulation`, `geometry`, `meshes`, `point-sets` | `delaunay-triangulation`, `fortran`, `fortran-package-manager`, `geometry`, `triangulation`, `triangulation-delaunay` |

## High precision

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [bstrith](https://github.com/degawa/bstrith) — Fixed-width binary-string arithmetic, shifts and logical operations. | `binary-arithmetic`, `binary-strings`, `bit-operations`, `bit-shifts` | None supplied |
| [mpfun2020-var1](https://github.com/jacobwilliams/MPFUN2020-var1) — Thread-safe arbitrary-precision real and complex arithmetic. | `arbitrary-precision`, `complex-arithmetic`, `precision`, `real-arithmetic`, `thread-safe` | `arbitrary-precision` |
| [strith](https://github.com/degawa/strith) — Decimal-string arithmetic and signed or unsigned formatting of long integers. | `decimal-arithmetic`, `integer-arithmetic`, `integer-formatting`, `strings` | `fortran`, `fortran-library`, `fortran-package-manager`, `fortran2008`, `long-integer`, `modern-fortran`, `string` |

## Images

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [cairo-fortran](https://github.com/vmagnin/cairo-fortran) — Cairo bindings for drawing vector graphics into PNG and other output formats. | `drawing`, `images`, `language-bindings`, `png`, `vector-graphics` | `bindings`, `cairo`, `fortran`, `fortran-package-manager` |
| [forimage](https://github.com/gha3mi/forimage) — Create, read, write and transform PNM images and convert color representations. | `color-conversion`, `file-io`, `image-processing`, `images`, `pnm` | `color`, `decimal`, `fortran`, `fortran-package-manager`, `hexadecimal`, `hsl`, `hsv`, `image`, `pbm`, `pgm`, `pnm`, `ppm`, `rgb` |
| [fortran_stb_image](https://github.com/lewisfish/fortran_stb_image) — Read and write PNG and other raster image formats through the stb libraries. | `file-io`, `image-io`, `images`, `language-bindings`, `png` | None supplied |

## Integral transforms

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [spherepack](https://github.com/jlokimlin/spherepack) — Spherical harmonic transforms and spherical differential-equation solvers. | `helmholtz-equation`, `integral-transforms`, `partial-differential-equations`, `spherical-harmonics` | None supplied |

## Integration

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [dcuhre](https://github.com/Zaneham/dcuhre) — Adaptive multidimensional integration over hyperrectangles with vector integrands and error estimates. | `adaptive-methods`, `cubature`, `error-estimation`, `multidimensional`, `quadrature` | `dcuhre`, `fortran`, `fortran-package-manager`, `integration`, `mathematics`, `multidimensional-integration`, `numerical-integration`, `quadrature` |
| [fortran_cubatures](https://github.com/willklausler/fortran_cubatures) — Gaussian cubature rules for finite-element reference lines, triangles, quadrilaterals, tetrahedra, hexahedra and wedges. | `cubature`, `finite-elements`, `gaussian-quadrature`, `multidimensional`, `quadrature` | `cubature`, `finite-elements`, `fortran`, `fpm`, `numerical-integration`, `quadrature` |
| [gaussjacobiquad](https://github.com/HaoZeke/GaussJacobiQuad) — Gauss-Jacobi quadrature nodes and weights for weighted numerical integration. | `gauss-jacobi`, `gaussian-quadrature`, `quadrature`, `weighted-integrals` | `f2py`, `gauss-jacobi`, `meson`, `numerical-integration`, `quadrature` |
| [integrate_fortran](https://github.com/Euler-37/integrate_fortran) — Gauss-Legendre quadrature for one-dimensional and multidimensional integrals. | `gauss-legendre`, `gaussian-quadrature`, `multidimensional`, `quadrature` | `gauss-legendre-integration`, `numerical-integration`, `quadrature` |
| [qdutillib](https://github.com/lauvergn/QDUtilLib) — Gauss-Legendre and Gauss-Hermite quadrature, linear algebra and numerical utilities. | `gauss-hermite`, `gauss-legendre`, `gaussian-quadrature`, `quadrature` | `fortran` |
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
| [fglm](https://github.com/jordan4ibanez/fglm) — Typed vectors and 4-by-4 matrices for geometric transformations. | `geometry`, `matrices`, `transformations`, `vectors` | None supplied |
| [fordot](https://github.com/gha3mi/fordot) — Selectable dot-product implementations, including BLAS and blocked calculations. | `blas`, `blocked-algorithms`, `dot-products`, `linear-algebra` | `coarray`, `dot-product`, `fortran`, `fortran-package-manager` |
| [foreig](https://github.com/gha3mi/foreig) — LAPACK interfaces for eigenvalues and eigenvectors of real matrices. | `eigenvalues`, `eigenvectors`, `lapack`, `linear-algebra` | `eig`, `eigenvalues`, `eigenvalues-and-eigenvectors`, `eigenvectors`, `fortran`, `fortran-package-manager`, `lapack`, `mkl` |
| [forinv](https://github.com/gha3mi/forinv) — Matrix inverses and singular-value-decomposition pseudoinverses. | `linear-algebra`, `matrix-inverse`, `pseudoinverse`, `svd` | `fortran`, `fortran-package-manager`, `inverse`, `pseudoinverse`, `svd` |
| [formatmul](https://github.com/gha3mi/formatmul) — Matrix products with transpose options and selectable multiplication methods. | `blas`, `linear-algebra`, `matrix-multiplication`, `matrix-vector-products`, `transpose` | `coarray`, `fortran`, `fortran-package-manager`, `matmul` |
| [forsvd](https://github.com/gha3mi/forsvd) — Singular value decomposition and truncated low-rank matrix approximations. | `lapack`, `linear-algebra`, `low-rank-approximation`, `singular-value-decomposition` | `fortran`, `fortran-package-manager`, `image-compression`, `low-rank-approximation`, `singular-value-decomposition`, `svd` |
| [fortran-lapack](https://github.com/perazz/fortran-lapack) — Modern linear algebra: linear systems, eigenvalues, least squares, and matrix factorizations. | `eigenvalues`, `lapack`, `least-squares`, `linear-algebra`, `linear-systems`, `matrix-factorization` | `blas`, `eigenvalues`, `eigenvectors`, `fortran`, `fortran-package-manager`, `lapack`, `lapack95`, `lapacke`, `linear-algebra`, `linear-equations`, `machine-learning`, `matrix-factorization`, `modern-fortran`, `modern-fortran-modules`, `numpy`, `singular-values`, `svd` |
| [fsparse](https://github.com/jalvesz/FSPARSE) — Sparse matrix storage, format conversions and matrix-vector products. | `format-conversion`, `linear-algebra`, `matrix-vector-products`, `sparse-matrices` | `fortran`, `fortran-library`, `fortran-package-manager`, `sparse-matrices` |
| [kiss](https://github.com/ivan-pi/kiss) — Krylov iterative solvers for dense matrices and matrix-free linear operators. | `iterative-solvers`, `krylov-methods`, `linear-algebra`, `linear-systems`, `matrix-free` | None supplied |
| [lightkrylov](https://github.com/nekStab/LightKrylov) — Krylov methods for eigenvalues, linear systems, singular values and matrix exponentials. | `eigenvalues`, `krylov-methods`, `linear-algebra`, `linear-systems`, `matrix-exponentials`, `svd` | None supplied |
| [linalg](https://github.com/jchristopherson/linalg) — Convenient dense and sparse linear algebra interfaces to BLAS, LAPACK and ARPACK. | `arpack`, `blas`, `lapack`, `linear-algebra`, `sparse-matrices` | `blas`, `cholesky-decomposition`, `compressed-row-storage`, `compressed-sparse-row`, `eigenvalues`, `eigenvectors`, `fortran`, `lapack`, `linear-algebra`, `lu-decomposition`, `qr-decomposition`, `singular-value-decomposition`, `sparse-matrix` |
| [linalg_fortran](https://github.com/Euler-37/linalg_fortran) — Typed LAPACK interfaces for matrix inverses, determinants and Hermitian eigenproblems. | `determinants`, `eigenvalues`, `lapack`, `linear-algebra`, `matrix-inversion` | `lapack`, `linalg`, `matrix-library` |
| [lsmr](https://github.com/jacobwilliams/LSMR) — Iterative solution of sparse linear equations and least-squares problems. | `iterative-solvers`, `least-squares`, `linear-algebra`, `linear-systems`, `sparse-matrices` | `fortran`, `fortran-package-manager`, `least-squares`, `linear-algebra`, `linear-equations`, `lsmr`, `sparse-linear-systems` |
| [lsqr](https://github.com/jacobwilliams/LSQR) — Iterative sparse linear systems and least-squares solver using coordinate storage. | `iterative-solvers`, `least-squares`, `linear-algebra`, `linear-systems`, `sparse-matrices` | `conjugate-gradient`, `fortran`, `fortran-package-manager`, `least-squares`, `linear-algebra`, `linear-equations`, `lsqr` |
| [lusol](https://github.com/jacobwilliams/lusol) — Sparse LU factorization, linear solves and efficient column updates. | `linear-systems`, `lu-factorization`, `matrix-updates`, `sparse-linear-algebra` | `fortran`, `fortran-package-manager`, `linear-algebra`, `lu-decomposition`, `lu-factorization`, `lusol`, `matrix-factorization`, `sparse-linear-algebra`, `sparse-matrix` |
| [m_la](https://github.com/urbanjost/M_LA) — Magic squares, reduced row-echelon forms and other small matrix utilities. | `linear-algebra`, `magic-squares`, `matrices`, `row-reduction` | `determinant`, `fortran-package-manager`, `linear-algebra`, `magic-square`, `matrix-inverse` |
| [minres](https://github.com/willdickson/minres) — Iterative solution of symmetric sparse systems, including indefinite matrices. | `iterative-solvers`, `linear-algebra`, `linear-systems`, `sparse-matrices`, `symmetric-systems` | None supplied |
| [qdldl-fortran](https://github.com/jacobwilliams/qdldl-fortran) — Sparse LDL-transpose factorization, orderings and solves for quasi-definite systems. | `ldlt-factorization`, `linear-systems`, `matrix-ordering`, `quasi-definite`, `sparse-linear-algebra` | `fortran`, `fortran-package-manager`, `ldl-factorization`, `linear-algebra`, `linear-systems`, `numerical-optimization`, `sparse-data`, `sparse-linear-systems` |
| [sparse_fortran](https://github.com/Euler-37/sparse_fortran) — Coordinate and compressed-row sparse matrices with matrix-vector products. | `coordinate-storage`, `csr-storage`, `linear-algebra`, `matrix-vector-products`, `sparse-matrices` | None supplied |
| [specialmatrices](https://github.com/loiseaujc/SpecialMatrices) — Structured diagonal, circulant, Toeplitz, tridiagonal, and other matrices. | `circulant-matrices`, `linear-algebra`, `structured-matrices`, `toeplitz-matrices`, `tridiagonal-matrices` | `linear-algebra`, `sparse-linear-systems`, `sparse-matrix` |
| [y12m](https://github.com/ivan-pi/y12m) — Direct sparse LU factorization with pivoting, reordering and reuse for multiple right-hand sides. | `direct-solvers`, `linear-algebra`, `linear-systems`, `lu-factorization`, `sparse-matrices` | None supplied |

## Machine learning

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [athena](https://github.com/nedtaylor/athena) — Neural networks with convolutional, graph-based and physics-informed layers. | `automatic-differentiation`, `deep-learning`, `machine-learning`, `neural-networks` | `automatic-differentiation`, `cnn`, `convolution`, `convolutional-neural-networks`, `deep-learning`, `feed-forward-neural-networks`, `fortran`, `fortran-package-manager`, `graph-neural-network`, `inverse-design`, `machine-learning`, `message-passing-neural-network`, `neural-network`, `physics-informed-neural-networks` |
| [fortran-flann](https://github.com/ivan-pi/fortran-flann) — FLANN interfaces for nearest-neighbor searches and spatial indexing. | `language-bindings`, `machine-learning`, `nearest-neighbors`, `spatial-indexing` | `approximate-nearest-neighbor-search`, `hierarchical-clustering`, `high-dimensional-data`, `kdtree`, `kmeans-clustering`, `nearest-neighbor-search`, `spatial-search` |
| [neural-fortran](https://github.com/modern-fortran/neural-fortran) — Neural networks with dense and convolutional layers and gradient-based training. | `convolutional-networks`, `gradient-based-optimization`, `machine-learning`, `neural-networks` | `cnn`, `deep-learning`, `fortran`, `machine-learning`, `neural-network`, `parallel` |

## Memory management

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [smart-pointers](https://github.com/sourceryinstitute/smart-pointers) — Reference-counted smart pointers with automatic resource cleanup. | `memory-management`, `reference-counting`, `resource-management` | `garbage-collection`, `reference-counting`, `smart-pointers` |

## Number theory

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran-primes](https://github.com/perazz/fortran-primes) — Generate prime numbers, test primality, and factor integers. | `integer-factorization`, `number-theory`, `prime-numbers` | `factorization`, `fortran`, `fortran-package-manager`, `modern-fortran`, `prime-numbers`, `primes` |
| [rational_number](https://github.com/art-rasa/rational_number) — Exact rational arithmetic with integer numerators and denominators. | `exact-arithmetic`, `number-theory`, `rational-arithmetic` | None supplied |

## Physical constants

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [codata](https://github.com/MilanSkocic/codata) — CODATA physical constants and uncertainties for several published adjustments. | `physical-constants`, `physics`, `uncertainty` | `c`, `codata`, `fortran-language`, `fortran-library`, `fortran-package-manager`, `python`, `science` |
| [fundamental_constants](https://github.com/vmagnin/fundamental_constants) — CODATA fundamental physical constants with explicitly selectable editions. | `codata`, `nist`, `physical-constants`, `physics` | `codata`, `fortran`, `fortran-package-manager`, `nist` |

## Physical properties

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [ciaaw](https://github.com/MilanSkocic/ciaaw) — Standard atomic weights, isotopic abundances and nuclide masses for chemistry. | `atomic-weights`, `chemistry`, `isotopes`, `physical-properties` | `chemistry`, `fortran`, `fortran-package-manager`, `isotopes`, `standard-atomic-masses` |
| [ecx](https://github.com/MilanSkocic/ecx) — Electrochemical kinetics, impedance and photoelectrochemistry calculations. | `electrical-impedance`, `electrochemistry`, `electrode-kinetics`, `equivalent-circuits` | `electrochemistry`, `fortran-language`, `fortran-library`, `fortran-package-manager`, `science` |
| [iapws](https://github.com/MilanSkocic/iapws) — IAPWS thermodynamic properties of water, including saturation pressure and temperature. | `iapws`, `physical-properties`, `thermodynamics`, `water` | `fortran-language`, `fortran-library`, `fortran-package-manager`, `iapws`, `science`, `water` |

## Plotting

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [pyplot-fortran](https://github.com/jacobwilliams/pyplot-fortran) — Create PNG plots from Fortran through Python and Matplotlib. | `matplotlib`, `plotting`, `png`, `python`, `visualization` | `contour-plot`, `fortran`, `fortran-package-manager`, `matplotlib`, `plot`, `plotting`, `plotting-in-fortran`, `pyplot` |

## Quadrature

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [kronrod](https://github.com/jacobwilliams/kronrod) — Generate Gauss-Kronrod quadrature nodes and weights using arbitrary precision. | `arbitrary-precision`, `gauss-kronrod`, `quadrature`, `quadrature-rules` | `fortran`, `fortran-package-manager`, `gauss-kronrod`, `gauss-kronrod-quadrature`, `quadpack` |

## Quantum mechanics

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [featom](https://github.com/atomic-solvers/featom) — Radial Schroedinger and Dirac equations solved with high-order finite elements. | `atomic-structure`, `dirac-equation`, `eigenvalue-problems`, `finite-elements`, `quantum-mechanics`, `schroedinger-equation` | `atomic-structures`, `dft`, `finite-element-methods`, `hartree-fock` |

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
| [seiscope-optimization](https://github.com/ofmla/seiscope_opt_toolbox_w_ctypes) — Gradient-based optimization with L-BFGS, nonlinear conjugate gradients and truncated Newton methods. | `gradient-based-optimization`, `lbfgs`, `nonlinear-conjugate-gradient`, `optimization`, `truncated-newton` | `ctypes-wrapper`, `fortran`, `fortran-package-manager`, `geophysics`, `gradient-based-optimisation`, `python-bindings`, `wrapper-library` |
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
| [amosf90](https://github.com/Euler-37/amosf90) — AMOS interfaces for complex-argument, noninteger-order Bessel and related functions. | `bessel-functions`, `complex-arguments`, `modified-bessel-functions`, `special-functions` | None supplied |
| [carlson-elliptic-integrals](https://github.com/jacobwilliams/carlson-elliptic-integrals) — Carlson symmetric elliptic integrals for pendulum periods and other applications. | `carlson-symmetric-forms`, `elliptic-integrals`, `pendulum`, `special-functions` | None supplied |
| [fortran-bessels](https://github.com/perazz/fortran-bessels) — Bessel and modified Bessel functions, demonstrated with fixed orders zero and one. | `bessel-functions`, `cylindrical-functions`, `modified-bessel-functions`, `special-functions` | `bessel`, `bessel-function`, `fortran`, `math`, `special-functions` |
| [rpn-calculator-fortran](https://github.com/scivision/rpn-calculator-fortran) — Numerical functions from an RPN calculator, including special functions, rational arithmetic and conversions. | `bessel-functions`, `gamma-function`, `rational-arithmetic`, `rpn-calculator`, `special-functions` | `modern-fortran`, `reverse-polish-calculator` |
| [specfun](https://github.com/jacobwilliams/specfun) — Special functions including Bessel, Airy, gamma, and related functions. | `airy-functions`, `bessel-functions`, `gamma-functions`, `special-functions` | `fortran`, `fortran-package-manager`, `scipy`, `special-functions` |
| [specfunc-fullerton](https://github.com/arjenmarkus/specfunc-fullerton) — Fullerton special functions including gamma, Bessel, Airy and exponential integrals. | `airy-functions`, `bessel-functions`, `exponential-integrals`, `gamma-functions`, `special-functions` | `special-functions` |

## Statistics

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [econ-toolchain](https://github.com/renatomatz/econ-toolchain) — Markov chains, stochastic-process discretization and numerical tools for economic models. | `economics`, `markov-chains`, `stationary-distributions`, `stochastic-processes`, `tauchen-discretization` | None supplied |
| [fjsample](https://github.com/RJaBi/FJsample) — Jackknife and bootstrap resampling, bias estimates and statistical uncertainties. | `bootstrap`, `jackknife`, `resampling`, `statistics`, `uncertainty` | `bootstrap-resampling`, `fortran`, `fortran-package-manager`, `jackknife-resampling`, `meson-python` |
| [forpca](https://github.com/gha3mi/forpca) — Principal component directions from eigendecomposition or singular value decomposition. | `dimensionality-reduction`, `eigenvalues`, `principal-component-analysis`, `statistics`, `svd` | `fortran`, `fortran-package-manager`, `pca`, `principal-component-analysis` |
| [fortsa](https://github.com/zoziha/fortsa) — Time-series autocorrelations, partial correlations and ARIMA modeling through CTSA. | `arima`, `autocorrelation`, `statistics`, `time-series` | `arima`, `arma`, `bindings`, `fortran`, `fpm`, `time-series`, `time-series-analysis`, `tsa` |
| [fstats](https://github.com/jchristopherson/fstats) — Probability distributions, statistical tests, regression, bootstrap sampling, and MCMC. | `bootstrap`, `hypothesis-testing`, `mcmc`, `probability-distributions`, `regression`, `statistics` | `allan-variance`, `anova`, `bootstrap`, `design-of-experiments`, `distributions`, `experimental-design`, `gauge-r-and-r-study`, `hypothesis-testing`, `interpolation`, `levenberg-marquardt`, `lowess`, `markov-chain-monte-carlo`, `mcmc-sampler`, `missing-data`, `regression`, `sampling-distribution`, `special-functions`, `statistical-testing`, `statistics` |
| [gslib](https://github.com/exepulveda/gslib2.0) — Geostatistical covariance models, kriging and spatial simulation routines. | `covariance-models`, `gaussian-simulation`, `geostatistics`, `kriging`, `spatial-statistics` | None supplied |
| [lib_statistics](https://github.com/sebastiandyrda/lib_statistics) — Logistic regression using iteratively reweighted least squares. | `least-squares`, `logistic-regression`, `regression`, `statistics` | None supplied |
| [odrpack95](https://github.com/HugoMVale/odrpack95) — Orthogonal distance regression with errors in both variables and optional parameter bounds. | `bound-constraints`, `errors-in-variables`, `least-squares`, `regression`, `statistics` | `fortran`, `fpm`, `mathematics`, `odr`, `regression`, `statistics` |

## Strings

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortran-pcre2](https://github.com/interkosmos/fortran-pcre2) — Perl-compatible regular expressions, capture groups and text matching through PCRE2. | `language-bindings`, `pattern-matching`, `pcre2`, `regular-expressions`, `text-processing` | `fortran`, `fortran-2018`, `fortran-package-manager`, `fpm`, `pcre`, `pcre2`, `regex`, `regexp` |
| [fortran-string-to-real](https://github.com/Carltoffel/Fortran-String-to-Real) — Experimental conversion of valid decimal and scientific-notation strings to real numbers. | `floating-point`, `number-parsing`, `strings`, `type-conversion` | None supplied |
| [iso_varying_string](https://github.com/everythingfunctional/iso_varying_string) — Variable-length strings implementing the ISO varying-string specification. | `strings`, `text-processing`, `variable-length-strings` | `fortran`, `iso`, `strings` |
| [ryu_fortran](https://github.com/St-Maxwell/ryu_fortran) — Ryu conversion of floating-point numbers to short decimal representations. | `floating-point`, `number-formatting`, `strings`, `type-conversion` | `floating-point`, `string` |
| [scanner](https://github.com/freevryheid/scanner) — Character-by-character text scanning with bounded navigation for small parsers. | `character-processing`, `parsing`, `strings`, `text-scanning` | `fortran`, `parser`, `scanner` |
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
| [fassert](https://github.com/degawa/fassert) — Extensible assertions for scalar and array values and numerical tolerances. | `assertions`, `floating-point-comparison`, `testing`, `unit-testing` | `assert`, `assertion`, `assertion-library`, `assertions`, `assertions-library`, `fortran`, `fortran-library`, `fortran-package-manager`, `fortran2008`, `modern-fortran`, `testing` |
| [fortran_test_helper](https://github.com/jchristopherson/fortran_test_helper) — Assertions and random array generators for numerical tests. | `assertions`, `numerical-testing`, `random-numbers`, `unit-testing` | None supplied |
| [m_framework](https://github.com/urbanjost/M_framework) — Unit testing, floating-point comparisons, and diagnostic formatting. | `assertions`, `diagnostics`, `floating-point`, `numerical-testing`, `unit-testing` | `fortran`, `fortran-package-manager`, `fpm`, `unit-testing` |
| [test-drive](https://github.com/fortran-lang/test-drive) — Lightweight unit testing with named tests and assertions. | `assertions`, `unit-testing` | `fortran-library`, `fortran-package-manager`, `testing-framework`, `unit-testing` |
| [veggies](https://github.com/everythingfunctional/veggies) — Functional unit-testing framework with readable specification-style results. | `bdd`, `functional-programming`, `test-framework`, `unit-testing` | None supplied |

## Text parsing

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [forgex](https://github.com/ShinobuAmasaki/forgex) — Regular expressions with Unicode support and full or substring matching. | `pattern-matching`, `regular-expressions`, `text-processing`, `unicode` | `fortran`, `fortran-package-manager`, `regex`, `regular-expression` |
| [fortran-regex](https://github.com/perazz/fortran-regex) — Search text with a lightweight regular expression engine. | `pattern-matching`, `regular-expressions`, `text-processing` | `fortran`, `regex`, `regex-parser`, `regular-expression`, `regular-expressions` |
| [fortran-shlex](https://github.com/perazz/fortran-shlex) — Split command strings into tokens while respecting quotes. | `command-line`, `parsing`, `quoting`, `tokenization` | `fortran`, `posix`, `regular-expressions`, `shlex`, `shlex-library` |
| [m_match](https://github.com/urbanjost/M_match) — Pattern matching with a compact grep-style regular expression syntax. | `pattern-matching`, `regular-expressions`, `text-processing` | `bre`, `fortran`, `fortran-package-manager`, `regex`, `regular-expressions` |
| [parff](https://github.com/everythingfunctional/parff) — Composable functional parsers for structured text and useful parse errors. | `functional-programming`, `parser-combinators`, `parsing`, `text-processing` | `fortran`, `parser`, `parser-combinators`, `parser-library` |

## Text processing

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [enclose](https://github.com/degawa/enclose) — Enclose strings in matching brackets or custom delimiters. | `brackets`, `strings`, `text-formatting` | `fortran`, `fortran-library`, `fortran-package-manager` |
| [fed](https://github.com/degawa/fed) — Construct Fortran format edit descriptors programmatically. | `format-descriptors`, `formatted-output`, `string-formatting` | `format`, `formatting-text`, `fortran`, `fortran-library`, `fortran-package-manager`, `fortran2008` |
| [jeyemhex-regex](https://github.com/jeyemhex/fortran-regex) — Pure Fortran regular-expression matching, splitting and replacement. | `pattern-matching`, `pure-fortran`, `regular-expressions`, `text-processing` | None supplied |
| [string-utf-8](https://github.com/guntherwillems/fortran-string-utf-8) — Manipulate UTF-8 strings as arrays of Unicode code points. | `strings`, `text-processing`, `unicode`, `utf-8` | None supplied |

## Timing

| Package and description | Playground topics | GitHub topics |
| --- | --- | --- |
| [fortime](https://github.com/gha3mi/fortime) — Measure wall-clock and CPU elapsed time, with optional parallel timers. | `cpu-time`, `performance-measurement`, `timing`, `wall-clock` | `cpu-time`, `date-and-time`, `debug`, `elapsed-time`, `fortran`, `fortran-package-manager`, `mpi`, `openmp`, `profile`, `time`, `timer` |

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
| `adaptive-methods` | 11 |
| `adjacency-structures` | 1 |
| `airy-functions` | 2 |
| `approximate-math` | 1 |
| `arbitrary-precision` | 2 |
| `argument-parsing` | 3 |
| `arima` | 1 |
| `arpack` | 1 |
| `array-bounds` | 1 |
| `array-containers` | 1 |
| `array-evaluation` | 1 |
| `array-indexing` | 1 |
| `array-io` | 1 |
| `arrays` | 11 |
| `assertions` | 4 |
| `astrodynamics` | 1 |
| `astronomy` | 1 |
| `atomic-structure` | 1 |
| `atomic-weights` | 1 |
| `autocorrelation` | 1 |
| `automatic-differentiation` | 5 |
| `b-splines` | 1 |
| `base64` | 1 |
| `bdd` | 1 |
| `bessel-functions` | 5 |
| `binary-arithmetic` | 2 |
| `binary-data` | 1 |
| `binary-strings` | 1 |
| `bit-operations` | 2 |
| `bit-shifts` | 1 |
| `bitsets` | 1 |
| `blas` | 4 |
| `blocked-algorithms` | 1 |
| `bootstrap` | 2 |
| `bound-constraints` | 6 |
| `boundary-value-problems` | 1 |
| `brackets` | 1 |
| `c-interoperability` | 3 |
| `calendar-arithmetic` | 2 |
| `carlson-symmetric-forms` | 1 |
| `cartesian-coordinates` | 1 |
| `cattaneo-model` | 1 |
| `character-processing` | 1 |
| `chemistry` | 1 |
| `circulant-matrices` | 1 |
| `codata` | 1 |
| `color-conversion` | 2 |
| `colormaps` | 1 |
| `colors` | 2 |
| `command-line` | 4 |
| `command-line-options` | 1 |
| `command-line-parsing` | 1 |
| `complex-arguments` | 1 |
| `complex-arithmetic` | 3 |
| `complex-step` | 2 |
| `compression` | 3 |
| `computational-geometry` | 1 |
| `configuration` | 3 |
| `configuration-files` | 1 |
| `conservation-laws` | 1 |
| `constitutive-models` | 1 |
| `constrained-optimization` | 6 |
| `constraint-solving` | 1 |
| `contact-mechanics` | 1 |
| `containers` | 10 |
| `control-systems` | 1 |
| `convolution` | 2 |
| `convolutional-networks` | 1 |
| `coordinate-storage` | 1 |
| `coordinate-transformations` | 4 |
| `cosine-transforms` | 1 |
| `coulomb-friction` | 1 |
| `covariance-models` | 1 |
| `cpu-time` | 1 |
| `csr-storage` | 1 |
| `csv` | 1 |
| `cubature` | 2 |
| `curve-approximation` | 1 |
| `curve-fitting` | 3 |
| `cylindrical-functions` | 1 |
| `dae` | 2 |
| `damping` | 1 |
| `data-frames` | 1 |
| `data-structures` | 3 |
| `database` | 1 |
| `databases` | 1 |
| `date-time` | 2 |
| `decimal-arithmetic` | 1 |
| `deep-learning` | 1 |
| `defaults` | 1 |
| `delaunay-triangulation` | 1 |
| `delay-differential-equations` | 1 |
| `dense-output` | 1 |
| `dependency-ordering` | 1 |
| `derivative-free` | 3 |
| `derivatives` | 5 |
| `determinants` | 1 |
| `diagnostics` | 4 |
| `dictionaries` | 3 |
| `differential-equations` | 3 |
| `differentiation` | 4 |
| `dimensional-analysis` | 1 |
| `dimensionality-reduction` | 1 |
| `dirac-equation` | 1 |
| `direct-solvers` | 1 |
| `directed-acyclic-graphs` | 1 |
| `directories` | 1 |
| `distances` | 1 |
| `dot-products` | 1 |
| `drawing` | 1 |
| `dual-numbers` | 2 |
| `duplicate-removal` | 1 |
| `durations` | 1 |
| `dynamic-arrays` | 3 |
| `economics` | 1 |
| `eigenvalue-problems` | 1 |
| `eigenvalues` | 6 |
| `eigenvectors` | 1 |
| `electrical-impedance` | 1 |
| `electrochemistry` | 1 |
| `electrode-kinetics` | 1 |
| `elementary-functions` | 1 |
| `ellipsoids` | 1 |
| `elliptic-integrals` | 1 |
| `encoding` | 1 |
| `equivalent-circuits` | 1 |
| `error-estimation` | 1 |
| `error-handling` | 4 |
| `errors-in-variables` | 1 |
| `event-detection` | 3 |
| `exact-arithmetic` | 1 |
| `exponential-functions` | 1 |
| `exponential-integrals` | 1 |
| `expression-parsing` | 4 |
| `fft` | 2 |
| `fifo` | 1 |
| `file-io` | 13 |
| `filesystem` | 2 |
| `filtering` | 1 |
| `finite-differences` | 5 |
| `finite-elements` | 2 |
| `finite-volumes` | 1 |
| `floating-point` | 3 |
| `floating-point-comparison` | 1 |
| `format-conversion` | 1 |
| `format-descriptors` | 1 |
| `formatted-output` | 2 |
| `formatting` | 3 |
| `forward-mode` | 1 |
| `fourier-transforms` | 3 |
| `frequency-response` | 1 |
| `friction` | 1 |
| `function-evaluation` | 1 |
| `functional-programming` | 3 |
| `gamma-function` | 1 |
| `gamma-functions` | 2 |
| `gauss-hermite` | 1 |
| `gauss-jacobi` | 1 |
| `gauss-kronrod` | 1 |
| `gauss-legendre` | 2 |
| `gaussian-quadrature` | 5 |
| `gaussian-simulation` | 1 |
| `generic-values` | 1 |
| `genetic-algorithms` | 1 |
| `geodesics` | 1 |
| `geodesy` | 2 |
| `geographic-coordinates` | 1 |
| `geometry` | 2 |
| `geostatistics` | 1 |
| `global-optimization` | 3 |
| `gradient-based-optimization` | 2 |
| `gradient-descent` | 1 |
| `gradients` | 1 |
| `graph-partitioning` | 1 |
| `graphs` | 3 |
| `grids` | 3 |
| `growable-arrays` | 1 |
| `hash-tables` | 1 |
| `hdf5` | 1 |
| `heapsort` | 1 |
| `heat-equation` | 1 |
| `heat-transfer` | 1 |
| `helmholtz-equation` | 2 |
| `help-text` | 1 |
| `heterogeneous-data` | 1 |
| `higher-order-derivatives` | 2 |
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
| `ini-files` | 1 |
| `initial-value-problems` | 7 |
| `input-parameters` | 1 |
| `integer-arithmetic` | 3 |
| `integer-factorization` | 1 |
| `integer-formatting` | 1 |
| `integer-vectors` | 1 |
| `integral-transforms` | 1 |
| `interpolation` | 8 |
| `isotopes` | 1 |
| `iterative-solvers` | 5 |
| `jackknife` | 1 |
| `jacobians` | 1 |
| `json` | 3 |
| `json-parsing` | 1 |
| `julian-dates` | 1 |
| `kiss-generator` | 1 |
| `kriging` | 1 |
| `krylov-methods` | 3 |
| `language-bindings` | 12 |
| `lapack` | 5 |
| `lbfgs` | 1 |
| `ldlt-factorization` | 1 |
| `least-squares` | 9 |
| `limited-memory` | 1 |
| `linear-algebra` | 20 |
| `linear-programming` | 1 |
| `linear-systems` | 11 |
| `linked-lists` | 4 |
| `logarithms` | 1 |
| `logging` | 1 |
| `logistic-regression` | 1 |
| `lossless-compression` | 3 |
| `low-rank-approximation` | 1 |
| `lu-factorization` | 2 |
| `machine-learning` | 3 |
| `magic-squares` | 1 |
| `map-filter-reduce` | 1 |
| `markov-chains` | 1 |
| `mathematical-expressions` | 3 |
| `matlab-like` | 1 |
| `matplotlib` | 1 |
| `matrices` | 2 |
| `matrix-exponentials` | 1 |
| `matrix-factorization` | 1 |
| `matrix-free` | 1 |
| `matrix-inverse` | 1 |
| `matrix-inversion` | 1 |
| `matrix-multiplication` | 1 |
| `matrix-operations` | 1 |
| `matrix-ordering` | 2 |
| `matrix-updates` | 1 |
| `matrix-vector-products` | 3 |
| `mcmc` | 1 |
| `medians` | 1 |
| `memory-management` | 1 |
| `memory-mapped-files` | 1 |
| `mersenne-twister` | 1 |
| `meshes` | 1 |
| `messagepack` | 1 |
| `metadata` | 3 |
| `minimax` | 1 |
| `minimization` | 1 |
| `modal-analysis` | 1 |
| `modified-bessel-functions` | 2 |
| `modular-arithmetic` | 1 |
| `morton-codes` | 1 |
| `multidimensional` | 10 |
| `multidimensional-arrays` | 1 |
| `multistep-methods` | 1 |
| `natural-sort` | 1 |
| `nearest-neighbors` | 2 |
| `nearly-linear-problems` | 1 |
| `nelder-mead` | 1 |
| `netcdf` | 2 |
| `neural-networks` | 2 |
| `newton-methods` | 2 |
| `nist` | 1 |
| `nlopt` | 1 |
| `nonlinear-conjugate-gradient` | 1 |
| `nonlinear-equations` | 5 |
| `nonlinear-optimization` | 2 |
| `number-formatting` | 1 |
| `number-parsing` | 1 |
| `number-theory` | 2 |
| `numeric-kinds` | 1 |
| `numerical-methods` | 3 |
| `numerical-testing` | 2 |
| `ode` | 9 |
| `operator-precedence` | 1 |
| `optimization` | 17 |
| `orbital-mechanics` | 1 |
| `order-statistics` | 1 |
| `oscillatory-integrals` | 1 |
| `parser-combinators` | 1 |
| `parsing` | 9 |
| `partial-differential-equations` | 3 |
| `particle-swarm` | 1 |
| `paths` | 2 |
| `pattern-matching` | 5 |
| `pcre2` | 1 |
| `peak-detection` | 1 |
| `pendulum` | 1 |
| `performance-measurement` | 1 |
| `physical-constants` | 2 |
| `physical-properties` | 2 |
| `physical-units` | 1 |
| `physics` | 2 |
| `plotting` | 1 |
| `png` | 3 |
| `pnm` | 1 |
| `point-sets` | 2 |
| `poisson-equation` | 1 |
| `polyline-simplification` | 1 |
| `polymorphism` | 5 |
| `polynomials` | 1 |
| `portability` | 2 |
| `precision` | 2 |
| `prime-numbers` | 1 |
| `principal-component-analysis` | 1 |
| `probability-distributions` | 1 |
| `processes` | 1 |
| `pseudoinverse` | 1 |
| `pseudorandom` | 3 |
| `pure-fortran` | 1 |
| `puzzles` | 1 |
| `python` | 1 |
| `quadratic-programming` | 1 |
| `quadrature` | 8 |
| `quadrature-rules` | 1 |
| `quantum-mechanics` | 1 |
| `quasi-definite` | 1 |
| `quasi-newton` | 2 |
| `quasi-random` | 1 |
| `queues` | 1 |
| `quicksort` | 1 |
| `quoting` | 1 |
| `random-numbers` | 5 |
| `ranking` | 1 |
| `rational-arithmetic` | 2 |
| `real-arithmetic` | 1 |
| `reference-counting` | 1 |
| `regression` | 3 |
| `regular-expressions` | 5 |
| `reproducibility` | 4 |
| `resampling` | 2 |
| `resource-management` | 1 |
| `reverse-communication` | 1 |
| `reverse-mode` | 1 |
| `rgb` | 2 |
| `root-finding` | 4 |
| `rosenbrock-methods` | 1 |
| `row-reduction` | 1 |
| `rpn-calculator` | 1 |
| `runge-kutta` | 5 |
| `sampled-data` | 1 |
| `scalar-functions` | 2 |
| `schroedinger-equation` | 1 |
| `scientific-data` | 3 |
| `searching` | 4 |
| `sequential-quadratic-programming` | 2 |
| `serialization` | 6 |
| `sets` | 2 |
| `shape-preserving` | 2 |
| `shunting-yard-algorithm` | 1 |
| `signal-processing` | 4 |
| `simulated-annealing` | 1 |
| `sine-transforms` | 1 |
| `singular-value-decomposition` | 1 |
| `smoothing` | 2 |
| `sorted-arrays` | 1 |
| `sorting` | 6 |
| `spacecraft-trajectories` | 1 |
| `sparse-linear-algebra` | 2 |
| `sparse-linear-systems` | 1 |
| `sparse-matrices` | 10 |
| `spatial-indexing` | 1 |
| `spatial-statistics` | 1 |
| `special-functions` | 6 |
| `spectral-analysis` | 1 |
| `spherical-harmonics` | 1 |
| `splines` | 5 |
| `sql` | 2 |
| `sqlite` | 2 |
| `standard-library` | 1 |
| `stationary-distributions` | 1 |
| `statistics` | 8 |
| `status-codes` | 1 |
| `stiff-equations` | 3 |
| `stochastic-methods` | 3 |
| `stochastic-processes` | 1 |
| `storage-management` | 1 |
| `stribeck-friction` | 1 |
| `string-formatting` | 1 |
| `strings` | 14 |
| `structured-matrices` | 1 |
| `subprocesses` | 1 |
| `sudoku` | 1 |
| `svd` | 3 |
| `symmetric-systems` | 1 |
| `tabular-data` | 4 |
| `tabulated-data` | 3 |
| `tauchen-discretization` | 1 |
| `terminal-styling` | 1 |
| `test-framework` | 1 |
| `testing` | 1 |
| `text-files` | 1 |
| `text-formatting` | 1 |
| `text-processing` | 14 |
| `text-scanning` | 1 |
| `thermodynamics` | 1 |
| `thread-safe` | 2 |
| `time-series` | 1 |
| `timing` | 1 |
| `toeplitz-matrices` | 1 |
| `tokenization` | 4 |
| `toml` | 2 |
| `topological-sort` | 1 |
| `transformations` | 1 |
| `transpose` | 1 |
| `tridiagonal-matrices` | 1 |
| `truncated-newton` | 1 |
| `trust-region` | 1 |
| `tvd` | 1 |
| `type-conversion` | 4 |
| `type-erasure` | 1 |
| `type-safety` | 1 |
| `uncertainty` | 2 |
| `unicode` | 3 |
| `unique-values` | 2 |
| `unit-conversion` | 1 |
| `unit-testing` | 5 |
| `unsigned-integers` | 1 |
| `utf-8` | 2 |
| `variable-length-strings` | 1 |
| `vector-graphics` | 1 |
| `vector-operations` | 1 |
| `vectors` | 1 |
| `vibration` | 1 |
| `visualization` | 2 |
| `wall-clock` | 1 |
| `warnings` | 1 |
| `water` | 1 |
| `weighted-integrals` | 1 |
| `weno` | 1 |
| `zlib` | 1 |
| `zstandard` | 1 |
