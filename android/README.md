# Android client
Native Android shell for STANDALONE ASSISTANT GA.LAW.HELP.

## Current
- Play-ready package namespace: `help.galaw.standalone`
- Android 8+ (minSdk 26)
- Target/compile SDK 35
- Launcher dashboard for Cases, Evidence, Legal Research, and Second-Look review
- INTERNET permission and cleartext HTTP disabled

## Build configuration

Set the backend URL without committing secrets:

`./gradlew assembleDebug -PGALAW_API_BASE_URL=https://api.your-domain.example`

The client enforces HTTPS for non-debug builds, stores access and refresh tokens
with Android Keystore-backed encrypted preferences, rotates refresh tokens, and
switches evidence larger than 8 MiB to the resumable upload API.

## Next before production
Add notifications, recovery/MFA screens, release signing, privacy/data-safety disclosures, accessibility and full UI tests.
