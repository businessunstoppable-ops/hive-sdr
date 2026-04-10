from dataclasses import dataclass, asdict
from typing import List, Optional
import json
import googlemaps

@dataclass
class Lead:
    name: str
    place_id: str
    address: str
    phone: Optional[str]
    website: Optional[str]
    rating: Optional[float]
    total_ratings: Optional[int]
    business_status: str
    lat: float
    lng: float

    def to_dict(self):
        return asdict(self)

class GoogleMapsLeadFinder:
    def __init__(self, api_key: str):
        self.client = googlemaps.Client(key=api_key)
        self.api_calls_count = 0

    def search_by_keyword(self, keyword: str, location: str, max_results: int = 50) -> List[Lead]:
        leads = []
        next_page_token = None
        while len(leads) < max_results:
            result = self.client.places(query=f"{keyword} in {location}", page_token=next_page_token)
            self.api_calls_count += 1
            for place in result.get('results', []):
                details = self._get_place_details(place['place_id'])
                if details:
                    lead = Lead(
                        name=place.get('name', ''),
                        place_id=place['place_id'],
                        address=place.get('formatted_address', ''),
                        phone=details.get('formatted_phone_number'),
                        website=details.get('website'),
                        rating=place.get('rating'),
                        total_ratings=place.get('user_ratings_total'),
                        business_status=place.get('business_status', 'OPERATIONAL'),
                        lat=place['geometry']['location']['lat'],
                        lng=place['geometry']['location']['lng']
                    )
                    leads.append(lead)
                if len(leads) >= max_results:
                    break
            next_page_token = result.get('next_page_token')
            if next_page_token:
                import time
                time.sleep(2)
            else:
                break
        return leads

    def _get_place_details(self, place_id: str) -> dict:
        try:
            result = self.client.place(place_id, fields=['formatted_phone_number', 'website'])
            self.api_calls_count += 1
            return result.get('result', {})
        except Exception as e:
            print(f"Error getting details: {e}")
            return {}

    def save_leads_to_file(self, leads: List[Lead], filename: str = "leads.json"):
        with open(filename, 'w') as f:
            json.dump([lead.to_dict() for lead in leads], f, indent=2)
        print(f"Saved {len(leads)} leads to {filename}")
