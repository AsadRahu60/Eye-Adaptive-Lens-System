from __future__ import annotations

import logging
from pathlib import Path

from host.pi.ml.model import TherapyModel
from host.pi.ml.policy_ml import ml_suggest

log = logging.getLogger(__name__)

# Resolve model path relative to this file so it works regardless of cwd
_HERE = Path(__file__).parent
MODEL_PATH = _HERE / "models" / "therapy_lr.joblib"

try:
    MODEL: TherapyModel | None = TherapyModel.load(str(MODEL_PATH))
    log.info("Loaded therapy model from %s", MODEL_PATH)
except FileNotFoundError:
    log.warning("Model file not found at %s — running without ML (rule-based fallback)", MODEL_PATH)
    MODEL = None
except Exception as exc:  # noqa: BLE001
    log.error("Failed to load therapy model: %s", exc, exc_info=True)
    MODEL = None


def compute_challenge(
    ctx_row: dict,
    prev_duty: float,
    prev_defocus: float,
) -> tuple[float, float]:
    """Return (duty, defocus_dpt) suggestion using ML model or rule-based fallback.

    ctx_row should include: dist_cm, lux, head_yaw, comfort_0_10, prev_* keys.
    """
    return ml_suggest(ctx_row, prev_duty, prev_defocus, MODEL)


def classify(distance_cm: float, lux: float, motion: float) -> str:  # noqa: ARG001
    """Classify current context into one of: near, outdoor, desk."""
    if distance_cm and distance_cm < 60:
        return "near"
    if lux and lux > 5000:
        return "outdoor"
    return "desk"
