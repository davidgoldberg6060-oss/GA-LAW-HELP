# Attorney General opinion index tail

Fetched 2026-10-08 23:10 UTC with `python -m backend.app.ingestion.import_ag_opinions --discover-only --pause 0.5`. DATABASE_URL was unset. No PDFs were downloaded and no authority rows were written. This is not current-law verification.

The importer stops when a page names no citation labels. Page 11 was that stop (`stopped_reason=no-citation-labels`). Pages after 11 were not fetched.

| Page | URL | HTTP | Bytes | SHA-256 | Citation labels |
| --- | --- | ---: | ---: | --- | ---: |
| 0 | https://law.georgia.gov/opinions | 200 | 146,784 | `89adba418f9312da28c9ee3ea233d62654ef52524a940b7cf95f251265d76ba4` | 50 |
| 1 | https://law.georgia.gov/opinions?page=1 | 200 | 142,536 | `444bce0bd0500a7be7853c42bad5902e1279c2bbdc6c00ca60cf2455c0b5b1f4` | 50 |
| 2 | https://law.georgia.gov/opinions?page=2 | 200 | 144,532 | `fc3d6875d0412e0f669630023a5214944df451e80d551bfc8331b0013a283d92` | 50 |
| 3 | https://law.georgia.gov/opinions?page=3 | 200 | 142,010 | `f2eadfe3e0ffed26e5348a206229ec9fd09e58bcfe11b16360060dd6e4724e4a` | 50 |
| 4 | https://law.georgia.gov/opinions?page=4 | 200 | 142,009 | `80351d668665876e56759da7792b9fdbbaabd59a58a0ddbb4a60c8bb87c5c4bd` | 50 |
| 5 | https://law.georgia.gov/opinions?page=5 | 200 | 141,290 | `68c0c69c2575014cd19c0ffc5ab20f28f07e54f0a01fb3783fca1e58cba8a02c` | 50 |
| 6 | https://law.georgia.gov/opinions?page=6 | 200 | 140,727 | `8a3d4464e78be01781d0a0f0368c7d0b71b44ed1a46ade5a11e96138ca344b07` | 50 |
| 7 | https://law.georgia.gov/opinions?page=7 | 200 | 141,651 | `5de76402e2d7ca67d59fd5e600798245ee69a5b81ad9ee6c1791b2ff0a02ce4f` | 50 |
| 8 | https://law.georgia.gov/opinions?page=8 | 200 | 142,488 | `430dc744ee19a7c2ab4a22ab7093dfeec03b9a8a96b1e59156582bdd104bbaca` | 50 |
| 9 | https://law.georgia.gov/opinions?page=9 | 200 | 140,541 | `ab2b0763b615d069c560199cb7906cf2be56d102c75aab293dc8580a0d6e210c` | 50 |
| 10 | https://law.georgia.gov/opinions?page=10 | 200 | 126,949 | `012ea1150b5db648a5429e6530380e14594085981d79e56d59ee008a3ed0d694` | 37 |
| 11 | https://law.georgia.gov/opinions?page=11 | 200 | 93,601 | `5666188473f79e98b739c44ef9e418b6bce5f4e97fce94cfed2a481511e3fa04` | 0 |

Pages 0-10 name 537 citation labels. Page 0 names five PDF download links. One URL contains `UNPUBLISHED-document--DO-NOT-SHARE` and was not fetched. Pages 1-10 name labels without PDF links. Labels are index checkpoints, not opinion text. `https://law.georgia.gov/robots.txt` allows `/opinions` (SHA-256 `1ec8e6c4fed3dc4f55da7a82412fc7bb6649941ba44ccc6b47ba7968604d1c1b`). These counts are not persisted coverage.
