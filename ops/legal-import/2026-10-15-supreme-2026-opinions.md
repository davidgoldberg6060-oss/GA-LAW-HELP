# Supreme Court of Georgia 2026 opinions index checkpoint (2026-10-15)

Fetch date: 2026-10-15 23:01 UTC. DATABASE_URL is unset. No opinion PDFs were downloaded. No authority rows were written. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,625,440 | `6e62bbfd1c10851f9a536b912ce353585b7b0a9e88792f7c9814cc2e073a0ace` | Index labels only; 283 unique uploads PDF URLs named |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallows `/wp-content/uploads/` |

The index names 283 unique PDF links under `/wp-content/uploads/`. robots.txt disallows that path, so none of those files were fetched. No docket token was observed mapping to more than one PDF URL in a quick scan of the raw HTML. Lexis was not opened. These counts are not persisted coverage.

Gap notes: inventory of index labels and page hash only. Opinion PDFs remain unfetched due to robots.txt. Missing DATABASE_URL means no corpus rows can be written. Prior checkpoints covered 2017–2025 annual indexes; this adds the current 2026 page.
