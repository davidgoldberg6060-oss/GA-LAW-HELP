Last production check: 2026-10-16 05:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only hashed the 2026 annual opinion index and robots.txt (page bytes and PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,625,440 | `8e9d34f4a8465508d5259d9b701ea54d8af51143b16b52e32e9ed2cea78e3896` | 283 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

robots.txt disallows `/wp-content/uploads/`, so none of the named PDF files were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-supreme-2026-opinions.md`.

