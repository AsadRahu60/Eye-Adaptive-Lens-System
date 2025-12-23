from __future__ import annotations

import time


def now_s() -> float:
    return time.time()


def therapy_is_on(t_elapsed: float, cycle_sec: float, on_sec: float) -> bool:
    """
    Returns True/False if therapy is currently ON.
    If cycle_sec <= 0 -> always ON (continuous).
    """
    if cycle_sec <= 0:
        return True
    if on_sec <= 0:
        return False
    phase = t_elapsed % cycle_sec
    return phase < on_sec