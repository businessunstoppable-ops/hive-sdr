import os
from typing import Dict
from google import genai
from openai import OpenAI

class SDROrchestrator:
    def __init__(self):
        self.use_mock = True
        self.provider = None
        
        # Try OpenAI first
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                self.provider = "openai"
                self.use_mock = False
                print("✅ SDR Orchestrator using OpenAI")
                return
            except Exception as e:
                print(f"⚠️ OpenAI init failed: {e}")
        
        # Then try Gemini
        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key:
            try:
                self.gemini_client = genai.Client(api_key=gemini_key)
                self.provider = "gemini"
                self.use_mock = False
                print("✅ SDR Orchestrator using Gemini")
                return
            except Exception as e:
                print(f"⚠️ Gemini init failed: {e}")
        
        print("⚠️ No AI provider configured, using mock")

    def process_lead_workflow(self, lead, research: Dict) -> Dict:
        print(f"🎯 Processing workflow for: {lead.name}")
        score = self._score_lead_mock(lead)
        if score['score'] < 5:
            return {'skipped': True, 'reason': score['reasoning'], 'lead_name': lead.name}
        strategy = self._generate_strategy_mock(lead, score)
        email = self._create_outreach_email(lead, research, strategy)
        return {
            'lead_name': lead.name,
            'score': score,
            'strategy': strategy,
            'email_draft': email,
            'status': 'ready_for_outreach'
        }

    def _score_lead_mock(self, lead) -> Dict:
        score = 5
        if lead.rating:
            if lead.rating >= 4.5:
                score += 2
            elif lead.rating >= 4.0:
                score += 1
            elif lead.rating < 3.0:
                score -= 2
        if lead.website:
            score += 1
        if lead.total_ratings and lead.total_ratings > 100:
            score += 1
        score = min(score, 10)
        return {'score': score, 'reasoning': f"Rating {lead.rating}, reviews {lead.total_ratings}, has website"}

    def _generate_strategy_mock(self, lead, score: Dict) -> Dict:
        strategy = {'channel': 'email', 'timing': 'immediate', 'value_proposition': ''}
        if score['score'] >= 7 and lead.phone:
            strategy['channel'] = 'both'
        if score['score'] >= 8:
            strategy['timing'] = 'immediate - high priority'
        elif score['score'] <= 4:
            strategy['timing'] = 'nurture sequence'
        return strategy

    def _create_outreach_email(self, lead, research: Dict, strategy: Dict) -> str:
        insights = research.get('ai_insights', {})
        opening_line = insights.get('opening_line', f"I noticed {lead.name} has potential for improvement.")
        email = f"""Subject: Quick idea for {lead.name}

Hi there,

{opening_line}

We've helped businesses like yours implement systems that solve these exact challenges. 

**Schedule a quick 10-minute chat here:** https://yourdomain.com/book/{{lead_id}}

Or reply to this email with a time that works for you.

Best,
[Your Name]"""
        return email
