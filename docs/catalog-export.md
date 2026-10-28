# Reusable Fortran software catalog

The playground publishes a portable metadata feed to seed a separate Fortran software catalog. Its initial collection is the 159 selected packages. A receiving catalog can add GitHub projects using any build system, including projects without FPM manifests or playground support.

The feed and the importer are a foundation for the separate catalog; this change does not create its search website or move ownership of the existing metadata.

## Published feed

Every normal Pages build generates these files automatically:

- [catalog-v1.json](https://beliavsky.github.io/fortran-playground/catalog/catalog-v1.json): software records, taxonomy, and provenance.
- [catalog-v1.schema.json](https://beliavsky.github.io/fortran-playground/catalog/catalog-v1.schema.json): JSON Schema for the version 1 contract.

These URLs become available after publishing this change. Building the site reads local metadata only; it never compiles packages, contacts GitHub or NIST, or redeploys Modal. The feed is a separate static download and is not loaded by the playground interfaces.

Generate a local snapshot with Python 3.12 or later:

```text
python xcatalog_export.py
```

This creates `catalog-export/catalog-v1.json` and its schema. The output directory is ignored by Git. To choose another directory:

```text
python xcatalog_export.py --output-dir path/to/export
```

The authoritative schema is [catalog/catalog-v1.schema.json](../catalog/catalog-v1.schema.json). The exporter validates its output with the standard library. A separate JSON Schema validator can also check it; cross-record checks such as duplicate IDs, classification references, cycles, and snapshot integrity are handled by the Python validator.

## Version 1 records

`schema_version` identifies the feed format. `$schema` identifies its JSON Schema document. Unknown format versions are rejected by the importer; future incompatible formats should use a new versioned filename. Consumers should tolerate additional fields in a supported version.

| Field | Meaning and source |
| --- | --- |
| `id` | Lowercase canonical GitHub identity, for example `github:perazz/fortran-lapack`. |
| `name`, `description`, `categories` | Playground-maintained descriptive metadata. |
| `repository` | Hosting service, GitHub account owner, repository name, and URL. An account owner is not an authorship list; authors have not been collected. |
| `languages`, `build_systems` | Known technologies. The seed records identify Fortran and FPM; the format accepts other build systems and does not require FPM. |
| `license.label` | Existing descriptive license text, preserved verbatim. `spdx_expression` is null because these labels have not been systematically normalized into SPDX expressions. |
| `github` | Author-supplied repository topics, star count, and retrieval timestamps. Unknown counts/timestamps can be null. |
| `curation.topics` | Our curated topics, kept separate from GitHub topics. |
| `curation.gams_codes` | Explicit parent and subclass assignments referencing the included taxonomy. |
| `curation.procedures` (optional) | Pinned module/procedure identities, derivative requirements, GAMS codes, source evidence hashes, and author-example references. |
| `curation.numerical_review` (optional) | Coverage status, archive/revision pins, procedure IDs, and qualifications from the numerical review ledger. Supporting declarations are distinguished from numerical procedures. |
| `demonstrations` (optional) | Verified drivers with source hashes, licenses, procedure references, load links, and saved validation paths. Importers retain these in the publisher source layer. |
| `curation.gams_review_level`, `gams_notes`, `reviewed_revision` | Current discovery-review scope, qualifications, and upstream package revision. Inclusion does not claim a procedure-level driver verification. |
| `playground` | Optional relationship to a selected playground entry, including its revision, example reference, and package-specific URL. It can be absent or null for other software. |

`playground.catalog_status = "selected"` means the entry is maintained in the selected catalog. `live_service_checked = false` explicitly distinguishes that fact from a live service/capability check. A catalog may show **Try in playground**, but should not infer universal compiler support from this field. Examples are linked by path and checksum; source code, compilation recipes, patches, dependency locks, and compiled artifacts remain in the playground repository.

The current sources are:

- [fpm_catalog.json](../fpm_catalog.json): project descriptions, recorded license labels, categories, revisions, and playground selection.
- [fpm_catalog/topics.json](../fpm_catalog/topics.json): saved GitHub metadata.
- [fpm_catalog/playground-topics.json](../fpm_catalog/playground-topics.json): our topics.
- [fpm_catalog/gams.json](../fpm_catalog/gams.json): GAMS taxonomy, assignments, and review notes.
- [fpm_catalog/gams-numerical-review.json](../fpm_catalog/gams-numerical-review.json): numerical-package review coverage and remaining scope.
- [fpm_catalog/demos](../fpm_catalog/demos): example references.

IDs are independent of package names, compiler versions, and revisions. GitHub account/repository casing is normalized. A repository rename or transfer changes this initial canonical identity; handle that as an explicit migration in the receiving catalog, retaining an alias if desired. The exporter does not guess rename relationships.

The taxonomy includes explicit parent references, so C1 and C10 are siblings. The [numerical review](gams-numerical.md) adds detailed classes across the numerical areas, retaining every ancestor. For example, I1a1a identifies nonstiff one-step initial-value methods while I1a2 identifies stiff/DAE methods. The detailed taxonomy source is included alongside the existing NIST taxonomy reference. Further levels can be added without changing the format; only reviewed assignments should be added.

## Reproducible provenance

Each snapshot records:

- Source repository and commit when all exporter inputs match that commit.
- Base commit and `inputs_modified` status for local changes. `source_commit` is null when inputs are modified or Git information is unavailable; a base commit is not a claim that it contains local edits.
- Relative input paths and SHA-256 hashes, including the export implementation, schema, classification metadata, and example files.

Input file hashes use UTF-8 text with line endings normalized to LF. Unrelated working-directory files do not mark the metadata dirty. No machine-specific paths, owner keys, or environment settings are exported.

`snapshot_id` is `sha256:` followed by the hash of the complete JSON object with `snapshot_id` removed, serialized with sorted object keys, no insignificant whitespace, unescaped Unicode, and UTF-8 encoding. Array order is preserved. This is a consistency checksum, not a signature. Exporting the same source state is deterministic; there is no changing export-generation timestamp. GitHub retrieval dates remain available in their own fields.

The published URL follows the latest successful site build. For a reproducible catalog build, retain the downloaded feed with the receiving catalog, or check out the recorded `source_commit` and regenerate it. After a metadata-only update, an ordinary push and Pages build publishes a fresh feed.

## Importing into another catalog

Run the supplied importer against a local snapshot:

```text
python xcatalog_import.py --feed catalog-export/catalog-v1.json --catalog path/to/software-catalog.json
```

Or read the published feed directly:

```text
python xcatalog_import.py --feed https://beliavsky.github.io/fortran-playground/catalog/catalog-v1.json --catalog path/to/software-catalog.json
```

The catalog file is created if missing. Use `--output path/to/preview.json` to write a reviewable result separately. The importer validates the complete feed before replacing the destination atomically. Failed downloads, malformed data, unknown schema versions, and invalid identities/classifications leave the existing catalog intact.

The receiving document keeps editable metadata separate from imported records:

```json
{
  "schema_version": 1,
  "sources": {},
  "projects": [
    {
      "id": "github:perazz/fortran-lapack",
      "local": {
        "description": "Description chosen by the catalog editor",
        "topics": ["dense-linear-algebra"],
        "notes": "Our own annotations"
      },
      "imports": {}
    },
    {
      "id": "github:example/legacy-math-library",
      "local": {
        "name": "Illustrative non-FPM entry",
        "build_systems": ["make"],
        "description": "Software maintained directly in this catalog"
      },
      "imports": {}
    }
  ]
}
```

Importing writes only `imports.fortran-playground` within matching projects and `sources.fortran-playground` at the document level. These retain the feed's original records, taxonomy, source commit, and snapshot ID. Local descriptions, topics, classifications, notes, other source layers, and projects maintained independently are preserved. The receiving site's presentation code decides how local overrides and topic unions are displayed; the importer deliberately retains the original sources instead of flattening them.

An entry removed from a later feed loses that source's import layer. A project with local metadata or other sources remains; an imported-only project with no remaining information is removed. To keep a project independently of playground selection, adopt its description/classifications into its `local` layer. Removing playground availability does not mean the upstream software has disappeared.

Repeated imports of the same snapshot are idempotent. This importer currently owns only the `fortran-playground` source; other sources can have their own importers and namespaces.

Only [xcatalog_import.py](../xcatalog_import.py) and [catalog_export.py](../catalog_export.py) are needed in the receiving repository to perform imports. They use the standard library and do not require the playground source tree or a compiler. Alternatively, invoke them from a sibling checkout of this repository. Pin the importer version in an automated build. A receiving site's build can run the HTTPS import command above before generating its pages; it does not need to commit imported updates automatically.

## Playground links

An exported link such as `https://beliavsky.github.io/fortran-playground/fpm/?package=fortran-lapack` selects the package and loads its pinned example when loading is available. It never compiles or runs automatically. Unknown package IDs produce a visible message; unavailable service entries retain the existing loading checks. `package` takes precedence over `collection` when both are supplied because these links identify selected entries. The same link parameter works in the main local FPM interface.

## Later ownership migration

Once a separate catalog is established, move shared descriptions, curated topics, GAMS mappings, and routine/driver references there and have the playground import its selected entries. Keep build recipes, patches, dependency pins, sandbox verification, and precompiled artifacts under playground ownership. Moving one field at a time with an explicit owner avoids two competing editable copies.
