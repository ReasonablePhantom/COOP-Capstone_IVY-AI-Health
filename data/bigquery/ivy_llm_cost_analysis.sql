-- ====================================================================
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
