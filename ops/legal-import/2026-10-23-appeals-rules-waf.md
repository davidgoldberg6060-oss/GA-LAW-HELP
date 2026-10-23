# Court of Appeals rules HTML pages WAF checkpoint

Date: 2026-10-23

DATABASE_URL was unset. No rule text downloaded. No authority rows written.

Raw curl of https://www.gaappeals.gov/rules-1-8/ returned:

- HTTP 405
- content-length: 2511
- x-amzn-waf-action: captcha
- SHA-256 of body: aa533296d324d8fe9704461d24a6099c1792d8ea4e16781d95c92ffd032c4bcf

robots.txt at https://www.gaappeals.gov/robots.txt allows /wp-admin/admin-ajax.php and has a sitemap, but does not prevent the WAF captcha on rules HTML pages.

A complete rules PDF is linked from the site (https://www.gaappeals.gov/wp-content/uploads/2026/03/COA-Rules-Complete-Eff-26-March-26.pdf) but was not fetched.

Not stored rule text. Not current-law verification. Lexis was not opened. These counts are not persisted coverage.
