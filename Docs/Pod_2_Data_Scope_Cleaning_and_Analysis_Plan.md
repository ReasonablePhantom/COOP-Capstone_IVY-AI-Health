# Pod 2 data scope, definitions, and the cleaning and analysis plan

- Version: 2026-11-06
- Basis: FA26 Data Analytics Capstone Brief (October 2026), sections 9-11
- Existing assets: `ivy_all_historical_reviews_2011_2026.csv` (6,726 reviews), `ivy_store_baselines.csv` (2026-10-28), `ivy_app_reviews_tagged.csv` (1,500 reviews), `ivy_pod2_25_reviews_tagged.csv` (50 reviews)

---

## 0. One-sentence definition, ready to paste into the Discovery header

> **Store baseline: pulled 2026-10-28, re-checked 2026-11-06. Primary review sample: 2025-11-06 to 2026-11-06, the 25 most recent reviews per app, 50 in total. Historical corpus: 2011-06-04 to 2026-10-17, 6,726 reviews, used only as background and for cross-checking, never to infer population proportions.**

Why the primary sample and the historical corpus must be stated separately: the Brief's review rule is **25 reviews per app from the last 12 months**. The 6,726 reviews are a convenience sample, not a random one, so they cannot be used to say "X% of users". Mixing the two is the easiest way to lose Accuracy points.

---

## 1. The six date rules the Brief sets

| Data type | Brief rule | How Pod 2 applies it |
|---|---|---|
| Store ratings and prices | As of the date checked | 2026-10-28 baseline plus a 2026-11-06 re-check; both dates are written down |
| App reviews | The 25 most recent per app from the last 12 months | 2 apps x 25 = 50; taken per app, not per store |
| Google Trends | Past five years, United States | 2021-11 to 2026-11, US only |
| Surveys and market reports | Latest edition, with its year | KFF 2026-09, Rock Health 2025, Pew 2020, Grand View 2026 |
| Open datasets | Any year, stated in the proxy statement | Fitbit/Kaggle and similar, as long as "collected in year X" is stated |
| Our own small survey | 5-10 people, habits only | Report counts ("6 of 8"), not percentages, and never touch health details |

**Additional hard rules (section 11):**

- Every research question gets at least **one quantitative and one qualitative** source.
- Every number carries its date or period.
- Every source gets one sentence pair on why we trust it and what its limit is.
- Any finding from data that is not Ivy's carries a **three-line proxy statement**: what the source is, why it stands in, and where it stops being reliable.

---

## 2. Data scope map: what we have and what is missing

### A. First-party store facts, all of which must exist and be re-checked

| What to get | What we have | Gap | Used for |
|---|---|---|---|
| Ratings, rating counts and installs, 2 apps x 2 stores | Yes (2026-10-28) | Needs the 2026-11-06 re-check; installs are only public on Play | Desirability / Viability |
| In-app purchase lists and prices (monthly/yearly/trial) | **None** | The largest gap: is this one membership or two subscriptions? | Viability |
| Latest update date, version number, What's New | Only version numbers quoted inside reviews | Needs the store release notes, to date the January 2026 redesign | Feasibility / event attribution |
| Developer reply rate to bad reviews | Yes (Tracker 9.5%, Coach 27.8%) | Covers only the "Our Scrape" batch; the teammate batch is entirely empty | Supporting evidence for Desirability |

### B. First-party reviews

| Layer | What we have | Used for | Limit |
|---|---|---|---|
| Primary sample, 25 x 2 | Already generated as `pod2_25_recent_sample.csv` | The main evidence for Desirability | n=25, cannot be generalized |
| 12-month corpus | 93 Tracker, 25 Coach | Sensitivity analysis | Still not random |
| Full 6,726 | Yes | Event study, theme trends | Convenience sample; spans 15 years and the product has changed |

### C. Competitors (the Brief names Flo, Oura and Calm)

