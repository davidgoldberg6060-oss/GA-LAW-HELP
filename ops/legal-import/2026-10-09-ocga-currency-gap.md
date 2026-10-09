# 2026-10-09 OCGA currency-gap checkpoint

DATABASE_URL was unset. No title ODT, bill, or Lexis page was downloaded. No corpus rows were written.

| Source | URL | Result | SHA-256 | Gap |
| --- | --- | --- | --- | --- |
| General Assembly laws shell | https://www.legis.ga.gov/laws | HTTP 200, 1,492 bytes, then client route 404 | `05dd7a574b081f27c023001daa94e1f2f49a3f84151f0c6639ec54d7c691479a` | Application shell, not unannotated statute text |
| Legislation search | https://www.legis.ga.gov/search | Rendered session list through 2001 | n/a (client rendered) | Not a code text source |
| Georgia Code nav link | http://www.lexisnexis.com/hottopics/gacode | Not opened | n/a | Publisher site; annotations not scraped |
| Signed by Governor, 2025-2026 Regular Session | https://www.legis.ga.gov/legislation/signed-by-governor | Rendered label "Showing Results 1-20 of 742" | n/a (client rendered) | Not stored acts; not proof each act amends the OCGA |
| Supreme Court 2016 index | https://www.gasupreme.us/2016-opinions/ | HTTP 404 | n/a | Importer floor stays 2017; no opinion PDFs |
| Supreme Court 2015 index | https://www.gasupreme.us/2015-opinions/ | HTTP 404 | n/a | No pre-2017 annual index at that path |
| Court of Appeals robots | https://www.gaappeals.gov/robots.txt | HTTP 405 | n/a | Still blocked |
| Court of Appeals opinions | https://www.gaappeals.gov/opinions/ | HTTP 405 | n/a | No appeals opinion index |

Fetched 2026-10-09. The 742 figure is a page label only. First listed caption was an index label (HB 5), not bill text. Lexis was not opened. These notes are not persisted coverage and do not verify that release86.2022.11 is current law.
