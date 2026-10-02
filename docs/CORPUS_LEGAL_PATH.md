# Permanent Georgia corpus

This seed is the legal starter. It is not the complete code.

Allowed in the app database:
- Unannotated statute text acquired from the Georgia General Assembly site.
- Official appellate opinion PDFs from the Supreme Court and Court of Appeals.
- Court rules from the Judicial Council / AOC sites.

Not allowed to copy:
- Official Code of Georgia Annotated annotations, editors' notes, case summaries, and headnotes.
- Commercial reporter text from West or Lexis.

Legal way to get the annotated material:
1. License OCGA from LexisNexis, the state's designated publisher.
2. Store only what that license permits inside Supabase.
3. Until a license exists, answer from unannotated code plus official opinions.

Load opinions after DATABASE_URL is set:
python -m backend.app.ingestion.import_supreme_opinions --year 2025 --limit 25 --commit