| What to get | Why | Now |
|---|---|---|
| Flo's membership price and what Flo Health Assistant can do | AI Q&A is already standard for competitors, which shows that "having a chat" is not differentiation | **Missing**, needs checking with the date recorded |
| Clue and Oura membership and AI features | Pricing anchor and feature boundary | **Missing** |
| Whether competitors serve perimenopause | Decides whether growth lever ② is a real gap | **Missing** |

### D. Macro and industry data (all proxy, each needs the three-line statement)

| Source | What to take | Which cell it fills |
|---|---|---|
| KFF (2026-09) | 42% have used AI, 25% trust it (against 86% for doctors) | "Demand exists but trust is low" for Desirability |
| Rock Health 2025 | Wearable and smart-ring ownership | Feasibility of lever ④ |
| Pew 2020 | Tracker use by gender | Same, noting the 2020 data |
| Grand View 2026 | Femtech market size (cite one edition only) | Background, never a score |
| Business of Apps | Subscription conversion benchmarks for health apps | Scenario math for Viability |

### E. Regulation, which sets the ceiling on Feasibility

- **FDA De Novo DEN170052 (Natural Cycles):** shows that making a medical claim from body data requires years of clinical work and clearance, so the assistant must stay on wellness.
- **The FTC action against Flo (2021):** privacy is the compliance floor for this product line and also growth lever ⑤.

### F. Our own collection, which the Brief explicitly allows and which closes the qualitative gap

- A 5-10 person survey asking only "what do you do when the prediction is wrong" and "what would you pay for", reported as counts.
- Reddit: r/menopause, r/Perimenopause, r/xxfitness, quoting short phrases only and never usernames.
- **Note:** neither group is made of Ivy users, so both need a proxy statement.

### G. Ivy's own statements, used to judge Strategic fit and never to prove usage behavior

- The ivyhealth.ai home page, the AI Health Assistant page, shop, support, journal and bellabeat.com.
- These prove only what the company says it is becoming, not what users actually do.

### Deliberately not used (excluded by the Brief or unsound methodologically)

- ❌ The conclusions of the Bellabeat case study in the Google Data Analytics Certificate (the Brief forbids it).
- ❌ Reviews of legacy hardware such as Leaf, Spring and Time, treated as evidence about the current IVY+.
- ❌ Play installs treated as active users (MAU).
- ❌ "AI-first" on a marketing page treated as a capability the product already has.
- ❌ Numbers from different editions of the same market report mixed together.

---

## 3. The eight kinds of missing data, by priority

| P | What to add | Which score it fills | How to get it | Time |
|---|---|---|---|---|
| **P0** | In-app purchase lists for both apps: SKUs, prices, trials, whether it is one subscription | Viability | The App Store and Play product pages, screenshot plus date | 1 hour |
| **P0** | New Coach reviews (the iOS data stops at 2026-02-08; only 3 iOS reviews in the last 12 months) | Desirability | Re-scrape the Apple RSS and Play, recording the pull date | 1 hour |
| **P0** | The 2026-11-06 re-check of ratings and rating counts on all four store listings | Accuracy | Store pages | 20 minutes |
| **P0** | The version and update-date timeline, especially the forced update in January 2026 | Feasibility / event attribution | Store What's New plus version numbers quoted in reviews | 1 hour |
| P1 | Flo, Clue and Oura membership prices and AI features | Viability / Strategic | Official sites and store pages, with dates | 2 hours |
| P1 | Google Trends: period tracker, perimenopause, AI health assistant (5 years, US) | Background for Desirability | trends.google.com | 30 minutes |
| P1 | The two KFF 2026-09 figures and the sampling note, from the report itself | Desirability | The KFF report page | 30 minutes |
| P2 | Reddit phrases plus a 5-10 person survey | Qualitative triangulation | By hand | 2 hours |

> The test: **if a piece of data cannot change any of the four scores, do not spend time on it.** All four P0 items either move a score directly or rescue Accuracy.

