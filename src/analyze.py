"""Analyze: daily/province aggregates, intensity profile, key findings for the
report. Writes processed CSVs consumed by the dashboard + report."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = ROOT / "data" / "processed"
OUT_DIR = ROOT / "output"


def analyze(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    df["tanggal"] = df["acq_date"].dt.date

    # 1. Daily hotspot count (all sensors)
    daily = df.groupby("tanggal").size().rename("hotspot").reset_index()

    # 2. By province (count + mean FRP)
    prov = (
        df.groupby("provinsi")
        .agg(hotspot=("latitude", "size"), frp_mean=("frp", "mean"), frp_max=("frp", "max"))
        .sort_values("hotspot", ascending=False)
        .reset_index()
    )

    # 3. By province x day (for heatmap)
    prov_daily = (
        df.groupby(["provinsi", "tanggal"])
        .size()
        .rename("hotspot")
        .reset_index()
        .pivot(index="provinsi", columns="tanggal", values="hotspot")
        .fillna(0)
    )

    # 4. Intensity bands distribution
    bands = df.groupby("frp_band").size().rename("count").reset_index()

    # 5. Peak day + worst province
    peak_day = daily.loc[daily["hotspot"].idxmax()]
    worst_prov = prov.iloc[0]

    # 6. Night vs day
    daynight = df.groupby("daynight").size().rename("count").reset_index()

    # 7. Weekly-ish trend: hotspots per day per province (top 3 provinces)
    top3 = prov.head(3)["provinsi"].tolist()
    top3_daily = (
        df[df["provinsi"].isin(top3)]
        .groupby(["provinsi", "tanggal"])
        .size()
        .rename("hotspot")
        .reset_index()
    )

    # 8. Accumulate history (cron daily) -> enables seasonality analysis later
    history_path = PROC_DIR / "history_daily.csv"
    today_snapshot = (
        df.groupby(["provinsi", "tanggal"])
        .size()
        .rename("hotspot")
        .reset_index()
        .assign(fetched_at=pd.Timestamp.now().normalize())
    )
    # Normalize tanggal to string so dedupe works across mixed types
    # (datetime.date from groupby vs str read back from CSV)
    today_snapshot["tanggal"] = today_snapshot["tanggal"].astype(str)
    if history_path.exists():
        hist = pd.read_csv(history_path)
        hist["tanggal"] = hist["tanggal"].astype(str)
        hist = pd.concat([hist, today_snapshot], ignore_index=True)
        # dedupe: same (provinsi, tanggal) from a re-run of the same day
        hist = hist.drop_duplicates(subset=["provinsi", "tanggal"], keep="last")
    else:
        hist = today_snapshot
    hist.to_csv(history_path, index=False)
    print(f"[analyze] history_daily.csv: {len(hist):,} baris akumulasi")

    results = {
        "daily": daily,
        "province": prov,
        "province_daily": prov_daily,
        "bands": bands,
        "daynight": daynight,
        "top3_daily": top3_daily,
    }
    for name, d in results.items():
        d.to_csv(PROC_DIR / f"agg_{name}.csv", index=True if name == "province_daily" else False)

    summary = {
        "total_hotspot": int(len(df)),
        "hari_cakupan": int(df["tanggal"].nunique()),
        "rentang_data": f"{df['tanggal'].min()} s/d {df['tanggal'].max()}",
        "peak_day": str(peak_day["tanggal"]),
        "peak_day_count": int(peak_day["hotspot"]),
        "worst_province": str(worst_prov["provinsi"]),
        "worst_province_count": int(worst_prov["hotspot"]),
        "frp_max": round(float(df["frp"].max()), 1),
        "sensor_split": df.groupby("sensor").size().to_dict(),
        "top3_provinces": top3,
    }
    print("[analyze] SUMMARY:")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    return results, summary


if __name__ == "__main__":
    df = pd.read_csv(PROC_DIR / "indonesia_hotspots.csv", parse_dates=["acq_date"])
    analyze(df)
