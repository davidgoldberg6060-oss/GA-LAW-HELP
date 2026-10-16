Last production check: 2026-10-16 13:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of the Court of Appeals rules index, a section page, and robots.txt. All returned the AWS WAF captcha; no rule text was obtained; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `250c72a072c5a247e052146e60c5929b5d4af960640581e016be756ef52858aa` | WAF captcha; not a rules index |
| rules 1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `5eb9ae13be78f8a67812f4f8724dec20c802526487431ab7dfab91d0b5bcf09e` | WAF captcha; not rule text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `6bed2fb82f90f8a01003e33310e250285736dd6e253b4a4042b58b2cfa436458` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge for each. No rule text or PDF links were named. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-appeals-rules.md`.

Last production check: 2026-10-16 06:19 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Secretary of State Rules and Regulations download page (https://rules.sos.ga.gov/Download_pdf.aspx) and robots.txt. Page bytes were hashed; department PDFs were not downloaded; not stored regulation text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| download page | https://rules.sos.ga.gov/Download_pdf.aspx | 200 | 163,973 | `36fca85cfbc0836a8b9afed0a2220c5a68693976115be7b1ac9164f1489e442f` | HTML index; current through September 17, 2026; ~154 department PDF labels |
| robots.txt | https://rules.sos.ga.gov/robots.txt | 200 | 3,628 | `c7ade8fc670dbef7bf1610f34f7b5484cd478e83cb35b67c2cd0456418d80fd0` | Allows department PDF downloads; disallows per-rule HTML |

The download page names approximately 154 unique department PDF labels. None were fetched. Lexis was not opened. Court of Appeals rules pages returned WAF captcha on raw fetch. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-sos-rules-download.md`.

[... full prior history restored from main; see commit for complete file ...]