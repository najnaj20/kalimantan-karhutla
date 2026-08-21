"""Build a preview of the target Tableau visualization: Kalimantan map +
fire hotspot dots (sized/colored by FRP). Saves HTML + PNG screenshot.

This is a REFERENCE image so the user knows what the Tableau sheet should
look like — not a replacement for the Tableau build.
"""
from __future__ import annotations

import json
from pathlib import Path

import folium
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
BOUNDARIES = ROOT / "data" / "boundaries" / "idn_adm1.geojson"
OUT = ROOT / "output"

KALIMANTAN = {"West Kalimantan", "Central Kalimantan", "South Kalimantan", "East Kalimantan", "North Kalimantan"}
WARNA = {
    "West Kalimantan": "#d62728",
    "Central Kalimantan": "#ff7f0e",
    "South Kalimantan": "#2ca02c",
    "East Kalimantan": "#1f77b4",
    "North Kalimantan": "#9467bd",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROC / "kalimantan_hotspots.csv", parse_dates=["acq_date"])
    gjson = json.loads(BOUNDARIES.read_text())

    m = folium.Map(location=[-1.2, 114.5], zoom_start=6, tiles="CartoDB positron")

    # Province boundaries (only Kalimantan)
    for f in gjson["features"]:
        name = f["properties"].get("shapeName")
        if name not in KALIMANTAN:
            continue
        folium.GeoJson(
            f,
            style_function=lambda _feat, n=name: {
                "fillColor": WARNA.get(n, "#ccc"),
                "color": "#444",
                "weight": 1.6,
                "fillOpacity": 0.06,
            },
            tooltip=folium.GeoJsonTooltip(fields=["shapeName"], aliases=["Provinsi"]),
        ).add_to(m)

    # Fire dots sized+colored by FRP (top ~8k by FRP for a readable preview)
    d = df.nlargest(8000, "frp")
    cmap = folium.LinearColormap(["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c", "#7b241c"], vmin=0, vmax=400)
    for _, row in d.iterrows():
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=1.5 + (row["frp"] / 60),
            color=None,
            fill=True,
            fill_color=cmap(min(row["frp"], 400)),
            fill_opacity=0.55,
            popup=f"FRP {row['frp']:.0f} MW · {row['provinsi']}<br>{row['acq_datetime']}",
        ).add_to(m)
    cmap.add_to(m)
    cmap.caption = "FRP (MW) — Fire Radiative Power"

    html_path = OUT / "preview_peta_kalimantan.html"
    m.save(str(html_path))
    print(f"saved {html_path}")


if __name__ == "__main__":
    main()
