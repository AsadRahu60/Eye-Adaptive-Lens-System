Vision Therapy Simulator (Computer Vision)

Overview

This module is part of the Eye Adaptive Lens System project. It implements a computer-vision-based simulation of vision therapy concepts such as occlusion, blur, and contrast modulation using a live camera or video input.

The purpose of this module is to enable rapid experimentation, validation, and testing when physical tunable lens hardware is unavailable. It follows the same system-level principles as the hardware path: safety bounds, staged control, telemetry, and reproducible logging.

Disclaimer: This is a research and educational prototype. It is not a medical device and must not be used for diagnosis or treatment.

⸻

Motivation

This work is a personal research-driven exploration inspired by real-world vision challenges. Traditional amblyopia therapy often relies on static occlusion (patching), which can be uncomfortable and difficult to personalize, especially for children.

The goal of this module is to explore adaptive, gradual, and data-driven visual strategies that can:
	•	Reduce discomfort
	•	Improve therapy adherence
	•	Enable objective measurement and validation

This module allows those ideas to be tested safely in software before any hardware integration.

⸻

What This Module Does
	•	Captures live frames from a webcam or video file
	•	Applies simulated therapy effects:
	•	Occlusion (left / right / both)
	•	Gaussian blur
	•	Contrast & brightness adjustment
	•	Uses JSON-based therapy profiles to define behavior
	•	Enforces conservative safety limits on all effects
	•	Logs all session data to CSV for later analysis

⸻

System Design (Software)

Input
	•	Webcam or prerecorded video

Control
	•	Time-based therapy scheduler (on/off cycles)
	•	Profile-driven configuration (profiles.json)

Processing
	•	Computer vision effects applied per frame
	•	Optional debug overlays

Output
	•	Live visualization window
	•	CSV session logs (timestamps, parameters, states)

⸻

Project Structure

vision_therapy_cv/
├── app.py                  # Main runnable application
├── config/
│   └── profiles.json       # Therapy profiles (JSON)
├── src/
│   ├── effects.py          # CV effects (occlusion, blur, contrast)
│   ├── scheduler.py        # Therapy timing logic
│   ├── logger.py           # CSV session logging
│   └── utils.py            # Config loading & validation
├── tests/                  # Unit tests (expanded in later stages)
├── logs/                   # Runtime logs (gitignored)
├── reports/                # Generated reports (gitignored)
└── README.md


⸻

Installation

Create a virtual environment (recommended) and install dependencies:

pip install -r requirements.txt


⸻

How to Run

Webcam (default)

python app.py --profile intermittent_occlusion_left --show_debug

Use a video file

python app.py --video sample.mp4 --profile blur_right_soft --show_debug

Press q to exit.

⸻

Configuration: Therapy Profiles

Therapy behavior is defined in:

config/profiles.json

Each profile specifies:
	•	Duration and cycle timing
	•	Target eye (left / right / both)
	•	Effect strengths (occlusion, blur, contrast)
	•	Safety limits (hard bounds)

Profiles can be changed without modifying code.

⸻

Logging & Validation
	•	Each run creates a CSV file in logs/
	•	Logged data includes:
	•	Timestamps
	•	Active profile
	•	Therapy on/off state
	•	Effect parameters
	•	Frame metadata

These logs support:
	•	Offline analysis
	•	Report generation (next stage)
	•	ML experimentation (later stages)

⸻

Safety Principles
	•	Conservative defaults on startup
	•	Hard limits on blur, contrast, and occlusion strength
	•	Deterministic, testable effect functions
	•	Clear separation of concerns (effects, scheduling, logging)

Safety constraints always override adaptive logic.

⸻

Roadmap (This Module)
	•	Week 1: Therapy simulator MVP (current)
	•	Week 2: Automated reports, plots, CI, expanded tests
	•	Week 3: Software-based autofocus / sharpness metrics
	•	Week 4: Eye-region detection and context-aware policies

⸻

Relationship to the Main Project

This module does not replace the optical hardware path. It serves as:
	•	A rapid prototyping tool
	•	A validation and testing environment
	•	A data-generation pipeline

It complements the ESP32-based embedded system described in the root project README.

⸻

Author

Asadullah Rahoo
Eye Adaptive Lens System — Personal Research Project