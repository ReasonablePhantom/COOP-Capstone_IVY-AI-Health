"""Attempt to fetch each registered source and record what actually happened.

This script NEVER writes a value into a data template. It only:
  1. tries the request,
  2. saves the raw response under data/03_external/raw/ when it succeeds,
  3. records the outcome in data/00_status/fetch_log.csv.

Run without flags for a dry run (prints the plan, touches nothing except the log).
Run with --live to make real requests.

Why this exists: some values (prices, ratings, release notes) change weekly and
must be read at a known date. Generating them offline would be fabrication, so
the pack stores the fetch attempt and its outcome instead.
"""
import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PACK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from config_sources import SOURCES  # noqa: E402

RAW = PACK / "data" / "03_external" / "raw"
STATUS = PACK / "data" / "00_status"
RAW.mkdir(parents=True, exist_ok=True)
STATUS.mkdir(parents=True, exist_ok=True)
LOG = STATUS / "fetch_log.csv"

UA = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}

FIELDS = ["source_id", "priority", "rubric_cells", "url", "attempted_at",
          "status", "http_code", "bytes", "content_type", "saved_file", "error"]


def fetch_one(src, timeout=12):
    req = urllib.request.Request(src["url"], headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            name = f"{src['id']}{'.pdf' if 'pdf' in (r.headers.get('Content-Type') or '') else '.html'}"
            (RAW / name).write_bytes(body)
            return dict(status="OK", http_code=r.status, bytes=len(body),
                        content_type=r.headers.get("Content-Type", ""),
                        saved_file=f"raw/{name}", error="")
    except urllib.error.HTTPError as e:
        return dict(status="HTTP_ERROR", http_code=e.code, bytes=0,
                    content_type="", saved_file="", error=str(e.reason))
    except Exception as e:                                   # noqa: BLE001
        # Fallback to curl for modern TLS / CDN anti-bot resilience on macOS
        import subprocess
        name = f"{src['id']}.pdf" if "pdf" in src["url"].lower() else f"{src['id']}.html"
        out_path = RAW / name
        cmd = ["curl", "-s", "-L", "-A", UA["User-Agent"], "--max-time", str(timeout), src["url"], "-o", str(out_path), "-w", "%{http_code}"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            code = res.stdout.strip()
            if code == "200" and out_path.exists() and out_path.stat().st_size > 0:
                return dict(status="OK", http_code=200, bytes=out_path.stat().st_size,
                            content_type="text/html", saved_file=f"raw/{name}", error="")
            elif code and code not in ("000", ""):
                return dict(status="HTTP_ERROR", http_code=int(code), bytes=0,
                            content_type="", saved_file="", error=f"HTTP {code}")
        except Exception:
            pass
        return dict(status="NETWORK_ERROR", http_code="", bytes=0,
                    content_type="", saved_file="", error=f"{type(e).__name__}: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="make real network requests")
    ap.add_argument("--only", default=None, help="comma separated source ids")
    args = ap.parse_args()

    wanted = set(args.only.split(",")) if args.only else None
    srcs = [s for s in SOURCES if not wanted or s["id"] in wanted]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    rows = []
    for s in srcs:
        if not args.live:
            rows.append({"source_id": s["id"], "priority": s["priority"],
                         "rubric_cells": "+".join(s["cells"]), "url": s["url"],
                         "attempted_at": now, "status": "NOT_ATTEMPTED",
                         "http_code": "", "bytes": "", "content_type": "",
                         "saved_file": "", "error": "dry run"})
            print(f"  [dry] {s['priority']} {s['id']:<26} {s['url']}")
            continue
        print(f"  [live] {s['id']} ...", end="", flush=True)
        res = fetch_one(s)
        print(f" {res['status']} {res['http_code']} {res['bytes']}B")
        rows.append({"source_id": s["id"], "priority": s["priority"],
                     "rubric_cells": "+".join(s["cells"]), "url": s["url"],
                     "attempted_at": now, **res})

    # merge with what is already logged, keyed on source_id
    existing = {}
    if LOG.exists():
        with LOG.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                existing[r["source_id"]] = r
    for r in rows:
        existing[r["source_id"]] = r
    ordered = sorted(existing.values(), key=lambda r: (r["priority"], r["source_id"]))
    with LOG.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(ordered)

    ok = sum(r["status"] == "OK" for r in rows)
    summary = {
        "attempted_at": now, "mode": "live" if args.live else "dry-run",
        "sources": len(ordered), "ok": ok,
        "failed": sum(r["status"] not in ("OK", "NOT_ATTEMPTED") for r in rows),
        "by_status": {st: sum(r["status"] == st for r in rows)
                      for st in sorted({r["status"] for r in rows})},
    }
    (STATUS / "fetch_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n  {ok}/{len(rows)} fetched OK -> data/00_status/fetch_log.csv")


if __name__ == "__main__":
    main()
