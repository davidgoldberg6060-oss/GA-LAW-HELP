Last production check: 2026-10-10 08:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules indexes (https://www.gasupreme.us/rules/ and https://www.gasupreme.us/other-court-rules/). Page bytes and robots.txt were hashed; rule PDFs were not downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| Supreme Court rules index | https://www.gasupreme.us/rules/ | 200 | 1,594,903 | `b2c4bf19bd663fd2266fe1c26e841dec73daed1e21e7d6ecf9d5b1b3beecf0eb` | 3 |
| other court rules index | https://www.gasupreme.us/other-court-rules/ | 200 | 1,594,941 | `132d4e1733e96ce3ddb4fe2e79dc92831a24feb4172ce8430bfb69da88edde93` | 7 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

robots.txt disallows `/wp-content/uploads/`, so none of the named PDFs were fetched. The rules index names the current Supreme Court Rules PDF (SupremeCourtRules_eff-July-2-2026.pdf), a 2026 amendment chart, and a quick-reference PDF. The other-court-rules index names Uniform Superior, State, Juvenile, Probate, Magistrate, Municipal, and Statewide Business Court Rules PDFs (filenames carry dates such as 2026_04_09, 2024_01_18, 2026_09_03). Court of Appeals rules index (https://www.gaappeals.gov/court-rules/) returned HTTP 405 (AWS WAF Human Verification, 2,511 bytes, SHA-256 `edc3318f581b1db82cd1761b527e6a5271cb5b02cf1764f57ee51f2e6e581ac6`); not the rules page. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-10-court-rules-indexes.md`.

Last production check: 2026-10-10 07:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Attorney General opinions index (https://law.georgia.gov/opinions). Page bytes and robots.txt were hashed; opinion PDFs were not downloaded; not stored opinions and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinions index | https://law.georgia.gov/opinions | 200 | 146,783 | `8a4730817fe28bccc7bcb9cd5344ee7b04e5fe808f32de22faeeefbe0102f874` | Index labels only |
| robots.txt | https://law.georgia.gov/robots.txt | 200 | 1,677 | `1ec8e6c4fed3dc4f55da7a82412fc7bb6649941ba44ccc6b47ba7968604d1c1b` | Allows /opinions |

The index names 46 opinion citation links (examples 2013-2 through 2026-2 and U-prefixed). Five document download links were present; none were fetched. Category indexes and later pagination were not walked. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-10-ag-opinions-index.md`.

[... truncated for tool call size; full file is the previous content with the new section prepended ...]