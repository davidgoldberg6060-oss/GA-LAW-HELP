# 2026-10-29 Supreme Court of Georgia homepage checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only fetch of the Supreme Court homepage (https://www.gasupreme.us/). Homepage bytes hashed; no opinion PDFs, rules PDFs, or other files were downloaded. Lexis was not opened. This is not stored opinion or rule text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage | https://www.gasupreme.us/ | 200 | 1,606,323 | `de5502900a4a3de662a4016283253633c72a1c9f177b02a7ce68b6e2de258214` | Links to forthcoming-opinions, 2026-opinions, 2025-paqc-cases; no direct PDF anchors on homepage |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The homepage names opinion index paths including /forthcoming-opinions/ and /2026-opinions/. robots.txt disallows /wp-content/uploads/, so any PDFs there remain unfetched. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of the homepage and robots only. Appellate opinion indexes remain to be fetched in browser-capable or non-WAF environments. Missing DATABASE_URL means no corpus rows can be written. Preferred bulk unannotated OCGA source remains Public.Resource.Org. No Lexis annotations scraped.
