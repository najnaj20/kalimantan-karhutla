"""Root launcher for Streamlit Community Cloud.

Streamlit Cloud expects the main script at the repo root; the real
dashboard lives in dashboard/app.py. Path(__file__) inside that file
resolves correctly when run via runpy, so no code duplication needed.
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).parent / "dashboard" / "app.py"), run_name="__main__")
