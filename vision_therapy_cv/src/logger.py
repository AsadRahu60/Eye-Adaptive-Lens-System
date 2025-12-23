from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class SessionLogger:
    csv_path: str
    _writer: csv.DictWriter | None = None
    _fh: Any = None

    def open(self, fieldnames: list[str]) -> None:
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        self._fh = open(self.csv_path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._fh, fieldnames=fieldnames)
        self._writer.writeheader()

    def log(self, row: dict) -> None:
        if not self._writer:
            raise RuntimeError("Logger not opened. Call open() first.")
        self._writer.writerow(row)

    def close(self) -> None:
        if self._fh:
            self._fh.close()
            self._fh = None
            self._writer = None


def new_session_csv(log_dir: str, profile_name: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"session_{ts}_{profile_name}.csv"
    return os.path.join(log_dir, fname)