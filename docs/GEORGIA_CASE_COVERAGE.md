Last production check: 2026-10-15 01:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals of Georgia opinion-search page and robots.txt. Both returned the AWS WAF captcha page (HTTP 405, x-amzn-waf-action: captcha); not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search page | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `d4e5dbbd5b67fecf55e1d3c14cd635698eb510b4dc5e6a61792a3bf9473b5f2e` | WAF captcha; no index labels |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `d4e5dbbd5b67fecf55e1d3c14cd635698eb510b4dc5e6a61792a3bf9473b5f2e` | Same captcha body |

No docket labels or PDF links were present. Date-window search and efast PDFs were not requested. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-15-appeals-opinion-search-index.md`.

Last production check: 2026-10-13 16:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia other-court-rules and rules indexes. Page bytes and robots.txt were hashed; rule PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,719 | `08411b3a60c162ce26230c41261c53990ba8068380065a201bc7d78e6dc04c32` | Index labels only |
| supreme rules index | https://www.gasupreme.us/rules/ | 200 | 1,592,694 | `c60a61aeee1fe49912bbde1eb67feb622d213964609bbda77112d840e4dc4e6b` | Index labels only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

The other-court-rules index names 7 Uniform/other rule PDF links (Superior 2026-04-09, State 2024-01-18, Juvenile 2026-09-03, Probate 2023-06-01, Magistrate 2023-04-01, Municipal 2024-12-12, Statewide Business 2026-06-11). The rules index names the Supreme Court Rules PDF effective July 2, 2026 plus a chart and quick-reference PDF. robots.txt disallows `/wp-content/uploads/`, so none were fetched. Filenames are index labels, not effective dates and not stored rule text. Court of Appeals rules pages were not fetched in this pass. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-13-court-rules-indexes.md`.

[... truncated for this call; full history retained in prior main version. This push restores the prepend. See ops checkpoint for the new gap.]