#!/usr/bin/env bash
# Runs one legal-source importer for .github/workflows/import-legal-sources.yml.
# Inputs arrive as env vars (never interpolated into the script). Any extra arguments
# (the workflow passes --commit only from its guarded commit step) are appended.
set -euo pipefail
SCRIPTS_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPTS_DIR/../../backend"

# Commit mode: normalize the secret's URL for SQLAlchemy + psycopg v3 (postgresql+psycopg://, sslmode=require).
for arg in "$@"; do
  if [ "$arg" = "--commit" ]; then source "$SCRIPTS_DIR/db-url.sh"; fi
done

case "$LIMIT" in ''|*[!0-9]*) echo "::error::limit must be a whole number"; exit 1 ;; esac
case "$OFFSET" in ''|*[!0-9]*) echo "::error::offset must be a whole number"; exit 1 ;; esac

case "$SOURCE" in
  ocga)
    # SCOPE: comma list of OCGA titles (e.g. "16" or "16,17") or "all"
    args=(-m app.ingestion.import_ocga_release --release "${RELEASE:-release86.2022.11}"
          --title "${SCOPE:-all}" --limit "$LIMIT" --offset "$OFFSET" --quiet) ;;
  courtlistener)
    # SCOPE: "ga", "gactapp" or "ga,gactapp"; bulk files only (no API token needed)
    args=(-m app.ingestion.import_courtlistener_opinions --source bulk --court "${SCOPE:-ga,gactapp}"
          --limit "$LIMIT" --offset "$OFFSET" --index-cache .import-cache/courtlistener-index.json --quiet) ;;
  appeals)
    # SCOPE: judgment date range "YYYY-MM-DD..YYYY-MM-DD" (at most one year)
    if [[ ! "$SCOPE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\.\.[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
      echo "::error::For appeals, scope must be YYYY-MM-DD..YYYY-MM-DD"; exit 1
    fi
    args=(-m app.ingestion.import_appeals_opinions --start "${SCOPE%%..*}" --end "${SCOPE##*..}"
          --limit "$LIMIT" --offset "$OFFSET") ;;
  regulations)
    # SCOPE: rules.sos.ga.gov department numbers ("40", "40,111") or "all"
    args=(-m app.ingestion.import_ga_regulations --department "${SCOPE:-all}"
          --limit "$LIMIT" --offset "$OFFSET" --quiet) ;;
  court_rules)
    # SCOPE: coa, supreme, superior, state, juvenile, probate, magistrate (comma list) or "all".
    # PDFs that robots.txt disallows are reported as blocked_by_robots, never fetched.
    args=(-m app.ingestion.import_court_rules --set "${SCOPE:-all}"
          --limit "$LIMIT" --offset "$OFFSET" --quiet) ;;
  *)
    echo "::error::unknown source: $SOURCE"; exit 1 ;;
esac

python "${args[@]}" "$@"
