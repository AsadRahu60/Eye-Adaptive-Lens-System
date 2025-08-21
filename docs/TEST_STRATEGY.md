# Test Strategy

## Levels of Testing
1. **Unit Tests** (Python functions, C++ classes).
2. **Integration Tests** (sensor-driver + actuator link).
3. **System Tests** (end-to-end therapy workflows).
4. **Usability Tests** (clinician/researcher workflows).

## Types of Testing
- Functional
- Performance (latency, accuracy)
- Safety (lens bounds, occlusion timing)
- Reliability (repeatability)
- Compliance (logs, traceability)

## Tools
- Python: pytest, unittest
- Arduino: arduino-cli lint, serial monitor tests
- CI/CD: GitHub Actions (Black, Flake8, Markdownlint, PyTest, Arduino lint)
