"""Health check and system status endpoints"""

from fastapi import APIRouter
from datetime import datetime
import os
import sys

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with system info"""
    
    # Check data directory
    data_dir_exists = os.path.exists("hive_data")
    
    # Check leads database
    leads_file = "hive_data/leads.json"
    leads_count = 0
    if os.path.exists(leads_file):
        import json
        with open(leads_file, 'r') as f:
            leads_count = len(json.load(f))
    
    # Check available disk space
    import shutil
    disk_usage = shutil.disk_usage(".")
    free_gb = disk_usage.free / (1024**3)
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": {
            "python_version": sys.version,
            "platform": sys.platform
        },
        "storage": {
            "data_dir_exists": data_dir_exists,
            "leads_count": leads_count,
            "free_disk_gb": round(free_gb, 2)
        }
    }
