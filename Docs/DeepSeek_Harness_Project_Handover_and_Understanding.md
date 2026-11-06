# DeepSeek Harness — Project Handover and Understanding

**Author:** DeepSeek Harness (coding agent session)
**Date:** 2026-11-06, 11:20–12:25 PT
**Project:** COOP FA26 Data Analytics Capstone — Ivy Health AI, Product R&D Strategy
**Cohort / Pod:** C690 / Pod 2 ("IVY Apps and AI Health Assistant")
**Scope of this document:** what I understood about the project, what I changed, what I verified,
what I could not verify, and what should happen next.

> **How to read this.** Every factual claim carries a verification level:
> **VERIFIED** = I re-read the primary source myself in this session (raw HTML or PDF text).
> **COMPUTED** = derived from a local CSV/DB in this folder, reproducible with the scripts named.
> **REPORTED** = present in the folder but produced outside this session; not independently re-derived.
> **INFERRED** = a judgement, flagged as such.

---

## 1. What this project is

A simulated consulting engagement. The cohort works as one unnamed data consultancy; the client is
Ivy Health AI (consumer brand of String Health Inc., formerly Bellabeat). Ivy must pick **two of four**
product lines to fund for R&D in Q1 2027, and cannot share its own user data.

### 1.1 The forcing question

> If Ivy can fund only two of four product R&D initiatives next quarter, which two should it fund,
> and why those two over the other two?

No "all of them", no "it depends". Each pod owns one line; the cohort decides together on Night 5.

### 1.2 Structure and calendar

| Item | Value |
|---|---|
| Meetings | Capstone Introduction Night + **Nights 1–6** (seven total; there is no Night 7 or 8) |
| Pod 2's line | IVY Apps and AI Health Assistant — Period & Pregnancy Tracker, Wellness Coach, and the assistant that sits inside the Tracker |
| Framework | **DFV+**: Desirability, Feasibility, Viability, Strategic fit — each 1–4, equal weight, out of 16 |
| Positions | Build / Improve / Deprioritize / Reposition — one word per pod, with a revisit condition for the two not funded |
| Deliverables | Preliminary Discovery (Night 2, required), AI Disclosure Statement (required), Internal R&D Proposal deck (Night 6, graded), Product Investment Memo (graded, final before Night 6) |
| Scoring | 80 shared points (Accuracy, Utility, Communication, Presentation × 20) + 20 individual (self 10 + peer 10) |
| Deadline inference | Discovery is dated 2026-10-28 and is due end of Night 2, so Night 2 ≈ 10/28; if weekly, Nights 4–6 ≈ 11/11, 11/18, 11/25. **INFERRED** — confirm with the captain |

### 1.3 What actually gets graded

Reasoning, not the answer. The Brief says a pod that recommends Deprioritize or Reposition for its
own line, with a strong scorecard, can earn full marks. Accuracy is judged as *every score backed by
evidence, a source and a date, with one method across pods* — which is why the data gaps in §5 matter
more than the prose quality.

### 1.4 The tension built into Pod 2's question

The line is called "Apps **and** AI Health Assistant", so the assistant looks like the protagonist.
The evidence says otherwise: only 13 of 5,019 Tracker reviews mention AI (0.26%). **COMPUTED**
(`Evidence_Pack/data/01_corpus/keyword_evidence.csv`). The assistant is a retention and trust surface,
not an acquisition channel. Any recommendation that leans on "ship more AI" is arguing against the data.

---

## 2. The analytical position the pod has reached

**Improve** — rebuild the existing assistant on the user's own cycle history, fix data continuity and
trust first, then talk about intelligence. Scorecard draft: D3 / F4 / V3 / S4 = **14/16** (strong band).
Source: `Docs/Pod_2_Analysis_Framework_and_Growth_Levers.md`.

I think this position is well supported, with one caveat in §4.1 that could move Viability.

---

## 3. What I did in this session

### 3.1 Located the missing deck

The task began with "is the Introduction Slides file here?". It was not, at 11:22. It appeared at
11:24:29 and Spotlight (`mdfind`) surfaced it before `ls` did. **VERIFIED**: 42 pages, 720×405 pt
(16:9), covers industry, role, client, DFV+, roles, deliverables, timeline, grading.

### 3.2 Filled the two required working documents

| Output | What was empty | What I added |
|---|---|---|
| `Docs/Pod_2_TeamCharter_v1.docx` | Part 3 agreements (5 placeholders), competencies table (5 rows for 7 people), Part 4 standup (Night 1–6 blank), Part 5 Team Alignment (blank) | 5 pod agreements; 7-member competencies; Night 1–3 standup drafts; Part 5 four-question draft; title cleaned of "(Make a Copy)" |
| `Docs/Pod_2_AIDisclosureStatement_v1.docx` | Part 2 ratings, Part 3 tool links, Part 4 five agreements, Part 5 log gaps | 0–10 ratings with reasons; three tool links; five AI agreements; gap note for 11/3–11/6 |

