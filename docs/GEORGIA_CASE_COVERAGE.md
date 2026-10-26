Last production check: 2026-10-26 04:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only notes on Court of Appeals of Georgia domain transition and robots.txt. No opinion or rule PDFs downloaded; not stored text and not current-law verification:

| Source | URL | Notes |
| --- | --- | --- |
| domain transition | https://www.gaappeals.gov/ | Alert on homepage: transitioned from gaappeals.us to gaappeals.gov. |
| robots.txt | https://www.gaappeals.gov/robots.txt | Disallow only /wp-admin/; sitemap present. |
| raw curl | homepage / robots | AWS WAF challenge page (~2.5 KiB); tool-based fetch confirmed content earlier. |

Lexis was not scraped. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-26-coa-domain-robots.md`.

Last production check: 2026-10-25 21:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of Public.Resource.Org OCGA item metadata. Metadata bytes hashed; no ODT/RTF/HTML statute files downloaded; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| item metadata | https://archive.org/metadata/gov.ga.ocga.2018 | 200 | 834,800 | `fb5e0ff9c5ccd462be9f3684b3c5f1117413d7d14c8f6783048465d8c199ad45` | Manifest only; files_count 3219; release86.2022.11 present; prior 2026-10-22 hash differed |

Preferred bulk unannotated source remains this archive. Lexis was not scraped. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-25-ocga-release86-metadata.md`.

(See full historical inventory in prior commits; this update prepends the 2026-10-26 Court of Appeals domain entry.)
