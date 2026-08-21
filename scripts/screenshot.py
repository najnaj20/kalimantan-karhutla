"""Headless screenshot of the Streamlit dashboard (full page + top)."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "output"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1500, "height": 1000})
        page.goto("http://localhost:8502", wait_until="networkidle", timeout=60000)
        time.sleep(12)  # let folium tiles + plotly render
        page.screenshot(path=str(OUT / "dashboard_top.png"), full_page=False)
        # scroll to reveal charts
        page.mouse.wheel(0, 1200)
        time.sleep(5)
        page.screenshot(path=str(OUT / "dashboard_charts.png"), full_page=False)
        page.mouse.wheel(0, 1600)
        time.sleep(5)
        page.screenshot(path=str(OUT / "dashboard_heatmap.png"), full_page=False)
        browser.close()
    print("screenshots saved")


if __name__ == "__main__":
    main()
