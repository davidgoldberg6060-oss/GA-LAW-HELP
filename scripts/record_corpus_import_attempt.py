"""Record whether a Supreme Court corpus import can be committed.

This script never invents authorities. If DATABASE_URL is missing it prints a
skip record and exits 2. It does not copy the Official Code of Georgia
Annotated and it does not write trial-docket data.
"""
from __future__ import annotations

import json
import os
import sys

IMPORT_COMMAND = (
    "python -m backend.app.ingestion.import_supreme_opinions "
    "--year 2025 --limit 25 --commit"
)


def attempt_record(database_url: str | None) -> dict:
    available = bool((database_url or "").strip())
    if not available:
        return {
            "command": IMPORT_COMMAND,
            "database_url_available": False,
            "status": "skipped",
            "committed": False,
            "rows_written": None,
            "reason": (
                "DATABASE_URL is not available. No corpus rows were written "
                "or invented."
            ),
        }
    return {
        "command": IMPORT_COMMAND,
        "database_url_available": True,
        "status": "database_present_import_not_run_by_this_script",
        "committed": False,
        "rows_written": None,
        "reason": (
            "DATABASE_URL is set. Run the importer explicitly and record "
            "discovered, attempted, succeeded, and failed counts. This "
            "script does not import."
        ),
    }


def main() -> int:
    record = attempt_record(os.environ.get("DATABASE_URL"))
    print(json.dumps(record, indent=2))
    return 0 if record["database_url_available"] else 2


if __name__ == "__main__":
    sys.exit(main())
