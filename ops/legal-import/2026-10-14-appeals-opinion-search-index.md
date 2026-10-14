# Court of Appeals opinion-search index — discover-only checkpoint

Fetch date: 2026-10-14 (UTC). DATABASE_URL was unset, so no corpus rows were written. Automated fetch of the public opinion-search page and robots.txt was blocked by AWS WAF captcha (HTTP 405, Human Verification page). No opinion PDFs were named or downloaded. Not stored opinions and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search index | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `0a431c3d159fffb3b68ad1fbcf047e9271e6fa4156adbbfbfdbc837b079e69a7` | WAF captcha; not the index HTML |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `09ba0beb1783510507e76a4c0a36fefa506ba9e0db5d2819d769b5bb010d724b` | WAF captcha; expected content not retrieved |

The importer's `discover_index` would treat this as a non-opinion index (WAF captcha or non-200). Prior public knowledge of the page (via other tools) confirms it hosts a date-range docket search form that links to efast.gaappeals.gov PDFs, but this automated checkpoint did not retrieve the form HTML or any PDF links. Lexis was not opened. These counts are not persisted coverage.

Gap notes: AWS WAF blocks unauthenticated automated access to www.gaappeals.gov. No opinion PDFs downloaded. Missing DATABASE_URL means no authority rows can be written. Court of Appeals rules pages remain unfetched. Companion Supreme Court indexes were checkpointed separately.
