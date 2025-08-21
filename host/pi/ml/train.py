#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path
from typing import List, Tuple
from .features import row_to_features
from .model import TherapyModel


def load_csv(path: Path) -> Tuple[List[List[float]], List[int]]:
    X: List[List[float]] = []
    y: List[int] = []
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            X.append(row_to_features(row))
            y.append(int(row.get("task_success", 0)))
    return X, y


def main() -> None:
    data_path = Path("data/sessions/synth_training.csv")
    if not data_path.exists():
        raise SystemExit(
            "data not found. Run: python host/pi/ml/make_synthetic.py"
        )
    X, y = load_csv(data_path)
    model = TherapyModel.new()
    model.fit(X, y)
    Path("models").mkdir(exist_ok=True)
    out = "models/therapy_lr.joblib"
    model.save(out)
    print(f"[train] saved model to {out} (n={len(X)})")


if __name__ == "__main__":
    main()
