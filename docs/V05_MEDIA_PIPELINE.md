# v0.5 Evidence pipeline

Implemented now: resumable/chunked evidence upload sessions, deterministic chunk assembly, SHA-256 integrity hashing after assembly, owner authorization on every upload operation, immutable-original storage convention, and queued analysis jobs for media probing, Deep Listening, frame analysis, reflection analysis and off-camera reconstruction.

The analysis job records are production plumbing, not a claim that forensic algorithms are already complete. Workers for transcription/reflection/frame interpretation still need model/provider integration. Enhanced media must remain separate from originals and findings must be labeled OBSERVED, TRANSCRIBED, INFERRED, UNCERTAIN or USER_CLAIM.
