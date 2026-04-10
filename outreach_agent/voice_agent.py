# outreach_agent/voice_agent.py
from typing import Dict

class VoiceAgent:
    """
    Handles AI-powered phone calls.
    (Requires ElevenLabs API key for real calls)
    """
    
    def __init__(self):
        self.enabled = False
        self.api_key = None
        
    def configure_elevenlabs(self, api_key: str):
        """Configure ElevenLabs API for real voice calls"""
        self.api_key = api_key
        self.enabled = True
        print("✅ ElevenLabs configured. Voice calls are now available.")
    
    def prepare_phone_script(self, lead, research: Dict, orchestration: Dict) -> str:
        """Generate a phone script from research data"""
        
        insights = research.get('ai_insights', {})
        pain_point = insights.get('pain_points', ['improving their business'])[0]
        opportunity = insights.get('opportunities', ['helping businesses grow'])[0]
        
        script = f"""
=== PHONE SCRIPT FOR {lead.name} ===

INTRO:
"Hello, may I speak with the owner or manager please?"

(When connected)

"This is [Your Name] from [Your Company]. I'm calling because I noticed {lead.name} has great reviews online."

PAIN POINT:
"I noticed that many businesses like yours struggle with {pain_point.lower()}."

SOLUTION:
"We've helped similar businesses {opportunity.lower()}."

CALL TO ACTION:
"Would you have 5-10 minutes this week for a quick call to discuss how this might work for {lead.name}?"

OBJECTION HANDLING:
- "Not interested": "I understand. Would it be okay if I send you a quick email with more information?"
- "Too busy": "I completely understand. When would be a better time to reach out?"
- "Send me info": "Absolutely. What's the best email address to send that to?"

CLOSING:
"Great, I'll send that over. Thank you for your time, and have a great day."

=== END SCRIPT ===
"""
        return script
    
    def make_call(self, phone_number: str, script: str) -> Dict:
        """Mock make a phone call (real API call will be added later)"""
        
        if not self.enabled:
            print("⚠️ VoiceAgent not configured - running in mock mode")
        
        print(f"📞 MOCK CALL:")
        print(f"   Number: {phone_number}")
        print(f"   Script preview: {script[:100]}...")
        
        return {
            'success': True,
            'mock_mode': True,
            'phone_number': phone_number,
            'message': 'Call would be made here with ElevenLabs API'
        }
