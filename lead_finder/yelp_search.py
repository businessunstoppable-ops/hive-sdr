import requests
import os
from typing import List, Dict

class YelpLeadFinder:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.yelp.com/v3/businesses/search"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def search_by_keyword(self, keyword: str, location: str, max_results: int = 20) -> List[Dict]:
        params = {
            "term": keyword,
            "location": location,
            "limit": min(max_results, 50),
            "sort_by": "rating"
        }
        response = requests.get(self.base_url, headers=self.headers, params=params)
        if response.status_code != 200:
            print(f"Yelp API error: {response.status_code}")
            return []
        businesses = response.json().get("businesses", [])
        leads = []
        for biz in businesses:
            leads.append({
                "name": biz.get("name", ""),
                "website": "",  # will be filled by details call
                "phone": biz.get("phone", ""),
                "rating": biz.get("rating", 0),
                "total_ratings": biz.get("review_count", 0),
                "address": ", ".join(biz.get("location", {}).get("display_address", [])),
                "categories": [cat["title"] for cat in biz.get("categories", [])],
                "yelp_id": biz.get("id", "")
            })
        # Fetch websites from business details
        for lead in leads:
            details = self._get_business_details(lead["yelp_id"])
            if details:
                lead["website"] = details.get("website", "")
        return leads

    def _get_business_details(self, business_id: str) -> Dict:
        url = f"https://api.yelp.com/v3/businesses/{business_id}"
        resp = requests.get(url, headers=self.headers)
        return resp.json() if resp.status_code == 200 else {}
