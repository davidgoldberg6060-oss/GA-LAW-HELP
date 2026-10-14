# Court of Appeals opinion-search — discover-only gap checkpoint

Fetch date: 2026-10-14 (UTC). DATABASE_URL was unset, so no corpus rows were written.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion-search page | https://www.gaappeals.gov/opinion-search/ | 405 | n/a | n/a | WAF captcha (x-amzn-waf-action: captcha); Human Verification page; no index or opinion list returned |
| robots.txt | https://www.gaappeals.gov/robots.txt | 200 | 122 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Allows all except /wp-admin/; Sitemap listed |

robots.txt permits the path, but CloudFront WAF returns captcha / Human Verification. No docket-labeled PDF links, no annual index, and no opinion text were obtained. Docket search (https://www.gaappeals.gov/docket-search/) was not further probed. Lexis was not opened. These counts are not persisted coverage. Companion Supreme Court opinion indexes were previously inventoried; this COA source remains a gap.

Gap notes: WAF block prevents automated discover-only fetch of opinion indexes or PDFs. No corpus rows written. Missing DATABASE_URL means no authority rows can be written. Manual or alternate official source may be required for COA opinions.