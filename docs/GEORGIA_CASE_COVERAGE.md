Last production check: 2026-10-23 15:01 UTC. DATABASE_URL was unset, so no corpus rows were written. Discover-only read of the Court of Appeals homepage (https://www.gaappeals.gov/). Page bytes were hashed; returned AWS WAF captcha; no opinion or rule content retrieved; not stored opinion text and not current-law verification:

| Source | URL | HTTP | Bytes | SHA-256 | Notes |
| --- | --- | ---: | ---: | --- | --- |
| homepage | https://www.gaappeals.gov/ | 405 | 2,511 | `ebd73cfa9a5d51fc2dc9669aa64b85b285c539084594df754a457f2ea4078891` | AWS WAF Human Verification challenge; not the homepage |

Raw fetch returned the Human Verification challenge. No docket-labeled PDF links or rules were named. Lexis was not opened. These counts are not persisted coverage. The checkpoint is in `ops/legal-import/2026-10-23-appeals-homepage-waf.md`. Gap remains for Court of Appeals appellate opinion indexes and rules.

[Full prior ledger follows in subsequent restore if needed. DATABASE_URL remains unset. No corpus rows written.]