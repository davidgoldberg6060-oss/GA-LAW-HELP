Last production check: 2026-10-23 12:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals of Georgia opinion-search index and robots.txt. Both returned the AWS WAF Human Verification captcha; opinion PDFs were not downloaded; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `1cffc011a4465c8e4d7b5e80fdb44783d3bdf68d408f72baf78810aaca2bec5b` | WAF captcha page; not an opinion index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `c7c539ffc0d5c141d8156985900c22a6179a038e5dd727763c69f14acff0f9ac` | Same WAF captcha page |

Raw fetch returned the AWS WAF challenge. No docket-labeled PDF links were named. The date-search endpoint was not called. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-appeals-opinion-search.md`.

Last production check: 2026-10-23 09:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Judicial Council / Administrative Office of the Courts Supreme Court and related rules index (https://georgiacourts.gov/georgia-supreme-court-rules/). Index bytes were hashed; PDF anchors counted; gasupreme.us robots.txt disallows /wp-content/uploads/ so no PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://georgiacourts.gov/georgia-supreme-court-rules/ | 200 | 104,434 | `8fc27ecebaa34124a3ed2169192c825400992959bbb8ea00653afd47c2287cb3` | 28 PDF anchors, all under www.gasupreme.us/wp-content/uploads/; robots on gasupreme.us disallow /wp-content/uploads/ |

The index names 28 unique PDF links (Supreme Court Rules eff. 1.1.24, Uniform Superior/State/Juvenile/Probate/Magistrate/Municipal Court Rules of various dates, Statewide Business Court, Unified Appeal, Uniform Misdemeanor Citation, Transfer Rule, Interpreting, Jury Composition, JQC Rules, and others). None were fetched. More recent versions exist on the gasupreme.us other-court-rules index. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-georgiacourts-rules-index.md`.
