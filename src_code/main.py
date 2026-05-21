"""
main.py – Entry point cho xe dò line ESP32 MicroPython.

Quy trình:
  1. Khởi tạo modules
  2. Thử đọc calibration cũ từ flash
  3. Có calibration thì dùng calibration đã lưu; chưa có thì dùng ngưỡng mặc định
  4. Tự chạy sau khi cấp nguồn, không chờ nút start
  5. Vòng lặp chính: đọc sensor → PD → FSM → motor
"""

import time

from machine import Pin

from calibration import Calibration
from config import LOOP_DELAY_MS, PIN_BUTTON, SPEED_DEFAULT
from controller import PDController
from fsm import LineFollowerFSM
from motor import MotorDriver
from sensor import SensorArray


def wait_button_release(button):
    """Chờ nút được nhả ra (debounce đơn giản)."""
    while button.value() == 0:
        time.sleep_ms(10)
    time.sleep_ms(50)


def main():
    """Hàm chính – khởi tạo và chạy xe dò line."""
    print("=" * 40)
    print("  LINE FOLLOWER CAR – ESP32 MicroPython")
    print("=" * 40)

    # ==================== INIT ====================
    # Button (pull-up, nhấn = LOW)
    button = Pin(PIN_BUTTON, Pin.IN, Pin.PULL_UP)

    # Modules
    motor = MotorDriver()
    sensor = SensorArray()
    calibration = Calibration()
    controller = PDController()

    # Thử đọc calibration cũ
    has_saved_calib = calibration.load()
    if has_saved_calib:
        print("[MAIN] Calibration cũ đã tải.")
        calibration.print_values()
    else:
        print("[MAIN] Không có calibration cũ. Dùng ngưỡng mặc định.")

    motor.stop()

    print()
    print("[MAIN] Tự chạy sau khi cấp nguồn.")

    print()
    print("[MAIN] === BẮT ĐẦU CHẠY ===")
    print("[MAIN] Tốc độ:", SPEED_DEFAULT)
    print()

    # Delay khởi động (đặt xe lên track)
    time.sleep_ms(500)

    # ==================== MAIN LOOP ====================
    # Khởi tạo FSM
    controller.reset()
    fsm = LineFollowerFSM(motor, sensor, controller, calibration)
    fsm.speed = SPEED_DEFAULT

    try:
        while True:
            # FSM update (đọc sensor + PD + điều khiển motor bên trong)
            fsm.update()

            # Nút nhấn = dừng khẩn cấp
            if button.value() == 0:
                print("[MAIN] DỪNG KHẨN CẤP!")
                motor.stop()
                wait_button_release(button)

                # Nhấn lần nữa để chạy lại
                print("[MAIN] Nhấn nút để chạy lại...")
                while button.value() == 1:
                    time.sleep_ms(50)
                wait_button_release(button)

                print("[MAIN] Tiếp tục chạy...")
                fsm.reset()
                time.sleep_ms(500)

            time.sleep_ms(LOOP_DELAY_MS)

    except KeyboardInterrupt:
        print("\n[MAIN] Đã dừng bằng Ctrl+C.")
    finally:
        motor.stop()
        motor.deinit()
        print("[MAIN] Motor đã tắt. Kết thúc.")


# Auto-run khi ESP32 khởi động
main()
