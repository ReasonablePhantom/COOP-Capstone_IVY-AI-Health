import datetime
import requests
import pandas as pd
from google_play_scraper import app as gp_app, Sort, reviews as gp_reviews

# 1. Define Ivy Health AI apps and their official Store IDs
APPS = {
    "IVY Wellness Coach": {
        "google_play_id": "com.bellabeat.cacao",
        "apple_app_id": "1005052173"
    },
    "IVY Period & Pregnancy Tracker": {
        "google_play_id": "org.nanobit.perioddiary",
        "apple_app_id": "436762566"
    }
}

DATE_CHECKED = datetime.date.today().isoformat()
all_reviews = []
baseline_metrics = []

print(f"--- Starting Ivy Health AI App Scrape ({DATE_CHECKED}) ---\n")

for app_name, ids in APPS.items():
    # ==========================================
    # PART A: GOOGLE PLAY STORE (Ratings & Reviews)
    # ==========================================
    gp_id = ids["google_play_id"]
    print(f"[Google Play] Fetching baseline & reviews for: {app_name} ({gp_id})...")
    try:
        gp_info = gp_app(gp_id, lang="en", country="us")
        baseline_metrics.append({
            "app_name": app_name,
            "store": "Google Play Store (US)",
            "store_id": gp_id,
            "overall_rating": round(gp_info.get("score", 0), 2),
            "total_ratings_count": gp_info.get("ratings", 0),
            "total_reviews_count": gp_info.get("reviews", 0),
            "installs": gp_info.get("installs", "N/A"),
            "date_checked": DATE_CHECKED
        })

        # Fetch up to 500 newest reviews from Google Play
        gp_rev_list, _ = gp_reviews(
            gp_id,
            lang="en",
            country="us",
            sort=Sort.NEWEST,
            count=500
        )
        for r in gp_rev_list:
            all_reviews.append({
                "app_name": app_name,
                "store": "Google Play",
                "review_id": r.get("reviewId"),
                "date": r.get("at").isoformat() if r.get("at") else None,
                "rating": r.get("score"),
                "title": None,
                "review_text": r.get("content"),
                "thumbs_up": r.get("thumbsUpCount", 0),
                "app_version": r.get("reviewCreatedVersion"),
                "developer_reply": r.get("replyContent"),
                "date_scraped": DATE_CHECKED
            })
        print(f"  -> Pulled {len(gp_rev_list)} Google Play reviews.")
    except Exception as e:
        print(f"  -> Error on Google Play ({app_name}): {e}")

    # ==========================================
    # PART B: APPLE APP STORE (Ratings & RSS Reviews)
    # ==========================================
    apple_id = ids["apple_app_id"]
    print(f"[Apple App Store] Fetching baseline & reviews for: {app_name} ({apple_id})...")
    try:
        # Lookup baseline rating via iTunes Search API
        lookup_url = f"https://itunes.apple.com/lookup?id={apple_id}&country=us"
        resp = requests.get(lookup_url, timeout=15).json()
        if resp.get("resultCount", 0) > 0:
            info = resp["results"][0]
            baseline_metrics.append({
                "app_name": app_name,
                "store": "Apple App Store (US)",
                "store_id": apple_id,
                "overall_rating": round(info.get("averageUserRating", 0), 2),
                "total_ratings_count": info.get("userRatingCount", 0),
                "total_reviews_count": "N/A (Apple RSS max 500)",
                "installs": "N/A",
                "date_checked": DATE_CHECKED
            })

        # Pull up to 10 pages (500 reviews max) from Apple's public Customer Reviews RSS feed
        apple_rev_count = 0
        for page in range(1, 11):
            rss_url = f"https://itunes.apple.com/us/rss/customerreviews/page={page}/id={apple_id}/sortby=mostrecent/json"
            r_resp = requests.get(rss_url, timeout=15)
            if r_resp.status_code != 200:
                break
            feed = r_resp.json().get("feed", {})
            entries = feed.get("entry", [])
            if not entries:
                break
            # If only 1 entry exists, ensure it's a list
            if isinstance(entries, dict):
                entries = [entries]

            for entry in entries:
                # Skip metadata entry if present
                if "author" not in entry or "im:rating" not in entry:
                    continue
                all_reviews.append({
                    "app_name": app_name,
                    "store": "Apple App Store",
                    "review_id": entry.get("id", {}).get("label"),
                    "date": entry.get("updated", {}).get("label"),
                    "rating": int(entry.get("im:rating", {}).get("label", 0)),
                    "title": entry.get("title", {}).get("label"),
                    "review_text": entry.get("content", {}).get("label"),
                    "thumbs_up": int(entry.get("im:voteSum", {}).get("label", 0)),
                    "app_version": entry.get("im:version", {}).get("label"),
                    "developer_reply": None,
                    "date_scraped": DATE_CHECKED
                })
                apple_rev_count += 1
        print(f"  -> Pulled {apple_rev_count} Apple App Store reviews.\n")
    except Exception as e:
        print(f"  -> Error on Apple App Store ({app_name}): {e}\n")

# 2. Save Baselines & Reviews to CSV
df_baselines = pd.DataFrame(baseline_metrics)
df_reviews = pd.DataFrame(all_reviews)

df_baselines.to_csv("ivy_store_baselines.csv", index=False)
df_reviews.to_csv("ivy_app_reviews.csv", index=False)

print("=== SCRAPE COMPLETE ===")
print("\n1. Store Baseline Metrics (Saved to ivy_store_baselines.csv):")
print(df_baselines.to_string(index=False))
print(f"\n2. Total Reviews Saved to ivy_app_reviews.csv: {len(df_reviews)}")
if not df_reviews.empty:
    print("\nReview Counts by App & Store:")
    print(df_reviews.groupby(["app_name", "store", "rating"]).size().unstack(fill_value=0))
