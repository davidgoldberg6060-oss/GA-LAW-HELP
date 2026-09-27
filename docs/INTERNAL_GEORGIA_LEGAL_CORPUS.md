# GA.LAW.HELP Internal Georgia Legal Corpus

## Goal
GA.LAW.HELP should answer legal research questions from its own indexed corpus at runtime instead of redirecting users to external legal websites. External official/public sources are ingestion and verification sources, not the primary user interface.

## Corpus collections

### 1. Georgia statutes and legislation
Store Georgia Code material that can lawfully be stored, legislative enactments, effective dates, amendments, repeals, cross-references, historical versions, source provenance, and verification timestamps.

### 2. Georgia case law
Index publicly available Georgia Supreme Court and Court of Appeals opinions and other public Georgia judicial decisions available from lawful sources. Store citation, court, docket, date, judges where public, procedural posture, charges/issues, holdings, disposition, full searchable text where permitted, summaries, cited statutes, cited cases, subsequent-history/status metadata, source provenance, and verification timestamps.

Do not represent this collection as literally every Georgia case: sealed, restricted, juvenile, expunged, unpublished/unavailable, non-digitized, and otherwise inaccessible records will not be present. Mark coverage explicitly.

### 3. Motions and remedies knowledge base
Build a structured catalog of motion/remedy TYPES and legal requirements rather than claiming to possess every motion ever filed. Include criminal, civil, appellate, habeas/post-conviction, probation/parole where applicable. Each entry should store name, purpose, procedural stage, prerequisites, deadlines when determinable, governing rules/statutes, leading authority, required factual predicates, common opposition, requested relief, verification date, and jurisdiction/court applicability.

Examples include suppression, dismissal, severance, continuance, discovery-related motions, motions in limine, directed verdict, new trial, reconsideration where applicable, sentence-related remedies, withdrawal of plea, appeal/post-conviction remedies, and civil procedural motions.

### 4. Law-enforcement procedure and rights knowledge base
Store structured rules concerning encounters, detention, arrest, searches, warrants, consent, vehicles, homes, questioning/interrogation, Miranda, identification, use of force, evidence handling, body-worn-camera/public-record issues where applicable, booking, jail/custody, and related Georgia/federal constitutional rules.

Never use a simplistic universal `legal/illegal` label. Each procedure must support: generally permitted, generally prohibited, fact-dependent, unsettled, agency-policy-only, or unknown. Store governing authority, exceptions, factual conditions, date verified, and confidence/source status.

### 5. Court rules and legal procedure
Index current publicly available Georgia court rules and procedural authorities needed to explain filing, service, deadlines, appeals, evidence, and court procedure. Version rules so an amendment never silently rewrites the historical rule used by an older case.

## Required database entities
- legal_sources
- statutes
- statute_versions
- cases
- case_issues
- case_charges
- case_citations
- motions
- motion_authorities
- procedures
- procedure_authorities
- court_rules
- legal_updates
- ingestion_runs
- verification_events

All substantive records need `effective_from`, `effective_to` when known, `source_kind`, `source_locator`, `retrieved_at`, `verified_at`, `content_hash`, and `status`.

## AI retrieval rules
1. Search the internal corpus first.
2. Separate primary authority from AI explanation.
3. Return citations for material legal propositions.
4. Never invent a case, citation, statute, motion, deadline, holding, or quotation.
5. If internal coverage is insufficient, say so rather than filling the gap from model memory.
6. Distinguish binding authority, persuasive authority, superseded/reversed/vacated authority, and non-authority guidance.
7. Rank cases by legal/factual similarity only after filtering by jurisdiction, status, and relevant date.
8. Charge search should return public indexed cases associated with the charge/statute, then let AI summarize patterns and differences.

## Update pipeline
Use scheduled ingestion jobs. New source material enters a staging table, is normalized/deduplicated, versioned, validated, and only then promoted to the searchable corpus. Never overwrite prior legal versions. Generate an audit record for each ingestion and verification run.

The application UI may show source citations/details inside the app without forcing users to leave GA.LAW.HELP. Source URLs remain stored internally for provenance and administrator verification.
