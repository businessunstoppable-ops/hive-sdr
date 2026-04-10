#!/usr/bin/env python
"""Launch the HIVE-SDR Dashboard"""

import uvicorn

PORT = 58954

if __name__ == "__main__":
    print("=" * 60)
    print("🐝 HIVE-SDR Dashboard Starting...")
    print("=" * 60)
    print(f"\n📍 Dashboard will be available at: http://localhost:{PORT}")
    print(f"📍 API docs at: http://localhost:{PORT}/docs")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)
    
    uvicorn.run(
        "ui_client.app:app",
        host="127.0.0.1",
        port=PORT,
        reload=True,
        log_level="info"
    )
