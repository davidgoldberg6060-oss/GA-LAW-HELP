# 2026-10-26 Court of Appeals domain and robots checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only notes on the Court of Appeals of Georgia site. No opinion PDFs, rule PDFs, or other authority text were downloaded. Lexis was not opened. This is not stored opinion or rule text and not current-law verification.

| Source | URL | Notes |
| --- | --- | --- |
| domain transition | https://www.gaappeals.gov/ (from gaappeals.us) | Homepage alert: site transitioned from gaappeals.us to gaappeals.gov; employee emails now @gaappeals.gov. |
| robots.txt | https://www.gaappeals.gov/robots.txt | User-agent: * ; Disallow: /wp-admin/ ; Allow: /wp-admin/admin-ajax.php ; Sitemap: https://www.gaappeals.gov/sitemaps.xml |
| raw fetch | curl to homepage and robots | Returned AWS WAF Human Verification challenge page (~2511 bytes); not the live content. |

Gap notes: inventory of public index access only. robots.txt does not disallow opinion or rules paths, but no files were fetched. Preferred sources for future import remain official indexes; currency unknown. These counts are not persisted coverage. No corpus rows written.
