#!/usr/bin/env python
"""Backup and restore utility for HIVE-SDR"""

import os
import sys
import shutil
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def backup():
    """Create a backup of all data"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup leads database
    if os.path.exists("hive_data/leads.json"):
        shutil.copy("hive_data/leads.json", f"{backup_dir}/leads.json")
        print(f"✅ Backed up leads.json")
    
    # Backup campaigns
    if os.path.exists("hive_data/campaigns.json"):
        shutil.copy("hive_data/campaigns.json", f"{backup_dir}/campaigns.json")
        print(f"✅ Backed up campaigns.json")
    
    # Backup logs
    if os.path.exists("logs"):
        shutil.copytree("logs", f"{backup_dir}/logs")
        print(f"✅ Backed up logs")
    
    print(f"\n📦 Backup saved to: {backup_dir}")
    return backup_dir

def restore(backup_dir: str):
    """Restore from a backup"""
    if not os.path.exists(backup_dir):
        print(f"❌ Backup directory not found: {backup_dir}")
        return False
    
    # Restore leads
    if os.path.exists(f"{backup_dir}/leads.json"):
        os.makedirs("hive_data", exist_ok=True)
        shutil.copy(f"{backup_dir}/leads.json", "hive_data/leads.json")
        print(f"✅ Restored leads.json")
    
    # Restore campaigns
    if os.path.exists(f"{backup_dir}/campaigns.json"):
        shutil.copy(f"{backup_dir}/campaigns.json", "hive_data/campaigns.json")
        print(f"✅ Restored campaigns.json")
    
    print(f"\n🔄 Restored from: {backup_dir}")
    return True

def list_backups():
    """List all available backups"""
    backups = [d for d in os.listdir(".") if d.startswith("backup_") and os.path.isdir(d)]
    backups.sort(reverse=True)
    
    if not backups:
        print("No backups found")
        return
    
    print("\n📋 Available backups:")
    for i, backup in enumerate(backups):
        print(f"  {i+1}. {backup}")
    
    return backups

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup.py backup           - Create a backup")
        print("  python backup.py restore <dir>    - Restore from backup")
        print("  python backup.py list             - List available backups")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        backup()
    elif command == "restore" and len(sys.argv) > 2:
        restore(sys.argv[2])
    elif command == "list":
        list_backups()
    else:
        print("Invalid command")
