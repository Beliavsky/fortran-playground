# Forking and self-hosting the Fortran playground

[Back to the README](../README.md)

You can run an independent playground with your own examples, branding, and execution service. This guide documents GitHub Pages for the static frontend and Modal for the backend. Other platforms can be used if they meet the requirements below.

If you only want a collection of examples, consider [generating a page of shared-code links](../README.md#generate-a-page-of-links-from-a-repository) instead. That avoids deploying a separate playground and uses the existing site's service and shared usage limits.

## What you are deploying

| Component | Source | Hosting |
| --- | --- | --- |
| Static frontend | Your fork of [fortran-playground](https://github.com/Beliavsky/fortran-playground) | GitHub Pages or another static HTTPS host |
| Execution backend | A checkout of [python-to-fortran-playground](https://github.com/Beliavsky/python-to-fortran-playground) | Your own Modal workspace, or an adapted backend on another platform |

The backend originated with the Python-to-Fortran (p2f) site and is shared by the author's two playgrounds. Your visitors do not need to visit or use that p2f site. Your frontend can submit Fortran directly to a backend deployed in your own account. The current backend build still includes the p2f sources and precompiled helpers: it has not been extracted into a Fortran-only backend repository.

Forking the frontend does not deploy a backend. Its copied `site/service.json` initially points to the author's service. Replace it before publishing your own site; do not assume that endpoint is available for other sites. Shared access can be discussed separately with the operator.

## Prerequisites

- Git, Python 3.12, and Node.js 22 with npm. These match the frontend workflow's Python and Node versions.
- gfortran on PATH for the local compiler tests. The Pages workflow installs gfortran itself.
- A GitHub account and a fork of the frontend repository.
- A Modal account/workspace for the documented backend deployment, plus network access to download the pinned upstream bundle and build compiler images.

Commands below use PowerShell and sibling frontend/backend directories. Replace `YOUR_GITHUB_USER` and example hostnames with your own values. On Linux or macOS, use `.venv-execution/bin/python` in place of `.venv-execution/Scripts/python.exe`.

## 1. Fork the frontend and choose your examples

Fork the repository on GitHub, then clone your fork:

```powershell
git clone https://github.com/YOUR_GITHUB_USER/fortran-playground.git fortran-playground
cd fortran-playground
npm ci
python xeditor.py
```

Replace or extend the programs directly in `site/examples/`. Use short standalone UTF-8 programs that need no interactive input or external libraries. Supported extensions are `.f90`, `.f95`, `.f03`, and `.f08`, case-insensitively. Each filename stem must be unique. Numeric prefixes control ordering, and an optional comment supplies the dropdown label:

```fortran
! Example: Arrays: masked sums
```

Update `tests/example_results.json` to match your set of programs. Every example needs expected labeled output; keys are filename stems. Remove entries for deleted examples and update expected output when editing a program. The [README](../README.md#examples) explains generation and testing in more detail.

Update the title, introductory text, and repository link in `site/index.html`, and adjust the README for your site. Keep attribution for adapted examples and dependencies. Relative frontend asset URLs support a different repository name or project path.

For a beginner-focused site, set `interfaceMode: 'simple'` in `site/config.mjs`. This starts the reduced interface with gfortran and compiler defaults; visitors can switch to Advanced. The repository's default is `advanced`. See [the interface descriptions](../README.md#simple-and-advanced-interfaces). Your backend must advertise gfortran for Simple to run programs.

## 2. Obtain the backend and configure Modal

From the parent of your frontend directory:

```powershell
cd ..
git clone https://github.com/Beliavsky/python-to-fortran-playground.git execution-service
cd execution-service
python -m venv .venv-execution
.venv-execution/Scripts/python.exe -m pip install -r requirements-execution.txt
.venv-execution/Scripts/python.exe -m modal token new
.venv-execution/Scripts/python.exe xvendor.py
```

The authentication command opens a browser to configure a token for your Modal workspace. Check the selected workspace before deploying. Modal's [getting-started guide](https://modal.com/docs/guide/getting-started) describes authentication; the commands above use the backend's pinned SDK requirements.

`xvendor.py` downloads the upstream revision pinned in `upstream.json` and generates the bundle required by the service image. Run it before deployment even if you only intend to submit Fortran. No local transpiler checkout is required.

Keep Modal account credentials outside public source files and the frontend. Visitors obtain short-lived application session tokens; they do not need your Modal credentials. The included frontend Pages workflow needs no Modal credentials because it deploys only static files.

Use a fork of the backend repository if you want to keep your backend configuration under version control. You do not need to publish its p2f frontend or enable its Pages workflow to use the execution service.

### Allow your frontend's browser origin

In the **backend checkout**, edit `ORIGINS` in `xpublic_api.py`:

```python
ORIGINS = [
    'https://YOUR_GITHUB_USER.github.io',
    'http://127.0.0.1:8766',
    'http://localhost:8766',
]
```

An origin consists of scheme, hostname, and optional port. Do not include the repository path or a trailing slash. For `https://YOUR_GITHUB_USER.github.io/fortran-playground/`, the origin is `https://YOUR_GITHUB_USER.github.io`. Use your actual origin if you have a custom domain. Keep the local origins only if you want local previews to connect to this backend.

Both the request-origin check and CORS middleware use this list. Origin checking is a browser-access control, not authentication of an individual site owner; non-browser clients can supply an Origin header. Keep the service's session ownership, sandboxing, and workload limits in place. Sites under different paths on the same origin cannot be distinguished by this setting.

### Set workload and spending limits

In the backend's `xpublic_api.py`, review the current defaults:

| Constant | Current default |
| --- | --- |
| `MAX_ACTIVE` | Two active jobs across the service |
| `MAX_DAILY` | 100 jobs per UTC day across the service |
| `MAX_PER_ADDRESS` | 30 jobs per address in a ten-minute window |

Compilation, execution, formatting, and checking share these allowances. Multiple visitors behind one school or office address share the per-address allowance. These job-count limits are not dollar spending caps.

Set a workspace usage budget and spend limit in Modal's billing dashboard. A budget caps usage before credits; a spend limit caps net charges after credits. See [Modal's budget documentation](https://modal.com/docs/guide/budgets) for current behavior. The account deploying the service pays for its builds and visitors' workloads. Avoid relying on a particular free-credit amount or plan price.

### Deploy the service

For an initial GNU-only service, run from the backend checkout:

```powershell
.venv-execution/Scripts/python.exe -X utf8 xdeploy_service.py --without-intel --without-flang --without-lfortran --without-ofort
```

To attempt all supported optional compiler/interpreter images, omit those flags:

```powershell
.venv-execution/Scripts/python.exe -X utf8 xdeploy_service.py
```

The script builds and publishes the required images, verifies optional tools, then deploys the API. Review warnings: an optional tool that fails its build or verification is not advertised. Building more toolchains takes additional time and resources. Compiler packages remain subject to their applicable licenses.

Use `xdeploy_service.py` for subsequent deployments too. Running `modal deploy xmodal.py` alone does not perform the required image-build/publication and metadata preparation.

Copy the HTTPS API origin printed by the deployment, for example:

```text
https://YOUR_WORKSPACE--p2f-playground-execution-api.modal.run
```

Use the actual printed URL rather than constructing it from the example. The Modal app and persistent state use p2f-based names, which do not make your frontend dependent on the author's running site. Deploying again under those names in the same Modal environment updates that service; use a separate workspace/environment if you need independent instances, and configure Modal to target it consistently.

## 3. Connect your frontend to your backend

Back in your **frontend checkout**, replace `site/service.json` with your service origin:

```json
{
  "url": "https://YOUR_WORKSPACE--p2f-playground-execution-api.modal.run"
}
```

Use an HTTPS origin only: no `/api` suffix, other path, credentials, query, or fragment. This is a public URL, not a secret. The p2f backend's `xconnect_service.py` updates that repository's `site/run/service.json`; it does not configure this standalone frontend. Edit this frontend's `site/service.json` directly.

The frontend accepts HTTPS origins on other providers too. The browser's Content Security Policy is configured separately in `site/index.html`. Its default connection rule is:

```text
connect-src 'self' https://*.modal.run;
```

It already permits normal Modal deployment URLs. For a custom domain or another provider, add your exact execution-service origin to that directive, for example:

```text
connect-src 'self' https://*.modal.run https://execute.example.org;
```

You can remove the Modal wildcard if your fork only uses the other host. Preserve the other policy directives. If your web host also sends a CSP response header, update that policy as well; a permissive meta tag cannot override a more restrictive response header. Updating only `service.json` is insufficient when CSP blocks the new host.

## 4. Test locally and publish

From the frontend directory:

```powershell
npm test
python -m unittest discover -s tests -v
npm run test:fixes
python xsite.py
python xserve.py
```

The JavaScript UI tests use a mocked service and submit no hosted jobs. The Python suite compiles and runs every dropdown example with gfortran when Node and gfortran are on PATH. Confirm that the compiler test actually runs rather than being skipped. The site build writes `_site/`.

Open `http://127.0.0.1:8766/`. Choose a short program and check:

1. The site connects to your service and shows GNU Fortran's version.
2. Compile succeeds; Compile and Run prints the expected result.
3. Run Again reuses a retained executable. Editing the source disables reuse.
4. Format works with the enhanced editor, and Check displays Fortitude results.
5. Shared links load source without submitting a job. Copy share link produces your fork's URL.
6. Stop and Reconnect behave as expected.

These manual hosted actions use your Modal resources and job allowance. Check the browser's Network panel to confirm requests go to your own backend.

In your GitHub frontend fork, enable Actions if prompted and select **Settings > Pages > Source > GitHub Actions**. Use the included workflow; do not replace it with a branch-based publication of the repository. See [GitHub's publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

Commit your frontend configuration and example changes, then push to `main`. The workflow tests, builds, and deploys `_site/`. It assumes `main`; update its branch trigger and build condition if you use another branch. After deployment, repeat the connection and execution checks at the public URL. Its origin must match the backend's `ORIGINS` setting.

Other static hosts can serve the contents of `_site/` over HTTPS. They must serve JavaScript modules with a suitable content type and permit the configured execution origin through CSP. Update the backend's allowed origins when moving the frontend.

## Using an execution provider other than Modal

Modal is the deployment option documented and implemented by the current backend. The static frontend communicates over HTTPS and does not require Modal itself. Another backend can implement the same API, but `xmodal.py` and `xdeploy_service.py` are Modal-specific and cannot be deployed unchanged to another provider.

Use `site/app.mjs` in this repository and `xpublic_api.py`, `xmodal.py`, `xsandbox_worker.py`, and `xrun.py` in the backend repository as the implementation references. A replacement service needs these behaviors:

| Interface | Required behavior |
| --- | --- |
| `GET /api/session` | Issue an application token and advertise compilers, versions, options, standards, and supported features. |
| `POST /api/jobs` | Accept the frontend's source/mode/options JSON and return a job `id`. Authenticate with `X-P2F-Token`. |
| `GET /api/jobs/{id}` | Return job state and, when done, the result structure expected by the frontend. |
| `POST /api/jobs/{id}/cancel` | Stop a job owned by the session. |
| Feature flags | Advertise only implemented compile-only, retained-run, format, and check capabilities. Unsupported features stay unavailable in the UI. |
| Cross-origin requests | Allow your frontend origin, GET/POST and preflight requests, and the `Content-Type` and `X-P2F-Token` headers. Return readable JSON errors. |

The current backend also provides `GET /api/health` for diagnostics. Retained executables, if supported, must remain private to their owning session and expire. Preserve the source/options and diagnostic semantics expected by the frontend, not just the endpoint names.

Compiling and running public submissions requires fresh isolated jobs, unprivileged execution, time/CPU/memory/process/output limits, network restrictions, cancellation, and cleanup. Keep platform credentials outside those jobs. Preserve durable workload limits and session/job ownership checks when adapting the backend. A publicly reachable Python process that invokes a compiler on the host is not an equivalent replacement for the current sandbox service.

This guide does not provide or claim validation of another provider's sandbox implementation. After adapting the backend, test the complete API and isolation behavior, configure its frontend origin, and update both `site/service.json` and the frontend CSP. No provider credentials belong in the static site.

## Updating and troubleshooting

Example, shared-link, and layout changes require only a frontend rebuild/push. Backend origin, quota, compiler, or service changes require redeployment from the backend checkout. Re-run `xvendor.py` when updating the backend's upstream pin, and use `xdeploy_service.py` to rebuild and publish the matching images. Keep custom backend changes in your own version control so updates do not discard them.

| Symptom | What to check |
| --- | --- |
| The frontend builds but cannot connect | Correct `site/service.json`, HTTPS origin validation, deployed API URL, and browser Console/Network errors. |
| Browser reports a CSP violation | The meta policy in `site/index.html` and any host-provided CSP header must permit the execution origin. |
| Requests fail with 403 or CORS errors | Backend `ORIGINS` must contain the actual frontend origin without its project path; redeploy after edits. |
| Deployment fails with missing vendor files | Run `xvendor.py` in the backend checkout before deployment. |
| An optional compiler is unavailable | Read deployment verification warnings; the service only advertises verified optional tools. |
| Requests return 429 | Review active-job, daily, per-address and session allowances, as well as platform limits. |
| Compiler tests are skipped locally | Put both gfortran and Node on PATH and rerun the Python suite. |
| A new example fails deployment tests | Add its expected output entry and check that it compiles and runs without input or external helpers. |
| Your origin change has no effect | Confirm you edited and redeployed the backend checkout used by the frontend's configured endpoint. |

The commands and configuration paths above were checked against the current source. Deployment in a fresh account remains a step for the person hosting the fork.
