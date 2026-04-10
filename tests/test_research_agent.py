"""Test Research Agent with mock data"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lead_finder.google_maps_search import Lead
from research_agent.agent import ResearchAgent

def test_research_agent():
    print("=" * 50)
    print("TESTING RESEARCH AGENT")
    print("=" * 50)
    
    # Create a mock lead
    mock_lead = Lead(
        name="Joe's Coffee Shop",
        place_id="test123",
        address="123 Main St, Brooklyn, NY",
        phone="555-1234",
        website="https://joescoffee.com",
        rating=4.7,
        total_ratings=245,
        business_status="OPERATIONAL",
        lat=40.7128,
        lng=-74.0060
    )
    
    # Create research agent
    agent = ResearchAgent()
    
    # Research the lead
    result = agent.research_lead(mock_lead)
    
    print(f"\n📊 Research Results:")
    print(f"Lead: {result['lead_name']}")
    print(f"Website: {result['website']}")
    
    print(f"\n📝 AI Insights:")
    insights = result['ai_insights']
    print(f"Pain points: {insights['pain_points'][0]}")
    print(f"Opportunities: {insights['opportunities'][0]}")
    print(f"Opening line: {insights['opening_line']}")
    
    print("\n" + "=" * 50)
    print("✅ Research Agent test passed!")
    print("=" * 50)

def test_multiple_leads():
    print("\n" + "=" * 50)
    print("TESTING MULTIPLE LEADS RESEARCH")
    print("=" * 50)
    
    # Create multiple mock leads
    mock_leads = [
        Lead(name="Pizza Place", place_id="p1", address="1 Main St", phone="555-0001", 
             website="https://pizza.com", rating=4.5, total_ratings=100, 
             business_status="OPERATIONAL", lat=0, lng=0),
        Lead(name="Dry Cleaner", place_id="p2", address="2 Main St", phone="555-0002", 
             website="https://dryclean.com", rating=4.3, total_ratings=80, 
             business_status="OPERATIONAL", lat=0, lng=0),
        Lead(name="Gym", place_id="p3", address="3 Main St", phone="555-0003", 
             website="https://gym.com", rating=4.6, total_ratings=200, 
             business_status="OPERATIONAL", lat=0, lng=0),
    ]
    
    agent = ResearchAgent()
    results = agent.research_multiple_leads(mock_leads)
    
    print(f"\n📊 Researched {len(results)} leads:")
    for result in results:
        print(f"  - {result['lead_name']}: {result['ai_insights']['pain_points'][0][:50]}...")
    
    print("\n✅ Multiple leads test passed!")
    print("=" * 50)

if __name__ == "__main__":
    test_research_agent()
    test_multiple_leads()
    print("\n🎉 All Research Agent tests completed successfully!")
