# Court of Appeals homepage and robots.txt checkpoint — 2026-10-25

DATABASE_URL was unset, so no corpus rows were written. Discover-only. No opinion or rule PDFs were downloaded. Lexis was not opened. Not stored opinion or rule text and not current-law verification.

Raw non-browser fetch of the homepage and robots.txt returns the AWS WAF Human Verification challenge (HTTP 405). Browser-capable retrieval of robots.txt succeeds and returns the allow/disallow policy.

| Source | URL | HTTP (raw) | Bytes (raw) | SHA-256 (raw captcha) | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage | https://www.gaappeals.gov/ | 405 | 2,511 | `76ba51182f7bdf9bd88e83906c52fb8cc7595ca28aaf7199273f7d6086858873` | WAF captcha page; not the court homepage content |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `790a24b56942592c1680472cea5e942287407eb29848dfca30fe2ab7f527e04d` | WAF captcha page |

Browser-capable retrieval of robots.txt (2026-10-25) returned:

```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php

Sitemap: https://www.gaappeals.gov/sitemaps.xml
```

## Notes

- Homepage text extract (browser-capable) confirms the Court of Appeals of the State of Georgia description: intermediate appellate court, established 1906, fifteen judges in five divisions, statewide appellate jurisdiction except constitutional questions, murder, and habeas corpus (original jurisdiction with Supreme Court).
- Rules pages (e.g. https://www.gaappeals.gov/rules-1-8/, https://www.gaappeals.gov/rules-33-36/) are published and effective March 26, 2026 per public announcements; raw fetch remains WAF-blocked so no rule text was stored.
- Prior 2026-10-15 checkpoint recorded the same WAF response for the opinion-search index.
- Gap: Court of Appeals opinion indexes and rule PDFs remain unfetched from non-browser clients due to WAF. No authority rows can be written without DATABASE_URL. Preferred bulk sources for opinions remain public indexes that do not require captcha where available.

These counts are not persisted coverage. No corpus rows written.