Also split a real conflict: two members both held the title "Scorecard lead". I split it into
Desirability/Feasibility (Alyssa) and Viability/pricing (Derek).

Deliberately left blank: Pod lead confirmations (Fion's to tick), Part 6 final review (post-Night 6),
pod-rep names (unknown), captain sign-off (Sheila's).

### 3.3 Translated the two working notes into English

`Pod_2_Analysis_Framework_and_Growth_Levers.md` and `Pod_2_Data_Scope_Cleaning_and_Analysis_Plan.md`.
Heading counts (18/18, 34/34) and table rows (25/25, 66/66) match the originals; zero CJK characters
remain. Originals preserved at `Docs/_zh_source/`.

### 3.4 Built `Evidence_Pack/`

A folder that separates what is **computed from local data** from what must be **fetched and dated**:

- `scripts/01_build_local_analysis.py` — 9 tables recomputed from the local CSVs (corpus summary,
  rating distribution, keyword evidence, version timeline, monthly trend, sensitivity scenarios,
  reply rate by batch, country coverage, data-quality flags).
- `scripts/02_make_templates.py` — empty, status-tracked templates. **Nothing is prefilled.**
- `scripts/03_fetch_public_data.py` — fetches each registered source, saves raw, logs the outcome.
- `scripts/04_extract_facts.py` — extracts facts with the verbatim snippet and raw-file pointer.
- `scripts/05_check_coverage.py` — per-rubric-cell gate.

### 3.5 Audited the data and found six problems

Detailed in §6. Three of them change numbers that are already written into the Discovery.

---

## 4. The three findings that matter most

### 4.1 The two apps are two separate subscription products

| App | Store | SKUs shown | Ladder |
|---|---|---|---|
| Period & Pregnancy Tracker | iOS | Period Diary Premium / (1 Year) | $8.49/mo, $48.00/yr |
| Wellness Coach | iOS | Bellabeat+ / Bellabeat+ Yearly | $9.99/mo, $99.99/yr |
| Tracker | Play | range only | $8.49 – $47.99 per item |
| Coach | Play | range only | $7.99 – $119.99 per item |

**VERIFIED** against `Evidence_Pack/data/03_external/raw/iap_ios_tracker.html` and
`iap_ios_coach.html`.

Why it matters: the "same membership" connection point in the pod's notes is **false**. The two apps
are sold as different products (Period Diary Premium vs Bellabeat+), on different ladders. That
removes one of the three bridges the notes used to argue the apps belong together, and it means the
assistant cannot assume it will ever see Coach or device data. It also strengthens the case that
Improve must be scoped to *the Tracker's own cycle history*, not to cross-app data — cross-app data
depends on Pod 1's device sync plus a unified account, neither of which exists today.

### 4.2 "Restore" is undocumented, but cloud sync is mentioned in boilerplate

- Help-centre search for **`restore` → "No results"**. **VERIFIED** (`raw/ivy_support_search_restore.html`).
- The IVY+ Getting Started section lists **10 articles**, none about export, backup or restore. **VERIFIED**.
- But the iOS subscription description says the subscription lets you *"synchronize data between
  devices using cloud services and to use more features"*. **VERIFIED** (`raw/iap_ios_tracker.html`).

These pull in opposite directions. The boilerplate is Apple's standard subscription text and may
describe intended behaviour rather than a shipped feature, but it is enough to stop anyone saying
"restore is impossible". Correct phrasing for the Discovery: **"no restore or export path is
documented"**, and growth lever ① is *rebuild/import* unless a support answer proves otherwise.

### 4.3 The corpus every document quotes is the wrong number

| Figure | Meaning | Where it comes from |
|---|---|---|
| 6,726 | raw pull, before de-duplication | `ivy_all_historical_reviews_2011_2026.csv` |
| **6,226** | de-duplicated analysis base | `ivy_reviews_clean.csv`, `ivy_reviews.db` |
| 5,518 | teammate's xlsx | `Teammate_Data/` |

500 Coach/Apple rows were removed as cross-batch duplicates. Tracker (5,019) is untouched, so the
headline keyword counts survive; Coach (1,707 → 1,207) does not. **COMPUTED**.

---

## 5. Verification register

| Claim | Value | Level | Evidence |
|---|---|---|---|
| Tracker Play rating | 3.2, 9.88K reviews, 500,000+ installs | VERIFIED | `raw/iap_play_tracker.html` |
| Coach Play rating | 3.5, 3.8K reviews, 1,000,000+ installs | VERIFIED | `raw/iap_play_coach.html` |
| Both apps updated on Play | 2026-10-23 | VERIFIED | same |
| Tracker iOS | 4.7, 67,897 ratings, v7.7.5, updated 2026-11-05 | VERIFIED | `raw/iap_ios_tracker.html` |
| Coach iOS | 3.9, 409 ratings, v4.3.3, updated 2026-06-08 | VERIFIED | `raw/iap_ios_coach.html` |
| KFF trust: AI / provider / social | 25% / 86% / 15% | VERIFIED | `raw/kff_women_online_health.html` |
| FDA DEN170052 | Natural Cycles, 21 CFR 884.5370, "Software application for contraception", Class II, **August 10, 2018** | VERIFIED (PDF text) | `raw/fda_den170052.pdf` |
| KFF 42% used AI | 42% women | COMPUTED from `data-PmfG5.csv` | local file |
| Corpus 6,226; Coach 1,207 | — | COMPUTED | `ivy_reviews_clean.csv` |
| Sensitivity: Tracker primary 4.24 / 12-mo 3.31 / iOS 2.55 / no-burst 2.53 | — | COMPUTED | `sensitivity_scenarios.csv` |
| Competitor prices (Flo, Clue, Oura, Calm) | e.g. Flo $9.99/mo, Oura $5.99/mo | REPORTED | filled outside this session; not re-derived |
| Pew 21% tracker use | 2020 fieldwork | REPORTED | `raw/pew_trackers_2020.html` |

---

## 6. Known problems in the data (all reproducible)

| # | Problem | Impact | Fix |
|---|---|---|---|
| 1 | Corpus is 6,226, documents say 6,726 | every "of 6,726" sentence is wrong | restate as 6,226 and disclose the 500 removals |
| 2 | Primary sample is 49 reviews (Tracker 25, Coach 24) | "25 per app" claim is technically false | re-pull the missing Coach review, or state n=49 |
| 3 | Coach iOS reviews stop 2026-02-08 (270 days), app updated 2026-06-08 | Coach "recent sentiment" is not recent | re-scrape or disclose |
| 4 | Notes' 448 lost-data hits recompute to **426** with the listed terms (469 with a broader set) | an unreproducible number sits in the argument | record the exact regex, or change to 426 |
| 5 | All 49 sampled reviews are uncoded | the theme table cannot be built | code against a 7-theme taxonomy |
| 6 | De-duplication removed rows by text match, but the plan says "only by review_id" | method description contradicts the code | correct the plan text |
| 7 | Burst contamination: 55 reviews Jul–Aug 2026 | "25 most recent" reads 4.24 vs 2.55 iOS | already disclosed; keep it in the limits |

---

## 7. State of the folder

### 7.1 Authoritative files

| Deliverable | Use this | Not this |
|---|---|---|
| Team Charter | `Docs/Pod_2_TeamCharter_v1.docx` | `[Cohort C690] [Pod 2] Team Charter .docx` (template copy) |
| AI Disclosure | `Docs/Pod_2_AIDisclosureStatement_v1.docx` | `[Cohort  C690] [Pod 2] AI Disclosure Statement.docx` |
| Analysis framework | `Docs/Pod_2_Analysis_Framework_and_Growth_Levers.md` | `Docs/_zh_source/*.md` (Chinese originals, archive only) |
| Data scope and cleaning plan | `Docs/Pod_2_Data_Scope_Cleaning_and_Analysis_Plan.md` | same |
| Evidence | `Evidence_Pack/` | — |
| Submitted Discovery | `Docs/Pod2_Preliminary_Discovery.pdf` | — |

### 7.2 Two agents worked in this folder

Between 12:14 and 12:18, outside this session, another agent (Gemini / Antigravity) populated the
evidence templates that I had deliberately left empty: iOS listings, FDA record, competitor pricing,
Pew. It also initialised git, added a root `README.md`, and wrote
`Docs/Pod2_Gemini_Antigravity_Project_Overview_and_Strategic_Analysis.md`.

Consequences you should decide on:

1. **That document is in Chinese.** Every other deliverable is English, and the stated requirement is
   English. If it is for the captain, it needs translating; if it is internal, move it to `_zh_source/`.
2. **Two narratives now describe the same project** (mine, in English, and that one, in Chinese).
   They must not drift. Pick one as canonical before Night 6.
3. **The values it added are REPORTED, not re-derived by me**, except the iOS prices, iOS versions and
   the FDA record, which I re-checked against the raw files and the PDF.
4. `Evidence_Pack/README.md` still says "12 of 15 requirements not supported"; the coverage file now
   says 10 supported / 5 missing. **The README is stale** — regenerate it from `05_check_coverage.py`.

### 7.3 Remaining gaps (5)

| Cell | Missing | Why it matters |
|---|---|---|
| D | theme coding of the 49 sampled reviews | the theme table is the backbone of Desirability |
| D | 5–10 person habit survey | only qualitative source that is not Ivy's reviews |
| D | Reddit / forum quotes | second qualitative leg |
| D | Google Trends (5y, US) | interest trend; blocked (HTTP 429) |
| S | Ivy's own platform language, dated | Strategic fit currently cites the Brief, not the site (ivyhealth.ai unreachable) |

---

## 8. What I could not do

- **Google Drive.** The Project Folder structure, sharing and naming rules (`Pod_#_Deliverable_v#`) live
  there. I cannot create or move those; the local folder is now named consistently, but nothing was
  uploaded.
- **Render the DOCX files.** No LibreOffice on this machine, so table layout after adding rows was not
  visually checked. Open both in Word or Google Docs before submitting.
- **Some hosts stay unreachable**, with these recorded outcomes: `ivyhealth.ai` NETWORK_ERROR,
  Google Trends HTTP 429, Rock Health HTTP 403, Ivy support home HTTP 403.
- **Run the Night 3 peer review conversation.** Part 5 of the charter holds a draft written from
  observable evidence; the pod must actually hold the conversation and rewrite it.

---

## 9. Recommended next steps, in order

1. **Decide the corpus number** (6,226) and correct every document that says 6,726 — including the
   Discovery. This is the cheapest Accuracy win available.
2. **Fix the sample to 25+25** or disclose n=49. Same rubric cell.
3. **Code the 49 reviews** with one primary theme each; the theme table then exists.
4. **Resolve the restore question** with one support ticket or one look at the in-app settings, then
   rewrite lever ① as restore or rebuild accordingly.
5. **Rewrite the "same membership" bridge** in the notes now that two separate SKUs are confirmed.
6. **Re-run `05_check_coverage.py`** and regenerate `Evidence_Pack/README.md`; the stale gate text will
   otherwise contradict the data.
7. **Translate or archive the Chinese Gemini report**, then pick one canonical narrative.
8. **Delete or archive the two bracket-named template copies** in `Docs/` so nobody submits the wrong file.

---

## Appendix A — File map

```
Capstone_Project/
├── README.md                     repo overview (added outside this session)
├── requirements.txt, .gitignore  (added outside this session)
├── Docs/
│   ├── FA26 ... Brief.pdf                    17 pp, rules and rubric
│   ├── FA26 ... Introduction Slides.pdf      42 pp, 16:9, the deck that was missing
│   ├── Pod2_Preliminary_Discovery.pdf        the Night 2 deliverable, already submitted
│   ├── Pod_2_TeamCharter_v1.docx             filled by me
│   ├── Pod_2_AIDisclosureStatement_v1.docx   filled by me
│   ├── Pod_2_Analysis_Framework_and_Growth_Levers.md      EN, translated by me
│   ├── Pod_2_Data_Scope_Cleaning_and_Analysis_Plan.md     EN, translated by me
│   ├── Pod2_Gemini_Antigravity_...md         Chinese report, other agent
│   ├── Analysis Command & Result.md          SQLite session transcript
│   └── _zh_source/                           Chinese originals (archive)
├── Evidence_Pack/                             see its own README
├── Teammate_Data/                             teammate pulls (xlsx + csv)
├── ivy_reviews_clean.csv / .db                6,226 rows, the analysis base
├── ivy_all_historical_reviews_2011_2026.csv   6,726 rows, raw
├── pod2_25_recent_sample.csv                  49 rows, uncoded
├── dedupe_report.csv                          500 removed rows
├── data-PmfG5.csv                             KFF table (42% use)
└── *.py                                       pipeline scripts (scrape, clean, db, validate)
```

## Appendix B — Reproducing the evidence pack

```bash
cd Evidence_Pack/scripts
python3 01_build_local_analysis.py      # offline
python3 02_make_templates.py            # offline — RESETS all templates to NOT_COLLECTED
python3 03_fetch_public_data.py --live  # network; merges into 00_status/fetch_log.csv
python3 04_extract_facts.py             # offline; reads raw/
python3 05_check_coverage.py            # offline; the gate
```

Note: step 2 wipes filled values, including anything the other agent added. Run it only when
rebuilding from scratch.

## Appendix C — Where the two narratives could contradict each other

| Topic | My reading | Watch for |
|---|---|---|
| Corpus size | 6,226 | any document still saying 6,726 |
| Membership | two separate products, different SKUs | "one shared membership" claims |
| Restore | undocumented; boilerplate hints at cloud sync | "restore is impossible" claims |
| AI demand | 0.26% mention rate, treat as weak signal not zero demand | "users do not want AI" |
| Position | Improve, scoped to the Tracker's own data | "Improve by connecting the two apps" (needs Pod 1) |
