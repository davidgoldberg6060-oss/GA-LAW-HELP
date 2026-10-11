# STANDALONE ASSISTANT GA.LAW.HELP — v1.3 production foundation

Production-oriented starter for a standalone Georgia legal research and case-intelligence application.

Current layers include owner-scoped authenticated cases, email verification and SMTP password recovery, refresh-token rotation/reuse detection/revocation, evidence integrity and resumable large-media jobs, an encrypted-session Android client, official-source ingestion/provenance, historical legal authority/version handling, Supabase/PostgreSQL migrations, and Case Intelligence: retrieval, Why?, favorable/adverse authority, Red-Team and Second-Look screening.

This remains a development build. The GALAWHELP database migrations are live; before public release it still requires production hosting and secret configuration, SMTP verification, complete official-source ingestion, a real search/vector index, model-provider integration, MFA, privacy/retention controls, observability, independent security review, Play Store release engineering, and legal-data QA.

Official-source coverage is an inventory, not ingested authority. `docs/GEORGIA_CASE_COVERAGE.md` records citation, source URL, hash, fetch date, and gap notes. A missing `DATABASE_URL` means no corpus rows are written and no coverage is claimed. Answers must not invent statute or case text.

Latest discover-only checkpoint (2026-10-11): Georgia court rules indexes (`ops/legal-import/2026-10-11-court-rules-indexes.md`). Supreme Court Rules and Uniform Rules PDF links were inventoried from official indexes; robots.txt disallows `/wp-content/uploads/`, so no PDF bytes were fetched and no authority rows written.

## Verification

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt pytest httpx
.venv/bin/pytest -q
```

See `docs/SUPABASE.md` for the GALAWHELP deployment contract and `android/README.md` for Android build configuration.
