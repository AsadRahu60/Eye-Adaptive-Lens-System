"""Tests for vision_therapy_cv image effects (occlusion, blur, contrast)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))  # ensure src/ is importable

from src.effects import apply_blur, apply_contrast, apply_occlusion


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_frame(h: int = 100, w: int = 100, fill: int = 128) -> np.ndarray:
    """Return a solid-colour BGR frame."""
    return np.full((h, w, 3), fill, dtype=np.uint8)


def left_half(frame: np.ndarray) -> np.ndarray:
    return frame[:, : frame.shape[1] // 2]


def right_half(frame: np.ndarray) -> np.ndarray:
    return frame[:, frame.shape[1] // 2 :]


# ─── apply_occlusion ─────────────────────────────────────────────────────────

class TestApplyOcclusion:
    def test_zero_strength_returns_original(self) -> None:
        frame = make_frame(fill=200)
        result = apply_occlusion(frame, "left", 0.0)
        np.testing.assert_array_equal(result, frame)

    def test_full_occlusion_left_darkens_left_half(self) -> None:
        frame = make_frame(fill=200)
        result = apply_occlusion(frame, "left", 1.0)
        assert left_half(result).mean() == pytest.approx(0.0, abs=1)
        # Right half should be unchanged
        np.testing.assert_array_equal(right_half(result), right_half(frame))

    def test_full_occlusion_right_darkens_right_half(self) -> None:
        frame = make_frame(fill=200)
        result = apply_occlusion(frame, "right", 1.0)
        assert right_half(result).mean() == pytest.approx(0.0, abs=1)
        np.testing.assert_array_equal(left_half(result), left_half(frame))

    def test_full_occlusion_both_darkens_whole_frame(self) -> None:
        frame = make_frame(fill=200)
        result = apply_occlusion(frame, "both", 1.0)
        assert result.mean() == pytest.approx(0.0, abs=1)

    def test_partial_occlusion_reduces_brightness(self) -> None:
        frame = make_frame(fill=200)
        result = apply_occlusion(frame, "left", 0.5)
        assert left_half(result).mean() < left_half(frame).mean()

    def test_strength_clamped_above_one(self) -> None:
        frame = make_frame(fill=200)
        result = apply_occlusion(frame, "left", 5.0)
        # Should behave same as strength=1.0
        expected = apply_occlusion(frame, "left", 1.0)
        np.testing.assert_array_equal(result, expected)

    def test_output_shape_matches_input(self) -> None:
        frame = make_frame(80, 120)
        result = apply_occlusion(frame, "left", 0.7)
        assert result.shape == frame.shape

    def test_input_frame_not_mutated(self) -> None:
        frame = make_frame(fill=200)
        original = frame.copy()
        apply_occlusion(frame, "left", 1.0)
        np.testing.assert_array_equal(frame, original)


# ─── apply_blur ──────────────────────────────────────────────────────────────

class TestApplyBlur:
    def test_zero_sigma_returns_original(self) -> None:
        frame = make_frame(fill=150)
        result = apply_blur(frame, "left", 0.0)
        np.testing.assert_array_equal(result, frame)

    def test_blur_reduces_sharpness_on_left(self) -> None:
        # Create a sharp vertical edge *inside* the left ROI (at col 15 of 50)
        # so GaussianBlur has actual gradients to smooth
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[:, 15:50] = 255          # right portion of left-ROI is white, left portion black
        result = apply_blur(frame, "left", 5.0)
        lh = left_half(result)
        # After blurring, there must be intermediate pixel values (not only 0 or 255)
        unique_vals = np.unique(lh)
        assert len(unique_vals) > 2, "Blur should introduce intermediate pixel values"

    def test_right_half_unchanged_when_blurring_left(self) -> None:
        frame = make_frame(fill=100)
        result = apply_blur(frame, "left", 3.0)
        np.testing.assert_array_equal(right_half(result), right_half(frame))

    def test_output_shape_preserved(self) -> None:
        frame = make_frame(80, 120)
        result = apply_blur(frame, "both", 2.0)
        assert result.shape == frame.shape

    def test_input_frame_not_mutated(self) -> None:
        frame = make_frame(fill=100)
        original = frame.copy()
        apply_blur(frame, "right", 4.0)
        np.testing.assert_array_equal(frame, original)


# ─── apply_contrast ──────────────────────────────────────────────────────────

class TestApplyContrast:
    def test_alpha_one_beta_zero_returns_original(self) -> None:
        frame = make_frame(fill=128)
        result = apply_contrast(frame, "left", alpha=1.0, beta=0)
        np.testing.assert_array_equal(result, frame)

    def test_positive_beta_increases_brightness_on_left(self) -> None:
        frame = make_frame(fill=100)
        result = apply_contrast(frame, "left", alpha=1.0, beta=30)
        assert left_half(result).mean() > left_half(frame).mean()
        np.testing.assert_array_equal(right_half(result), right_half(frame))

    def test_negative_beta_decreases_brightness_on_left(self) -> None:
        frame = make_frame(fill=150)
        result = apply_contrast(frame, "left", alpha=1.0, beta=-50)
        assert left_half(result).mean() < left_half(frame).mean()

    def test_output_clipped_to_uint8_range(self) -> None:
        frame = make_frame(fill=250)
        result = apply_contrast(frame, "both", alpha=2.0, beta=100)
        assert result.max() <= 255
        assert result.min() >= 0

    def test_output_shape_preserved(self) -> None:
        frame = make_frame(80, 120)
        result = apply_contrast(frame, "right", alpha=1.5, beta=-10)
        assert result.shape == frame.shape

    def test_input_frame_not_mutated(self) -> None:
        frame = make_frame(fill=128)
        original = frame.copy()
        apply_contrast(frame, "left", alpha=1.5, beta=20)
        np.testing.assert_array_equal(frame, original)

    def test_right_half_unchanged_when_adjusting_left(self) -> None:
        frame = make_frame(fill=100)
        result = apply_contrast(frame, "left", alpha=2.0, beta=0)
        np.testing.assert_array_equal(right_half(result), right_half(frame))


# ─── scheduler (basic smoke tests) ───────────────────────────────────────────

class TestScheduler:
    def test_imports(self) -> None:
        from src.scheduler import therapy_is_on, now_s  # noqa: F401

    def test_continuous_mode_always_on(self) -> None:
        from src.scheduler import therapy_is_on
        for t in [0.0, 5.0, 100.0, 3600.0]:
            assert therapy_is_on(t, cycle_sec=0, on_sec=15.0) is True

    def test_zero_on_sec_always_off(self) -> None:
        from src.scheduler import therapy_is_on
        for t in [0.0, 5.0, 100.0]:
            assert therapy_is_on(t, cycle_sec=30.0, on_sec=0.0) is False

    def test_on_during_first_half_of_cycle(self) -> None:
        from src.scheduler import therapy_is_on
        # cycle=30s, on=15s → on for first 15s of each 30s cycle
        assert therapy_is_on(0.0, 30.0, 15.0) is True
        assert therapy_is_on(14.9, 30.0, 15.0) is True
        assert therapy_is_on(15.0, 30.0, 15.0) is False
        assert therapy_is_on(29.9, 30.0, 15.0) is False
        assert therapy_is_on(30.0, 30.0, 15.0) is True  # next cycle
