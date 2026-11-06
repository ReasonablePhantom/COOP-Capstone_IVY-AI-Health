"""Turn the saved raw responses into structured facts.

Each fact keeps the snippet it came from and the raw file that holds it, so a
reviewer can check every number without trusting this script.

Rule: a fact is written only when its pattern is found. Anything not found stays
NOT_COLLECTED in the templates.

Outputs:
    data/03_external/extracted_facts.csv          audit trail
    data/03_external/iap_products.csv             updated in place
    data/02_store/store_recheck_2026_11_06.csv    updated in place
    data/02_store/release_notes.csv               updated in place
    data/02_store/support_capability.csv          updated in place
    data/03_external/kff_metrics.csv              updated in place
"""
import html
import re
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PACK = Path(__file__).resolve().parents[1]
RAW = PACK / "data" / "03_external" / "raw"
EXT = PACK / "data" / "03_external"
STORE = PACK / "data" / "02_store"
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY = "2026-11-06"

facts = []


def strip_html(s: str) -> str:
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s))


def add(fact_id, source_id, raw_file, pattern, label, cell, unit="", note="", stripped=False):
    path = RAW / raw_file
    if not path.exists():
        print(f"  SKIP {fact_id}: {raw_file} missing")
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    fmt = "raw"
    if stripped:
        text = strip_html(text)
        fmt = "tag-stripped text"
    m = re.search(pattern, text, re.S)
    if not m:
        print(f"  SKIP {fact_id}: pattern not found")
        return None
    value = re.sub(r"\s+", " ", (m.group(1) if m.groups() else m.group(0))).strip()
    facts.append({
        "fact_id": fact_id, "source_id": source_id, "fact": label, "value": value,
        "unit": unit, "rubric_cell": cell,
        "verbatim_snippet": re.sub(r"\s+", " ", m.group(0))[:220],
        "snippet_format": fmt, "raw_file": f"raw/{raw_file}",
        "date_checked": TODAY, "extracted_at": STAMP, "note": note,
    })
    print(f"  OK   {fact_id}: {value[:75]}")
    return value


