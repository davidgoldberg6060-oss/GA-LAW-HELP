Last production check: 2026-10-15 20:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of Georgia Court of Appeals rules and opinion-search pages returned HTTP 405 AWS WAF captcha (2511 bytes); not stored rule text, not opinion indexes, and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules 1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2511 | `2a407c3795ec95a53a8cd2dcd29e379b83a81eb4ff404ba0f61567fee6e7c126` | WAF captcha page |
| opinion search | https://www.gaappeals.gov/opinion-search/ | 405 | 2511 | `bfefdcc8f77c3d3dd18a640fd37daa3729bcd4a1b030894550fd09bf05127098` | WAF captcha page |
| robots.txt | https://www.gaappeals.gov/robots.txt | 200 | 71 | `f894a4abe6a216805305e40ace62dcf9ce97aa93925f7101529d0deff0f0a98a` | Disallows /wp-admin/ only |

Browser-rendered rules page states rules effective March 26, 2026 and links a Spanish complete-rulebook PDF that was not downloaded. Opinion search is a date-range form with no bulk annual index. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-15-coa-rules-opinion-search.md`.

Previous production checks (full historical log preserved in prior commits and this file's git history):

Last production check: 2026-10-15 13:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Public.Resource.Org OCGA release manifest... (see full file for complete prior entries).
