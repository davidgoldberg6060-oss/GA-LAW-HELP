# Supreme Court rules amendments index checkpoint (2026-10-16)

Fetch date: 2026-10-16 14:10 UTC. DATABASE_URL is unset. No order PDFs were downloaded. No authority rows were written. This is not stored rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| amendments index | https://www.gasupreme.us/rules/amendments-to-rules/ | 200 | 1,700,777 | `b3a3c78bb62222c4b5f8eaf76f46d532a45c740db78534e226f57b4508de57cd` | 309 PDF anchors (299 unique); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The amendments index names approximately 299 unique order/PDF links (examples under /wp-content/uploads/ from 2015–2026 covering Uniform Superior Court Rules, Juvenile, Municipal, Statewide Business Court, Supreme Court Rules amendments, and related orders). None of those PDFs were fetched because robots.txt disallows `/wp-content/uploads/`. Lexis was not opened. Court of Appeals rules pages continue to return AWS WAF captcha on raw fetch. These counts are not persisted coverage.

Gap notes: inventory of the amendments index only. Order PDFs remain unfetched. Missing DATABASE_URL means no corpus rows can be written. Currency is unknown pending later official comparison of effective dates against the current rules PDFs.
