import pandas as pd
import numpy as np

print("--- Building Master Historical Reviews Dataset (2011 - 2026) ---")

# 1. Load our scraped data and teammate's data
our_df = pd.read_csv("ivy_app_reviews.csv")
t_preg = pd.read_csv("Teammate_Data/teammate_pregnancy_reviews.csv")
t_coach = pd.read_csv("Teammate_Data/teammate_coach_reviews.csv")

# Drop completely empty rows in teammate data (e.g. trailing empty rows from Excel)
t_preg = t_preg.dropna(subset=['review_id']).copy()
t_coach = t_coach.dropna(subset=['review_id']).copy()

def parse_excel_date(v):
    if pd.isna(v):
        return None
    try:
        f = float(v)
        # Excel date origin: 1899-12-30
        return (pd.to_datetime('1899-12-30') + pd.to_timedelta(f, 'D')).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(v)

# 2. Standardize Teammate Pregnancy Reviews (Apple App Store, Multi-country)
t_preg['app_name'] = 'IVY Period & Pregnancy Tracker'
t_preg['store'] = 'Apple App Store'
t_preg['date'] = t_preg['date'].apply(parse_excel_date)
t_preg['review_text'] = t_preg['review'].fillna('')
t_preg['thumbs_up'] = pd.to_numeric(t_preg['helpful_votes'], errors='coerce').fillna(0).astype(int)
t_preg['developer_reply'] = None
t_preg['date_scraped'] = '2026-10-28'
t_preg['source_batch'] = 'Teammate (Global Apple RSS)'

# 3. Standardize Teammate Coach Reviews (Apple App Store, Multi-country)
t_coach['app_name'] = 'IVY Wellness Coach'
t_coach['store'] = 'Apple App Store'
t_coach['date'] = t_coach['date'].apply(parse_excel_date)
t_coach['review_text'] = t_coach['review'].fillna('')
t_coach['thumbs_up'] = pd.to_numeric(t_coach['helpful_votes'], errors='coerce').fillna(0).astype(int)
t_coach['developer_reply'] = None
t_coach['date_scraped'] = '2026-10-28'
t_coach['source_batch'] = 'Teammate (Global Apple RSS)'

# 4. Standardize Our Scraped Reviews (US Google Play & US Apple App Store)
our_df['country'] = 'us'
our_df['author'] = None
our_df['date'] = pd.to_datetime(our_df['date'], format='ISO8601', utc=True).dt.strftime('%Y-%m-%d %H:%M:%S')
our_df['source_batch'] = 'Our Scrape (US Store)'

# Target columns
cols = [
    'app_name', 'store', 'country', 'review_id', 'date', 
    'rating', 'title', 'review_text', 'thumbs_up', 
    'app_version', 'developer_reply', 'source_batch'
]

df_master = pd.concat([
    t_preg[cols],
    t_coach[cols],
    our_df[cols]
], ignore_index=True)

# 5. Clean & Deduplicate
df_master['rating'] = pd.to_numeric(df_master['rating'], errors='coerce')
# Deduplicate on app_name, store, review_id
df_master = df_master.drop_duplicates(subset=['app_name', 'store', 'review_id'])
# Sort chronologically from oldest to newest
df_master = df_master.sort_values(by='date', ascending=True).reset_index(drop=True)

# 6. Save to CSV
output_path = "ivy_all_historical_reviews_2011_2026.csv"
df_master.to_csv(output_path, index=False)

print(f"\nSuccessfully generated: {output_path}")
print(f"Total Unique Historical Reviews: {len(df_master)}")
print(f"Date Range: {df_master['date'].min()} to {df_master['date'].max()}")
print(f"Missing Dates: {df_master['date'].isna().sum()}")
print("\nBreakdown by App & Store:")
print(df_master.groupby(['app_name', 'store']).size())
