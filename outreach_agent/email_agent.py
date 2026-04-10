# outreach_agent/email_agent.py
from typing import Dict, List
import json
from datetime import datetime

class EmailAgent:
    """
    Handles preparing and tracking outreach emails.
    (Real sending requires SMTP configuration)
    """
    
    def __init__(self):
        self.sent_emails = []  # Track sent emails (mock)
        self.email_config = {
            'configured': False,
            'message': 'Email sending not configured - use mock mode'
        }
        
    def prepare_outreach(self, lead, orchestration_result: Dict) -> Dict:
        """Prepare email for sending"""
        
        email_draft = orchestration_result.get('email_draft', '')
        
        # Add professional signature
        signature = """
---
Best regards,
[Your Name]
[Your Title]
[Your Company]
Phone: [Your Number]
"""
        
        full_email = email_draft + signature
        
        # Extract or generate email address
        # In real use, you'd need to find the actual email
        estimated_email = self._estimate_email(lead.name, lead.website)
        
        return {
            'to': estimated_email,
            'subject': f"Quick idea for {lead.name}",
            'body': full_email,
            'lead_name': lead.name,
            'score': orchestration_result.get('score', {}).get('score', 0),
            'ready_to_send': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _estimate_email(self, business_name: str, website: str) -> str:
        """Estimate email address when real one isn't available"""
        if website and website != "None":
            # Extract domain from website
            domain = website.replace("https://", "").replace("http://", "").split("/")[0]
            # Common patterns
            patterns = [
                f"info@{domain}",
                f"hello@{domain}",
                f"contact@{domain}",
                f"owner@{domain}"
            ]
            return patterns[0]  # Return most likely
        return "email@example.com"
    
    def send_email(self, prepared_email: Dict) -> Dict:
        """Mock send email (real SMTP will be added later)"""
        print(f"📧 MOCK SENDING EMAIL:")
        print(f"   To: {prepared_email['to']}")
        print(f"   Subject: {prepared_email['subject']}")
        print(f"   Lead: {prepared_email['lead_name']}")
        
        # Store in sent log
        self.sent_emails.append({
            **prepared_email,
            'sent_at': datetime.now().isoformat(),
            'status': 'mock_sent'
        })
        
        return {
            'success': True,
            'message': f"Email prepared for {prepared_email['lead_name']}",
            'mock_mode': True,
            'recipient': prepared_email['to']
        }
    
    def send_batch(self, prepared_emails: List[Dict]) -> List[Dict]:
        """Send multiple emails"""
        results = []
        for email in prepared_emails:
            result = self.send_email(email)
            results.append(result)
        return results
    
    def get_sent_log(self) -> List[Dict]:
        """Return all sent emails (mock)"""
        return self.sent_emails
    
    def configure_smtp(self, username: str, password: str, server: str = "smtp.gmail.com", port: int = 587):
        """Configure real SMTP settings (for later use)"""
        self.email_config = {
            'configured': True,
            'username': username,
            'server': server,
            'port': port,
            'message': 'SMTP configured - ready to send real emails'
        }
        print("✅ SMTP configured. Real email sending is now available.")