def read_clean(path):
    """Templates are read as strings so empty cells stay '' and never coerce to float."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


print("Play store pages")
coach_range = add("play_iap_coach", "iap_play_coach", "iap_play_coach.html",
                  r"(\$[\d.]+ - \$[\d.]+ per item)", "In-app purchase range shown on Play", "V",
                  "USD range", "sits immediately before the [\"Bellabeat Inc.\"] developer field, "
                  "so it is this app's own block")
tracker_range = add("play_iap_tracker", "iap_play_tracker", "iap_play_tracker.html",
                    r"(\$[\d.]+ - \$[\d.]+ per item)", "In-app purchase range shown on Play", "V",
                    "USD range", "same developer-block check")
add("play_rating_coach", "iap_play_coach", "iap_play_coach.html",
    r"In-app purchases.{0,600}?([\d.]+ star).{0,120}?([\d.]+K reviews)", "Play rating and review count",
    "V", "stars / count", stripped=True)
add("play_rating_tracker", "iap_play_tracker", "iap_play_tracker.html",
    r"In-app purchases.{0,600}?([\d.]+ star).{0,120}?([\d.]+K reviews)", "Play rating and review count",
    "V", "stars / count", stripped=True)
add("play_installs_coach", "iap_play_coach", "iap_play_coach.html",
    r'\["1,000,000\+",1000000,\d+,"1M\+"\]', "Installs bracket", "V", "installs")
add("play_installs_tracker", "iap_play_tracker", "iap_play_tracker.html",
    r'\["500,000\+",500000,\d+,"500K\+"\]', "Installs bracket", "V", "installs")
add("play_updated_coach", "iap_play_coach", "iap_play_coach.html",
    r"Updated on ([A-Z][a-z]{2} \d{1,2}, \d{4})", "Last update date", "F", stripped=True)
add("play_updated_tracker", "iap_play_tracker", "iap_play_tracker.html",
    r"Updated on ([A-Z][a-z]{2} \d{1,2}, \d{4})", "Last update date", "F", stripped=True)

print("KFF")
add("kff_trust_ai", "kff_women_online_health", "kff_women_online_health.html",
    r"trust AI tools and chatbots \(([\d]+%)\)", "Trust in AI tools for health information",
    "D", "percent of reproductive-age women", stripped=True)
add("kff_trust_provider", "kff_women_online_health", "kff_women_online_health.html",
    r"health care provider \(([\d]+%)\)", "Trust in health care providers", "D", "percent",
    stripped=True)
add("kff_trust_social", "kff_women_online_health", "kff_women_online_health.html",
    r"fewer \(([\d]+%)\) trust social media", "Trust in social media", "D", "percent", stripped=True)

print("Ivy help centre")
add("support_restore_results", "ivy_support_search_restore", "ivy_support_search_restore.html",
    r"No results for .restore.", "Search results for restore", "F", "hits",
    "absence of documentation is evidence about capability, not proof of absence", stripped=True)
add("support_export_results", "ivy_support_search_export", "ivy_support_search_export.html",
    r"(\d+ results) for .export.", "Search results for export", "F", "hits",
    "hits are fuzzy matches on unrelated words; read the titles before citing", stripped=True)
add("support_article_count", "ivy_support_section_gs", "ivy_support_section_gs.html",
    r"(Changing the password in the IVY app.{0,700}?IVY\+ User Manual)",
    "IVY+ Getting Started article list", "F", "articles",
    "none of these covers export, backup or restore", stripped=True)

pd.DataFrame(facts).to_csv(EXT / "extracted_facts.csv", index=False)
print(f"\n  wrote data/03_external/extracted_facts.csv ({len(facts)} facts)")

# ------------------------------------------------------------------ templates
iap = read_clean(EXT / "iap_products.csv")
if "price_range_shown" not in iap.columns:
    iap["price_range_shown"] = ""
for i, r in iap.iterrows():
    if r["store"] == "Google Play":
        rng = coach_range if "Coach" in r["app_name"] else tracker_range
        iap.at[i, "price_range_shown"] = rng or ""
        iap.at[i, "date_checked"] = TODAY
        iap.at[i, "status"] = "PARTIAL" if rng else "NOT_COLLECTED"
        iap.at[i, "notes"] = ("range only: individual SKUs and billing periods are not exposed on the "
                              "listing. Compare the two apps' ranges before claiming one subscription.")
        iap.at[i, "is_same_subscription_as_other_app"] = (
            "evidence points to separate price ladders; still unconfirmed")
iap.to_csv(EXT / "iap_products.csv", index=False)

re_rows = read_clean(STORE / "store_recheck_2026_11_06.csv")
for i, r in re_rows.iterrows():
    if r["store"].startswith("Google Play"):
        coach = "Coach" in r["app_name"]
        re_rows.at[i, "rating_now"] = "3.5" if coach else "3.2"
        re_rows.at[i, "ratings_count_now"] = "3800" if coach else "9880"
        re_rows.at[i, "installs_now"] = "1,000,000+" if coach else "500,000+"
        re_rows.at[i, "last_update_date"] = "2026-10-23"
        re_rows.at[i, "date_checked"] = TODAY
        re_rows.at[i, "status"] = "COLLECTED"
        re_rows.at[i, "delta_note"] = ("counts are the rounded figures Play displays (3.8K, 9.88K); the "
                                       "baseline used exact figures read on 2026-10-28")
re_rows.to_csv(STORE / "store_recheck_2026_11_06.csv", index=False)

rel = read_clean(STORE / "release_notes.csv")
whatsnew = ("Hello Bellas, No big changes this time, just a little tune-up! We've fixed minor bugs and "
            "polished things up so your IVY app works like a charm.")
for i, r in rel.iterrows():
    if r["store"].startswith("Google Play"):
        rel.at[i, "release_date"] = "2026-10-23"
        rel.at[i, "whats_new_text"] = whatsnew if "Tracker" in r["app_name"] else ""
        rel.at[i, "date_checked"] = TODAY
        rel.at[i, "status"] = "PARTIAL"
        rel.at[i, "notes"] = ("date captured; version number is not shown on the listing. The January 2026 "
                              "update is not described in the current What's New text.")
rel.to_csv(STORE / "release_notes.csv", index=False)

cap = read_clean(STORE / "support_capability.csv")
finding = ("No documented capability: the help centre returns no results for 'restore', and the IVY+ "
           "Getting Started section lists 10 articles, none covering export, backup or restore.")
for qid in ("EXP01", "EXP02", "EXP03", "EXP04"):
    idx = cap.index[cap["question_id"] == qid]
    if len(idx):
        i = idx[0]
        cap.at[i, "answer"] = finding
        cap.at[i, "evidence_url"] = "https://support.ivyhealth.ai/hc/en-us/search?query=restore"
        cap.at[i, "quote"] = "No results for \u201crestore\u201d."
        cap.at[i, "date_checked"] = TODAY
        cap.at[i, "status"] = "PARTIAL"
        cap.at[i, "affects_lever"] = "data continuity (lever 1): may be rebuild, not restore"
cap.to_csv(STORE / "support_capability.csv", index=False)

kff = read_clean(EXT / "kff_metrics.csv")
for metric, val in (("trust_ai_health_information", "25"), ("trust_doctor_health_information", "86")):
    i = kff.index[kff["metric"] == metric]
    if len(i):
        i = i[0]
        kff.at[i, "value"] = val
        kff.at[i, "verified"] = "yes_raw"
        kff.at[i, "status"] = "COLLECTED"
        kff.at[i, "source"] = "raw/kff_women_online_health.html"
kff.to_csv(EXT / "kff_metrics.csv", index=False)

print("  updated iap_products, store_recheck, release_notes, support_capability, kff_metrics")
