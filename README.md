# 🔥 Karhutla Kalimantan — Wildfire Hotspot Analysis (NASA FIRMS)

> 📖 [English](README.md) · [Bahasa Indonesia](README.id.md)

End-to-end data analysis of **active fire detections in Kalimantan (Indonesian
Borneo)** from NASA's FIRMS (VIIRS 375m + MODIS C6.1), pulled **without an API key**
via the Humanitarian Data Exchange (HDX) mirror. Built as a data-analyst portfolio
project: real data, real storytelling, reproducible pipeline.

**Live data window:** 14–21 Aug 2026 · **30,972 hotspots detected** · Peak: 18 Aug
(5,905/day) · Worst province: West Kalimantan (41.6% of total)

![Dashboard top](output/dashboard_top.png)

## What's inside

```
kalimantan-karhutla/
├── src/
│   ├── extract.py       # pull FIRMS VIIRS+MODIS 7d CSVs (retry + backoff, --refresh)
│   ├── transform.py     # bbox filter → point-in-polygon → province assignment
│   ├── analyze.py       # daily/province aggregates, FRP bands, history accumulation
│   ├── export_tableau.py# Tableau-ready CSVs (data/tableau/)
│   └── pipeline.py      # extract → transform → analyze, end to end
├── dashboard/
│   └── app.py           # Streamlit: interactive folium map + plotly charts
├── scripts/
│   ├── screenshot.py    # headless dashboard capture (Playwright)
│   └── daily_update.sh  # cron job: refresh data + export (live mode)
├── data/
│   ├── raw/             # original FIRMS CSVs (SE Asia, gitignored)
│   ├── processed/       # cleaned hotspots + aggregates + history_daily.csv
│   ├── tableau/         # Tableau-ready exports (see guide below)
│   └── boundaries/      # province boundaries (geoBoundaries ADM1, CC BY)
├── output/
│   ├── LAPORAN.md       # findings & recommendations (Bahasa Indonesia)
│   ├── PANDUAN_TABLEAU.md  # step-by-step Tableau dashboard guide
│   └── dashboard_*.png  # dashboard screenshots
└── requirements.txt
```

## 📊 Tableau version

This repo ships **Tableau-ready CSVs** (`data/tableau/`) and a complete
step-by-step guide (`output/PANDUAN_TABLEAU.md`) to build a Tableau Public
dashboard: interactive hotspot map, province ranking, daily trend, and a
province × day heatmap — then publish it as a shareable portfolio link.
Regenerate exports anytime with `python src/export_tableau.py`.

## 🔄 Live mode (daily updates)

The FIRMS near-real-time window is ~7 days, so the project is designed to run
daily via cron — accumulating `data/processed/history_daily.csv` (province × day
counts) that grows into a seasonality dataset over weeks/months:

```bash
# crontab -e
0 6 * * * /home/ubuntu/projects/kalimantan-karhutla/scripts/daily_update.sh
# or: ./scripts/daily_update.sh  (refresh + export + compact summary)
```


## Key findings (8-day window)

1. **West Kalimantan is the epicenter** — 12,875 hotspots (41.6%), followed by
   Central Kalimantan (10,732; 34.7%).
2. **Sharp surge 16→18 Aug** — daily count doubled to 5,905 and stayed high (5,500+)
   through Aug 21: a "fire outbreak" pattern, not a fading event.
3. **High-intensity fires present** — FRP up to **817 MW** in East/South Kalimantan;
   high-FRP points are the source of transboundary haze.

## How to run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Run the pipeline (downloads fresh 7-day data, ~30 MB)
python src/pipeline.py

# 2. Launch the dashboard
streamlit run dashboard/app.py
# open http://localhost:8501

# 3. (Optional) re-capture screenshots
python scripts/screenshot.py   # needs playwright + chromium
```

## Honest limitations

- **NRT data window**: FIRMS near-real-time covers ~7 days; the longer the project
  runs, the richer the seasonality story. A daily cron (`python src/pipeline.py`)
  accumulates history into `data/processed/`.
- **Hotspot ≠ burned area**: detections are thermal anomalies; VIIRS detects more
  points than MODIS due to finer resolution (375m vs 1km) — both are combined here
  for coverage, not double-counted for area.
- **FRP is a proxy** for fire intensity, not flame size.
- This is a portfolio/education project, **not** an official early-warning tool.

## Data sources & licenses

- **NASA FIRMS** active fire data (VIIRS S-NPP/NOAA-20/21 C2, MODIS C6.1) — public,
  via HDX mirror: `nasa-firms-active-fire-southeast-asia-viirs` / `-modis` (CC BY).
- **Province boundaries**: geoBoundaries `IDN_ADM1` (CC BY) via HDX.
- **ENSO context** (for seasonality studies): NOAA ONI index.
