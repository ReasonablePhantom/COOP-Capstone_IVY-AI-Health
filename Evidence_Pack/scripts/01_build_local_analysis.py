"""Build every analysable table that the LOCAL data can support.

No value is invented: every number here is computed from a file that already
exists in the capstone folder. Provenance columns record the source file.

Outputs -> Evidence_Pack/data/01_corpus/ and data/02_store/
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]          # Capstone_Project
PACK = Path(__file__).resolve().parents[1]          # Evidence_Pack
OUT_CORPUS = PACK / "data" / "01_corpus"
OUT_STORE = PACK / "data" / "02_store"
for d in (OUT_CORPUS, OUT_STORE):
    d.mkdir(parents=True, exist_ok=True)

STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
CLEAN = ROOT / "ivy_reviews_clean.csv"
SAMPLE = ROOT / "pod2_25_recent_sample.csv"
BASELINE = ROOT / "ivy_store_baselines.csv"
DEDUPE = ROOT / "dedupe_report.csv"

reviews = pd.read_csv(CLEAN, dtype={"review_id": str})
reviews["date"] = pd.to_datetime(reviews["date"], format="mixed", utc=True)
sample = pd.read_csv(SAMPLE, dtype={"review_id": str})

CUTOFF = pd.Timestamp("2025-11-06", tz="UTC")      # per the pod's own 12-month rule


def write(df, path, note=""):
    df = df.copy()
    df.insert(0, "generated_at", STAMP)
    df.to_csv(path, index=False)
    print(f"  wrote {path.relative_to(PACK)}  ({len(df)} rows)" + (f"  # {note}" if note else ""))


# --------------------------------------------------------------------------
# 1. Corpus summary, one row per app x store
# --------------------------------------------------------------------------
rows = []
for (app, store), g in reviews.groupby(["app_name", "store"]):
    rows.append({
        "app_name": app, "store": store, "n": len(g),
        "mean_rating": round(g.rating.mean(), 3),
        "share_1_2": round((g.rating <= 2).mean(), 4),
        "share_5": round((g.rating == 5).mean(), 4),
        "first_date": g.date.min().date().isoformat(),
        "last_date": g.date.max().date().isoformat(),
        "n_burst": int(g.is_burst.sum()),
        "share_non_english": round((g.lang_guess.fillna("ascii") != "ascii").mean(), 4),
        "source_file": CLEAN.name,
    })
corpus = pd.DataFrame(rows).sort_values(["app_name", "store"])
write(corpus, OUT_CORPUS / "corpus_summary.csv")

# --------------------------------------------------------------------------
# 2. Rating distribution
# --------------------------------------------------------------------------
dist = (reviews.groupby(["app_name", "store", "rating"]).size()
        .rename("n").reset_index())
dist["share"] = dist.n / dist.groupby(["app_name", "store"]).n.transform("sum")
dist["share"] = dist.share.round(4)
write(dist, OUT_CORPUS / "rating_distribution.csv")

# --------------------------------------------------------------------------
# 3. Keyword evidence (real counts, regex recorded for audit)
# --------------------------------------------------------------------------
import sys
sys.path.insert(0, str(Path(__file__).parent))
from config_sources import KEYWORDS  # noqa: E402

kw_rows = []
for name, cell, pattern in KEYWORDS:
    for app, g in reviews.groupby("app_name"):
        hit = g.review_text.fillna("").str.contains(pattern, case=False, regex=True)
        kw_rows.append({
            "keyword_group": name, "rubric_cell": cell, "app_name": app,
            "n_matched": int(hit.sum()), "n_app_total": len(g),
            "share": round(hit.mean(), 4),
            "regex": pattern,
            "mean_rating_matched": round(g.loc[hit, "rating"].mean(), 3) if hit.any() else None,
        })
write(pd.DataFrame(kw_rows), OUT_CORPUS / "keyword_evidence.csv",
      "regex kept so a reviewer can reproduce every count")

# --------------------------------------------------------------------------
# 4. Version timeline reconstructed from reviews (Feasibility / event dating)
# --------------------------------------------------------------------------
vt = (reviews.dropna(subset=["app_version"])
      .groupby(["app_name", "app_version"])
      .agg(n=("rating", "size"), first_date=("date", "min"),
           last_date=("date", "max"), mean_rating=("rating", "mean"))
      .reset_index())
vt["first_date"] = vt.first_date.dt.date.astype(str)
vt["last_date"] = vt.last_date.dt.date.astype(str)
vt["mean_rating"] = vt.mean_rating.round(3)
vt = vt.sort_values(["app_name", "first_date"])
write(vt, OUT_CORPUS / "version_timeline_from_reviews.csv",
      "proxy for release dates; confirm against store release notes")

# --------------------------------------------------------------------------
# 5. Monthly trend with burst flag
# --------------------------------------------------------------------------
m = reviews.copy()
m["month"] = m.date.dt.strftime("%Y-%m")
mt = (m.groupby(["app_name", "month"])
      .agg(n=("rating", "size"), mean_rating=("rating", "mean"),
           share_5=("rating", lambda s: (s == 5).mean()),
           share_1_2=("rating", lambda s: (s <= 2).mean()),
           n_burst=("is_burst", "sum"))
      .reset_index())
for c in ("mean_rating", "share_5", "share_1_2"):
    mt[c] = mt[c].round(4)
write(mt, OUT_CORPUS / "monthly_trend_with_burst.csv")

# --------------------------------------------------------------------------
# 6. Sensitivity table (the three analyses the pod's plan promises)
# --------------------------------------------------------------------------
primary = sample.copy()
primary["date"] = pd.to_datetime(primary["date"], format="mixed", utc=True)
win = reviews[reviews.date >= CUTOFF]

sens = []
for app in reviews.app_name.unique():
    short = "Tracker" if "Tracker" in app else "Coach"
    p = primary[primary.app_name == app]
    w = win[win.app_name == app]
    wi = w[w.store == "Apple App Store"]
    wp = w[w.store == "Google Play"]
    s = w[w.is_burst == False]  # noqa: E712
    for label, frame in [
        ("primary sample (25 per app)", p),
        ("12-month corpus, both stores", w),
        ("12-month corpus, iOS only", wi),
        ("12-month corpus, Play only", wp),
        ("12-month corpus, burst rows removed", s),
    ]:
        if len(frame):
            sens.append({
                "app_name": app, "app_short": short, "scenario": label,
                "n": len(frame), "mean_rating": round(frame.rating.mean(), 3),
                "share_1_2": round((frame.rating <= 2).mean(), 4),
                "share_5": round((frame.rating == 5).mean(), 4),
            })
write(pd.DataFrame(sens), OUT_CORPUS / "sensitivity_scenarios.csv")

# --------------------------------------------------------------------------
# 7. Reply rate with honest denominators
# --------------------------------------------------------------------------
rr = (reviews.assign(has_reply=reviews.developer_reply.notna())
      .groupby(["app_name", "source_batch"])
      .agg(n=("has_reply", "size"), n_reply=("has_reply", "sum"))
      .reset_index())
rr["share_reply"] = (rr.n_reply / rr.n).round(4)
rr["denominator_note"] = rr.source_batch.map(
    lambda b: "reply field populated" if "Our Scrape" in b
    else "reply field all null: unknown, not 'no reply'")
write(rr, OUT_CORPUS / "reply_rate_by_batch.csv",
      "a null reply is UNKNOWN, not zero; denominators must not be pooled")

# --------------------------------------------------------------------------
# 8. Country coverage
# --------------------------------------------------------------------------
cc = (reviews.groupby(["country"]).size().rename("n").reset_index()
      .sort_values("n", ascending=False))
cc["share"] = (cc.n / len(reviews)).round(4)
write(cc, OUT_CORPUS / "country_coverage.csv")

# --------------------------------------------------------------------------
# 9. Data quality flags, computed where computable
# --------------------------------------------------------------------------
flags = []
nat = reviews.date.isna().sum()
flags.append({"flag": "date_parse_failures", "value": int(nat),
              "expectation": "0 with format='mixed'",
              "status": "PASS" if nat == 0 else "FAIL",
              "action": "reparse or investigate" if nat else "none"})
flags.append({"flag": "label_blank_primary_theme", "value": int(sample.primary_theme.isna().sum()),
              "expectation": "0 before Night 4",
              "status": "FAIL" if sample.primary_theme.isna().any() else "PASS",
              "action": "code every sampled review against a 7-theme taxonomy"})
flags.append({"flag": "primary_sample_rows", "value": int(len(sample)),
              "expectation": "50 (25 per app, per the Brief)",
              "status": "FAIL" if len(sample) != 50 else "PASS",
              "action": "re-pull the missing Coach review or disclose n=49"})
ne = (reviews.lang_guess.fillna("ascii") != "ascii").mean()
flags.append({"flag": "share_non_english", "value": round(float(ne), 4),
              "expectation": "disclosed in limits", "status": "INFO",
              "action": "read 30 and re-tag, or use multilingual keywords"})
dup_text = reviews.review_text.duplicated(keep=False).mean()
flags.append({"flag": "share_duplicated_text", "value": round(float(dup_text), 4),
              "expectation": "known: same phrases repeated by different users", "status": "INFO",
              "action": "de-duplicate on review_id only"})
flags.append({"flag": "cross_batch_duplicates_removed",
              "value": int(len(pd.read_csv(DEDUPE))) if DEDUPE.exists() else None,
              "expectation": "documented in the methodology",
              "status": "INFO",
              "action": "state that removal used text matching, not review_id"})
coach_ios = reviews[(reviews.app_name.str.contains("Coach")) & (reviews.store == "Apple App Store")]
age_days = int((pd.Timestamp("2026-11-06", tz="UTC") - coach_ios.date.max()).days)
flags.append({"flag": "coach_ios_staleness_days", "value": age_days,
              "expectation": "under 30 days at submission",
              "status": "FAIL" if age_days > 30 else "PASS",
              "action": "re-scrape the Coach, or disclose the window difference"})
flags_df = pd.DataFrame(flags)
flags_df["value"] = flags_df["value"].map(
    lambda v: "" if v is None else (str(int(v)) if float(v) == int(v) else f"{float(v):.4f}"))
write(flags_df, OUT_CORPUS / "data_quality_flags.csv")

# --------------------------------------------------------------------------
# 10. Store baseline, cleaned and dated
# --------------------------------------------------------------------------
base = pd.read_csv(BASELINE)
base["installs_lower_bound"] = (base.installs.astype(str)
                                .str.replace(r"[^0-9]", "", regex=True)
                                .replace("", None).astype("Int64"))
base["source_file"] = BASELINE.name
write(base, OUT_STORE / "store_baseline_clean.csv")

# --------------------------------------------------------------------------
# Run manifest
# --------------------------------------------------------------------------
manifest = {
    "generated_at": STAMP,
    "inputs": [str(p.name) for p in (CLEAN, SAMPLE, BASELINE, DEDUPE) if p.exists()],
    "input_rows": {"reviews_clean": len(reviews), "sample_50": len(sample),
                   "store_baseline": len(base)},
    "note": "All values computed from local files only. Nothing fetched, nothing imputed.",
}
(OUT_CORPUS / "_run_manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"  wrote data/01_corpus/_run_manifest.json")
print("\nDone: local analysis tables built.")
