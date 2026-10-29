# 2026-10-29 Supreme Court forthcoming opinions index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia forthcoming opinions page. Index bytes hashed; PDF anchors counted; uploads are robots-disallowed so no opinion PDFs were downloaded; not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| forthcoming opinions | https://www.gasupreme.us/opinions/forthcoming-opinions/ | 200 | 1,595,041 | `44b09a9c7fdf92583f37c0f1eae9cc273c8fe3e1b98ed10a3efcef18301b47e7` | 11 PDF anchors under /wp-content/uploads/2026/10/ (S26A0636 et al.); robots disallow |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/; Disallow: /readme.html |

The page lists forthcoming opinions for October 27, 2026 (11 PDF links). robots.txt disallows /wp-content/uploads/, so none were fetched. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the index page only. Appellate opinion PDFs remain behind robots disallow. Preferred sources for bulk opinions remain CourtListener or other public indexes once DATABASE_URL is set and reviewed.
