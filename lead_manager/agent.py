from utils.industry_detector import detect_industry_from_website
import json
from utils.industry_detector import detect_industry_from_website
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    NEGOTIATING = "negotiating"
    WON = "won"
    LOST = "lost"
    FOLLOW_UP = "follow_up"

class LeadDatabase:
    """Simple JSON-based database for storing leads"""
    
    def __init__(self, db_path: str = "leads_db.json"):
        self.db_path = db_path
        self.leads = self._load()
        self._rebuild_indices()
    
    def _load(self) -> Dict:
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save(self):
        self._rebuild_indices()
        with open(self.db_path, 'w') as f:
            json.dump(self.leads, f, indent=2)
    
    def _rebuild_indices(self):
        """Rebuild indices after loading or after many changes."""
        self._index_status = {}
        self._index_type = {}
        self._index_created = []
        for lid, lead in self.leads.items():
            status = lead.get("status", "new")
            self._index_status.setdefault(status, set()).add(lid)
            typ = lead.get("type", "Company")
            self._index_type.setdefault(typ, set()).add(lid)
            self._index_created.append((lead["created_at"], lid))
        self._index_created.sort(key=lambda x: x[0], reverse=True)
    
    def add_lead(self, lead_data: Dict, lead_type: str = "Company", linked_company_id: str = None, auto_detect_industry: bool = True) -> str:
        import uuid
        lead_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        self.leads[lead_id] = {
            'id': lead_id,
            'name': lead_data.get('name', 'Unknown'),
            'email': lead_data.get('email', ''),
            'website': lead_data.get('website', ''),
            'phone': lead_data.get('phone', ''),
            'rating': lead_data.get('rating', 0),
            'score': lead_data.get('score', 0),

            'category': lead_data.get('category', ''),
            'role': lead_data.get('role', ''),
            'keywords': lead_data.get('keywords', ''),
            'industry': lead_data.get('industry', '') or (auto_detect_industry and lead_data.get('website') and detect_industry_from_website(lead_data['website']) or ''),
            'industry': lead_data.get('industry', '') or (auto_detect_industry and lead_data.get('website') and detect_industry_from_website(lead_data['website']) or ''),
            'type': lead_type,
            'linked_company_id': linked_company_id,
            'matched_by': 'manual' if linked_company_id else None,
            'status': 'new',
            'notes': [],
            'email_sent': False,
            'email_sent_at': None,
            'email_count': 0,
            'follow_up_date': None,
            'created_at': now,
            'updated_at': now
        }
        self._save()
        return lead_id
    
    def update_status(self, lead_id: str, status: str):
        if lead_id in self.leads:
            self.leads[lead_id]['status'] = status
            self.leads[lead_id]['updated_at'] = datetime.now().isoformat()
            self._save()
    
    def mark_email_sent(self, lead_id: str):
        if lead_id in self.leads:
            self.leads[lead_id]['email_sent'] = True
            self.leads[lead_id]['email_sent_at'] = datetime.now().isoformat()
            self.leads[lead_id]['updated_at'] = datetime.now().isoformat()
            self._save()
    
    def schedule_follow_up(self, lead_id: str, days_from_now: int = 3):
        if lead_id in self.leads:
            follow_up_date = (datetime.now() + timedelta(days=days_from_now)).isoformat()
            self.leads[lead_id]['follow_up_date'] = follow_up_date
            self.leads[lead_id]['status'] = LeadStatus.FOLLOW_UP.value
            self.leads[lead_id]['updated_at'] = datetime.now().isoformat()
            self._save()
    
    def add_note(self, lead_id: str, note: str):
        if lead_id in self.leads:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            full_note = f"[{timestamp}] {note}"
            self.leads[lead_id]['notes'].append(full_note)
            self.leads[lead_id]['updated_at'] = datetime.now().isoformat()
            self._save()
    
    def get_lead(self, lead_id: str) -> Optional[Dict]:
        return self.leads.get(lead_id)
    
    def get_all_leads(self) -> List[Dict]:
        return list(self.leads.values())
    
    def get_follow_ups_needed(self) -> List[Dict]:
        now = datetime.now()
        needed = []
        for lead in self.leads.values():
            if lead.get('follow_up_date'):
                follow_date = datetime.fromisoformat(lead['follow_up_date'])
                if follow_date <= now:
                    needed.append(lead)
        return needed
    
    def get_stats(self) -> Dict:
        leads = self.get_all_leads()
        if not leads:
            return {'total': 0, 'by_status': {}, 'avg_score': 0}
        by_status = {}
        for lead in leads:
            status = lead.get('status', 'unknown')
            by_status[status] = by_status.get(status, 0) + 1
        avg_score = sum(l.get('score', 0) for l in leads) / len(leads)
        return {
            'total': len(leads),
            'by_status': by_status,
            'avg_score': round(avg_score, 1),
            'emails_sent': sum(1 for l in leads if l.get('email_sent'))
        }
    
    def clear_all(self):
        self.leads = {}
        self._save()

# For backward compatibility with lead_manager/agent.py that uses LeadManagerAgent
class LeadManagerAgent:
    def __init__(self, db_path: str = "leads_db.json"):
        self.db = LeadDatabase(db_path)
    
    def get_dashboard(self):
        return {"stats": self.db.get_stats(), "follow_ups_needed": len(self.db.get_follow_ups_needed())}
    
    def update_lead_status(self, lead_id: str, status: str):
        self.db.update_status(lead_id, status)
    
    # Delegate other methods as needed
    def add_lead(self, *args, **kwargs):
        return self.db.add_lead(*args, **kwargs)
    
    def get_lead(self, lead_id):
        return self.db.get_lead(lead_id)
    
    def get_all_leads(self):
        return self.db.get_all_leads()
    
    def add_note(self, lead_id, note):
        self.db.add_note(lead_id, note)
    
    # etc.
