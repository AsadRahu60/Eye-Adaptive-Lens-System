#!/usr/bin/env python3
"""
Telemetry demo for Eye project.

- Default: --mock generates fake sensor packets (CI-safe)
- Later: --ble to read a BLE characteristic (requires bleak + hardware)

Usage:
  python host/pi/telemetry_demo.py --mock --duration 10 --interval 0.5
"""

from __future__ import annotations
import argparse
import csv
import json
import logging
import random
import time
from pathlib import Path

log = logging.getLogger(__name__)

try:
    # Optional; only used when --ble is passed
    from bleak import BleakClient  # type: ignore
except ImportError:  # pragma: no cover
    BleakClient = None  # noqa: N816
    log.debug("bleak not installed; BLE mode unavailable")


def mock_packet() -> dict:
    """Generate a fake telemetry packet (distance cm, lux, yaw)."""
    return {
        "ts": time.time(),
        "dist_cm": round(random.uniform(30.0, 120.0), 1),
        "lux": round(random.uniform(50.0, 500.0), 1),
        "yaw_deg": round(random.uniform(-45.0, 45.0), 1),
    }


def to_csv_row(pkt: dict) -> list:
    return [pkt["ts"], pkt["dist_cm"], pkt["lux"], pkt["yaw_deg"]]


def run_mock(duration: float, interval: float, out: Path | None) -> None:
    """Run mock telemetry stream; writes CSV if *out* is provided."""
    log.info("Starting mock telemetry stream (duration=%.1fs, interval=%.2fs)", duration, interval)
    start = time.time()
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        # Use context manager to guarantee file is closed even on exception
        with out.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ts", "dist_cm", "lux", "yaw_deg"])
            while time.time() - start < duration:
                pkt = mock_packet()
                log.debug("packet: %s", json.dumps(pkt))
                writer.writerow(to_csv_row(pkt))
                time.sleep(interval)
        log.info("Wrote CSV → %s", out)
    else:
        while time.time() - start < duration:
            pkt = mock_packet()
            log.debug("packet: %s", json.dumps(pkt))
            time.sleep(interval)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    p = argparse.ArgumentParser()
    p.add_argument(
        "--mock",
        action="store_true",
        default=True,
        help="use generated packets (default)",
    )
    p.add_argument(
        "--ble",
        action="store_true",
        help="read from BLE characteristic (needs hardware)",
    )
    p.add_argument(
        "--interval", type=float, default=0.5, help="seconds between packets"
    )
    p.add_argument(
        "--duration", type=float, default=10.0, help="total seconds to stream"
    )
    p.add_argument(
        "--out",
        type=str,
        default="data/sessions/demo.csv",
        help="optional CSV output path",
    )
    p.add_argument(
        "--verbose", action="store_true", help="enable DEBUG logging"
    )
    args = p.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    out = Path(args.out) if args.out else None

    if args.ble:
        if BleakClient is None:
            raise SystemExit("bleak not installed; run: pip install bleak")
        # Placeholder: keep mock for CI; wire up BLE later
        log.warning("--ble not implemented; falling back to --mock")
    run_mock(args.duration, args.interval, out)


if __name__ == "__main__":
    main()
