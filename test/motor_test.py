"""
Motor smoke test for ESP32 MicroPython.

Run this with the car lifted off the ground. The script tests:
  1. left motor forward/reverse
  2. right motor forward/reverse
  3. both motors forward/reverse

It always stops motors in finally.
"""

import sys
import time

for path in ("/", "/src_code"):
    if path not in sys.path:
        sys.path.append(path)

from motor import MotorDriver


SPEED_FORWARD = 120
# Current MotorDriver keeps Arduino-style reverse PWM: duty = 255 + speed.
# -200 gives a slow reverse duty, safer for first hardware checks.
SPEED_REVERSE = -200
STEP_MS = 1200
PAUSE_MS = 500


def pause(motor):
    motor.stop()
    time.sleep_ms(PAUSE_MS)


def run_step(motor, name, right, left):
    print("[MOTOR_TEST]", name, "right=", right, "left=", left)
    motor.speed_run(right, left)
    time.sleep_ms(STEP_MS)
    pause(motor)


def main():
    motor = MotorDriver()
    try:
        pause(motor)
        run_step(motor, "left forward", 0, SPEED_FORWARD)
        run_step(motor, "left reverse", 0, SPEED_REVERSE)
        run_step(motor, "right forward", SPEED_FORWARD, 0)
        run_step(motor, "right reverse", SPEED_REVERSE, 0)
        run_step(motor, "both forward", SPEED_FORWARD, SPEED_FORWARD)
        run_step(motor, "both reverse", SPEED_REVERSE, SPEED_REVERSE)
        print("[MOTOR_TEST] done")
    finally:
        motor.stop()
        motor.deinit()
        print("[MOTOR_TEST] stopped")


main()
