"""
Script to run the FastAPI backend server
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import API_HOST, API_PORT

if __name__ == "__main__":
    import uvicorn
    from api.main import app
    
    print("=" * 70)
    print("🏥 SMART PATIENT TRIAGE SYSTEM - API SERVER")
    print("=" * 70)
    print(f"Starting API server at http://{API_HOST}:{API_PORT}")
    print(f"API Documentation: http://localhost:{API_PORT}/docs")
    print(f"Health Check: http://localhost:{API_PORT}/health")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        log_level="info"
    )
