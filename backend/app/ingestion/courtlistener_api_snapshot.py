"""Fetch recent Georgia opinions from the CourtListener v4 API into a JSON-lines snapshot.

Run this where CourtListener does not throttle you (it 429s GitHub's shared runner IPs), upload the
file as a release asset (courtlistener-api-YYYY-MM-DD), then import it with
`import_courtlistener_opinions --source file --records-file ...` (no network).

Uses list endpoints only: clusters list, one dockets list (id__in), and an opinions list filtered by
court + date, so ~30 opinions cost about 5-8 requests. The free key allows 5/min and 125/day. Needs COURTLISTENER_TOKEN in the environment.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from urllib.parse import urlencode

from .import_courtlistener_opinions import API_BASE, BULK_DATE, COURTS, TEXT_FIELDS, _fetch_text, check_url


def fetch_all(url: str, token: str, pause: float, counter: list[int], max_requests: int) -> list[dict]:
    results: list[dict] = []
    while url:
        if counter[0] >= max_requests:
            raise SystemExit(f"stopped: would exceed --max-requests {max_requests}")
        if counter[0]:
            time.sleep(pause)
        counter[0] += 1
        try:
            page = json.loads(_fetch_text(check_url(url), {"Authorization": f"Token {token}"}))
        except Exception as exc:  # show which list call failed and why (never the token)
            body = getattr(exc, "read", lambda: b"")()[:300]
            raise SystemExit(f"request {counter[0]} failed: {exc} {url} {body!r}")
        results.extend(page.get("results", []))
        url = page.get("next")
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--court", default="ga", choices=sorted(COURTS))
    parser.add_argument("--since", required=True, help="YYYY-MM-DD (date_filed on/after)")
    parser.add_argument("--out", required=True)
    parser.add_argument("--pause", type=float, default=20.0)
    parser.add_argument("--cache-dir", help="reuse finished list steps from an earlier, interrupted run")
    parser.add_argument("--max-requests", type=int, default=25)
    args = parser.parse_args(argv)
    if not BULK_DATE.match(args.since):
        parser.error("--since must be YYYY-MM-DD")
    token = os.environ.get("COURTLISTENER_TOKEN", "")
    if not token:
        parser.error("COURTLISTENER_TOKEN is not set")
    n = [0]

    def get(q: dict, path: str) -> list[dict]:
        # Optional per-step cache so a rerun after a 429 does not spend requests again.
        cache = os.path.join(args.cache_dir, path.strip("/") + ".json") if args.cache_dir else None
        if cache and os.path.exists(cache):
            return json.load(open(cache, encoding="utf-8"))
        rows = fetch_all(API_BASE + path + "?" + urlencode(q), token, args.pause, n, args.max_requests)
        if cache:
            os.makedirs(args.cache_dir, exist_ok=True)
            json.dump(rows, open(cache, "w", encoding="utf-8"))
        return rows

    clusters = get({"docket__court": args.court, "date_filed__gte": args.since, "order_by": "id", "page_size": 100,
                    "fields": "id,case_name,date_filed,docket_id,precedential_status,citations,slug"}, "clusters/")
    if not clusters:
        open(args.out, "w").close()
        print(json.dumps({"clusters": 0, "requests": n[0]}))
        return 0
    docket_ids = sorted({int(c["docket_id"]) for c in clusters})
    dockets = {str(d["id"]): d for d in get({"court": args.court, "id__gte": docket_ids[0],
                                              "id__lte": docket_ids[-1], "order_by": "id",
                                              "fields": "id,docket_number,court_id"}, "dockets/")}
    opinions = get({"cluster__docket__court": args.court, "cluster__date_filed__gte": args.since, "order_by": "id",
                    "page_size": 20, "fields": "id,type,cluster_id," + ",".join(TEXT_FIELDS)}, "opinions/")
    by_cluster: dict[str, list[dict]] = {}
    for op in opinions:
        by_cluster.setdefault(str(op.get("cluster_id")), []).append(op)
    written = 0
    with open(args.out, "w", encoding="utf-8") as fh:
        for c in clusters:
            docket = dockets.get(str(c["docket_id"]))
            if docket is None or docket.get("court_id") != args.court:
                continue
            fh.write(json.dumps({"court": args.court, "cluster": c, "docket": docket,
                                 "opinions": by_cluster.get(str(c["id"]), [])}) + "\n")
            written += 1
    print(json.dumps({"clusters": len(clusters), "written": written, "opinions": len(opinions),
                      "requests": n[0]}), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
