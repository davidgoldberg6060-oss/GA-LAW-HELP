Last production check: 2026-10-24 16:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals of Georgia page on georgiacourts.gov. Raw page bytes hashed; no PDFs downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| COA index page | https://georgiacourts.gov/court-of-appeals/ | 200 | 76,152 | `a838f778d4d53545f051162d8a7a6fd07c0973d09c083ccc1e4de5f38d88e0f7` | Official Court of Appeals gateway. No direct PDF anchors in static HTML. |
| robots.txt | https://georgiacourts.gov/robots.txt | 200 | 118 | `a9dffa4bb5c0fc6ea8aa71450e41d843e36033a7bce006356850dad36c3e33c0` | Disallow /wp-admin/; sitemap present. |

The page is the Judicial Council gateway for the Court of Appeals. No bulk opinion texts fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-24-court-of-appeals-index.md`.

Last production check: 2026-10-24 08:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia General Assembly homepage for official OCGA access point. Raw homepage bytes hashed; LexisNexis portal not opened or scraped; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage (raw) | https://www.legis.ga.gov/ | 200 | 1,492 | `301e217dc5d384b4243ee12b56ae51d5ecf1d0b0becedae1da952a1d361bac65` | Minimal HTML shell; JS-rendered content links to http://www.lexisnexis.com/hottopics/gacode for free official OCGA. |

The site provides the official free OCGA portal via LexisNexis (annotations included post-2020). Lexis was not scraped. Preferred bulk source remains Public.Resource.Org. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-24-legis-ocga-access.md`.

(See full historical inventory in prior commits; this update prepends the 2026-10-24 COA entry.)
