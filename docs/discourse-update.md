I have added several features to the [Fortran playground](https://beliavsky.github.io/fortran-playground/), particularly for comparing compiler behavior and trying libraries.

**Comparing compilers in the browser.** The **Compare compilers** interface lets you select several compilers and compile or run the same program with each, successively. It displays a summary of results and compilation/run times. You can inspect individual results, show all outputs together, or copy the complete report. By default, a compilation failure does not prevent trying the remaining compilers.

**Optional output comparisons.** You can compare outputs exactly, ignore whitespace differences, or use a numeric comparison with absolute and relative tolerances. Numeric comparison accommodates differences such as `D` versus `E` exponents while retaining text and punctuation. This is a convenience for investigating differences, rather than a proof that programs give equivalent results. The Python runner supports these comparisons too.

**External source files.** In Advanced and Compare modes, you can load up to five public Fortran source URLs. They are compiled in the order listed, followed by the program in the editor. This lets a short main program use modules or procedures maintained elsewhere. The Python runner now accepts HTTPS source URLs as well as local files.

**Editor improvements.** The editor now provides automatic indentation and deindentation for common Fortran constructs. The default indentation is three spaces, configurable to two or four.

**Links that configure the playground.** Links can select the interface, compilers, example, standard, and preprocessing setting. For example, [this link opens Compare compilers with GNU, Intel, and Flang selected](https://beliavsky.github.io/fortran-playground/?interface=compare&compilers=gfortran,ifx,flang). Another example selects [GNU Fortran, the Fortran 2018 standard, preprocessing, and the arithmetic example](https://beliavsky.github.io/fortran-playground/?compiler=gfortran&standard=2018&preprocess=1&example=01_arithmetic). Opening a link configures the page without running code. Existing links that load source code still work.

There is also an experimental [FPM package playground](https://beliavsky.github.io/fortran-playground/fpm/). Supply a public GitHub package URL and either:

- Write a main program that uses the package.
- Build the package itself.
- Run one of its applications.
- Run its tests.

FPM mode initially uses gfortran 16.2 and builds from scratch. Five examples demonstrate numerical integration, root finding, interpolation, TOML parsing, and date arithmetic. GitHub dependencies are supported, but registry dependencies and metapackages are not yet supported. Builds and execution remain subject to sandbox limits, so not every package will work.

Finally, the repository now includes a command-line runner and browser interface for **compilers installed on your own computer**:

```text
python xfortran_run.py module.f90 main.f90 --compilers gfortran ifx flang
python xfortran_serve.py --workspace .
```

These local tools do not use the hosted service or its quotas.

The [README](https://github.com/Beliavsky/fortran-playground#readme) explains the interfaces, options, and limitations. Reports of compiler discrepancies, useful small examples, and packages worth testing are welcome.
