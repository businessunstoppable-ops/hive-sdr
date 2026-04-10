#!/usr/bin/env python
"""Pre-launch validation script for HIVE-SDR"""

import os
import sys
import json
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test all modules can be imported"""
    print("\n" + "="*60)
    print("TEST 1: Module Imports")
    print("="*60)
    
    modules = [
        "lead_finder",
        "research_agent", 
        "sdr_orchestrator",
        "outreach_agent",
        "lead_manager",
        "ui_client.working_app"
    ]
    
    all_ok = True
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {str(e)[:50]}")
            all_ok = False
    
    return all_ok

def test_data_directory():
    """Test data directory is writable"""
    print("\n" + "="*60)
    print("TEST 2: Data Directory")
    print("="*60)
    
    test_dir = "hive_data"
    try:
        os.makedirs(test_dir, exist_ok=True)
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print(f"  ✅ {test_dir} is writable")
        return True
    except Exception as e:
        print(f"  ❌ Cannot write to {test_dir}: {e}")
        return False

def test_agent_creation():
    """Test agents can be instantiated"""
    print("\n" + "="*60)
    print("TEST 3: Agent Instantiation")
    print("="*60)
    
    agents = [
        ("LeadFinderAgent", "lead_finder.agent"),
        ("ResearchAgent", "research_agent.agent"),
        ("SDROrchestrator", "sdr_orchestrator.agent"),
        ("EmailAgent", "outreach_agent.email_agent"),
        ("LeadManagerAgent", "lead_manager.agent")
    ]
    
    all_ok = True
    for agent_name, module_path in agents:
        try:
            module = importlib.import_module(module_path)
            agent_class = getattr(module, agent_name)
            agent = agent_class()
            print(f"  ✅ {agent_name} created successfully")
        except Exception as e:
            print(f"  ❌ {agent_name}: {str(e)[:50]}")
            all_ok = False
    
    return all_ok

def test_campaign_flow():
    """Test a minimal campaign flow (no API calls)"""
    print("\n" + "="*60)
    print("TEST 4: Campaign Flow (Mock Mode)")
    print("="*60)
    
    try:
        from lead_finder.agent import LeadFinderAgent
        from research_agent.agent import ResearchAgent
        from sdr_orchestrator.agent import SDROrchestrator
        
        finder = LeadFinderAgent()
        leads = finder.find_leads_for_campaign("coffee shop", "Brooklyn, NY", max_leads=2)
        
        if not leads:
            print("  ⚠️ No leads found (mock mode - expected)")
        else:
            print(f"  ✅ Found {len(leads)} leads")
        
        researcher = ResearchAgent()
        orchestrator = SDROrchestrator()
        
        for lead in leads:
            research = researcher.research_lead(lead)
            result = orchestrator.process_lead_workflow(lead, research)
            if not result.get('skipped'):
                print(f"  ✅ Processed: {lead.name} (Score: {result['score']['score']})")
        
        return True
    except Exception as e:
        print(f"  ❌ Campaign flow failed: {e}")
        return False

def test_dashboard_import():
    """Test the dashboard can be imported"""
    print("\n" + "="*60)
    print("TEST 5: Dashboard Import")
    print("="*60)
    
    try:
        from ui_client.working_app import app
        print("  ✅ Dashboard app imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Dashboard import failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🐝 HIVE-SDR PRE-LAUNCH VALIDATION")
    print("="*60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Data Directory", test_data_directory),
        ("Agent Creation", test_agent_creation),
        ("Campaign Flow", test_campaign_flow),
        ("Dashboard Import", test_dashboard_import)
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All tests passed! HIVE-SDR is ready for launch.")
    else:
        print("⚠️ Some tests failed. Please fix before launching.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
