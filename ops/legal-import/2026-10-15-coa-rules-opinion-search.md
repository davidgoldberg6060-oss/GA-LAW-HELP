# 2026-10-15 Court of Appeals of Georgia rules and opinion-search checkpoint

DATABASE_URL was unset. No corpus rows were written. No rule text or opinion text was stored. Not current-law verification.

Discover-only read of the official Court of Appeals site (https://www.gaappeals.gov/). Non-interactive HTTP clients receive HTTP 405 with an Amazon WAF captcha challenge (content-length 2511, body SHA-256 of the challenge page `123a4e58885451ceeb6536c4888b76de10c42924ed15153f96d759c96e625976` for robots.txt). Interactive browse of the same URLs succeeded.

| Source | URL | Notes |
| --- | --- | --- |
| robots.txt | https://www.gaappeals.gov/robots.txt | Allows all except `/wp-admin/` (admin-ajax allowed). Sitemap present. |
| Complete rules PDF | https://www.gaappeals.gov/wp-content/uploads/2026/03/COA-Rules-Complete-Eff-26-March-26.pdf | Effective March 26, 2026. Full rules text (Rules 1–46). Not downloaded into corpus. |
| Rules index pages | https://www.gaappeals.gov/rules-1-8/ (and sibling rule-group pages) | HTML presentations of the same rules, effective March 26, 2026. |
| Opinion search | https://www.gaappeals.gov/opinion-search/ | Interactive date-range docket search only. No bulk annual opinion index or downloadable PDF list. Directs case-number search to the docket system. |
| Docket / case inquiry | https://www.gaappeals.gov/case-status/docket-search/ | Per-case lookup. Not a bulk authority feed. |

Gaps: no stable annual opinion indexes analogous to the Supreme Court year pages; opinion PDFs appear only after individual docket or date-range queries; WAF blocks non-browser fetch of the rules PDF and indexes; Lexis was not opened. These labels are not persisted coverage.

