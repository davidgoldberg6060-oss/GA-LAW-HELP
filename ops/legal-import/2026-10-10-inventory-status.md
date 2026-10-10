# 2026-10-10 official-source inventory status

DATABASE_URL is unset. No authority rows were written and no coverage is claimed.

## Recorded discover-only checkpoints (not stored text)

- OCGA release86.2022.11: title files 01-53 named in archive.org metadata; published SHA-1s recorded; ODT text not downloaded.
- Supreme Court annual indexes 2017-2025 and forthcoming: page bytes hashed, docket-labeled PDF link counts recorded, robots.txt disallows /wp-content/uploads/, PDFs not downloaded. Some years have multi-PDF dockets or filename mismatches noted as gaps.
- Court of Appeals opinion-search and robots.txt: HTTP 405 WAF captcha responses (bytes and SHA-256 of captcha pages recorded); no docket labels extracted.
- Court rules and other-codes indexes: named PDFs listed as blocked by robots.txt; not downloaded.

## Production corpus

Prior production checks reported legal_sources=0, legal_authorities=0, authority_versions=0. These inventories do not change that.

## Search and empty coverage

`search_georgia_authorities` uses Postgres full-text (to_tsvector / websearch_to_tsquery with OR ranking) or portable keyword ILIKE fallback. Whole-question ILIKE is not used. When no matching verified authorities exist, the grounded assistant returns a clear coverage notice and does not invent citations.

## Next required step

Set DATABASE_URL in the production environment, then run reviewed commit-mode imports against the inventoried sources. Until then, do not claim any Georgia authorities are ingested.

Lexis annotations were not opened. No private case data was published.
