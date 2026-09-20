# Production roadmap

## Built foundation
- FastAPI backend, PostgreSQL-ready models, JWT authentication
- Owner-scoped cases, timeline and evidence records
- Evidence SHA-256 integrity metadata and audit logging
- Legal authority/version model and issue-analysis foundation
- Docker deployment configuration
- Native Android application project and launch dashboard

## P0 — launch blockers
1. Production migrations and test suite
2. HTTPS deployment and secrets management
3. Password reset, email verification, MFA and session revocation
4. Object storage with encryption, signed URLs, malware scanning, retention/backups
5. Android API client, secure credential storage, case CRUD and evidence picker/upload
6. Privacy policy, terms, support/contact, Play Data Safety mapping

## P1 — legal intelligence
Official/public Georgia source adapters; source snapshots; statute/opinion versioning; citation graph; authority-status checks; historical-law resolver; source-bound retrieval; Why? citations; updater/verification queue.

## P1 — case intelligence
Issue spotting, favorable/adverse analysis, Red Team, Second-Look, appeal/habeas/civil workflows, deadlines, procedural barriers, attorney export.

## P2 — evidence intelligence
Chunked/resumable long-video ingestion; immutable originals; transcoding; speech transcription; speaker/audio passes; frame extraction; OCR; reflection candidates; contradiction engine; synchronized case replay. All derived media must remain traceable to originals and transformations.
