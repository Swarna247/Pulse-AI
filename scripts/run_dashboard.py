"""
Script to run the Streamlit dashboard
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    from config.settings import DASHBOARD_PORT
    
    print("=" * 70)
    print("🏥 SMART PATIENT TRIAGE SYSTEM - DASHBOARD")
    print("=" * 70)
    print(f"Starting dashboard at http://localhost:{DASHBOARD_PORT}")
    print("=" * 70)
    
    # Path to main app
    app_path = Path(__file__).resolve().parent.parent / "app" / "main.py"
    
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        f"--server.port={DASHBOARD_PORT}",
        "--server.headless=true"
    ]
    
    sys.exit(stcli.main())
