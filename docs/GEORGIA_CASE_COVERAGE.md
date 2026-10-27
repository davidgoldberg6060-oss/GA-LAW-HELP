Last production check: 2026-10-27 20:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only attempts on Court of Appeals of Georgia opinion search and rules indexes returned AWS WAF/CloudFront captcha challenge pages (HTTP 405). Challenge page bytes hashed; no opinion indexes, rule text, or PDFs retrieved; not stored authority text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion search | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `6e7ca7453976a37958e2bf8be13988d4d82977808ae86ff38a8da8dfd56b1766` | Captcha challenge; no content fetched |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `e26015e979b9884f402ebfa6b45e26ef466c64203f2710e26557346885c215fc` | Captcha challenge; no content fetched |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `8f2d122df1d485ffc32b9c6c0c6b163e361a79721341ae4789914624d4784ee1` | Captcha challenge; robots not retrieved |

The official Court of Appeals sites are currently protected by AWS WAF captcha, preventing automated discover-only inventory of opinion indexes and rules. Lexis was not scraped. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-27-coa-opinion-rules-indexes.md`.

Last production check: 2026-10-25 21:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of Public.Resource.Org OCGA item metadata. Metadata bytes hashed; no ODT/RTF/HTML statute files downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `fb5e0ff9c5ccd462be9f3684b3c5f1117413d7d14c8f6783048465d8c199ad45` | Manifest only; files_count 3219; release86.2022.11 present; prior 2026-10-22 hash differed |

Preferred bulk unannotated source remains this archive. Lexis was not scraped. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-25-ocga-release86-metadata.md`.

(See full historical inventory in prior commits; this update restores the complete report with the new 2026-10-27 entry at the top.)
