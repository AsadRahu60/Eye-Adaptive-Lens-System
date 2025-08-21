# Risk Register

This register is reviewed at each stage boundary (S1–S6). Severity is a simple
product: **Severity = Likelihood × Impact** on a 1–5 scale. Items with
Severity ≥ 12 require an owner and dated mitigation task.

## Scale
- **Likelihood (L):** 1 rare · 3 possible · 5 likely  
- **Impact (I):** 1 low discomfort · 3 session disruption · 5 safety critical

---

| ID  | Risk                                           | Area          | L | I | Sev | Triggers / Early Signals                              | Mitigation / Controls                                                                 | Owner | Status |
|-----|------------------------------------------------|---------------|---|---|-----|--------------------------------------------------------|---------------------------------------------------------------------------------------|-------|--------|
| R1  | Lens driver overheating                        | Optics/Power  | 3 | 5 | 15  | Driver temp rising, thermal throttle                   | Heatsinking, temp monitor, auto-shutdown, longer ramps                                | AR    | Open   |
| R2  | LC shutter DC bias damages panel               | Optics        | 2 | 5 | 10  | Asymmetric waveform on scope                           | True AC via H-bridge (200–500 Hz), verify with scope, code review                     | AR    | Open   |
| R3  | BLE disconnect during session                  | Comms         | 4 | 3 | 12  | Packet loss, timeouts                                  | Retry policy, watchdog to **neutral focus + transparent shutters**                    | AR    | Open   |
| R4  | Context misclassification → discomfort         | Policy        | 3 | 3 | 9   | Rapid mode flips, nausea reports                       | Hysteresis + dead-bands, lower update rate, operator abort                            | AR    | Open   |
| R5  | Excessive slew/occlusion duty → eye strain     | Safety        | 2 | 5 | 10  | Headache, dizziness                                    | Hard limits: slew-rate cap, duty caps, session timers                                 | AR    | Open   |
| R6  | Data loss / corruption in logs                 | Data          | 2 | 3 | 6   | Missing rows, parse errors                             | Atomic writes, CSV schema test, periodic flush, checksums                             | AR    | Open   |
| R7  | Power brownout / unexpected reboot             | Power         | 3 | 3 | 9   | Voltage dip under load                                 | Power budget, brownout detect, graceful resume, battery margin                        | AR    | Open   |
| R8  | Cable strain / mechanical failure              | Mech          | 3 | 3 | 9   | Intermittent connections                               | Strain relief, harness routing, connector latch, bench tug test                       | AR    | Open   |
| R9  | Lens thermal drift → focus error               | Optics        | 3 | 3 | 9   | Diopter offset grows with time                         | Temperature compensation if available, periodic re-zero, longer ramps                 | AR    | Open   |
| R10 | Vendor SDK/protocol change                     | Software      | 2 | 2 | 4   | Driver update breaks commands                          | Adapter layer, pin versions in `requirements.txt`, mock for CI                         | AR    | Open   |
| R11 | Privacy/ethics concerns with session data      | Governance    | 2 | 4 | 8   | Identifiable data stored                               | No personal data in device logs, anonymize IDs, consent notes in `ETHICS_AND_SAFETY`  | AR    | Open   |

### Notes
- Owners use GitHub Issues to track mitigation tasks and link commits/PRs.
- Upload scope screenshots for R2 to `docs/tests/` and reference them in PRs.
- If any risk escalates to **Sev ≥ 15**, pause new features until mitigated.

### Last reviewed: YYYY-MM-DD
