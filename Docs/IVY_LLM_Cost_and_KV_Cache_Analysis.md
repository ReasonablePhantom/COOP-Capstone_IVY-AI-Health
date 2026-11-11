# IVY Period & Pregnancy Tracker — Assistant Operating-Cost Estimate (Engineering Model)

> **What this document is.** An engineering estimate of what it would cost to run a conversational
> assistant inside the Period Tracker, built to answer one Feasibility question: *is compute cost a
> reason not to fund the assistant?*
>
> **What this document is not.** It is not evidence that the assistant attracts users or raises
> retention. Cost is a supply-side number; retention is demand-side. The retention argument lives in
> `Pod_2_Analysis_Framework_and_Growth_Levers.md` §9.
>
> **Data status.** Model prices are real and were fetched 2026-11-06 from the LiteLLM pricing
> repository. The multi-turn session telemetry is **simulated** (§4). Token volumes, cache hit rates
> and the resulting costs are therefore a *modelled magnitude*, not a measurement of Ivy's traffic.

---

## 1. Verified inputs

| Input | Value | Status |
|---|---|---|
| Model prices | 8 models, input / cached-read / output per 1M tokens | **Verified** — fetched from `raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json`, saved as `data/pricing/model_prices_raw.json` (5,868 model entries) |
| Price extraction | `data/pricing/dim_model_pricing.csv` | **Verified** — every one of the 8 models matched a row in the raw JSON; 0 unpriced rows in the cost run |
| Tracker subscription price | $8.49/month; $48.00/year (Period Diary Premium) | **Verified** — iOS listing, `Evidence_Pack/data/03_external/raw/iap_ios_tracker.html` |
| Coach subscription price | $9.99/month; $99.99/year (Bellabeat+) | **Verified** — same pack |
| Session telemetry | 2,547 requests, 800 sessions, 345 distinct user ids, 2026-10-01 to 2026-10-31 | **Simulated** (§4), numbers here are recomputed from the generated file |

### Price table used in the model

| Model | Tier | Input $/1M | Cached read $/1M | Output $/1M |
|---|---|---|---|---|
| gemini-2.0-flash | budget | 0.15 | 0.0375 | 0.60 |
| gpt-4o-mini | budget | 0.165 | 0.083 | 0.66 |
| deepseek-chat | budget | 0.28 | 0.028 | 0.42 |
| claude-3-5-haiku | budget | 0.80 | 0.08 | 4.00 |
| meta-llama/llama-3.3-70b | open weights | 0.135 | 0.027 | 0.40 |
| gpt-4o | frontier | 2.75 | 1.375 | 11.00 |
| claude-3-5-sonnet | frontier | 3.00 | 0.30 | 15.00 |
| deepseek-reasoner | reasoning | 0.28 | 0.028 | 0.42 |

---

## 2. The question this answers

The pod's recommendation is **Improve**: rebuild the existing assistant on the user's own cycle
history. The objection a reviewer will raise is cost — *"a conversational assistant on top of a
$8.49/month subscription is a margin problem."*

This document answers exactly that objection, and nothing else:

> At the token volumes modelled here, assistant inference costs **about one cent per user per
> month**, which is **0.1–0.2% of subscription revenue**. Compute cost is not the constraint on
> funding the assistant. The constraint is product and data quality.

---

## 3. Cost model

The prompt is assembled so that the static prefix is as long as possible, which is what makes cache
reads possible at all:

| Layer | Tokens | Reuse pattern |
|---|---|---|
| Global clinical guardrails and disclaimers | ~750 | identical for every request |
| Reproductive profile (cycle length, LMP, gestational week, TTC logs) | 400–850 | stable within a session |
| Retrieved guideline context (RAG) | ~950 | semi-static across similar topics |
| Prior turns in session | 200–1,200 | grows turn by turn |
| Current question | 35–150 | always new |

Cost per request = uncached input tokens at the full input rate + cached tokens at the cache-read
rate + output tokens at the output rate. Cache-read price is 10–50% of input price depending on the
model, which is the entire source of the saving.

**These layer sizes are design assumptions, not measurements.** They come from typical assistant
prompt structures; nothing in this folder measures Ivy's real prompts.

---

## 4. What is simulated, and how

`scripts/fetch_ivy_cost_datasets.py` generates the telemetry with `random`: session counts, turn
counts, token sizes, cohort assignment, model routing and inter-turn gaps are all drawn from
ranges, then priced with the real table above.

Consequences that matter when citing this work:

