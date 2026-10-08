Fortran playground
==================

A standalone Fortran-only frontend for the existing Python-to-Fortran execution
service. The original playground and backend are unchanged.

Features: editable Fortran with syntax coloring and line counts; four examples;
file loading and downloading; compiler selection and supported option presets;
compile/run timings, diagnostics and output; cancellation and reconnect.
No Python is submitted or translated. Code runs only on an explicit Run click.
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
No Modal redeployment is needed if the existing service supports fortran-edit.
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
The Fortran-only page and client are separate; the original files were not edited.
CodeMirror is MIT-licensed; xeditor.py includes its LICENSE in the built assets.
