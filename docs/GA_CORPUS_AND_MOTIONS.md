# Georgia corpus and motion coverage

This file is the app contract for all Georgia law and all motions.

## Law

The app can index official public materials, including the full Official Code of Georgia Annotated (OCGA). In *Georgia v. Public.Resource.Org, Inc.*, 590 U.S. 255 (2020), the U.S. Supreme Court held that the OCGA, including its annotations, is not copyrightable under the government edicts doctrine. Statutes, annotations, session laws, court rules, agency rules, and opinions are therefore all part of the lawful corpus. See `docs/LEGAL_SOURCES_AND_PROVENANCE.md`.

Every stored statute must keep provenance: the source (e.g. the Public.Resource.Org release or legis.ga.gov), the release identifier and release/as-of date, the file URL, and a content hash. Annotations (history, editor's notes, cross references, case notes) are stored separately from the statutory text: they are editorial material, not enacted law, and must never be presented as the text of a Code section. A release's as-of date is not an effective date, and a bulk release is not evidence that a section is still current; currency stays `unknown` until checked against a newer official source.

Official entry points already in config/sources.yaml:

- Georgia General Assembly: https://www.legis.ga.gov/
- Supreme Court of Georgia: https://www.gasupreme.us/
- Georgia courts and Uniform Rules: https://georgiacourts.gov/
- Court of Appeals: https://www.gaappeals.us/

Coverage order: Civil Practice Act, Evidence Code, Criminal Procedure, Domestic Relations, Juvenile Code, Probate, Magistrate; Uniform Rules; appellate opinions and rules; session laws.

Issue 88 remains the release blocker until those sources are ingested and counted. A catalog is not the corpus.

## Motions

Georgia has no closed list. OCGA 9-11-7(b) makes any written application for an order a motion. config/ga_motion_catalog.json is the practical filing set for civil, criminal, family, juvenile, probate, magistrate, appellate, and administrative cases.

Local rules and standing orders can add forms and deadlines.