---

## 4. The eleven cleaning problems in the existing data

### 4.1 Mixed date formats, and 500 rows silently becoming NaT

- **Symptom:** in `ivy_app_reviews_tagged.csv` the Apple dates look like `2026-01-01T07:28:12-07:00` and the Google dates look like `2026-09-05 16:10:53`.
- **Evidence:** `pd.to_datetime(..., utc=True)` returns NaT for all 500 of those rows; switching to `format="mixed"` gives zero failures.
- **Fix:** standardize on `pd.to_datetime(..., format="mixed", utc=True)` and assert `isna().sum() == 0`.
- **Impact:** unfixed, "the Coach iOS has no reviews in the last 12 months" is read as "there is no data", when in fact the parse failed.

### 4.2 De-duplicate on ID, not on text

- **Evidence:** 743 reviews have identical text, but in 527 of the 583 groups the reviews come from the same country on different dates, meaning different users each wrote "Good" or "Great app".
- **Fix:** de-duplicate only on `(app_name, store, review_id)`. Add a separate `cross_country_dup` flag (same text, same date, different country) for manual review; this run produced zero.
- **Impact:** de-duplicating on text deletes genuine short reviews and hurts the Coach's sample size in particular.

### 4.3 The sampling frame is wrong

- **Symptom:** `ivy_app_reviews_tagged.csv` is 500 reviews per store spanning 2015-2026, not the Brief's 25 most recent from the last 12 months.
- **Evidence:** only 69 of the 1,500 fall inside the last 12 months.
- **Fix:** use `pod2_25_recent_sample.csv` as the primary sample; demote the 1,500 to "historical background" and say so in the limits.

### 4.4 Theme labels break the one-theme-per-review rule

- **Evidence:** of the 1,500, **400 have no label and 473 have more than one** (up to five).
- **Fix:** replace with `primary_theme` (exactly one) plus `secondary_tags` (not counted); rows with no label go back to the source text for manual tagging.
- **Impact:** multiple labels make theme shares add up to more than 100%, and the Senior Manager will see the method is not clean.

### 4.5 The taxonomy is a junk drawer

- **Evidence:** in `ivy_pod2_macro_theme_summary.csv`, "UI/UX & General Satisfaction" is 63% for both apps. That category carries no decision value.
- **Fix:** replace it with themes that map to the scorecard, seven categories suggested:
  1. Data loss / accounts / redesign
  2. Prediction accuracy, including irregular cycles
  3. Paywall / pricing / refunds
  4. Device sync / hardware
  5. AI assistant (availability, cost, privacy)
  6. Pregnancy / postpartum mode
  7. Other, including pure praise
- **Impact:** a theme must answer "where do users lose value"; it cannot be a mood category.

### 4.6 Language bias

- **Evidence:** 243 reviews (3.6%) contain non-ASCII text (Spanish, Italian, French, German, Portuguese).
- **Fix:** English keyword search misses them; read 30 of the non-English reviews by hand and tag them, or use multilingual keywords with manual review.
- **Impact:** complaints about lost data and paywalls exist in multilingual markets too, so searching English only underestimates them.

### 4.7 Mixing before and after the redesign

- **Evidence:** reviews from 2011 to 2025 belong to Bellabeat Period Diary and only 2026 onward is IVY; January 2026 averages **1.38** with **0%** five-star.
- **Fix:** add `period = bellabeat_legacy / ivy_rebrand`, split at 2026-01-01 as an approximation, and draw every trend chart as two lines.
- **Impact:** without the split, the good reviews from ten years ago average together with the bad reviews after the redesign into a meaningless number.

### 4.8 Five-star burst contamination

