"""Test SDR Orchestrator with mock data"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lead_finder.google_maps_search import Lead
from research_agent.agent import ResearchAgent
from sdr_orchestrator.agent import SDROrchestrator

def test_orchestrator():
    print("=" * 60)
    print("TESTING SDR ORCHESTRATOR")
    print("=" * 60)
    
    # Create mock lead
    mock_lead = Lead(
        name="Brooklyn Bakery",
        place_id="test123",
        address="456 Smith St, Brooklyn, NY",
        phone="555-5678",
        website="https://brooklynbakery.com",
        rating=4.8,
        total_ratings=320,
        business_status="OPERATIONAL",
        lat=40.7128,
        lng=-74.0060
    )
    
    # Research the lead
    print("\n📌 Phase 1: Researching lead...")
    researcher = ResearchAgent()
    research = researcher.research_lead(mock_lead)
    
    # Orchestrate
    print("\n📌 Phase 2: Orchestrating workflow...")
    orchestrator = SDROrchestrator()
    result = orchestrator.process_lead_workflow(mock_lead, research)
    
    print("\n" + "=" * 60)
    print("📋 FINAL OUTPUT")
    print("=" * 60)
    print(f"Lead: {result['lead_name']}")
    print(f"Score: {result['score']['score']}/10")
    print(f"Reasoning: {result['score']['reasoning']}")
    print(f"Channel: {result['strategy']['channel']}")
    print(f"Timing: {result['strategy']['timing']}")
    print(f"Value Prop: {result['strategy']['value_proposition'][:60]}...")
    
    print(f"\n📧 Email Draft:")
    print("-" * 40)
    print(result['email_draft'])
    print("-" * 40)
    
    print("\n✅ SDR Orchestrator test passed!")

def test_multiple_leads():
    print("\n" + "=" * 60)
    print("TESTING MULTIPLE LEADS WITH ORCHESTRATOR")
    print("=" * 60)
    
    # Create multiple mock leads with different quality scores
    mock_leads = [
        Lead(name="High Quality Co", place_id="h1", address="1 Main St", phone="555-0001", 
             website="https://highquality.com", rating=4.9, total_ratings=500, 
             business_status="OPERATIONAL", lat=0, lng=0),
        Lead(name="Medium Quality", place_id="m1", address="2 Main St", phone="555-0002", 
             website="https://medium.com", rating=4.0, total_ratings=50, 
             business_status="OPERATIONAL", lat=0, lng=0),
        Lead(name="Low Quality", place_id="l1", address="3 Main St", phone="555-0003", 
             website=None, rating=3.2, total_ratings=10, 
             business_status="OPERATIONAL", lat=0, lng=0),
    ]
    
    # Research all leads
    researcher = ResearchAgent()
    research_results = []
    for lead in mock_leads:
        research = researcher.research_lead(lead)
        research_results.append(research)
    
    # Orchestrate all leads
    orchestrator = SDROrchestrator()
    results = orchestrator.process_multiple_leads(mock_leads, research_results)
    
    print(f"\n📊 Results Summary:")
    for result in results:
        if result.get('skipped'):
            print(f"  ❌ {result['lead_name']}: SKIPPED (score < 5)")
        else:
            print(f"  ✅ {result['lead_name']}: Score {result['score']['score']}/10 - {result['strategy']['channel']}")
    
    print("\n✅ Multiple leads test passed!")

def test_low_score_skip():
    print("\n" + "=" * 60)
    print("TESTING LOW SCORE LEAD SKIP")
    print("=" * 60)
    
    # Create low quality lead
    low_lead = Lead(
        name="Poor Business",
        place_id="p1",
        address="123 Bad St",
        phone=None,
        website=None,
        rating=2.5,
        total_ratings=5,
        business_status="OPERATIONAL",
        lat=0,
        lng=0
    )
    
    researcher = ResearchAgent()
    research = researcher.research_lead(low_lead)
    
    orchestrator = SDROrchestrator()
    result = orchestrator.process_lead_workflow(low_lead, research)
    
    if result.get('skipped'):
        print(f"\n✅ Correctly skipped low quality lead")
        print(f"   Reason: {result.get('reason')}")
    else:
        print(f"\n❌ Failed to skip - lead scored {result.get('score', {}).get('score', 'unknown')}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_orchestrator()
    test_multiple_leads()
    test_low_score_skip()
    print("\n🎉 All SDR Orchestrator tests completed successfully!")
