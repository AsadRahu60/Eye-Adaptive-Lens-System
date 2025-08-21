# Project Management Plan (PM Plan)

## 1) Scope & Objectives
Build a research-ready prototype of the **Eye — Adaptive Lens System** with
per-eye tunable focus, LC occlusion, context-aware control, data logging, and
safety guardrails. Deliverables align to S1–S6 in `docs/ROADMAP.md`.

**Outcome targets (Year 1):**
- Bench-validated dual-eye control with conservative safety
- Calibration + telemetry + basic therapy profiles
- Reproducible repo (CI, tests, docs) + pilot protocol draft

---

## 2) Work Breakdown (linked to Roadmap)
- **S1 Foundations:** shutters, sensors, BLE telemetry
- **S2 Single-Eye:** one tunable lens + calibration
- **S3 Dual-Eye:** L/R independence, context engine, logging
- **S4 Therapy & Safety:** IO/contrast profiles, guardrails, reports
- **S5 Wearable:** rig, comfort, power, usability notes
- **S6 Advanced:** eye tracking, analytics (stretch)

Each stage has **exit criteria** in `docs/ROADMAP.md`.

---

## 3) Roles & Responsibilities
- **Asadullah (Owner):** firmware, host control, tests, docs, CI
- **Supervisor (TBD):** research direction, ethics, evaluation design
- **Collaborators (TBD):** optics advice, clinical input, UI support

---

## 4) Process & Cadence
- **Sprints:** 2–3 weeks
- **Tracking:** GitHub Issues + Projects (Kanban: Backlog → Doing → Review → Done)
- **Branching:** `feature/<topic>`, `fix/<topic>`, PRs to `main`
- **Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`)
- **Definition of Done (DoD):**
  - CI green (black, flake8, pytest, markdownlint, arduino-lint)
  - Docs updated (README or relevant `docs/*`)
  - Exit criteria met & short entry in `docs/CHANGELOG.md`

---

## 5) Quality & Safety Gates
- **Safety defaults:** slew-rate limits, watchdog, occlusion duty caps
- **Bench checks:** shutter AC (no DC), repeatability (±0.1 D)
- **Artifacts:** scope screenshots, calibration CSV, session logs
- **Peer review:** self or supervisor review on PR before merge

---

## 6) Risk Management
- Register in `docs/RISK_REGISTER.md` (likelihood, impact, mitigation, owner)
- Reassess at each stage transition
- Add mitigations as tasks/issues

---

## 7) Configuration & Environments
- **Firmware:** Arduino/ESP32 core (document board + libs in `firmware/README.md`)
- **Host:** Python 3.11 (pin in `requirements.txt`)
- **Optional BLE:** `bleak` in `requirements-dev.txt`
- **Data:** CSV/SQLite under `data/` (no personal data)

---

## 8) Change Management
- Propose changes via GitHub Issue → PR
- Update URS/SRS/RTM if requirements change
- Note in `docs/CHANGELOG.md`

---

## 9) Deliverables (living list)
- **Code:** `firmware/esp32/*`, `host/pi/*`
- **Calibration:** `calibration/diopter_map.csv`
- **Reports:** `reports/*`
- **Docs:** URS, SRS, RTM, TEST_STRATEGY, TEST_CASES, ARCHITECTURE, ROADMAP,
  ETHICS_AND_SAFETY, PM_PLAN, RISK_REGISTER, NAMING_CONVENTIONS
- **Proposal PDFs:** `docs/PROPOSAL.pdf` (detailed), `docs/PROPOSAL_SHORT.pdf` (2–3 pages)

### Last updated: 2025-08-20
