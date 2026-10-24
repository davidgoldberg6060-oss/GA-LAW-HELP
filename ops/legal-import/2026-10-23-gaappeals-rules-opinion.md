# Court of Appeals of Georgia rules index and opinion-search (discover-only)

Fetch date: 2026-10-23 20:00 EDT (2026-10-24 00:00 UTC approx).
DATABASE_URL was unset in this environment; no corpus rows were written; no coverage is claimed.
Raw HTTP fetch of both pages returns HTTP 405 with AWS WAF captcha (content-length 2511). Browser-accessible reads of the same URLs succeeded. No rule text or opinion PDFs were downloaded or stored. Lexis was not opened. These notes are not persisted coverage and are not current-law verification.

| Source | URL | HTTP (raw) | Notes |
| --- | --- | ---: | --- |
| rules index | https://www.gaappeals.gov/court-rules/ | 405 (WAF) | Lists 20+ rule-group pages (Rules 1-8 General through Rule 46 Electronic Filing, etc.). Effective dates noted on individual pages (e.g. Rules 1-8 effective March 26, 2026). No full rulebook PDF stored. |
| opinion-search | https://www.gaappeals.gov/opinion-search/ | 405 (WAF) | Search-by-date form only; links to Docket/Case Inquiry. No opinion list or PDFs named. |
| rules example | https://www.gaappeals.gov/rules-1-8/ | 200 (via browser tool) | HTML text of Rules 1-8 (Clerk hours, filings, fees, service, etc.). Effective March 26, 2026. Not stored as authority. |

Gaps: WAF blocks unauthenticated/raw crawls; opinion archive is search-only (no bulk index); full rulebook may exist as PDF elsewhere but not fetched here; no unannotated OCGA or Supreme Court materials in this checkpoint. Checkpoint does not invent text or claim ingestion.
