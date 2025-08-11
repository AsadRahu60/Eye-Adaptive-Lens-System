# Eye — Adaptive Lens System for Amblyopia (R&D Prototype)

> **Disclaimer:** Research/education prototype. **Not a medical device.** Do not use for self-treatment.

[![License: MIT](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/AsadRahu60/eye-adaptive-lens/ci.yml?label=CI)](https://github.com/AsadRahu60/eye-adaptive-lens/actions)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Made with: ESP32 + Python](https://img.shields.io/badge/made%20with-ESP32%20%2B%20Python-blue)](https://www.espressif.com/en/products/socs/esp32-s3)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-success.svg)](CONTRIBUTING.md)

Electronically tunable **per-eye focus** + **LC shutter occlusion** for supervised amblyopia research tasks. Sensor-aware modes (near/desk/outdoor), **manual + automated therapy profiles**, and **QA-first** documentation (URS → SRS → RTM → Tests).

---

## Table of Contents
- [Why](#why)
- [Architecture](#architecture)
- [Quality & Testing](#quality--testing)
- [Quick Start](#quick-start)
- [Project Layout](#project-layout)
- [Roadmap](#roadmap)
- [Hiring Manager Highlights](#hiring-manager-highlights)
- [Contributing](#contributing)
- [License](#license)

---

## Why
Traditional patching is static and hard to personalize. **Eye** explores dynamic, clinician-configurable training: subtle per-eye focus changes + intermittent occlusion, driven by context and fully logged.

### MVP Goals
- Per-eye focus control (Optotune/Varioptic) with smooth ramps
- Per-eye LC occlusion (AC drive, no DC bias)
- Sensors (ToF, ALS, IMU) → context (near/desk/outdoor)
- BLE UI (manual sliders + profiles) and data logging

---

## Architecture
```mermaid
flowchart LR
  subgraph Optics
    LTL[Tunable Lens L]:::opt
    RTL[Tunable Lens R]:::opt
    LCSL[LC Shutter L]:::opt
    LCSR[LC Shutter R]:::opt
  end

  subgraph Control
    ESP[ESP32-S3\nSensors + BLE + LC drive]:::ctrl
    PI[Raspberry Pi 5\nPolicy + Logs + UI]:::ctrl
  end

  LTL <-. USB/UART .-> PI
  RTL <-. USB/UART .-> PI
  LCSL <-- PWM AC --> ESP
  LCSR <-- PWM AC --> ESP
  ESP <-- I2C --> SENSORS[VL53L1X + TSL2591 + BNO055]:::sens
  PI <-- BLE / Wi-Fi --> APP[Mobile / Web UI]:::ui

  classDef opt fill:#f6ffed,stroke:#47c73b;
  classDef ctrl fill:#eef7ff,stroke:#2f6feb;
  classDef sens fill:#fff6e6,stroke:#e59f00;
  classDef ui fill:#f3e8ff,stroke:#7c3aed;

```

**Stack:** ESP32‑S3 (Arduino), Python 3 host, BLE GATT, I²C sensors, H‑bridge for LC shutters, Optotune/Varioptic lens drivers, optional Flutter app.

---

## Quality & Testing
Standards‑inspired (ISO 14971 risk thinking, IEC 62304/62366 mindset) — **not certified**.
- **Levels:** unit (Python), integration (sensors/driver links), system (bench), usability (operator workflows)
- **Types:** functional, performance (latency/accuracy), reliability (repeatability), safety (slew limits, watchdog), data integrity
- **Gates:** entry/exit criteria per sprint; mandatory logs attached to PRs
- **CI:** lint (black, flake8), markdown lint, Arduino lint — see `.github/workflows/ci.yml`

Docs: [`docs/URS.md`](docs/URS.md) · [`docs/SRS.md`](docs/SRS.md) · [`docs/RTM.md`](docs/RTM.md) · [`docs/TEST_STRATEGY.md`](docs/TEST_STRATEGY.md) · [`docs/TEST_CASES.md`](docs/TEST_CASES.md) · [`docs/SAFETY_PROTOCOLS.md`](docs/SAFETY_PROTOCOLS.md)

---

## Quick Start
### Firmware (ESP32‑S3)
1. Install Arduino IDE + ESP32 core.
2. Wire LC shutter via DRV8833; sensors to I²C.
3. Flash `firmware/esp32/main.cpp`; check serial output.

### Host (Pi/PC)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
python host/pi/lens_controller.py   # update serial ports and driver commands

---

## Project Layout
```markdown
.
├─ firmware/esp32/               # BLE + sensors + LC shutters
├─ host/pi/                      # Lens driver control + policy + logs
├─ apps/flutter_mobile/          # future BLE app
├─ calibration/
├─ tests/automation/
├─ docs/                         # URS, SRS, RTM, Test Strategy, etc.
├─ .github/workflows/ci.yml
├─ README.md  CONTRIBUTING.md  CODE_OF_CONDUCT.md
└─ LICENSE  CHANGELOG.md  .gitignore
```

---

## Roadmap
- **S1:** LC shutters + sensors + BLE telemetry (bench)
- **S2:** One tunable lens + calibration; Python control
- **S3:** Dual‑eye integration; context policy; logging
- **S4:** Therapy modes; safety guards; reports
- **S5:** Wearable rig; comfort tuning; power mgmt
- **S6:** Optional eye tracking; analytics

Full details: [`docs/ROADMAP.md`](docs/ROADMAP.md)

---

## Hiring Manager Highlights
- **Traceability:** URS → SRS → RTM → Test cases (audit‑ready thinking)
- **Safety mindset:** slew‑rate limiter, bounds, watchdog, session caps
- **Process:** CI with lint/tests; issue/PR templates; Conventional Commits
- **Systems thinking:** optics + embedded + host + data pipeline

---

## Contributing
See [`CONTRIBUTING.md`](CONTRIBUTING.md). Use **Conventional Commits** and PR template. Attach test logs (scope screenshots for LC drive, diopter ramps) when relevant.

---

## License
MIT — see [`LICENSE`](LICENSE).

---

### GitHub Polish Checklist
- Repo topics: `amblyopia`, `tunable-lens`, `embedded`, `esp32`, `python`, `vision-science`, `qa-testing`
- Social preview: upload `assets/social-preview.png` (1200×630)
- Pin this repo; add it to CV/LinkedIn
- CI badge already points to `https://github.com/AsadRahu60/eye-adaptive-lens/actions`
