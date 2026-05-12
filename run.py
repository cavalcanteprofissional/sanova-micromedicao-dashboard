import sys
import os

# Add src/ to path so "dashboard" package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import streamlit.web.cli as stcli

if __name__ == "__main__":
    sys.argv = [
        "streamlit", "run",
        "src/dashboard/main.py",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    stcli.main()