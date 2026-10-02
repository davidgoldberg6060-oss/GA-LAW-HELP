# Unannotated code path

The statute source is the unannotated Code of Georgia on legis.ga.gov, maintained by the General Assembly and GeorgiaNet.

Do not import Lexis annotations. Official appellate opinions still come from gasupreme.us and gaappeals.us.

`backend/app/unannotated_code.py` is the starter index. Full section text is loaded into Supabase only after DATABASE_URL is set and the official text is acquired.
