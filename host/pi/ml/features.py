from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Union

log = logging.getLogger(__name__)

FEATURE_ORDER: List[str] = [
    "dist_cm",
    "lux",
    "abs_yaw_deg",
    "prev_duty",
    "prev_defocus_dpt",
    "comfort_0_10",
]

# Sensible defaults used when a key is missing or unparseable
_DEFAULTS: Dict[str, float] = {
    "dist_cm": 80.0,
    "lux": 200.0,
    "head_yaw": 0.0,
    "prev_duty": 0.2,
    "prev_defocus_dpt": 0.0,
    "comfort_0_10": 7.0,
}


def _safe_float(value: Union[str, float, int, None], key: str, default: float) -> float:
    """Convert *value* to float, returning *default* on failure."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        log.warning("Invalid value for feature '%s': %r — using default %.2f", key, value, default)
        return default


def row_to_features(row: Dict[str, object]) -> List[float]:
    """Convert a data row dict into a fixed-length feature vector.

    Missing or unparseable values are replaced with safe defaults rather than
    raising exceptions, so the pipeline degrades gracefully on bad sensor data.
    """
    dist_cm = _safe_float(row.get("dist_cm"), "dist_cm", _DEFAULTS["dist_cm"])
    lux = _safe_float(row.get("lux"), "lux", _DEFAULTS["lux"])
    yaw = _safe_float(row.get("head_yaw"), "head_yaw", _DEFAULTS["head_yaw"])
    prev_duty = _safe_float(row.get("prev_duty"), "prev_duty", _DEFAULTS["prev_duty"])
    prev_defocus = _safe_float(row.get("prev_defocus_dpt"), "prev_defocus_dpt", _DEFAULTS["prev_defocus_dpt"])
    comfort = _safe_float(row.get("comfort_0_10"), "comfort_0_10", _DEFAULTS["comfort_0_10"])
    return [dist_cm, lux, abs(yaw), prev_duty, prev_defocus, comfort]


def batch_to_features(rows: Iterable[Dict[str, object]]) -> List[List[float]]:
    """Map a batch of dict rows to a feature matrix."""
    return [row_to_features(r) for r in rows]
