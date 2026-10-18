Last production check: 2026-10-18 04:04 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Courts Supreme Court rules index and robots.txt. Index bytes were hashed; PDF anchors counted; targets are on gasupreme.us uploads which are robots-disallowed so no rule PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| Supreme Court rules index | https://georgiacourts.gov/georgia-supreme-court-rules/ | 200 | 104,434 | `49741ccd480f39d93a5505233a12269bfd11d0b3297182ecdc0c7b720895a957` | 28 unique PDF anchors pointing at gasupreme.us uploads |
| robots.txt | https://georgiacourts.gov/robots.txt | 200 | 118 | `a9dffa4bb5c0fc6ea8aa71450e41d843e36033a7bce006356850dad36c3e33c0` | Disallows /wp-admin/ only |

The index names 28 unique PDF links (Supreme Court Rules effective 2024, Uniform Superior/State/Juvenile/Probate/Magistrate/Municipal Court Rules, Statewide Business Court, related orders and charts). None of those PDFs were fetched. Lexis was not opened. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-18-georgiacourts-rules-index.md`.

Last production check: 2026-10-16 14:10 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules amendments index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no order PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| amendments index | https://www.gasupreme.us/rules/amendments-to-rules/ | 200 | 1,700,777 | `b3a3c78bb62222c4b5f8eaf76f46d532a45c740db78534e226f57b4508de57cd` | 309 PDF anchors (299 unique); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The amendments index names approximately 299 unique order/PDF links (examples from 2015–2026 covering Uniform Superior Court Rules, Juvenile, Municipal, Statewide Business Court, Supreme Court Rules amendments, and related orders). None of those PDFs were fetched. Lexis was not opened. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-supreme-amendments.md`.

