"""Transform: filter detections to Indonesia, standardize schema, spatial-join
hotspots to provinces (point-in-polygon via shapely), compute intensity bands."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROC_DIR = ROOT / "data" / "processed"
BOUNDARIES = ROOT / "data" / "boundaries" / "idn_adm1.geojson"

BBOX = (95.0, -11.5, 141.5, 6.5)  # seluruh Indonesia (lon_min, lat_min, lon_max, lat_max)

KALIMANTAN_PROVINCES = {
    "West Kalimantan",
    "Central Kalimantan",
    "South Kalimantan",
    "East Kalimantan",
    "North Kalimantan",
}

# FRP (Fire Radiative Power, MW) thresholds — VIIRS-based intensity bands
FRP_BANDS = [(0, 20, "Rendah"), (20, 100, "Sedang"), (100, 500, "Tinggi"), (500, 1e9, "Ekstrem")]

# Province -> island group (for the region selector in the dashboard)
ISLAND_GROUPS = {
    "Aceh": "Sumatra", "North Sumatra": "Sumatra", "West Sumatra": "Sumatra",
    "Riau": "Sumatra", "Jambi": "Sumatra", "Bengkulu": "Sumatra",
    "South Sumatra": "Sumatra", "Bangka-Belitung Islands": "Sumatra",
    "Lampung": "Sumatra", "Riau Islands": "Sumatra", "Banten": "Java",
    "West Java": "Java", "Central Java": "Java",
    "Special Region of Yogyakarta": "Java", "East Java": "Java",
    "Jakarta Special Capital Region": "Java", "Bali": "Bali & Nusa Tenggara",
    "West Nusa Tenggara": "Bali & Nusa Tenggara",
    "East Nusa Tenggara": "Bali & Nusa Tenggara", "West Kalimantan": "Kalimantan",
    "Central Kalimantan": "Kalimantan", "South Kalimantan": "Kalimantan",
    "East Kalimantan": "Kalimantan", "North Kalimantan": "Kalimantan",
    "North Sulawesi": "Sulawesi", "Gorontalo": "Sulawesi",
    "Central Sulawesi": "Sulawesi", "West Sulawesi": "Sulawesi",
    "South Sulawesi": "Sulawesi", "Southeast Sulawesi": "Sulawesi",
    "Maluku": "Maluku & Papua", "North Maluku": "Maluku & Papua",
    "Papua": "Maluku & Papua", "West Papua": "Maluku & Papua",
}


def _standardize(df: pd.DataFrame, sensor: str) -> pd.DataFrame:
    """Map raw FIRMS columns (VIIRS & MODIS differ) to one schema."""
    out = pd.DataFrame(
        {
            "latitude": df["latitude"],
            "longitude": df["longitude"],
            "acq_date": pd.to_datetime(df["acq_date"]),
            "acq_time": df["acq_time"],
            "satellite": df["satellite"],
            "confidence": df["confidence"].astype(str),
            "frp": pd.to_numeric(df["frp"], errors="coerce"),
            "daynight": df["daynight"],
            "sensor": sensor,
        }
    )
    return out


def _in_bbox(df: pd.DataFrame) -> pd.DataFrame:
    lon_min, lat_min, lon_max, lat_max = BBOX
    return df[
        (df["longitude"] >= lon_min)
        & (df["longitude"] <= lon_max)
        & (df["latitude"] >= lat_min)
        & (df["latitude"] <= lat_max)
    ].copy()


def _load_provinces(path: Path) -> list[tuple[str, object]]:
    g = json.loads(path.read_text())
    polys = []
    for f in g["features"]:
        name = f["properties"].get("shapeName") or f["properties"].get("ADM1_EN") or "Unknown"
        polys.append((name, shape(f["geometry"])))
    return polys


def _assign_province(df: pd.DataFrame, polys: list[tuple[str, object]]) -> pd.DataFrame:
    # Use STRtree for fast point-in-polygon
    from shapely.strtree import STRtree

    geoms = [p for _, p in polys]
    tree = STRtree(geoms)
    names = [n for n, _ in polys]
    idx_map = {id(g): i for i, g in enumerate(geoms)}

    provinces = []
    for lat, lon in zip(df["latitude"], df["longitude"]):
        pt = Point(lon, lat)
        hits = tree.query(pt)
        found = "Luar Provinsi"
        for h in hits:
            if geoms[h].contains(pt):
                found = names[idx_map[id(geoms[h])]]
                break
        provinces.append(found)
    df["provinsi"] = provinces
    return df


def _frp_band(frp: float) -> str:
    for lo, hi, label in FRP_BANDS:
        if lo <= frp < hi:
            return label
    return "Rendah"


def transform(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    parts = []
    for sensor in ("viirs", "modis"):
        df = frames[sensor]
        df = _standardize(df, sensor)
        df = _in_bbox(df)
        parts.append(df)
        print(f"[transform] {sensor}: {len(df):,} detections in Indonesia bbox")

    all_df = pd.concat(parts, ignore_index=True)
    polys = _load_provinces(BOUNDARIES)
    all_df = _assign_province(all_df, polys)
    all_df["frp_band"] = all_df["frp"].apply(_frp_band)

    # Keep only detections inside an Indonesian province (bbox is a rectangle,
    # so it captures neighbours — Singapore, Malaysia, Timor-Leste, etc.)
    n_out = (all_df["provinsi"] == "Luar Provinsi").sum()
    all_df = all_df[all_df["provinsi"] != "Luar Provinsi"].copy()
    if n_out:
        print(f"[transform] dropped {n_out:,} detections outside Indonesia")

    # Island group per province (Sumatra/Java/Kalimantan/...)
    all_df["pulau"] = all_df["provinsi"].map(ISLAND_GROUPS).fillna("Lainnya")

    # clean time
    all_df["acq_datetime"] = pd.to_datetime(
        all_df["acq_date"].astype(str) + " " + all_df["acq_time"].astype(str).str.zfill(4),
        format="%Y-%m-%d %H%M",
        errors="coerce",
    )
    all_df = all_df.drop(columns=["acq_time"])
    all_df = all_df.sort_values("acq_datetime").reset_index(drop=True)

    out = PROC_DIR / "indonesia_hotspots.csv"
    all_df.to_csv(out, index=False)
    print(f"[transform] total: {len(all_df):,} hotspots -> {out.name}")
    return all_df


if __name__ == "__main__":
    from extract import extract

    transform(extract())
