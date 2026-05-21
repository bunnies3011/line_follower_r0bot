"""
Sensor debug test for ESP32 MicroPython.

Prints raw inverted ADC values, bitmask, and normalized values.
Use it to verify that the line lights the expected bit:
  left edge  -> bit 7 / 0x80
  right edge -> bit 0 / 0x01
"""

import sys
import time

for path in ("/", "/src_code"):
    if path not in sys.path:
        sys.path.append(path)

from calibration import Calibration
from sensor import SensorArray


def main():
    sensor = SensorArray()
    calibration = Calibration()
    calibration.load()

    while True:
        raw = sensor.read_raw()
        mask = sensor.read_bitmask(raw, calibration.compare_value)
        normalized = sensor.normalize(
            raw,
            calibration.black_value,
            calibration.white_value,
        )
        print("raw:", raw)
        print("mask: {:08b}".format(mask), "0x{:02X}".format(mask))
        print("norm:", normalized)
        print()
        time.sleep_ms(300)


main()
