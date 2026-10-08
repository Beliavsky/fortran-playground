Fortran playground
==================

A standalone Fortran-only frontend for the existing Python-to-Fortran execution
service. The original playground pages are unchanged; the shared backend now
also supports compile-only jobs and retained builds for this frontend.

Features: editable Fortran with syntax coloring and line counts; four examples;
file loading and downloading; compiler selection and supported option presets;
compile/run timings, diagnostics and output; cancellation and reconnect.
The selected compiler's version is shown below its menu (and in option tooltips).
Compilation results preserve the actual job's version separately, so changing
the selection does not relabel old results. Older services show version unavailable
without disabling compilation. Publishing this feature requires redeploying the
shared execution service as well as pushing this frontend.
The Standard dropdown beside Compiler offers Compiler default and verified
year selections. Unsupported years are disabled; changing the year discards
the retained executable. GNU rejects extensions beyond the selected standard;
Intel reports conformance warnings instead. Strict adds diagnostics but no
longer selects a year. Standard flags apply only to user code, never helpers.
GNU/Intel year flags are tested during image construction and the results are
cached; Flang and LFortran currently offer only Compiler default.
No Python is submitted or translated. Compile builds without execution;
Compile and Run builds and executes; Run Again reuses the executable without
recompiling, in a fresh isolated environment. Execution requires an explicit click.
Retained builds expire after at most five minutes, are private to the session,
and are discarded by the frontend when source/compiler/options change or when
reconnecting. A failed compilation cannot enable Run Again. Files created by a
previous run are not carried over. Reruns count toward the usual usage limits.
The editor and results appear side by side (60/40) on wide screens, with output
above compilation diagnostics on the right. Each pane scrolls independently;
narrow screens stack the editor before the results.
Compile, Compile and Run, Run Again and Stop sit to the right of the Fortran
input label and line count. This header remains visible while the editor
scrolls; its buttons wrap when space is limited. Compiler/options stay above
the panes. Go to first error appears in the same header only for source errors.
Compiler errors referring to the submitted input_p.f90 source are highlighted
with a red line background and gutter marker; reported columns are underlined.
Hover over a marker or highlighted text to read the diagnostic. Click a marker
or Go to first error to navigate. Source/option changes and a new compilation
clear stale markers. Warnings and helper-file errors remain in the compilation
log without source markers. Recognized formats include GNU, Intel, LLVM Flang
and LFortran; diagnostics without recognized locations still appear in the log.
If syntax coloring cannot load, Go to first error selects the line in the
plain-text editor instead. This feature needs only a frontend push, not a
Modal redeployment.

Experimental syntax quick fixes
-------------------------------
Fix error appears beside the execution buttons after a failed gfortran build
when its first source error has a supported repair. Its tooltip and the text
above the panes describe the edit. Clicking applies one undoable edit, clears
stale markers and invalidates the retained executable. It never compiles or
runs automatically. Use Ctrl+Z to undo, then Compile when ready.
If the enhanced editor cannot load, quick fixes remain hidden: the plain-text
fallback cannot guarantee native undo. Diagnostics and navigation still work.
Set enableQuickFixes to false in site/config.mjs to disable detection and hide
the controls, leaving the ordinary playground behavior unchanged. Push this
frontend to publish configuration changes; no Modal redeployment is needed.
site/fixes.mjs contains the detector and an applicator that refuses stale source.
Four independently switchable rules
are available: print-format-comma inserts a missing comma after a quoted PRINT
format; closing-unit-name corrects an END PROGRAM, END MODULE, END SUBROUTINE
or END FUNCTION name. Both require a matching gfortran source diagnostic.
use-before-implicit-none moves an adjacent block of complete USE statements
before IMPLICIT NONE, keeping their text, indentation and inline comments.
Separate intervening comments, continuations, directives and interface scopes
are refused. The supported enclosing scopes are explicit programs, modules
and simple procedures.
missing-contains inserts CONTAINS before the first complete procedure definition
in an explicit program or module. It requires a matching gfortran diagnostic
and a balanced conservative scan of the corrected source. Existing CONTAINS,
interface bodies, derived-type definitions, implicit main programs, nested
internal procedures and unsupported/incomplete constructs are refused.
The closing-name rule cross-checks the diagnostic's expected name against a
conservative source-scope scan, preserves the opening name's capitalization,
and changes only the closing identifier. Simple procedure headers, CONTAINS,
and balanced IF/DO constructs are supported. Interfaces, other unsupported
structures, continuations, multiple statements and incomplete scopes are refused.
Set disabledQuickFixRules to ['closing-unit-name'] or ['print-format-comma']
in site/config.mjs to disable
either rule independently. Add 'use-before-implicit-none' or 'missing-contains'
to disable the corresponding new rule, or list all four to disable all rules.
Other compiler adapters are not implemented yet.

