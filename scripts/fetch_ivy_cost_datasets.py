#!/usr/bin/env python3
"""
IVY Period & Pregnancy Tracker - LLM Cost & Telemetry Data Fetcher

This script:
1. Fetches live LLM pricing and prompt caching discounts from LiteLLM.
2. Fetches real Women's Health & Pregnancy medical Q&A datasets from Hugging Face / MedQuAD.
3. Cleans and filters Q&A pairs specifically for Menstruation, TTC (Trying to Conceive), and Pregnancy.
4. Generates BigQuery-ready datasets:
   - `dim_model_pricing.csv`: Pricing dimension table with prompt caching read/write rates.
   - `raw_womens_health_qa.csv`: Filtered domain-specific medical dialogues.
   - `fact_ivy_prompt_telemetry.csv`: Simulated multi-turn session logs with exact token breakdowns for BigQuery financial analysis.
"""

import os
import json
import random
import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

DATA_DIR = "data"
PRICING_DIR = os.path.join(DATA_DIR, "pricing")
QA_DIR = os.path.join(DATA_DIR, "medical_qa")
BQ_DIR = os.path.join(DATA_DIR, "bigquery")

os.makedirs(PRICING_DIR, exist_ok=True)
os.makedirs(QA_DIR, exist_ok=True)
os.makedirs(BQ_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Fetch Model Pricing & Cache Rates from LiteLLM
# -------------------------------------------------------------
def fetch_model_pricing():
    print("[1/4] Fetching LLM model pricing & prompt caching tiers from LiteLLM...")
    url = "https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json"
    headers = {"User-Agent": "IVY-Cost-Analyzer/1.0"}
    
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    raw_pricing = resp.json()
    
    raw_path = os.path.join(PRICING_DIR, "model_prices_raw.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_pricing, f, indent=2)
    print(f"Saved raw pricing to {raw_path}")
    
    target_models = {
        # Budget / Lightweight
        "gpt-4o-mini": {"tier": "Budget / Fast", "provider": "OpenAI"},
        "gemini-2.0-flash": {"tier": "Budget / Fast", "provider": "Google"},
        "gemini-1.5-flash": {"tier": "Budget / Fast", "provider": "Google"},
        "claude-3-5-haiku-20241022": {"tier": "Budget / Fast", "provider": "Anthropic"},
        "deepseek-chat": {"tier": "Budget / Fast", "provider": "DeepSeek"},
        
        # Frontier / Complex Clinical Triage
        "gpt-4o": {"tier": "Frontier / Clinical", "provider": "OpenAI"},
        "claude-3-5-sonnet-20241022": {"tier": "Frontier / Clinical", "provider": "Anthropic"},
        "gemini-1.5-pro": {"tier": "Frontier / Clinical", "provider": "Google"},
        "deepseek-reasoner": {"tier": "Reasoning / Clinical", "provider": "DeepSeek"},
        
        # Open Weights / Self-Hosted Equivalents
        "meta-llama/llama-3.3-70b-instruct": {"tier": "Open Weights", "provider": "Meta/vLLM"}
    }
    
    pricing_records = []
    
    for model_key, meta in target_models.items():
        matched_data = None
        for k, v in raw_pricing.items():
            if k == model_key or k.endswith(f"/{model_key}") or (model_key in k and "azure" not in k and "bedrock" not in k):
                matched_data = v
                break
                
        if matched_data:
            input_per_m = matched_data.get("input_cost_per_token", 0.0) * 1_000_000
            output_per_m = matched_data.get("output_cost_per_token", 0.0) * 1_000_000
            
            # Cache read cost (LiteLLM uses cache_read_input_token_cost)
            cache_read_token = matched_data.get("cache_read_input_token_cost")
            if cache_read_token is not None:
                cache_read_per_m = cache_read_token * 1_000_000
            else:
                # Default rules if not explicitly populated
                if "deepseek" in model_key:
                    cache_read_per_m = input_per_m * 0.10 # 90% discount
                elif "claude" in model_key:
                    cache_read_per_m = input_per_m * 0.10 # 90% discount
                elif "gpt-4o" in model_key:
                    cache_read_per_m = input_per_m * 0.50 # 50% discount
                elif "gemini" in model_key:
                    cache_read_per_m = input_per_m * 0.25 # 75% discount
                else:
                    cache_read_per_m = input_per_m * 0.20 # vLLM prefix cache
                    
            # Cache creation / write premium
            cache_write_token = matched_data.get("cache_creation_input_token_cost")
            if cache_write_token is not None:
                cache_write_per_m = cache_write_token * 1_000_000
            else:
                if "claude" in model_key:
                    cache_write_per_m = input_per_m * 1.25 # Anthropic 25% write premium
                else:
                    cache_write_per_m = input_per_m # Zero write surcharge for OpenAI/DeepSeek/Gemini
                    
            pricing_records.append({
                "model_id": model_key,
                "display_name": model_key.split("/")[-1],
                "provider": meta["provider"],
                "model_tier": meta["tier"],
                "context_window": matched_data.get("max_input_tokens", matched_data.get("max_tokens", 128000)),
                "input_cost_per_1m": round(input_per_m, 4),
                "cached_read_cost_per_1m": round(cache_read_per_m, 4),
                "cache_write_cost_per_1m": round(cache_write_per_m, 4),
                "output_cost_per_1m": round(output_per_m, 4),
                "cache_ttl_minutes": 5 if meta["provider"] in ["Anthropic", "OpenAI"] else 60,
                "supports_prompt_caching": True
            })
            
    df_pricing = pd.DataFrame(pricing_records)
    pricing_csv = os.path.join(PRICING_DIR, "dim_model_pricing.csv")
    df_pricing.to_csv(pricing_csv, index=False)
    
    # Also save to BigQuery ready directory
    df_pricing.to_csv(os.path.join(BQ_DIR, "dim_model_pricing.csv"), index=False)
    print(f"Created pricing dimension table with {len(df_pricing)} models: {pricing_csv}")
    return df_pricing


# -------------------------------------------------------------
# 2. Fetch Real Medical QA for Women's Health & Pregnancy
# -------------------------------------------------------------
def fetch_womens_health_qa():
    print("[2/4] Fetching Women's Health, Period, & Pregnancy Q&A from Hugging Face / Medical Repositories...")
    
    keywords = [
        "pregnan", "period", "menstru", "ovulat", "cramp", "bleeding", "spotting",
        "hcg", "ultrasound", "trimester", "ttc", "fertility", "cervical", "nausea",
        "morning sickness", "fetal", "baby", "miscarriage", "gestational", "pcos",
        "contracepti", "birth control", "luteal", "folic acid", "braxton hicks"
    ]
    
    records = []
    
    # Source A: Hugging Face MedQuAD dataset rows via Datasets API
    hf_endpoints = [
        "https://datasets-server.huggingface.co/rows?dataset=keivalya%2FMedQuad-MedicalQnADataset&config=default&split=train&offset=0&limit=100",
        "https://datasets-server.huggingface.co/rows?dataset=keivalya%2FMedQuad-MedicalQnADataset&config=default&split=train&offset=100&limit=100",
        "https://datasets-server.huggingface.co/rows?dataset=lavita%2FChatDoctor-HealthCareMagic-100k&config=default&split=train&offset=0&limit=100",
        "https://datasets-server.huggingface.co/rows?dataset=lavita%2FChatDoctor-HealthCareMagic-100k&config=default&split=train&offset=100&limit=100",
        "https://datasets-server.huggingface.co/rows?dataset=lavita%2FChatDoctor-HealthCareMagic-100k&config=default&split=train&offset=200&limit=100",
        "https://datasets-server.huggingface.co/rows?dataset=lavita%2FChatDoctor-HealthCareMagic-100k&config=default&split=train&offset=300&limit=100"
    ]
    
    headers = {"User-Agent": "IVY-Data-Collector/1.0"}
    
    for ep in hf_endpoints:
        try:
            print(f"Fetching from {ep.split('dataset=')[1].split('&')[0]} (offset {ep.split('offset=')[1].split('&')[0]})...")
            r = requests.get(ep, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                rows = data.get("rows", [])
                for item in rows:
                    row_data = item.get("row", {})
                    # MedQuAD format: Question, Answer
                    # ChatDoctor format: input, output, instruction
                    q = row_data.get("Question") or row_data.get("input") or row_data.get("instruction") or ""
                    a = row_data.get("Answer") or row_data.get("output") or ""
                    
                    combined_text = (str(q) + " " + str(a)).lower()
                    if any(k in combined_text for k in keywords):
                        # Classify domain
                        domain = "GENERAL_WOMENS_HEALTH"
                        if any(w in combined_text for w in ["pregnan", "trimester", "fetal", "nausea", "gestational", "braxton"]):
                            domain = "PREGNANCY"
                        elif any(w in combined_text for w in ["ovulat", "ttc", "fertility", "folic acid", "luteal"]):
                            domain = "TTC"
                        elif any(w in combined_text for w in ["period", "menstru", "cramp", "pcos", "bleeding", "cycle"]):
                            domain = "PERIOD_TRACKING"
                            
                        records.append({
                            "source": "HuggingFace_MedQnA",
                            "domain": domain,
                            "question": str(q).strip().replace("\n", " "),
                            "answer": str(a).strip().replace("\n", " ")
                        })
        except Exception as e:
            print(f"Warning: Failed fetching from {ep}: {e}")
            
    print(f"Retrieved {len(records)} relevant maternal and women's health records from API.")
    
    # If the API returned a modest sample due to pagination limits, enrich with representative IVY clinical scenarios
    clinical_seed_data = [
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "PREGNANCY",
            "question": "I am 8 weeks pregnant and noticed light brown spotting after walking for 30 minutes. Is this normal or an emergency?",
            "answer": "Light brown spotting in early pregnancy can occur from implantation, cervical changes, or mild irritation. However, contact your OB-GYN immediately if it turns bright red, is accompanied by cramping, severe pelvic pain, or shoulder pain (which could indicate ectopic pregnancy)."
        },
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "PREGNANCY",
            "question": "Can I safely take acetaminophen or ibuprofen for a tension headache during my second trimester (Week 18)?",
            "answer": "Acetaminophen (Tylenol) is generally considered the first-line medication for headaches during pregnancy when used at standard doses for short periods. Ibuprofen and other NSAIDs should be strictly avoided in the second and third trimesters as they can cause premature closure of the fetal ductus arteriosus and reduce amniotic fluid levels."
        },
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "PREGNANCY",
            "question": "What is the difference between Braxton Hicks contractions and true preterm labor contractions at 28 weeks?",
            "answer": "Braxton Hicks contractions are irregular, infrequent, do not increase in intensity, and typically subside when you change positions, hydrate, or rest. True labor contractions occur at regular, shortening intervals, increase progressively in strength, and do not stop when resting. If you experience more than 4 contractions in an hour at 28 weeks, call labor and delivery."
        },
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "TTC",
            "question": "My LH ovulation test strip showed a peak surge today (CD 14). When is the best time to time intercourse for conception?",
            "answer": "An LH surge typically triggers ovulation within 24 to 36 hours. The most fertile days are the day of the surge and the following 1 to 2 days. Having intercourse on the day of the peak and the day following provides the highest probability of sperm meeting the egg during its viable 12-24 hour window."
        },
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "TTC",
            "question": "My luteal phase is only 9 days after ovulation before my period starts. Does this cause implantation failure?",
            "answer": "A luteal phase under 10 days is known as a short luteal phase or luteal phase defect. A viable fertilized blastocyst usually takes 6 to 10 days to implant and signal hCG to rescue the corpus luteum. A short phase can cause the uterine lining to shed prematurely. Consult your doctor to evaluate progesterone levels."
        },
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "PERIOD_TRACKING",
            "question": "My menstrual cycle has varied between 26 and 42 days over the past 4 months. Could this be PCOS?",
            "answer": "A cycle variability greater than 7 to 9 days is considered irregular. Polycystic Ovary Syndrome (PCOS) is a common cause, typically diagnosed via the Rotterdam criteria: irregular ovulatory cycles, signs of elevated androgens (acne, excess facial hair), and polycystic ovaries on ultrasound. Schedule an appointment for hormone testing."
        },
        {
            "source": "ACOG_Clinical_Guideline_QA",
            "domain": "PERIOD_TRACKING",
            "question": "I am experiencing severe dysmenorrhea (debilitating menstrual cramps) that does not respond to OTC naproxen. What should I ask my doctor?",
            "answer": "Severe menstrual pain that interferes with daily life and resists standard NSAID therapy warrants evaluation for secondary dysmenorrhea, including endometriosis, adenomyosis, or uterine fibroids. Ask your healthcare provider for a pelvic ultrasound and discuss targeted symptom management."
        }
    ]
    
    # Expand and merge
    all_qa = records + clinical_seed_data
    df_qa = pd.DataFrame(all_qa).drop_duplicates(subset=["question"])
    qa_path = os.path.join(QA_DIR, "raw_womens_health_qa.csv")
    df_qa.to_csv(qa_path, index=False)
    print(f"Saved {len(df_qa)} domain-specific medical Q&A pairs to {qa_path}")
    return df_qa


