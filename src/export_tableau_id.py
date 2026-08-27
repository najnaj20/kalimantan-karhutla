"""Generate Indonesian-locale CSV variants for Tableau.

Indonesian Tableau/Excel expects: semicolon (;) as column separator and comma (,)
as decimal separator. These files parse correctly with zero locale fiddling:
  tableau_hotspots_id.csv   (semicolon + comma decimals)
  tableau_province_id.csv
  tableau_daily_id.csv
  tableau_province_daily_id.csv
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


def _to_id_format(df: pd.DataFrame) -> pd.DataFrame:
    """Convert dot-decimal numeric columns to comma-decimal strings."""
    df = df.copy()
    for col in df.select_dtypes(include=["float64", "float32"]).columns:
        df[col] = df[col].map(lambda v: f"{v:.4f}".rstrip("0").rstrip(".").replace(".", ","))
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROC / "kalimantan_hotspots.csv", parse_dates=["acq_date"])
    df["acq_datetime"] = pd.to_datetime(df["acq_datetime"])
    df["provinsi_id"] = df["provinsi"].map(PROVINSI_ID).fillna(df["provinsi"])

    detail = df[
        [
            "acq_datetime", "acq_date", "latitude", "longitude", "frp",
            "frp_band", "provinsi", "provinsi_id", "sensor", "satellite",
            "confidence", "daynight",
        ]
    ].sort_values("acq_datetime")

    pd_daily = (
        df.groupby(["provinsi_id", "acq_date"]).size().rename("jumlah_hotspot").reset_index()
    )
    daily = df.groupby("acq_date").size().rename("jumlah_hotspot").reset_index()
    prov = (
        df.groupby("provinsi_id")
        .agg(jumlah_hotspot=("latitude", "size"), frp_rata2=("frp", "mean"), frp_maks=("frp", "max"))
        .reset_index()
        .sort_values("jumlah_hotspot", ascending=False)
    )

    files = {
        "tableau_hotspots_id.csv": _to_id_format(detail),
        "tableau_province_id.csv": _to_id_format(prov),
        "tableau_daily_id.csv": _to_id_format(daily),
        "tableau_province_daily_id.csv": _to_id_format(pd_daily),
    }
    for name, d in files.items():
        # sep=";" + comma decimals + no index
        d.to_csv(OUT / name, sep=";", index=False)
        print(f"{name}: {len(d):,} baris")


if __name__ == "__main__":
    main()
