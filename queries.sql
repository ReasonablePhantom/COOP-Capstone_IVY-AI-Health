-- ============================================================
-- Pod 2 常用查询（SQLite）
-- 打开方式：DB Browser for SQLite → 打开 ivy_reviews.db → Execute SQL
-- 或命令行：sqlite3 ivy_reviews.db < queries.sql
-- ============================================================

-- 1. 两个 App × 两个商店：规模、均分、差评率
SELECT app_name, store, n, avg_rating, pct_1_2, pct_5, first_date, last_date
FROM v_app_store_summary
ORDER BY app_name, store;

-- 2. 最近 12 个月 vs 全期（同一 App 的两个商店分开看）
SELECT app_name, store,
       COUNT(*) AS n,
       ROUND(AVG(rating), 2) AS avg_12m,
       ROUND(AVG(CASE WHEN rating <= 2 THEN 1.0 ELSE 0 END) * 100, 1) AS pct_1_2
FROM v_recent_12m
GROUP BY app_name, store;

-- 3. 2026-01 改版事件：按月看均分与 5 星占比
SELECT month, app_name, n, avg_rating, pct_5, pct_1_2
FROM v_monthly
WHERE month >= '2025-01'
ORDER BY month, app_name;

-- 4. 丢数据提及：按年、按 App
SELECT year, app_name, n, loss_mentions,
       ROUND(loss_mentions * 100.0 / n, 1) AS pct_of_year
FROM v_loss_by_year
WHERE year >= 2022
ORDER BY year, app_name;

-- 5. 主题提及 × 均分（基于 1,500 条 one-hot 标注，可多标签）
SELECT app_name, theme, mentions, avg_rating, negative_1_2, positive_4_5
FROM v_theme_summary
ORDER BY app_name, mentions DESC;

-- 6. 含 / 不含 2026-07~08 洪峰（最近 12 个月）
SELECT app_name, is_burst,
       COUNT(*) AS n,
       ROUND(AVG(rating), 2) AS avg_rating,
       ROUND(AVG(CASE WHEN rating <= 2 THEN 1.0 ELSE 0 END) * 100, 1) AS pct_1_2
FROM v_recent_12m
GROUP BY app_name, is_burst
ORDER BY app_name, is_burst;

-- 7. 25 条主样本：星级分布（Tracker 25 条、Coach 24 条；n 小，不要报百分比）
SELECT app_name, rating, COUNT(*) AS n
FROM sample_25
GROUP BY app_name, rating
ORDER BY app_name, rating;

-- 8. 关键词计数（英文；非英文会漏，需人工补）
SELECT app_name, store,
       SUM(CASE WHEN lower(review_text) LIKE '%subscription%'
                 OR lower(review_text) LIKE '%premium%'
                 OR lower(review_text) LIKE '%paywall%' THEN 1 ELSE 0 END) AS paywall,
       SUM(CASE WHEN lower(review_text) LIKE '%sync%'
                 OR lower(review_text) LIKE '%bluetooth%'
                 OR lower(review_text) LIKE '%connect%' THEN 1 ELSE 0 END) AS sync,
       SUM(CASE WHEN lower(review_text) LIKE '% ai %'
                 OR lower(review_text) LIKE '%chatbot%'
                 OR lower(review_text) LIKE '%assistant%' THEN 1 ELSE 0 END) AS ai
FROM reviews
GROUP BY app_name, store;

-- 9. 开发者回复率（只对 "Our Scrape" 批次有效，teammate 批次全空）
SELECT app_name, store,
       COUNT(*) AS n,
       SUM(CASE WHEN has_reply THEN 1 ELSE 0 END) AS replied,
       ROUND(AVG(CASE WHEN has_reply THEN 1.0 ELSE 0 END) * 100, 1) AS reply_rate
FROM reviews
WHERE source_batch = 'Our Scrape (US Store)'
GROUP BY app_name, store;

-- 10. 国家分布（注意：我们自己的 Apple 抓取把 country 硬编码成 us，不可信）
SELECT app_name, store, country, COUNT(*) AS n
FROM reviews
GROUP BY app_name, store, country
ORDER BY n DESC
LIMIT 20;
