"""Export Tableau-ready CSVs from the processed Kalimantan hotspot data.

Produces files under data/tableau/ that map 1:1 to Tableau data types
(date, number, string) so the user can drag-and-drop in Tableau Desktop/Public
without any reshaping:

  tableau_hotspots.csv        one row per detection (30k rows, for maps/scatter)
  tableau_province_daily.csv  province x day counts (heatmap / trend)
  tableau_daily.csv           day totals (line chart)
  tableau_province.csv        province aggregates (bar chart)
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
OUT = ROOT / "data" / "tableau"

PROVINSI_ID = {
    "West Kalimantan": "Kalimantan Barat",
    "Central Kalimantan": "Kalimantan Tengah",
    "South Kalimantan": "Kalimantan Selatan",
    "East Kalimantan": "Kalimantan Timur",
    "North Kalimantan": "Kalimantan Utara",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROC / "kalimantan_hotspots.csv", parse_dates=["acq_date"])
    df["acq_datetime"] = pd.to_datetime(df["acq_datetime"])
    df["provinsi_id"] = df["provinsi"].map(PROVINSI_ID).fillna(df["provinsi"])

    # 1. Detail (maps, scatter, filters)
    detail = df[
        [
            "acq_datetime", "acq_date", "latitude", "longitude", "frp",
            "frp_band", "provinsi", "provinsi_id", "sensor", "satellite",
            "confidence", "daynight",
        ]
    ].sort_values("acq_datetime")
    detail.to_csv(OUT / "tableau_hotspots.csv", index=False)

    # 2. Province x day (heatmap)
    pd_daily = (
        df.groupby(["provinsi_id", "acq_date"])
        .size()
        .rename("jumlah_hotspot")
        .reset_index()
    )
    pd_daily.to_csv(OUT / "tableau_province_daily.csv", index=False)

    # 3. Daily totals (trend line)
    daily = df.groupby("acq_date").size().rename("jumlah_hotspot").reset_index()
    daily.to_csv(OUT / "tableau_daily.csv", index=False)

    # 4. Province aggregates (bar chart)
    prov = (
        df.groupby("provinsi_id")
        .agg(
            jumlah_hotspot=("latitude", "size"),
            frp_rata2=("frp", "mean"),
            frp_maks=("frp", "max"),
        )
        .reset_index()
        .sort_values("jumlah_hotspot", ascending=False)
    )
    prov.to_csv(OUT / "tableau_province.csv", index=False)

    for f in sorted(OUT.glob("*.csv")):
        print(f"{f.name}: {sum(1 for _ in open(f)) - 1:,} baris")


if __name__ == "__main__":
    main()
