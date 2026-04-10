#!/usr/bin/env python
"""Production launcher for HIVE-SDR with data persistence"""

import uvicorn
import os
import sys

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Create required directories
os.makedirs("hive_data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

PORT = 58954

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🐝 HIVE-SDR Agent Lounge")
    print("="*60)
    print(f"\n📍 Dashboard: http://localhost:{PORT}")
    print(f"📁 Data directory: ./hive_data")
    print(f"📝 Logs directory: ./logs")
    print("\nPress Ctrl+C to stop\n")
    print("="*60 + "\n")
    
    uvicorn.run(
        "ui_client.working_app:app",
        host="127.0.0.1",
        port=PORT,
        reload=False,
        log_level="info"
    )
