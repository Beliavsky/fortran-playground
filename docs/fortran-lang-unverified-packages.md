# Fortran-lang packages not yet verified for the FPM playground

Checked on **2026-10-30** against the [Fortran-lang package index](https://fortran-lang.org/packages/) and this repository's **290-package** verified catalog.

The upstream index data contains **273 projects**. **112** match our verified packages, including confirmed repository renames and recorded GitLab/GitHub mirrors; **161 remain without standalone playground verification**. Of these, **20 have recorded unsuccessful attempts**. For the other **141**, no matching attempt was found in the recorded investigations.

This is an inventory, not a recommendation to precompile every entry. The upstream index also includes scientific applications, command-line tools, code generators, and interfaces needing external software. An unverified entry is not evidence that a package fails to compile. Verification here means a pinned package with a checked consumer example and successful restricted-sandbox cache-reuse test, not testing every upstream feature.

## Recorded unsuccessful attempts

FLAP, StringiFor, FOODIE, FoX, FiNeR and VTKFortran stopped during source preparation, before compilation. GALAHAD, SHTOOLS and the maintained PROPACK author archives exceed the source download limit; Selected offers a separately identified historical SciPy version. FGSL and fdict are now verified using reproducible generated configuration/sources; their earlier blocked investigations remain in their source-review directories. FMM3D compiles but its example fails the bounds-checked execution profile. ParaMonte now passes its pinned 128 MiB operator preparation profile and reaches GNU compilation, but FPM misses a dependency inside a preprocessor include. libNEGF contains test-directory symbolic links rejected before compilation. ELPA source archives contain rejected symbolic links, and PROGRESS root/release archives exceed the compressed download limit; neither reaches compilation. FTorch CPU inference is verified with pinned LibTorch. FortJSON passes all 38 upstream checked CMake tests but awaits GitLab catalog support; parquet-fortran awaits pinned Arrow 24+ native dependencies and FPM manifest adaptation. These are playground preparation/build/run results at the stated pins, not claims that the upstream libraries are generally broken.

| Package | Recorded result | Evidence |
| --- | --- | --- |
| [General-Purpose Fortran](https://github.com/urbanjost/general-purpose-fortran) | The pinned root archive and release tags v3.0.0 and v2.0.0 exceed the unchanged 16 MiB compressed source download limit. Bounded downloads stop before complete archive validation, extraction or compilation; no complete archive hash or compiler failure is claimed. The proposed M_units/M_math example and native dependencies therefore remain unverified. | [Investigation](fpm-candidates/gpf/source-review.json); [tested root commit](https://github.com/urbanjost/general-purpose-fortran/commit/70057310d711ef644460ba61d587052a816a8046) |
| [FLAP](https://github.com/szaghi/FLAP) | Latest root archive contains a symlink; an older root passes extraction but explicitly pins FACE 1455c549ae0c1ead96961ca61a73131d8176b6a4, whose archive also contains a symlink. No archive rules were relaxed; compilation was not attempted. | [Investigation](fpm-candidates/flap/source-review.json); [tested root commit](https://github.com/szaghi/FLAP/commit/17d58bd8c867206baec6f56cbf8156a1afd3cc4a) |
| [StringiFor](https://github.com/szaghi/StringiFor) | Latest root archive contains a symlink; an older root passes extraction but explicitly pins FACE 1455c549ae0c1ead96961ca61a73131d8176b6a4, whose archive also contains a symlink. No archive rules were relaxed; compilation was not attempted. | [Investigation](fpm-candidates/stringifor/source-review.json); [tested root commit](https://github.com/szaghi/StringiFor/commit/019fe9c15a89305b7d2052d9e1bf39ec5f215f7e) |
| [FortJSON](https://gitlab.com/elsi_project/fortjson) | The pinned GitLab source compiles with GNU Fortran 16.2.0 and -fcheck=all; all 38 upstream CMake/CTest tests pass in a network-disabled gVisor operator probe. It is not selected because catalog source preparation and project export currently require GitHub sources or explicitly mapped GitHub mirrors; no usable mirror was found. This is an integration limitation, not a compiler failure. The library writes JSON; a JSON-reading demonstration would be inappropriate. | [Investigation](fpm-candidates/fortjson/source-review.json); [tested root commit](https://gitlab.com/elsi_project/fortjson/-/commit/0126d48f79886ba994612e108117eeb096d9cbc4) |
| [VTKFortran](https://github.com/szaghi/VTKFortran) | The current archive and tags v3.0.0, v2.0.10 and v2.0.9 contain a CONTRIBUTING.md symbolic link. The unchanged archive extractor rejects links before compilation. No compiler failure is claimed. A safe upstream source distribution is required before the proposed mesh-file example can be verified. | [Investigation](fpm-candidates/vtkfortran/source-review.json); [tested root commit](https://github.com/szaghi/VTKFortran/commit/bca0eb0bafe9c59ade72ed7be6f9bc124290c5f0) |
| [fox](https://github.com/andreww/fox) | The pinned head and tagged releases 4.1.2 and 4.1.1 contain symbolic links and are rejected by the unchanged archive extractor before compilation. No compiler failure is claimed. A safe source distribution or a separately reviewed source-preparation facility is needed before an XML round-trip example can be verified. | [Investigation](fpm-candidates/fox/source-review.json); [tested root commit](https://github.com/andreww/fox/commit/6f60cf178d0776b21406303e91f1e6b42ff0f204) |
| [FiNeR](https://github.com/szaghi/FiNeR) | The current source archive and tags v2.3.0 and v2.2.0 contain a CONTRIBUTING.md symbolic link and are rejected by the unchanged source extractor before compilation. No compiler failure is claimed. The current FPM manifest also pins StringiFor; dependencies were not downloaded after root extraction was rejected. | [Investigation](fpm-candidates/finer/source-review.json); [tested root commit](https://github.com/szaghi/FiNeR/commit/e898add18d36456d0bd0d46c02fef51ded741d6d) |
| [parquet-fortran](https://github.com/etempel/parquet-fortran) | The pinned source archive extracts safely. Its documented full Parquet interface requires Apache Arrow >=24.0.0, including libarrow, libarrow-compute and libparquet, and C++20. None of those development packages has a candidate in the current Debian trixie image repositories. The manifest also requires FPM >=0.13 for features/profiles, while the playground uses 0.12, and references a TOML-F fork. Native dependency installation was not attempted from an unpinned external repository; compilation and runtime are not verified. No upstream compiler or Parquet round-trip failure is claimed. | [Investigation](fpm-candidates/parquet-fortran/source-review.json); [tested root commit](https://github.com/etempel/parquet-fortran/commit/f611cbb7da8951c611f9b3f279b2d7bf7038e9d1) |
| [PROPACK](http://sun.stanford.edu/~rmunk/PROPACK) | The maintained author repository head and tags v2.2 and v2.1 exceed the unchanged 16 MiB source download limit, before compilation. The repository includes large saved example output matrices. Selected propack instead verifies the explicitly labeled historical SciPy version; it does not establish that the maintained author sources compile in the playground. | [Investigation](fpm-candidates/propack-author/source-review.json); [tested root commit](https://github.com/rmlarsen/propack/commit/1323a0c53040e49afbbf18efd7f618c5bc779313) |
| [SHTOOLS](https://github.com/SHTOOLS/SHTOOLS) | The current source archive and tags v4.14.1 and v4.14.0 exceed the unchanged 16 MiB source download limit. The source preparer stops before extraction or compilation; no compiler failure is claimed. Complete archive checksums are unavailable because bounded downloads are aborted at the limit. A smaller reproducible source distribution or separately reviewed preparation support is needed. | [Investigation](fpm-candidates/shtools/source-review.json); [tested root commit](https://github.com/SHTOOLS/SHTOOLS/commit/a69878128331554dfef4cdd7d754e1ee7ec8562e) |
| [ParaMonte](https://github.com/cdslaborg/paramonte) | The reviewed 128 MiB operator allowance passes source staging and prepared-bundle extraction. After checksum-guarded submodule compatibility edits and serial external-module declarations, FPM 0.12 accepts the model and GNU Fortran 16.2.0 starts compilation. The build stops around 24% at pm_sampling_base.F90 because USE pm_sysPath appears inside pm_sampling_base.imp.F90 and the required pm_syspath.mod has not been built. This is a remaining FPM dependency-ordering issue involving a preprocessor include, not the former source-size rejection. Runtime and edited-main cache reuse remain unverified. | [Investigation](fpm-candidates/paramonte/source-review.json); [tested root commit](https://github.com/cdslaborg/paramonte/commit/93a9f4f472894115b9f15ac0c68490af719f44fb) |
| [FOODIE](https://github.com/Fortran-FOSS-Programmers/FOODIE) | The current head and tags v0.4.1 and v0.4.0 contain symlinks, including CONTRIBUTING.md and plotting/benchmark assets. The ordinary source preparer rejects links before compilation. No extraction rules were changed, no incomplete package is selected, and no compiler failure is claimed. | [Investigation](fpm-candidates/foodie/source-review.json); [tested root commit](https://github.com/Fortran-FOSS-Programmers/FOODIE/commit/52487d49e1b2b47e2f1136e24fc4bc1a37a5001a) |
| [PSBLAS](https://github.com/sfilippone/psblas3) | Adding the four existing MINRES implementations fixes the earlier undefined-symbol link failure. All 813 library sources and the checked main compile with GNU Fortran 16.2.0, and direct execution as nobody succeeds: solution [1,2,3], three CG iterations, maximum residual 1.7764e-15. However, FPM 0.12 remains CPU-active after producing the executable, without completing its build or writing compile_commands.json. A disposable checkpoint clone also starts another library build rather than providing a completed reusable cache. The operator stopped the original job after observing the post-link stall; this was not a Fortran compiler or numerical failure and not the public service timeout. Ordinary edited-main cache reuse remains unverified, so PSBLAS is not selected. | [Investigation](fpm-candidates/psblas/source-review.json); [tested root commit](https://github.com/sfilippone/psblas3/commit/68ae08adf2f71c9db80b58569ec140b948f626bf) |
| [GALAHAD](https://github.com/ralna/GALAHAD) | The current source archive and tags v5.5.3 and v5.5.2 exceed the unchanged 16 MiB source download limit. Preparation stops before extraction or compilation; no compiler failure is claimed. Complete archive checksums are unavailable because bounded downloads are aborted at the limit. A smaller reproducible source distribution or separately reviewed preparation support is needed. | [Investigation](fpm-candidates/galahad/source-review.json); [tested root commit](https://github.com/ralna/GALAHAD/commit/4275b98e4fdf9af1141d302f04ef944bcda23d32) |
| [libnegf](https://github.com/libnegf/libnegf) | The pinned GitHub archive contains six symbolic links in test directories. The unchanged source extractor rejects links before compilation. This does not establish a compiler or numerical failure. | [Investigation](fpm-candidates/libnegf/source-review.json); [tested root commit](https://github.com/libnegf/libnegf/commit/f34f7e0aebcbc73f3d5bdcbe723a821ded984180) |
| [ELPA](https://gitlab.mpcdf.mpg.de/elpa/elpa) | The declared GitHub mirror archive and both probed 2026.02 release tags contain symbolic links, including a parent-directory link under fdep/test_project and GPU/test source links. The unchanged extractor rejects them before configuration or compilation. No compiler or eigensolver failure is established. | [Investigation](fpm-candidates/elpa/source-review.json); [tested root commit](https://github.com/marekandreas/elpa/commit/6119b4cfcd7422d8493cc0c33e8b8a2264cd81d0) |
| [QMD-PROGRESS](https://github.com/lanl/qmd-progress) | The pinned main archive and release tags v1.3.0 and v1.2.0 exceed the unchanged 16 MiB compressed download limit. Downloads stop before complete archive validation, configuration or compilation; no complete archive hash or compiler failure is claimed. | [Investigation](fpm-candidates/progress/source-review.json); [tested root commit](https://github.com/lanl/qmd-progress/commit/d78a88a905981cb1e91408fdd95fe6f2f2e3a34c) |
| [aenet](https://github.com/atomisticnet/aenet) | The pinned main archive and release tags v2.0.5, v2.0.4 and v2.0.3 exceed the unchanged 16 MiB compressed source download limit. Bounded downloads stopped before complete archive validation, extraction, configuration or compilation; no complete archive hash or compiler failure is claimed. Obtain a smaller pinned author source distribution or separately review a narrowly pinned operator download allowance, then check a tiny energy/force example and cache reuse. | [Investigation](fpm-candidates/aenet/source-review.json); [tested root commit](https://github.com/atomisticnet/aenet/commit/8f35990f5e3dd6cb296b953448cb11694d0cff3d) |
| [FMM3D](https://github.com/flatironinstitute/FMM3D) | The pinned native Fortran library compiles with GNU Fortran 16.2.0, but its Laplace example fails the playground bounds-checked run. Adding the upstream quadrature include directory resolves preparation of Helmholtz sources; adapting two scarray(1) dummy declarations passes the isolated workspace check, but the full run then stops at fexpe(2) with declared extent 1 in lpwrouts.f. A separate local GNU 17 checked run also reports an unallocated disabled dipole buffer argument. The package is deferred under the current checked build profile; these findings do not establish failure with the upstream release build settings. | [Investigation](fpm-candidates/fmm3d/source-review.json); [tested root commit](https://github.com/flatironinstitute/FMM3D/commit/cad293ae9b8ae1218dd8319d459ffcc5f1412875) |
| [Numerical methods in fortran](https://github.com/planelles20/numerical-methods-fortran) | The unchanged quadrature module compiles locally, but rectangle, trapezoidal and Simpson all return 1.111111164 for the integral of 1 on [0,1] with n=10 (expected 1). Each uses step=(b-a)/(n-1) while iterating n intervals. The checked constant-integrand reproducer exits unsuccessfully. Other modules have not been validated; no full-package or GNU 16 sandbox verification is claimed. Ask the author to correct the quadrature interval count, then check polynomial integrals, Newton solves and an ODE example before catalog/cache verification. | [Investigation](fpm-candidates/numerical-methods-fortran/source-review.json); [tested root commit](https://github.com/c-planelles/numerical-methods-fortran/commit/adec2977efac83c3a5297d01cbeaac4ac50e3d11) |

## Remaining projects by category

Each project appears once, under its first upstream category; additional categories are shown in the table. No recorded attempt means no matching record was found in the sources listed below. It does not establish that nobody has ever built the project.

### Data types and containers (1)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [FyCollections](https://bitbucket.org/aradi/fycollections/src/develop) | -- | No recorded attempt |

### Examples and templates (4)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [Blocktran](https://github.com/fortran-gaming/blocktran) | -- | No recorded attempt |
| [Fortran 2018 examples](https://github.com/scivision/fortran2018-examples) | -- | No recorded attempt |
| [Fortran patterns](https://github.com/farhanjk/FortranPatterns) | -- | No recorded attempt |
| [Numerical methods in fortran](https://github.com/planelles20/numerical-methods-fortran) | Numerical projects | Compiled locally; numerical check failed; see investigation above. GNU 16 sandbox not tested. |

### Graphics, plotting and user interfaces (9)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [f03gl](http://www-stone.ch.cam.ac.uk/pub/f03gl/index.xhtml) | Interface libraries | No recorded attempt |
| [fortran-grace](https://github.com/interkosmos/fortran-grace) | Interface libraries | No recorded attempt |
| [fortran-motif](https://github.com/interkosmos/fortran-motif) | Interface libraries | No recorded attempt |
| [fortran-raylib](https://github.com/interkosmos/fortran-raylib) | Interface libraries | No recorded attempt |
| [fortran-sdl2](https://github.com/interkosmos/fortran-sdl2) | Interface libraries | No recorded attempt |
| [fortran-xlib](https://github.com/interkosmos/fortran-xlib) | Interface libraries | No recorded attempt |
| [gtk-fortran](https://github.com/vmagnin/gtk-fortran) | Interface libraries | No recorded attempt |
| [Illustrate](https://github.com/ccsb-scripps/illustrate) | -- | No recorded attempt |
| [PLplot](http://plplot.sourceforge.net) | Interface libraries | No recorded attempt |

### Interface libraries (18)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [arrayfire-fortran](https://github.com/arrayfire/arrayfire-fortran) | -- | No recorded attempt |
| [clfortran](https://github.com/cass-support/clfortran) | -- | No recorded attempt |
| [ELSI](https://gitlab.com/elsi_project/elsi_interface) | -- | No recorded attempt |
| [eophis](https://github.com/IGE-OPERA/eophis) | Numerical projects, Scientific | No recorded attempt |
| [Focal](https://github.com/LKedward/focal) | -- | No recorded attempt |
| [fortran-curl](https://github.com/interkosmos/fortran-curl) | -- | No recorded attempt |
| [fortran-modbus](https://github.com/interkosmos/fortran-modbus) | -- | No recorded attempt |
| [fortran-ncurses](https://github.com/interkosmos/fortran-ncurses) | -- | No recorded attempt |
| [fortran-xmpp](https://github.com/interkosmos/fortran-xmpp) | -- | No recorded attempt |
| [fortyxima](https://bitbucket.org/aradi/fortyxima/src/develop) | Programming utilities | No recorded attempt |
| [LuaF](https://chiselapp.com/user/vadimz/repository/luaf) | -- | No recorded attempt |
| [M_ncurses](https://github.com/urbanjost/M_ncurses) | -- | No recorded attempt |
| [node-fortran](https://github.com/IonicaBizau/node-fortran) | -- | No recorded attempt |
| [node.fortran](https://github.com/IonicaBizau/node.fortran) | -- | No recorded attempt |
| [preCICE](https://github.com/precice/precice) | Scientific | No recorded attempt |
| [SmartSim](https://github.com/CrayLabs/SmartSim) | Numerical projects, Scientific | No recorded attempt |
| [tcp-client-server](https://github.com/modern-fortran/tcp-client-server) | Examples and templates | No recorded attempt |
| [TorchFort](https://github.com/NVIDIA/TorchFort) | Numerical projects, Scientific | No recorded attempt |

### Input, output and parsing (9)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [atomsk](https://github.com/pierrehirel/atomsk) | -- | No recorded attempt |
| [FEconv](https://github.com/victorsndvg/FEconv) | -- | No recorded attempt |
| [FiNeR](https://github.com/szaghi/FiNeR) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [FortJSON](https://gitlab.com/elsi_project/fortjson) | -- | Integration deferred; see investigation above. |
| [fox](https://github.com/andreww/fox) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [jsonff](https://gitlab.com/everythingfunctional/jsonff) | -- | No recorded attempt |
| [parquet-fortran](https://github.com/etempel/parquet-fortran) | -- | Integration deferred; see investigation above. |
| [Serialbox](https://github.com/GridTools/serialbox) | -- | No recorded attempt |
| [VTKFortran](https://github.com/szaghi/VTKFortran) | -- | Preparation blocked; see investigation above. Compiler not reached. |

### Libraries (8)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [caffeine](https://github.com/berkeleylab/caffeine) | -- | No recorded attempt |
| [FLAP](https://github.com/szaghi/FLAP) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [Futility](https://code.ornl.gov/futility/Futility) | Interface libraries, Programming utilities, Characters and strings, Input, output and parsing, Numerical projects, Scientific | No recorded attempt |
| [General-Purpose Fortran](https://github.com/urbanjost/general-purpose-fortran) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [M_CLI](https://github.com/urbanjost/M_CLI) | -- | No recorded attempt |
| [M_history](https://github.com/urbanjost/M_history) | -- | No recorded attempt |
| [OpenCoarrays](https://github.com/sourceryinstitute/OpenCoarrays) | -- | No recorded attempt |
| [The NJOY Nuclear Data Processing System](https://github.com/njoy/NJOY2016) | -- | No recorded attempt |

### Numerical projects (21)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [ElmerFEM](https://github.com/ElmerCSC/elmerfem) | -- | No recorded attempt |
| [ELPA](https://gitlab.mpcdf.mpg.de/elpa/elpa) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [FMM3D](https://github.com/flatironinstitute/FMM3D) | -- | Compiled; checked sandbox run failed; see investigation above. |
| [FOODIE](https://github.com/Fortran-FOSS-Programmers/FOODIE) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [GALAHAD](https://github.com/ralna/GALAHAD) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [HANDE](https://github.com/hande-qmc/hande) | Scientific | No recorded attempt |
| [Incompact3d](https://github.com/xcompact3d/incompact3d) | -- | No recorded attempt |
| [LAPACK](https://github.com/Reference-LAPACK/lapack) | -- | No recorded attempt |
| [libnegf](https://github.com/libnegf/libnegf) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [librsb](http://librsb.sourceforge.net) | Interface libraries, Scientific | No recorded attempt |
| [Los Alamos Grid Toolbox (LaGriT)](https://github.com/lanl/LaGriT) | -- | No recorded attempt |
| [NUFFT](https://cims.nyu.edu/cmcl/nufft/nufft.html) | -- | No recorded attempt |
| [ODEPACK](https://computing.llnl.gov/projects/odepack/software) | -- | No recorded attempt. The selected `odepack` uses the [Nicholaswogan port](https://github.com/Nicholaswogan/odepack), not the original LLNL source linked here. |
| [OpenBLAS](https://github.com/xianyi/OpenBLAS) | -- | No recorded attempt |
| [OpenFFT](http://www.openmx-square.org/openfft) | Interface libraries | No recorded attempt |
| [ParaMonte](https://github.com/cdslaborg/paramonte) | -- | Compilation reached; an FPM dependency-ordering issue in a preprocessor include stopped the build; see investigation above. |
| [PROPACK](http://sun.stanford.edu/~rmunk/PROPACK) | -- | Preparation blocked; see investigation above. Compiler not reached. The selected [propack](https://github.com/scipy/PROPACK) uses the historical SciPy version, not the maintained author sources. |
| [PSBLAS](https://github.com/sfilippone/psblas3) | Data types and containers | Compiled and direct solve passed; FPM completion/cache reuse unverified; see investigation above. |
| [QMD-PROGRESS](https://github.com/lanl/qmd-progress) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [qr_mumps](https://gitlab.com/qr_mumps/qr_mumps) | -- | No recorded attempt |
| [SHTOOLS](https://github.com/SHTOOLS/SHTOOLS) | -- | Preparation blocked; see investigation above. Compiler not reached. |

### Programming utilities (22)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [camfort](https://github.com/camfort/camfort) | -- | No recorded attempt |
| [convert_FORTRAN_case](https://github.com/dav05/convert_FORTRAN_case) | -- | No recorded attempt |
| [Enzyme](https://github.com/EnzymeAD/Enzyme) | -- | No recorded attempt |
| [f90wrap](https://github.com/jameskermode/f90wrap) | -- | No recorded attempt |
| [ffmt](https://github.com/sbryngelson/ffmt) | -- | No recorded attempt |
| [findent](https://sourceforge.net/projects/findent) | -- | No recorded attempt |
| [FORD](https://github.com/Fortran-FOSS-Programmers/ford) | preview | No recorded attempt |
| [Fortitude](https://github.com/PlasmaFAIR/fortitude) | -- | No recorded attempt |
| [FortranCallGraph](https://github.com/fortesg/fortrancallgraph) | -- | No recorded attempt |
| [fparser](https://github.com/stfc/fparser) | -- | No recorded attempt |
| [fpm](https://github.com/fortran-lang/fpm) | -- | No recorded attempt |
| [fprettify](https://github.com/pseewald/fprettify) | -- | No recorded attempt |
| [fypp](https://github.com/aradi/fypp) | -- | No recorded attempt |
| [fytest](https://bitbucket.org/aradi/fytest/src/develop) | -- | No recorded attempt |
| [hipfort](https://github.com/ROCmSoftwarePlatform/hipfort) | -- | No recorded attempt |
| [PSyclone](https://github.com/stfc/PSyclone) | Scientific | No recorded attempt |
| [setup-fortran](https://github.com/fortran-lang/setup-fortran) | -- | No recorded attempt |
| [shroud](https://github.com/LLNL/shroud) | -- | No recorded attempt |
| [SWIG-Fortran](https://github.com/swig-fortran/swig) | -- | No recorded attempt |
| [Tapenade](https://gitlab.inria.fr/tapenade/tapenade) | Numerical projects | No recorded attempt |
| [tree-sitter-fortran](https://github.com/stadelmanma/tree-sitter-fortran) | -- | No recorded attempt |
| [vegetables](https://gitlab.com/everythingfunctional/vegetables) | -- | No recorded attempt. The selected [veggies](https://github.com/everythingfunctional/veggies) is a different repository; no equivalence is assumed. |

### Scientific (67)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [ABINIT](https://github.com/abinit/abinit) | -- | No recorded attempt |
| [ADflow](https://github.com/mdolab/adflow) | -- | No recorded attempt |
| [aenet](https://github.com/atomisticnet/aenet) | -- | Preparation blocked; see investigation above. Compiler not reached. |
| [BandUP](https://github.com/band-unfolding/bandup) | -- | No recorded attempt |
| [BigDFT](https://gitlab.com/l_sim/bigdft-suite) | -- | No recorded attempt |
| [CaNS](https://github.com/p-costa/CaNS) | -- | No recorded attempt |
| [Cantera](https://github.com/Cantera/cantera) | -- | No recorded attempt |
| [Castro](https://github.com/AMReX-Astro/Castro) | -- | No recorded attempt |
| [CFL3D](https://github.com/nasa/CFL3D) | -- | No recorded attempt |
| [CompDam_DGD](https://github.com/nasa/CompDam_DGD) | -- | No recorded attempt |
| [cp2k](https://github.com/cp2k/cp2k) | -- | No recorded attempt |
| [crest](https://github.com/grimme-lab/crest) | -- | No recorded attempt |
| [CTSM](https://github.com/ESCOMP/CTSM) | -- | No recorded attempt |
| [Dalton](https://gitlab.com/dalton/dalton) | -- | No recorded attempt |
| [DAMASK](https://github.com/eisenforschung/DAMASK) | -- | No recorded attempt |
| [DFTB+](https://github.com/dftbplus/dftbplus) | -- | No recorded attempt |
| [DL_POLY_4](https://gitlab.com/ccp5/dl-poly) | -- | No recorded attempt |
| [Elk](https://elk.sourceforge.io) | -- | No recorded attempt |
| [eT](https://gitlab.com/eT-program/eT) | -- | No recorded attempt |
| [fds](https://github.com/firemodels/fds) | -- | No recorded attempt |
| [FLAME](https://gitlab.com/flame-code/FLAME) | -- | No recorded attempt |
| [flexi](https://github.com/flexi-framework/flexi) | -- | No recorded attempt |
| [fluidity](https://github.com/FluidityProject/fluidity) | -- | No recorded attempt |
| [FMS](https://github.com/NOAA-GFDL/FMS) | -- | No recorded attempt |
| [Fortnet](https://github.com/vanderhe/fortnet) | -- | No recorded attempt |
| [freeCappuccino](https://github.com/nikola-m/freeCappuccino) | -- | No recorded attempt |
| [Gemini3D](https://github.com/gemini3d/gemini3d) | -- | No recorded attempt |
| [GEOS-Chem](https://github.com/geoschem/geos-chem) | -- | No recorded attempt |
| [ICAR](https://github.com/NCAR/icar) | -- | No recorded attempt |
| [LATTE](https://github.com/lanl/LATTE) | -- | No recorded attempt |
| [lesgo](https://github.com/lesgo-jhu/lesgo) | -- | No recorded attempt |
| [LFRic apps](https://github.com/MetOffice/lfric_apps) | -- | No recorded attempt |
| [LFRic core](https://github.com/MetOffice/lfric_core) | -- | No recorded attempt |
| [LSDalton](https://gitlab.com/dalton/lsdalton) | -- | No recorded attempt |
| [MESA](https://github.com/MESAHub/mesa) | -- | No recorded attempt |
| [MFC](https://github.com/MFlowCode/MFC) | -- | No recorded attempt |
| [MITgcm](https://github.com/MITgcm/MITgcm) | -- | No recorded attempt |
| [MOKIT](https://gitlab.com/jxzou/mokit) | -- | No recorded attempt |
| [MOM6](https://github.com/NOAA-GFDL/MOM6) | -- | No recorded attempt |
| [MPAS-Model](https://github.com/MPAS-Dev/MPAS-Model) | -- | No recorded attempt |
| [NASTRAN 93](https://github.com/nasa/NASTRAN-93) | -- | No recorded attempt |
| [NASTRAN 95](https://github.com/nasa/NASTRAN-95) | -- | No recorded attempt |
| [Nek5000](https://github.com/Nek5000/Nek5000) | -- | No recorded attempt |
| [NWChem](https://github.com/nwchemgit/nwchem) | -- | No recorded attempt |
| [Octopus](https://gitlab.com/octopus-code/octopus) | -- | No recorded attempt |
| [OFF](https://github.com/szaghi/OFF) | -- | No recorded attempt |
| [OpenMolcas](https://gitlab.com/Molcas/OpenMolcas) | -- | No recorded attempt |
| [OpenSWPC](https://github.com/tktmyd/OpenSWPC) | -- | No recorded attempt |
| [pencil-code](https://github.com/pencil-code/pencil-code) | -- | No recorded attempt |
| [PHANTOM](https://github.com/danieljprice/phantom) | -- | No recorded attempt |
| [qcxms](https://github.com/qcxms/qcxms) | -- | No recorded attempt |
| [Quantum ESPRESSO](https://github.com/QEF/q-e) | -- | No recorded attempt |
| [QUICK](https://github.com/merzlab/QUICK) | -- | No recorded attempt |
| [QUIP](https://github.com/libAtoms/QUIP) | -- | No recorded attempt |
| [SeisSol](https://github.com/SeisSol/SeisSol) | -- | No recorded attempt |
| [siesta](https://gitlab.com/siesta-project/siesta) | -- | No recorded attempt |
| [SNaC](https://github.com/p-costa/SNaC) | -- | No recorded attempt |
| [SNAP](https://github.com/lanl/SNAP) | -- | No recorded attempt |
| [Specfem3D](https://github.com/geodynamics/specfem3d) | -- | No recorded attempt |
| [tinker](https://github.com/TinkerTools/tinker) | -- | No recorded attempt |
| [Tracmass](https://github.com/TRACMASS/tracmass) | -- | No recorded attempt |
| [Truchas](https://gitlab.com/truchas/truchas) | -- | No recorded attempt |
| [UKCA](https://github.com/MetOffice/ukca) | -- | No recorded attempt |
| [Wannier90](https://github.com/wannier-developers/wannier90) | -- | No recorded attempt |
| [WHIZARD](https://whizard.hepforge.org) | -- | No recorded attempt |
| [WRF](https://github.com/wrf-model/WRF) | -- | No recorded attempt |
| [xtb](https://github.com/grimme-lab/xtb) | -- | No recorded attempt |

### Characters and strings (1)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [StringiFor](https://github.com/szaghi/StringiFor) | -- | Preparation blocked; see investigation above. Compiler not reached. |

### Other (upstream index data only) (1)

| Package | Additional categories | Recorded status |
| --- | --- | --- |
| [fortran-machine](https://github.com/mapmeld/fortran-machine) | -- | No recorded attempt. Present in upstream index data under `other`, which is not one of the live browse categories. |

## Already verified under another URL

These entries are excluded from the unverified list. The other verified matches use the same GitHub repository identity (ignoring letter case).

| Upstream listing | Verified playground package | Match |
| --- | --- | --- |
| [sqliteff](https://gitlab.com/everythingfunctional/sqliteff) | [sqliteff](https://github.com/everythingfunctional/sqliteff) | Recorded GitLab upstream / GitHub mirror |
| [erloff](https://gitlab.com/everythingfunctional/erloff) | [erloff](https://github.com/everythingfunctional/erloff) | Recorded GitLab upstream / GitHub mirror |
| [strff](https://gitlab.com/everythingfunctional/strff) | [strff](https://github.com/everythingfunctional/strff) | Recorded GitLab upstream / GitHub mirror |
| [iso_varying_string](https://gitlab.com/everythingfunctional/iso_varying_string) | [iso_varying_string](https://github.com/everythingfunctional/iso_varying_string) | Recorded GitLab upstream / GitHub mirror |
| [fortran-csv-module](https://github.com/jacobwilliams/fortran-csv-module) | [csv-fortran](https://github.com/jacobwilliams/csv-fortran) | Confirmed GitHub repository rename |
| [parff](https://gitlab.com/everythingfunctional/parff) | [parff](https://github.com/everythingfunctional/parff) | Recorded GitLab upstream / GitHub mirror |
| [SciFortran](https://github.com/aamaricci/SciFortran) | [scifortran](https://github.com/SciFortran/SciFortran) | Confirmed GitHub repository rename |
| [quaff](https://gitlab.com/everythingfunctional/quaff) | [quaff](https://github.com/everythingfunctional/quaff) | Recorded GitLab upstream / GitHub mirror |
| [RPNcalc](https://github.com/scivision/rpn-calc-fortran) | [rpn-calculator-fortran](https://github.com/scivision/rpn-calculator-fortran) | Confirmed GitHub repository rename |
| [2DECOMP&FFT](http://www.2decomp.org) | [2decomp-fft](https://github.com/2decomp-fft/2decomp-fft) | Upstream project website / GitHub source |

## Sources and scope

- [Upstream package index data at commit `3f86c713e0d2`](https://github.com/fortran-lang/webpage/blob/3f86c713e0d26d8f45b29baabcce0c549afafbd6/data/package_index.yml).
- [Upstream category definitions at the same commit](https://github.com/fortran-lang/webpage/blob/3f86c713e0d26d8f45b29baabcce0c549afafbd6/data/categories.yml).
- All ten live [browse categories](https://fortran-lang.org/packages/) were checked: they expose 272 distinct project URLs, all present in the pinned index data. The one extra data entry, `fortran-machine`, is explicitly marked above.
- [Selected catalog](../fpm_catalog.json) and [successful validation records](fpm-precompiled-validation.json).
- [Recorded candidate attempts and deferred projects](fpm-candidate-checks.json), [investigation notes](fpm-candidate-notes.md), and the [earlier discovery audit](fpm-discovery-audit.json).
- The original Stanford PROPACK listing is associated with the maintained [author repository](https://rmlarsen.github.io/propack/) for its preparation attempts; the historical SciPy fork is treated separately.
- Project identity is matched by repository URL, with only the explicit rename/mirror matches shown above. Related libraries, forks, rewrites, or individually verified components do not establish verification of a larger upstream project.
- No packages were downloaded for compilation or newly built for this inventory.
