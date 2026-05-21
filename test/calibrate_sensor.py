"""
Standalone sensor calibration for ESP32 MicroPython.

Upload this file as main.py only when calibrating. It keeps both motors
stopped while you move the sensor array over both the track background and
the black line. It saves /calibration.json, then exits.
"""

import sys
import time

for path in ("/", "/src_code"):
    if path not in sys.path:
        sys.path.append(path)

from calibration import Calibration
from motor import MotorDriver
from sensor import SensorArray


CALIB_SECONDS = 8
SAMPLE_DELAY_MS = 20


def main():
    motor = MotorDriver()
    motor.stop()

    sensor = SensorArray()
    calibration = Calibration()

    print("[CALIB] Start")
    print("[CALIB] Motors stopped.")
    print("[CALIB] Move sensors over both background and black line.")
    print("[CALIB] Duration:", CALIB_SECONDS, "seconds")

    start = time.ticks_ms()
    sample_count = 0

    while time.ticks_diff(time.ticks_ms(), start) < CALIB_SECONDS * 1000:
        motor.stop()
        raw = sensor.read_raw()
        calibration.update(raw)
        sample_count += 1

        if sample_count % 25 == 0:
            mask = sensor.read_bitmask(raw, calibration.compare_value)
            print("raw:", raw)
            print("mask: {:08b}".format(mask), "0x{:02X}".format(mask))
            print("compare:", calibration.compare_value)
            print()

        time.sleep_ms(SAMPLE_DELAY_MS)

    calibration.finalize()
    calibration.save()
    motor.stop()
    motor.deinit()
    calibration.print_values()
    print("[CALIB] Done. Re-upload src_code/main.py to run the car.")


main()
