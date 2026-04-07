"""Central configuration loader for the Eye Adaptive Lens System host software.

Reads values from environment variables (and an optional .env file via
python-dotenv).  All values have safe defaults so the system runs out-of-the-
box without any .env file.

Usage::

    from host.pi.config import cfg
    print(cfg.lens_port)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger(__name__)

# Load .env if python-dotenv is installed (optional dependency)
try:
    from dotenv import load_dotenv  # type: ignore

    _env_file = Path(__file__).parents[2] / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
        log.debug("Loaded environment from %s", _env_file)
    else:
        log.debug(".env not found at %s — using environment variables only", _env_file)
except ImportError:
    log.debug("python-dotenv not installed; skipping .env loading")


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _get_int(key: str, default: int) -> int:
    raw = _get(key, str(default))
    try:
        return int(raw)
    except ValueError:
        log.warning("Invalid integer for %s=%r; using default %d", key, raw, default)
        return default


def _get_float(key: str, default: float) -> float:
    raw = _get(key, str(default))
    try:
        return float(raw)
    except ValueError:
        log.warning("Invalid float for %s=%r; using default %.4f", key, raw, default)
        return default


_HERE = Path(__file__).parent


@dataclass(frozen=True)
class AppConfig:
    """Immutable configuration object populated from environment variables."""

    # Lens controller
    lens_port: str = field(default_factory=lambda: _get("LENS_PORT") or "")
    lens_baud: int = field(default_factory=lambda: _get_int("LENS_BAUD", 115200))
    lens_timeout: float = field(default_factory=lambda: _get_float("LENS_TIMEOUT", 0.2))

    # BLE / telemetry
    ble_sensor_uuid: str = field(default_factory=lambda: _get("BLE_SENSOR_UUID"))
    telemetry_duration: float = field(default_factory=lambda: _get_float("TELEMETRY_DURATION", 10.0))
    telemetry_interval: float = field(default_factory=lambda: _get_float("TELEMETRY_INTERVAL", 0.5))

    # ML model
    ml_model_path: str = field(
        default_factory=lambda: _get("ML_MODEL_PATH") or str(_HERE / "models" / "therapy_lr.joblib")
    )

    # Vision therapy CV
    cv_profile: str = field(default_factory=lambda: _get("CV_PROFILE", "intermittent_occlusion_left"))
    cv_config_path: str = field(default_factory=lambda: _get("CV_CONFIG_PATH", "config/profiles.json"))
    cv_camera_index: int = field(default_factory=lambda: _get_int("CV_CAMERA_INDEX", 0))
    cv_log_dir: str = field(default_factory=lambda: _get("CV_LOG_DIR", "logs"))
    cv_flush_every: int = field(default_factory=lambda: _get_int("CV_FLUSH_EVERY", 50))

    # Data / storage
    data_dir: str = field(default_factory=lambda: _get("DATA_DIR", "data/sessions"))

    # Logging
    log_level: str = field(default_factory=lambda: _get("LOG_LEVEL", "INFO").upper())
    log_file: str = field(default_factory=lambda: _get("LOG_FILE"))


# Singleton — import and use as `from host.pi.config import cfg`
cfg = AppConfig()
