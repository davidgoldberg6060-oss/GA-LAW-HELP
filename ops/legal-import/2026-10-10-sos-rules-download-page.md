# SOS Rules and Regulations download page — discover-only checkpoint

Fetch date: 2026-10-10 (UTC). DATABASE_URL was unset, so no department PDFs were downloaded and no corpus rows were written.

Source: https://rules.sos.ga.gov/Download_pdf.aspx

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| download page | https://rules.sos.ga.gov/Download_pdf.aspx | 200 | 163,973 | `36fca85cfbc0836a8b9afed0a2220c5a68693976115be7b1ac9164f1489e442f` | Department PDF labels only |
| robots.txt | https://rules.sos.ga.gov/robots.txt | 200 | 3,406 | `9b7272de9a8a6ecdc6d70e11948738271558e464cde15739728fc7f1098c0bca` | Allows general access; disallows specific bots |

The page names 154 unique departments (examples: Department 20. RULES OF STATE BOARD OF ACCOUNTANCY; Department 40. RULES OF GEORGIA DEPARTMENT OF AGRICULTURE). Current-through label on the home page is September 17, 2026. None of the department PDFs were fetched. The site states that Fastcase is the designated publisher; XML feeds were not requested. Lexis was not opened. These labels are not stored rule text and not current-law verification. A missing DATABASE_URL means no authority rows can be written.

Gap notes: inventory of download-page labels only. Full rule text requires per-department PDF download under a configured DATABASE_URL and after robots/terms review. Court of Appeals opinion search remains blocked by WAF (HTTP 405). No corpus rows written.
