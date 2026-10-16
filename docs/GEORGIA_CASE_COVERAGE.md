Last production check: 2026-10-16 06:19 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Secretary of State Rules and Regulations download page (https://rules.sos.ga.gov/Download_pdf.aspx) and robots.txt. Page bytes were hashed; department PDFs were not downloaded; not stored regulation text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| download page | https://rules.sos.ga.gov/Download_pdf.aspx | 200 | 163,973 | `36fca85cfbc0836a8b9afed0a2220c5a68693976115be7b1ac9164f1489e442f` | HTML index; current through September 17, 2026 |
| robots.txt | https://rules.sos.ga.gov/robots.txt | 200 | 3,628 | `c7ade8fc670dbef7bf1610f34f7b5484cd478e83cb35b67c2cd0456418d80fd0` | Allows department PDF downloads; disallows per-rule HTML |

The download page names approximately 154 unique department PDF labels. None were fetched. Lexis was not opened. Court of Appeals rules pages returned WAF captcha on raw fetch. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-sos-rules-download.md`.

