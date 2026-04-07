from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Dict

log = logging.getLogger(__name__)


def log_row(path: str, row: Dict[str, object]) -> None:
    """Append *row* to a CSV at *path*, writing a header if the file is new.

    The parent directory is created automatically if it does not exist.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    write_header = not p.exists() or p.stat().st_size == 0

    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            w.writeheader()
            log.debug("Created CSV with header at %s", path)
        w.writerow(row)
