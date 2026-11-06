import pandas as pd
import numpy as np
import re

# Load raw reviews
df = pd.read_csv("ivy_app_reviews.csv")
df["dt"] = pd.to_datetime(df["date"], utc=True, format="ISO8601")
df["clean_text"] = (df["title"].fillna("") + " " + df["review_text"].fillna("")).str.strip()

# 1. Define the 25 most recent reviews for each app
tracker_25 = df[df["app_name"] == "IVY Period & Pregnancy Tracker"].sort_values("dt", ascending=False).head(25).copy()
coach_25 = df[df["app_name"] == "IVY Wellness Coach"].sort_values("dt", ascending=False).head(25).copy()

# Combine into official 50-review cohort dataset (25 per app)
official_df = pd.concat([tracker_25, coach_25], ignore_index=True)

# 2. Strict Single-Theme Mutually Exclusive Tagging
# The 6 Pod 2 Themes:
# - Theme A: Core Cycle & Health Tracking (Value Driver)
# - Theme B: Hardware & Wearable Sync (Pain Point / Technical)
# - Theme C: Technical Bugs, Crashes & Data Loss (Pain Point)
# - Theme D: Subscription Paywall & Ads (Friction)
# - Theme E: AI Assistant, Coaching & Insights (Core Research Focus)
# - Theme F: UI/UX & General Satisfaction (Design, Usability, General Praise/Dislike)

def assign_single_theme(row):
    text = row["clean_text"].lower()
    app = row["app_name"]
    rating = row["rating"]
    
    # Priority 1: Technical Bugs, Crashes, Blank Screen, Data Loss
    if any(k in text for k in ["blank screen", "crashed", "crashes", "bug", "freeze", "disappeared", "lost data", "un-installed", "latest api"]):
        return "Technical Bugs, Crashes & Data Loss", "Reports crashes, blank screen, freezing, or broken API integrations"

    # Priority 2: Wearable & Device Sync Issues
    if any(k in text for k in ["sync with google fit", "sync with the app", "sync accurately", "connecting", "bluetooth", "pair", "device", "necklace", "bracelet", "steps do not sync", "doesn't sync", "track outside of 9am"]):
        return "Hardware & Wearable Sync", "Reports device connectivity, Bluetooth, or step syncing problems"
        
    # Priority 3: Paywall, Membership, Ads & Billing
    if any(k in text for k in ["locked behind a membership", "ads", "subscription", "renewal reminder", "costume jewelry"]):
        if "subscription" in text or "membership" in text or "ads" in text:
            return "Subscription Paywall & Pricing", "Comments on paid paywall, ads, or renewal reminders"
        if "costume jewelry" in text:
            return "Hardware & Wearable Sync", "Frustration over device becoming useless costume jewelry due to sync"

    # Priority 4: AI Assistant, Coaching & Daily Check-ins
    if any(k in text for k in ["ai agent", "ai wellness", "ai-assisted", "chatbot", "assistant", "daily check-ins", "lifestyle coaching", "nutrition guidance"]):
        return "AI Assistant, Coaching & Support", "Feedback on AI features, automated support, or coaching check-ins"

    # Priority 5: Core Cycle & Pregnancy Tracking Functionality
    if any(k in text for k in ["period", "pregnancy", "cycle", "ovulation", "fertile", "fetal development", "bbt", "predictions", "track fetal", "lead", "track everything in one place"]):
        return "Core Cycle & Health Tracking", "Focuses on cycle, pregnancy, period tracking utility & accuracy"
        
    # Priority 6: UI/UX & General Satisfaction
    return "UI/UX & General Satisfaction", "General praise or feedback on design and overall user experience"

assigned_results = [assign_single_theme(r) for _, r in official_df.iterrows()]
official_df["primary_theme"] = [res[0] for res in assigned_results]
official_df["theme_rationale"] = [res[1] for res in assigned_results]
official_df["sentiment_band"] = official_df["rating"].apply(lambda r: "Positive (4-5★)" if r >= 4 else ("Neutral (3★)" if r == 3 else "Negative (1-2★)"))

# Save the official tagged dataset
cols_to_save = [
    "app_name", "store", "review_id", "date", "rating", "sentiment_band",
    "primary_theme", "theme_rationale", "clean_text"
]
official_df[cols_to_save].to_csv("ivy_pod2_25_reviews_tagged.csv", index=False)

# 3. Create Summary Table per App
summary = official_df.groupby(["app_name", "primary_theme"]).agg(
    review_count=("rating", "count"),
    avg_rating=("rating", "mean"),
    positive_count=("rating", lambda s: (s >= 4).sum()),
    negative_count=("rating", lambda s: (s <= 2).sum())
).reset_index()

summary["pct_of_25"] = (summary["review_count"] / 25.0) * 100
summary["avg_rating"] = summary["avg_rating"].round(2)
summary.to_csv("ivy_pod2_25_theme_summary.csv", index=False)

print("=== TAGGING COMPLETED ===")
print(summary.to_string(index=False))
