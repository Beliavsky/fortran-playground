# Fortran playground

[Open the playground](https://beliavsky.github.io/fortran-playground/) ? [GitHub repository](https://github.com/Beliavsky/fortran-playground) ? [Python-to-Fortran playground](https://beliavsky.github.io/python-to-fortran-playground/)

Explore Fortran in your browser with short examples, an editable source pane, and a choice of compilers or an interpreter. No local compiler is needed to use the site. The playground submits Fortran directly to the shared Python-to-Fortran execution service; it does not translate or submit Python.

## Using the playground

1. Choose an example, load a local Fortran file, or write your own program.
2. Select an available compiler or interpreter and, optionally, a language standard and compiler options.
3. Click **Compile** to build without execution, or **Compile and Run** to build and execute.
4. Edit the program and repeat. Use **Download Fortran** to save the source, or **Copy share link** to share it.

The editor provides syntax coloring, line counts, undo, and navigation to recognized source errors. A plain-text fallback remains available if the enhanced editor cannot load. Wide screens show the editor and results side by side; narrow screens stack them. Execution controls stay visible above the source pane.

### Compilers, standards, and execution

The service reports which tools are available: GNU Fortran, Intel Fortran, LLVM Flang, LFortran, and the experimental ofort interpreter. The selected tool's version appears below its menu; results retain the version used for that particular job. Older services can show ?version unavailable? while still allowing compilation.

The **Standard** menu offers **Compiler default** and years verified by the service. Unsupported years are disabled. GNU rejects extensions beyond the selected standard; Intel reports conformance warnings. The **Strict** option adds diagnostics without choosing a standard year. Standard flags apply only to submitted code, while helpers retain their own fixed build options. GNU and Intel year flags are checked during service image construction and cached; Flang and LFortran currently offer only **Compiler default**.

**Run Again** reuses a successfully compiled executable for up to five minutes. It starts a fresh isolated process without recompiling. Source or option changes, reconnecting, failed compilation, and expiration invalidate the retained build. Files from a previous run are not carried over, and reruns count toward service usage limits. Retained builds are private to the session.

With **ofort**, **Compile** becomes **Check syntax**, and **Compile and Run** becomes **Run**. Compiler flags and **Run Again** are disabled. Each Run starts a fresh interpretation using `ofort --fast`; Check syntax uses `ofort --fast --check`. Both use compact-array fast mode. Only standalone source is supported; compiled `python_mod` helpers cannot be linked into ofort. Its execution detects reads of uninitialized variables that its syntax check may not detect. Unsupported features can be rejected, and failures never silently switch tools.

### Formatting, checks, and diagnostics

| Control | Behavior |
| --- | --- |
| **Format** | Uses fprettify for whitespace-only formatting with three-space indentation. One undo restores the previous source. Requires the enhanced editor and service formatting support. |
| **Check** | Runs Fortitude without fixes or execution. Uses its default rules and Fortran 2018 target, independently of the selected compiler standard. Findings appear in a separate panel. |
| **Go to first error** | Navigates to the first recognized source error, including in the plain-text fallback. |
| **Fix error** | Applies a supported experimental syntax repair as one undoable edit; see below. |

Formatting is not syntax validation or automatic repair. Failed, cancelled, or stale formatting results never replace the source. Fortitude checking preserves source, compiler output, and any retained executable. Hosted formatting and checking use the shared service and its limits.

Recognized errors in the submitted `input_p.f90` source receive a red line background and gutter marker; reported columns are underlined. Hover to read the message, or click a marker to navigate. Source or option changes and new compilations clear stale markers. Warnings and helper-file errors remain in the compilation log without source markers. GNU, Intel, LLVM Flang, and LFortran diagnostic formats are recognized; other diagnostics still appear in the log.

### Limits

- Source limit: **100 KB** (100,000 UTF-8 bytes).
- Output limit: **200 KB per output stream**.
- No interactive stdin or arbitrary compiler-flag input.
- Programs run in isolated environments without network access.
- Compilation, execution, formatting, and checking require an explicit button click.

## Sharing code with a link

Click **Copy share link** to create a link containing the current source. If clipboard access is unavailable, a selected text field lets you copy it manually. Anyone opening the link sees the code in the editor and chooses when to compile or run it. The link includes source only, without compiler settings, results, or session tokens.

The public format is:

```text
https://beliavsky.github.io/fortran-playground/#code=URL_ENCODED_FORTRAN
```

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

Empty, incorrectly encoded, or oversized shared source is rejected with a message. Changing to another shared-code fragment in the same tab asks before replacing nonempty input. Opening a shared link never automatically submits a job. Long links may be truncated by browsers, messaging tools, or forums; sharing is best suited to short examples even though the source limit remains 100 KB.

### Generate a page of links from a repository

Use [`xplayground_links.py`](xplayground_links.py) to create a standalone HTML page from a directory of Fortran programs. It requires Python only and works with a local checkout of any repository; the source files do not have to be in this playground's repository.

```powershell
# Generate links for this playground's examples:
python xplayground_links.py site/examples --output playground-links.html

# Scan another repository, including its subdirectories:
python xplayground_links.py C:/projects/my-fortran/examples --recursive --output docs/index.html --title "My Fortran examples"
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

The starter collection contains **14 language demonstrations** and **six numerical calculations**. Every program is standalone, prints labeled results, and includes a suggested change to try. FortranTip adaptations retain source URLs and original attribution in comments.

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

## Local development

You need Python and Node/npm to build and preview. Install gfortran to run the compiler tests; a compiler is not needed merely to preview the frontend.

```powershell
npm ci
python xeditor.py
npm test
python -m unittest discover -s tests -v
python xserve.py
```

Open <http://127.0.0.1:8766/>. The `/run/` path redirects to the main page. Use port 8766 for the service's allowed local origin.

This is a static preview. Execution, formatting, and checking still use the hosted service configured in `site/service.json`, consume the owner's Modal resources, and share its usage limits. Do not publish the Python preview server as an execution sandbox.

### Testing

```powershell
npm test
python -m unittest discover -s tests -v
npm run test:fixes
python xsite.py
```

- **JavaScript tests** cover editor behavior, diagnostics, quick fixes, formatting, shared links, and UI interactions without submitting hosted jobs.
- **Python tests** cover catalog generation, asset versioning, and frontend structure. With Node and gfortran on PATH, they compile and run every generated dropdown example twice: with compiler defaults, then with Fortran 2018 conformance, warnings as errors, and runtime checks. Expected labeled output is checked with floating-point tolerances.
- **Quick-fix compiler tests** use real gfortran diagnostics to verify repairs and refusals.
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

The repository's [Pages workflow](.github/workflows/pages.yml) tests the frontend and compiler fixtures, bundles CodeMirror, builds versioned assets, and deploys `_site/` when changes reach `main`. GitHub Pages should use **GitHub Actions** as its publishing source.

Frontend changes such as examples, shared links, layout, and quick-fix configuration require only a frontend push. Backend changes belong in the existing execution-service project. For service changes, redeploy from `C:\python\python-to-fortran-playground`:

```powershell
.venv-execution\Scripts\python.exe xdeploy_service.py
```

Then push any related frontend changes. Compile-only, retained builds, compiler-version reporting, standard selection, formatting, checking, and ofort depend on the corresponding service support. Older services can still provide Compile and Run while newer controls remain unavailable.

## Architecture and provenance

| Path | Purpose |
| --- | --- |
| `site/` | Static HTML, CSS, JavaScript, and Fortran examples |
| `xeditor.py` | Bundles pinned CodeMirror assets and its MIT license |
| `xexamples.py` | Generates the example catalog from Fortran files |
| `xplayground_links.py` | Generates a standalone HTML page of shared-code links |
| `xsite.py` | Builds the Pages artifact and versions browser assets |
| `xserve.py` | Serves a trusted local preview |
| `site/service.json` | Public execution-service URL; contains no credential |

Session tokens are acquired at runtime and kept in memory. The frontend has no duplicate compiler/backend code, browser Python runtime, or transpiler pin. The service advertises compiler availability, presets, limits, and runtime revision, and enforces source limits and sandbox restrictions. Compiled helpers retain fixed build options and are not portable to ofort; future library or interpreter capabilities need explicit backend support and tests.

The editor wrapper, shared styles, asset builder, bundling script, and public service URL originated in `C:\python\python-to-fortran-playground`. This Fortran frontend is separate from the original playground. CodeMirror is MIT-licensed; the bundler includes its license in the built assets.
