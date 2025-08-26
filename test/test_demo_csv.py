from pathlib import Path
import csv 
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
SAMPLE = REPO / "data/samples/demo_session_small.csv"
RAW = REPO / "data/demo_session.csv"
DEMO = REPO / "host/pi/telemetry_demo.py"


def _ensure_sample():
    if SAMPLE.exists():
        return
    SAMPLE.parent.mkdir(parents=True, exist_ok=True)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    # Generate a tiny CSV in mock mode (no hardware)
    subprocess.run(
        [
            sys.executable,
            str(DEMO),
            "--mock",
            "--duration",
            "3",
            "--interval",
            "1",
            "--out",
            str(RAW),
        ],
        check=True,
        cwd=REPO,
    )
    # Keep only ~50 lines for the tracked sample
    with RAW.open() as fin, SAMPLE.open("w") as fout:
        for i, line in enumerate(fin):
            fout.write(line)
            if i >= 50:
                break


def test_sample_csv_exists_and_has_header():
    _ensure_sample()
    assert SAMPLE.exists(), f"Missing sample CSV: {SAMPLE}"
    with SAMPLE.open() as f:
        reader = csv.DictReader(f)
        for col in ("ts", "dist_cm"):
            assert col in reader.fieldnames, f"Missing column {col}"
        # read a few rows
        rows = [next(reader) for _ in range(3)]
        assert len(rows) > 0
