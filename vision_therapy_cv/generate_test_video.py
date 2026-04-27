#!/usr/bin/env python3
"""
Generate a synthetic test video for the Vision Therapy CV Simulator.

Usage:
    python3 generate_test_video.py              # creates test_video.mp4 (30s)
    python3 generate_test_video.py --duration 60 --output myvideo.mp4
"""

import argparse
import math
import cv2
import numpy as np


def generate(output: str, duration_s: int, fps: int = 30) -> None:
    width, height = 640, 480
    total_frames = duration_s * fps

    writer = cv2.VideoWriter(
        output,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    print(f"Generating {duration_s}s test video → {output} ...")

    for i in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Colour gradient background (changes over time so blur is visible)
        for x in range(width):
            r = int(x * 0.4)
            g = int((i * 0.3 + x * 0.2) % 255)
            b = int((width - x) * 0.3)
            frame[:, x] = [b, g, r]

        # Moving white circle
        cx = int(width / 2 + 200 * math.sin(i * 0.05))
        cy = int(height / 2 + 150 * math.cos(i * 0.04))
        cv2.circle(frame, (cx, cy), 50, (255, 255, 255), cv2.FILLED)

        # Grid lines — make blur effect very obvious
        for gx in range(0, width, 60):
            cv2.line(frame, (gx, 0), (gx, height), (60, 60, 60), 1)
        for gy in range(0, height, 50):
            cv2.line(frame, (0, gy), (width, gy), (60, 60, 60), 1)

        # Centre split line (shows left/right eye boundary)
        cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 255, 255), 2)

        # Timestamp
        t = i / fps
        cv2.putText(frame, f"t = {t:.1f}s", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

        # Therapy cycle indicator (15s ON / 15s OFF)
        cycle_pos = t % 30
        therapy_on = cycle_pos < 15
        status = "THERAPY ON  (left eye occluded)" if therapy_on else "THERAPY OFF (both eyes open)"
        colour = (0, 80, 255) if therapy_on else (0, 200, 0)
        cv2.putText(frame, status, (10, height - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, colour, 2)

        # Eye labels
        cv2.putText(frame, "LEFT EYE",  (80,  460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, "RIGHT EYE", (380, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        writer.write(frame)

        # Progress indicator
        if i % (fps * 5) == 0:
            print(f"  {t:.0f}s / {duration_s}s ...")

    writer.release()
    print(f"Done! Saved to: {output}")


def main() -> None:
    p = argparse.ArgumentParser(description="Generate a synthetic test video.")
    p.add_argument("--output",   default="test_video.mp4", help="Output file path")
    p.add_argument("--duration", type=int, default=30,     help="Duration in seconds")
    p.add_argument("--fps",      type=int, default=30,     help="Frames per second")
    args = p.parse_args()
    generate(args.output, args.duration, args.fps)


if __name__ == "__main__":
    main()
