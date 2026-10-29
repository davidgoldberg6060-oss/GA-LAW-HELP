Last production check: 2026-10-29 05:02 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only access attempt to the official Court of Appeals of Georgia opinion search page. Response bytes hashed; WAF/captcha blocked full content; no opinion PDFs or indexes downloaded; not stored opinion text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| opinion search (captcha) | https://www.gaappeals.gov/opinion-search/ | 405 | 2,511 | `9f6a6bdbee15a3fc82c9754899d3c72902c9fefccc5d86221822a664885cc651` | CloudFront WAF captcha; no opinion list retrieved |
| homepage (captcha) | https://www.gaappeals.gov/ | 200? | 2,511 | `814d9422ab13ae94c1047d240a0abb12ffb689f4796e1e8433814076bb631770` | Same WAF response size; site moved from gaappeals.us |

The Court of Appeals site hosts an opinion search and docket tools. Access was blocked by captcha/WAF in this run. No Lexis scraped. Preferred bulk sources for opinions remain CourtListener or official PDF releases when accessible. These counts are not persisted coverage. Gap: full opinion index not retrieved due to access control; historical coverage incomplete without DATABASE_URL and successful fetch.
