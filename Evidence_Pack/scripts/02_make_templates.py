"""Create the empty, status-tracked templates for every value that needs the
outside world.

Hard rule: this script writes NO factual value. Every row carries
status = NOT_COLLECTED until a human fills it from the live page. The only
prefilled text is structure (app names, store names, URLs, the questions to
answer) and values that already exist in a local file, which are labelled with
their local source.

Outputs -> Evidence_Pack/data/02_store/ and data/03_external/
"""
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PACK = Path(__file__).resolve().parents[1]
OUT_STORE = PACK / "data" / "02_store"
OUT_EXT = PACK / "data" / "03_external"
for d in (OUT_STORE, OUT_EXT):
    d.mkdir(parents=True, exist_ok=True)

STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
TODAY = "2026-11-06"
NC = "NOT_COLLECTED"

APPS = [
    ("IVY Period & Pregnancy Tracker", "Apple App Store", "436762566",
     "https://apps.apple.com/us/app/id436762566"),
    ("IVY Period & Pregnancy Tracker", "Google Play", "org.nanobit.perioddiary",
     "https://play.google.com/store/apps/details?id=org.nanobit.perioddiary"),
    ("IVY Wellness Coach", "Apple App Store", "1005052173",
     "https://apps.apple.com/us/app/id1005052173"),
    ("IVY Wellness Coach", "Google Play", "com.bellabeat.cacao",
     "https://play.google.com/store/apps/details?id=com.bellabeat.cacao"),
]


def write(df, path):
    df = df.copy()
    df.insert(0, "generated_at", STAMP)
    df.to_csv(path, index=False)
    print(f"  wrote {path.relative_to(PACK)}  ({len(df)} rows)")


# ---------------------------------------------------------------- 1. In-app purchases
iap = pd.DataFrame([{
    "app_name": app, "store": store, "store_id": sid, "source_url": url,
    "sku_name": "", "product_type": "", "price_usd": "", "billing_period": "",
    "trial_days": "", "is_same_subscription_as_other_app": "",
    "date_checked": "", "screenshot_file": "",
    "status": NC, "notes": "",
} for app, store, sid, url in APPS])
write(iap, OUT_EXT / "iap_products.csv")

# ------------------------------------------------ 2. Store re-check (baseline vs now)
baseline = pd.read_csv(ROOT / "ivy_store_baselines.csv", dtype={"store_id": str})
URL_BY_ID = {sid: url for _a, _s, sid, url in APPS}
re_rows = []
for _, r in baseline.iterrows():
    re_rows.append({
        "app_name": r.app_name, "store": r.store, "store_id": r.store_id,
        "baseline_rating": r.overall_rating,
        "baseline_ratings_count": r.total_ratings_count,
        "baseline_installs": r.installs,
        "baseline_date": r.date_checked,
        "rating_now": "", "ratings_count_now": "", "installs_now": "",
        "last_update_date": "", "version_now": "",
        "date_checked": "",
        "source_url": URL_BY_ID[str(r.store_id)],
        "status": NC, "delta_note": "",
    })
write(pd.DataFrame(re_rows), OUT_STORE / "store_recheck_2026_11_06.csv")

# --------------------------------------------------------- 3. Release notes timeline
rel = pd.DataFrame([{
    "app_name": app, "store": store, "version": "", "release_date": "",
    "whats_new_text": "", "source_url": url, "date_checked": "",
    "status": NC, "notes": "focus on the January 2026 update",
} for app, store, _sid, url in APPS])
write(rel, OUT_STORE / "release_notes.csv")

# ------------------------------------------------ 4. Support capability questions
QUESTIONS = [
    ("EXP01", "Can a user export their cycle history (file or share)?", "F"),
    ("EXP02", "Is there a cloud backup, or is data device-local?", "F"),
    ("EXP03", "After reinstalling, does history return or is it lost?", "F"),
    ("EXP04", "Can history move to a new phone automatically?", "F"),
    ("EXP05", "Can one account see data from both apps (Coach and Tracker)?", "F"),
    ("EXP06", "Does connecting an IVY device make its data visible in the Tracker?", "F"),
    ("EXP07", "Is account deletion available in-app, and what happens to the data?", "F"),
]
cap = pd.DataFrame([{
    "question_id": qid, "question": q, "rubric_cell": cell,
    "answer": "", "evidence_url": "", "quote": "", "date_checked": "",
    "status": NC, "affects_lever": "data continuity (lever 1)" if qid in ("EXP01", "EXP02", "EXP03", "EXP04") else "",
} for qid, q, cell in QUESTIONS])
write(cap, OUT_STORE / "support_capability.csv")

