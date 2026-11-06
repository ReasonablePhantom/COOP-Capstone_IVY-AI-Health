"""
build_all_historical_reviews_v2.py — 修复版主表构建

修复了 v1 的四个问题：
  1. review_id 在 teammate 表里因 292 个空行被读成 float64，与字符串 ID 去重匹配不到 → 先 dropna + 统一成字符串
  2. 日期混用 "2026-01-01T07:28:12-07:00" 与 "2026-09-05 16:10:53" → 全部转 UTC
  3. 去重只按 review_id，未归一化 → 归一化后再去重
  4. 丢掉 date_scraped → 保留

输出: ivy_all_historical_reviews_v2.csv + dedupe_report.csv
"""

import pandas as pd

REBRAND_SRC = "ivy_app_reviews.csv"
OUT = "ivy_all_historical_reviews_v2.csv"


def parse_excel_date(v):
    if pd.isna(v):
        return pd.NaT
    try:
        return pd.to_datetime("1899-12-30") + pd.to_timedelta(float(v), "D")
    except (TypeError, ValueError):
        return pd.to_datetime(v, format="mixed", errors="coerce")


def norm_id(x):
    if pd.isna(x):
        return None
    try:
        return str(int(float(x)))
    except (TypeError, ValueError):
        return str(x).strip()


# ---------- 读入 ----------
our = pd.read_csv(REBRAND_SRC, dtype={"review_id": str})
tp = pd.read_csv("Teammate_Data/teammate_pregnancy_reviews.csv", dtype={"review_id": str})
tc = pd.read_csv("Teammate_Data/teammate_coach_reviews.csv", dtype={"review_id": str})

print("raw rows:", len(our), len(tp), len(tc))
tp = tp.dropna(subset=["review_id"]).copy()
tc = tc.dropna(subset=["review_id"]).copy()
print("after dropna:", len(our), len(tp), len(tc))

# ---------- 标准化 ----------
our = our.copy()
our["country"] = "us"
our["date"] = pd.to_datetime(our["date"], format="mixed", utc=True)
our["source_batch"] = "Our Scrape (US Store)"
our["date_scraped"] = "2026-10-28"

for df, app, batch in [(tp, "IVY Period & Pregnancy Tracker", "Teammate (Global Apple RSS)"),
                       (tc, "IVY Wellness Coach", "Teammate (Global Apple RSS)")]:
    df["app_name"] = app
    df["store"] = "Apple App Store"
    df["date"] = df["date"].map(parse_excel_date).dt.tz_localize("UTC")
    df["review_text"] = df["review"].fillna("")
    df["thumbs_up"] = pd.to_numeric(df["helpful_votes"], errors="coerce").fillna(0).astype(int)
    df["developer_reply"] = None
    df["source_batch"] = batch
    df["date_scraped"] = "2026-10-28"

cols = ["app_name", "store", "country", "review_id", "date", "rating", "title",
        "review_text", "thumbs_up", "app_version", "developer_reply", "source_batch", "date_scraped"]

# 自己的抓取放前面：重复时保留 UTC 时间戳更精确的那条
master = pd.concat([our[cols], tp[cols], tc[cols]], ignore_index=True)
master["review_id"] = master["review_id"].map(norm_id)
master["rating"] = pd.to_numeric(master["rating"], errors="coerce")
master = master.dropna(subset=["review_id", "date", "rating"])
master = master[master["rating"].between(1, 5)]

# ---------- 去重 ----------
key = ["app_name", "store", "review_id"]
dup_mask = master.duplicated(subset=key, keep="first")
report = master[dup_mask].copy()
master = master[~dup_mask].sort_values("date").reset_index(drop=True)

master.to_csv(OUT, index=False)
report.to_csv("dedupe_report.csv", index=False)

print(f"\n[v2] {len(master)} 行 -> {OUT}")
print(f"[v2] 丢弃重复 {len(report)} 行 -> dedupe_report.csv")
print("\n按 App/Store：")
print(master.groupby(["app_name", "store"]).size().to_string())
print("\n重复集中在：")
print(report.groupby(["app_name", "store"]).size().to_string() if len(report) else "无")
print("\nCoach 均分：", round(master[master.app_name.str.contains("Wellness")].rating.mean(), 2))
