"""Logging system for HIVE-SDR"""

import os
from datetime import datetime
from typing import Optional

class HiveLogger:
    """Simple file-based logger for the system"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self._ensure_log_dir()
        self.current_log = self._get_log_filename()
    
    def _ensure_log_dir(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _get_log_filename(self) -> str:
        return os.path.join(self.log_dir, f"hive_{datetime.now().strftime('%Y%m%d')}.log")
    
    def _write(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        
        with open(self.current_log, 'a') as f:
            f.write(log_entry)
        
        # Also print to console for visibility
        print(log_entry.strip())
    
    def info(self, message: str):
        self._write("INFO", message)
    
    def warning(self, message: str):
        self._write("WARNING", message)
    
    def error(self, message: str):
        self._write("ERROR", message)
    
    def campaign_start(self, industry: str, city: str, max_leads: int):
        self.info(f"Campaign started: industry={industry}, city={city}, max_leads={max_leads}")
    
    def campaign_complete(self, industry: str, leads_found: int, emails_generated: int):
        self.info(f"Campaign completed: industry={industry}, leads={leads_found}, emails={emails_generated}")
    
    def lead_added(self, lead_name: str, score: int):
        self.info(f"Lead added: name={lead_name}, score={score}")
    
    def status_change(self, lead_id: str, old_status: str, new_status: str):
        self.info(f"Status change: lead={lead_id}, {old_status} → {new_status}")

# Global logger instance
logger = HiveLogger()
