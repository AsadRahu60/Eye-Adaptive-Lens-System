#!/usr/bin/env python3
from __future__ import annotations
import csv
import random
from pathlib import Path

RNG = random.Random(42)


def synth_row() -> dict:
    dist_cm = RNG.uniform(35.0, 120.0)
    lux = RNG.uniform(30.0, 600.0)
    yaw = RNG.uniform(-50.0, 50.0)
    prev_duty = RNG.choice([0.0, 0.05, 0.10, 0.15, 0.20, 0.25])
    prev_defocus = RNG.choice([0.0, 0.10, -0.10, 0.20, -0.20])
    comfort = RNG.uniform(4.0, 9.5)

    # Simple ground-truth heuristic for label:
    # success if moderate duty and decent comfort and reasonable distance
    success = (prev_duty <= 0.25) and (comfort >= 6.0) and (50.0 <= dist_cm <= 100.0)
    y = 1 if success else 0

    return {
        "dist_cm": round(dist_cm, 1),
        "lux": round(lux, 1),
        "head_yaw": round(yaw, 1),
        "prev_duty": round(prev_duty, 2),
        "prev_defocus_dpt": round(prev_defocus, 2),
        "comfort_0_10": round(comfort, 1),
        "task_success": y,
    }


def main() -> None:
    out = Path("data/sessions/synth_training.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "dist_cm",
                "lux",
                "head_yaw",
                "prev_duty",
                "prev_defocus_dpt",
                "comfort_0_10",
                "task_success",
            ],
        )
        w.writeheader()
        for _ in range(1200):
            w.writerow(synth_row())
    print(f"[synth] wrote {out}")


if __name__ == "__main__":
    main()
