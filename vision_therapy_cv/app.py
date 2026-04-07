from __future__ import annotations

import argparse
import logging
import re
import signal
import sys

import cv2

from src.effects import apply_blur, apply_contrast, apply_occlusion
from src.logger import SessionLogger, new_session_csv
from src.scheduler import now_s, therapy_is_on
from src.utils import clip_effects, load_profiles, validate_profile

log = logging.getLogger(__name__)

# Allow only safe alphanumeric profile names to prevent path traversal
_PROFILE_NAME_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")

# Global flag set by SIGINT/SIGTERM for graceful shutdown
_shutdown_requested = False


def _handle_signal(signum: int, _frame: object) -> None:
    global _shutdown_requested  # noqa: PLW0603
    log.warning("Received signal %d — requesting graceful shutdown", signum)
    _shutdown_requested = True


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Vision therapy simulator (CV-based).")
    ap.add_argument("--profile", default="intermittent_occlusion_left", help="Profile name from config/profiles.json")
    ap.add_argument("--config", default="config/profiles.json", help="Path to profiles.json")
    ap.add_argument("--camera", type=int, default=0, help="Webcam index (default: 0)")
    ap.add_argument("--video", default="", help="Optional path to a video file instead of webcam")
    ap.add_argument("--logdir", default="logs", help="Directory for CSV logs")
    ap.add_argument("--show_debug", action="store_true", help="Show debug overlay text")
    ap.add_argument("--verbose", action="store_true", help="Enable DEBUG logging")
    return ap.parse_args()


def open_capture(args: argparse.Namespace) -> cv2.VideoCapture:
    """Open a VideoCapture from webcam index or video file path."""
    source = args.video.strip() if args.video.strip() else args.camera
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera/video source: {source!r}")
    log.info("Opened video source: %s", source)
    return cap


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout,
    )

    args = parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate profile name before using it in a filesystem path
    if not _PROFILE_NAME_RE.match(args.profile):
        log.error("Invalid profile name '%s'. Only alphanumeric, _ and - are allowed.", args.profile)
        sys.exit(1)

    profiles = load_profiles(args.config)
    if args.profile not in profiles:
        available = ", ".join(profiles.keys())
        log.error("Unknown profile '%s'. Available: %s", args.profile, available)
        sys.exit(1)

    profile = validate_profile(args.profile, profiles[args.profile])
    effects = clip_effects(profile.effects, profile.safety)

    cap = open_capture(args)

    csv_path = new_session_csv(args.logdir, profile.name)
    logger = SessionLogger(csv_path=csv_path)
    fields = [
        "ts_wall",
        "t_elapsed",
        "profile",
        "therapy_on",
        "target_eye",
        "occlusion_strength",
        "blur_sigma",
        "contrast_alpha",
        "brightness_beta",
        "frame_w",
        "frame_h",
    ]
    logger.open(fields)

    # Register signal handlers for graceful shutdown (SIGINT = Ctrl-C, SIGTERM = systemd stop)
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    log.info("Running profile: %s — %s", profile.name, profile.description)
    log.info("Logging to: %s", csv_path)
    log.info("Press 'q' to quit.")

    t0 = now_s()

    try:
        while not _shutdown_requested:
            ok, frame = cap.read()
            if not ok:
                log.warning("Frame read failed — end of stream or camera error")
                break

            if frame is None or frame.size == 0:
                log.warning("Received empty frame; skipping")
                continue

            t = now_s()
            t_elapsed = t - t0

            if profile.duration_sec > 0 and t_elapsed > profile.duration_sec:
                log.info("Session duration reached (%.1fs)", profile.duration_sec)
                break

            on = therapy_is_on(t_elapsed, profile.cycle_sec, profile.on_sec)

            out = frame
            if on:
                out = apply_occlusion(out, profile.target_eye, effects["occlusion_strength"])
                out = apply_blur(out, profile.target_eye, effects["blur_sigma"])
                out = apply_contrast(out, profile.target_eye, effects["contrast_alpha"], effects["brightness_beta"])

            if args.show_debug:
                txt = f"{profile.name} | on={on} | eye={profile.target_eye} | t={t_elapsed:.1f}s"
                cv2.putText(out, txt, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("vision_therapy_cv", out)

            logger.log(
                {
                    "ts_wall": t,
                    "t_elapsed": round(t_elapsed, 4),
                    "profile": profile.name,
                    "therapy_on": int(on),
                    "target_eye": profile.target_eye,
                    "occlusion_strength": effects["occlusion_strength"] if on else 0.0,
                    "blur_sigma": effects["blur_sigma"] if on else 0.0,
                    "contrast_alpha": effects["contrast_alpha"] if on else 1.0,
                    "brightness_beta": effects["brightness_beta"] if on else 0,
                    "frame_w": int(out.shape[1]),
                    "frame_h": int(out.shape[0]),
                }
            )

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                log.info("User pressed 'q' — stopping")
                break
    finally:
        logger.close()
        cap.release()
        cv2.destroyAllWindows()
        log.info("Session complete. Resources released.")


if __name__ == "__main__":
    main()