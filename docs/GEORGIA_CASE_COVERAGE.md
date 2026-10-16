Last production check: 2026-10-16 05:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only hashed the 2026 annual opinion index and robots.txt (page bytes and PDF link labels only; opinion PDFs not downloaded; not stored opinions and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| 2026 opinions index | https://www.gasupreme.us/2026-opinions/ | 200 | 1,625,440 | `8e9d34f4a8465508d5259d9b701ea54d8af51143b16b52e32e9ed2cea78e3896` | 283 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

robots.txt disallows `/wp-content/uploads/`, so none of the named PDF files were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-16-supreme-2026-opinions.md`.

Last production check: 2026-10-15 22:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals opinion-search index and robots.txt. Page bytes were hashed; both returned the AWS WAF captcha; opinion PDFs were not downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `a60e59e2e67412d10f9968a360c89a48e30fec247553546c59d17638a0c444c4` | WAF captcha; not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `6f6c93f471077686c272395d6325401e3b5a5ff08eef110b11b082ad109867cb` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge. No docket-labeled PDF links were named. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-15-appeals-opinion-search.md`.

