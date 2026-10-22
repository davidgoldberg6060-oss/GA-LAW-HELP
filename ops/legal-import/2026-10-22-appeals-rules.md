# 2026-10-22 Court of Appeals rules index checkpoint

DATABASE_URL was unset. Discover-only raw fetch of Court of Appeals rules pages returned AWS WAF captcha. No rule text was stored. Not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `fe342b0b361532beab155782fb34b72f887c76ef0452fdf520c45141d6f0c9b1` | WAF captcha; not rule text |
| rules 1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `68c77b7561765f7f314065e7e4ebaa7da025d59185a57b049d91f4431eb7e9ad` | WAF captcha; not rule text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `6f6c93f471077686c272395d6325401e3b5a5ff08eef110b11b082ad109867cb` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge on all tested paths. No PDF or HTML rule text was downloaded. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.
