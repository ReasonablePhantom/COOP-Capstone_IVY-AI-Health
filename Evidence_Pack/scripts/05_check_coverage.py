"""Report, per rubric cell, what is actually supported right now.

Reads only files inside the pack (plus the local corpus summary) and prints a
coverage table plus the blockers. Exit code 1 when a P0 blocker remains, so this
can be used as a gate before submitting.
"""
from pathlib import Path

import pandas as pd

PACK = Path(__file__).resolve().parents[1]
DATA = PACK / "data"
EXT, STORE, CORP = DATA / "03_external", DATA / "02_store", DATA / "01_corpus"


def load(path, dtype=str):
    return pd.read_csv(path, dtype=dtype, keep_default_na=False) if path.exists() else pd.DataFrame()


def collected(df, col="status"):
    if df.empty or col not in df.columns:
        return 0
    return int(df[col].isin(["COLLECTED", "PARTIAL"]).sum())


iap = load(EXT / "iap_products.csv")
recheck = load(STORE / "store_recheck_2026_11_06.csv")
notes = load(STORE / "release_notes.csv")
cap = load(STORE / "support_capability.csv")
kff = load(EXT / "kff_metrics.csv")
comp = load(EXT / "competitor_pricing.csv")
trends = load(EXT / "google_trends.csv")
reg = load(EXT / "regulatory_records.csv")
survey = load(EXT / "survey_responses.csv")
quotes = load(EXT / "reddit_quotes.csv")
facts = load(EXT / "extracted_facts.csv")
corpus = load(CORP / "corpus_summary.csv")

rows = []


def add(cell, requirement, file, got, total, blocker, action):
    if got == 0:
        status = "MISSING"
    elif got >= total:
        status = "SUPPORTED"
    else:
        status = "PARTIAL"
    rows.append({"rubric_cell": cell, "requirement": requirement, "evidence_file": file,
                 "evidence_rows": got, "rows_needed": total, "status": status,
                 "blocker": blocker, "next_action": action})


n_reviews = int(corpus["n"].astype(int).sum()) if not corpus.empty else 0
add("D", "review evidence, both stores", "01_corpus/corpus_summary.csv",
    sum(1 for _ in range(len(corpus))), 4,
    "convenience sample; Coach iOS stops 2026-02-08",
    "disclose sampling and window in the limits")
add("D", "theme coding of the primary sample", "03_external/../01_corpus (coding)",
    0, 49, "all 49 sampled reviews have no primary theme",
    "code every review against a 7-theme taxonomy")
add("D", "AI trust context (KFF)", "03_external/kff_metrics.csv",
    collected(kff), 4, "sampling note still missing", "add the survey n and method")
add("D", "own 5-10 person survey", "03_external/survey_responses.csv",
    0, 1, "no responses collected", "run the habit-only survey")
add("D", "forum quotes (qualitative side)", "03_external/reddit_quotes.csv", 0, 5,
    "no quotes captured", "capture short phrases, no usernames")
add("D", "search interest over time", "03_external/google_trends.csv", 0, 3,
    "trends blocked from this machine", "open Google Trends manually and record the index")

add("F", "data export / backup / restore capability", "02_store/support_capability.csv",
    collected(cap), 7, "only an absence of documentation, not a confirmed limitation",
    "ask support directly, or confirm from in-app settings")
add("F", "release dates and version timeline", "02_store/release_notes.csv",
    collected(notes), 4, "January 2026 update not described in current notes",
    "pull the version history from the stores")
add("F", "regulatory line (FDA pathway)", "03_external/regulatory_records.csv",
    0, 2, "record named in the Brief but not read at source",
    "read DEN170052 and record the indication and date")

add("V", "store scale (ratings, installs)", "02_store/store_recheck_2026_11_06.csv",
    collected(recheck), 4, "iOS listings unreachable from this machine",
    "re-check the two iOS listings in a browser")
add("V", "price data", "03_external/iap_products.csv", collected(iap), 4,
    "no individual price points yet", "capture monthly and annual price per app")
add("V", "competitor benchmarks", "03_external/competitor_pricing.csv",
    collected(comp), 8, "no competitor price captured",
    "record Flo, Clue, Oura and Calm tier prices with dates")

add("S", "Ivy's own platform language, dated", "03_external (ivy_home: fetch failed)",
    0, 1, "ivyhealth.ai unreachable from this machine",
    "open the page and record the exact phrasing with a date")
add("S", "evidence that AI is not a purchase driver", "01_corpus/keyword_evidence.csv",
    1, 1, "", "keep the 0.26% figure and pair it with the KFF trust finding")
add("S", "privacy / regulatory context", "03_external/regulatory_records.csv",
    0, 1, "FTC case not read at source", "locate the 2021 Flo order")

cov = pd.DataFrame(rows)
cov.to_csv(DATA / "04_gaps" / "rubric_coverage.csv", index=False) if (DATA / "04_gaps").exists() else None
(DATA / "04_gaps").mkdir(exist_ok=True)
cov.to_csv(DATA / "04_gaps" / "rubric_coverage.csv", index=False)

print(f"{'cell':<5}{'status':<12}{'file':<42}requirement")
print("-" * 110)
for _, r in cov.iterrows():
    print(f"{r.rubric_cell:<5}{r.status:<12}{r.evidence_file:<42}{r.requirement}")

blocked = cov[cov.status != "SUPPORTED"]
print(f"\n{len(blocked)} of {len(cov)} requirements are not yet fully supported.")
p0 = blocked[blocked.evidence_file.str.contains("iap_products|support_capability", na=False)]
if len(p0):
    print("P0 blockers still open:")
    for _, r in p0.iterrows():
        print(f"  - {r.requirement}: {r.blocker}")
print("\nwrote data/04_gaps/rubric_coverage.csv")
