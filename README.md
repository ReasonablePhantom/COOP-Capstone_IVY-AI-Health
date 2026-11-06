# COOP Capstone Project — IVY AI Health: Product R&D Strategy

Cohort C690 | Pod 2 | Fall 2026

## Project Overview

This repository contains the end-to-end data pipeline, analytical models, SQLite database, and strategy documentation for the **COOP FA26 Data Analytics Capstone Project (Pod 2: IVY AI Health Assistant)**.

The project evaluates user feedback, sentiment drivers, and feature demands across IVY's flagship applications:
1. **IVY Period & Pregnancy Tracker**
2. **IVY Wellness Coach**

The core objective is to formulate a data-backed **Product R&D Strategy (Build / Improve / Deprioritize / Reposition)** to maximize daily active usage and user retention through an integrated AI Health Assistant.

---

## Directory Structure

```text
├── Docs/                                    # Capstone documentation, presentations & project charters
│   ├── Pod2_Gemini_Antigravity_Project_Overview_and_Strategic_Analysis.md # Comprehensive project review & strategic analysis (Gemini/Antigravity)
│   ├── Pod_2_Analysis_Framework_and_Growth_Levers.md   # Strategic analysis framework & growth opportunities (EN)
│   ├── Pod_2_Data_Scope_Cleaning_and_Analysis_Plan.md  # Data scope, cleaning rules, and methodology (EN)
│   ├── Analysis Command & Result.md                    # SQLite query executions & outputs
│   ├── Pod2_Preliminary_Discovery.pdf                  # Preliminary research discovery presentation
│   ├── Pod_2_TeamCharter_v1.docx                       # Team Charter and project timeline
│   ├── Pod_2_AIDisclosureStatement_v1.docx             # AI Disclosure and compliance statement
│   └── _zh_source/                                     # Chinese source documentation
│       ├── Pod2_分析框架与增长点.md
│       └── Pod2_数据范围_清理_分析方案.md
├── Evidence_Pack/                           # Multi-source quantitative & qualitative evidence audit pack
│   ├── README.md                            # Methodology, source registry & run sequence
│   ├── data/                                # Status, corpus metrics, store facts & external sources
│   └── scripts/                             # Pipelines to compute tables, fetch data & verify rubric coverage
├── Teammate_Data/                           # Raw input files and teammate contributions
│   ├── ivy_pregnancy_tracker_review.xlsx
│   ├── ivy_wellness_coach_reviews.xlsx
│   ├── teammate_coach_reviews.csv
│   └── teammate_pregnancy_reviews.csv
├── data-PmfG5.csv                           # Supplementary data
├── dedupe_report.csv                        # Deduplication audit report
├── ivy_all_historical_reviews_2011_2026.csv # Full historical review dataset (2011–2026)
├── ivy_all_historical_reviews_v2.csv        # Cleaned and reconciled historical reviews
├── ivy_app_reviews_tagged.csv               # Sentiment and theme-tagged reviews
├── ivy_pod2_25_reviews_tagged.csv           # Pod 2 sample (25 reviews per app)
├── ivy_pod2_25_theme_summary.csv            # Theme aggregation summary
├── ivy_pod2_macro_theme_summary.csv         # Macro-level thematic analysis
├── ivy_pod2_theme_summary.csv               # Summary of core themes
├── ivy_reviews.db                           # SQLite analytical database
├── ivy_reviews_clean.csv                    # Final cleaned reviews dataset
├── ivy_store_baselines.csv                  # App Store & Google Play metadata baselines
├── pod2_25_recent_sample.csv                # Extracted 12-month sample dataset
├── pod2_monthly_trend.csv                   # Longitudinal rating trends
├── queries.sql                              # Core SQL queries for reporting & cohort metrics
├── analyze_ivy_reviews.py                   # Exploratory analysis script
├── build_all_historical_reviews_v2.py       # Review dataset merger & schema standardizer
├── build_sqlite_db.py                       # SQLite database builder
├── clean_pod2_reviews.py                    # Data cleaning pipeline
├── compare_macro.py                         # Macro vs. sample comparison
├── compare_teammate.py                      # Teammate data reconciliation
├── convert_teammate_data.py                 # File conversion utilities
├── fill_night3_docs.py                      # Automated docx report populator
├── scrape_full_history_live.py              # App Store review scraper
├── scrape_ivy_reviews.py                    # App review collection pipeline
├── tag_25_reviews.py                        # NLP thematic tagger
└── validate_pipeline.py                     # Data pipeline validation and integrity checks
```

---

## Data Pipeline & Quickstart

### 1. Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # or install pandas, numpy, openpyxl, python-docx
```

### 2. Build the SQLite Database
To generate or update `ivy_reviews.db`:
```bash
python build_sqlite_db.py
```

### 3. Run Analysis Queries
Open `ivy_reviews.db` with [DB Browser for SQLite](https://sqlitebrowser.org/) or run queries directly via CLI:
```bash
sqlite3 ivy_reviews.db < queries.sql
```

### 4. Validate Pipeline
To verify deduplication rules, timestamps, and data constraints:
```bash
python validate_pipeline.py
```

---

## Key Methodologies & Compliance

- **Primary Sample**: Recent 25 reviews per app across the past 12 months (50 total reviews) strictly adhering to Capstone Brief Section 9–11 specifications.
- **Historical Corpus**: 6,700+ reviews (2011–2026) utilized for long-term longitudinal context, trend validation, and feature migration analysis.
- **Verification Baseline**: Captured on 2026-10-28 and re-verified on 2026-11-06.
