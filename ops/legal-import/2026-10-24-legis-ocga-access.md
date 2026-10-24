# Official OCGA access inventory — 2026-10-24

DATABASE_URL was unset, so no corpus rows were written. Discover-only. LexisNexis portal was not scraped (annotations not fetched).

## Source

- Homepage: https://www.legis.ga.gov/
- Official Georgia Code link (from rendered page): http://www.lexisnexis.com/hottopics/gacode
- General Statutes Summary: https://www.legis.ga.gov/general-statutes

## Raw fetch of homepage (2026-10-24 ~08:01 UTC)

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage (raw) | https://www.legis.ga.gov/ | 200 | 1,492 | `301e217dc5d384b4243ee12b56ae51d5ecf1d0b0becedae1da952a1d361bac65` | Minimal HTML shell; full content is JS-rendered. Contains link to Lexis free OCGA portal. |

## Notes

- The Georgia General Assembly site links to the free official OCGA portal hosted by LexisNexis (now includes annotations per post-2020 updates).
- Per project policy, Lexis annotations are not scraped.
- Preferred bulk unannotated/structured source remains Public.Resource.Org archive.org/details/gov.ga.ocga.2018 (release86.2022.11 ODTs).
- This is an inventory of the official access point only; no statute text stored, no coverage claimed.
- Gap: currency of any future import must be checked against newer official sources; annotations are editorial, not law.

Not stored statute text and not current-law verification.
