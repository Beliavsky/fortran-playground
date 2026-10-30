# Fortran software by GAMS classification

The [GAMS catalog](https://beliavsky.github.io/fortran-playground/gams/) browses the selected precompiled packages independently of the FPM playground. It has an index of the 20 main classes, a page for every recorded class or subclass, and a detail page for every package.

Class pages include packages explicitly assigned to that class or its descendants. They show matching reviewed APIs where available. Package pages include descriptions, topics, classifications, pinned repository sources, procedure evidence, author example/test references and links to checked playground examples. Classification and source review do not imply coverage of every problem in a class or a performance benchmark. A checked package example may exercise only part of the mapped functionality.

Each package page also lists **Package dependencies** and **Used by**. These use the resolved GitHub source records from the verified playground build, combining direct and indirect dependencies. Dependencies with their own selected catalog entry link to that page; other repositories link to GitHub. Every dependency includes a link to the exact source revision, with a note when it differs from the selected catalog version. Reverse lists cover only selected builds, not usage elsewhere on GitHub. Large reverse lists are collapsed initially.

The dependency list describes the pinned playground configuration, including any playground adaptations. It does not classify edges as direct, identify internal Fortran module relationships, or list native system libraries and build tools. An empty list means no additional GitHub repository dependencies were recorded; it does not claim the package needs no external software. These sections are generated offline and add no compilation, service requests or backend deployment requirements.

Package lists and navigation are present in the HTML and work without JavaScript. Optional browser search combines words across names, GitHub owners, descriptions, categories, author and curated topics, class labels and procedure names. Search changes the `q` parameter, so a filtered page can be bookmarked or shared.

Repository owner names are clickable on package cards and detail pages. An owner page lists that account's selected precompiled packages and links to its GitHub profile. The [owner index](https://beliavsky.github.io/fortran-playground/gams/authors/) searches both public display names and account names. Names appear as “Federico Perini (perazz)” when a public display name is supplied; otherwise the account name is shown. Organizations use the same convention. These are repository owners, not necessarily the original or sole authors.

The `fortran-lang` account is displayed as **fortran-lang**, since its GitHub display name names the language. Its original public profile metadata remains saved for provenance and search.

The [curated attribution review](name-attributions.md) records explicit public source credits separately from account identities. Confirmed source authors are searchable and shown with their scope and evidence under **Name attribution** on package and owner pages. An author credited in an example is not automatically identified as the owner of the account.

## Addresses

- Index: `/fortran-playground/gams/`
- Linear systems: `/fortran-playground/gams/D2/`
- Multivariate unconstrained optimization: `/fortran-playground/gams/G1b/`
- Package details: `/fortran-playground/gams/packages/fortran-lapack/`
- Repository owners: `/fortran-playground/gams/authors/`
- An owner's packages: `/fortran-playground/gams/authors/perazz/`
- Search: `/fortran-playground/gams/?q=jacobwilliams+optimization`
- Sitemap: `/fortran-playground/gams/sitemap.xml`

Class pages use explicit parent links, rather than code-prefix matching: C1 and C10 are siblings. Empty classes remain linkable and explain that there is no currently classified selected package.

## Updating packages and classifications

Continue the existing catalog workflow. Edit `fpm_catalog.json`, the classifications and procedure records in `fpm_catalog/gams.json`, the numerical review ledger, topics and checked example references as appropriate. Then regenerate the playground and review files:

```text
python xpackage_topics.py
python xpackage_gams.py
python xfpm_examples.py
```

Every normal `python xsite.py` build publishes the portable catalog feed and passes that same data to `xgams_site.py`. The generator writes class pages, package pages and a sitemap into `_site/gams/`. Counts and membership are computed from the feed, so there is no second classification list to maintain. Obsolete generated class/package HTML is removed on a rebuild. CSS and browser search live in `site/gams/`; generated HTML is not committed.

GitHub Actions already runs `xsite.py` when changes reach `main`. Publishing these pages requires no backend redeployment, package recompilation or Modal jobs. The playground loads only its own existing assets; the new pages and their search script are separate.

## Public owner names

The [combined GitHub/name mapping table](github-name-mappings.md) lists every selected repository owner, the catalog name, profile/manual source, review dates, pending attribution notes, evidence and package links. The [manual attribution review](name-attributions.md) gives the detailed reasoning behind curated records.

`fpm_catalog/owners.json` stores each owner's public GitHub display name once, keyed by the lowercase account ID. Each record contains its account type, profile/source URLs and retrieval time. The portable catalog exports this shared mapping too. Site builds read the saved snapshot offline; account names remain the fallback for a newly added owner without saved metadata.

Fetch profiles for newly added accounts:

```text
python xgithub_owners.py --refresh --missing
```

Periodically refresh all accounts with `python xgithub_owners.py --refresh`. To update just one, use `python xgithub_owners.py --refresh --owners perazz`. The API reader uses `GITHUB_TOKEN` or `GH_TOKEN` when present. If the public API is rate-limited, wait before retrying or explicitly read the public profile headings instead:

```text
python xgithub_owners.py --refresh --missing --html
```

Refresh errors retain saved names. A successful refresh with no public name clears the previous name. Names are read only from public profile fields/headings; they are not inferred from account names, README acknowledgments, commits or email addresses. Run `python xgithub_owners.py` to validate the snapshot and report coverage without network access. Commit the snapshot, then publish through the ordinary Pages build.

## Curated names and source credits

Edit `fpm_catalog/name-attributions.json` for manual research. `owner_names` holds account-name mappings; `project_authors` holds credits for specific projects or source files. Each record requires a name, confirmed/inferred status, scope, rationale, review date and public evidence links. Prefer exact commit and line links. Do not collect unrelated personal information. Source credits establish authorship within their stated scope; they do not alone establish an account identity or sole authorship of a project.

Only confirmed account mappings override owner labels. Display order is confirmed manual account name, saved GitHub display name, then account ID. Inferred account mappings remain in the review table and portable feed, but do not rename accounts. Confirmed project/source credits are displayed and searched independently. Differences between a manual name and a GitHub display name are flagged in the review table and explained on the owner page. GitHub profile refreshes never overwrite curated records.

After editing the manual file, refreshing profiles or adding packages, regenerate both the combined name table and manual review table:

```text
python xpackage_attributions.py
python xpackage_attributions.py --check
```

The site build exports these records and renders the name-attribution sections automatically. The initial AD_dnSVM record credits David Lauvergnat for `APP/Example_dnS.f90`; the possible connection to account `lauvergn` is recorded separately as inferred.

## Preview and verification

```text
python xsite.py
python -m http.server 8878 --bind 127.0.0.1 --directory _site
```

Open <http://127.0.0.1:8878/gams/>. Stop the preview server with Ctrl+C.

```text
python -m unittest discover -s tests -p test_gams_site.py
node tests/gams_search.mjs
```

The checks cover hierarchy membership, generated navigation, pinned package links, HTML escaping, removal of obsolete pages, search and restoration of shared search queries. The ordinary site-build test also checks the published pages and versioned assets.

## A broader catalog

The renderer consumes the [portable catalog feed](catalog-export.md), rather than compiling or discovering packages itself. A future catalog can import the maintained records and add non-FPM projects or individual Fortran sources with their own review status. Keep those additions in a separate catalog so playground availability is not implied. The catalog's canonical base address is currently shared with the exporter in `catalog_export.py`.
