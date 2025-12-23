from __future__ import annotations

import cv2
import numpy as np


def _split_roi(frame: np.ndarray, side: str) -> tuple[slice, slice]:
    h, w = frame.shape[:2]
    if side == "left":
        return slice(0, h), slice(0, w // 2)
    if side == "right":
        return slice(0, h), slice(w // 2, w)
    # "both" -> whole frame
    return slice(0, h), slice(0, w)


def apply_occlusion(frame: np.ndarray, side: str, strength: float) -> np.ndarray:
    """Overlay a dark mask on the selected half of the frame."""
    strength = float(np.clip(strength, 0.0, 1.0))
    if strength <= 0:
        return frame

    out = frame.copy()
    ys, xs = _split_roi(out, side)
    roi = out[ys, xs]

    mask = np.zeros_like(roi, dtype=np.uint8)  # black
    out[ys, xs] = cv2.addWeighted(roi, 1.0 - strength, mask, strength, 0)
    return out


def apply_blur(frame: np.ndarray, side: str, sigma: float) -> np.ndarray:
    """Gaussian blur on selected half of the frame."""
    sigma = float(max(0.0, sigma))
    if sigma <= 0:
        return frame

    out = frame.copy()
    ys, xs = _split_roi(out, side)
    roi = out[ys, xs]

    blurred = cv2.GaussianBlur(roi, ksize=(0, 0), sigmaX=sigma, sigmaY=sigma)
    out[ys, xs] = blurred
    return out


def apply_contrast(frame: np.ndarray, side: str, alpha: float, beta: int) -> np.ndarray:
    """
    Adjust contrast/brightness on selected half:
      new = alpha * pixel + beta
    """
    alpha = float(alpha)
    beta = int(beta)

    out = frame.copy()
    ys, xs = _split_roi(out, side)
    roi = out[ys, xs]

    # convertScaleAbs does: saturate(|alpha*src + beta|)
    # We'll do it in float and clip for predictable behavior
    roi_f = roi.astype(np.float32) * alpha + beta
    roi_f = np.clip(roi_f, 0, 255).astype(np.uint8)
    out[ys, xs] = roi_f
    return out