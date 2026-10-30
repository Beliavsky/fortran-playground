# Curated public name attributions

See the [combined GitHub/name mapping table](github-name-mappings.md) for all selected repository owners, including public profile names and curated records.

These records document public project credits and proposed or confirmed account-name mappings. They are maintained separately from automatically refreshed GitHub profiles. A source author credit does not by itself establish who controls a GitHub account or sole authorship of a package.

Only **confirmed** manual account mappings override owner display names. Inferred account mappings remain a review queue; confirmed project credits are displayed with their stated scope. Search includes confirmed project credits without treating them as account identities.

## Account-name mappings

| Account | Proposed name | Status | Scope / reasoning | GitHub display name | Profile conflict | Reviewed | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [lauvergn](https://github.com/lauvergn) | David Lauvergnat | inferred | Possible account-to-person connection; not used as an owner display-name override. The public source credits David Lauvergnat as author and copyright holder. This supports source authorship but does not independently establish the identity behind the repository-owner account. | Not supplied | None recorded | 2026-10-30 | [Explicit public author credit in the pinned example source.](https://github.com/lauvergn/AD_dnSVM/blob/32db0bd122ce1dae290e9cf4c1fda4ab8f3de6f1/APP/Example_dnS.f90#L53) |

## Project/source author credits

| Project | Credited name | Status | Scope / reasoning | Reviewed | Evidence |
| --- | --- | --- | --- | --- | --- |
| [lauvergn/ad_dnsvm](https://github.com/lauvergn/ad_dnsvm) | David Lauvergnat | confirmed | Author credited in APP/Example_dnS.f90. The pinned example explicitly names David Lauvergnat in its author annotation and copyright notice. This records the stated source credit, not sole authorship of the package or ownership of the GitHub account. | 2026-10-30 | [Explicit author annotation.](https://github.com/lauvergn/AD_dnSVM/blob/32db0bd122ce1dae290e9cf4c1fda4ab8f3de6f1/APP/Example_dnS.f90#L53); [Copyright notice naming the same author.](https://github.com/lauvergn/AD_dnSVM/blob/32db0bd122ce1dae290e9cf4c1fda4ab8f3de6f1/APP/Example_dnS.f90#L8) |

## Maintenance

Edit [name-attributions.json](../fpm_catalog/name-attributions.json). Record explicit public credits, scope, reasoning, a review date and evidence links; prefer links pinned to commits and source lines. Use account mappings only when the evidence connects the person to the account. Names, initials or an account spelling alone are not sufficient. Your existing software list can supply attribution leads, with primary project evidence recorded where available.

Do not collect unrelated personal details or infer identities from private information. Keep organization names distinct from individual project credits. If a manually mapped name differs from the current GitHub display name, review the conflict rather than changing either source automatically.

Run `python xpackage_attributions.py` to regenerate this table, or add `--check` to validate it without writing. GitHub refreshes never edit the manual file. The Pages build exports the records and renders name attribution evidence automatically; no package compilation or backend redeployment is needed.
