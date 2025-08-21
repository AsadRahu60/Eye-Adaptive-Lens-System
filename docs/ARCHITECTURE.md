# Architecture

The **Eye–Adaptive Lens System** integrates embedded sensing and actuation with host-side control logic and user-facing interfaces. It is designed for modularity, safety, and clinical scalability.

---

## High-Level Components

- **ESP32-S3 Microcontroller**
  - Integrates sensors (distance, ambient light, IMU)  
  - Provides Bluetooth Low Energy (BLE) communication  
  - Drives liquid crystal (LC) shutters and tunable lenses  

- **Tunable Lenses**
  - One per eye, electronically adjustable focus  
  - Controlled via ESP32 and Raspberry Pi host  

- **Raspberry Pi 5 (or PC Host)**
  - Runs therapy policy engine and orchestration logic  
  - Stores session logs in CSV or database format  
  - Monitors safety and watchdog conditions  

- **Sensors**
  - **Distance:** VL53L1X  
  - **Ambient light:** TSL2591  
  - **IMU:** BNO055 for motion tracking  

- **Mobile/Web UI**
  - Used by patients and clinicians for configuration  
  - Displays therapy progress and compliance reports  
  - Communicates with host for monitoring and analytics  

---

## Data Flow

1. **Sensors → ESP32**: Collect distance, ambient, and motion data  
2. **ESP32 → Host (Pi/PC)**: Transmit telemetry and receive commands via BLE  
3. **Host → Lenses/Shutters**: Send control commands for optical actuation  
4. **Logs → Storage**: Record session-level data for compliance and research  
5. **UI → Host**: Configure therapy and visualize results in real time  

---

## System Diagrams

See [README.md](../README.md) for detailed **Mermaid diagrams**, which illustrate:  
- Optical subsystem (tunable lenses, LC shutters)  
- Embedded control (ESP32-S3)  
- Host orchestration (Raspberry Pi/PC)  
- User interface layer (mobile/web)  

---

## Design Principles

- **Modular:** Each subsystem can be tested independently  
- **Safety-First:** Watchdogs, slew-rate limits, and safe defaults prevent unsafe optical output  
- **Traceable:** Requirements (URS → SRS → RTM → Test Cases) ensure systematic validation  
- **Extendable:** Architecture supports future ML-driven therapy policies and clinical studies  
