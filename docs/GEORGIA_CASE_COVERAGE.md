Last production check: 2026-10-25 02:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals of Georgia homepage (gaappeals.us) which serves the docket-search shell linking to official .gov opinion-search and rules. Raw homepage bytes hashed; opinion-search and rules pages behind AWS WAF captcha so not retrieved; no PDFs downloaded; not stored opinion or rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage (raw) | https://gaappeals.us/ | 200 | 39,314 | `4c92b0d07ca7b0a76fd30ecdb37fbdfebaa77cb8e4a05685b4768b7f710d3d15` | Docket-search shell; links to https://www.gaappeals.gov/opinion-search/ and /rules-1-8/; TLS cert chain verify failed, fetch continued. |

Opinion-search and rules URLs returned Human Verification captcha. No private dockets fetched. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-25-coa-access.md`.

Last production check: 2026-10-24 08:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia General Assembly homepage for official OCGA access point. Raw homepage bytes hashed; LexisNexis portal not opened or scraped; not stored statute text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage (raw) | https://www.legis.ga.gov/ | 200 | 1,492 | `301e217dc5d384b4243ee12b56ae51d5ecf1d0b0becedae1da952a1d361bac65` | Minimal HTML shell; JS-rendered content links to http://www.lexisnexis.com/hottopics/gacode for free official OCGA. |

The site provides the official free OCGA portal via LexisNexis (annotations included post-2020). Lexis was not scraped. Preferred bulk source remains Public.Resource.Org. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-24-legis-ocga-access.md`.

Last production check: 2026-10-23 17:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no rule PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,244 | `4ffe25395619943f6f19c943932272c97907748dc7e9a389964676693a308729` | 3 PDF anchors under /wp-content/uploads/ (Supreme Court Rules eff. July 2, 2026; chart; quick-reference); robots disallow |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The rules index names the Supreme Court Rules PDF effective July 2, 2026, a chart, and a quick-reference PDF. robots.txt disallows /wp-content/uploads/, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-supreme-rules-index.md`.

(See full historical inventory in prior commits; this update restores the complete report with the new 2026-10-25 entry at the top.)
