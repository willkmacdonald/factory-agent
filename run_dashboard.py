"""Wrapper script to run the Streamlit dashboard."""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the dashboard
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys

    dashboard_path = os.path.join(os.path.dirname(__file__), "src", "dashboard.py")
    sys.argv = ["streamlit", "run", dashboard_path]
    sys.exit(stcli.main())
