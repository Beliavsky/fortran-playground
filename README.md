# Fortran playground

### Plotting

Programs can `use pyplot_module` and call `savefig` to generate PNGs using [pyplot-fortran](https://github.com/jacobwilliams/pyplot-fortran). The hosted and local source/FPM pages display returned images with download links; Compare mode keeps each compiler's plots separate. Python runners save returned images under `playground-plots/COMPILER/`, configurable with `--plot-dir`. Local plotting requires NumPy and Matplotlib. Hosted plotting requires redeploying both execution services. See [examples, local use, limits, and deployment](docs/plotting.md).

## Open the playground with URL settings

Links can configure the playground without embedding code or running a job. For example, [open Compare compilers](https://beliavsky.github.io/fortran-playground/?interface=compare), or [select GNU Fortran and Intel](https://beliavsky.github.io/fortran-playground/?interface=compare&compilers=gfortran,ifx).

| Query parameter | Supported values / example |
| --- | --- |
| `interface` | `simple`, `advanced`, `compare` |
| `compiler` | `gfortran`, `gfortran17`, `ifx`, `flang`, `lfortran`, `ofort` |
| `compilers` | Comma-separated compiler IDs for Compare, e.g. `gfortran,ifx,flang` |
| `example` | Filename stem from `site/examples/`, e.g. `01_arithmetic` |
| `standard` | `default`, `1995`, `2003`, `2008`, `2018`, `2023`, subject to compiler/service support |
| `preprocess` | `1` to enable, `0` to disable |

For example: `?compiler=gfortran&standard=2018&preprocess=1&example=01_arithmetic`. With no explicit interface, `compilers` selects Compare, while `compiler`, `standard`, or `preprocess` selects Advanced. Simple keeps its GNU defaults and reports incompatible query settings as ignored. In Compare, `compiler` chooses the compiler displayed in **Options for**, while `compilers` chooses the checked compilers.

Settings are applied on page load, override corresponding defaults, and leave unspecified choices alone. Compiler capabilities are checked after connecting. Unavailable compilers and unsupported settings produce visible messages; if every requested comparison compiler is unavailable, select one before running. Invalid values and duplicate recognized parameters are ignored with a message. Other query parameters, including existing `owner=1` links, retain their existing behavior.

Existing `#code=...&interface=...` shared-code links still work. When combined with query settings, the shared fragment determines the source, interface, preprocessing, and image settings; query compiler and standard choices apply when compatible with that interface. Opening a link never compiles or runs code. These query settings apply to the ordinary playground; FPM URL settings are not included yet.

The separate [FPM package playground](https://beliavsky.github.io/fortran-playground/fpm/) supports a custom main program using a package, or the package's own Build, Run, and Test actions. GNU Fortran 16.2.0 remains the default; a compiler selector also offers GNU 17 experimental, Intel ifx, and LLVM Flang when the service has built and verified their separate images. It builds from scratch in its own sandbox service. See [FPM usage, limits, and deployment](docs/fpm-mode.md), including the GNU 17 test-drive compiler limitation; the service must be deployed and its URL configured before the page can submit jobs.

[Open the playground](https://beliavsky.github.io/fortran-playground/) ? [GitHub repository](https://github.com/Beliavsky/fortran-playground) ? [Python-to-Fortran playground](https://beliavsky.github.io/python-to-fortran-playground/)

Explore Fortran in your browser with short examples, an editable source pane, and a choice of compilers or an interpreter. No local compiler is needed to use the site. The playground submits Fortran directly to the shared Python-to-Fortran execution service; it does not translate or submit Python.

## Using the playground

FPM packages can also be used from the command line: `python xplayground_run.py --fpm GITHUB_URL --action test` uses the hosted package service, while `python xfortran_run.py --fpm DIRECTORY --action test` uses installed compilers and FPM. The main local package page, started with `python xfortran_serve.py --workspace DIRECTORY --fpm`, shares the hosted interface and catalog but downloads and compiles locally from scratch. Install its source-preparation dependency with `python -m pip install tomli-w==1.2.0`. The secondary **Local FPM projects** page retains directory-based operation and compiler comparison; open it from the main page or use `--fpm-projects`. See [hosted/local FPM runner and browser instructions](docs/fpm-runners.md) for custom main programs, comparisons, targets, limits, and working directories.

1. Choose an example, load a local Fortran file, or write your own program.
2. Select an available compiler or interpreter and, optionally, a language standard and compiler options.
3. Click **Compile** to build without execution, or **Compile and Run** to build and execute.
4. Edit the program and repeat. Use **Download Fortran** to save the source, or **Copy share link** to share it.

The editor provides syntax coloring, line counts, undo, and navigation to recognized source errors. A plain-text fallback remains available if the enhanced editor cannot load. Wide screens show the editor and results side by side; narrow screens stack them. Execution controls stay visible above the source pane.

### Simple, Advanced, and Compare compilers interfaces

Use the **Interface** menu to choose **Simple**, **Advanced**, or **Compare compilers**. Ordinary visits default to Advanced; educational forks can set `interfaceMode: 'simple'` in [`site/config.mjs`](site/config.mjs) to start with Simple. Shared-code links default to Simple and can explicitly request Advanced or Compare compilers, overriding the site's configured default. Reloading follows the link's mode when shared code is present, otherwise the configured default.

Simple uses **GNU Fortran with compiler defaults**, with preprocessing off. Its primary **Run** button compiles and executes the program. Examples, file loading, downloading, sharing, Format, Stop, and error navigation remain available. Compiler/standard/flag selectors, Compile-only, Run Again, Fortitude Check, and experimental quick-fix controls are hidden. **Advanced options** switches to the full interface to access those controls.

Program output fills the results area in Simple until a compilation or execution failure reveals the Compilation pane. A subsequent successful run hides that pane again. Switching interfaces preserves source and results. Entering Simple resets the compiler, standard, preset, warnings, fast-math, and preprocessing settings; execution-setting changes invalidate retained builds. Returning to Advanced keeps the current settings rather than restoring hidden older choices. Interface switching is disabled during a job or connection attempt.

If the service does not advertise gfortran, Simple disables Run and explains how to switch to Advanced to select another available compiler. It never substitutes another compiler silently.

### Comparing compilers

Choose **Interface → Compare compilers** to compile or run the same program with several compilers. GNU Fortran is checked initially; check other available tools or use **Select all available**. The editor, ordered external source files, stdin, formatting, and Fortitude checks work as in Advanced mode.

**Compile** checks/builds with each selected compiler without executing. **Compile and Run** builds and runs with each one, sequentially in checkbox order. ofort checks syntax or interprets the source. Each submitted compiler counts as a separate job under the existing usage limits; the number of jobs appears beside the action buttons. Unsupported settings show a reason beside the compiler and produce **SKIP** without submitting a job. A compiler failure does not prevent later compilers from running unless **Stop on first failure** is checked. **Stop** cancels the current job and skips all remaining submissions. Authentication or quota errors stop further submissions automatically.

Standard, preset, warnings, fast math, preprocessing, and coarray image count are shared settings. Use **Options for** to edit additional options separately for each compiler; switching that dropdown preserves each compiler's additional options. A setting unsupported by a compiler skips that compiler rather than silently changing the request. The service remains the authority on allowed options.

The summary table reports **Total**, **Compile**, **Run**, and **Other**, all in seconds. Total measures client elapsed time from submission through receipt of the result, including polling. Other is Total minus the reported compilation and execution times, covering waiting, service overhead, and transfers. Missing stages appear as `-`; an interpreter can still have an Other time. These hosted times include startup and resource sharing and are not controlled compiler benchmarks.

Select a compiler's name in the table to inspect its build log, version, and output in the existing results panes. Every job in a comparison uses the source, external snapshots, stdin, and options captured at its start. If the editor or settings change during a comparison, earlier results remain available and are marked as such; their errors are not placed on the changed editor source. Automatic quick fixes and retained **Run Again** executables are disabled for comparisons. Use Advanced for Run Again.

Enable **Show all outputs** above the timing table to display a section for every selected compiler, in submission order, below the editor. Each section shows its status, version, program output, and a collapsible compilation log. Successful build logs start collapsed; failed jobs start with their logs expanded. Empty program output is distinguished from an operation that did not run. Standard output and standard error are shown separately with whitespace preserved. The editor expands when the individual output panes are hidden; Fortitude checks can still be shown. This view updates as results arrive, submits no additional jobs, and is saved as a browser preference. The individual-compiler view remains the default.

**Copy all results** copies the current comparison's compiler versions, settings, effective flags, timings, diagnostics, and program output as plain text. It includes failed and skipped entries and marks results retained from an earlier source/settings snapshot. If clipboard access is unavailable, a selected text area lets you copy the report manually. The report does not include source code, stdin, or owner credentials; use **Copy share link** to share the source separately.

Share links preserve the combined source, interface, preprocessing, and coarray image count. Compiler checkbox selections, additional options, other compiler settings, and stdin are not embedded. Opening a comparison link never submits jobs; the recipient chooses compilers and settings before running. The comparison interface uses the existing backend API and needs no backend redeployment.

### Compilers, standards, and execution

The service reports which tools are available: GNU Fortran, Intel Fortran, LLVM Flang, LFortran, and the experimental ofort interpreter. The selected tool's version appears below its menu; results retain the version used for that particular job. Older services can show ?version unavailable? while still allowing compilation.

The updated service pins the default **GNU Fortran (stable)** to **16.2.0**, using the official GCC container image by immutable digest. Advanced mode also offers **GNU Fortran 17 (experimental, 2026-10-18)** when its separately verified snapshot image is available. Simple mode continues using the stable `gfortran` choice. Actual versions are reported by the deployed service; these labels do not upgrade an older backend automatically.

The experimental compiler uses the ID `gfortran17` in the Python runner and options files:

```powershell
python xplayground_run.py example.f90 --compilers gfortran gfortran17 --O 3 --list
```

GNU 17 shares the GNU option vocabulary and portable mappings, but has its own executable, image, helper-module cache, and retained executables. The snapshot is downloaded from GNU's release server and verified against a pinned SHA-512 checksum during the image build. It is never updated during a user job. Snapshot failures do not silently fall back to stable GNU.

Redeploy the shared backend with `.venv-execution\Scripts\python.exe -X utf8 xdeploy_service.py --owner-secret p2f-owner`, then publish the frontends. The first deployment builds the snapshot compiler from source and rebuilds GNU helper modules; it can take substantially longer than later deployments, which reuse cached compiler layers. `--without-gnu17` skips the optional snapshot image. If that image cannot be built or verified, GNU 16.2 remains the default and GNU 17 stays unavailable. GNU 16.2 build/verification failures stop deployment. Deployment verification checks compiler identity, preprocessing and options, diagnostics, helper reuse, and retained execution. LLVM Flang is pinned to 23.1.5 for experimental coarray support; Intel, LFortran, and ofort keep their existing compiler installations.

The **Standard** menu offers **Compiler default** and years verified by the service. Unsupported years are disabled. GNU rejects extensions beyond the selected standard; Intel reports conformance warnings. The **Strict** option adds diagnostics without choosing a standard year. Standard flags apply only to submitted code, while helpers retain their own fixed build options. GNU and Intel year flags are checked during service image construction and cached; Flang and LFortran currently offer only **Compiler default**.

**Run Again** reuses a successfully compiled executable for up to five minutes. It starts a fresh isolated process without recompiling. Source or option changes, reconnecting, failed compilation, and expiration invalidate the retained build. Files from a previous run are not carried over, and reruns count toward service usage limits. Retained builds are private to the session.

With **ofort**, **Compile** becomes **Check syntax**, and **Compile and Run** becomes **Run**. Compiler flags and **Run Again** are disabled. Each Run starts a fresh interpretation using `ofort --fast`; Check syntax uses `ofort --fast --check`. Both use compact-array fast mode. Only standalone source is supported; compiled `python_mod` helpers cannot be linked into ofort. Its execution detects reads of uninitialized variables that its syntax check may not detect. Unsupported features can be rejected, and failures never silently switch tools.

### Preprocessing

In Advanced mode, **Enable preprocessing** supports macros and conditional compilation. It is off by default and changes only the submitted source's compiler flags; helper libraries keep their fixed build options. The source filename remains `input_p.f90`. Toggling the option invalidates retained executables.

| Compiler | Preprocessing flag |
| --- | --- |
| GNU Fortran | [`-cpp`](https://gcc.gnu.org/onlinedocs/gfortran/Preprocessing-Options.html) |
| Intel ifx on the Linux service | [`-fpp`](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2026-0/fpp.html) |
| LLVM Flang | [`-cpp`](https://flang.llvm.org/docs/FlangCommandLineReference.html) |
| LFortran | [`--cpp`](https://docs.lfortran.org/en/usage/) |

For example, enable preprocessing and run:

```fortran
#define VALUE 42
program preprocessing_example
   implicit none
#if VALUE > 0
   print *, VALUE
#else
   print *, 0
#endif
end program preprocessing_example
```

The checkbox depends on the service's advertised options. ofort does not offer preprocessing. If a shared link requests it but the compiler or service does not support it, compilation is blocked with an explanation; choose a supporting compiler or turn the option off. A new request is never silently sent without required preprocessing. Older services continue working with preprocessing off because the frontend omits the new option in that case.

This feature requires redeploying the shared backend as well as publishing the frontend. Image verification tests preprocessing with macros, conditionals, and cached helpers. Format and Fortitude Check still receive the original source, without running the compiler's preprocessor. The playground remains a single-file environment; it does not upload additional include files or provide arbitrary include paths or command-line macro definitions. Use `#define` in the source for small experiments.

### External source files

In **Advanced** mode, enter a direct raw-code URL in **External source URL**, then press **Load**. For example:

```text
https://jblevins.org/mirror/amiller/luxury.f90
```

The loaded files can supply modules or external procedures used by the program in the editor. **Load does not compile or run code.** The preview shows the downloaded snapshot; its URL and SHA-256 hash are displayed. **Compile** or **Compile and Run** submits the loaded snapshots from top to bottom, followed by the editor code, using the selected compiler and options. Press **Load** again to refresh the snapshot, or **Remove** to remove that row. **Add another**, beside the last row, adds another URL box (up to five). Put modules before files that use them. Empty rows are ignored; every nonempty row must be loaded successfully. Changing the URL blocks compilation until it is loaded or removed. Switching to Simple mode removes all external sources.

Up to five UTF-8 free-form source files are supported. All external sources, editor code, and provenance comments together must fit the existing **100 KB** source limit. They are concatenated into one compilation unit; preprocessing macro state carries across the boundary. Additional files, include files, external libraries, and fpm packages are not downloaded automatically. Supply supporting modules/procedures, rather than another main program. GitHub file-view pages return HTML; use their raw-source URL.

**Download Fortran** saves `playground_combined.f90` containing all loaded sources and the editor code. Share links also embed all sources, so opening them does not need another download. Loading, removing, or changing external code invalidates Run Again. Formatting and Fortitude checks apply only to the editor code. Recognized compilation errors are mapped to the external filename or the editor's line numbers; automatic quick fixes are disabled for combined source.

External loading requires the updated hosted backend. The service fetches public HTTPS URLs with bounded sizes, redirects, and timeouts; private-network destinations are rejected. Loading has a separate limit of 30 downloads per address per ten minutes and at most two concurrent downloads. It does not consume execution jobs. Compilation and execution retain the existing sandbox isolation and job quotas.

### Editor indentation

Automatic indentation is enabled by default with **three spaces** per level. The **Indent** menu offers 2, 3, or 4 spaces; **Auto-indent** switches automatic indentation on or off. Both preferences are saved in this browser, apply in every interface, and are not included in share links. Changing a preference does not rewrite source or invalidate a compiled executable.

Enter after a recognized loop, block IF, SELECT, program, module, or procedure indents the next line. Closing statements align with their opening statement; ELSE/ELSE IF align with IF, and CASE branches indent under SELECT. Tab inserts spaces or indents selected lines; Shift+Tab unindents. Escape leaves the editor. These controls also work in the plain-text fallback.

Loading or pasting source preserves its indentation. The indentation helper recognizes comments, quoted strings, and common continued statements. Ambiguous constructs such as labeled DO loops and multiple statements separated by semicolons retain existing indentation rather than guessing. This is editing assistance, not a Fortran parser or syntax check.

**Format** uses the selected width, even when Auto-indent is off. Widths other than three require the updated execution service; until it is redeployed, automatic indentation works at any offered width but Format is disabled at two or four spaces with an explanatory message. Redeploy the shared backend and publish the frontend to enable all formatter widths.

### Formatting, checks, and diagnostics

| Control | Behavior |
| --- | --- |
| **Format** | Uses fprettify for whitespace-only formatting with the selected indentation width (three spaces by default). One undo restores the previous source. Requires the enhanced editor and service formatting support. |
| **Check** | Runs Fortitude without fixes or execution. Uses its default rules and Fortran 2018 target, independently of the selected compiler standard. Findings appear in a separate panel. |
| **Go to first error** | Navigates to the first recognized source error, including in the plain-text fallback. |
| **Fix error** | Applies a supported experimental syntax repair as one undoable edit; see below. |

The Fortitude pane is hidden initially so Program output and Compilation fill the results column. Clicking **Check** reveals it immediately with a progress message; findings, successful checks, and errors remain visible afterward. **Hide checks** reclaims the space without discarding the results. Clicking **Check** again reveals the pane and starts a new check.

Formatting is not syntax validation or automatic repair. Failed, cancelled, or stale formatting results never replace the source. Fortitude checking preserves source, compiler output, and any retained executable. Hosted formatting and checking use the shared service and its limits.

Recognized errors in the submitted `input_p.f90` source receive a red line background and gutter marker; reported columns are underlined. Hover to read the message, or click a marker to navigate. Source or option changes and new compilations clear stale markers. Warnings and helper-file errors remain in the compilation log without source markers. GNU, Intel, LLVM Flang, and LFortran diagnostic formats are recognized; other diagnostics still appear in the log.

### Limits

- Source limit: **100 KB** (100,000 UTF-8 bytes).
- Output limit: **200 KB per output stream**.
- Program input can be supplied before execution; there is no interactive terminal.
- Programs run in isolated environments without network access.
- Compilation, execution, formatting, and checking require an explicit button click.

## Sharing code with a link

Click **Copy share link** to create a link containing the current source, selected interface mode, preprocessing setting, and coarray image count when enabled. If clipboard access is unavailable, a selected text field lets you copy it manually. Anyone opening the link sees the code in the editor and chooses when to compile or run it. The link does not include compiler selections, other compiler flags, results, or session tokens.

The public format is:

```text
https://beliavsky.github.io/fortran-playground/#code=URL_ENCODED_FORTRAN
```

This format, including existing generated links, opens Simple. Append `&interface=advanced` to request Advanced, or `&interface=simple` to select Simple explicitly. **Copy share link** writes the selected mode explicitly. Percent-encode the complete source before appending options; literal ampersands in the program must be encoded as `%26`.

Append `&preprocess=1` to request preprocessing. It opens Advanced automatically when the interface is unspecified. An explicit `interface=simple` combined with `preprocess=1` is rejected because Simple always turns preprocessing off. Copied links preserve preprocessing when enabled; it defaults to off when absent. `preprocess=0` explicitly requests off. Other compiler settings are not included.

For example, [open a short Hello program](https://beliavsky.github.io/fortran-playground/#code=print%20*%2C%20%22Hello%22%0Aend%0A).

Documentation sites and scripts can generate links without using the copy button. Encode the complete UTF-8 source, including newlines, using JavaScript's `encodeURIComponent`:

```javascript
const source = 'program hello\n   print *, "Hello!"\nend program hello\n';
const link = 'https://beliavsky.github.io/fortran-playground/#code='
  + encodeURIComponent(source);
```

Or generate the same format in Python:

```python
from urllib.parse import quote

source = 'program hello\n   print *, "Hello!"\nend program hello\n'
link = 'https://beliavsky.github.io/fortran-playground/#code=' + quote(source, safe='')
```

The source is embedded after `#`; opening the link does not fetch an external source file or require a storage service. The fragment is not sent to GitHub Pages in the page request. Anyone with the link can read the code, and the link can remain in browser history. Explicit compilation, execution, formatting, or checking sends source to the execution service as usual.

Empty, incorrectly encoded, or oversized shared source and invalid interface options are rejected with a message. Changing to another shared-code fragment in the same tab asks before replacing nonempty input or changing its interface. Cancelling preserves both. Shared links cannot be loaded while a job or connection attempt is running; retry the link afterward. Opening a shared link never automatically submits a job. Long links may be truncated by browsers, messaging tools, or forums; sharing is best suited to short examples even though the source limit remains 100 KB.

### Generate a page of links from a repository

Use [`xplayground_links.py`](xplayground_links.py) to create a standalone HTML page from a directory of Fortran programs. It requires Python only and works with a local checkout of any repository; the source files do not have to be in this playground's repository.

```powershell
# Generate links for this playground's examples:
python xplayground_links.py site/examples --output playground-links.html

# Scan another repository, including its subdirectories:
python xplayground_links.py ../my-fortran/examples --recursive --output docs/index.html --title "My Fortran examples"
```

The generator scans `.f90`, `.f95`, `.f03`, and `.f08` files case-insensitively. Links appear in relative-path order, with filenames displayed to distinguish examples in different subdirectories. A file's optional `! Example:` comment supplies its link label; otherwise the filename stem is used. UTF-8 source, including Unicode and line endings, is embedded directly in the link. A UTF-8 byte-order mark is removed.

Empty, non-UTF-8, unreadable, and oversized files are skipped with warnings. Links longer than 8,000 characters also produce warnings because some sites truncate long URLs. The generator does not compile programs or resolve dependencies: choose short standalone programs that need no interactive input or external files.

Open the generated HTML file locally or publish it through GitHub Pages. Visitors use the existing playground, so publishing the link page requires no Modal account or separate execution service. Runs still use the playground's shared service and its limits. To target a separately hosted playground supporting the same fragment format, pass `--playground-url https://example.org/fortran-playground/`.

Regenerate the page whenever source files change. To automate this, add a step to your repository's existing Pages build before its artifact is uploaded, adjusting the paths to match your repository:

```yaml
- name: Generate playground links
  run: python path/to/fortran-playground/xplayground_links.py examples --recursive --output _site/playground-links.html
```

Copy the script into your repository or make this playground's checkout available at the path shown. It uses only the Python standard library. The generated HTML is self-contained and contains snapshots of all included source; publish only code you intend to share.

## Examples

The starter collection contains **14 language demonstrations** and **six numerical calculations**. The core programs are standalone, print labeled results, and include a suggested change to try. Additional examples demonstrate coarrays and plotting; the plotting example uses the supplied pyplot-fortran module. FortranTip adaptations retain source URLs and original attribution in comments.

| Language demonstrations | Numerical calculations |
| --- | --- |
| Arithmetic and formatted output | Descriptive statistics and least-squares fitting |
| Loops and decisions | Bisection root finding |
| Precision and rounding | Trapezoidal integration |
| Array construction and slicing | Runge-Kutta integration of an ODE |
| Whole-array expressions | One-dimensional heat diffusion |
| Reductions and locations | Complex-step differentiation |
| Masks and selection | |
| Matrices and column-major order | |
| Allocatable arrays | |
| Internal functions | |
| Optional and keyword arguments | |
| Elemental functions | |
| Derived types and particle motion | |
| Strings and internal I/O | |

### Adding or changing examples

Add, edit, or delete single-file Fortran programs directly in [`site/examples/`](site/examples/). Supported extensions are `.f90`, `.f95`, `.f03`, and `.f08`, case-insensitively. Subdirectories are not scanned, and each filename stem must be unique.

Files appear in filename order. Use prefixes such as `01_` and `02_` to control the order. The first example loads on an ordinary page visit; a shared-code link loads its embedded source instead.

Set the dropdown label with an optional Fortran comment:

```fortran
! Example: Arrays: construction and slicing
```

Without that comment, the label comes from the filename, with a numeric prefix removed and underscores or hyphens replaced by spaces. Programs should run without interactive input or external libraries. Every current dropdown example works with a local gfortran installation; none requires `python_mod`.

[`xexamples.py`](xexamples.py) generates the ignored `site/examples.generated.mjs` catalog. Edit the Fortran files rather than that generated module. The site builder regenerates it before versioning assets; `npm test` regenerates it before frontend tests. Push changes to `main` to publish through GitHub Actions. Example changes require no backend deployment.

For local preview, `python xserve.py` generates the catalog at startup and whenever the browser requests it. Refresh after changing examples. With another static server, run `python xexamples.py` after changes first. An empty examples directory leaves the editor blank and disables example loading.

## Python command-line client

[`xplayground_run.py`](xplayground_run.py) submits Fortran source from local files or raw HTTPS URLs to the hosted execution service and displays the compiler/version, build diagnostics, program output, and timings. Keep `fortran_output_diff.py` and `fortran_plot.py` beside the script when copying it elsewhere. It uses only Python's standard library; no local compiler, Modal account, or Modal credentials are required. Execution is remote and uses the same shared resources and server-enforced quotas as the website.

```powershell
# Compile and run with gfortran:
python xplayground_run.py hello.f90

# Compile and run sequentially with several compilers:
python xplayground_run.py hello.f90 --compilers gfortran ifx flang lfortran

# Stop after the first compilation or execution failure:
python xplayground_run.py hello.f90 --compilers gfortran ifx flang --fail-fast

# Show program output, diagnostics, and the final timing summary:
python xplayground_run.py hello.f90 --compilers gfortran ifx --terse

# Include the submitted source once before compiler results:
python xplayground_run.py kinds.f90 solver.f90 main.f90 --compilers gfortran ifx --list --terse

# Combine a module and its caller, in the order supplied:
python xplayground_run.py kinds.f90 solver.f90 main.f90 --compilers gfortran ifx

# Download a module and combine it with a local main program:
python xplayground_run.py https://jblevins.org/mirror/amiller/luxury.f90 main.f90 --compilers gfortran ifx --list

# Other supported options:
python xplayground_run.py example.f90 --compiler lfortran --preprocess
python xplayground_run.py example.f90 --standard 2018 --preset debug --warnings
python xplayground_run.py example.f90 --compile-only
python xplayground_run.py --help
```

Use `--stdin-file data.txt` to supply UTF-8 program input to `read(*,*)`:

```powershell
python xplayground_run.py example.f90 --stdin-file data.txt --compilers gfortran ifx
```

The same input is supplied to each compiler's run, followed by end-of-file. Input is limited to 100 KB of UTF-8 text; an optional BOM is removed and line endings are normalized. `--stdin-file` cannot be combined with `--compile-only`. The service must advertise stdin support; older services report an error before any job is submitted.

In the browser, expand **Program input (stdin)** to type input or load a text file. **Run Again** uses the current input without recompiling. **Compile**, formatting, and checks omit program input. Input is kept only in the current page and is omitted from share links; it is sent to the service when running. Empty input produces immediate end-of-file. For coarray programs, read input on image 1 and distribute values to other images.

Source arguments can mix local paths and raw HTTPS URLs in compilation order, with modules before their callers. Each URL is downloaded once into client memory before contacting the execution service; all selected compilers receive the same combined snapshot. Downloads use verified HTTPS on port 443, timeouts, at most five redirects, and bounded sizes. HTTP URLs, URL credentials/fragments, compressed responses, HTML pages, empty content, NUL bytes, and invalid UTF-8 are rejected. Use raw-code links rather than GitHub file-view pages. Sources are not downloaded by the backend, and downloading does not consume Modal jobs.

Normal output includes the final URL, requested URL if redirected, SHA-256 hash, and combined-source line range for each remote source. The hash covers UTF-8 source after removing an optional BOM and normalizing line endings, before adding any missing final newline. Remote-source separator comments include the URL and hash, so `--list` includes provenance even with `--terse`. All source text and separator comments count toward the existing **100 KB** combined limit. Repository cloning, fpm dependencies, include files, and libraries are not fetched automatically. `--stdin-file` still accepts local files only.

Put source paths and URLs before `--compilers`; that option takes a list of compiler names. The default is gfortran, with compiler defaults and preprocessing off. Available options also include `--fast-math` and `--timeout SECONDS` (300 seconds per compiler by default). Compile-only performs a syntax check when selecting ofort. All compiler choices and requested options are checked against the service session before any jobs are submitted.

### Coarrays

**Performance:** All coarray images in a job share a CPU reservation of **0.5 physical cores** and a CPU limit of **1 physical core**, regardless of whether you select one, two, or four images. Increasing the image count does not increase the CPU allocation. Multiple images can therefore take longer than one image because they compete for the same CPU allowance and add communication and synchronization overhead. Timings can also vary between runs and sandbox hosts. Coarray support is intended for exploring language features and checking program behavior; use a suitably provisioned multicore machine to measure parallel speedup.

In Advanced mode, select **Coarrays: Off, 1 image, 2 images, or 4 images**. Only counts verified for the selected deployed compiler are enabled. Off is the default, and Simple mode resets coarrays to Off.

| Compiler | Coarray implementation |
| --- | --- |
| GNU Fortran | `-fcoarray=single` for one image; `-fcoarray=lib` with the native `-lcaf_shmem` library for two or four |
| Intel ifx | `-coarray=single`, or `-coarray=shared -coarray-num-images=N` with Intel MPI shared-memory communication |
| LLVM Flang 23.1.5 | Caffeine runtime prepared, but the exchange probe currently fails; coarray controls remain disabled |
| LFortran 0.66.0 | Experimental `--coarray=true` with its own Caffeine/GASNet shared-memory runtime |
| ofort | Unavailable |

Flang and LFortran coarrays are incomplete language implementations. The browser and runner display an experimental note when using them. Passing the deployment probe establishes basic image-to-image exchange, not support for every coarray feature. LFortran 0.66 passed sandbox exchange tests with 1, 2, and 4 images and both two-image examples, including Run Again. It may print `STOP` for each image on normal termination; these messages are preserved in program output and do not by themselves indicate failure.

The pinned Flang 23.1.5 can run the identify-images example, but rejects references to coarray variables with a compiler "not yet implemented" error. It therefore advertises no coarray image counts. Its runtime wiring and deployment probe are in place for a future compiler upgrade; ordinary Flang compilation remains available. Caffeine installation failures likewise leave ordinary compilation available and coarrays disabled for that compiler. See [Caffeine](https://github.com/BerkeleyLab/caffeine) and [LFortran's Caffeine tests](https://github.com/lfortran/lfortran/blob/v0.66.0/ci/test_caffeine.sh).

The examples **Coarrays: identify images** and **Coarrays: exchange values around a ring** demonstrate image numbering, synchronization, and coindexed reads. Loading one switches to Advanced, selects stable GNU, and requests two images. If the service has not verified two-image execution, a clear error blocks submission; select an available count. Their `! Coarray images: 2` comment supplies this example setting. Output is ordered using synchronization and `FLUSH`; arbitrary multi-image programs may print in a different order on each run.

The runner supports the same feature:

```powershell
python xplayground_run.py site/examples/22_coarray_exchange.f90 --compiler gfortran --images 4 --list
python xplayground_run.py site/examples/22_coarray_exchange.f90 --compilers gfortran ifx --images 2 --terse
python xplayground_run.py site/examples/22_coarray_exchange.f90 --compiler lfortran --images 2 --terse
```

An options file may include `"common": {"images": 2}`. `--images` overrides that default. Every selected compiler must advertise the requested count before any jobs are submitted. Copy share link preserves enabled images using `&images=1`, `&images=2`, or `&images=4`; these links require Advanced and select stable GNU when loaded. As with preprocessing, an unsupported request is blocked rather than silently dropped. Old code links still open Simple by default.

All images execute inside **one sandbox and count as one job**, sharing its existing CPU, memory, wall-time, output, and concurrency limits. For GNU, the backend sets `GFORTRAN_NUM_IMAGES` to the requested count, a **64 MB** shared-memory segment, and a bounded image-restart limit. For Intel, it initializes the installed MPI environment, sets `FOR_COARRAY_NUM_IMAGES`, selects the `shm` fabric, disables CPU pinning, and enables MPI wait mode. Flang and LFortran launch their executable with `GASNET_PSHM_NODES` set to the bounded image count and a 64 MB maximum GASNet segment per image. Intel multi-image jobs use Modal's isolated VM runtime so Intel MPI receives a real Linux CPU topology; other jobs use gVisor. External network access remains blocked. Run Again preserves the compiled build's image count; changing the selector invalidates it. These runs demonstrate parallel language behavior, not parallel speedup under the current CPU allocation. No arbitrary environment variables or raw coarray flags are accepted from clients.

Redeploy the shared service to activate support. Deployment compiles and executes an image-to-image exchange separately for 1, 2, and 4 images in each available GNU, Intel, Flang, and LFortran image **inside a network-blocked sandbox with the same runtime, CPU/memory settings, and Unix limits as user jobs**. Only successful counts are advertised in the session's `coarray_images` catalog. A failed probe disables the corresponding counts and leaves ordinary compilation available. There are no extra probes or sandbox launches during normal user jobs. Caffeine and GASNet are built once in cached compiler-specific image layers; the first deployment takes longer. Local example tests exercise both examples with one GNU image; deployment verifies multi-image runtime behavior. See the [GNU shared-memory coarray documentation](https://gcc.gnu.org/onlinedocs/gfortran/Shared-memory-Coarrays.html) and [Intel coarray options](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2025-1/coarray-qcoarray.html).

### Additional compiler options

In Advanced mode, the **Additional options** field to the right of Standard accepts space-separated arguments such as `-O2 -Wall -fcheck=all` for GNU Fortran or `-O2 -warn all` for Intel. The supported choices for the selected compiler appear below the field. Entries are kept separately for each compiler during the page session. ofort has no additional options. Entering Simple clears these entries; shared links do not include them.

The effective user-code flags appear below the controls. Additional options supplement the preset, standard, and checkboxes. Conflicting choices, such as Debug's `-O0` plus `-O2`, are rejected; select Default or remove the conflicting option. Identical repeated flags are accepted. Standards use the existing Standard selector. Helpers retain their fixed build options.

The Python runner accepts the same options through a JSON file, using separate strings for each command argument:

```json
{
  "gfortran": ["-O2", "-Wall", "-fcheck=all"],
  "ifx": ["-O2", "-warn", "all"],
  "flang": ["-O2"]
}
```

```powershell
python xplayground_run.py primes.f90 xprimes.f90 --compilers gfortran ifx --options-file compiler-options.example.json
```

Copy and edit [compiler-options.example.json](compiler-options.example.json) for your experiments. The file selects additional options; `--compiler` or `--compilers` selects which tools run. A missing compiler entry means no additional options. Normal output shows effective user-code options; `--terse` suppresses them. All requested compilers' options are validated against the session catalog before the first job is submitted.

Both clients use the service's advertised allowlist, and the server validates again before launching a sandbox or charging job quota. Options that name files, change output locations, load plugins, or alter helper compatibility are not accepted. Each entry is limited to 32 arguments of at most 128 characters. Validation adds no sandbox launches or compiler probes. Selected optimization and checking flags can affect compilation and execution times. Supported choices build on the [GNU Fortran documentation](https://gcc.gnu.org/onlinedocs/gfortran/Debugging-Options.html) and [Intel compiler documentation](https://www.intel.com/content/www/us/en/developer/articles/guide/porting-guide-for-ifort-to-ifx.html).

This feature requires redeploying the shared execution service from the `python-to-fortran-playground` repository with `python xdeploy_service.py`, then publishing the frontend. Against an older service, the field is disabled and the runner rejects nonempty additional options before submitting jobs.

### Portable options in the Python runner

Use `--optimization 0|1|2|3` (aliases `--O` and `-O`), `--bounds-check`, and `--backtrace` to request comparable settings across compilers:

```powershell
python xplayground_run.py primes.f90 xprimes.f90 --compilers gfortran ifx --O 3 --bounds-check --backtrace
python xplayground_run.py example.f90 --compilers gfortran ifx flang --optimization 2
```

The optional `common` object in an options file supplies defaults for these settings:

```json
{
  "common": {"optimization": 3, "bounds_check": true, "backtrace": true},
  "gfortran": ["-Wall"],
  "ifx": ["-warn", "all"]
}
```

Command-line values override `common`; `--no-bounds-check` and `--no-backtrace` turn off the corresponding common request. They do not remove flags supplied by a preset or compiler-specific entry. Optimization must be an integer from 0 through 3, and the two check settings must be JSON booleans. Compiler-specific arguments supplement the translated common settings; conflicting values are rejected rather than overriding one another. For example, `--preset debug --O 3` conflicts with Debug's `-O0`.

Mappings come from the service catalog:

| Request | GNU Fortran | Intel ifx | LLVM Flang |
| --- | --- | --- | --- |
| `--O 0` through `--O 3` | `-O0` through `-O3` | `-O0` through `-O3` | `-O0` through `-O3` |
| `--bounds-check` | `-fcheck=bounds` | `-check bounds` | Unavailable |
| `--backtrace` | `-fbacktrace` | `-traceback` | Unavailable |

Optimization requests also have approximate mappings for LFortran and ofort:

| Request | LFortran | ofort |
| --- | --- | --- |
| `--O 0` | Default mode (no extra flags) | Default interpreter mode |
| `--O 1`, `--O 2`, `--O 3` | `--fast` | Default interpreter mode |

The runner prints a note for every approximate or ignored optimization request, including with `--terse`. LFortran's `--fast` relaxes strict standard compliance and does not distinguish levels 1, 2, and 3. ofort ignores numbered optimization requests because its interpreter has no equivalent. Notes and mappings come from the service catalog. A LFortran `--O 0` request conflicts with an explicitly supplied `--fast`.

Comparable options do not guarantee identical optimization or diagnostics. Unsupported bounds checks and backtraces remain errors. If any selected compiler or an older service lacks a requested mapping, the runner names it and stops before submitting any jobs. False check settings request no flags and need no mapping. The existing `--warnings`, `--preprocess`, `--fast-math`, and `--preset` controls remain available. Redeploy the shared backend to advertise the new mappings and notes; translating them requires no additional API requests or sandbox launches.

### Multiple source files

Multiple files are **concatenated into one submitted free-form source**, in argument order, with a newline and a `! --- Source: filename ---` comment at each boundary. Put modules before code that uses them. This is not separate compilation: all files must form one complete program and use compatible free-form syntax and compiler options. Preprocessor macro state extends across file boundaries. Additional include files, object files, external libraries, and per-file compiler options are not uploaded or resolved.

Files must contain UTF-8 text. UTF-8 byte-order marks are stripped, line endings are normalized, and a final newline is supplied when needed. The combined source, including separator comments and added newlines, must fit the service's 100,000-byte limit. Duplicate input paths and empty files are rejected.

The compiler sees `input_p.f90`. The client prints the combined-source line ranges and maps recognized GNU/Flang/LFortran and Intel diagnostic references back to original filenames and lines. Original diagnostic text is preserved. Other diagnostic formats and locations pointing to a separator comment remain in their original form.

### Private owner access

The shared service's daily limit applies to all public users combined. Its owner can configure a private key to bypass the daily and per-address quotas. Owner jobs are counted separately and do not consume public job allowance. The two-job concurrency limit, session ownership/expiry, source and option validation, sandbox isolation, time limits, and output limits still apply. Ordinary users keep the existing limits.

Configure this once in the `python-to-fortran-playground` backend repository:

1. Generate a random key on your own machine with `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Keep it private; do not put it in Git, an options file, a URL, or a share link.
2. In the [Modal dashboard](https://modal.com/secrets), create a secret named `p2f-owner` containing a variable named `P2F_OWNER_KEY` with that value. The key must contain 32 to 256 characters.
3. Redeploy using `.venv-execution\Scripts\python.exe -X utf8 xdeploy_service.py --owner-secret p2f-owner`. Use `--owner-secret p2f-owner` on subsequent deployments too, or set the nonsecret deployment variable `P2F_OWNER_SECRET_NAME=p2f-owner`. Forks need no owner secret unless they enable this feature. The secret is injected only into the API function, using [Modal Secrets](https://modal.com/docs/guide/secrets), and never into job sandboxes or build images.
4. Publish the frontend changes. Visit [the playground with owner controls](https://beliavsky.github.io/fortran-playground/?owner=1), open **Owner access**, enter the key, and submit normally. Bookmark this URL for future use. Owner controls are hidden on ordinary visits; `?owner=1` only reveals the controls and still requires the private key. Share links omit this parameter. The password field holds the key only in the current page; reloading clears it. **Clear owner key** restores public access. Keys are checked for every submitted job; a wrong key rejects the job rather than falling back to public access.

For the Python runner:

```powershell
python xplayground_run.py primes.f90 xprimes.f90 --compilers gfortran ifx --owner
```

`--owner` prompts for the key without echoing it. For repeated runs, supply `P2F_OWNER_KEY` in your process environment instead; `--owner` is still required. The key goes only in an HTTPS job-request header, never in source, output, command-line arguments, or job JSON. Polling and cancellation use the ordinary session token. An older or unconfigured service rejects owner mode before submission. Rotate the key by updating the Modal secret and redeploying; remove owner-secret configuration and redeploy to disable the exemption. No public counters need to be reset, even if today's allowance is already exhausted.

### Results, cancellation, and service configuration

Add `--list` to print the exact combined source submitted to every compiler, once before the compiler results, between `=== Submitted source ===` and `=== End submitted source ===` markers. The listing includes filename separator comments for multiple files, with no added line numbers, so it can be copied as source. It reflects the normal UTF-8 BOM removal, line-ending normalization, and final newline; it is the source before compiler preprocessing. Listing stays visible with `--terse` and does not change compilation, execution, or job count.

Use `--terse` to keep compiler-labeled PASS/FAIL results, program stdout and stderr, compilation diagnostics (including warnings on successful builds), and the final timing summary. It suppresses the service URL, source-range listing, submission messages, compiler versions, routine successful build logs, and individual timing lines. Diagnostic mappings to original source files, service errors, and `--fail-fast` stopping messages remain visible.

Each compiler gets a separate sequential job with a fresh build environment; files within a combined program do not consume separate jobs. Compilation or program failures are reported, and by default the client continues to the next requested compiler. Add `--fail-fast` to stop after the first compilation or execution failure, keeping the completed results and returning exit code 1. It displays outputs individually without assuming differences imply incorrect results. HTTP/service failures, including quota errors, always stop further submissions regardless of `--fail-fast`. Submissions are never automatically retried, since a request may have been accepted before a connection failure.

The final summary lists completed compilers with **Total**, **Compile**, **Run**, and **Other** times, all in seconds. Total is the client elapsed time, including submission and polling; Compile and Run are the times reported by the service. Other is Total minus Compile and Run, covering network requests, polling delays, queueing, and service overhead. A dash indicates an unavailable time, such as Run for a compile-only job or a compilation failure. A skipped run counts as zero when calculating Other; if an expected timing is missing, Other is also a dash. For an ofort run without a compilation stage, Other is Total minus Run and Compile displays a dash. For ofort compile-only jobs, Compile measures the syntax check.

Exit codes are **0** for all successful jobs, **1** for any completed job failure, **2** for local input/options or service failures, and **130** for Ctrl+C. On timeout or interruption, the client attempts to cancel a known pending job. Cancellation cannot be confirmed if the service is unreachable; a submission interrupted before its ID is received cannot be cancelled by the client. The total per-compiler timeout includes submission and polling, while an individual HTTP request is bounded to at most 30 seconds (five seconds for best-effort cancellation).

By default, the client reads `site/service.json` beside the script, independently of the current working directory. To use an independently hosted service, supply its HTTPS origin and a frontend origin permitted by that backend:

```powershell
python xplayground_run.py hello.f90 --service-url https://execute.example.org --origin https://my-site.example.org
```

The Origin header identifies the configured frontend origin; it does not authenticate a site owner or bypass workload limits. The client requests a short-lived application session token and never needs the owner's Modal credentials. Keep experiments small; public-service access is subject to its current shared allowances and availability.

## Optional output comparison

Output diffing is **off by default**. In either browser's comparison interface, select **Compare outputs** after or before running compilers. Choose Ignore whitespace (the initial mode), Exact, or Numeric-aware, and optionally select a reference compiler. The default reference is the first successful complete execution. Changing comparison controls uses captured results and never submits another job. Copy all results includes the comparison report when enabled. Raw program output is preserved, and no display rounding is used for comparisons.

Both Python runners accept the same options:

```powershell
python xplayground_run.py main.f90 --compilers gfortran ifx --diff
python xfortran_run.py main.f90 --compilers gfortran flang --diff exact
python xfortran_run.py main.f90 --compilers gfortran ifx --diff numeric --diff-atol 1e-12 --diff-rtol 1e-6 --diff-reference gfortran
```

`--diff` alone ignores whitespace, including line wrapping. Exact mode normalizes CRLF/CR line endings only and retains final-newline differences. Numeric-aware comparison retains text, punctuation, quoted strings, and token order; it recognizes decimal numbers with E/D exponents, complex components, and T/F versus .TRUE./.FALSE. Both tolerances default to **zero**. Two integer tokens must agree exactly, including values larger than binary floating-point can represent. Other numeric pairs match when `abs(a-b) <= max(atol, rtol * max(abs(a), abs(b)))`; decimal arithmetic avoids binary rounding during comparison. Signed zeros compare equally in numeric mode.

Reports distinguish Exact match, Formatting only, Numeric match, Within tolerance, Different, and Not comparable, and identify the first differing line/token or unequal token counts. Stdout alone is compared; compiler logs and stderr remain separate. Failed/cancelled/timed-out runs, missing executions (including compile-only jobs), and known truncated streams are not comparable. Numeric mode flags NaNs, infinities, and `*****` overflow fields for inspection. To bound work in the browser, comparisons are limited to 1,000,000 characters per stream and numeric mode to 20,000 tokens, 2,000 digits per number, and exponent magnitude 2,000; larger cases are reported as Not comparable. Numeric-aware comparison is a text heuristic, not a general parser for arbitrary output or a proof of program correctness. Printed timings and random values are not removed automatically. CLI exit codes continue to reflect compilation/execution success; output differences are reported separately.

## FPM package feasibility

The FPM page also offers a [searchable catalog of 83 precompiled GNU Fortran 16 packages](docs/fpm-precompiled.md) in 32 categories: numerical methods, machine learning, databases, geodesy, plotting, data formats, dates, containers, files, and command-line utilities. Each has a one-line description and an editable example. Catalog and service edits preserve compatible compiled libraries; other compilers and custom package URLs retain clean builds.

Each catalog selection links to its pinned upstream source. You can download your edited main as a Fortran file or an FPM project ZIP with local build tools, dependency locks, and recorded patches/settings. Package sources download on the first local run; the ZIP README explains setup. Downloads do not submit a compiler job or require the execution service.

The [FPM feasibility audit](docs/fpm-feasibility/README.md) found five packages that build and run short consumer programs within the configured public sandbox limits. It includes pinned package revisions, tested main programs, measurements, and a callback compatibility limitation. The separate [FPM mode](docs/fpm-mode.md) builds on these examples and also supports package Build, Run, and Test actions; it requires its own service deployment.

## Local compiler tools

The independent local tools use **installed gfortran, gfortran17, ifx, LLVM Flang, LFortran, and/or ofort**, with Python's standard library for source-file and existing-directory package operation. The local catalog page additionally needs `tomli-w`. They do not contact the hosted playground, require Modal, or consume hosted quotas. Source-file mode accepts local files; package mode uses installed FPM, which may download dependencies normally. See [moving the local tools](docs/fpm-runners.md#moving-the-local-tools) for the files needed by each interface, including the shared frontend and catalog preparation modules. Source-only command-line use needs `xfortran_run.py`, `fortran_output_diff.py`, and `fortran_plot.py`; plotting also needs the vendored module, NumPy, and Matplotlib.

### Local command-line runner

```powershell
python xfortran_run.py kinds.f90 solver.f90 main.f90 --compilers gfortran ifx --O 3
python xfortran_run.py main.f90 --preset debug --stdin-file input.txt --list --terse
python xfortran_run.py module.f90 main.f90 --compile-only
python xfortran_run.py main.f90 --compilers gfortran gfortran17 ifx flang lfortran ofort
python xfortran_run.py main.f90 --compiler flang --compiler-path "flang=C:\Programs\LLVM\bin\flang.exe"
```

Supply local source files in dependency order, before `--compilers`. Each source is compiled separately, then its objects are linked into a complete program; Compile-only includes linking but omits execution. Filenames and extensions are preserved, including preprocessing behavior for `.F90`. Each compiler gets an isolated temporary object/module directory, which is removed afterward. Versions, diagnostics, program output, and Total/Compile/Run/Other times are reported. A failure normally allows the next compiler to proceed; `--fail-fast` stops further submissions. Ctrl+C stops the active process. These tools run with your permissions, and programs can read/write files and use the network.

Compiler executables are discovered on `PATH`. GNU 17 discovery tries `gfortran17`, `gfortran-17`, then `gfortran`, accepting only a version reporting GNU 17. Thus a single installed GNU 17 can appear under both GNU choices; installing this tool does not install a second compiler. Flang discovery tries `flang`, `flang-new`, and versioned `flang-23`, `flang-22`, or `flang-21`. Use an Intel compiler/developer terminal when ifx needs its environment initialized, or override any executable with `--compiler-path "gfortran=C:\path\to\gfortran.exe"` (substitute the chosen compiler name). Overrides work in both the runner and server. They do not initialize compiler environments. On Windows, LFortran also needs a suitable Microsoft linker environment; a GNU `link.exe` earlier on PATH is not a substitute. Initialize Visual Studio or your Intel setup before starting the tools. On Windows, ifx receives native Windows options; on Linux it receives Unix options. Missing compilers are reported, without substituting another compiler.

Portable settings include `--O 0..3`, `--standard`, `--preset`, `--warnings`, `--bounds-check`, `--backtrace`, `--preprocess`, and `--fast-math`. Positive optimization levels map to `--fast` for LFortran and ofort, with a note explaining that numbered levels are unavailable. The verified explicit standard selections are 2018 for LLVM Flang and 2023 for LFortran/ofort; Compiler default works for comparisons without requiring equivalent standard switches. Other common settings without a supported mapping produce an ERROR for that compiler while comparisons continue by default. Native flags remain available in the options file or browser extra-argument boxes. The options file supports common settings and per-compiler argument lists, or separate compilation/linking lists:

```json
{
  "common": {"optimization": 2, "warnings": true},
  "gfortran": {"compile": ["-fcheck=bounds"], "link": []},
  "ifx": []
}
```

Pass it with `--options-file local-options.json`. A compiler's plain argument list is used in both compilation and linking; object entries separate these phases. Common command-line settings override common options-file settings; additional compiler flags follow the common flags. Use native flags for each operating system and absolute paths for additional include/library directories, since compilation runs in a temporary build directory. Output/object/module paths, response files, and the compile-only switch are managed by the runner.

**ofort is an interpreter:** it receives the source files in the supplied order, without generating objects or linking. `--compile-only` (or the browser's Compile button) uses `ofort --check`. Multiple sources are combined temporarily for this syntax check, with line numbers referring to the combined source; mixing fixed and free source forms in one syntax check is rejected. During an interpreted run, Compile time is unavailable and Run time includes parsing and execution; Other time is still reported. ofort argument lists apply to the interpreter, and separate linker arguments are rejected. Its language support differs from the native compilers.

In source-file mode, programs run in the current directory unless `--cwd PATH` is given. `--stdin-file` supplies text followed by EOF. Default timeouts are 120 seconds for compilation/linking and 30 seconds for execution; set `--compile-timeout` or `--run-timeout`, with 0 meaning unlimited. `--max-output-mb` sets captured output per stream per process (default 4 MiB); excess output is drained and marked as truncated. Coarray/MPI launchers are not managed. FPM packages use the separate `--fpm` mode described in [FPM runner instructions](docs/fpm-runners.md).

### Local browser interface

```powershell
python xfortran_serve.py --workspace C:\fortran\test
```

This starts a loopback server and opens the session URL in your browser. Type or paste directly into the empty Fortran pane to create an in-memory `main.f90` source. The page also lists Fortran files within the chosen workspace. Add sources, arrange their compilation order with Up/Down, and edit their in-memory copies. **New program** creates a temporary source buffer containing a Hello World program. Original sources are never overwritten by the editor; **Download current source** saves an edited copy through the browser. Fortran INCLUDE searches include original source directories and the workspace as well as temporary source/module directories.

Choose **Single compiler** or **Compare compilers**, then Compile or Compile and Run. Both interfaces include Fortran syntax highlighting and line numbers using locally bundled CodeMirror 5 (MIT license in `local_site/editor-vendor/LICENSE`); no CDN or npm installation is needed. The interface supports common settings, additional native compiler arguments, stdin text or file loading, configurable timeouts, Stop, failure handling, per-compiler output/build logs, a timing table, and Copy all results. Comparisons run sequentially from one snapshot. Programs use the workspace as their working directory; their own file operations can modify it. The browser editor accepts UTF-8 sources, with a 16 MiB request bound; use the command-line runner for larger jobs. Submission, connection, and server errors appear in the status message and affected compiler results instead of leaving them marked QUEUED. After updating these local tools, restart `xfortran_serve.py` and reload its printed session URL.

Both local interfaces use the hosted editor's auto-indentation, with **3 spaces** by default, selectable 2/3/4-space indentation, automatic dedenting, and Tab/Shift+Tab support. Preferences are saved in the browser. **Format** runs installed `fprettify` on the current source using the selected indentation width; **Check** runs installed `fortitude` and opens a checks pane with clickable findings and editor markers. Editing or switching sources clears old findings. **Clear** and formatting can be undone with Ctrl+Z in the enhanced editor. Put both tools on PATH before starting the server, just as with compilers. These actions run against temporary copies of the selected source, using the tools' defaults and any applicable user configuration; they never rewrite workspace source files. Editor tool requests have a 30-second process timeout. No hosted service is used.

The local bundle contains copies of `site/editors.mjs`, `site/indentation.mjs`, and `site/output_diff*.mjs` so it can be moved to an independent project. Keep those copies synchronized when changing editor or comparison behavior; `tests/local_ui.mjs` verifies they match.

Use `--no-browser` to open the printed URL yourself, `--port 0` for an automatically chosen port, or `--compiler-path COMPILER=PATH` for executable overrides. Use the full printed session URL, including its fragment, when opening a new tab. The page retains its temporary session token in per-tab session storage so reloading works, and removes the fragment when storage is available. Restarting the server creates a new session; open its new printed URL. Ctrl+C shuts down the server and cancels active work.

The service binds only to `127.0.0.1`, checks Host and Origin, requires an unpredictable session token for API access, and restricts source-file browsing to the selected workspace. It does not expose an endpoint for saving arbitrary workspace files. Local program execution is **not sandboxed**; use it for code you choose to run on your machine. Do not expose this server through a public proxy or port forward.

## Local development

You need Python and Node/npm to build and preview. Install gfortran to run the compiler tests; a compiler is not needed merely to preview the frontend.

```powershell
npm ci
python xeditor.py
python -m pip install matplotlib==3.10.8 tomli-w==1.2.0
npm test
python -m unittest discover -s tests -v
python xserve.py
```

Open <http://127.0.0.1:8766/>. The `/run/` path redirects to the main page. Use port 8766 for the service's allowed local origin.

This is a static preview. Execution, formatting, and checking still use the hosted service configured in `site/service.json`, consume the owner's Modal resources, and share its usage limits. Do not publish the Python preview server as an execution sandbox.

### Testing

Install the Python test dependencies with `python -m pip install matplotlib==3.10.8 tomli-w==1.2.0`. The FPM catalog and project-download tests require `tomli-w` to write prepared package manifests.

```powershell
npm test
python -m unittest discover -s tests -v
npm run test:fixes
python xsite.py
```

- **JavaScript tests** cover editor behavior, diagnostics, quick fixes, formatting, shared links, and UI interactions without submitting hosted jobs.
- **Python tests** cover catalog generation, asset versioning, and frontend structure. With Node and gfortran on PATH, they compile and run every generated dropdown example twice: with compiler defaults, then with Fortran 2018 conformance, warnings as errors, and runtime checks. Expected labeled output is checked with floating-point tolerances.
- **Quick-fix compiler tests** use real gfortran diagnostics to verify repairs and refusals.
- **Command-line client tests** use mocked API requests for validation, polling, cancellation, quotas, and sequential compilers. A local gfortran test checks concatenated module/main sources. These automated tests submit no hosted jobs.
- **The site build** generates `_site/` with content-versioned asset URLs.

[`tests/example_results.json`](tests/example_results.json) specifies expected output for every example. Add or update its entry when changing a program. A new dropdown example without expected results fails the compiler test. Numerical references use known roots, exact solutions, or independently derived discrete formulas. Compiler builds use temporary directories; runs have closed stdin and timeouts. Compiler-dependent tests are skipped locally when their required tools are absent. The Pages workflow installs the tools before running them.

To save the quick-fix compiler report:

```powershell
node xcheck_fixes.mjs --report reports\quick_fixes_gfortran.json
```

## Experimental syntax quick fixes

After a failed gfortran build, **Fix error** appears when the first source error has a supported repair. Its tooltip and the note above the panes describe the edit. Clicking applies one undoable change, clears stale markers, and invalidates the retained executable. It never compiles or runs automatically. Use **Ctrl+Z** to undo, then compile when ready.

Quick fixes require the enhanced editor because the plain-text fallback cannot guarantee native undo. Ordinary diagnostics and navigation remain available in the fallback.

| Rule | Repair and scope |
| --- | --- |
| `print-format-comma` | Inserts a missing comma after a quoted PRINT format, using a matching gfortran diagnostic. |
| `closing-unit-name` | Corrects an END PROGRAM, END MODULE, END SUBROUTINE, or END FUNCTION identifier. Cross-checks the diagnostic against a conservative scope scan and preserves the opening name's capitalization. |
| `use-before-implicit-none` | Moves an adjacent block of complete USE statements before IMPLICIT NONE, preserving text, indentation, and inline comments. Supports explicit programs, modules, and simple procedures. |
| `missing-contains` | Inserts CONTAINS before the first complete procedure definition in an explicit program or module. Requires a matching diagnostic and balanced conservative scan. |

The detector refuses stale source and ambiguous or unsupported constructs. The USE-ordering rule refuses intervening comments, continuations, directives, and interface scopes. The missing-CONTAINS rule refuses existing CONTAINS, interfaces, derived-type definitions, implicit main programs, nested internal procedures, and unsupported or incomplete constructs. Closing-name detection supports simple procedure headers and balanced IF/DO constructs, while refusing interfaces, continuations, multiple statements, and unsupported or incomplete scopes. Other compiler adapters are not implemented.

Configure [`site/config.mjs`](site/config.mjs):

```javascript
// Disable all quick-fix detection and controls:
enableQuickFixes: false

// Or disable selected rules:
disabledQuickFixRules: ['closing-unit-name', 'missing-contains']
```

The four rule names in the table can be disabled independently. Push frontend configuration changes to publish them; no Modal redeployment is needed. [`site/fixes.mjs`](site/fixes.mjs) contains the detector and guarded applicator.

[`tests/cases/quick_fixes/cases.json`](tests/cases/quick_fixes/cases.json) defines malformed sources, exact `.fixed.f90` counterparts, and refusal/control cases. For each supported repair, the harness confirms that original compilation fails, the real diagnostic yields the expected edit, the corrected source matches exactly, recompilation succeeds, and executable output matches expectations. Tests also cover valid code, warnings, unrelated errors, helper-file diagnostics, stale source, CRLF endings, disabled features/rules, and scope disagreements. Original fixtures are never overwritten. Future compiler adapters should reuse these fixtures with compiler-specific diagnostics.

## Publishing and the execution service

To create an independent playground with your own examples and execution service, follow the [forking and self-hosting guide](docs/self-hosting.md). It documents Modal deployment and explains the requirements for other hosting platforms.

The repository's [Pages workflow](.github/workflows/pages.yml) tests the frontend and compiler fixtures, bundles CodeMirror, builds versioned assets, and deploys `_site/` when changes reach `main`. GitHub Pages should use **GitHub Actions** as its publishing source.

Frontend changes such as examples, shared links, layout, and quick-fix configuration require only a frontend push. Backend changes belong in your checkout of the [execution-service repository](https://github.com/Beliavsky/python-to-fortran-playground). To redeploy, run from that checkout using the Python environment configured for Modal:

```text
python -X utf8 xdeploy_service.py
```

Then push any related frontend changes. Compile-only, retained builds, compiler-version reporting, standard selection, formatting, checking, and ofort depend on the corresponding service support. Older services can still provide Compile and Run while newer controls remain unavailable.

## Architecture and provenance

| Path | Purpose |
| --- | --- |
| `site/` | Static HTML, CSS, JavaScript, and Fortran examples |
| `xeditor.py` | Bundles pinned CodeMirror assets and its MIT license |
| `xexamples.py` | Generates the example catalog from Fortran files |
| `xplayground_links.py` | Generates a standalone HTML page of shared-code links |
| `xplayground_run.py` | Runs ordered local Fortran sources through the hosted execution API |
| `xsite.py` | Builds the Pages artifact and versions browser assets |
| `xserve.py` | Serves a trusted local preview |
| `site/service.json` | Public execution-service URL; contains no credential |

Session tokens are acquired at runtime and kept in memory. The frontend has no duplicate compiler/backend code, browser Python runtime, or transpiler pin. The service advertises compiler availability, presets, limits, and runtime revision, and enforces source limits and sandbox restrictions. Compiled helpers retain fixed build options and are not portable to ofort; future library or interpreter capabilities need explicit backend support and tests.

The editor wrapper, shared styles, asset builder, bundling script, and public service URL originated in the [Python-to-Fortran playground repository](https://github.com/Beliavsky/python-to-fortran-playground). This Fortran frontend is separate from the original playground. CodeMirror is MIT-licensed; the bundler includes its license in the built assets.
