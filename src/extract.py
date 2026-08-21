"""Extract: pull NASA FIRMS active fire detections (VIIRS + MODIS) for Southeast Asia.

Data is mirrored on HDX (license CC BY) and downloadable directly from NASA FIRMS
without an API key. Source: https://firms.modaps.eosdis.nasa.gov/active_fire/
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

SOURCES = {
    "viirs": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_SouthEast_Asia_7d.csv",
    "modis": "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_SouthEast_Asia_7d.csv",
}

# Kalimantan bounding box (lon_min, lat_min, lon_max, lat_max)
BBOX = (108.6, -4.3, 119.4, 7.2)


def _download(url: str, out: Path, retries: int = 3) -> Path:
    """Download with retry + backoff (FIRMS is a public server, be gentle)."""
    delay = 3
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=60)
            r.raise_for_status()
            out.write_bytes(r.content)
            return out
        except Exception as e:  # noqa: BLE001
            if attempt == retries:
                raise
            print(f"  retry {attempt}/{retries} for {url.name}: {e}")
            time.sleep(delay * attempt)
    raise RuntimeError(f"unreachable: {url}")


def extract(refresh: bool = False) -> dict[str, pd.DataFrame]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    frames: dict[str, pd.DataFrame] = {}
    for name, url in SOURCES.items():
        out = RAW_DIR / f"{name}_7d.csv"
        if refresh or not out.exists() or out.stat().st_size == 0:
            print(f"[extract] downloading {name} ...")
            _download(url, out)
        df = pd.read_csv(out)
        print(f"[extract] {name}: {len(df):,} raw detections (SE Asia, 7d)")
        frames[name] = df
    return frames


if __name__ == "__main__":
    import sys

    extract(refresh="--refresh" in sys.argv)
