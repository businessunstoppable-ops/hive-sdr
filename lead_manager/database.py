# lead_manager/database.py
import json
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

@dataclass
class StoredLead:
    """Lead stored in the database"""
    id: str
    name: str
    website: str
    phone: Optional[str]
    rating: float
    score: int
    status: str
    notes: List[str]
    email_sent: bool
    email_sent_at: Optional[str]
    follow_up_date: Optional[str]
    created_at: str
    updated_at: str

class LeadDatabase:
    """Simple JSON-based database for storing leads"""
    
    def __init__(self, db_path: str = "leads_db.json"):
        self.db_path = db_path
        self.leads = self._load()
    
    def _load(self) -> Dict:
        """Load leads from JSON file"""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save(self):
        """Save leads to JSON file"""
        with open(self.db_path, 'w') as f:
            json.dump(self.leads, f, indent=2)
    
    def add_lead(self, lead_data: Dict) -> str:
        """Add a new lead to the database"""
        import uuid
        lead_id = str(uuid.uuid4())[:8]
        
        self.leads[lead_id] = {
            'id': lead_id,
            'name': lead_data.get('name', 'Unknown'),
            'website': lead_data.get('website', ''),
            'phone': lead_data.get('phone', ''),
            'rating': lead_data.get('rating', 0),
            'score': lead_data.get('score', 0),
            'status': LeadStatus.NEW.value,
            'notes': [],
            'email_sent': False,
            'email_sent_at': None,
            'follow_up_date': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        self._save()
        return lead_id
    
    def update_status(self, lead_id: str, status: str):
        """Update lead status"""
        if lead_id in self.leads:
            self.leads[lead_id]['status'] = status
            self.leads[lead_id]['updated_at'] = datetime.now().isoformat()
            self._save()
    
    def mark_email_sent(self, lead_id: str):
        """Mark that an email was sent to this lead"""
        if lead_id in self.leads:
            self.leads[lead_id]['email_sent'] = True
            self.leads[lead_id]['email_sent_at'] = datetime.now().isoformat()
            self.leads[lead_id]['updated_at'] = datetime.now().isoformat()
            self._save()
    
    def schedule_follow_up(self, lead_id: str, days_from_now: int = 3):
        """Schedule a follow-up for a lead"""
        if lead_id in self.leads:
            follow_up_date = (datetime.now() + timedelta(days=days_from_now)).isoformat()
            self.leads[lead_id]['follow_up_date'] = follow_up_date
            self.leads[lead_id]['status'] = LeadStatus.FOLLOW_UP.value
            self.leads[lead_id]['updated_at'] = datetime.now().isoformat()
            self._save()
    
    def add_note(self, lead_id: str, note: str):
        """Add a note to a lead"""
        if lead_id in self.leads:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            full_note = f"[{timestamp}] {note}"
            self.leads[lead_id]['notes'].append(full_note)
            self.leads[lead_id]['updated_at'] = datetime.now().isoformat()
            self._save()
    
    def get_lead(self, lead_id: str) -> Optional[Dict]:
        """Get a lead by ID"""
        return self.leads.get(lead_id)
    
    def get_all_leads(self) -> List[Dict]:
        """Get all leads"""
        return list(self.leads.values())
    
    def get_follow_ups_needed(self) -> List[Dict]:
        """Get leads that need follow-up"""
        now = datetime.now()
        needed = []
        for lead in self.leads.values():
            if lead.get('follow_up_date'):
                follow_date = datetime.fromisoformat(lead['follow_up_date'])
                if follow_date <= now:
                    needed.append(lead)
        return needed
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
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
        """Clear all leads (for testing)"""
        self.leads = {}
        self._save()
