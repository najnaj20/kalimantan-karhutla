"""Pipeline orchestrator: extract -> transform -> analyze, end to end."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("pipeline")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from analyze import analyze  # noqa: E402
from extract import extract  # noqa: E402
from transform import transform  # noqa: E402


def run_pipeline(refresh: bool = False) -> None:
    log.info("== EXTRACT ==")
    frames = extract(refresh=refresh)
    log.info("== TRANSFORM ==")
    df = transform(frames)
    log.info("== ANALYZE ==")
    analyze(df)
    log.info("== PIPELINE DONE ==")


if __name__ == "__main__":
    import sys

    run_pipeline(refresh="--refresh" in sys.argv)
