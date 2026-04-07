# tests/test_lead_finder.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lead_finder.agent import LeadFinderAgent

def test_lead_finder():
    print("=" * 50)
    print("TESTING LEAD FINDER AGENT")
    print("=" * 50)
    
    agent = LeadFinderAgent()
    
    leads = agent.find_leads_for_campaign(
        industry="coffee shop",
        city="Brooklyn, NY",
        max_leads=5,
        min_rating=4.0
    )
    
    print(f"\n📋 Results:")
    for i, lead in enumerate(leads, 1):
        print(f"{i}. {lead.name} - Rating: {lead.rating}")
        print(f"   Website: {lead.website}")
        print(f"   Address: {lead.address[:50]}...")
        
    print(f"\n✅ Test complete! Found {len(leads)} leads.")
    print(f"📊 API calls made: {agent.finder.api_calls_count}")

if __name__ == "__main__":
    test_lead_finder()
