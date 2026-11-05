# STANDALONE ASSISTANT 1.7.0 performance

Measured 2026-11-05 America/New_York against live API `https://api-production-60cc.up.railway.app`.

## APK size

| Build | Bytes | MiB |
|-------|------:|----:|
| 1.6.9 signed release (baseline, no minify) | 6,829,227 | 6.51 |
| 1.7.0 same features, minify OFF | 6,835,231 | 6.52 |
| **1.7.0 R8 minify + resource shrink** | **2,807,205** | **2.68** |

Delta vs 1.6.9: **−4,022,022 bytes (−58.9%)**.

## Live API latency (client → Railway, median of 3 unless noted)

| Endpoint | Median / notes |
|----------|----------------|
| GET `/health` | ~0.13 s |
| GET `/public/georgia-laws/search?q=theft` | ~0.16 s |
| GET `/public/georgia-cases?q=miranda` | ~0.18 s |
| GET `/public/georgia-laws/law` (O.C.G.A. § 16-8-2) | ~0.12 s |
| POST `/public/rights-assistant` | warm ~0.15 s; cold AI ~11 s (n=2 mean 5.6 s) |

After: guest laws/cases GET responses carry `Cache-Control: public, max-age=60`; Android `GuestPublicApi` caches law search/detail 120 s in-process; `Connection: keep-alive` on ApiClient + GuestPublicApi.

## Client optimizations shipped

- R8 full mode + resource shrinking (release)
- HTTP keep-alive
- Guest GET response cache (laws)
- Backend Cache-Control on public laws/cases/health GETs
- ProGuard keep rules for app package

Cold start / frame jank require a physical device; measure on phone after installing the signed APK (see report steps).
