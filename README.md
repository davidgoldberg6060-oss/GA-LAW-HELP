# STANDALONE ASSISTANT GA.LAW.HELP — v1.3 production foundation

Production-oriented starter for a standalone Georgia legal research and case-intelligence application.

Current layers include owner-scoped authenticated cases, email verification and SMTP password recovery, refresh-token rotation/reuse detection/revocation, evidence integrity and resumable large-media jobs, an encrypted-session Android client, official-source ingestion/provenance, historical legal authority/version handling, Supabase/PostgreSQL migrations, and Case Intelligence: retrieval, Why?, favorable/adverse authority, Red-Team and Second-Look screening.

This remains a development build. The GALAWHELP database migrations are live; before public release it still requires production hosting and secret configuration, SMTP verification, complete official-source ingestion, a real search/vector index, model-provider integration, MFA, privacy/retention controls, observability, independent security review, Play Store release engineering, and legal-data QA.

Official-source coverage is an inventory, not ingested authority. `docs/GEORGIA_CASE_COVERAGE.md` records citation, source URL, hash, fetch date, and gap notes. A missing `DATABASE_URL` means no corpus rows are written and no coverage is claimed. Answers must not invent statute or case text. Search uses keyword/full-text retrieval (Postgres `to_tsvector` / `websearch_to_tsquery` or portable word ILIKE), not whole-question `ILIKE`.

## Current coverage inventory (as of 2026-10-16)

Discover-only checkpoints exist for:

- Public.Resource.Org OCGA release86.2022.11 manifest (53 title ODTs + companions; none downloaded)
- Georgia Supreme Court annual opinion indexes 2017–2026 (PDF anchors named; robots.txt disallows `/wp-content/uploads/`; none downloaded)
- Georgia Court of Appeals opinion-search index (raw fetch returns AWS WAF captcha)
- Secretary of State Rules and Regulations download page (~154 department PDF labels; none downloaded)
- Supreme Court and Uniform/other court-rules indexes (PDF labels named; robots disallow uploads)
- Georgia Attorney General opinions index (citation links named; documents not downloaded)
- Georgia General Assembly annual general-statutes summary index (SPA shell; Lexis link not opened)

Known gaps (not claimed as coverage):

- No unannotated OCGA section text stored
- No court-rule PDFs or regulation text stored
- No appellate opinion PDFs stored (Supreme or Appeals)
- Court of Appeals raw fetches blocked by WAF
- Lexis annotations never scraped
- Production database counts remain zero while `DATABASE_URL` is unset

## Verification

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt pytest httpx
.venv/bin/pytest -q
```

See `docs/SUPABASE.md` for the GALAWHELP deployment contract and `android/README.md` for Android build configuration.
