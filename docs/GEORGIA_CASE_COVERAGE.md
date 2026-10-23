Last production check: 2026-10-22 23:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Supreme Court of Georgia rules index and robots.txt. Index bytes were hashed; PDF anchors counted; uploads are robots-disallowed so no rule PDFs were downloaded; not stored rule text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| rules index | https://www.gasupreme.us/rules/ | 200 | 1,586,244 | `205c705a3d1d849e95ccfcadfe11ce4bf0d0fdf6be18d3c761cece8c08b051c0` | Names current Rules PDF (effective July 2, 2026), amendment chart, and quick-reference PDF; all under /wp-content/uploads/ |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | Disallow: /wp-content/uploads/ |

The index names three PDF links under /wp-content/uploads/. robots.txt disallows that path, so none were fetched. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-supreme-rules-index.md`.

Last production check: 2026-10-22 23:00 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Secretary of State Georgia Constitution revised 2025 page and robots.txt. Both returned Cloudflare challenge pages; constitution text was not retrieved; not stored constitution text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| constitution page | https://sos.ga.gov/georgia-constitution-revised-2025 | 403 | 5,446 | `74e34e06f812fad7ec10f63cebc3c17cd2657ab7f0d6f6cdad84c7b1aa623175` | Cloudflare challenge page; not constitution text |
| robots.txt | https://sos.ga.gov/robots.txt | 403 | 5,356 | `15499df10a6a491e52bdf5833fc04963ab43e723c03819ba49a8ebf8fb84645a` | Same Cloudflare challenge |

Raw fetch returned the Cloudflare "Just a moment..." security verification page for both. No constitution text was retrieved. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-22-sos-constitution.md`.

