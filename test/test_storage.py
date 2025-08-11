from host.pi.storage import log_row
import csv, os
import tempfile


def test_log_row_writes_header_and_data():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "log.csv")
        log_row(p, {"a": 1, "b": 2})
        with open(p) as f:
            rows = list(csv.reader(f))
        assert rows[0] == ["a", "b"]
        assert rows[1] == ["1", "2"]
