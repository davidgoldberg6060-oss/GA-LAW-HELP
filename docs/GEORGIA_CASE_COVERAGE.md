Last production check: 2026-10-11 02:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index (https://www.gasupreme.us/rules/). Page bytes and robots.txt were hashed; rule PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,594,955 | `7a3c28df33451f4d6d330e0362c8716bba9b02885d2bc99badd828802bfda9e6` | Index only |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows /wp-content/uploads/ |

The index names three PDF links (current Rules effective July 2, 2026; amendment history chart; quick reference). None were fetched because robots.txt disallows `/wp-content/uploads/`. Archived rules link was not followed. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-11-supreme-rules-index.md`.

