"""
Robust launcher for Finance Data Analysis & AI Automation Dashboard.
Starts the local production WSGI server (Waitress) and automatically opens
the dashboard in the user's default web browser without development warnings.
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))

    host = '127.0.0.1'
    port = 5000

    threading.Thread(target=open_browser, daemon=True).start()

    from app import app
    print("=================================================================")
    print("Finance Data Analysis & AI Automation Dashboard is running!")
    try:
        from waitress import serve
        print(f"Serving production WSGI via Waitress on http://{host}:{port}")
        print("=================================================================")
        serve(app, host=host, port=port, threads=6)
    except ImportError:
        print(f"Serving on http://{host}:{port}")
        print("=================================================================")
        app.run(host=host, port=port, debug=False)
