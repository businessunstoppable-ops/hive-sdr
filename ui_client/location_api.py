"""Location autocomplete using Google Places API"""

from fastapi import APIRouter, Query
from typing import List, Dict
import requests
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/locations", tags=["locations"])

@router.get("/autocomplete")
async def autocomplete_location(input: str = Query(..., min_length=2)):
    """Get location suggestions based on user input"""
    
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    
    if not api_key or len(api_key) < 20:
        # Fallback to common cities if API key not available
        return fallback_suggestions(input)
    
    try:
        # Use Google Places Autocomplete API
        url = "https://places.googleapis.com/v1/places:autocomplete"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key
        }
        
        payload = {
            "input": input,
            "includeQueryPredictions": True,
            "locationBias": {"circle": {"center": {"latitude": 40.7128, "longitude": -74.0060}, "radius": 500000.0}}
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            suggestions = []
            
            # Extract place predictions
            for place in data.get('suggestions', []):
                place_prediction = place.get('placePrediction', {})
                text = place_prediction.get('text', {}).get('text', '')
                if text:
                    suggestions.append({
                        'name': text,
                        'description': place_prediction.get('description', text)
                    })
            
            # Also add place predictions (cities, neighborhoods)
            for place in data.get('suggestions', []):
                query_prediction = place.get('queryPrediction', {})
                text = query_prediction.get('text', {}).get('text', '')
                if text:
                    suggestions.append({
                        'name': text,
                        'description': query_prediction.get('description', text)
                    })
            
            # Remove duplicates and limit
            seen = set()
            unique_suggestions = []
            for s in suggestions:
                if s['name'] not in seen:
                    seen.add(s['name'])
                    unique_suggestions.append(s)
            
            return unique_suggestions[:10]
        else:
            return fallback_suggestions(input)
            
    except Exception as e:
        print(f"Location autocomplete error: {e}")
        return fallback_suggestions(input)


def fallback_suggestions(input_text: str) -> List[Dict]:
    """Fallback list of common cities when API is unavailable"""
    cities = [
        {"name": "Amsterdam, Netherlands", "description": "Amsterdam, Netherlands"},
        {"name": "Rotterdam, Netherlands", "description": "Rotterdam, Netherlands"},
        {"name": "Utrecht, Netherlands", "description": "Utrecht, Netherlands"},
        {"name": "The Hague, Netherlands", "description": "The Hague, Netherlands"},
        {"name": "New York, NY, USA", "description": "New York, New York, USA"},
        {"name": "Los Angeles, CA, USA", "description": "Los Angeles, California, USA"},
        {"name": "Chicago, IL, USA", "description": "Chicago, Illinois, USA"},
        {"name": "Austin, TX, USA", "description": "Austin, Texas, USA"},
        {"name": "London, United Kingdom", "description": "London, United Kingdom"},
        {"name": "Paris, France", "description": "Paris, France"},
        {"name": "Berlin, Germany", "description": "Berlin, Germany"},
        {"name": "Madrid, Spain", "description": "Madrid, Spain"},
        {"name": "Barcelona, Spain", "description": "Barcelona, Spain"},
        {"name": "Milan, Italy", "description": "Milan, Italy"},
        {"name": "Rome, Italy", "description": "Rome, Italy"},
        {"name": "Vienna, Austria", "description": "Vienna, Austria"},
        {"name": "Prague, Czech Republic", "description": "Prague, Czech Republic"},
        {"name": "Budapest, Hungary", "description": "Budapest, Hungary"},
        {"name": "Warsaw, Poland", "description": "Warsaw, Poland"},
        {"name": "Copenhagen, Denmark", "description": "Copenhagen, Denmark"},
        {"name": "Stockholm, Sweden", "description": "Stockholm, Sweden"},
        {"name": "Oslo, Norway", "description": "Oslo, Norway"},
        {"name": "Helsinki, Finland", "description": "Helsinki, Finland"},
        {"name": "Dublin, Ireland", "description": "Dublin, Ireland"},
        {"name": "Brussels, Belgium", "description": "Brussels, Belgium"},
        {"name": "Zurich, Switzerland", "description": "Zurich, Switzerland"},
        {"name": "Munich, Germany", "description": "Munich, Germany"},
        {"name": "Frankfurt, Germany", "description": "Frankfurt, Germany"},
        {"name": "Hamburg, Germany", "description": "Hamburg, Germany"},
        {"name": "Cologne, Germany", "description": "Cologne, Germany"},
    ]
    
    # Filter cities matching input
    input_lower = input_text.lower()
    matches = [c for c in cities if input_lower in c['name'].lower()]
    
    # Return matches, or top 10 if no matches
    if matches:
        return matches[:10]
    else:
        return cities[:10]
