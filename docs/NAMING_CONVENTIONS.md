# Naming & Contribution Conventions

Consistent naming improves readability, traceability, and CI/lint compliance.  
This document defines repository structure, coding style, test practices, and PR/reporting guidelines.

---

## 1) Repository Structure (top level)

- `/firmware/esp32/` — ESP32 Arduino/C++  
- `/host/pi/` — Python host tools & policies  
- `/tests/` — Automated tests (pytest)  
- `/docs/` — Documentation (Markdown + PDFs)  
- `/calibration/` — Calibration data (CSV)  
- `/data/sessions/` — Example logs (CSV/SQLite)  
- `/reports/` — Generated reports  
- `/assets/` — Images (social preview, diagrams)  

---

## 2) Files & Folders

- **Python files:** `snake_case.py` (e.g., `lens_controller.py`)  
- **C++/Arduino:** `CamelCase.cpp/.h` or `snake_case.ino`  
- **Markdown docs:** `TITLE_CASE.md` (e.g., `TEST_CASES.md`, `PM_PLAN.md`)  
- **Calibration:** `lowercase_with_underscores.csv` (e.g., `diopter_map.csv`)  
- **Images/Assets:** `kebab-case.png` (e.g., `social-preview.png`)  

---

## 3) Python Style (`host/`)

- **Modules/funcs/vars:** `snake_case` (e.g., `ramp_focus`, `context_state`)  
- **Classes:** `PascalCase` (e.g., `OptoLens`)  
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_SLEW_DPT_S = 0.25`)  
- **Type hints:** Required for public functions  
- **Line length:** **88** (Black default; Flake8 set to 88)  
- **Imports:** stdlib → third-party → local; no wildcard imports  
- **Docstrings:** One-line summary + brief params/return  

**Example:**
```python
def ramp_focus(start_dpt: float, end_dpt: float, duration_s: float, steps: int = 20) -> list[float]:
    """Generate a linear ramp from start to end diopters over duration."""
```

---

## 4) C++/Arduino Style (`firmware/esp32/`)

- **Classes:** `PascalCase` (e.g., `ShutterDriver`)  
- **Methods/vars:** `camelCase` (e.g., `setOpacity`, `targetDiopter`)  
- **Constants/macros:** `UPPER_SNAKE_CASE` (e.g., `PWM_HZ`)  
- **Pins:** `PIN_<NAME>` (e.g., `PIN_SHUTTER_L_A`)  
- **Comments:** Doxygen-style for public interfaces  

**Example:**
```cpp
/// Drive the left shutter to a given opacity (0.0–1.0).
/// @param opacity Target opacity in [0,1].
void setOpacity(float opacity);
```

---

## 5) Tests

- **Pytest files:** `test_<module>.py` (e.g., `test_lens.py`)  
- **Test names:** `test_<behavior>_<expected>()`  
- **IDs:** Reference matching cases in `docs/TEST_CASES.md`  
- **Data fixtures:** Place small CSVs under `tests/data/` (kebab-case names)  

---

## 6) Branches, Commits, PRs

- **Branches:** `feature/<short-topic>`, `fix/<short-topic>`, `docs/<topic>`  
- **Commits:** Conventional Commits  
```text
feat: add ramp_focus API
fix: clamp slew rate
docs: add safety protocols
test: cover context hysteresis
chore: bump flake8 to 7.x
```

- **PR titles:** Sentence case; reference Issue ID or Test Case IDs if relevant  
- **PR body:** What/why, safety impact (if any), and how verified (tests/logs)  

---

## 7) Data, Logs, Reports

- **CSV headers:** Include units in name or docstring  
  Example: `ts,dist_cm,lux,yaw_deg,L_dpt,R_dpt`  
- **Session logs:** `data/sessions/<name>.csv`  
- **Reports:** `reports/<name>.md`  
- **Calibration:** `calibration/diopter_map.csv` (document columns in `docs/calibration.md`)  

---

## 8) Markdown Hygiene

- End every `.md` with a **single trailing newline** (markdownlint MD047)  
- Use fenced code blocks with language tags (`python`, `bash`, `cpp`, `json`)  
- Prefer headings ≤ H3; keep lines ≤ 120 chars  
- Link related docs with relative paths (e.g., see `TEST_CASES`)  

---

## 9) Linters Configured

- **Black** (88)  
- **Flake8** (88)  
- **Markdownlint** (GitHub Actions)  

---

_Last updated: 2025-08-20_
