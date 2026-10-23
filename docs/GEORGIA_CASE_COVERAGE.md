Last production check: 2026-10-23 01:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals rules index and robots.txt. Both returned AWS WAF captcha pages; rule text was not retrieved; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gaappeals.gov/rules/ | 405 | 2,511 | `54881bc0bd242436c8a2b251336e70c8c7d5cee3e47c5f2115cf850b362f4fb4` | AWS WAF captcha; not a rules index |
| robots.txt | https://www.gaappeals.gov/robots.txt | 405 | 2,511 | `2302dbccf73be2eb47759de5c649b18c549ad425bf9bbfd0e79757f5ca8d46aa` | Same WAF captcha page |

Raw fetch returned the Human Verification challenge. No rule text or PDF links were named. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-appeals-rules.md`.

Last production check: 2026-10-22 23:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Secretary of State Georgia Constitution revised 2025 page and robots.txt. Both returned Cloudflare challenge pages; constitution text was not retrieved; not stored constitution text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| constitution page | https://sos.ga.gov/georgia-constitution-revised-2025 | 403 | 5,446 | `74e34e06f812fad7ec10f63cebc3c17cd2657ab7f0d6f6cdad84c7b1aa623175` | Cloudflare challenge page; not constitution text |
| robots.txt | https://sos.ga.gov/robots.txt | 403 | 5,356 | `15499df10a6a491e52bdf5833fc04963ab43e723c03819ba49a8ebf8fb84645a` | Same Cloudflare challenge |

Raw fetch returned the Cloudflare "Just a moment..." security verification page for both. No constitution text was retrieved. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-sos-constitution.md`.