- **Evidence:** 55 reviews across July and August 2026; the Tracker's 25 July reviews average 4.20 with 80% five-star, the Coach's 15 are all five-star, the wording is highly templated, and they span five countries.
- **Fix:** add an `is_burst` flag and produce every key conclusion twice, with and without the burst.
- **Impact:** the Tracker's 21 Play reviews in `pod2_25_recent_sample.csv` land exactly in this burst and average 4.67, while the 4 iOS reviews from the same period average only 2.00. Failing to disclose this looks like cherry-picking.

### 4.9 The reply-rate denominator is biased

- **Evidence:** `developer_reply` is **empty for every row** in the teammate batch (5,226 reviews) and non-empty for 954 rows in the "Our Scrape" batch (1,500 reviews).
- **Fix:** compute the reply rate within the "Our Scrape" batch only, or mark empty values as "unknown" rather than "no reply".
- **Impact:** the 9.5% and 27.8% currently reported mix two sources in the denominator, and the conclusion will be challenged.

### 4.10 Store and country mixed

- **Evidence:** the corpus covers 12 countries (2,500 reviews from the US) while the store baseline is US.
- **Fix:** either compare against the store using the US subset only, or state in the conclusion that this is global reviews against a US store.
- **Impact:** using global sentiment to explain a US store rating of 4.66 is a definition mismatch.

### 4.11 Uneven freshness

- **Evidence:** the Tracker iOS runs to 2026-10-17 and Play to 2026-09-05; the Coach iOS stops at **2026-02-08** and Play runs to 2026-09-06.
- **Fix:** re-scrape the Coach; if that fails, write in the limits that the Coach iOS has had no public reviews for about eight months and that Desirability rests mainly on Play.
- **Impact:** the two apps have different review windows, so their recent sentiment cannot be compared side by side.

---

## 5. Analysis strategy: six moves

### Move 1: unit and counts, the quantitative base table

- Unit: one review; one `primary_theme`.
- For every theme report four numbers: **count, share, average rating, share of 1-2 star**, with the window and the store named.
- Cross-tabs: `theme x period`, `theme x store`, `theme x app`.
- Rule: for themes with n<30 report the count and a typical quote only, never a share.

### Move 2: event study, turning "the redesign" into a verifiable point in time

Use `pod2_monthly_trend.csv` for the monthly average rating:

| Period | Tracker monthly average | How to read it |
|---|---|---|
| All of 2025 | 2.1-2.8 | Already low before the redesign |
| 2026-01 | **1.38**, 0% five-star | A forced update plus lost data, concentrated |
| 2026-03 to 05 | 3.1-3.5 | A rebound after some fixes |
| 2026-07 to 08 | 4.2-4.6, 80% five-star | The burst, flagged separately |
| 2026-09 to 10 | 3.3 to 1.0 | Tiny samples, no conclusion |

Wording rule: say only that the timing coincides, never that it proves causation.

### Move 3: three sensitivity analyses, written into the limits, which buys Accuracy directly

1. **With and without the burst:** the Tracker's 12-month average is **3.31**; removing the July-August burst gives **2.53** (53 reviews).
2. **The 25-review primary sample against the 12-month corpus:** the primary sample gives the Tracker **4.24** against **3.31** for the 12-month corpus and **2.55** for iOS alone; the primary sample without the burst gives **2.40**. Put all three on one page so the reader sees how fragile "the 25 most recent" is.
3. **iOS against Play, separately:** the same app tells two stories on two stores (Tracker iOS 2.55 and Play 4.09; Coach iOS 1.33 on n=3, which cannot carry a conclusion, and Play 4.14).

### Move 4: Viability as scenarios, never a point estimate

- Use Play installs (500k+ and 1M+) as the denominator and **state that installs are not active users**.
- Take the Business of Apps range for conversion and show low, middle and high: "at 2-5% conversion, that is 10,000-25,000 paying users".
- Never write an unsourced point estimate such as "we will convert 10%".
- Use $47.99/year (2026-10-28) as ARPU and note that it is a discounted price.

### Move 5: an auditable qualitative coding process