# ------------------------------------------------------- 5. Competitor benchmarks
comp_rows = []
for name, url, note in [
    ("Flo", "https://flo.health/", "AI assistant already shipped"),
    ("Clue", "https://helloclue.com/", "membership anchor"),
    ("Oura", "https://ouraring.com/membership", "hardware plus subscription"),
    ("Calm", "https://www.calm.com/", "content subscription contrast"),
]:
    for tier in ("free", "premium"):
        comp_rows.append({
            "competitor": name, "tier": tier, "price_usd": "", "billing_period": "",
            "trial_days": "", "ai_feature_included": "", "serves_perimenopause": "",
            "source_url": url, "date_checked": "", "status": NC, "notes": note,
        })
write(pd.DataFrame(comp_rows), OUT_EXT / "competitor_pricing.csv")

# ------------------------------------------------------------- 6. KFF / survey metrics
kff = pd.DataFrame([
    # this one is REAL and already in a local file
    {"metric": "used_ai_chatbot_for_health", "segment": "Women", "value": "42",
     "unit": "percent", "survey": "KFF (Sept 2026)", "period": "2026-09",
     "source": "data-PmfG5.csv (local)", "source_url": "", "verified": "yes_local_file",
     "status": "COLLECTED", "notes": "use figure only; trust and methods still missing"},
    {"metric": "used_ai_chatbot_for_health", "segment": "Men (reference)", "value": "46",
     "unit": "percent", "survey": "KFF (Sept 2026)", "period": "2026-09",
     "source": "data-PmfG5.csv (local)", "source_url": "", "verified": "yes_local_file",
     "status": "COLLECTED", "notes": ""},
    {"metric": "trust_ai_health_information", "segment": "Women", "value": "",
     "unit": "percent", "survey": "KFF (Sept 2026)", "period": "2026-09",
     "source": "", "source_url":
     "https://www.kff.org/womens-health-policy/womens-experiences-accessing-health-information-online-trusted-sources-and-contraceptive-information/",
     "verified": "", "status": NC, "notes": "pod notes cite 25%; confirm on the page before use"},
    {"metric": "trust_doctor_health_information", "segment": "Women", "value": "",
     "unit": "percent", "survey": "KFF (Sept 2026)", "period": "2026-09",
     "source": "", "source_url":
     "https://www.kff.org/womens-health-policy/womens-experiences-accessing-health-information-online-trusted-sources-and-contraceptive-information/",
     "verified": "", "status": NC, "notes": "pod notes cite 86%; confirm on the page before use"},
    {"metric": "sample_size_and_method", "segment": "US adults", "value": "",
     "unit": "n", "survey": "KFF (Sept 2026)", "period": "2026-09",
     "source": "", "source_url": "", "verified": "", "status": NC,
     "notes": "required for the proxy statement"},
])
write(kff, OUT_EXT / "kff_metrics.csv")

# ------------------------------------------------------------- 7. Google Trends
trends = pd.DataFrame([{
    "term": t, "geo": "US", "date_from": "2021-11-01", "date_to": "2026-11-01",
    "month": "", "index_0_100": "", "source_url": "https://trends.google.com/trends/explore",
    "date_checked": "", "status": NC,
} for t in ("period tracker", "perimenopause", "AI health assistant")])
write(trends, OUT_EXT / "google_trends.csv")

# --------------------------------------------------------- 8. Regulatory records
reg = pd.DataFrame([
    {"record_id": "DEN170052", "agency": "FDA", "pathway": "De Novo",
     "subject": "Natural Cycles", "decision_date": "", "indication": "",
     "device_type": "", "source_url": "https://www.accessdata.fda.gov/cdrh_docs/pdf17/DEN170052.pdf",
     "verified": "", "status": NC,
     "notes": "the Brief p.10 names this record; decision date and indication must be read from the source"},
    {"record_id": "FTC-FLO-2021", "agency": "FTC", "pathway": "Consent order",
     "subject": "Flo Health", "decision_date": "", "indication": "",
     "device_type": "", "source_url": "https://www.ftc.gov/",
     "verified": "", "status": NC,
     "notes": "the Brief p.11 names this case; locate the 2021 press release on ftc.gov"},
])
write(reg, OUT_EXT / "regulatory_records.csv")

# --------------------------------------------------------------- 9. Small survey
survey = pd.DataFrame([{
    "respondent_id": "", "date": "", "age_band": "", "uses_cycle_app": "",
    "q_when_prediction_wrong": "", "q_would_trust_history_explanation": "",
    "q_would_pay_for_summary": "", "q_current_app": "",
    "consent_no_health_details": "", "status": NC, "notes": "habits and preferences only",
}])
write(survey, OUT_EXT / "survey_responses.csv")

# ------------------------------------------------------------- 10. Forum quotes
quotes = pd.DataFrame([{
    "subreddit": s, "theme": "", "quote_short": "", "date_seen": "", "post_url": "",
    "status": NC, "notes": "short phrases only, never usernames"
} for s in ("r/menopause", "r/Perimenopause", "r/xxfitness", "r/fitbit", "r/ouraring")])
write(quotes, OUT_EXT / "reddit_quotes.csv")

print("\nDone: templates created. Every row starts NOT_COLLECTED.")
print("Only the two KFF use figures are filled, because they come from data-PmfG5.csv.")
