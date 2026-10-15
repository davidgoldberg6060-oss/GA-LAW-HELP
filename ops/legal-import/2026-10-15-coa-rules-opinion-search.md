# 2026-10-15 Court of Appeals of Georgia rules and opinion-search checkpoint

DATABASE_URL was unset. No rule text, opinion indexes, or PDFs were downloaded and no corpus rows were written.

Raw fetches (curl, no browser) of the following returned HTTP 405 with AWS WAF captcha challenge (content-length 2511, content-type text/html):

| Source | URL | HTTP | Bytes | SHA-256 (of captcha page) | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules 1-8 page | https://www.gaappeals.gov/rules-1-8/ | 405 | 2511 | `2a407c3795ec95a53a8cd2dcd29e379b83a81eb4ff404ba0f61567fee6e7c126` | WAF captcha; not rule text |
| opinion search | https://www.gaappeals.gov/opinion-search/ | 405 | 2511 | `bfefdcc8f77c3d3dd18a640fd37daa3729bcd4a1b030894550fd09bf05127098` | WAF captcha; not opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 200 | 71 | `f894a4abe6a216805305e40ace62dcf9ce97aa93925f7101529d0deff0f0a98a` | Disallows /wp-admin/ only; Sitemap present |

Browser-rendered access (separate tool) to https://www.gaappeals.gov/rules-1-8/ shows the page titled "Rules 1-8: General" and states "These rules are effective on March 26, 2026." It lists Rule 1 through Rule 6 text excerpts and links to a Spanish PDF of the complete rulebook (https://www.gaappeals.gov/wp-content/uploads/2026/03/ES-MX.completerulebook-32126-Final-1.pdf). That PDF was not downloaded. Opinion search page is a date-range form pointing to Docket/Case Inquiry System; no bulk annual opinion PDF index is exposed on the landing page. Lexis was not opened. These observations are not persisted coverage and not current-law verification. Court of Appeals opinions remain a gap relative to the Supreme Court annual indexes already checkpointed.

Fetch date: 2026-10-15 20:01 UTC.
