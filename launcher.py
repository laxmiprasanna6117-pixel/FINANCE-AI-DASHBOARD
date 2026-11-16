"""
Robust launcher for Finance Data Analysis & AI Automation Dashboard.
Handles environment configuration, disables credential prompts,
and automatically opens the dashboard in the default browser.
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

# Force Streamlit to skip email prompt, skip telemetry, and run cleanly
os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
os.environ["STREAMLIT_SERVER_SHOW_EMAIL_PROMPT"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
os.environ["STREAMLIT_SERVER_PORT"] = "8501"

project_dir = Path(__file__).resolve().parent
os.environ["STREAMLIT_CONFIG_DIR"] = str(project_dir / ".streamlit")

def open_browser():
    time.sleep(2.0)
    print("\n" + "="*60)
    print(" Dashboard is live at: http://localhost:8501")
    print(" Opening your browser automatically...")
    print("="*60 + "\n")
    try:
        webbrowser.open("http://localhost:8501")
    except Exception:
        pass

if __name__ == "__main__":
    print("="*60)
    print(" Starting Finance Data Analysis & AI Automation Dashboard...")
    print("="*60)
    
    # Launch browser opener in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    from streamlit.web import cli as stcli
    sys.argv = [
        "streamlit",
        "run",
        str(project_dir / "app.py"),
        "--server.port=8501",
        "--server.headless=true",
        "--server.showEmailPrompt=false",
        "--browser.gatherUsageStats=false"
    ]
    sys.exit(stcli.main())
