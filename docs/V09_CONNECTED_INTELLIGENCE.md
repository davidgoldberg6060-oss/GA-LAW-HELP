# v0.9 Connected Case Intelligence

The Android case workspace now calls authenticated backend endpoints for case screening, Why? authority, Red-Team review, and Second-Look screening.

## Safety / accuracy design
- Screening creates research leads from the user's case posture and narrative; it does not invent citations.
- `Why?` only displays authorities explicitly linked to the case.
- Authority verification and record completeness remain visible requirements.
- Red-Team presents counterarguments and missing facts instead of promising outcomes.
- Second-Look is a screening workspace, not a conclusion that a remedy is available.

## Still required for production
Official-source population at scale, live authority-status updating, production object storage, worker execution for media jobs, recovery/MFA, Android release signing, privacy policy/terms, observability, backups, security testing, and Play submission assets.
