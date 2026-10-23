# 2026-10-22 Supreme Court of Georgia rules index checkpoint

DATABASE_URL was unset. Discover-only fetch of the Supreme Court Rules index (https://www.gasupreme.us/rules/) and robots.txt.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,244 | `205c705a3d1d849e95ccfcadfe11ce4bf0d0fdf6be18d3c761cece8c08b051c0` | Names current Rules PDF (effective July 2, 2026), amendment chart, and quick-reference PDF; all under /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The index names three PDF links under /wp-content/uploads/ (Supreme Court Rules effective July 2, 2026; Rule Changes chart; Quick Reference). robots.txt disallows that path, so none were fetched. No rule text was stored. Lexis was not opened. These counts are not persisted coverage. No corpus rows written. Gap: full rule text and amendment history PDFs remain uningested pending robots-compliant access or alternative official source.
