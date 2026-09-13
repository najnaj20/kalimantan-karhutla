"""Headless screenshot of the Streamlit dashboard (full page + key sections)."""
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "output"
URL = "http://localhost:8501"


def scroll_to(page, selector_text: str) -> bool:
    """Scroll the main streamlit container so an element containing text is visible."""
    return page.evaluate(
        """(text) => {
            const els = [...document.querySelectorAll('h1,h2,h3,h4,[data-testid="stMarkdownContainer"] p')];
            const el = els.find(e => e.innerText && e.innerText.includes(text));
            if (!el) return false;
            el.scrollIntoView({block: 'start'});
            window.scrollBy(0, -80);
            return true;
        }""",
        selector_text,
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1500, "height": 1000})
        page.goto(URL, wait_until="networkidle", timeout=60000)
        time.sleep(14)  # let folium tiles + plotly render

        # 1. Top: title, ENSO banner, metrics, map
        page.screenshot(path=str(OUT / "dashboard_top.png"), full_page=False)

        # 2. Daily trend chart
        if scroll_to(page, "Tren Hotspot") or scroll_to(page, "Hotspot Trend"):
            time.sleep(4)
            page.screenshot(path=str(OUT / "dashboard_charts.png"), full_page=False)

        # 3. Year-over-Year comparison (new feature)
        if scroll_to(page, "Perbandingan per Tahun") or scroll_to(page, "Year-over-Year"):
            time.sleep(4)
            page.screenshot(path=str(OUT / "dashboard_yoy.png"), full_page=False)

        # 4. Province heatmap grid
        if scroll_to(page, "Heatmap Provinsi") or scroll_to(page, "Province × Day Heatmap"):
            time.sleep(4)
            page.screenshot(path=str(OUT / "dashboard_heatmap.png"), full_page=False)

        browser.close()
    print("screenshots saved:", ", ".join(sorted(f.name for f in OUT.glob("dashboard_*.png"))))


if __name__ == "__main__":
    main()
