Last production check: 2026-10-10 00:01 UTC. DATABASE_URL was unset, so `python -m backend.app.ingestion.import_court_rules --discover-other-codes --commit` was refused and no corpus rows were written. Discover-only hashed the other-codes-rules index and robots.txt (page bytes and PDF link labels only; rule PDFs not downloaded; not stored rule text and not current-law verification):

| Source | URL | HTTP | Bytes | SHA-256 | PDF links named |
| --- | --- | ---: | ---: | --- | ---: |
| other-codes-rules index | https://www.gasupreme.us/other-codes-rules/ | 200 | 1,606,014 | `419a09378a0f38e69aa7aa37edacce29b32958e33fc0cbddc9b5fc882099607a` | 27 |
| robots.txt | https://www.gasupreme.us/robots.txt | 200 | 71 | `2c3d50be784b56de8c6cbdc174817ab688c3b9892494616d3a414a115aa85196` | 0 |

The discover-other-codes path named 27 unique gasupreme.us PDF URLs (Code of Judicial Conduct, JQC Rules, Unified Appeal Procedure, Uniform Misdemeanor Citation, Statewide Minimum Standards, Jury Composition, legal interpreting, and related orders). robots.txt disallows `/wp-content/uploads/`, so none of those files were fetched. Filenames are index labels only, not effective dates and not stored rule text. Lexis was not opened. These counts are not persisted coverage. The label list is in `ops/legal-import/2026-10-10-other-codes-rules.md`.

