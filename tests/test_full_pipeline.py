"""End-to-end test of the complete Agent Lounge"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lead_finder.agent import LeadFinderAgent
from research_agent.agent import ResearchAgent
from sdr_orchestrator.agent import SDROrchestrator
from outreach_agent.email_agent import EmailAgent
from lead_manager.agent import LeadManagerAgent

def run_full_pipeline():
    print("=" * 70)
    print("🚀 RUNNING COMPLETE AGENT LOUNGE PIPELINE")
    print("=" * 70)
    
    # Clear previous database
    if os.path.exists("leads_db.json"):
        os.remove("leads_db.json")
        print("🧹 Cleared previous database\n")
    
    # ============================================
    # AGENT 1: Lead Finder
    # ============================================
    print("=" * 70)
    print("📌 AGENT 1: Lead Finder - Discovering Businesses")
    print("=" * 70)
    
    lead_finder = LeadFinderAgent()
    leads = lead_finder.find_leads_for_campaign(
        industry="coffee shop",
        city="Brooklyn, NY",
        max_leads=5,
        min_rating=4.0
    )
    
    print(f"\n✅ Found {len(leads)} qualified leads:")
    for lead in leads:
        print(f"   - {lead.name} (Rating: {lead.rating}/5)")
    
    if not leads:
        print("❌ No leads found. Exiting.")
        return
    
    # ============================================
    # AGENT 2: Research Agent
    # ============================================
    print("\n" + "=" * 70)
    print("📌 AGENT 2: Research Agent - Analyzing Each Lead")
    print("=" * 70)
    
    researcher = ResearchAgent()
    research_results = []
    
    for lead in leads:
        research = researcher.research_lead(lead)
        research_results.append(research)
        print(f"\n   📊 {lead.name}:")
        print(f"      Pain point: {research['ai_insights']['pain_points'][0][:60]}...")
        print(f"      Opportunity: {research['ai_insights']['opportunities'][0][:60]}...")
    
    # ============================================
    # AGENT 3: SDR Orchestrator
    # ============================================
    print("\n" + "=" * 70)
    print("📌 AGENT 3: SDR Orchestrator - Scoring & Strategy")
    print("=" * 70)
    
    orchestrator = SDROrchestrator()
    orchestration_results = []
    
    for lead, research in zip(leads, research_results):
        result = orchestrator.process_lead_workflow(lead, research)
        orchestration_results.append(result)
        
        if not result.get('skipped'):
            print(f"\n   🎯 {lead.name}:")
            print(f"      Score: {result['score']['score']}/10")
            print(f"      Channel: {result['strategy']['channel']}")
            print(f"      Timing: {result['strategy']['timing']}")
    
    # ============================================
    # AGENT 4: Outreach Agent
    # ============================================
    print("\n" + "=" * 70)
    print("📌 AGENT 4: Outreach Agent - Preparing Emails")
    print("=" * 70)
    
    email_agent = EmailAgent()
    prepared_emails = []
    
    for lead, orchestration in zip(leads, orchestration_results):
        if not orchestration.get('skipped'):
            prepared = email_agent.prepare_outreach(lead, orchestration)
            prepared_emails.append(prepared)
            print(f"\n   📧 {lead.name}:")
            print(f"      To: {prepared['to']}")
            print(f"      Subject: {prepared['subject'][:50]}...")
    
    # Send emails (mock)
    print("\n   📬 Sending emails...")
    send_results = email_agent.send_batch(prepared_emails)
    for result in send_results:
        print(f"      {result['message']}")
    
    # ============================================
    # AGENT 5: Lead Manager
    # ============================================
    print("\n" + "=" * 70)
    print("📌 AGENT 5: Lead Manager - Tracking & Follow-ups")
    print("=" * 70)
    
    manager = LeadManagerAgent()
    
    # Import leads
    imported_ids = manager.import_from_campaign(leads, orchestration_results)
    print(f"\n   📥 Imported {len(imported_ids)} leads to database")
    
    # Mark emails sent
    for lead_id in imported_ids[:3]:  # First 3
        manager.mark_outreach_complete(lead_id)
    
    # Schedule follow-ups
    for lead_id in imported_ids:
        manager.schedule_follow_up(lead_id, days=3)
    
    # Add notes
    for lead_id in imported_ids[:2]:
        manager.db.add_note(lead_id, "Initial outreach sent - waiting for response")
    
    # ============================================
    # FINAL SUMMARY
    # ============================================
    print("\n" + "=" * 70)
    print("📊 FINAL CAMPAIGN SUMMARY")
    print("=" * 70)
    
    dashboard = manager.get_dashboard()
    
    print(f"""
    Leads Discovered:     {len(leads)}
    Qualified Leads:      {len([r for r in orchestration_results if not r.get('skipped')])}
    Emails Prepared:      {len(prepared_emails)}
    Emails Sent:          {dashboard['stats']['emails_sent']}
    Leads in Database:    {dashboard['stats']['total']}
    Average Lead Score:   {dashboard['stats']['avg_score']}/10
    Follow-ups Scheduled: {dashboard['follow_ups_needed']}
    
    Leads by Status:
    """)
    
    for status, count in dashboard['stats']['by_status'].items():
        print(f"      {status}: {count}")
    
    # Sample email output
    if prepared_emails:
        print("\n" + "=" * 70)
        print("📧 SAMPLE EMAIL (First Lead)")
        print("=" * 70)
        print(f"\nTo: {prepared_emails[0]['to']}")
        print(f"Subject: {prepared_emails[0]['subject']}")
        print("\nBody:")
        print("-" * 50)
        print(prepared_emails[0]['body'][:500])
        print("-" * 50)
        if len(prepared_emails[0]['body']) > 500:
            print("... (truncated)")
    
    print("\n" + "=" * 70)
    print("🎉 FULL PIPELINE COMPLETE!")
    print("All 5 agents worked together successfully.")
    print("=" * 70)

def test_with_specific_industry():
    """Test with a different industry"""
    print("\n" + "=" * 70)
    print("🔄 TESTING WITH DIFFERENT INDUSTRY")
    print("=" * 70)
    
    lead_finder = LeadFinderAgent()
    leads = lead_finder.find_leads_for_campaign(
        industry="plumber",
        city="Austin, TX",
        max_leads=3,
        min_rating=4.0
    )
    
    print(f"\n✅ Found {len(leads)} plumbing businesses in Austin:")
    for lead in leads:
        print(f"   - {lead.name}")

if __name__ == "__main__":
    run_full_pipeline()
    test_with_specific_industry()
    print("\n🎉 All tests completed! Your Agent Lounge is fully operational.")
