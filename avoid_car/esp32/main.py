"""
main.py – Entry point cho avoid_car firmware (ESP32).

Workflow:
  1. Init motor driver, action driver, WiFi comm
  2. Kết nối WiFi → in IP address
  3. Main loop:
     - Đọc action từ UDP (non-blocking)
     - Execute action → điều khiển motor
     - Emergency stop check (button + timeout)
"""

import time
from machine import Pin

from motor import MotorDriver
from action_driver import ActionDriver
from wifi_comm import WiFiComm
from config import (
    WIFI_SSID,
    WIFI_PASS,
    UDP_PORT,
    LOOP_DELAY_MS,
    UDP_TIMEOUT_MS,
    PIN_BUTTON,
)


def main():
    """Main entry point."""
    print("=" * 50)
    print("Avoid Car Firmware — ESP32")
    print("=" * 50)

    # ── Init hardware ──
    print("\n[1/4] Initializing motor driver...")
    motor = MotorDriver()

    print("[2/4] Initializing action driver...")
    driver = ActionDriver(motor)

    print("[3/4] Initializing emergency stop button...")
    button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_UP)

    print("[4/4] Connecting WiFi...")
    wifi = WiFiComm(WIFI_SSID, WIFI_PASS, UDP_PORT)

    try:
        ip = wifi.connect()
    except RuntimeError as e:
        print(f"ERROR: {e}")
        print("Please check SSID/password in config.py")
        return

    print("\n" + "=" * 50)
    print(f"✓ Ready! Listening on {ip}:{UDP_PORT}")
    print("=" * 50)
    print("\nWaiting for actions from PC...")
    print("Press button (GPIO23) for emergency stop.\n")

    # ── Main loop ──
    last_action_time = time.ticks_ms()
    action_count = 0

    try:
        while True:
            # Emergency stop button check
            if button.value() == 0:  # Button pressed (active LOW)
                driver.stop()
                print("\n[EMERGENCY STOP] Button pressed!")
                break

            # Read action from UDP (non-blocking)
            action = wifi.read_action()

            if action is not None:
                # Valid action received
                driver.execute(action)
                last_action_time = time.ticks_ms()
                action_count += 1

                # Print action (throttle output)
                if action_count % 10 == 0:
                    action_name = ["FORWARD", "TURN_LEFT", "TURN_RIGHT"][action]
                    print(f"[{action_count}] Action: {action_name} ({action})")

            else:
                # No action received → check timeout
                elapsed = time.ticks_diff(time.ticks_ms(), last_action_time)
                if elapsed > UDP_TIMEOUT_MS:
                    # Timeout → stop motor for safety
                    driver.stop()
                    # Don't spam console, just wait for next action

            # Loop delay (match simulation timestep)
            time.sleep_ms(LOOP_DELAY_MS)

    except KeyboardInterrupt:
        print("\n[STOP] Keyboard interrupt")

    finally:
        # Cleanup
        print("\nCleaning up...")
        driver.stop()
        motor.deinit()
        wifi.close()
        print("Done.")


if __name__ == "__main__":
    main()
