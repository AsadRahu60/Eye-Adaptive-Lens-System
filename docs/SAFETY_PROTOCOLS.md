# Safety Protocols

## Electrical Safety
- All LC shutters driven with AC (no DC bias).
- Watchdog timer resets MCU if unresponsive.

## Optical Safety
- Max lens diopter change: 0.5D per 100ms.
- Smooth occlusion ramp (≥200ms fade).

## Data Safety
- Logs timestamped and signed.
- No personal patient data stored on-device.

## Emergency Conditions
- If sensor anomaly detected → default safe mode.
- If overheating detected → shutdown lenses & shutters.
