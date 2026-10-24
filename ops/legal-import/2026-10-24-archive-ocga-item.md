# Official OCGA bulk source inventory — Archive.org item checkpoint (2026-10-24)

DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org / Archive.org item page for bulk unannotated OCGA. No ODT, PDF, or other files were downloaded. LexisNexis was not opened. Not stored statute text and not current-law verification.

## Source

- Item page: https://archive.org/details/gov.ga.ocga.2018
- Preferred structured bulk source for unannotated OCGA titles (release86.2022.11 and related).

## Raw fetch of item page (2026-10-24 ~20:01 UTC)

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item page | https://archive.org/details/gov.ga.ocga.2018 | 200 | 1,875,594 | `b909f443fc106a41e87e6282d7d639f581878637c43a868db04c581bdcbb0634` | HTML item page; many .odt references named; no files downloaded |

## Notes

- The page names numerous historical release identifiers (examples: release70.2018.12 through later releases) and thousands of .odt references.
- This confirms the existence of the bulk Archive.org item previously referenced in release86 manifest checkpoints.
- Per project policy, no files were fetched and no authority rows written while DATABASE_URL is unset.
- Gap: full title text, currency against later official sources, and any annotations remain uningested. Preferred for future import once DATABASE_URL is available and reviewed.

These counts are not persisted coverage.
