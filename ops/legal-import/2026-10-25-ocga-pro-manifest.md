# Public.Resource.Org OCGA metadata inventory — 2026-10-25

DATABASE_URL was unset, so no corpus rows were written. Discover-only. No title ODT, HTML, or PDF files were downloaded. LexisNexis was not scraped.

## Source

- Metadata: https://archive.org/metadata/gov.ga.ocga.2018
- Item: https://archive.org/details/gov.ga.ocga.2018
- Preferred bulk unannotated/structured OCGA source (Public.Resource.Org).

## Raw fetch of metadata (2026-10-25 ~06:01 UTC)

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| metadata (raw body) | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `14a12996b7ef949a4f0c4c25a7d65d9a8a78ddaaffaa94508ca252af238f2a03` | Large JSON listing files across releases including release86.2022.11 ODT titles and earlier HTML. HEAD returned 405 (WAF/rate); body fetch succeeded. |

## Notes

- Confirms the Archive.org item remains the preferred bulk source for unannotated OCGA text (ODT/HTML titles).
- Prior checkpoints (e.g. 2026-10-22) recorded similar metadata hashes; this is a fresh inventory point.
- No statute text stored. Currency must be verified against official sources before any future import; supplements and annotations are not included.
- Gap: DATABASE_URL unset prevents writing authority rows. Full title files remain unfetched in this run.

Not stored statute text and not current-law verification.