Run the JavaScript unit tests, then the real compiler fixture tests:
  npm test
  node xcheck_fixes.mjs
To save compiler diagnostics and validation outcomes as JSON:
  node xcheck_fixes.mjs --report reports\quick_fixes_gfortran.json
The compiler test requires gfortran on PATH. It is also run by GitHub Actions.

tests/cases/quick_fixes/cases.json defines the fixture suite: malformed PRINT
and closing-name statements have exact .fixed.f90 counterparts, alongside
refusal/control cases for ambiguous or unsupported syntax, valid code and warnings.
For every supported repair, the harness confirms original compilation fails,
the real diagnostic yields the expected edit, corrected source matches exactly,
recompilation succeeds, and the executable's output matches the expected output.
Refusal cases include other syntax errors, valid code, and real warnings.
Unit tests additionally cover helper-file errors, stale source, CRLF endings,
feature/rule disabling, diagnostic/opening-name disagreement, nested scopes,
and unknown first errors. Original fixtures are never
overwritten. Temporary builds stay outside the repository and are cleaned up.
Future compiler support should reuse these source fixtures with compiler-specific
diagnostic adapters. Compilation success alone does not establish correctness.
ofort is not integrated yet: adding it requires backend support, not only a menu.

Local preview (Windows)
-----------------------
npm ci
python xeditor.py
npm test
python -m unittest discover -s tests
python xserve.py

Open http://127.0.0.1:8766/ . The /run/ path redirects to the main page.
You need Python and Node/npm to build and preview, but no local Fortran compiler.
This is a static preview: execution still uses the hosted service configured in
site/service.json. Running jobs there uses the owner's Modal resources and
shares the existing service's usage limits. Use port 8766 for its allowed local
origin. Do not publish the Python preview server as an execution sandbox.

Publishing
----------
Create a GitHub repository named fortran-playground, push the files to main,
and select GitHub Actions under Settings > Pages. The included workflow tests,
bundles CodeMirror, versions assets with xsite.py, and deploys _site.
The resulting entry point is https://beliavsky.github.io/fortran-playground/ .
Redeploy the shared service from C:\python\python-to-fortran-playground:
  .venv-execution\Scripts\python.exe xdeploy_service.py
Then push this frontend. Against an older service, Compile and Run still works,
but Compile and Run Again stay disabled until the service advertises support.
No deployment or GitHub repository creation has been performed by this setup.

Architecture
------------
site/ contains HTML/CSS/JavaScript; xeditor.py bundles the pinned editor assets;
xsite.py builds the Pages artifact; xserve.py serves a trusted local preview.
site/service.json contains a public service URL, not a credential. Session tokens
are acquired at runtime and kept only in memory. This frontend has no duplicate
compiler/backend code and no browser Python runtime or transpiler pin. The shared
service advertises compiler availability, presets, limits and runtime revision.
Keep backend changes in the existing execution-service project. Current options
include GNU, Intel, LLVM Flang and LFortran when advertised by that service.

Source limits and sandbox restrictions are enforced by the service. There is no
interactive stdin or arbitrary compiler-flag input. Helpers retain their own
fixed build options. A future interpreter/library feature needs explicit backend
implementation and testing; existing compiled helpers are not portable to ofort.

Provenance
----------
The editor wrapper, shared styles, asset builder, bundling script and public
service URL were copied from C:\python\python-to-fortran-playground.
The Fortran-only page and client are separate; the original frontend was not edited.
CodeMirror is MIT-licensed; xeditor.py includes its LICENSE in the built assets.
