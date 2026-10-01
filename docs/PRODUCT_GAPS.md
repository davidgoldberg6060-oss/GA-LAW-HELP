# What GA.LAW.HELP still needs before public launch

## Done on main
- Encounter scripts for traffic stop, home, street, and interrogation live in `backend/app/encounter_rights.py` (PR 93).
- Ingestion pipeline exists under `backend/app/ingestion/` including Supreme Court listing and import.
- Motion seed registry exists; a fuller catalog is in PR 92.

## Blockers
1. Empty legal corpus (issue 88). Run official-source ingest against gasupreme.us, gaappeals.us, legis.ga.gov, and georgiacourts.gov. Do not copy OCGA annotations.
2. Guest research still forces an account (issue 82).
3. Verified motion screen is not on the live case endpoint (issue 44).

## Product gaps
- Wire `encounter_rights.encounter_pack()` into `grounded_legal_assistant` rights and talk_to_me modes so the scripts are actually used.
- Production host, secrets, SMTP, MFA, observability.
- Real search/vector index over ingested opinions.
- Model-provider key and rate limits.
- Privacy and retention policy for case uploads and live-encounter recordings.
- Play Store signing, listing, and content rating.
- Independent security review.
- Legal-data QA so the assistant never presents an unverified cite as current Georgia law.
- Close or rebase the pile of overlapping open PRs so main is the only source of truth.
