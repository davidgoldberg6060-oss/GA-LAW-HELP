Last production check: 2026-10-16 22:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only raw fetch of Court of Appeals rules HTML section and robots.txt returned AWS WAF captcha. Not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules 1-8 | https://www.gaappeals.gov/rules-1-8/ | 405 | 2,511 | `63494b675cfc8b7abcf41511110d293b07484a551f6db1aa329e55d19534407f` | WAF captcha; not rules text |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `41a114491cd50d27bdc386696eceb7eb0bdc645e35b444eee27e5e8f53c480d8` | Same WAF captcha |

The site publishes sectioned HTML rules effective March 26, 2026 and a complete PDF; none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-appeals-rules-html.md`.

