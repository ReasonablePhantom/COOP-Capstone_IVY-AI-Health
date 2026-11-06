"""
Comprehensive Historical Review Scraper for Ivy Health AI Apps
Scrapes Google Play (All reviews via reviews_all) and Apple App Store (Multi-country RSS up to Apple API limits)
"""
import datetime
import time
import requests
import pandas as pd
from google_play_scraper import reviews_all, Sort

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

APPLE_COUNTRIES = ['us', 'gb', 'ca', 'au', 'nz', 'ie', 'de', 'mx', 'fr', 'es', 'it', 'nl', 'sg', 'in']
DATE_CHECKED = datetime.date.today().isoformat()
all_scraped_reviews = []

print(f"=== Starting Full Historical Scrape ({DATE_CHECKED}) ===\n")

for app_name, ids in APPS.items():
    # -------------------------------------------------------------
    # 1. Google Play: Scrape ALL historical reviews
    # -------------------------------------------------------------
    gp_id = ids["google_play_id"]
    print(f"[Google Play] Pulling ALL historical reviews for {app_name} ({gp_id})...")
    try:
        gp_revs = reviews_all(
            gp_id,
            sleep_milliseconds=200,
            lang='en',
            country='us',
            sort=Sort.NEWEST
        )
        print(f"  -> Successfully fetched {len(gp_revs)} Google Play reviews.")
        for r in gp_revs:
            all_scraped_reviews.append({
                "app_name": app_name,
                "store": "Google Play",
                "country": "us",
                "review_id": str(r.get("reviewId")),
                "date": r.get("at").strftime('%Y-%m-%d %H:%M:%S') if r.get("at") else None,
                "rating": r.get("score"),
                "title": None,
                "review_text": r.get("content") or "",
                "thumbs_up": r.get("thumbsUpCount", 0),
                "app_version": r.get("reviewCreatedVersion"),
                "developer_reply": r.get("replyContent"),
                "source_batch": "Google Play Live Scrape"
            })
    except Exception as e:
        print(f"  -> Error scraping Google Play ({app_name}): {e}")

    # -------------------------------------------------------------
    # 2. Apple App Store: Multi-country RSS (up to 500 per country)
    # -------------------------------------------------------------
    apple_id = ids["apple_app_id"]
    print(f"\n[Apple App Store] Pulling reviews across {len(APPLE_COUNTRIES)} storefronts for {app_name} ({apple_id})...")
    app_apple_count = 0
    for country in APPLE_COUNTRIES:
        country_count = 0
        for page in range(1, 11):
            rss_url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={apple_id}/sortby=mostrecent/json"
            try:
                resp = requests.get(rss_url, timeout=10)
                if resp.status_code != 200:
                    break
                feed = resp.json().get("feed", {})
                entries = feed.get("entry", [])
                if not entries:
                    break
                if isinstance(entries, dict):
                    entries = [entries]

                for entry in entries:
                    if "author" not in entry or "im:rating" not in entry:
                        continue
                    all_scraped_reviews.append({
                        "app_name": app_name,
                        "store": "Apple App Store",
                        "country": country,
                        "review_id": str(entry.get("id", {}).get("label")),
                        "date": entry.get("updated", {}).get("label"),
                        "rating": int(entry.get("im:rating", {}).get("label", 0)),
                        "title": entry.get("title", {}).get("label"),
                        "review_text": entry.get("content", {}).get("label") or "",
                        "thumbs_up": int(entry.get("im:voteSum", {}).get("label", 0)),
                        "app_version": entry.get("im:version", {}).get("label"),
                        "developer_reply": None,
                        "source_batch": f"Apple RSS ({country})"
                    })
                    country_count += 1
                time.sleep(0.1)
            except Exception as e:
                break
        app_apple_count += country_count
    print(f"  -> Total Apple reviews pulled for {app_name}: {app_apple_count}\n")

df = pd.DataFrame(all_scraped_reviews)
if not df.empty:
    df['date'] = pd.to_datetime(df['date'], format='ISO8601', utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.drop_duplicates(subset=['app_name', 'store', 'review_id'])
    df = df.sort_values(by='date', ascending=True).reset_index(drop=True)
    out_file = "live_scraped_all_reviews.csv"
    df.to_csv(out_file, index=False)
    print(f"=== SCRAPE FINISHED: Saved {len(df)} total reviews to {out_file} ===")
else:
    print("No reviews fetched.")
