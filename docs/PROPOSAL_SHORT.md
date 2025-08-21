AI-Assisted Adaptive Optics for Personalized Amblyopia Therapy (R&D Prototype)
Candidate: Asadullah Rahoo
[asadullahrahoo98@gmail.com](mailto:asadullahrahoo98@gmail.com)
[GitHub Repository](https://github.com/AsadRahu60/eye-adaptive-lens)· Phone: +49 176 47604330

Current status: M.Sc. Computer Science (University of Passau); B.Eng. Electronics
Keywords: tunable lenses, LC occlusion, embedded systems, safety-critical control, vision therapy, ML assist
R&D prototype — not a medical device. All experimental work will follow conservative safety limits and proceed only under appropriate supervision and ethics approval.
Executive Summary (≈120 words)
Amblyopia therapies like patching are static, poorly personalized, and often face compliance challenges. I propose a supervised research platform that delivers per-eye optical modulation using electronically tunable lenses and liquid-crystal (LC) occlusion to enable graded, clinician-configured stimulation during near and everyday tasks. The system integrates sensors (distance, ambient light, IMU), a safety-first control stack (slew-rate limits, occlusion duty caps, watchdog fail-safe), complete telemetry, and an optional ML assist that only suggests mild changes under hard guardrails and falls back to rule-based logic. Phase 1 focuses on bench validation; later stages prepare a pilot protocol with a clinical partner. The aim is a reproducible, instrumented platform for testing hypotheses about adaptive amblyopia therapy—not a medical product.
Background & Gap
Clinical gap: Traditional patching is binary and difficult to tailor; older children and adults often see limited benefit.
Scientific opportunity: Small, per-eye graded changes to focus/contrast/occlusion may better promote binocular balance while maintaining comfort and adherence.
Technical enablers: Compact tunable lenses, LC shutters, low-power embedded controllers, BLE connectivity, and robust logging allow safe, configurable in-situ optical manipulation suitable for controlled research.
Research Aims
Build a safety-first adaptive optics platform with per-eye tunable focus and LC occlusion; provide complete telemetry and strong guardrails.
Develop therapy policies: start with conservative rule-based modes, then add a guardrailed ML assist that suggests small adjustments; always enforce hard limits.
Quantify feasibility: response latency, repeatability (target ±0.1 D), user comfort envelopes, operator usability.
Prepare for clinical studies with a partner: ethics-ready documentation, safety testing, and a pilot protocol outline (inclusion/exclusion, endpoints, data plan).
Approach & Work Packages (24 months)
WP1 — System Engineering (Months 0–6)
Hardware: Per-eye tunable lens drivers; LC shutter AC drive with true AC (no DC bias); sensors (ToF distance, ambient light, IMU).
Firmware: ESP32 BLE + sensor fusion; watchdog; soft limits and safe defaults.
Host software: Python control for lens drivers; context engine; logs; report tooling.
Exit criteria: Dual-eye bench control; safety clamps verified; deterministic logs captured; CI green on hardware-independent tests.
WP2 — Calibration & Safety Validation (Months 4–10)
Calibration: Per-eye diopter mapping; slew-rate comfort curves; LC opacity mapping vs. drive.
Safety: Verify AC drive on scope; thermal/current limits; watchdog behavior; fault-injection tests.
Data integrity: Session schema; reproducibility tests (e.g., 10 cycles within ±0.1 D).
Exit criteria: Calibration assets; safety protocol report; repeatability and latency metrics; automated test suite expanded.
WP3 — Therapy Policies & ML Assist (Months 8–16)
Rule-based policies: Intermittent occlusion (duty scheduling) and contrast-balancing for the fellow eye; conservative ramps and hysteresis.
ML assist: Train a small, interpretable model (e.g., logistic baseline) on session telemetry to suggest mild duty adjustments; enforce hard clamps and fallback to rules on uncertainty.
Evaluation: Compare adherence proxies (comfort rating windows, tolerated duty) and stability vs. rule-only baseline on bench tasks.
Exit criteria: ML assist improves predefined proxies without violating safety envelopes; complete audit trail of inputs/outputs and model versioning.
WP4 — Usability & Pilot Readiness (Months 14–24)
Wearable rig: Lightweight frame, cable management, and operator checklist; comfort prompts.
Pilot prep: Draft ethics package (risk analysis, consent model, data plan) with a clinic partner; define endpoints (adherence, comfort, binocular function tests decided with clinicians).
Exit criteria: Pilot protocol outline; operator usability report; documentation bundle for ethics submission.
Safety, Ethics, and Data
Non-clinical R&D by default; any human testing only under formal ethics approval and clinician supervision.
Guardrails: Per-eye slew-rate limits; duty caps; watchdog to neutral focus + transparent shutters on fault; conservative defaults.
Optical safety: True AC for LC shutters (no DC bias), current/thermal limits per vendor specs, emergency stop behavior.
Data & privacy: No personal identifiers; telemetry only; model versions logged; export under consent; storage with access control.
Expected Outcomes
A reproducible research platform for adaptive, per-eye optical stimulation with full telemetry and safety guards.
Benchmark results: response latency, repeatability, comfort envelopes, policy comparisons; reports and scripts for replication.
Open documentation: architecture, roadmap with exit criteria, risk register, safety protocols, tests, calibration procedures.
Pilot-ready materials to support a clinician-led feasibility study within the PhD timeframe (subject to partner and approvals).
Scholarly outputs: 2–3 papers across biomedical optics/vision science/embedded systems venues; open datasets and code where appropriate.
Candidate Fit & Supervision Request
I bring embedded systems + host software skills, safety-critical thinking (QA/test discipline), and personal motivation (amblyopia). I seek supervision within ophthalmology / biomedical optics / vision science with co-supervision from instrumentation/engineering. I can align scope to active grants (e.g., instrument development, clinical translation, analytics).
Lab alignment paragraph (edit per email):
Your lab’s work on <adaptive optics / ophthalmic imaging / binocular vision / biomedical instrumentation> is a natural fit. I can contribute a ready, instrumented platform and push toward pilot-readiness, while aligning experiments with your ongoing projects and clinical collaborations.
Minimal Technical Appendix (from repo)
Stack: ESP32 firmware (BLE + sensors + LC drive), Python host (lens control, context engine, logs), optional Flutter UI.
ML assist: Guardrailed logistic model suggests small duty changes; hard clamps always enforce safe ranges; full fallback to rules.
Reproducibility: CI green (format/lint/tests/markdown/arduino-lint), one-click synthetic demo (train + tests) runs without hardware.
Repository: AsadRahu60/eye-adaptive-lens → README points to architecture, roadmap, safety, tests, ML overview, and demo commands.
Last updated: 21.08.2025 (Europe/Berlin)