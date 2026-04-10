"""Test Outreach Agent with mock data"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lead_finder.google_maps_search import Lead
from research_agent.agent import ResearchAgent
from sdr_orchestrator.agent import SDROrchestrator
from outreach_agent.email_agent import EmailAgent
from outreach_agent.voice_agent import VoiceAgent

def test_email_agent():
    print("=" * 60)
    print("TESTING EMAIL AGENT")
    print("=" * 60)
    
    # Create a lead
    lead = Lead(
        name="Test Business",
        place_id="test123",
        address="123 Test St",
        phone="555-1234",
        website="https://testbusiness.com",
        rating=4.5,
        total_ratings=100,
        business_status="OPERATIONAL",
        lat=40.7128,
        lng=-74.0060
    )
    
    # Research and orchestrate
    researcher = ResearchAgent()
    research = researcher.research_lead(lead)
    
    orchestrator = SDROrchestrator()
    orchestration = orchestrator.process_lead_workflow(lead, research)
    
    # Prepare and send email
    email_agent = EmailAgent()
    prepared = email_agent.prepare_outreach(lead, orchestration)
    
    print(f"\n📧 Prepared Email:")
    print(f"   To: {prepared['to']}")
    print(f"   Subject: {prepared['subject']}")
    print(f"   Lead Score: {prepared['score']}/10")
    
    # Send email (mock)
    result = email_agent.send_email(prepared)
    print(f"\n📬 Send Result: {result['message']}")
    
    print("\n✅ Email Agent test passed!")

def test_voice_agent():
    print("\n" + "=" * 60)
    print("TESTING VOICE AGENT")
    print("=" * 60)
    
    # Create a lead
    lead = Lead(
        name="Voice Test Business",
        place_id="test456",
        address="456 Voice St",
        phone="555-5678",
        website="https://voicetest.com",
        rating=4.7,
        total_ratings=200,
        business_status="OPERATIONAL",
        lat=40.7128,
        lng=-74.0060
    )
    
    # Research
    researcher = ResearchAgent()
    research = researcher.research_lead(lead)
    
    # Create voice agent and generate script
    voice_agent = VoiceAgent()
    script = voice_agent.prepare_phone_script(lead, research, {})
    
    print(f"\n📞 Generated Phone Script:")
    print("-" * 40)
    print(script[:500] + "...")
    print("-" * 40)
    
    # Mock call
    result = voice_agent.make_call(lead.phone, script)
    print(f"\n📞 Call Result: {result['message']}")
    
    print("\n✅ Voice Agent test passed!")

def test_full_outreach_pipeline():
    print("\n" + "=" * 60)
    print("TESTING FULL OUTREACH PIPELINE")
    print("=" * 60)
    
    # Create multiple leads
    leads = [
        Lead(name="Pizza Palace", place_id="p1", address="1 Food St", phone="555-1000",
             website="https://pizzapalace.com", rating=4.6, total_ratings=300,
             business_status="OPERATIONAL", lat=0, lng=0),
        Lead(name="Clean R Us", place_id="p2", address="2 Clean St", phone="555-2000",
             website="https://cleanrus.com", rating=4.4, total_ratings=150,
             business_status="OPERATIONAL", lat=0, lng=0),
    ]
    
    email_agent = EmailAgent()
    researcher = ResearchAgent()
    orchestrator = SDROrchestrator()
    
    all_prepared = []
    
    for lead in leads:
        print(f"\n📌 Processing: {lead.name}")
        research = researcher.research_lead(lead)
        orchestration = orchestrator.process_lead_workflow(lead, research)
        
        if not orchestration.get('skipped'):
            prepared = email_agent.prepare_outreach(lead, orchestration)
            all_prepared.append(prepared)
            print(f"   ✅ Email prepared for {lead.name}")
        else:
            print(f"   ⏭️ Skipped: {lead.name}")
    
    # Send batch
    print(f"\n📬 Sending {len(all_prepared)} emails...")
    results = email_agent.send_batch(all_prepared)
    
    for result in results:
        print(f"   {result['message']}")
    
    # Show sent log
    log = email_agent.get_sent_log()
    print(f"\n📋 Sent Email Log ({len(log)} emails):")
    for entry in log[-2:]:  # Show last 2
        print(f"   - {entry['lead_name']} -> {entry['to']} at {entry['sent_at'][:19]}")
    
    print("\n✅ Full Outreach Pipeline test passed!")

if __name__ == "__main__":
    test_email_agent()
    test_voice_agent()
    test_full_outreach_pipeline()
    print("\n🎉 All Outreach Agent tests completed successfully!")
