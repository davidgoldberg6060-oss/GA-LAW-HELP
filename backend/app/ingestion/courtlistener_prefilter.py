"""Pre-filter the CourtListener opinions bulk CSV down to Georgia lead/majority opinions.

The full opinions file is ~55 GB compressed; streaming it inside one GitHub Actions job runs past
the 6-hour limit. Run this once on a machine with bandwidth, publish the small output (plus the
index cache) as a release asset, and point the import workflow at it (courtlistener_release input).

    lbzip2 -dc opinions-YYYY-MM-DD.csv.bz2 \\
      | python -m app.ingestion.courtlistener_prefilter courtlistener-index.json \\
      | lbzip2 -c > opinions-ga-YYYY-MM-DD.csv.bz2

Output keeps the importer's column names and CSV dialect, only rows of indexed Georgia clusters
with a lead/majority type, and only the first non-empty text field the importer would use, so
importing the output is equivalent to importing the full file.
"""
from __future__ import annotations

import csv
import io
import json
import sys
import time
from typing import Iterable, TextIO

from .import_courtlistener_opinions import MAIN_TYPES, TEXT_FIELDS

COLUMNS = ["id", "cluster_id", "type", *TEXT_FIELDS]


def prefilter(source: TextIO, sink: TextIO, cluster_ids: Iterable[str], progress: TextIO | None = None) -> tuple[int, int]:
    csv.field_size_limit((1 << 31) - 1)
    wanted = set(cluster_ids)
    writer = csv.writer(sink, doublequote=False, escapechar="\\", lineterminator="\n")
    writer.writerow(COLUMNS)
    scanned = kept = 0
    started = time.time()
    for row in csv.DictReader(source, escapechar="\\"):
        scanned += 1
        if progress and scanned % 500000 == 0:
            print(f"scanned={scanned} kept={kept} secs={round(time.time() - started)}", file=progress, flush=True)
        if row.get("cluster_id") not in wanted or row.get("type") not in MAIN_TYPES:
            continue
        texts = dict.fromkeys(TEXT_FIELDS, "")
        for name in TEXT_FIELDS:
            if (row.get(name) or "").strip():
                texts[name] = row[name]
                break
        writer.writerow([row.get("id", ""), row["cluster_id"], row["type"], *texts.values()])
        kept += 1
    return scanned, kept


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python -m app.ingestion.courtlistener_prefilter INDEX_JSON < opinions.csv > ga.csv", file=sys.stderr)
        return 2
    with open(args[0], encoding="utf-8") as handle:
        clusters = json.load(handle)["clusters"].keys()
    source = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", newline="")
    sink = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="")
    scanned, kept = prefilter(source, sink, clusters, progress=sys.stderr)
    sink.flush()
    print(f"DONE scanned={scanned} kept={kept}", file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
