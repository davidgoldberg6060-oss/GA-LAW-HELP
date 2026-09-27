# GA.LAW.HELP — In-App AI V2

## Product rule
Normal legal-learning workflows stay inside GA.LAW.HELP. Do not send a user to an outside website as the primary experience. Official public sources may be ingested/verified server-side and shown as citations/source metadata inside the app. External source opening is an optional secondary action only.

## Visual target
Use the supplied premium mockup as the visual direction: dark navy/black background, restrained gold brand treatment, blue active controls, richer iconography, stronger hierarchy, cards with depth, compact mobile spacing, and a persistent bottom navigation. Preserve accessibility and readable contrast.

## Case Analysis
The Case Analysis screen must work before and after a case is saved. Provide a large `Tell me what happened` input plus optional county, charge, stage, dates, and evidence/document upload. AI output is structured into: (1) factual timeline, (2) missing facts/questions, (3) charge elements, (4) possible defenses/issues, (5) potentially relevant motions/relief, (6) evidence to preserve/request/challenge, (7) deadlines/time-sensitive items, (8) prosecution/counterarguments, (9) practical next steps, and (10) verified Georgia authority/citations. Never promise an outcome. Distinguish verified law from AI inference.

## Charge + Public Case Lookup
Add an AI-controlled charge search. A user can type plain language or a Georgia charge/statute. The AI normalizes the charge, explains elements and common related charges, then searches the app's own indexed corpus of lawfully obtained PUBLIC case records. Return every matching indexed public case available in the corpus, with court, county, case number/citation where public, date, procedural posture, outcome when available, and source/verification status. Do not imply the corpus is exhaustive when records have not been ingested. Exclude sealed, restricted, expunged, juvenile, nonpublic, or otherwise unavailable records.

## Live `Talk to Me` / Encounter mode
The user explicitly starts microphone and/or camera access. No silent activation. Stream/transcribe only after permission. AI analyzes observable dialogue and user-provided/visible context and gives short, safety-first prompts. It should identify the apparent encounter state (consensual encounter, detention, traffic stop, search request, questioning, arrest/custody, warrant/entry, emergency) while clearly labeling uncertainty.

The live panel should show: `What appears to be happening`, `Safest immediate action`, `Your rights`, `What law enforcement may generally do`, `What generally requires consent/warrant/other legal basis`, and `A short sentence you can say`. Guidance must never tell the user to physically resist, flee, hide/destroy evidence, interfere, or disobey a lawful physical command. When facts are uncertain, say so. Emergency/medical danger takes priority.

## Legal Forms / Legal Tools / Georgia Laws / Court Info / Know Your Rights / Resources
Replace website-first buttons with native in-app AI/search views. Each section gets a search/chat box scoped to that section. Forms are generated as editable in-app drafts with jurisdiction/court warnings and source/version metadata. Laws and rights explanations cite the app's verified Georgia corpus. Court info uses the app's stored/indexed public directory. Resources render native cards; external phone/site actions, if retained, are secondary explicit actions.

## Reliability and data architecture
AI is the interface/reasoning layer, not the source of truth for case records. Public case records, statutes, rules, opinions, court directories, and form metadata must be ingested into GA.LAW.HELP storage, normalized, versioned, searchable, and source-attributed. AI queries that internal index. This prevents fabricated cases and supports in-app-only browsing.

Every legal answer should carry a source state: `Verified current source`, `Verified but check effective date`, `Public record`, `User-provided fact`, or `AI inference`. Where a source cannot be verified, the UI must say so rather than inventing authority.

## Service failure behavior
A temporary backend failure must not strand the app on a generic dead end. Keep navigation usable, preserve unsaved user input locally, show which feature is unavailable, and provide Retry. Static rights/safety material and previously cached public material should remain readable offline when feasible.
