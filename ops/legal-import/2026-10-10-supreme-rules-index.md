# Supreme Court of Georgia Rules index — discover-only checkpoint

Fetch date: 2026-10-10 (UTC). DATABASE_URL was unset, so no rule PDFs were downloaded and no corpus rows were written.

Sources:
- https://www.gasupreme.us/rules/
- https://www.gasupreme.us/rules/former-rules/
- https://www.gasupreme.us/robots.txt

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| current rules index | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `3f7e7a80cb1bb297266d45d2ccf46792d66061e5f485ad7b1618d5946f557dab` | Index page only |
| former rules page | https://www.gasupreme.us/rules/former-rules/ | 200 | 1,707,016 | `e5d41324d9182e148083abde8f73adf3f3fcf2d9ed8420a6d191694a6caf385b` | Embeds prior rule text; not a PDF archive list |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows /wp-content/uploads/ |

The current rules index names three PDF links under /wp-content/uploads/ (not fetched because robots.txt disallows that path):

| Label | Path |
| --- | --- |
| Rules of the Supreme Court (Effective July 2, 2026) | /wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf |
| Rule Changes & Amendment History (Chart – 2026 Updates) | /wp-content/uploads/2026/07/CHART-WEB-POSTING-July-2-2026.pdf |
| Quick Reference | /wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf |

The former-rules page states that Court Rules were amended on January 1, 2024, and points readers to the current Rules PDF. It embeds numbered former rule headings (Rule 1 through later rules) as HTML, not as downloadable archived PDFs. No full rule text was stored from that page.

Gap notes: inventory of the official rules index only. Rule PDFs were not downloaded. This is not stored court-rule text, not proof of current law, and not persisted coverage. Lexis was not opened. A missing DATABASE_URL means no authority rows can be written. Court of Appeals rules pages were not re-fetched this run (prior 2026-10-08 check returned HTTP 405 WAF pages).
