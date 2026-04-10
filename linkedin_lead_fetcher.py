#!/usr/bin/env python3
"""
LinkedIn Lead Fetcher - uses free Apify actor for regular LinkedIn search.
"""
import requests
import csv
import io
import os
import sys
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
if not APIFY_API_TOKEN:
    print("❌ APIFY_API_TOKEN not set in .env")
    sys.exit(1)

# Free actor for regular LinkedIn search (not Sales Navigator)
ACTOR_ID = "petr_cermak/linkedin-scraper"
SDR_IMPORT_URL = "http://localhost:54609/import/csv"

def fetch_leads_from_apify(search_url: str) -> list:
    print(f"🚀 Running Apify actor for URL: {search_url}")
    client = ApifyClient(APIFY_API_TOKEN)

    # Input for the actor
    run_input = {
        "searchUrl": search_url,
        "maxItems": 20,
        "proxy": { "useApifyProxy": True }
    }

    try:
        run = client.actor(ACTOR_ID).call(run_input=run_input)
        print(f"✅ Actor run finished.")
        leads = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            leads.append(item)
        return leads
    except Exception as e:
        print(f"❌ Apify error: {e}")
        return []

def convert_to_sdr_csv(leads: list) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Website", "Phone", "Rating", "Score"])
    for lead in leads:
        name = lead.get('name') or lead.get('fullName') or ''
        website = lead.get('website') or lead.get('linkedinUrl', '')  # not ideal but placeholder
        phone = lead.get('phone', '')
        writer.writerow([name, website, phone, "", 5])
    return output.getvalue()

def import_into_sdr(csv_data: str) -> None:
    print("📤 Sending leads to HIVE-SDR...")
    files = {'file': ('linkedin_leads.csv', csv_data, 'text/csv')}
    try:
        response = requests.post(SDR_IMPORT_URL, files=files)
        if response.status_code == 303:
            print("✅ Leads imported successfully!")
        else:
            print(f"❌ Import failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("Paste a LinkedIn search URL (e.g., https://www.linkedin.com/search/results/people/?keywords=gym%20owner)")
    search_url = input("URL: ").strip()
    if not search_url:
        print("No URL provided.")
        sys.exit(0)
    leads = fetch_leads_from_apify(search_url)
    if leads:
        csv_data = convert_to_sdr_csv(leads)
        import_into_sdr(csv_data)
    else:
        print("No leads found. Try a different search URL or check your Apify credits.")
