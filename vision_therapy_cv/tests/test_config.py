"""Tests for vision_therapy_cv profile loading and validation utilities."""

from __future__ import annotations

import json
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parents[1]))  # ensure src/ is importable

from src.utils import clip_effects, load_profiles, validate_profile, Profile


# ─── Fixtures ────────────────────────────────────────────────────────────────

MINIMAL_PROFILE = {
    "description": "Test profile",
    "duration_sec": 60,
    "cycle_sec": 30.0,
    "on_sec": 15.0,
    "target_eye": "left",
    "effects": {
        "occlusion_strength": 0.8,
        "blur_sigma": 3.0,
        "contrast_alpha": 1.2,
        "brightness_beta": 10,
    },
    "safety": {
        "max_occlusion_strength": 0.9,
        "max_blur_sigma": 6.0,
        "max_contrast_alpha": 2.0,
        "min_contrast_alpha": 0.5,
        "max_abs_brightness_beta": 80,
    },
}


@pytest.fixture()
def profiles_json(tmp_path: Path) -> Path:
    """Write a minimal profiles.json to a temp directory and return its path."""
    p = tmp_path / "profiles.json"
    p.write_text(json.dumps({"test_profile": MINIMAL_PROFILE}), encoding="utf-8")
    return p


# ─── load_profiles ────────────────────────────────────────────────────────────

