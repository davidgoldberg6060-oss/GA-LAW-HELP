# GA Rules and Regulations download-page checkpoint (2026-10-16)

Fetch date: 2026-10-16 06:19 UTC. DATABASE_URL is unset. No department PDFs were downloaded. No authority rows were written. This is not stored regulation text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| download page | https://rules.sos.ga.gov/Download_pdf.aspx | 200 | 163,973 | `36fca85cfbc0836a8b9afed0a2220c5a68693976115be7b1ac9164f1489e442f` | HTML index of department PDFs; current through September 17, 2026 |
| robots.txt | https://rules.sos.ga.gov/robots.txt | 200 | 3,628 | `c7ade8fc670dbef7bf1610f34f7b5484cd478e83cb35b67c2cd0456418d80fd0` | Allows per-department PDF downloads on `/Download_pdf.aspx`; Crawl-delay present; disallows per-rule HTML |

The download page names approximately 154 unique department PDF labels (examples: Department 100 RULES OF GEORGIA BOARD OF CHIROPRACTIC EXAMINERS, Department 111 RULES OF DEPARTMENT OF COMMUNITY HEALTH, Department 120 OFFICE OF COMMISSIONER OF INSURANCE...). None of those PDFs were fetched. The page states "Current through Rules and Regulations filed through September 17, 2026". Fastcase is the designated publisher. Lexis was not opened. Court of Appeals rules index and rules-1-8 page returned AWS WAF captcha on raw fetch (HTTP 405, ~2,511 bytes). These counts are not persisted coverage.

Gap notes: inventory of the download-page index only. Department PDFs remain unfetched. Missing DATABASE_URL means no corpus rows can be written. Currency is unknown pending later official comparison.
