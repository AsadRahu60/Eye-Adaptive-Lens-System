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
        self,
        port: Optional[str],
        baud: int = 115200,
        timeout: float = 0.2,
    ) -> None:
        self.port = port
        self.dry_run = port is None or serial is None
        self.ser = None
        if not self.dry_run:
            try:
                # type: ignore[attr-defined]
                self.ser = serial.Serial(port, baud, timeout=timeout)
            except Exception:
                self.dry_run = True

    def send(self, cmd: str) -> str:
        if self.dry_run or self.ser is None:
            print(f"[DRY-RUN] -> {cmd}")
            return "OK"
        # type: ignore[union-attr]
        self.ser.write((cmd + "\n").encode())
        # type: ignore[union-attr]
        return self.ser.readline().decode(errors="ignore").strip()

    def set_diopter(self, dpt: float) -> str:
        # TODO: replace with exact LD-4/ICC command when you have the manual.
        return self.send(f"SET DIOP {dpt:.2f}")

    def close(self) -> None:
        if self.ser:
            # type: ignore[union-attr]
            self.ser.close()


def ramp(current: float, target: float, max_rate_dpt_s: float, dt: float) -> float:
    delta = target - current
    if abs(delta) <= max_rate_dpt_s * dt:
        return target
    step = max(-max_rate_dpt_s * dt, min(max_rate_dpt_s * dt, delta))
    return current + step


def ramp_focus(
    start_dpt: float,
    end_dpt: float,
    duration_s: float,
    steps: int = 20,
    apply=None,
    sleep: bool = False,
):
    """
    Create a linear ramp of focus values from start_dpt to end_dpt.

    - steps: number of intervals (path will have steps+1 points)
    - apply: optional callable applied to each setpoint (e.g., lens.set_diopter)
    - sleep: if True, sleep duration_s/steps between points (avoid in tests)
    Returns: list of setpoints (floats)
    """
    if steps <= 0:
        # Edge case: jump directly to target
        path = [end_dpt]
        if apply:
            apply(end_dpt)
        return path

    dt = duration_s / steps if duration_s > 0 else 0.0
    path = []
    for i in range(steps + 1):
        level = start_dpt + (end_dpt - start_dpt) * (i / steps)
        path.append(level)
        if apply:
            apply(level)
        else:
            # Dry-run print to make behavior observable without hardware
            print(f"[RAMP] {level:.2f} dpt")
        if sleep and dt > 0:
            time.sleep(dt)
    return path


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