1. Read the 25 reviews first and run open coding to produce the seven-category taxonomy plus decision rules.
2. Two pod members code the same 25 reviews independently, compute agreement, and settle every disagreement on the spot by writing it into the rules.
3. Re-scan the 12-month corpus with the taxonomy and manually review a 10% sample.
4. Build a quote bank: every quote carries its date, store, star rating and theme so the deck can cite it directly.
5. Log every part where AI was involved, including this plan, in AI Disclosure Part 5.

### Move 6: the triangulation matrix, two sources for every score

| Score | Quantitative source | Qualitative source | Proxy statement |
|---|---|---|---|
| Desirability | Star distribution of the 25 reviews plus theme counts | Review text plus Reddit phrases | Reviewers are not all users |
| Feasibility | Version timeline plus the FDA route | Ivy support pages and PubMed | A regulatory case is not Ivy's product |
| Viability | Prices, installs and industry conversion benchmarks | Paywall reviews in their own words | An industry benchmark is not Ivy's actual figure |
| Strategic fit | Counts of data types (cycle, device, behavior) | Ivy's own website language | Marketing intent is not usage behavior |

---

## 6. How to order the five observations in the Discovery

| # | Observation | Evidence | How to write the trust level |
|---|---|---|---|
| 1 | The stores are asymmetric: iOS is the Tracker's asset, the Coach is "installed but not used" | iOS 4.66 / 67,901; Play 3.2 / 9,875; Coach 1M+ Play installs but 3.46 | Strong; installs are not active users |
| 2 | The January 2026 redesign caused concentrated data loss | 448 lost/deleted (8.9%, average 1.61); January average 1.38 | Strong; reviewers self-select |
| 3 | The paywall is the second largest self-inflicted harm | 88 reviews (1.8%, average 1.83, 76% at 1-2 star) | Strong; small n but the direction is consistent |
| 4 | AI demand is thin and the assistant is often broken or blocked | 13 of 5,019 mention AI; "try again later", "4 questions free" | Medium; a low mention rate does not mean low demand |
| 5 | Perimenopause is a clear gap | 60 reviews (1.2%); "after I became irregular the prediction stopped moving" | Medium; small sample but cross-checkable |

Write every one in the four-part format (Where we looked / What we noticed / Why it matters / How much we trust it) and push the burst and n=25 limits into the fourth part.

---

## 7. One-page checklist

**Data scope**

- [ ] Re-check all four store listings on 2026-11-06 and put the date in the header
- [ ] Keep the 50-review primary sample and the 6,726-review background corpus stated separately
- [ ] At least one quantitative and one qualitative source per research question
- [ ] A three-line proxy statement for every non-Ivy source
- [ ] No old Bellabeat case study, no legacy hardware conclusions, no installs treated as MAU

**Cleaning**

- [ ] Dates parsed with `format="mixed"`, zero NaT
- [ ] De-duplicate on review_id only
- [ ] Four flags: `period`, `is_burst`, `lang_guess`, `device_mention`
- [ ] Exactly one `primary_theme`, with zero-label rows filled
- [ ] Reply rate computed within the "Our Scrape" batch only
- [ ] Coach re-scraped, or the window difference stated

**Analysis**

- [ ] All three sensitivity analyses run
- [ ] The theme table reports counts, not only percentages, especially when n<30
- [ ] Viability uses a range, never a point estimate
- [ ] The event study claims coincidence in time, never causation
- [ ] AI use logged in Disclosure Part 5

---

### Appendix: the three files generated this round

| File | Contents | Used for |
|---|---|---|
| `ivy_reviews_clean.csv` | 6,726 reviews plus five derived flags | The base table for all analysis |
| `pod2_25_recent_sample.csv` | The 50-review primary sample with the theme column empty | The starting point for manual coding |
| `pod2_monthly_trend.csv` | Monthly average rating, five-star share, 1-2 star share | The event study chart |

Script: `clean_pod2_reviews.py`, rerunnable, with the dates set as constants at the top.
