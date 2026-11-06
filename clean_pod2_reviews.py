"""
Pod 2 — 数据清洗与抽样脚本
输入: ivy_all_historical_reviews_2011_2026.csv
输出:
  1) ivy_reviews_clean.csv            清洗后的全量语料（带 period / device / lang / burst 标记）
  2) pod2_25_recent_sample.csv        Brief 规定的"每个 App 最近 12 个月最新 25 条"候选样本（待人工编码）
  3) pod2_monthly_trend.csv           月度评分趋势（用于改版事件研究）

运行: ./venv/bin/python clean_pod2_reviews.py
"""

import re
import pandas as pd

TODAY = pd.Timestamp("2026-11-06", tz="UTC")
WINDOW_START = TODAY - pd.Timedelta(days=365)
REBRAND = pd.Timestamp("2026-01-01", tz="UTC")   # 改版/强制更新的近似分界，非精确上线日
BURST_START = pd.Timestamp("2026-07-01", tz="UTC")
BURST_END = pd.Timestamp("2026-08-31", tz="UTC")

SRC = "ivy_all_historical_reviews_2011_2026.csv"

# ---------- 1. 读入 ----------
df = pd.read_csv(SRC)

# 关键：日期列混用 "2026-01-01T07:28:12-07:00" 与 "2026-09-05 16:10:53"。
# 直接 pd.to_datetime(..., utc=True) 会静默把 500 行变成 NaT，必须用 format="mixed"。
df["date"] = pd.to_datetime(df["date"], format="mixed", utc=True, errors="coerce")

before = len(df)
df = df.dropna(subset=["date", "rating"]).copy()
df = df[df["rating"].between(1, 5)]
print(f"[dates] 丢弃无法解析日期/评分的行: {before - len(df)}")

# ---------- 2. 去重 ----------
# 只按 (app, store, review_id) 去重。不要按文本去重：
# 583 组重复文本里绝大多数是 "Good" / "Great app" 这类不同用户的短评。
# 注意：teammate 表的 292 个空行会让 review_id 被读成 float64（13581359445.0），
# 与字符串 "13581359445" 去重匹配不到，所以先归一成整数字符串。
def norm_id(x):
    if pd.isna(x):
        return None
    try:
        return str(int(float(x)))
    except (TypeError, ValueError):
        return str(x).strip()

df["review_id"] = df["review_id"].map(norm_id)
dup_before = len(df)
df = df.drop_duplicates(subset=["app_name", "store", "review_id"], keep="first")
print(f"[dedupe] 按 review_id 丢弃: {dup_before - len(df)}")

# 只标记"同文本 + 同日期 + 不同国家"的可疑跨区重复，供人工判断，不自动删
sig = df.groupby(["app_name", "review_text", "date"])["country"].nunique()
cross = sig[sig > 1].index
df["cross_country_dup"] = df.set_index(["app_name", "review_text", "date"]).index.isin(cross)

# ---------- 3. 派生标记 ----------
df["period"] = df["date"].ge(REBRAND).map({True: "ivy_rebrand", False: "bellabeat_legacy"})

legacy_pat = r"\bleaf\b|\bspring\b|\btime\b|airi|bellabeat"
ivy_pat = r"ivy\+|ivy plus|\bivy\b"
txt = (df["title"].fillna("") + " " + df["review_text"].fillna("")).str.lower()
df["device_mention"] = "none"
df.loc[txt.str.contains(legacy_pat, regex=True), "device_mention"] = "legacy"
df.loc[txt.str.contains(ivy_pat, regex=True), "device_mention"] = "ivy_plus"

df["lang_guess"] = df["review_text"].fillna("").map(
    lambda s: "ascii" if sum(ord(c) < 128 for c in s) / max(len(s), 1) > 0.95 else "non_ascii"
)
df["is_burst"] = df["date"].between(BURST_START, BURST_END)
df["text_len"] = df["review_text"].fillna("").str.len()

# ---------- 4. 输出清洗后全量 ----------
df = df.sort_values("date").reset_index(drop=True)
df.to_csv("ivy_reviews_clean.csv", index=False)

# ---------- 5. Brief 口径的 25 条/App 候选样本 ----------
# "the 25 most recent per app from the last 12 months" —— 按 App 取，不按门店
recent = df[df["date"] >= WINDOW_START].copy()
sample = (
    recent.sort_values("date", ascending=False)
    .groupby("app_name", group_keys=False)
    .head(25)
    .copy()
)
sample = sample.sort_values(["app_name", "date"], ascending=[True, False])
# 空列留给人工编码，避免脚本的标签先入为主
for c in ["primary_theme", "secondary_tags", "coder", "notes"]:
    sample[c] = ""
sample.to_csv("pod2_25_recent_sample.csv", index=False)

# ---------- 6. 月度趋势 ----------
monthly = (
    df.assign(month=df["date"].dt.strftime("%Y-%m"))
    .groupby(["month", "app_name"])
    .agg(n=("rating", "size"), mean_rating=("rating", "mean"),
         share_5=("rating", lambda s: (s == 5).mean()),
         share_1_2=("rating", lambda s: (s <= 2).mean()))
    .reset_index()
)
monthly.to_csv("pod2_monthly_trend.csv", index=False)

# ---------- 7. 控制台摘要 ----------
print(f"\n[clean] 输出 {len(df)} 行 -> ivy_reviews_clean.csv")
print(f"[sample] 最近 12 个月（{WINDOW_START.date()} 起）按 App 取 25 条 -> {len(sample)} 行")
print(sample.groupby(["app_name", "store"]).agg(
    n=("review_id", "size"), mean=("rating", "mean")
).round(2).to_string())
print("\n每个 App 在窗口内的可用条数：")
print(recent.groupby("app_name").size().to_string())
print("\n月度趋势尾部：")
print(monthly.tail(14).to_string(index=False))
print("\n跨国家可疑重复（同文本同日期）行数：", int(df["cross_country_dup"].sum()))
print("非 ASCII 文本行数：", int((df["lang_guess"] == "non_ascii").sum()))
print("标记为 7-8 月洪峰的行数：", int(df["is_burst"].sum()))
