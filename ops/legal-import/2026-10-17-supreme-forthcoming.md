# Supreme Court forthcoming opinions index checkpoint (2026-10-17)

Fetch date: 2026-10-17 02:01 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| forthcoming opinions | https://www.gasupreme.us/opinions/forthcoming-opinions/ | 200 (body) / 403 (HEAD) | 1,589,019 | `3a5eb03efba18d6143976b1a8d2831d55e1067a56c4ad8c94dc69d2f5bad6c6d` | 20 PDF anchors (20 unique); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The forthcoming opinions page names 20 unique opinion PDF links under /wp-content/uploads/ (examples: s25g1209.pdf, s25g1430.pdf, s26a0699.pdf, s26a0723.pdf, s26a0733.pdf). None of those PDFs were fetched because robots.txt disallows `/wp-content/uploads/`. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the forthcoming index only. Opinion PDFs remain unfetched. Missing DATABASE_URL means no corpus rows can be written. Currency and precedential status are unknown. Court of Appeals opinion-search continues to return AWS WAF captcha on raw fetch.
