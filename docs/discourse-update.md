I have added several features to the [Fortran playground](https://beliavsky.github.io/fortran-playground/), particularly for comparing compiler behavior and trying libraries.

**Comparing compilers in the browser.** The **Compare compilers** interface lets you select several compilers and compile or run the same program with each, successively. It displays a summary of results and compilation/run times. You can inspect individual results, show all outputs together, or copy the complete report. By default, a compilation failure does not prevent trying the remaining compilers.

**Optional output comparisons.** You can compare outputs exactly, ignore whitespace differences, or use a numeric comparison with absolute and relative tolerances. Numeric comparison accommodates differences such as `D` versus `E` exponents while retaining text and punctuation. This is a convenience for investigating differences, rather than a proof that programs give equivalent results. The Python runner supports these comparisons too.

**External source files.** In Advanced and Compare modes, you can load up to five public Fortran source URLs. They are compiled in the order listed, followed by the program in the editor. This lets a short main program use modules or procedures maintained elsewhere. The Python runner now accepts HTTPS source URLs as well as local files.

**Plotting.** Programs can use Jacob Williams' pyplot-fortran module to save PNG plots, which the hosted and local playgrounds display with download links. The same Fortran code works independently with the library, Python, NumPy, and Matplotlib installed. Compare mode keeps images with each compiler's results; Python runners save returned images to disk. See the [plotting instructions and compiler limitations](https://github.com/Beliavsky/fortran-playground/blob/main/docs/plotting.md).

**Editor improvements.** The editor now provides automatic indentation and deindentation for common Fortran constructs. The default indentation is three spaces, configurable to two or four.

**Links that configure the playground.** Links can select the interface, compilers, example, standard, and preprocessing setting. For example, [this link opens Compare compilers with GNU, Intel, and Flang selected](https://beliavsky.github.io/fortran-playground/?interface=compare&compilers=gfortran,ifx,flang). Another example selects [GNU Fortran, the Fortran 2018 standard, preprocessing, and the arithmetic example](https://beliavsky.github.io/fortran-playground/?compiler=gfortran&standard=2018&preprocess=1&example=01_arithmetic). Opening a link configures the page without running code. Existing links that load source code still work.

There is also an experimental [FPM package playground](https://beliavsky.github.io/fortran-playground/fpm/). Supply a public GitHub package URL and either:

- Write a main program that uses the package.
- Build the package itself.
- Run one of its applications.
- Run its tests.

FPM mode uses gfortran 16.2 by default, with gfortran 17 (experimental), Intel ifx, and LLVM Flang also supported when enabled by the service. Each compiler builds the package and its dependencies from scratch. Five examples demonstrate numerical integration, root finding, interpolation, TOML parsing, and date arithmetic; all five have been checked with the additional compilers. Package compatibility still varies: for example, GNU 17 encounters an internal compiler error in a dependency of the TOML package's upstream tests, although the example using that package works.

GitHub dependencies are supported, but registry dependencies and metapackages are not yet supported. Builds and execution remain subject to sandbox limits, so not every package will work. FPM jobs use a separate service from the ordinary source-code playground.

**FPM from Python.** The hosted runner now accepts package URLs, with optional application/test selection, standard input, and a main program of your own. For example:

```text
python xplayground_run.py --fpm https://github.com/jacobwilliams/PCHIP --action test --compiler ifx
python xplayground_run.py --fpm https://github.com/jacobwilliams/PCHIP --main main.f90 --compilers gfortran ifx flang --diff numeric
```

Selected compilers run successively, with logs, a timing summary, and optional output comparisons. Each submission remains subject to the hosted service's quotas.

**Local compilers and packages.** The repository also includes a command-line runner and browser interface for compilers installed on your own computer:

```text
python xfortran_run.py module.f90 main.f90 --compilers gfortran ifx flang
python xfortran_serve.py --workspace .
```

These now support local FPM projects too. Install FPM and the desired compilers, clone a package, and run these commands from its directory:

```text
python xfortran_run.py --fpm . --action test --compilers gfortran ifx flang
python xfortran_run.py --fpm . --main main.f90 --compilers gfortran ifx --diff numeric
python xfortran_serve.py --workspace . --fpm
```

The local FPM page offers Build, Run, and Test, or an editor for a main program using the package. It supports single- and multi-compiler runs, standard input, debug/release profiles, timings, logs, and optional output comparisons. The editor includes syntax highlighting, automatic indentation, and Format/Check buttons using locally installed fprettify and Fortitude.

Local tools use your installed compilers and your account's permissions, without hosted quotas. Timeouts are configurable and can be disabled. Native FPM manages dependencies and its build cache normally. The [FPM runner instructions](https://github.com/Beliavsky/fortran-playground/blob/main/docs/fpm-runners.md) cover both hosted and local workflows.

The [README](https://github.com/Beliavsky/fortran-playground#readme) explains the interfaces, options, and limitations. Reports of compiler discrepancies, useful small examples, and packages worth testing are welcome.
