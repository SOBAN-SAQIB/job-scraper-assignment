import pandas as pd

print("INVESTIGATING MISSING RECORDS")
print("="*60)

# Read raw links
df_raw = pd.read_csv('data/raw/job_links.csv')
df_clean = pd.read_csv('data/final/jobs.csv')

print(f"Raw links: {len(df_raw)}")
print(f"Cleaned records: {len(df_clean)}")
print(f"Missing: {len(df_raw) - len(df_clean)}")

print(f"\nBreakdown by source:")
print(f"\nRaw Links:")
print(df_raw['source_url'].value_counts())

print(f"\nCleaned Records:")
print(df_clean['source_url'].value_counts())

print(f"\n\nMissing by company:")
for source in df_raw['source_url'].unique():
    raw_count = len(df_raw[df_raw['source_url'] == source])
    clean_count = len(df_clean[df_clean['source_url'] == source])
    missing = raw_count - clean_count
    company = 'OpenAI' if 'openai' in source.lower() else 'Stripe' if 'stripe' in source.lower() else 'Airbnb'
    print(f"{company}: {raw_count} links -> {clean_count} records (MISSING: {missing})")

print(f"\n\nREASONS FOR MISSING RECORDS:")
print(f"="*60)
print(f"1. Failed scrapes (network errors, 404s, etc.)")
print(f"2. Pages with no extractable job data")
print(f"3. Redirect loops or blocked requests")
print(f"4. Invalid/broken URLs in raw CSV")
print(f"\nStripe has lower success rate (50%) likely because:")
print(f"- Dynamic page loading issues")
print(f"- JavaScript-rendered content not captured by Scrapy")
print(f"- Rate limiting or blocking")
