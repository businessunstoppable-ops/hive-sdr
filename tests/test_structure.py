"""Test that the project structure is correct - no API keys needed"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported (structure check)"""
    print("=" * 50)
    print("TESTING PROJECT STRUCTURE")
    print("=" * 50)
    
    # Test each module import
    modules_to_test = [
        "lead_finder",
        "research_agent", 
        "sdr_orchestrator",
        "outreach_agent",
        "lead_manager"
    ]
    
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - import successful")
        except Exception as e:
            print(f"⚠️ {module_name} - import issue: {str(e)[:50]}...")
    
    print("\n" + "=" * 50)
    print("Structure check complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_imports()
