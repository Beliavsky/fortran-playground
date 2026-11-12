# API documentation with FORD

The FPM playground's **Generate API documentation with FORD** link opens a
separate page with the current repository, revision and package directory filled
in. Generation never compiles the package or rebuilds compiler images and
precompiled libraries. Author documentation remains the best source for tutorials.

The reference includes public/protected procedures, modules, types, argument
declarations, source listings, search and author-supplied FORD comments. Missing
explanations are not invented. Successful generation does not verify a package.

## Local use

Install in the Python environment used to start the local playground:

```console
python -m pip install ford==7.0.13
python xford.py C:\fortran\my-package --serve
```

A public GitHub URL can replace the local directory. Use `--revision COMMIT`
to select a revision and `--subdirectory PATH` for a package inside a repository.
`--cache PATH` changes the default `.fpm-audit-cache/ford` cache. Without
`--serve`, the command prints the HTML and ZIP paths. With it, a local HTTP
server opens in the browser; Ctrl+C stops serving. Extract ZIPs before browsing.

The same link works in the Local FPM playground using its Python environment.
That server caches documentation in `.fortran-docs` under the workspace. Source
directories and compiler jobs are untouched. The CLI supports local source
trees; the browser pilot accepts public GitHub sources. FPM and a compiler are
not required for documentation generation.

## Online deployment

The independent Modal app is `fortran-playground-docs`. In an authenticated
Python environment with Modal installed, run:

```console
python -X utf8 -m modal deploy xford_modal.py
```

Put the API URL printed by deployment in `site/documentation/service.json`:

```json
{"url": "https://beliavsky--fortran-playground-docs-api.us-east.modal.run"}
```

Commit and push the static files to publish the page. Documentation-only changes
do not require `xdeploy_fpm.py`. Fork operators can set `DOCS_ORIGINS` to a
comma-separated list of allowed origins before deployment. An empty service URL
disables online generation with an explanatory message.

Admission limits are independent of compilation: two active requests, 30 requests
per address per ten minutes and 100 public requests per UTC day. Cached requests
also count. Artifacts persist in the separate `fortran-playground-docs-cache`
Modal Volume; polling records expire after 30 minutes. There is no automatic
artifact eviction in this pilot. Operators can remove old entries using Modal's
Volume management tools.

## Scope and caching

Branches and tags resolve to full commits before downloading. Cache identity
includes repository, commit, package directory, copied source content, FORD
version and the controlled generation recipe. Repeated requests reuse HTML and
ZIP files, although source resolution and downloading still take time. Local
source edits invalidate the cache.

The generator uses FORD 7.0.13 and a configuration created by this project. It
does not run repository scripts, read repository FORD settings or install
dependencies. Hidden, build, vendor and third-party directories are excluded.
Links and special archive entries are rejected or skipped. Markdown file includes
and Fortran/CPP INCLUDE directives are unsupported. The pilot supplies no
preprocessing, FYPP expansion, dependency documentation, call graphs or MathJax.
Unexpanded conditional source can produce incomplete API results.

Limits: the downloader's 16 MiB compressed / 64 MiB expanded archive limits;
1,500 copied source files / 32 MiB; 120 seconds of FORD runtime; and
32 MiB / 10,000 generated files. The independent worker has 1 GiB memory and
a 180-second timeout. Failures do not affect compiler jobs.

Generated pages use a sandbox policy and a separate online origin. They cannot
access the local playground's session token. Bootstrap and Lunr are bundled
for offline styling and search, with licenses/provenance in `vendor/ford`.
ZIPs include generation metadata and the exact commit. Upstream licenses
continue to apply to included source and documentation.

## Verification

`tests/test_ford_docs.py` checks source isolation, path validation, revision
resolution, cache invalidation, ZIP contents, generator failures/timeouts and
local HTTP/session/sandbox integration. When FORD is installed it also runs the
real generator and checks input/output argument declarations. No compiler is
needed. Pilot measurements are saved in `docs/ford-validation.json`.
