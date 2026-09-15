"""Fetch hourly air quality (PM2.5/PM10, US AQI + ISPU) for Kalimantan capitals
from Open-Meteo Air Quality API (free, no API key; CAMS ensemble model).
Writes data/processed/aqi_hourly.csv + data/processed/aqi_summary.json.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"

CITIES = {
    "Pontianak": (-0.02, 109.34, "Kalimantan Barat", "WIB"),
    "Palangka Raya": (-2.21, 113.92, "Kalimantan Tengah", "WIB"),
    "Banjarmasin": (-2.23, 114.59, "Kalimantan Selatan", "WITA"),
    "Samarinda": (-0.49, 117.15, "Kalimantan Timur", "WITA"),
    "Tanjung Selor": (2.86, 117.36, "Kalimantan Utara", "WITA"),
}

# US EPA AQI breakpoints for PM2.5 (conc_low, conc_high, aqi_low, aqi_high)
US_PM25_BP = [
    (0.0, 9.2, 0, 50), (9.3, 35.4, 51, 100), (35.5, 55.4, 101, 150),
    (55.5, 125.4, 151, 200), (125.5, 225.4, 201, 300), (225.5, 325.4, 301, 400),
    (325.5, 326.4, 401, 500),
]

def us_aqi_from_pm25(c: float | None) -> float | None:
    if c is None or pd.isna(c):
        return None
    for cl, ch, al, ah in US_PM25_BP:
        if c <= ch:
            return round(al + (ah - al) * (c - cl) / (ch - cl), 1)
    return 500.0

def ispu_category(pm24: float | None):
    """Indonesian ISPU for PM2.5 24h µg/m³ (PP 41/1999):
    Baik 0–15 · Sedang >15–50 · Tidak Sehat >50–150 · Berbahaya >150."""
    if pm24 is None or pd.isna(pm24):
        return None, None, None
    bands = [
        (15, "Baik", "#22c55e"), (50, "Sedang", "#eab308"),
        (150, "Tidak Sehat", "#f97316"), (1e9, "Berbahaya", "#ef4444"),
    ]
    for lim, label, color in bands:
        if pm24 <= lim:
            return label, color, None
    return None, None, None

def main() -> None:
    lats = ",".join(str(v[0]) for v in CITIES.values())
    lons = ",".join(str(v[1]) for v in CITIES.values())
    r = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={"latitude": lats, "longitude": lons,
                "hourly": "pm2_5,pm10", "past_days": 8, "forecast_days": 2,
                "timezone": "UTC"},
        timeout=60,
    )
    r.raise_for_status()
    locs = r.json()
    if not isinstance(locs, list):
        locs = [locs]

    frames = []
    for (city, (lat, lon, prov, tzname)), loc in zip(CITIES.items(), locs):
        h = pd.DataFrame({
            "time_local": pd.to_datetime(loc["hourly"]["time"]),
            "pm25": loc["hourly"]["pm2_5"],
            "pm10": loc["hourly"]["pm10"],
        })
        h["us_aqi"] = h["pm25"].map(us_aqi_from_pm25)
        h["city"] = city
        h["provinsi"] = prov
        frames.append(h)

    df = pd.concat(frames, ignore_index=True)
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M UTC")
    df["time_utc"] = df["time_local"]
    df = df[["time_utc", "city", "provinsi", "pm25", "pm10", "us_aqi"]]
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROC_DIR / "aqi_hourly.csv", index=False)

    # summary: current (last past-hour obs) + 24h mean for ISPU category
    cutoff = pd.Timestamp.now("UTC").tz_localize(None)
    summary = {}
    for city in CITIES:
        c = df[df["city"] == city]
        past = c[c["time_utc"] <= cutoff].dropna(subset=["pm25"])
        if past.empty:
            continue
        last = past.iloc[-1]
        mean24 = past[past["time_utc"] > last["time_utc"] - pd.Timedelta(hours=24)]["pm25"].mean()
        cat, color, _ = ispu_category(mean24)
        summary[city] = {
            "provinsi": str(last["provinsi"]),
            "pm25_now": float(last["pm25"]),
            "us_aqi_now": float(last["us_aqi"]),
            "time_utc": str(last["time_utc"]),
            "pm25_24h_mean": round(float(mean24), 1),
            "ispu_category": cat,
            "ispu_color": color,
        }
    (PROC_DIR / "aqi_summary.json").write_text(json.dumps(
        {"fetched_at_utc": now_utc, "cities": summary}, indent=2, ensure_ascii=False))
    print(f"AQI saved: {len(df)} hourly rows, {len(summary)} cities. Fetched {now_utc}")
    for city, s in summary.items():
        print(f"  {city}: PM2.5 {s['pm25_now']:.0f} µg/m³ | US-AQI {s['us_aqi_now']:.0f} | ISPU {s['ispu_category']}")

if __name__ == "__main__":
    main()
