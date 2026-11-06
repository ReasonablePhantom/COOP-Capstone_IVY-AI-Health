import pandas as pd
import numpy as np

# Load our data
our_df = pd.read_csv("ivy_app_reviews.csv")
our_df["dt"] = pd.to_datetime(our_df["date"], utc=True, format="ISO8601")

# Load teammate data
t_preg = pd.read_csv("Teammate_Data/teammate_pregnancy_reviews.csv")
t_coach = pd.read_csv("Teammate_Data/teammate_coach_reviews.csv")

# Convert Excel serial dates to datetime
# Excel origin: 1899-12-30
def excel_date_to_dt(val):
    try:
        f = float(val)
        return pd.to_datetime('1899-12-30') + pd.to_timedelta(f, 'D')
    except:
        return pd.to_datetime(val, errors='coerce')

t_preg["dt"] = t_preg["date"].apply(excel_date_to_dt)
t_coach["dt"] = t_coach["date"].apply(excel_date_to_dt)

print("================ 1. SOURCE & SCOPE COMPARISON ================")
print(f"Our Dataset Total Reviews: {len(our_df)}")
print("Our Dataset Breakdown:")
print(our_df.groupby(["app_name", "store"]).size())
print("\nTeammate Pregnancy Tracker Total Reviews:", len(t_preg))
print("Teammate Pregnancy Countries:", t_preg["country"].value_counts().head(8).to_dict())
print("Teammate Pregnancy Date Range:", t_preg["dt"].min(), "to", t_preg["dt"].max())
print("Teammate Pregnancy Avg Rating:", pd.to_numeric(t_preg["rating"], errors="coerce").mean().round(2))

print("\nTeammate Wellness Coach Total Reviews:", len(t_coach))
print("Teammate Coach Countries:", t_coach["country"].value_counts().head(8).to_dict())
print("Teammate Coach Date Range:", t_coach["dt"].min(), "to", t_coach["dt"].max())
print("Teammate Coach Avg Rating:", pd.to_numeric(t_coach["rating"], errors="coerce").mean().round(2))

print("\n================ 2. OVERLAP ANALYSIS ================")
# Check review_id overlap
our_ids = set(our_df["review_id"].astype(str).str.strip())
t_preg_ids = set(t_preg["review_id"].astype(str).str.strip())
t_coach_ids = set(t_coach["review_id"].astype(str).str.strip())

overlap_preg = our_ids.intersection(t_preg_ids)
overlap_coach = our_ids.intersection(t_coach_ids)

print(f"Review ID Overlap with Teammate Pregnancy: {len(overlap_preg)}")
print(f"Review ID Overlap with Teammate Coach: {len(overlap_coach)}")

# If overlap exists in coach, show sample
if overlap_coach:
    sample_id = list(overlap_coach)[0]
    print(f"Sample matching Review ID: {sample_id}")
    print("Our text:", our_df[our_df["review_id"].astype(str) == sample_id]["review_text"].iloc[0][:100])
    print("Teammate text:", t_coach[t_coach["review_id"].astype(str) == sample_id]["review"].iloc[0][:100])

print("\n================ 3. RATING DISTRIBUTION COMPARISON ================")
print("Our Rating Distribution:")
print(our_df.groupby("app_name")["rating"].value_counts(normalize=True).unstack().round(3) * 100)

print("\nTeammate Rating Distribution (Pregnancy Tracker):")
print((pd.to_numeric(t_preg["rating"], errors="coerce").value_counts(normalize=True).sort_index().round(3) * 100).to_dict())

print("\nTeammate Rating Distribution (Wellness Coach):")
print((pd.to_numeric(t_coach["rating"], errors="coerce").value_counts(normalize=True).sort_index().round(3) * 100).to_dict())
