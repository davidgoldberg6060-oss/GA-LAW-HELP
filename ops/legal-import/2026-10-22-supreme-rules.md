# 2026-10-22 Supreme Court rules index checkpoint

DATABASE_URL was unset. Discover-only fetch of the Supreme Court of Georgia rules index (https://www.gasupreme.us/rules/) and robots.txt.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,313 | `a5a05031430f063625ce8cc1c2f8621515cb9d231133d1814cac27fbd974f9c7` | 3 PDF anchors (Supreme Court Rules eff. July 2, 2026; chart; quick-reference); robots disallow /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The index names the current Supreme Court Rules PDF (effective July 2, 2026) plus companion chart and quick-reference. All under /wp-content/uploads/. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. No corpus rows written.
