# sdr/main.py
"""
Agent Lounge - Complete SDR System
Entry point for the multi-agent system
"""

import os
from dotenv import load_dotenv
from lead_finder.agent import LeadFinderAgent
from research_agent.agent import ResearchAgent
from sdr_orchestrator.agent import SDROrchestrator
from outreach_agent.email_agent import EmailAgent

load_dotenv()

def run_campaign(industry: str, city: str, max_leads: int = 10):
    """
    Run a complete SDR campaign
    
    Args:
        industry: Type of business (e.g., "plumber", "restaurant")
        city: Target city (e.g., "Austin, TX")
        max_leads: Maximum leads to process
    """
    print("\n" + "=" * 70)
    print(f"🚀 STARTING SDR CAMPAIGN: {industry} in {city}")
    print("=" * 70)
    
    # Step 1: Find leads
    print("\n📌 PHASE 1: Lead Discovery")
    finder = LeadFinderAgent()
    leads = finder.find_leads_for_campaign(industry, city, max_leads)
    print(f"   Found {len(leads)} qualified leads")
    
    # Step 2 & 3: Research and orchestrate for each lead
    print("\n📌 PHASE 2 & 3: Research + Orchestration")
    researcher = ResearchAgent()
    orchestrator = SDROrchestrator()
    
    results = []
    for i, lead in enumerate(leads, 1):
        print(f"\n   Processing lead {i}/{len(leads)}: {lead.name}")
        
        research = researcher.research_lead(lead)
        result = orchestrator.process_lead_workflow(lead, research)
        
        if not result.get('skipped', False):
            results.append(result)
            print(f"   ✅ Score: {result['score'].get('score', 'N/A')}/10")
        else:
            print(f"   ⏭️ Skipped: {result.get('reason', 'Low quality')}")
    
    # Step 4: Prepare outreach
    print("\n📌 PHASE 4: Outreach Preparation")
    email_agent = EmailAgent()
    
    for result in results:
        email_prep = email_agent.prepare_outreach(
            leads[results.index(result)], 
            result
        )
        result['email_ready'] = email_prep
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 CAMPAIGN SUMMARY")
    print("=" * 70)
    print(f"Total leads discovered: {len(leads)}")
    print(f"Qualified for outreach: {len(results)}")
    print(f"Conversion rate: {len(results)/len(leads)*100:.1f}%")
    
    return results

if __name__ == "__main__":
    # Example: Find plumbing businesses in Austin
    results = run_campaign("plumber", "Austin, TX", max_leads=5)
    
    # Print email drafts
    print("\n📧 EMAIL DRAFTS READY:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['lead_name']}")
        print(f"   Score: {result['score']['score']}/10")
        print(f"   Email: {result['email_ready']['subject']}")