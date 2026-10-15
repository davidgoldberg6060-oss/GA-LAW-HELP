# Court of Appeals rules index — discover-only checkpoint

Fetch date: 2026-10-14 (UTC). DATABASE_URL was unset, so no files were downloaded and no corpus rows were written.

Direct curl fetches of https://www.gaappeals.gov/ and https://www.gaappeals.gov/robots.txt returned HTTP 405 with x-amzn-waf-action: captcha (2511-byte captcha page). Content inspection tools retrieved the homepage and individual rules pages (e.g. /rules-1-8/, /rules-33-36/).

| Source | URL | HTTP (tool) | Notes |
| --- | --- | --- | --- |
| homepage | https://www.gaappeals.gov/ | 200 | Intermediate appellate court; 15 judges; jurisdiction except constitutional, murder, habeas (to Supreme Court) |
| robots.txt | https://www.gaappeals.gov/robots.txt | 200 | Allows general access; disallows only /wp-admin/ (except admin-ajax.php). SHA-256 of retrieved text: f72b00f6ff32e23dccd35f70ed58ed2303c46207ab25c8ff8054f11f3d4f4fc2 |
| rules 1-8 | https://www.gaappeals.gov/rules-1-8/ | 200 | Effective March 26, 2026; general provisions |
| rules 33-36 | https://www.gaappeals.gov/rules-33-36/ | 200 | Decisions and judgments; published opinions as binding precedent |

Opinion search (https://www.gaappeals.gov/opinion-search/) is a date-range form, not a static annual index of PDF links like the Supreme Court site. No opinion PDFs or full rule compilations were fetched. Lexis was not opened. These are index/page labels only, not stored rule text, not current-law verification, and not persisted coverage.

Gap notes: WAF blocks unauthenticated bulk fetches; individual rules pages exist but were not bulk-downloaded. Companion Supreme Court / Uniform rules indexes were checkpointed 2026-10-13. Missing DATABASE_URL means no authority rows can be written.
