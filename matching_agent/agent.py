import os
from typing import List, Dict, Optional
from google import genai
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lead_manager.agent import LeadManagerAgent

class MatchingAgent:
    def __init__(self):
        self.manager = LeadManagerAgent()
        self.use_mock = True  # Set to False when Gemini API key is configured
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key and not self.use_mock:
                self.client = genai.Client(api_key=api_key)
                self.use_mock = False
                print("✅ MatchingAgent using Gemini")
            else:
                print("⚠️ MatchingAgent using mock mode (no API key)")
        except:
            print("⚠️ MatchingAgent using mock mode")

    def find_best_company_for_person(self, person_lead: Dict, company_leads: List[Dict]) -> Optional[str]:
        """Return the company_id that best matches the person."""
        if self.use_mock:
            return self._mock_match(person_lead, company_leads)
        # Real AI matching
        person_name = person_lead.get("name", "")
        person_title = self._extract_title_from_notes(person_lead) or ""
        person_company_name = person_lead.get("company_name", "")
        if person_company_name:
            for comp in company_leads:
                if comp["name"].lower() == person_company_name.lower():
                    return comp["id"]
        companies_text = "\n".join([f"- {c['name']}: {c.get('description', '')[:200]}" for c in company_leads])
        prompt = f"""
        Person: {person_name}
        Job Title: {person_title}
        Companies:
        {companies_text}
        Which company is most likely the employer of this person? Return only the company name.
        If none, return "NONE".
        """
        try:
            response = self.client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            best_name = response.text.strip()
            for comp in company_leads:
                if comp["name"] == best_name:
                    return comp["id"]
        except Exception as e:
            print(f"AI matching error: {e}")
        return None

    def _mock_match(self, person_lead: Dict, company_leads: List[Dict]) -> Optional[str]:
        """Simple mock matching: try to match by keyword in name or title."""
        person_name = person_lead.get("name", "").lower()
        person_title = self._extract_title_from_notes(person_lead).lower()
        for comp in company_leads:
            comp_name = comp["name"].lower()
            if comp_name in person_name or comp_name in person_title:
                return comp["id"]
        return None

    def _extract_title_from_notes(self, lead: Dict) -> str:
        for note in lead.get("notes", []):
            if note.startswith("Job Title:"):
                return note.replace("Job Title:", "").strip()
        return ""

    def run_auto_matching(self) -> Dict:
        """Run matching for all unmatched person leads."""
        all_leads = self.manager.db.get_all_leads()
        companies = [l for l in all_leads if l.get("type") == "Company"]
        persons = [l for l in all_leads if l.get("type") == "Person" and not l.get("linked_company_id")]
        matched = 0
        for person in persons:
            company_id = self.find_best_company_for_person(person, companies)
            if company_id:
                person["linked_company_id"] = company_id
                person["matched_by"] = "auto"
                self.manager.db._save()
                matched += 1
                print(f"✅ Linked {person['name']} to company {company_id}")
        return {"matched": matched, "total_persons": len(persons)}
