# Supreme Court forthcoming opinions index checkpoint (2026-10-19)

Fetch date: 2026-10-19 05:01 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| forthcoming opinions index | https://www.gasupreme.us/forthcoming-opinions/ | 200 | 1,588,959 | `9a6445236c97be8e0f3065d64e53d10b91416775c4fb586a254fd42deaf83f27` | 20 PDF anchors (20 unique, all docket-labeled); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The forthcoming index names 20 unique docket-labeled PDF links (examples S25G1209, S26A0699, S26Y0645; announcement date Wednesday, October 14, 2026). All point under /wp-content/uploads/. robots.txt disallows that path, so none of those PDFs were fetched. Lexis was not opened. Court of Appeals rules and opinion-search pages continue to return WAF or captcha on raw fetch. These counts are not persisted coverage.

Gap notes: inventory of the forthcoming index labels only. Opinion PDFs remain unfetched. Missing DATABASE_URL means no corpus rows can be written. Currency is unknown; forthcoming opinions are subject to modification or withdrawal before publication.
