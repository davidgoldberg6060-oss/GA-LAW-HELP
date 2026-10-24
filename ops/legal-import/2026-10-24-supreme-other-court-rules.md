# 2026-10-24 Supreme Court other-court-rules index checkpoint

DATABASE_URL was unset. No rule PDFs were downloaded and no authority rows were written. Raw fetch of the other-court-rules index succeeded (HTTP 200, 1,586,239 bytes, SHA-256 103fc65aad2c1fd6ade1777c2594e773d4b293c633b0f312429c074845810167). 7 unique PDF anchors under /wp-content/uploads/; robots.txt disallows that path. No corpus coverage claimed. Lexis not opened.

## Sources hashed

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| other-court-rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,586,239 | `103fc65aad2c1fd6ade1777c2594e773d4b293c633b0f312429c074845810167` | 7 unique PDF anchors (Uniform Superior 2026-04-09, State 2024-01-18, Juvenile 2026-09-03, Probate 2023-06-01, Magistrate 2023-04-01, Municipal 2024-12-12, Statewide Business 2026-06-11); all under /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

## Gap notes

The index names 7 Uniform/other court rule PDF links. robots.txt disallows /wp-content/uploads/, so none were fetched. Filenames are index labels, not effective dates and not stored rule text. Court of Appeals rules pages returned AWS WAF captcha on raw fetch (HTTP 405). These counts are not persisted coverage.
