from pathlib import Path
import csv

SAMPLE = Path("data/samples/demo_session_small.csv")


def test_sample_csv_exists_and_has_header():
    assert SAMPLE.exists(), f"Missing sample CSV: {SAMPLE}"
    with SAMPLE.open() as f:
        reader = csv.DictReader(f)
        # minimal required columns
        for col in ("ts", "dist_cm"):
            assert col in reader.fieldnames, f"Missing column {col}"
        # read a few rows
        rows = [next(reader) for _ in range(3)]
        assert len(rows) > 0
