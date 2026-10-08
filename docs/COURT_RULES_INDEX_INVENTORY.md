# Court rules index inventory (not stored coverage)

Fetch date: 2026-10-08 09:00 UTC. `DATABASE_URL` was unset, so `python -m backend.app.ingestion.import_court_rules --set all --commit` was not run. No rule text was downloaded, parsed, or written to `legal_authorities`. These rows are index checkpoints only. A filename date is not an effective date and is not current-law verification. Lexis annotations were not scraped.

Importer sets and official indexes (`backend/app/ingestion/import_court_rules.py`):

| Set | Index URL | HTTP | Index bytes | Index SHA-256 | Linked PDF (not fetched) | Gap |
| --- | --- | ---: | ---: | --- | --- | --- |
| Court of Appeals rules | https://www.gaappeals.gov/court-rules/ | 405 | n/a | n/a | not observed | Human-verification / method block. No rule-page count. Same 405 class as the 2026-10-05 appeals opinion search. |
| Supreme Court rules | https://www.gasupreme.us/rules/ | 200 | 1,592,661 | `ddaa95526bb0c01fae222a22e356feb88a12a81bcca4e3ee008c15c69062c0d1` | https://www.gasupreme.us/wp-content/uploads/2026/07/SupremeCourtRules_eff-July-2-2026.pdf | robots.txt `Disallow: /wp-content/uploads/` so the importer would report `blocked_by_robots` unless an operator supplies `--pdf-dir`. |
| Uniform Superior Court Rules | https://www.gasupreme.us/other-court-rules/ | 200 | 1,592,686 | `fb1eaa6633b896ba00f84a7627fa45eabdd4817e6e3ed7b750714f1577a3e580` | https://www.gasupreme.us/wp-content/uploads/2026/04/UNIFORM-SUPERIOR-COURT-RULES-2026_04_09.pdf | Same robots block. |
| Uniform State Court Rules | same other-court-rules index | 200 | 1,592,686 | same index hash | https://www.gasupreme.us/wp-content/uploads/2024/01/UNIFORM-STATE-COURT-RULES-2024_01_18.pdf | Same robots block. |
| Uniform Juvenile Court Rules | same | 200 | 1,592,686 | same | https://www.gasupreme.us/wp-content/uploads/2026/09/UNIFORM-JUVENILE-COURT-RULES-2026_09_03_ADA.pdf | Same robots block. |
| Uniform Probate Court Rules | same | 200 | 1,592,686 | same | https://www.gasupreme.us/wp-content/uploads/2023/05/UNIFORM-PROBATE-COURT-RULES-2023_06_01.pdf | Same robots block. |
| Uniform Magistrate Court Rules | same | 200 | 1,592,686 | same | https://www.gasupreme.us/wp-content/uploads/2023/03/UNIFORM-MAGISTRATE-COURT-RULES-2023_04_01.pdf | Same robots block. |

Supreme Court `robots.txt` (https://www.gasupreme.us/robots.txt, HTTP 200, 71 bytes): `User-agent: *` / `Disallow: /wp-content/uploads/` / `Disallow: /readme.html`. Court of Appeals `robots.txt` also returned HTTP 405, so no allow/disallow list was recorded.

Extra PDF links on the other-court-rules index, not in the importer `RULE_SETS`, and not fetched:

- https://www.gasupreme.us/wp-content/uploads/2025/12/UNIFORM-MUNICIPAL-COURT-RULES-2024_12_12.pdf
- https://www.gasupreme.us/wp-content/uploads/2026/06/State-wide-Business-Court-Rules-2026_06_11.pdf
- https://www.gasupreme.us/wp-content/uploads/2026/01/QUICK-REFERENCE-RULES.pdf (linked from the Supreme Court rules index; not a rule set)

Earlier archive.org metadata for `gov.ga.ocga.2018` still lists `gov.ga.court.rules.odt` (3,026,291 bytes, published SHA-1 `4610a0430d2d6a6dabf67ce569a589bfb0a6a84a`) and `gov.ga.court.rules.index.odt` (123,188 bytes, SHA-1 `0a499e7d7ff0e89e1af0642489c0082586b1ece6`). Those files were not downloaded in this run. That November 2022 release is not a substitute for the later official PDF links above.

Stored production counts remain the unverified 2026-09-28 zeros. This inventory is not persisted coverage.
