# 2026-10-29 Georgia Courts homepage inventory checkpoint

DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Georgia Courts homepage. Homepage bytes were hashed; no PDFs or opinion/rule texts were downloaded; not stored authority text and not current-law verification.

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage | https://www.georgiacourts.gov/ | 200 | 90,519 | `c77fbb0d3df22230c36d92ecc9043441cfe25d9ef1f41496fad8a07aea9b06f7` | Official portal; links to court sites including Supreme and Court of Appeals. No bulk downloads. |

Lexis was not opened. These counts are not persisted coverage. No corpus rows written.

Gap notes: homepage inventory only. Specific rules and opinion indexes are tracked in separate checkpoints (e.g. gasupreme.us). Preferred bulk sources remain Public.Resource.Org for OCGA and CourtListener for opinions once DATABASE_URL is set and terms/robots are respected. Currency unknown.
