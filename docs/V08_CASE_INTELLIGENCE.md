# v0.8 Case Intelligence

Adds a source-bound analysis layer for GA.LAW.HELP:

- deterministic legal retrieval baseline with verification/current-status weighting
- event-date authority filtering (law at the time)
- favorable and adverse authority separation
- structured findings with facts used, missing facts, confidence and counterarguments
- `Why?` payload that exposes the exact authority attached to a finding
- Red-Team analysis that attacks unsupported or weak findings
- Second-Look screening categories for sentencing, merger, plea, ineffective assistance and newly discovered evidence

## Safety / accuracy invariant
No model-generated legal conclusion is treated as authority. A finding must point to separately stored, provenance-tracked authority. User-reported facts remain distinct from verified records. The engine is research support, not a guarantee of outcome.
