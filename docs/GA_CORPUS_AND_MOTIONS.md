# Georgia corpus and motion coverage

This file is the app contract for all Georgia law and all motions.

## Law

The app can index official public materials. It must not copy the Official Code of Georgia Annotated. Unannotated statutes, session laws, court rules, and opinions are the lawful corpus.

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
