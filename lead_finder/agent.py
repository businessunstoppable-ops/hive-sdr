from .google_maps_search import GoogleMapsLeadFinder
import os
from dotenv import load_dotenv

load_dotenv()

class LeadFinderAgent:
    def __init__(self):
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if not api_key:
            raise ValueError("❌ GOOGLE_MAPS_API_KEY not found in .env")
        self.finder = GoogleMapsLeadFinder(api_key)
        print("✅ LeadFinderAgent using real Google Maps API")

    def find_leads_for_campaign(self, industry: str, city: str, max_leads: int = 30, min_rating: float = 3.5) -> list:
        print(f"🔍 Searching for {industry} in {city} using Google Maps API...")
        raw_leads = self.finder.search_by_keyword(industry, city, max_leads * 2)
        qualified = [lead for lead in raw_leads if lead.rating and lead.rating >= min_rating and lead.website]
        print(f"✅ Found {len(qualified)} qualified leads (rating >= {min_rating})")
        self.finder.save_leads_to_file(qualified[:max_leads])
        return qualified[:max_leads]
