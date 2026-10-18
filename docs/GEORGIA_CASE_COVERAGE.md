Last production check: 2026-10-18 04:04 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Courts Supreme Court rules index and robots.txt. Index bytes were hashed; PDF anchors counted; targets are on gasupreme.us uploads which are robots-disallowed so no rule PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| Supreme Court rules index | https://georgiacourts.gov/georgia-supreme-court-rules/ | 200 | 104,434 | `49741ccd480f39d93a5505233a12269bfd11d0b3297182ecdc0c7b720895a957` | 28 unique PDF anchors pointing at gasupreme.us uploads |
| robots.txt | https://georgiacourts.gov/robots.txt | 200 | 118 | `a9dffa4bb5c0fc6ea8aa71450e41d843e36033a7bce006356850dad36c3e33c0` | Disallows /wp-admin/ only |

The index names 28 unique PDF links (Supreme Court Rules effective 2024, Uniform Superior/State/Juvenile/Probate/Magistrate/Municipal Court Rules, Statewide Business Court, related orders and charts). None of those PDFs were fetched. Lexis was not opened. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-18-georgiacourts-rules-index.md`.

