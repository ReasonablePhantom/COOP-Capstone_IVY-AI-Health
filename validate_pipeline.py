"""
Pipeline validator — 检查拉数脚本产出的数据是否自洽。
不改数据，只报告 PASS / WARN / FAIL。

运行: ./venv/bin/python validate_pipeline.py
"""

import json
import pandas as pd

RAW = "ivy_app_reviews.csv"
BASE = "ivy_store_baselines.csv"
MASTER = "ivy_all_historical_reviews_2011_2026.csv"
TAGGED = "ivy_app_reviews_tagged.csv"
SAMPLE = "pod2_25_recent_sample.csv"

results = []


def check(name, ok, detail):
    results.append((name, "PASS" if ok else "FAIL", detail))


def warn(name, detail):
    results.append((name, "WARN", detail))


def norm_id(x):
    """把 13581359445.0 和 '13581359445' 归一成同一个字符串。"""
    if pd.isna(x):
        return None
    try:
        return str(int(float(x)))
    except (TypeError, ValueError):
        return str(x).strip()


# ---------- 1. 四个目标单元格是否都抓到了 ----------
raw = pd.read_csv(RAW)
base = pd.read_csv(BASE)
expected_cells = {
    ("IVY Period & Pregnancy Tracker", "Apple App Store"),
    ("IVY Period & Pregnancy Tracker", "Google Play"),
    ("IVY Wellness Coach", "Apple App Store"),
    ("IVY Wellness Coach", "Google Play"),
}
present = set(map(tuple, raw[["app_name", "store"]].drop_duplicates().values))
missing = expected_cells - present
check("四个抓取目标都存在", not missing, f"缺失: {sorted(missing)}" if missing else "4/4 存在")

# ---------- 2. 抓取量 vs 门店基线 ----------
rows = []
for _, b in base.iterrows():
    app, store = b["app_name"], b["store"]
    key = "Google Play" if "Google Play" in store else "Apple App Store"
    n = len(raw[(raw.app_name == app) & (raw.store == key)])
    total = b["total_reviews_count"]
    if pd.notna(total) and str(total).isdigit():
        rows.append((app, key, n, int(total), n / int(total)))
    else:
        rows.append((app, key, n, None, None))
for app, store, n, total, ratio in rows:
    if total:
        check(
            f"抓取覆盖率 {app} / {store}",
            ratio >= 0.95,
            f"{n}/{total} = {ratio:.0%}",
        )
    else:
        warn(f"抓取覆盖率 {app} / {store}", f"抓到 {n} 条；门店不公开评论总数（Apple RSS 上限 500）")

# ---------- 3. 主表重复（归一化 ID 后） ----------
m = pd.read_csv(MASTER)
m["rid"] = m["review_id"].map(norm_id)
dups = m.duplicated(subset=["app_name", "store", "rid"], keep=False)
n_dup = int(dups.sum())
check("主表无重复评论（归一化 review_id）", n_dup == 0, f"重复行 {n_dup}；唯一行 {m.drop_duplicates(['app_name','store','rid']).shape[0]} / {len(m)}")
if n_dup:
    d = m[dups].groupby(["app_name", "store"]).size().to_dict()
    warn("重复集中在", str(d))

# ---------- 4. 日期解析 ----------
strict = pd.to_datetime(m["date"], format="mixed", utc=True, errors="coerce")
naive = pd.to_datetime(m["date"], utc=True, errors="coerce")
check("主表日期可解析（format=mixed）", strict.isna().sum() == 0, f"NaT {int(strict.isna().sum())}")
if naive.isna().sum() != strict.isna().sum():
    warn("默认解析会丢日期", f"默认 utc=True 产生 NaT {int(naive.isna().sum())}，必须显式 format='mixed'")

t = pd.read_csv(TAGGED)
t_naive = pd.to_datetime(t["date"], utc=True, errors="coerce")
t_mixed = pd.to_datetime(t["date"], format="mixed", utc=True, errors="coerce")
check("tagged 文件日期可解析", t_mixed.isna().sum() == 0, f"format=mixed NaT {int(t_mixed.isna().sum())}")
if t_naive.isna().sum():
    check("tagged 文件默认解析", False, f"默认 utc=True 把 {int(t_naive.isna().sum())} 行变成 NaT（下游按日期筛选会静默丢数据）")

# ---------- 5. 评分数值范围 / 空文本 ----------
check("评分在 1-5", m["rating"].between(1, 5).all(), f"越界 {int((~m['rating'].between(1,5)).sum())}")
empty = int((m["review_text"].fillna("").str.strip() == "").sum())
warn("空评论文本", f"{empty} 条（仅星级），会影响按文本的主题统计分母")

# ---------- 6. Apple 国家标签 vs 门店计数 ----------
coach_apple = m[(m.app_name.str.contains("Wellness")) & (m.store == "Apple App Store")]
coach_base = base[(base.app_name.str.contains("Wellness")) & (base.store.str.contains("Apple"))]
if len(coach_base):
    ratings = int(coach_base["total_ratings_count"].iloc[0])
    written = len(coach_apple)
    check(
        "Coach iOS 评论数 ≤ 评分数",
        written <= ratings,
        f"评论 {written} vs 评分 {ratings}：评论数不可能超过评分数，说明国家标签或去重有问题",
    )

# ---------- 7. 25 条样本窗口 ----------
if __import__("os").path.exists(SAMPLE):
    s = pd.read_csv(SAMPLE)
    s["d"] = pd.to_datetime(s["date"], format="mixed", utc=True)
    cutoff = pd.Timestamp("2025-11-06", tz="UTC")
    check("25 条样本都在最近 12 个月", s["d"].min() >= cutoff, f"最早 {s['d'].min().date()}；窗口起点 {cutoff.date()}")
    per_app = s.groupby("app_name").size().to_dict()
    check("每个 App 25 条", all(v == 25 for v in per_app.values()), str(per_app))

# ---------- 8. teammate 原始表的空行与 ID 精度 ----------
tc = pd.read_csv("Teammate_Data/teammate_coach_reviews.csv")
blank = int(tc["review_id"].isna().sum())
check("teammate coach 无空行", blank == 0, f"空行 {blank}（会导致 review_id 被读成 float，去重失效）")
if blank:
    warn("实测后果", "空行使 review_id 变成 float64；与字符串 ID 合并时去重匹配不到")

# ---------- 输出 ----------
out = pd.DataFrame(results, columns=["check", "status", "detail"])
print(out.to_string(index=False))
print("\nFAIL:", int((out.status == "FAIL").sum()), " WARN:", int((out.status == "WARN").sum()))
