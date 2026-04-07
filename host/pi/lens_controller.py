from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import Callable, List, Optional

log = logging.getLogger(__name__)

try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover
    serial = None
    log.debug("pyserial not installed; OptoLens will operate in dry-run mode")


class OptoLens:
    """Minimal controller for Optotune LD-4/ICC (placeholder protocol).

    Automatically falls back to dry-run mode when:
    - *port* is None, or
    - pyserial is not installed, or
    - the serial port cannot be opened.
    """

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
                self.ser = serial.Serial(port, baud, timeout=timeout)  # type: ignore[attr-defined]
                log.info("Opened serial port %s at %d baud", port, baud)
            except serial.SerialException as exc:  # type: ignore[attr-defined]
                log.error("Failed to open serial port %s: %s — switching to dry-run", port, exc)
                self.dry_run = True

    def send(self, cmd: str) -> str:
        """Send a command string and return the response (or 'OK' in dry-run)."""
        if self.dry_run or self.ser is None:
            log.debug("[DRY-RUN] -> %s", cmd)
            return "OK"
        self.ser.write((cmd + "\n").encode())  # type: ignore[union-attr]
        return self.ser.readline().decode(errors="ignore").strip()  # type: ignore[union-attr]

    def set_diopter(self, dpt: float) -> str:
        """Set lens power in diopters.

        NOTE: Replace 'SET DIOP' with the exact LD-4/ICC command once the
        hardware manual is available.
        """
        return self.send(f"SET DIOP {dpt:.2f}")

    def close(self) -> None:
        """Release the serial port if open."""
        if self.ser:
            self.ser.close()  # type: ignore[union-attr]
            log.debug("Serial port %s closed", self.port)


def ramp(current: float, target: float, max_rate_dpt_s: float, dt: float) -> float:
    """Advance *current* toward *target* by at most *max_rate_dpt_s* × *dt*."""
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
    apply: Optional[Callable[[float], None]] = None,
    sleep: bool = False,
) -> List[float]:
    """Create a linear ramp of focus values from *start_dpt* to *end_dpt*.

    Args:
        start_dpt: Starting diopter value.
        end_dpt: Target diopter value.
        duration_s: Total ramp duration in seconds.
        steps: Number of intervals (path will have steps+1 points).
        apply: Optional callable applied to each setpoint (e.g. lens.set_diopter).
        sleep: If True, sleep between steps — avoid in unit tests.

    Returns:
        List of diopter setpoints.
    """
    if steps <= 0:
        path = [end_dpt]
        if apply:
            apply(end_dpt)
        return path

    dt = duration_s / steps if duration_s > 0 else 0.0
    path: List[float] = []
    for i in range(steps + 1):
        level = start_dpt + (end_dpt - start_dpt) * (i / steps)
        path.append(level)
        if apply:
            apply(level)
        else:
            log.debug("[RAMP] %.2f dpt", level)
        if sleep and dt > 0:
            time.sleep(dt)
    return path


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
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
            log.info("set %.2f dpt -> %s", current, resp)
            if current == args.target:
                break
            time.sleep(dt)
        return 0
    finally:
        lens.close()


if __name__ == "__main__":
    sys.exit(main())
