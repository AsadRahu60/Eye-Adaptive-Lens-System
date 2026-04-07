from __future__ import annotations

import logging
from typing import Dict, Tuple

log = logging.getLogger(__name__)

# Valid therapy modes and their default shutter duty-cycles (%)
_MODE_POLICIES: Dict[str, Dict[str, float]] = {
    "near": {"L": 0.0, "R": 50.0, "period_ms": 30_000},
    "desk": {"L": 0.0, "R": 20.0, "period_ms": 60_000},
    "outdoor": {"L": 0.0, "R": 0.0, "period_ms": 0},
}

VALID_MODES = frozenset(_MODE_POLICIES.keys())


def policy(mode: str, base_L: float, base_R: float) -> Tuple[float, float, Dict]:
    """Return (lens_L_dpt, lens_R_dpt, shutter_config) for *mode*.

    Args:
        mode: Context classification string — one of 'near', 'desk', 'outdoor'.
        base_L: Baseline left-eye diopter setpoint.
        base_R: Baseline right-eye diopter setpoint.

    Returns:
        Tuple of (left_dpt, right_dpt, shutter_dict).
    """
    if mode not in VALID_MODES:
        log.warning("Unknown therapy mode '%s'; defaulting to 'desk'", mode)
        mode = "desk"

    shutters = dict(_MODE_POLICIES[mode])
    log.debug("Therapy policy: mode=%s shutters=%s", mode, shutters)
    return base_L, base_R, shutters