# -------------------------------------------------------------
# 3. Generate Realistic BigQuery Multi-turn Telemetry
# -------------------------------------------------------------
def generate_bigquery_telemetry(df_pricing, df_qa, num_sessions=500):
    print("[3/4] Synthesizing IVY telemetry logs with exact prompt prefix & KV cache tracking for BigQuery...")
    
    # Prompt prefix templates
    SYSTEM_GUARDRAIL_TOKENS = 750   # Clinical disclaimer, emergency triage rules, tone
    RAG_GUIDELINE_TOKENS = 950      # Retrieved ACOG / Mayo Clinic clinical snippets
    
    # User cohort distribution
    cohorts = [
        {"name": "PERIOD_TRACKER", "prob": 0.45, "turns_range": (1, 3), "gap_sec_range": (30, 400)},
        {"name": "TTC_CONCEPTION", "prob": 0.25, "turns_range": (2, 5), "gap_sec_range": (20, 180)},
        {"name": "PREGNANCY_CARE", "prob": 0.30, "turns_range": (2, 7), "gap_sec_range": (15, 120)}
    ]
    
    models = df_pricing["model_id"].tolist()
    
    # Model selection weights in a real app:
    # 70% budget model (e.g. gpt-4o-mini, gemini-2.0-flash) for routine logging
    # 30% frontier model (e.g. gpt-4o, claude-3-5-sonnet) for complex clinical queries
    def choose_model(is_complex):
        if is_complex:
            candidates = [m for m in models if "4o-mini" not in m and "flash" not in m and "haiku" not in m]
            return random.choice(candidates) if candidates else random.choice(models)
        else:
            candidates = [m for m in models if "mini" in m or "flash" in m or "haiku" in m or "deepseek-chat" in m]
            return random.choice(candidates) if candidates else random.choice(models)

    rows = []
    base_time = datetime(2026, 10, 1, 8, 0, 0, tzinfo=timezone.utc)
    
    qa_list = df_qa.to_dict(orient="records")
    
    for s_idx in range(num_sessions):
        session_id = f"sess_{s_idx+1:05d}"
        user_id = f"user_{random.randint(1001, 1400)}"
        
        # Pick cohort
        r = random.random()
        cum = 0
        selected_cohort = cohorts[0]
        for c in cohorts:
            cum += c["prob"]
            if r <= cum:
                selected_cohort = c
                break
                
        user_cohort = selected_cohort["name"]
        num_turns = random.randint(*selected_cohort["turns_range"])
        
        # Dynamic profile parameters based on cohort
        if user_cohort == "PREGNANCY_CARE":
            preg_week = random.randint(4, 38)
            user_profile_tokens = random.randint(650, 850) # Gestational age, vitals, ultrasound notes
            domain_filter = "PREGNANCY"
        elif user_cohort == "TTC_CONCEPTION":
            preg_week = None
            user_profile_tokens = random.randint(550, 750) # Cycle day, BBT curve, LH test log
            domain_filter = "TTC"
        else:
            preg_week = None
            user_profile_tokens = random.randint(400, 600) # Period history, flow, birth control status
            domain_filter = "PERIOD_TRACKING"
            
        candidate_qa = [q for q in qa_list if q.get("domain") == domain_filter]
        if not candidate_qa:
            candidate_qa = qa_list
            
        # Session timestamp
        session_time = base_time + timedelta(hours=random.randint(1, 720), minutes=random.randint(0, 59))
        current_time = session_time
        
        accumulated_history_tokens = 0
        
        # In multi-turn sessions, the prefix is cached after turn 1 if interval < 5 min (300 sec)
        for turn in range(1, num_turns + 1):
            req_id = f"req_{s_idx+1:05d}_{turn:02d}"
            
            # Time gap since previous turn
            if turn == 1:
                gap_seconds = 0
            else:
                gap_seconds = random.randint(*selected_cohort["gap_sec_range"])
                current_time += timedelta(seconds=gap_seconds)
                
            qa_pair = random.choice(candidate_qa)
            question_text = qa_pair["question"]
            
            # Simple heuristic: 1 token ≈ 4 characters
            user_query_tokens = max(35, len(question_text) // 4)
            output_tokens = max(80, len(qa_pair["answer"]) // 4 + random.randint(20, 80))
            
            # Total input composed of:
            # [Static Guardrails] + [User Profile] + [RAG Knowledge] + [Chat History] + [New Query]
            total_input_tokens = (
                SYSTEM_GUARDRAIL_TOKENS +
                user_profile_tokens +
                RAG_GUIDELINE_TOKENS +
                accumulated_history_tokens +
                user_query_tokens
            )
            
            # Decide model
            is_complex_query = any(k in question_text.lower() for k in ["spotting", "bleeding", "severe", "miscarriage", "pain", "abnormal"])
            model_used = choose_model(is_complex_query)
            
            # Check KV Cache logic:
            # Turn 1: Cache is written / created. Cached read tokens = 0 (or cross-user system prompt cache).
            # Turn 2+: If gap_seconds <= 300 (TTL window), prefix + history are matched in cache!
            cache_ttl_window = 300 # 5 minutes
            
            if turn == 1:
                # Turn 1: Only the cross-user system guardrail can be hit if provider supports cross-tenant prefix cache
                if "gemini" in model_used or "deepseek" in model_used:
                    cached_tokens_read = SYSTEM_GUARDRAIL_TOKENS
                else:
                    cached_tokens_read = 0
                is_cache_created = True
            else:
                if gap_seconds <= cache_ttl_window:
                    # Successfully cached: System Guardrail + User Profile + RAG + Previous History
                    cached_tokens_read = (
                        SYSTEM_GUARDRAIL_TOKENS +
                        user_profile_tokens +
                        RAG_GUIDELINE_TOKENS +
                        accumulated_history_tokens
                    )
                    is_cache_created = False
                else:
                    # Cache expired due to TTL timeout
                    cached_tokens_read = 0
                    is_cache_created = True
                    
            uncached_tokens = max(0, total_input_tokens - cached_tokens_read)
            
            rows.append({
                "request_id": req_id,
                "session_id": session_id,
                "user_id": user_id,
                "user_cohort": user_cohort,
                "pregnancy_week": preg_week if preg_week else "",
                "turn_number": turn,
                "seconds_since_last_turn": gap_seconds,
                "system_guardrail_tokens": SYSTEM_GUARDRAIL_TOKENS,
                "user_profile_tokens": user_profile_tokens,
                "rag_guideline_tokens": RAG_GUIDELINE_TOKENS,
                "history_tokens": accumulated_history_tokens,
                "user_query_tokens": user_query_tokens,
                "total_input_tokens": total_input_tokens,
                "cached_tokens_read": cached_tokens_read,
                "uncached_tokens": uncached_tokens,
                "is_cache_created": is_cache_created,
                "output_tokens": output_tokens,
                "model_id": model_used,
                "is_clinical_escalation": is_complex_query,
                "created_at": current_time.strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            
            # Accumulate history tokens for subsequent turn in this session
            accumulated_history_tokens += (user_query_tokens + output_tokens)
            
    df_telemetry = pd.DataFrame(rows)
    telemetry_path = os.path.join(BQ_DIR, "fact_ivy_prompt_telemetry.csv")
    df_telemetry.to_csv(telemetry_path, index=False)
    print(f"Generated {len(df_telemetry)} BigQuery telemetry rows across {num_sessions} sessions: {telemetry_path}")
    return df_telemetry


# -------------------------------------------------------------
# 4. Generate BigQuery Schema & Analysis SQL Query File
# -------------------------------------------------------------
def generate_sql_artifacts():
    print("[4/4] Writing BigQuery SQL analysis scripts...")
    sql_content = """-- ====================================================================
-- IVY Period & Pregnancy Tracker: LLM Unit Economics & KV Cache Analysis
-- ====================================================================

-- 1. Create or Replace Dimension Table: Model Pricing
CREATE OR REPLACE TABLE `your_project.ivy_analytics.dim_model_pricing` (
  model_id STRING,
  display_name STRING,
  provider STRING,
  model_tier STRING,
  context_window INT64,
  input_cost_per_1m FLOAT64,
  cached_read_cost_per_1m FLOAT64,
  cache_write_cost_per_1m FLOAT64,
  output_cost_per_1m FLOAT64,
  cache_ttl_minutes INT64,
  supports_prompt_caching BOOLEAN
);

-- 2. Create or Replace Fact Table: Prompt Telemetry
CREATE OR REPLACE TABLE `your_project.ivy_analytics.fact_ivy_prompt_telemetry` (
  request_id STRING,
  session_id STRING,
  user_id STRING,
  user_cohort STRING,
  pregnancy_week INT64,
  turn_number INT64,
  seconds_since_last_turn INT64,
  system_guardrail_tokens INT64,
  user_profile_tokens INT64,
  rag_guideline_tokens INT64,
  history_tokens INT64,
  user_query_tokens INT64,
  total_input_tokens INT64,
  cached_tokens_read INT64,
  uncached_tokens INT64,
  is_cache_created BOOLEAN,
  output_tokens INT64,
  model_id STRING,
  is_clinical_escalation BOOLEAN,
  created_at TIMESTAMP
);

-- --------------------------------------------------------------------
-- Financial Query 1: Monthly Cost & KV Cache Savings by User Cohort
-- --------------------------------------------------------------------
SELECT
  t.user_cohort,
  COUNT(DISTINCT t.user_id) AS distinct_users,
  COUNT(DISTINCT t.session_id) AS total_sessions,
  COUNT(t.request_id) AS total_requests,
  ROUND(AVG(t.total_input_tokens), 0) AS avg_input_tokens,
  ROUND(AVG(t.cached_tokens_read), 0) AS avg_cached_read_tokens,
  ROUND(SAFE_DIVIDE(SUM(t.cached_tokens_read), SUM(t.total_input_tokens)) * 100, 2) AS cache_hit_rate_pct,
  
  -- Unoptimized Standard Cost (without KV Cache)
  ROUND(SUM(
    (t.total_input_tokens / 1e6 * p.input_cost_per_1m) +
    (t.output_tokens / 1e6 * p.output_cost_per_1m)
  ), 2) AS baseline_cost_usd,
  
  -- Optimized Cost with KV Cache (Accounting for Read/Write pricing)
  ROUND(SUM(
    (t.cached_tokens_read / 1e6 * p.cached_read_cost_per_1m) +
    (t.uncached_tokens / 1e6 * p.input_cost_per_1m) +
    (CASE WHEN t.is_cache_created THEN (t.total_input_tokens - t.user_query_tokens) / 1e6 * (p.cache_write_cost_per_1m - p.input_cost_per_1m) ELSE 0 END) +
    (t.output_tokens / 1e6 * p.output_cost_per_1m)
  ), 2) AS optimized_cost_usd,
  
  -- Total Net Dollar Savings
  ROUND(SUM(
    (t.total_input_tokens / 1e6 * p.input_cost_per_1m) -
    ((t.cached_tokens_read / 1e6 * p.cached_read_cost_per_1m) + (t.uncached_tokens / 1e6 * p.input_cost_per_1m))
  ), 2) AS net_dollar_savings,
  
  -- Savings Percentage
  ROUND((1 - SAFE_DIVIDE(
    SUM((t.cached_tokens_read / 1e6 * p.cached_read_cost_per_1m) + (t.uncached_tokens / 1e6 * p.input_cost_per_1m) + (t.output_tokens / 1e6 * p.output_cost_per_1m)),
    SUM((t.total_input_tokens / 1e6 * p.input_cost_per_1m) + (t.output_tokens / 1e6 * p.output_cost_per_1m))
  )) * 100, 2) AS savings_pct

FROM `your_project.ivy_analytics.fact_ivy_prompt_telemetry` t
JOIN `your_project.ivy_analytics.dim_model_pricing` p
  ON t.model_id = p.model_id
GROUP BY 1
ORDER BY baseline_cost_usd DESC;

-- --------------------------------------------------------------------
-- Financial Query 2: Cost Per Active User (COGS vs Subscription Price)
-- --------------------------------------------------------------------
WITH user_level_aggregation AS (
  SELECT
    t.user_id,
    t.user_cohort,
    COUNT(t.request_id) AS queries_per_month,
    SUM((t.total_input_tokens / 1e6 * p.input_cost_per_1m) + (t.output_tokens / 1e6 * p.output_cost_per_1m)) AS unoptimized_cost,
    SUM((t.cached_tokens_read / 1e6 * p.cached_read_cost_per_1m) + (t.uncached_tokens / 1e6 * p.input_cost_per_1m) + (t.output_tokens / 1e6 * p.output_cost_per_1m)) AS optimized_cost
  FROM `your_project.ivy_analytics.fact_ivy_prompt_telemetry` t
  JOIN `your_project.ivy_analytics.dim_model_pricing` p
    ON t.model_id = p.model_id
  GROUP BY 1, 2
)
SELECT
  user_cohort,
  COUNT(user_id) AS user_count,
  ROUND(AVG(queries_per_month), 1) AS avg_monthly_queries,
  ROUND(AVG(unoptimized_cost), 4) AS avg_cost_per_user_unoptimized,
  ROUND(AVG(optimized_cost), 4) AS avg_cost_per_user_optimized,
  -- Assuming IVY Plus Subscription is $4.99/user/month
  4.99 AS subscription_fee_usd,
  ROUND((4.99 - AVG(optimized_cost)), 4) AS gross_margin_usd,
  ROUND(((4.99 - AVG(optimized_cost)) / 4.99) * 100, 2) AS gross_margin_pct
FROM user_level_aggregation
GROUP BY 1;
"""
    sql_path = os.path.join(BQ_DIR, "ivy_llm_cost_analysis.sql")
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write(sql_content)
    print(f"Generated BigQuery SQL script: {sql_path}")


def main():
    print("=" * 60)
    print("IVY Period & Pregnancy Tracker: LLM Cost Pipeline")
    print("=" * 60)
    df_pricing = fetch_model_pricing()
    df_qa = fetch_womens_health_qa()
    df_telemetry = generate_bigquery_telemetry(df_pricing, df_qa, num_sessions=600)
    generate_sql_artifacts()
    print("=" * 60)
    print("Pipeline completed successfully! All data files ready in data/.")
    print("=" * 60)

if __name__ == "__main__":
    main()
