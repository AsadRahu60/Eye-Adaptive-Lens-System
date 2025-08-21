# Roadmap

Short, practical plan for building the **Eye — Adaptive Lens System** from bench demo to wearable prototype.  
We keep stages **S1–S6** simple and add **exit criteria** so “done” is unambiguous.

**Quality gates for every stage**
- CI is green (black, flake8, pytest, markdownlint, arduino-lint)
- Safety defaults on (watchdog + conservative ramps)
- A short note added to `docs/CHANGELOG.md`

---

## Stage S1: Foundations
- Integrate LC shutters with basic on/off control
- Connect ambient + distance sensors
- Enable BLE telemetry from ESP32 → Host

**Exit criteria (done when):**
- LC shutters driven with true AC (no DC), ~200–500 Hz
- Sensors stream stable values ≥10 min
- BLE packets visible on host script (`telemetry_demo.py`)

---

## Stage S2: Single-Eye Control
- Integrate one tunable lens (±6 D range)
- Implement calibration routines
- Host software: basic Python driver with logs

**Exit criteria (done when):**
- `ramp_focus(start,end,duration)` sets a smooth sequence of diopters
- 0→+3 D sweep reproducible ±0.1 D across 10 cycles (bench or simulated)
- `calibration/diopter_map.csv` committed; unit test passes

---

## Stage S3: Dual-Eye System
- Add second tunable lens
- Introduce context-aware policies (near/desk/outdoor)
- Implement detailed session logging

**Exit criteria (done when):**
- Independent L/R control and shutters verified
- Context switching uses hysteresis; misclassification <5% on 30-min run
- Logs saved (CSV/SQLite) with timestamps and setpoints

---

## Stage S4: Therapy & Safety
- Develop graduated occlusion therapy modes
- Add slew-rate limiter, watchdog reset, and safety bounds
- Generate automated therapy reports

**Exit criteria (done when):**
- Intermittent occlusion + contrast-balancing profiles selectable
- Safety tests (TC-Safety-01..03) pass in CI
- Report auto-generated for a session (adherence %, duty curves)

---

## Stage S5: Wearable Prototype
- Assemble lightweight headset/rig
- Optimize comfort and power consumption (8+ hours)
- Conduct usability tests

**Exit criteria (done when):**
- 60-min wear test without discomfort; cables strain-relieved
- Power budget documented; no thermal warnings
- Short usability notes committed (`docs/USABILITY_NOTES.md`)

---

## Stage S6: Advanced Features
- Integrate eye-tracking for closed-loop control
- Implement analytics dashboards
- Explore ML-based therapy optimization

**Exit criteria (done when):**
- Eye-tracking signal (or simulated input) influences policy
- Basic analytics dashboard plots adherence/diopter history
- One small ML experiment (baseline) documented

---

## Engineering metrics to track (lightweight)
- Reliability: no unexpected resets in a 30-min run
- Latency: sensor→actuation < 200 ms (bench)
- Optical repeatability: ±0.1 D across cycles
- Adherence proxy: session completion %, occlusion duty applied
- Comfort: symptom checklist (0–10), target ≤ 2 median

### (Last updated: YYYY-MM-DD)
