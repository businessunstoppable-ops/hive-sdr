import os
import json
from typing import Dict
from google import genai
from openai import OpenAI

class ResearchAgent:
    def __init__(self):
        self.use_mock = True
        self.provider = None
        # Load industry templates
        self.industry_templates = {}
        try:
            with open('data/industries.json', 'r') as f:
                self.industry_templates = json.load(f)
        except:
            print("⚠️ Could not load industry templates, using fallback")
        
        # Try OpenAI first
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                self.provider = "openai"
                self.use_mock = False
                print("✅ ResearchAgent using OpenAI")
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
                print("✅ ResearchAgent using Gemini")
                return
            except Exception as e:
                print(f"⚠️ Gemini init failed: {e}")
        
        print("⚠️ No AI provider configured, using industry templates + mock")

    def research_lead(self, lead) -> Dict:
        # Handle both dictionary and Lead object
        if hasattr(lead, 'name'):
            # It's a Lead object
            lead_name = lead.name
            lead_rating = lead.rating
            lead_total_ratings = lead.total_ratings
            lead_website = lead.website
            lead_industry = getattr(lead, 'industry', '')
        else:
            # It's a dictionary
            lead_name = lead.get('name', '')
            lead_rating = lead.get('rating', 0)
            lead_total_ratings = lead.get('total_ratings', 0)
            lead_website = lead.get('website', '')
            lead_industry = lead.get('industry', '')
        
        print(f"🔬 Researching: {lead_name}")
        industry = lead_industry.lower() if lead_industry else ''
        # Try to use industry template first
        if industry and industry in self.industry_templates:
            template = self.industry_templates[industry]
            insights = {
                'pain_points': template['pain_points'],
                'opportunities': template['opportunities'],
                'opening_line': template['opening_line'],
                'business_summary': f"{lead_name} is a {industry} business with rating {lead_rating}/5.",
                'recommended_approach': "Use the industry‑specific email template."
            }
            print(f"   Using industry template for '{industry}'")
            return {'lead_name': lead_name, 'website': lead_website, 'ai_insights': insights}
        else:
            # Fallback to AI or mock
            if not self.use_mock:
                insights = self._generate_ai_insights(lead_name, lead_rating, lead_total_ratings, lead_website, industry)
            else:
                insights = self._generate_mock_insights(lead_name, lead_rating, industry)
            return {'lead_name': lead_name, 'website': lead_website, 'ai_insights': insights}

    def _generate_ai_insights(self, name, rating, total_ratings, website, industry) -> Dict:
        prompt = f"""
        Analyze this business and identify specific sales opportunities:

        Business Name: {name}
        Rating: {rating}/5 from {total_ratings} reviews
        Website: {website}
        Industry (if known): {industry}

        Provide a JSON response with:
        1. Three potential pain points (specific to this business).
        2. Two opportunities where our service could help.
        3. One personalized opening line for outreach.
        """
        try:
            if self.provider == "openai":
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                text = response.choices[0].message.content
            else:  # gemini
                response = self.gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )
                text = response.text
            start = text.find('{')
            end = text.rfind('}') + 1
            return json.loads(text[start:end])
        except Exception as e:
            print(f"AI error: {e}, falling back to mock")
            return self._generate_mock_insights(name, rating, industry)

    def _generate_mock_insights(self, name, rating, industry) -> Dict:
        # Use default template if no industry
        default = self.industry_templates.get('default', {
            'pain_points': ['customer retention', 'online visibility', 'operational efficiency'],
            'opportunities': ['automated marketing', 'customer feedback system', 'streamlined booking'],
            'opening_line': f"I noticed {name} has potential for growth. We've helped similar businesses improve their results."
        })
        return default
