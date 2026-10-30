# Fortran software by GAMS classification

The [GAMS catalog](https://beliavsky.github.io/fortran-playground/gams/) browses the selected precompiled packages independently of the FPM playground. It has an index of the 20 main classes, a page for every recorded class or subclass, and a detail page for every package.

Class pages include packages explicitly assigned to that class or its descendants. They show matching reviewed APIs where available. Package pages include descriptions, topics, classifications, pinned repository sources, procedure evidence, author example/test references and links to checked playground examples. Classification and source review do not imply coverage of every problem in a class or a performance benchmark. A checked package example may exercise only part of the mapped functionality.

Package lists and navigation are present in the HTML and work without JavaScript. Optional browser search combines words across names, GitHub owners, descriptions, categories, author and curated topics, class labels and procedure names. Search changes the `q` parameter, so a filtered page can be bookmarked or shared.

## Addresses

- Index: `/fortran-playground/gams/`
- Linear systems: `/fortran-playground/gams/D2/`
- Multivariate unconstrained optimization: `/fortran-playground/gams/G1b/`
- Package details: `/fortran-playground/gams/packages/fortran-lapack/`
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
