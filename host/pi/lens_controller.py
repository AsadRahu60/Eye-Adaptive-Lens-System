from __future__ import annotations

import argparse
import sys
import time
from typing import Optional

try:
    import serial  # type: ignore
except Exception:  # pragma: no cover
    serial = None


class OptoLens:
    """Minimal controller for Optotune LD-4/ICC (placeholder protocol)."""

    def __init__(
        self, port: Optional[str], baud: int = 115200, timeout: float = 0.2
    ) -> None:
        self.port = port
        self.dry_run = port is None or serial is None
        self.ser = None
        if not self.dry_run:
            try:
                self.ser = serial.Serial(port, baud, timeout=timeout)  # type: ignore[attr-defined]
            except Exception:
                self.dry_run = True

    def send(self, cmd: str) -> str:
        if self.dry_run or self.ser is None:
            print(f"[DRY-RUN] -> {cmd}")
            return "OK"
        self.ser.write((cmd + "\n").encode())  # type: ignore[union-attr]
        return self.ser.readline().decode(errors="ignore").strip()  # type: ignore[union-attr]

    def set_diopter(self, dpt: float) -> str:
        # TODO: replace with exact LD-4/ICC command when you have the manual.
        return self.send(f"SET DIOP {dpt:.2f}")

    def close(self) -> None:
        if self.ser:
            self.ser.close()  # type: ignore[union-attr]


def ramp(current: float, target: float, max_rate_dpt_s: float, dt: float) -> float:
    delta = target - current
    if abs(delta) <= max_rate_dpt_s * dt:
        return target
    step = max(-max_rate_dpt_s * dt, min(max_rate_dpt_s * dt, delta))
    return current + step


def main() -> int:
    p = argparse.ArgumentParser(description="Control lens (dry-run if no --port).")
    p.add_argument("--port", default=None, help="e.g., /dev/ttyUSB0 or COM3")
    p.add_argument("--start", type=float, default=0.00)
    p.add_argument("--target", type=float, default=1.50)
    p.add_argument("--rate", type=float, default=0.25)
    p.add_argument("--period", type=float, default=0.05)
    args = p.parse_args()

    lens = OptoLens(args.port)
    try:
        current = args.start
        dt = args.period
        while True:
            current = ramp(current, args.target, args.rate, dt)
            resp = lens.set_diopter(current)
            print(f"set {current:.2f} dpt -> {resp}")
            if current == args.target:
                break
            time.sleep(dt)
        return 0
    finally:
        lens.close()


if __name__ == "__main__":
    sys.exit(main())
