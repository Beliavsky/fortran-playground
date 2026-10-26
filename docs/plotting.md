# Plotting with pyplot-fortran

Programs can use Jacob Williams' [pyplot-fortran](https://github.com/jacobwilliams/pyplot-fortran) to generate plots in the hosted and local playgrounds. The playground supplies the pinned module when a source program uses `pyplot_module`; no new interface mode is needed. The library's own API is used, so programs can also run independently.

```fortran
program sine_plot
   use iso_fortran_env, only: dp => real64
   use pyplot_module, only: pyplot
   implicit none
   type(pyplot) :: plt
   real(dp) :: x(101)
   integer :: i, status

   x = [(real(i, dp)/10, i = 0, 100)]
   call plt%initialize(grid=.true., xlabel='x', title='Sine curve', &
      use_oo_api=.true.)
   call plt%add_plot(x, sin(x), label='sin(x)', linestyle='b-')
   call plt%savefig('sine.png', istat=status)
   if (status /= 0) error stop 'Plot generation failed'
end program sine_plot
```

A [complete two-curve example](examples/plot_trig.f90) is also provided. The supplied module uses `real64` arrays. Use `savefig` with a PNG filename in the program's working directory, and leave `wait` at its default `.true.`. `use_oo_api=.true.` selects Matplotlib's noninteractive drawing API; the playground also sets `MPLBACKEND=Agg`. Desktop windows, `showfig`, and LaTeX installations are not provided by hosted execution.

The library generates a Python script and executes it **inside the same execution environment as the Fortran program**. Hosted programs and Python child processes remain in the network-blocked sandbox with the existing CPU, memory, time, and output limits. Plot generation counts toward program execution time. No second hosted job is submitted. Ordinary runs do not import Matplotlib or compile the plotting module.

## Browser results

Generated PNGs appear in a **Plots** section with download links. Compare mode keeps each compiler's images with that compiler's results. Text output and optional text/numeric comparisons remain unchanged; images are not compared.

Only regular static PNG files directly in the run's working directory are collected. Subdirectories, symlinks, SVG, HTML, Python scripts, and PDF files are not returned. Limits are four images and 1 MiB combined PNG data per compiler run, with dimensions at most 4096 per side and eight million pixels. Skipped images produce a note. These limits bound returned results; they do not prevent local programs from creating larger files.

Local runs return only new or modified PNGs. Their original files stay in the selected working directory. FPM custom-main consumers run in a temporary directory; their PNGs are captured before cleanup. FPM package applications/tests run in the package directory, as usual. Files written to another directory are not collected.

## Python runners

```text
python xfortran_run.py docs/examples/plot_trig.f90 --compiler gfortran
python xplayground_run.py docs/examples/plot_trig.f90 --compilers gfortran ifx flang
python xplayground_run.py --fpm https://github.com/jacobwilliams/pyplot-fortran --main docs/examples/plot_trig.f90 --compiler gfortran
```

Returned images are saved under `playground-plots/COMPILER/plot-1.png`, etc. Use `--plot-dir DIRECTORY` to select another destination. The same option works with both runners' `--fpm` modes. Files with those generated names are replaced on subsequent runs; compiler directories keep results separate. Plot filenames and omitted-image notes are printed even with `--terse`.

For local plotting, install NumPy and Matplotlib into the Python environment used to start the runner/server:

```text
python -m pip install numpy matplotlib
python xfortran_serve.py --workspace .
```

The module, helper Python file, and vendored files must accompany a standalone copy of the local tools: copy `fortran_plot.py` and `vendor/pyplot-fortran/` along with the files listed in the README. Local programs run with your normal account permissions.

## Independent compilation

Using upstream's original source:

```text
gfortran -ffree-line-length-none vendor/pyplot-fortran/src/pyplot_module.F90 docs/examples/plot_trig.f90 -o plot_trig
```

Run the resulting executable from your terminal (`.\plot_trig.exe` on Windows, or `./plot_trig` on Linux). Python with NumPy and Matplotlib must be available as `python` on PATH, or pass the Python executable using the library's `savefig(..., python=...)` argument. The executable writes `trig.png`, which can be opened in any image viewer. Other compilers require their own preprocessing option for the upstream `.F90` file. In the playground, the pinned default-real64 source is prepared without preprocessor directives before compilation.

## Hosting and compatibility

Publishing frontend files alone does not enable hosted plotting. Redeploy both the shared ordinary execution service (in the `python-to-fortran-playground` repository) and the separate FPM service. Their runtime images install Matplotlib 3.10.8; rendering needs no network access. Existing compiler toolchain layers are reused. The ordinary API advertises `features.plotting` after redeployment.

With the existing sibling SDK environment and `p2f-owner` secret, run these commands from this repository, then publish the frontend:

```text
..\python-to-fortran-playground\.venv-execution\Scripts\python.exe -X utf8 ..\python-to-fortran-playground\xdeploy_service.py --owner-secret p2f-owner
..\python-to-fortran-playground\.venv-execution\Scripts\python.exe -X utf8 xdeploy_fpm.py --owner-secret p2f-owner
```

The vendored upstream revision and SHA-256 checksums are recorded in [upstream.json](../vendor/pyplot-fortran/upstream.json); the upstream BSD license is retained. All compilers compile the module from source; compiler-specific `.mod` and object files are not shared. Compilation and runtime diagnostics remain visible, with no compiler fallback.

Verified in disposable hosted sandboxes:

| Mode | Compilers returning a valid PNG |
| --- | --- |
| Ordinary source | GNU 16.2, GNU 17 experimental, Intel ifx, LLVM Flang, LFortran |
| FPM custom main, both automatic module provision and upstream package dependency | GNU 16.2, GNU 17 experimental, Intel ifx, LLVM Flang |

**ofort currently cannot run this library.** It fails on a substring operation on a derived-type string component in the pinned upstream module. Its diagnostics are preserved; selecting it does not switch to another compiler. Local Windows checks passed with GNU, ifx, and Flang. Local LFortran compiled the module but encountered an existing linker/environment problem, so its local execution is not verified.

The [source/local validation report](plotting-validation.json) and [eight FPM checks](plotting-fpm-validation.json) record results and timings. These are functional checks, not controlled performance benchmarks. Hosted tests used ephemeral sandboxes and did not deploy either public API. Run the FPM checks again with:

```text
python xverify_fpm.py --plotting-only --compilers gfortran gfortran17 ifx flang --report docs/plotting-fpm-validation.json
```

Use a Python environment containing the Modal SDK and your existing Modal credentials for that verification command. For coarray programs, generate plots on image 1 or use different filenames per image to avoid simultaneous writes to the same PNG.

A final [Compile and Run / Run Again check](plotting-rerun-validation.json) verified PNGs from both fresh executions and retained executables, with no standard-error output. Hosted Matplotlib configuration and font caches are placed in the writable job directory.
