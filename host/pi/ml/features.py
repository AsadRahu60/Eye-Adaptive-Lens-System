from __future__ import annotations
from typing import Dict, Iterable, List
# import math


FEATURE_ORDER: List[str] = [
    "dist_cm",
    "lux",
    "abs_yaw_deg",
    "prev_duty",
    "prev_defocus_dpt",
    "comfort_0_10",
]


def row_to_features(row: Dict[str, float]) -> List[float]:
    """Convert a data row dict into a fixed feature vector."""
    dist_cm = float(row.get("dist_cm", 80.0))
    lux = float(row.get("lux", 200.0))
    yaw = float(row.get("head_yaw", 0.0))
    prev_duty = float(row.get("prev_duty", 0.2))
    prev_defocus = float(row.get("prev_defocus_dpt", 0.0))
    comfort = float(row.get("comfort_0_10", 7.0))
    return [dist_cm, lux, abs(yaw), prev_duty, prev_defocus, comfort]


def batch_to_features(rows: Iterable[Dict[str, float]]) -> List[List[float]]:
    """Map a batch of dict rows to feature matrix."""
    return [row_to_features(r) for r in rows]