1. **The cache hit rate is an artefact of the generator.** It reflects the ranges chosen in the
   script, not how Ivy's users behave. Quoting "71%" or "83%" as an Ivy fact would be wrong.
2. **User ids are reused across cohorts.** 196 of the 345 ids appear in two or three cohorts, so the
   sum of per-cohort user counts (238 + 185 + 162 = 585) is **not** 585 people. Distinct users are
   **345**.
3. **The Q&A corpus behind the prompt sizing is partly mislabelled.** Of 157 rows, 146 came from a
   Hugging Face MedQnA pull whose domain filter failed (e.g. an Alkhuruma haemorrhagic fever
   question is tagged `PERIOD_TRACKING`), and 11 rows labelled `ACOG_Clinical_Guideline_QA` are
   **written by hand in the enrichment script**, not retrieved from ACOG. Those 11 rows must not be
   cited as ACOG guidance, and they are not used as evidence anywhere in the scorecard.

---

## 5. Modelled output (recomputed 2026-11-10)

Method: join each request to its model's price row, then sum
`uncached_tokens × input_price + cached_tokens × cache_read_price + output_tokens × output_price`.

| Metric | Value |
|---|---|
| Requests modelled | 2,547 across 800 sessions, 345 users, 29 days |
| Cost if every input token were billed at full price | $5.2457 |
| Cost with cache reads applied | $2.9984 |
| Reduction from caching | **42.8%** |
| Cost per request | **$0.00118** |
| Cache-read share of input tokens | **72.5%** |
| Cost per distinct user, whole window | **$0.0087** |
| Cost per user per month (window-scaled) | **≈ $0.0091** |

### Against real subscription prices

| Plan | Monthly revenue | Model cost | Cost as % of revenue |
|---|---|---|---|
| Tracker, monthly $8.49 | $8.49 | $0.0091 | **0.11%** |
| Tracker, annual $48.00 (≈ $4.00/mo) | $4.00 | $0.0091 | **0.23%** |
| Coach, monthly $9.99 | $9.99 | $0.0091 | **0.09%** |

Even if real traffic were **ten times** this model, the cost stays under 2.5% of revenue on the
cheapest annual plan. That is the whole finding.

> Corrections to the earlier draft of this document: the executive summary quoted "43.8% to 51.3%"
> and "$0.003–$0.008 per user/month". Recomputed from the same file, the reduction is **42.8%** and
> the per-user cost is **≈$0.0091**. The earlier $0.0051 figure divided by 585 (the sum of
> per-cohort counts) instead of 345 distinct users.

---

## 6. What this model cannot show

| Claim | Why it is out of scope |
|---|---|
| "The assistant raises retention" | Retention is a demand-side outcome; no usage data exists. See the framework note §9 |
| "Users want a chat assistant" | The corpus shows only 13 of 5,019 Tracker reviews mention AI (0.26%) |
| "Caching will save 42.8% in production" | The saving depends on real prompt structure and traffic spacing, both simulated here |
| "Gross margin is 99.9%" | That divides by inference cost only, ignoring infrastructure, payment fees, support and people |
| "Ivy's assistant costs $0.009/user/month" | It costs that in this model; Ivy has published no telemetry |

---

## 7. How to use this in the deck

Put it in the appendix as **Feasibility support**, and say one sentence on the slide:

> "Operating cost is not the constraint: at modelled volumes the assistant runs at roughly one cent
> per user per month, under a quarter of one percent of subscription revenue. The binding constraint
> is whether the assistant can see the user's history and be trusted with it."

Do not put the percentage reduction on a scorecard slide. It answers a question nobody in the room
is asking; the room is asking whether users will stay.

---

## 8. Reproducing

```bash
python3 scripts/fetch_ivy_cost_datasets.py   # refetches prices, regenerates simulated telemetry
python3 - <<'PY'
import pandas as pd
t = pd.read_csv("data/bigquery/fact_ivy_prompt_telemetry.csv")
p = pd.read_csv("data/pricing/dim_model_pricing.csv")
m = t.merge(p[["model_id","input_cost_per_1m","cached_read_cost_per_1m","output_cost_per_1m"]], on="model_id")
m["c"] = (m.uncached_tokens/1e6)*m.input_cost_per_1m + (m.cached_tokens_read/1e6)*m.cached_read_cost_per_1m + (m.output_tokens/1e6)*m.output_cost_per_1m
print(round(m.c.sum(), 4), round(m.c.sum()/m.user_id.nunique(), 5))
PY
```

Re-running the fetch script **replaces the simulated file with a different random draw**, so the
numbers in §5 will move slightly. Any figure quoted from this document must carry the date of the
run it came from.
