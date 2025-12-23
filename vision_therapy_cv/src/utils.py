from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Profile:
    name: str
    description: str
    duration_sec: int
    cycle_sec: float
    on_sec: float
    target_eye: str
    effects: dict[str, Any]
    safety: dict[str, Any]


def load_profiles(path: str) -> dict[str, dict]:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not data:
        raise ValueError("profiles.json must be a non-empty JSON object.")
    return data


def validate_profile(name: str, raw: dict) -> Profile:
    required = ["description", "duration_sec", "cycle_sec", "on_sec", "target_eye", "effects", "safety"]
    for k in required:
        if k not in raw:
            raise ValueError(f"Profile '{name}' missing key: {k}")

    target_eye = raw["target_eye"]
    if target_eye not in ("left", "right", "both"):
        raise ValueError(f"Profile '{name}' target_eye must be left/right/both")

    eff = raw["effects"]
    saf = raw["safety"]

    # Apply safety clipping at runtime too, but validate here
    return Profile(
        name=name,
        description=str(raw["description"]),
        duration_sec=int(raw["duration_sec"]),
        cycle_sec=float(raw["cycle_sec"]),
        on_sec=float(raw["on_sec"]),
        target_eye=target_eye,
        effects=dict(eff),
        safety=dict(saf),
    )


def clip_effects(effects: dict, safety: dict) -> dict:
    # Safety defaults if missing
    max_occ = float(safety.get("max_occlusion_strength", 1.0))
    max_blur = float(safety.get("max_blur_sigma", 6.0))
    max_a = float(safety.get("max_contrast_alpha", 2.0))
    min_a = float(safety.get("min_contrast_alpha", 0.5))
    max_b = int(safety.get("max_abs_brightness_beta", 80))

    occlusion_strength = float(effects.get("occlusion_strength", 0.0))
    blur_sigma = float(effects.get("blur_sigma", 0.0))
    contrast_alpha = float(effects.get("contrast_alpha", 1.0))
    brightness_beta = int(effects.get("brightness_beta", 0))

    occlusion_strength = max(0.0, min(max_occ, occlusion_strength))
    blur_sigma = max(0.0, min(max_blur, blur_sigma))
    contrast_alpha = max(min_a, min(max_a, contrast_alpha))
    brightness_beta = max(-max_b, min(max_b, brightness_beta))

    return {
        "occlusion_strength": occlusion_strength,
        "blur_sigma": blur_sigma,
        "contrast_alpha": contrast_alpha,
        "brightness_beta": brightness_beta,
    }