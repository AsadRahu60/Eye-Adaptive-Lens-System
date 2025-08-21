# Software Requirements Specification (SRS)

## Scope
Software stack controls adaptive lenses and LC shutters, logs therapy data, and provides UI integration.

## Functional Requirements
- FR1: Control per-eye tunable lenses (smooth ramp, step, calibration).
- FR2: Control LC shutters (gradual occlusion, programmable profiles).
- FR3: Read sensor inputs (distance, ambient light, IMU).
- FR4: Communicate with host app via BLE.
- FR5: Store and retrieve therapy logs.

## Non-Functional Requirements
- Reliability: >99% successful actuation in bench tests.
- Latency: <200ms for sensor-to-actuator response.
- Safety: watchdog resets, emergency shutdown.
- Portability: ESP32 + Python 3 host.

## Interfaces
- Firmware: C++ (Arduino ESP32 core).
- Host: Python modules.
- UI: BLE GATT, optional Flutter app.
