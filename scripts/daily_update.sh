#!/usr/bin/env bash
# Daily live update: refresh FIRMS data -> pipeline -> Tableau export.
# Run by cron every day; prints a compact summary (delivered to chat).
set -euo pipefail

cd "$(dirname "$0")/.."
source .venv/bin/activate

python src/pipeline.py --refresh >/tmp/karhutla_daily.log 2>&1
python src/export_tableau.py >>/tmp/karhutla_daily.log 2>&1
python src/fetch_aqi.py >>/tmp/karhutla_daily.log 2>&1

# Compact summary for the chat delivery
python - <<'EOF'
import pandas as pd

df = pd.read_csv("data/processed/kalimantan_hotspots.csv", parse_dates=["acq_date"])
prov = df.groupby("provinsi").size().sort_values(ascending=False)
top = prov.index[0]
hist = pd.read_csv("data/processed/history_daily.csv")

print("🔥 Karhutla Kalimantan — update harian")
print(f"Periode: {df['acq_date'].min():%d %b} – {df['acq_date'].max():%d %b %Y}")
print(f"Total hotspot: {len(df):,} | Hari: {df['acq_date'].dt.date.nunique()}")
print(f"Terparah: {top} ({int(prov.iloc[0]):,})")
print(f"Akumulasi history: {len(hist):,} baris (provinsi × hari)")
try:
    import json
    a=json.load(open("data/processed/aqi_summary.json"))
    worst=max(a["cities"].items(), key=lambda kv: kv[1]["us_aqi_now"])
    wc, wv = worst[0], worst[1]
    line=" | ".join(f'{c} {v["us_aqi_now"]:.0f}' for c,v in a["cities"].items())
    isp, aqi = wv["ispu_category"], wv["us_aqi_now"]
    print(f"🌫️ AQI (US, model): {line} — terburuk {wc}: {isp} ({aqi:.0f})")
except Exception as e:
    print(f"🌫️ AQI: tidak tersedia ({e})")
EOF
