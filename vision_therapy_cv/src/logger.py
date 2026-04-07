from __future__ import annotations

import csv
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

log = logging.getLogger(__name__)

# Flush to disk every N rows to reduce per-frame I/O on Raspberry Pi
_DEFAULT_FLUSH_EVERY = 50


@dataclass
class SessionLogger:
    """CSV session logger with write-buffering for low-I/O environments.

    Args:
        csv_path: Path to the output CSV file.
        flush_every: Number of rows to buffer before flushing to disk.
                     Set to 1 to flush every row (max safety, lowest performance).
    """

    csv_path: str
    flush_every: int = _DEFAULT_FLUSH_EVERY
    _writer: Optional[csv.DictWriter] = field(default=None, repr=False)
    _fh: Any = field(default=None, repr=False)
    _buffer: List[Dict[str, Any]] = field(default_factory=list, repr=False)
    _rows_written: int = field(default=0, repr=False)

    def open(self, fieldnames: List[str]) -> None:
        """Open the CSV file and write the header row."""
        dir_path = os.path.dirname(self.csv_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        self._fh = open(self.csv_path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._fh, fieldnames=fieldnames)
        self._writer.writeheader()
        self._fh.flush()
        log.debug("SessionLogger opened: %s (flush_every=%d)", self.csv_path, self.flush_every)

    def log(self, row: Dict[str, Any]) -> None:
        """Buffer *row* and flush to disk every *flush_every* rows."""
        if not self._writer:
            raise RuntimeError("SessionLogger not opened. Call open() first.")
        self._buffer.append(row)
        if len(self._buffer) >= self.flush_every:
            self._flush()

    def _flush(self) -> None:
        """Write buffered rows to disk immediately."""
        if self._writer and self._buffer:
            self._writer.writerows(self._buffer)
            self._fh.flush()
            self._rows_written += len(self._buffer)
            log.debug("Flushed %d rows (total %d) to %s", len(self._buffer), self._rows_written, self.csv_path)
            self._buffer.clear()

    def close(self) -> None:
        """Flush any remaining buffered rows and close the file."""
        if self._fh:
            self._flush()  # write any remaining buffered rows
            self._fh.close()
            self._fh = None
            self._writer = None
            log.info("SessionLogger closed: %s (%d rows written)", self.csv_path, self._rows_written)


def new_session_csv(log_dir: str, profile_name: str) -> str:
    """Return a timestamped CSV path for a new session."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"session_{ts}_{profile_name}.csv"
    return os.path.join(log_dir, fname)