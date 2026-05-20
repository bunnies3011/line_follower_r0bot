"""
main.py – Entry point cho xe dò line ESP32 MicroPython.

Quy trình:
  1. Khởi tạo modules
  2. Thử đọc calibration cũ từ flash
  3. Nếu chưa có calibration: quét sensor qua line đen/trắng, nhấn nút để lưu
  4. Chờ nút start
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


def wait_button_press(button):
    """Chờ nút được nhấn rồi nhả ra."""
    while button.value() == 1:
        time.sleep_ms(10)
    wait_button_release(button)


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
        print("[MAIN] Không có calibration cũ.")

    motor.stop()

    if has_saved_calib:
        print()
        print("[MAIN] Nhấn nút (D23) để bắt đầu chạy với calibration đã lưu.")
        wait_button_press(button)
    else:
        # ==================== CALIBRATION LOOP ====================
        print()
        print("[MAIN] === CHẾ ĐỘ HIỆU CHUẨN ===")
        print("[MAIN] Quét cảm biến qua line đen và nền trắng.")
        print("[MAIN] Nhấn nút (D23) để lưu calibration và bắt đầu chạy.")
        print()

        sample_count = 0

        while button.value() == 1:  # Chờ nút được nhấn (LOW = nhấn)
            raw = sensor.read_raw()
            calibration.update(raw)
            sample_count += 1

            # In giá trị debug mỗi 50 lần đọc (~250ms)
            if sample_count % 50 == 0:
                bitmask = sensor.read_bitmask(raw, calibration.compare_value)
                print(
                    "[CALIB] Raw:",
                    raw,
                    " Mask: {:08b}".format(bitmask),
                )

            time.sleep_ms(LOOP_DELAY_MS)

        wait_button_release(button)

        # Lưu calibration
        calibration.finalize()
        calibration.save()
        calibration.print_values()

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
                controller.reset()
                fsm.state = 10  # STATE_STARTUP
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
