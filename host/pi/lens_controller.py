from __future__ import annotations

import time
import serial


class OptoLens:
    def __init__(self, port: str, baud: int = 115200, timeout: float = 0.2) -> None:
        self.ser = serial.Serial(port, baud, timeout=timeout)

    def set_diopter(self, dpt: float) -> str:
        # Replace with your LD-4/ICC command (placeholder)
        self.ser.write(f"SET DIOP {dpt:.2f}\n".encode())
        return self.ser.readline().decode(errors="ignore").strip()


if __name__ == "__main__":
    lens = OptoLens("/dev/ttyUSB0")
    d = 1.00
    step = 0.05
    try:
        while True:
            print("Set:", lens.set_diopter(d))
            d += step
            if d > 2.0 or d < 1.0:
                step = -step
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
