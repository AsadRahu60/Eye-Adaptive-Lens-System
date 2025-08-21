from __future__ import annotations
from typing import Dict, Optional, Tuple
from .features import row_to_features
from .model import TherapyModel


# Safety bounds (conservative)
MAX_DUTY = 0.5  # max occlusion duty
MIN_DUTY = 0.0
DUTY_STEP = 0.05

MAX_DEFOCUS = 0.50  # +/- D allowed by policy
DEFOCUS_STEP = 0.10

UP_THRESH = 0.70  # if p_improve high -> increase challenge a bit
DOWN_THRESH = 0.30  # if p_improve low  -> decrease challenge
MIN_COMFORT = 6.0  # require min comfort to push challenge up


def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def rule_based_suggest(prev_duty: float, prev_defocus: float) -> Tuple[float, float]:
    """Simple fallback: gentle nudge toward mild challenge."""
    duty = clamp(prev_duty + DUTY_STEP, MIN_DUTY, MAX_DUTY)
    defocus = clamp(prev_defocus + 0.0, -MAX_DEFOCUS, MAX_DEFOCUS)
    return duty, defocus


def ml_suggest(
    ctx_row: Dict[str, float],
    prev_duty: float,
    prev_defocus: float,
    model: Optional[TherapyModel],
) -> Tuple[float, float]:
    """Return (duty, defocus_dpt) suggestion with hard safety clamps.

    ctx_row expects keys: dist_cm, lux, head_yaw, prev_duty, prev_defocus_dpt,
    comfort_0_10.
    """
    # Fallback if no model
    if model is None:
        return rule_based_suggest(prev_duty, prev_defocus)

    feats = [row_to_features(ctx_row)]
    p = model.predict_proba(feats)[0]
    comfort = float(ctx_row.get("comfort_0_10", 7.0))

    duty = prev_duty
    defocus = prev_defocus

    if p >= UP_THRESH and comfort >= MIN_COMFORT:
        duty += DUTY_STEP
        # keep defocus neutral for now (optical comfort first)
    elif p <= DOWN_THRESH or comfort < MIN_COMFORT:
        duty -= DUTY_STEP
        # reduce optical challenge if comfort is low
        defocus -= DEFOCUS_STEP

    duty = clamp(duty, MIN_DUTY, MAX_DUTY)
    defocus = clamp(defocus, -MAX_DEFOCUS, MAX_DEFOCUS)
    return duty, defocus
