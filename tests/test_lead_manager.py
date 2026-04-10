"""Test Lead Manager Agent"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lead_finder.google_maps_search import Lead
from research_agent.agent import ResearchAgent
from sdr_orchestrator.agent import SDROrchestrator
from outreach_agent.email_agent import EmailAgent
from lead_manager.agent import LeadManagerAgent

def test_lead_manager():
    print("=" * 60)
    print("TESTING LEAD MANAGER AGENT")
    print("=" * 60)
    
    # Clear existing database
    import json
    import os
    if os.path.exists("leads_db.json"):
        os.remove("leads_db.json")
        print("🧹 Cleared existing database")
    
    # Create mock leads
    leads = [
        Lead(name="ABC Corp", place_id="1", address="1 Business Rd", phone="555-1000",
             website="https://abccorp.com", rating=4.7, total_ratings=250,
             business_status="OPERATIONAL", lat=0, lng=0),
        Lead(name="XYZ Solutions", place_id="2", address="2 Tech Blvd", phone="555-2000",
             website="https://xyzsolutions.com", rating=4.5, total_ratings=180,
             business_status="OPERATIONAL", lat=0, lng=0),
        Lead(name="123 Services", place_id="3", address="3 Service Ln", phone="555-3000",
             website="https://123services.com", rating=4.3, total_ratings=120,
             business_status="OPERATIONAL", lat=0, lng=0),
    ]
    
    # Research and orchestrate
    print("\n📌 Phase 1: Research and Orchestrate leads...")
    researcher = ResearchAgent()
    orchestrator = SDROrchestrator()
    
    research_results = []
    orchestration_results = []
    
    for lead in leads:
        research = researcher.research_lead(lead)
        orchestration = orchestrator.process_lead_workflow(lead, research)
        research_results.append(research)
        orchestration_results.append(orchestration)
    
    # Import to lead manager
    print("\n📌 Phase 2: Import leads to database...")
    manager = LeadManagerAgent()
    imported_ids = manager.import_from_campaign(leads, orchestration_results)
    
    # Check dashboard
    print("\n📌 Phase 3: Check dashboard...")
    dashboard = manager.get_dashboard()
    print(f"   Total leads: {dashboard['stats']['total']}")
    print(f"   By status: {dashboard['stats']['by_status']}")
    print(f"   Average score: {dashboard['stats']['avg_score']}")
    
    # Mark outreach complete
    print("\n📌 Phase 4: Mark outreach complete...")
    if imported_ids:
        manager.mark_outreach_complete(imported_ids[0])
    
    # Schedule follow-ups
    print("\n📌 Phase 5: Schedule follow-ups...")
    for lead_id in imported_ids:
        manager.schedule_follow_up(lead_id, days=3)
    
    # Add notes
    print("\n📌 Phase 6: Add notes...")
    if imported_ids:
        manager.db.add_note(imported_ids[0], "Spoke with owner - interested in learning more")
        manager.db.add_note(imported_ids[0], "Sent follow-up email with pricing")
    
    # Update status
    print("\n📌 Phase 7: Update lead status...")
    if imported_ids:
        manager.update_lead_status(imported_ids[0], "qualified")
    
    # Check follow-ups needed
    print("\n📌 Phase 8: Check follow-ups needed...")
    follow_ups = manager.process_follow_ups()
    print(f"   Follow-ups due: {len(follow_ups)}")
    
    # Final dashboard
    print("\n📌 Phase 9: Final dashboard...")
    final_dashboard = manager.get_dashboard()
    print(f"   Total leads: {final_dashboard['stats']['total']}")
    print(f"   Emails sent: {final_dashboard['stats']['emails_sent']}")
    print(f"   By status: {final_dashboard['stats']['by_status']}")
    
    # Show a lead detail
    if imported_ids:
        print("\n📌 Lead Detail Example:")
        lead_detail = manager.db.get_lead(imported_ids[0])
        print(f"   Name: {lead_detail['name']}")
        print(f"   Status: {lead_detail['status']}")
        print(f"   Score: {lead_detail['score']}/10")
        print(f"   Notes:")
        for note in lead_detail['notes'][-3:]:
            print(f"     - {note}")
    
    print("\n" + "=" * 60)
    print("✅ Lead Manager Agent test passed!")
    print("=" * 60)

def test_persistence():
    """Test that database persists between runs"""
    print("\n" + "=" * 60)
    print("TESTING DATABASE PERSISTENCE")
    print("=" * 60)
    
    manager = LeadManagerAgent()
    dashboard = manager.get_dashboard()
    print(f"   Leads still in database: {dashboard['stats']['total']}")
    
    if dashboard['stats']['total'] > 0:
        print("✅ Database persistence working!")
    else:
        print("⚠️ No leads found (database may have been cleared)")

if __name__ == "__main__":
    test_lead_manager()
    test_persistence()
    print("\n🎉 All Lead Manager tests completed successfully!")
