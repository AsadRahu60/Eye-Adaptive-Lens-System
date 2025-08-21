from __future__ import annotations
from pathlib import Path
from host.pi.ml.features import row_to_features
from host.pi.ml.model import TherapyModel
from host.pi.ml.policy_ml import ml_suggest


def test_row_to_features_shape():
    vec = row_to_features(
        {
            "dist_cm": 80,
            "lux": 200,
            "head_yaw": 10,
            "prev_duty": 0.2,
            "prev_defocus_dpt": 0.0,
            "comfort_0_10": 7.0,
        }
    )
    assert len(vec) == 6


def test_training_and_save(tmp_path: Path):
    # Tiny training sample
    X = [
        [80, 200, 5, 0.1, 0.0, 7.0],
        [40, 50, 20, 0.3, 0.2, 5.0],
    ]
    y = [1, 0]
    model = TherapyModel.new()
    model.fit(X, y)
    out = tmp_path / "m.joblib"
    model.save(str(out))
    assert out.exists()
    m2 = TherapyModel.load(str(out))
    p = m2.predict_proba([[80, 200, 5, 0.1, 0.0, 7.0]])[0]
    assert 0.0 <= p <= 1.0


def test_policy_clamps_and_fallback():
    ctx = {
        "dist_cm": 80,
        "lux": 200,
        "head_yaw": 5,
        "prev_duty": 0.2,
        "prev_defocus_dpt": 0.0,
        "comfort_0_10": 7.0,
    }
    # Fallback path (no model)
    duty, defocus = ml_suggest(ctx, 0.2, 0.0, None)
    assert 0.0 <= duty <= 0.5
    assert -0.5 <= defocus <= 0.5
