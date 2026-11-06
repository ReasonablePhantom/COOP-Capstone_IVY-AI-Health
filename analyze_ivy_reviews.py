import pandas as pd
import re

df = pd.read_csv("ivy_app_reviews.csv")
df["full_text"] = (df["title"].fillna("") + " " + df["review_text"].fillna("")).str.strip()
df["sentiment"] = df["rating"].apply(lambda r: "Positive (4-5★)" if r >= 4 else ("Neutral (3★)" if r == 3 else "Negative (1-2★)"))

# Define keyword buckets aligned with the 4 Capstone Product Lines & Pod 2 Question
THEMES = {
    "Cycle & Pregnancy Tracking": r"\b(period|cycle|ovulation|pregnant|pregnancy|fertile|fertility|calendar|predict|prediction|log|symptoms|luteal)\b",
    "AI Assistant & Chat/Coach": r"\b(ai|assistant|chat|chatbot|airi|coach|advice|insights|personalized|questions|smart)\b",
    "Subscription & Paywall (Membership)": r"\b(pay|paid|subscription|subscribe|membership|premium|free|cost|money|charge|charged|price|expensive|paywall|trial|vip)\b",
    "Wearable Sync & Hardware (IVY+/Leaf)": r"\b(sync|syncing|bluetooth|connect|connection|bracelet|ivy|leaf|tracker|device|watch|wearable|step|steps|sleep|firmware|battery)\b",
    "App Bugs, Crashes & Login/Data Loss": r"\b(bug|crash|crashes|crashing|freeze|glitch|update|login|log in|account|lost data|deleted|disappeared|slow|error|blank|screen)\b"
}

for theme, pattern in THEMES.items():
    df[theme] = df["full_text"].str.contains(pattern, flags=re.IGNORECASE, regex=True)

summary_rows = []
for (app_name, store), group in df.groupby(["app_name", "store"]):
    total = len(group)
    for theme in THEMES.keys():
        matched = group[group[theme]]
        count = len(matched)
        neg_count = len(matched[matched["rating"] <= 2])
        pos_count = len(matched[matched["rating"] >= 4])
        avg_rating = round(matched["rating"].mean(), 2) if count > 0 else 0.0
        summary_rows.append({
            "app_name": app_name,
            "store": store,
            "theme": theme,
            "mentions": count,
            "pct_of_reviews": round((count / total) * 100, 1) if total > 0 else 0,
            "avg_star_rating": avg_rating,
            "positive_4_5_star": pos_count,
            "negative_1_2_star": neg_count
        })

df_summary = pd.DataFrame(summary_rows)
df_summary.to_csv("ivy_pod2_theme_summary.csv", index=False)
df.to_csv("ivy_app_reviews_tagged.csv", index=False)

print("=== POD 2 DESIRABILITY THEME BREAKDOWN (Saved to ivy_pod2_theme_summary.csv) ===\n")
print(df_summary.to_string(index=False))

print("\n=== SAMPLE RECENT NEGATIVE & POSITIVE MENTIONS OF AI / COACH / PAYWALL ===")
ai_or_paywall = df[df["AI Assistant & Chat/Coach"] | df["Subscription & Paywall (Membership)"]].head(8)
for _, row in ai_or_paywall.iterrows():
    snippet = row["full_text"][:180].replace("\n", " ")
    print(f"[{row['app_name']} | {row['store']} | {row['rating']}★ | {str(row['date'])[:10]}] {snippet}...")
