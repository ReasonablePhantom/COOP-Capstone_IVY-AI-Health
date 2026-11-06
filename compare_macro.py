import pandas as pd
import numpy as np
import re

df = pd.read_csv("ivy_app_reviews.csv")
df["clean_text"] = (df["title"].fillna("") + " " + df["review_text"].fillna("")).str.strip()

# Apply the same logic across the entire macro dataset (1,500 reviews)
from tag_25_reviews import assign_single_theme

macro_results = [assign_single_theme(r) for _, r in df.iterrows()]
df["primary_theme"] = [res[0] for res in macro_results]

macro_summary = df.groupby(["app_name", "primary_theme"]).agg(
    total_mentions=("rating", "count"),
    avg_rating=("rating", "mean"),
    positive_4_5=("rating", lambda s: (s >= 4).sum()),
    negative_1_2=("rating", lambda s: (s <= 2).sum())
).reset_index()

# Add percentages per app
for app in df["app_name"].unique():
    app_mask = macro_summary["app_name"] == app
    total_app = macro_summary.loc[app_mask, "total_mentions"].sum()
    macro_summary.loc[app_mask, "pct_of_total"] = (macro_summary.loc[app_mask, "total_mentions"] / total_app) * 100

macro_summary["pct_of_total"] = macro_summary["pct_of_total"].round(1)
macro_summary["avg_rating"] = macro_summary["avg_rating"].round(2)

macro_summary.to_csv("ivy_pod2_macro_theme_summary.csv", index=False)

print("=== MACRO (1,500 REVIEWS) SUMMARY ===")
print(macro_summary.to_string(index=False))
