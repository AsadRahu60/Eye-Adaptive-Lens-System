# Test Cases

This file enumerates key tests linked to requirements. See `docs/RTM.md` for mapping.

## Legend
- **Auto?** yes/no
- **Tool** pytest / arduino / manual
- **Ref** SRS/URS IDs if applicable

---

## A) Functional – Optics & Control

| ID           | Title                                 | Precondition                      | Steps                                                                 | Expected Result                                           | Auto? | Tool   |
|--------------|----------------------------------------|-----------------------------------|-----------------------------------------------------------------------|-----------------------------------------------------------|-------|--------|
| TC-FOC-001   | Ramp focus 0→+3 D                      | Host connected (mock ok)          | Call `ramp_focus(0, 3, 2s, steps=10)`                                | List of 11 setpoints, last ≈ 3.0 D                       | yes   | pytest |
| TC-FOC-002   | Rate limit applied                     | Host connected                    | Call `ramp` with delta beyond `max_rate * dt`                         | Output step ≤ `max_rate * dt`                             | yes   | pytest |
| TC-OCC-001   | LC shutter toggles (bench)             | ESP32 + H-bridge wired            | Command 5 s occlusion; observe                                             | Visible occlusion; no DC bias across shutter              | no    | manual |
| TC-CTX-001   | Context change near→desk               | Telemetry mock or sensors         | Increase distance + lux as thresholds                                  | Mode switches with hysteresis; no oscillation             | yes   | pytest |
| TC-CAL-001   | Calibration map loaded                 | `calibration/*.csv` present       | Load map; query setpoint for 40 cm                                     | Returns expected dpt ± tolerance                          | yes   | pytest |

---

## B) Safety

| ID           | Title                                 | Precondition                 | Steps                                      | Expected Result                                      | Auto? | Tool   |
|--------------|----------------------------------------|------------------------------|--------------------------------------------|------------------------------------------------------|-------|--------|
| TC-SAF-001   | Slew-rate limiter                      | Host running                 | Request large diopter jump                  | Limited per configured max rate                       | yes   | pytest |
| TC-SAF-002   | Watchdog to safe state                 | Running session              | Kill host/comms or inject fault             | Lenses → neutral; shutters → transparent              | no    | manual |
| TC-SAF-003   | Duty cap enforced                      | Therapy mode active          | Set high occlusion duty                     | Duty limited; warning logged                          | yes   | pytest |
| TC-SAF-004   | No DC across LC shutters               | Scope on LC terminals        | Run for 2 min                               | Pure AC waveform; average ≈ 0 V                       | no    | manual |

---

## C) Integration – Telemetry & Logs

| ID           | Title                                 | Precondition                 | Steps                                                | Expected Result                               | Auto? | Tool   |
|--------------|----------------------------------------|------------------------------|------------------------------------------------------|-----------------------------------------------|-------|--------|
| TC-TEL-001   | Mock telemetry stream                  | Python env                   | `telemetry_demo.py --mock --duration 5 --out demo.csv` | Console JSON; CSV created with 4 columns      | yes   | pytest |
| TC-LOG-001   | Session log schema                     | Storage module               | Start/stop session; write 10 samples                 | CSV/SQLite row count and columns validated    | yes   | pytest |
| TC-REP-001   | Report generation                      | Sample logs available        | Run report script                                   | Markdown/HTML report written to `reports/`    | yes   | pytest |

---

## D) UI / Operator (lightweight)

| ID           | Title                                 | Precondition                 | Steps                                  | Expected Result                         | Auto? | Tool   |
|--------------|----------------------------------------|------------------------------|----------------------------------------|-----------------------------------------|-------|--------|
| TC-UI-001    | Manual override controls               | Host + UI running            | Adjust sliders for L/R focus & opacity | Values applied; safety constraints hold | no    | manual |
| TC-OPS-001   | Operator checklist                     | Doc in repo                  | Follow `USABILITY_NOTES.md` before run | All checks ticked                       | no    | manual |

---

## Notes
- Link these IDs in code comments (e.g., test names or docstrings).
- Keep tests CI-friendly; hardware tests are **manual** with screenshots uploaded to `docs/tests/`.
- See `docs/TEST_STRATEGY.md` for levels, tools, and coverage philosophy.

_Last updated: YYYY-MM-DD_
