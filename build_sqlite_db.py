"""
build_sqlite_db.py — 把 CSV 变成可以用 SQL 直接查的 SQLite 数据库

为什么用 SQLite:
  - 单文件、无需安装服务、Python 自带 sqlite3
  - DB Browser for SQLite 可以直接打开、点开表、写 SQL
  - 6,000 行数据用它绰绰有余（SQL 的价值是可复现的聚合，不是性能）

输出: ivy_reviews.db
用法: ./venv/bin/python build_sqlite_db.py
"""

import sqlite3
import pandas as pd

DB = "ivy_reviews.db"

# ---------- 读入 ----------
reviews = pd.read_csv("ivy_all_historical_reviews_v2.csv", dtype={"review_id": str})
baselines = pd.read_csv("ivy_store_baselines.csv")
tagged = pd.read_csv("ivy_app_reviews_tagged.csv", dtype={"review_id": str})
sample = pd.read_csv("pod2_25_recent_sample.csv", dtype={"review_id": str})
sample_tagged = pd.read_csv("ivy_pod2_25_reviews_tagged.csv", dtype={"review_id": str})  # 旧版，含 1 条重复

# 日期统一成 SQLite 可排序的 ISO 文本（去掉纳秒/时区）
reviews["date"] = pd.to_datetime(reviews["date"], format="mixed", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
reviews["review_year"] = reviews["date"].str[:4].astype(int)
reviews["review_month"] = reviews["date"].str[:7]
reviews["period"] = (reviews["date"] >= "2026-01-01").map({True: "ivy_rebrand", False: "bellabeat_legacy"})
reviews["is_burst"] = reviews["date"].between("2026-07-01", "2026-08-31 23:59:59")
reviews["has_reply"] = reviews["developer_reply"].notna()
reviews["text_len"] = reviews["review_text"].fillna("").str.len()

# 主题表：保留 one-hot 原样，便于按主题聚合
tagged["date"] = pd.to_datetime(tagged["date"], format="mixed", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
tagged["review_month"] = tagged["date"].str[:7]

# ---------- 写库 ----------
con = sqlite3.connect(DB)
reviews.to_sql("reviews", con, if_exists="replace", index=False)
baselines.to_sql("store_baselines", con, if_exists="replace", index=False)
tagged.to_sql("reviews_tagged", con, if_exists="replace", index=False)
sample.to_sql("sample_25", con, if_exists="replace", index=False)
sample_tagged.to_sql("sample_25_tagged", con, if_exists="replace", index=False)

cur = con.cursor()
cur.executescript(
    """
    DROP VIEW IF EXISTS v_app_store_summary;
    CREATE VIEW v_app_store_summary AS
    SELECT app_name, store,
           COUNT(*)                                   AS n,
           ROUND(AVG(rating), 2)                       AS avg_rating,
           ROUND(AVG(CASE WHEN rating <= 2 THEN 1.0 ELSE 0 END) * 100, 1) AS pct_1_2,
           ROUND(AVG(CASE WHEN rating = 5 THEN 1.0 ELSE 0 END) * 100, 1)  AS pct_5,
           MIN(date) AS first_date, MAX(date) AS last_date
    FROM reviews
    GROUP BY app_name, store;

    DROP VIEW IF EXISTS v_monthly;
    CREATE VIEW v_monthly AS
    SELECT review_month AS month, app_name,
           COUNT(*)                                    AS n,
           ROUND(AVG(rating), 2)                        AS avg_rating,
           ROUND(AVG(CASE WHEN rating = 5 THEN 1.0 ELSE 0 END) * 100, 1) AS pct_5,
           ROUND(AVG(CASE WHEN rating <= 2 THEN 1.0 ELSE 0 END) * 100, 1) AS pct_1_2
    FROM reviews
    GROUP BY review_month, app_name;

    DROP VIEW IF EXISTS v_recent_12m;
    CREATE VIEW v_recent_12m AS
    SELECT * FROM reviews WHERE date >= '2025-11-06';

    DROP VIEW IF EXISTS v_theme_mentions;
    CREATE VIEW v_theme_mentions AS
    SELECT app_name, store, review_id, rating, 'Cycle & Pregnancy Tracking' AS theme
      FROM reviews_tagged WHERE "Cycle & Pregnancy Tracking" = 1
    UNION ALL
    SELECT app_name, store, review_id, rating, 'AI Assistant & Chat/Coach'
      FROM reviews_tagged WHERE "AI Assistant & Chat/Coach" = 1
    UNION ALL
    SELECT app_name, store, review_id, rating, 'Subscription & Paywall (Membership)'
      FROM reviews_tagged WHERE "Subscription & Paywall (Membership)" = 1
    UNION ALL
    SELECT app_name, store, review_id, rating, 'Wearable Sync & Hardware (IVY+/Leaf)'
      FROM reviews_tagged WHERE "Wearable Sync & Hardware (IVY+/Leaf)" = 1
    UNION ALL
    SELECT app_name, store, review_id, rating, 'App Bugs, Crashes & Login/Data Loss'
      FROM reviews_tagged WHERE "App Bugs, Crashes & Login/Data Loss" = 1;

    DROP VIEW IF EXISTS v_theme_summary;
    CREATE VIEW v_theme_summary AS
    SELECT app_name, theme,
           COUNT(*)               AS mentions,
           ROUND(AVG(rating), 2)  AS avg_rating,
           SUM(CASE WHEN rating <= 2 THEN 1 ELSE 0 END) AS negative_1_2,
           SUM(CASE WHEN rating >= 4 THEN 1 ELSE 0 END) AS positive_4_5
    FROM v_theme_mentions
    GROUP BY app_name, theme;

    DROP VIEW IF EXISTS v_loss_by_year;
    CREATE VIEW v_loss_by_year AS
    SELECT review_year AS year, app_name,
           COUNT(*) AS n,
           SUM(CASE WHEN lower(coalesce(title,'') || ' ' || coalesce(review_text,''))
                         LIKE '%lost%'
                      OR lower(coalesce(title,'') || ' ' || coalesce(review_text,''))
                         LIKE '%deleted%'
                      OR lower(coalesce(title,'') || ' ' || coalesce(review_text,''))
                         LIKE '%erased%'
                    THEN 1 ELSE 0 END) AS loss_mentions
    FROM reviews
    GROUP BY review_year, app_name;
    """
)
cur.executescript(
    """
    CREATE INDEX IF NOT EXISTS idx_reviews_app_store ON reviews(app_name, store);
    CREATE INDEX IF NOT EXISTS idx_reviews_date ON reviews(date);
    CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
    CREATE INDEX IF NOT EXISTS idx_reviews_year ON reviews(review_year);
    """
)
con.commit()

# ---------- 自检 ----------
print("tables:", [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")])
print("views: ", [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")])
print("\n行数:", cur.execute("SELECT COUNT(*) FROM reviews").fetchone()[0])
print("\n按 App / Store:")
for row in cur.execute("SELECT * FROM v_app_store_summary ORDER BY app_name, store"):
    print(" ", row)
con.close()
print(f"\n已生成 {DB}")
