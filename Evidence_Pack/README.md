# Evidence Pack — Pod 2 (Cohort C690)

Built 2026-11-06. Everything here is either **computed from a file that already existed in
the capstone folder** or **captured from a live page on 2026-11-06 and saved verbatim**
under `data/03_external/raw/`. Nothing is estimated, interpolated or filled in as a guess.
A cell that could not be obtained stays empty and its row says `NOT_COLLECTED`.

## Why this folder exists

The pod's notes hold strong review evidence and almost nothing on price, regulation or
product capability. The rubric scores Accuracy on "every score backed by evidence, a
source and a date", so the missing cells had to be made visible rather than described
in prose. This pack does three things:

1. recomputes every analysis the notes claim, into tables a reviewer can check;
2. records, per source, what was actually fetched and what was not;
3. states, per rubric cell, whether it is supported yet.

## Layout

```
Evidence_Pack/
├── README.md
├── scripts/
│   ├── config_sources.py          source registry: URL, rubric cell, what to capture
│   ├── 01_build_local_analysis.py computes tables from the local CSVs (no network)
│   ├── 02_make_templates.py       creates empty, status-tracked templates
│   ├── 03_fetch_public_data.py    fetches sources, logs the outcome, saves raw
│   ├── 04_extract_facts.py        extracts facts + verbatim snippet from raw
│   └── 05_check_coverage.py       per-cell coverage report and blockers
└── data/
    ├── 00_status/                 fetch_log.csv, fetch_summary.json
    ├── 01_corpus/                 tables computed from local review data
    ├── 02_store/                  store baselines, re-check, release notes, support gaps
    ├── 03_external/               price/survey/trends/regulatory templates + raw pages
    └── 04_gaps/                   rubric_coverage.csv
```

## Run order

```bash
cd Evidence_Pack/scripts
python3 01_build_local_analysis.py     # offline, recomputes from ../../
python3 02_make_templates.py           # offline, wipes the templates back to NOT_COLLECTED
python3 03_fetch_public_data.py --live # needs network; writes 00_status/fetch_log.csv
python3 04_extract_facts.py            # offline, reads 03_external/raw/
python3 05_check_coverage.py           # offline, prints the gate
```

`03_fetch_public_data.py` uses urllib, not curl. On this machine curl is reset by the
sandbox but urllib reaches some hosts, so run it and read the log rather than assuming.

## What is real (checked against the page on 2026-11-06)

| Fact | Value | Source |
|---|---|---|
| Tracker in-app purchase range on Play | `$8.49 - $47.99 per item` | raw/iap_play_tracker.html |
| Coach in-app purchase range on Play | `$7.99 - $119.99 per item` | raw/iap_play_coach.html |
| Tracker Play rating | 3.2 star, 9.88K reviews, 500,000+ installs | raw/iap_play_tracker.html |
| Coach Play rating | 3.5 star, 3.8K reviews, 1,000,000+ installs | raw/iap_play_coach.html |
| Both apps' last Play update | 2026-10-23 | raw/ (tag-stripped text) |
| KFF: trust in AI tools for health information | 25% of reproductive-age women | raw/kff_women_online_health.html |
| KFF: trust in health care providers | 86% | raw/kff_women_online_health.html |
| KFF: trust in social media | 15% | raw/kff_women_online_health.html |
| Ivy help centre search "restore" | `No results for "restore"` | raw/ivy_support_search_restore.html |
| Ivy IVY+ Getting Started section | 10 articles, none on export, backup or restore | raw/ivy_support_section_gs.html |

Every one of these is stored in `data/03_external/extracted_facts.csv` with the verbatim
snippet, the raw file name and the date checked.

## Two findings that can change the recommendation

1. **The two apps do not share a price ladder.** Tracker runs to $47.99 and Coach to
   $119.99. That points to two separate subscription products rather than one shared
   membership, which weakens the "same membership" connection point in the notes. It is
   still unconfirmed: ranges are not SKU lists.
2. **No documented way to restore history.** The help centre returns nothing for
   "restore" and lists no article on export or backup. Growth lever 1 (data continuity)
   may therefore be *rebuild/import*, not *restore*. Absence of documentation is not proof
   of absence, so the row is marked `PARTIAL` and the Discovery must phrase it as "not
   documented" rather than "impossible".

## What is still empty, and why

| Template | Rows empty | Reason |
|---|---|---|
| `iap_products.csv` | SKU names, periods, trials, iOS rows | listing pages show a range only; iOS listings unreachable |
| `competitor_pricing.csv` | 8 | flo.health, helloclue.com, ouraring.com unreachable |
| `google_trends.csv` | 3 | trends.google.com unreachable |
| `regulatory_records.csv` | 2 | FDA and FTC hosts unreachable; the Brief names both records |
| `survey_responses.csv` | 1 | no respondents yet; habit-only questions |
| `reddit_quotes.csv` | 5 | no quotes captured |
| `kff_metrics.csv` | sample size and method | not on the page section captured |

## Problems found in the existing data

| # | Problem | Evidence |
|---|---|---|
| 1 | Corpus is 6,226 rows, not the 6,726 quoted in the notes | `ivy_reviews_clean.csv`; 500 Coach/Apple duplicates removed |
| 2 | Primary sample is 49 reviews, not 50 | `pod2_25_recent_sample.csv`: Tracker 25, Coach 24 |
| 3 | Coach iOS stops at 2026-02-08, 270 days stale | `data_quality_flags.csv` |
| 4 | The notes' 448 lost-data hits recompute to 426 | `keyword_evidence.csv` carries the regex used |
| 5 | 49 of 49 sampled reviews are uncoded | `data_quality_flags.csv` |
| 6 | Dedupe used text matching, not review_id as the plan states | `dedupe_report.csv` |

## Gate

Run `05_check_coverage.py` for the current state; the numbers below move as rows get filled, so
treat the script output as authoritative, not this paragraph.

At the last run: **10 of 15 requirements supported, 5 missing** — theme coding of the 49 sampled
reviews, the habit survey, forum quotes, Google Trends, and Ivy's own platform language (dated).
None of those five is a P0 blocker any more; they are the remaining gaps in Desirability and
Strategic fit.
