from host.pi.ml.model import TherapyModel
from host.pi.ml.policy_ml import ml_suggest

MODEL_PATH = "models/therapy_lr.joblib"
try:
    MODEL = TherapyModel.load(MODEL_PATH)
except Exception:
    MODEL = None


def compute_challenge(ctx_row, prev_duty, prev_defocus):
    # ctx_row should include: dist_cm, lux, head_yaw, comfort_0_10, prev_* keys
    return ml_suggest(ctx_row, prev_duty, prev_defocus, MODEL)


def classify(distance_cm: float, lux: float, motion: float) -> str:
    if distance_cm and distance_cm < 60:
        return "near"
    if lux and lux > 5000:
        return "outdoor"
    return "desk"
