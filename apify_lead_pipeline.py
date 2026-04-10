#!/usr/bin/env python3
"""
Lead discovery using Apify Google Maps Scraper.
"""
import os
import asyncio
import csv
import io
import requests
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
HIVE_SDR_IMPORT_URL = os.getenv("HIVE_SDR_IMPORT_URL", "http://localhost:54609/import/csv")

async def run_actor(actor_id, actor_input):
    client = ApifyClient(APIFY_API_TOKEN)
    print(f"🚀 Running actor {actor_id} with input {actor_input}")
    run = await client.actor(actor_id).call(run_input=actor_input)
    items = await client.dataset(run["defaultDatasetId"]).list_items()
    print(f"✅ Retrieved {len(items.items)} items.")
    return items.items

def format_leads_for_hive_sdr(leads, lead_type="Company"):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Website", "Phone", "Type", "Job Title", "LinkedIn URL", "Company"])
    for lead in leads:
        name = lead.get('title') or lead.get('name') or ''
        website = lead.get('website') or ''
        phone = lead.get('phone') or ''
        writer.writerow([name, website, phone, lead_type, '', '', ''])
    return output.getvalue()

def import_to_hive_sdr(csv_data):
    files = {'file': ('apify_leads.csv', csv_data, 'text/csv')}
    try:
        response = requests.post(HIVE_SDR_IMPORT_URL, files=files)
        if response.status_code == 303:
            print("✅ Leads imported successfully.")
        else:
            print(f"❌ Import failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")

async def main():
    actor_id = "curious_coder/google-maps-scraper"
    search_queries = [
        "gym in Brooklyn",
        "fitness center in Brooklyn",
        "yoga studio in Brooklyn"
    ]
    all_leads = []
    for query in search_queries:
        actor_input = {
            "searchString": query,
            "maxCrawledPlaces": 20,
            "language": "en",
            "maxResults": 20
        }
        leads = await run_actor(actor_id, actor_input)
        all_leads.extend(leads)
    if all_leads:
        csv_data = format_leads_for_hive_sdr(all_leads, lead_type="Company")
        import_to_hive_sdr(csv_data)
    else:
        print("No leads found.")

if __name__ == "__main__":
    asyncio.run(main())