class TestLoadProfiles:
    def test_loads_valid_json(self, profiles_json: Path) -> None:
        result = load_profiles(str(profiles_json))
        assert "test_profile" in result

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_profiles(str(tmp_path / "nonexistent.json"))

    def test_raises_on_empty_object(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.json"
        p.write_text("{}", encoding="utf-8")
        with pytest.raises(ValueError, match="non-empty"):
            load_profiles(str(p))

    def test_raises_on_non_dict(self, tmp_path: Path) -> None:
        p = tmp_path / "list.json"
        p.write_text("[]", encoding="utf-8")
        with pytest.raises(ValueError, match="non-empty"):
            load_profiles(str(p))


# ─── validate_profile ────────────────────────────────────────────────────────

class TestValidateProfile:
    def test_returns_profile_dataclass(self) -> None:
        result = validate_profile("test_profile", MINIMAL_PROFILE)
        assert isinstance(result, Profile)

    def test_correct_field_types(self) -> None:
        p = validate_profile("test_profile", MINIMAL_PROFILE)
        assert isinstance(p.duration_sec, int)
        assert isinstance(p.cycle_sec, float)
        assert isinstance(p.on_sec, float)
        assert isinstance(p.target_eye, str)

    def test_valid_target_eyes(self) -> None:
        for eye in ("left", "right", "both"):
            raw = {**MINIMAL_PROFILE, "target_eye": eye}
            result = validate_profile("p", raw)
            assert result.target_eye == eye

    def test_invalid_target_eye_raises(self) -> None:
        raw = {**MINIMAL_PROFILE, "target_eye": "center"}
        with pytest.raises(ValueError, match="target_eye"):
            validate_profile("p", raw)

    def test_missing_key_raises(self) -> None:
        for key in ["description", "duration_sec", "cycle_sec", "on_sec", "target_eye", "effects", "safety"]:
            raw = {k: v for k, v in MINIMAL_PROFILE.items() if k != key}
            with pytest.raises(ValueError, match=key):
                validate_profile("p", raw)

    def test_name_stored_on_profile(self) -> None:
        p = validate_profile("my_profile", MINIMAL_PROFILE)
        assert p.name == "my_profile"


# ─── clip_effects ─────────────────────────────────────────────────────────────

class TestClipEffects:
    def test_values_within_safety_bounds_unchanged(self) -> None:
        effects = {"occlusion_strength": 0.5, "blur_sigma": 2.0, "contrast_alpha": 1.0, "brightness_beta": 0}
        safety = {
            "max_occlusion_strength": 0.9,
            "max_blur_sigma": 6.0,
            "max_contrast_alpha": 2.0,
            "min_contrast_alpha": 0.5,
            "max_abs_brightness_beta": 80,
        }
        result = clip_effects(effects, safety)
        assert result["occlusion_strength"] == pytest.approx(0.5)
        assert result["blur_sigma"] == pytest.approx(2.0)
        assert result["contrast_alpha"] == pytest.approx(1.0)
        assert result["brightness_beta"] == 0

    def test_occlusion_clamped_to_max(self) -> None:
        effects = {"occlusion_strength": 1.5, "blur_sigma": 0.0, "contrast_alpha": 1.0, "brightness_beta": 0}
        safety = {"max_occlusion_strength": 0.8, "max_blur_sigma": 6.0,
                  "max_contrast_alpha": 2.0, "min_contrast_alpha": 0.5, "max_abs_brightness_beta": 80}
        result = clip_effects(effects, safety)
        assert result["occlusion_strength"] == pytest.approx(0.8)

    def test_blur_clamped_to_max(self) -> None:
        effects = {"occlusion_strength": 0.0, "blur_sigma": 99.0, "contrast_alpha": 1.0, "brightness_beta": 0}
        safety = {"max_occlusion_strength": 1.0, "max_blur_sigma": 5.0,
                  "max_contrast_alpha": 2.0, "min_contrast_alpha": 0.5, "max_abs_brightness_beta": 80}
        result = clip_effects(effects, safety)
        assert result["blur_sigma"] == pytest.approx(5.0)

    def test_negative_occlusion_clamped_to_zero(self) -> None:
        effects = {"occlusion_strength": -0.5, "blur_sigma": 0.0, "contrast_alpha": 1.0, "brightness_beta": 0}
        safety = {"max_occlusion_strength": 1.0, "max_blur_sigma": 6.0,
                  "max_contrast_alpha": 2.0, "min_contrast_alpha": 0.5, "max_abs_brightness_beta": 80}
        result = clip_effects(effects, safety)
        assert result["occlusion_strength"] == pytest.approx(0.0)

    def test_brightness_clamped_positive(self) -> None:
        effects = {"occlusion_strength": 0.0, "blur_sigma": 0.0, "contrast_alpha": 1.0, "brightness_beta": 200}
        safety = {"max_occlusion_strength": 1.0, "max_blur_sigma": 6.0,
                  "max_contrast_alpha": 2.0, "min_contrast_alpha": 0.5, "max_abs_brightness_beta": 80}
        result = clip_effects(effects, safety)
        assert result["brightness_beta"] == 80

    def test_brightness_clamped_negative(self) -> None:
        effects = {"occlusion_strength": 0.0, "blur_sigma": 0.0, "contrast_alpha": 1.0, "brightness_beta": -200}
        safety = {"max_occlusion_strength": 1.0, "max_blur_sigma": 6.0,
                  "max_contrast_alpha": 2.0, "min_contrast_alpha": 0.5, "max_abs_brightness_beta": 80}
        result = clip_effects(effects, safety)
        assert result["brightness_beta"] == -80

    def test_contrast_clamped_to_min(self) -> None:
        effects = {"occlusion_strength": 0.0, "blur_sigma": 0.0, "contrast_alpha": 0.1, "brightness_beta": 0}
        safety = {"max_occlusion_strength": 1.0, "max_blur_sigma": 6.0,
                  "max_contrast_alpha": 2.0, "min_contrast_alpha": 0.5, "max_abs_brightness_beta": 80}
        result = clip_effects(effects, safety)
        assert result["contrast_alpha"] == pytest.approx(0.5)

    def test_missing_safety_keys_use_defaults(self) -> None:
        """clip_effects should not crash when safety dict has missing keys."""
        effects = {"occlusion_strength": 0.5, "blur_sigma": 2.0, "contrast_alpha": 1.0, "brightness_beta": 10}
        result = clip_effects(effects, {})  # empty safety dict
        assert 0.0 <= result["occlusion_strength"] <= 1.0
