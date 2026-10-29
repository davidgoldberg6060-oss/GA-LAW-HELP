# 2026-10-29 Court of Appeals opinion search index checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only raw automated fetch of the Court of Appeals of Georgia opinion search page. No opinion PDFs, dockets, or text files were downloaded. Lexis was not opened. This is not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion search (raw) | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `1003128ea5fd7f53d98c3fcb3df3835df72f3a6df1381edf49b161b4be6dc6c1` | AWS WAF Human Verification captcha challenge; site moved from gaappeals.us to gaappeals.gov |
| homepage (raw) | https://www.gaappeals.gov/ | 405 | 2,511 | `e652ec756c9d9ccba050f437ae884699ede7ca68f3c201409344a4918b7b3e30` | Same WAF challenge |
| robots.txt (raw) | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `48d2b702da3775f4fae4ffadb0537525e31d3c988af9b189ddda129cc7ca6d9b` | Same WAF challenge (content tool saw Allow: /wp-admin/admin-ajax.php; Sitemap) |

The Court of Appeals website has migrated to https://www.gaappeals.gov/. Opinion search is available at /opinion-search/ (date-range docket search; case number search via separate docket system). Automated raw fetches hit AWS WAF captcha. No opinions or rules PDFs were fetched. These counts are not persisted coverage. No corpus rows written.

Gap notes: inventory of the public index location only. Intermediate appellate opinions remain uningested. Preferred sources for future import must respect robots/WAF and provenance requirements. Annotations remain editorial and are not scraped.
