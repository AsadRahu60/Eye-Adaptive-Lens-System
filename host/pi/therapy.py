from typing import Dict, Tuple


def policy(mode: str, base_L: float, base_R: float) -> Tuple[float, float, Dict]:
    shutters = {"L": 0.0, "R": 0.0, "period_ms": 30000}
    if mode == "near":
        shutters["R"] = 50.0
    return base_L, base_R, shutters

