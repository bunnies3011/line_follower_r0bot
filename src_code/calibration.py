"""
calibration.py – Hiệu chuẩn cảm biến dò line.

Ghi nhận min (đen) / max (trắng) của từng cảm biến,
tính ngưỡng compare_value = (black + white) / 2.
Lưu/đọc từ file JSON trên flash ESP32 (thay EEPROM Arduino).
"""

import json

from config import (
    ADC_MAX,
    CALIB_DEFAULT_BLACK,
    CALIB_DEFAULT_WHITE,
    CALIB_FILE,
    NUM_SENSORS,
)


class Calibration:
    """Quản lý hiệu chuẩn 8 cảm biến IR.

    Quy trình:
    1. Gọi update() liên tục khi quét cảm biến qua line đen và nền trắng.
    2. black_value[i] = giá trị nhỏ nhất ghi nhận (đã đảo → line đen = thấp).
    3. white_value[i] = giá trị lớn nhất ghi nhận (đã đảo → nền trắng = cao).
    4. compare_value[i] = (black + white) / 2 → ngưỡng phân biệt đen/trắng.

    Lưu ý: Code Arduino đảo giá trị (1023 - analogRead), nên:
      - Line đen → ADC cao → đảo → giá trị THẤP → black_value = min
      - Nền trắng → ADC thấp → đảo → giá trị CAO → white_value = max

    Tuy nhiên code Arduino lại init black_value = 1100 (giá trị cao) và cập nhật
    bằng '<' (lấy min). Chúng ta giữ logic tương tự.
    """

    def __init__(self):
        # black_value = min recorded (init cao để bất kỳ giá trị nào cũng < init)
        self.black_value = [CALIB_DEFAULT_BLACK] * NUM_SENSORS
        # white_value = max recorded (init 0 để bất kỳ giá trị nào cũng > init)
        self.white_value = [CALIB_DEFAULT_WHITE] * NUM_SENSORS
        # Ngưỡng so sánh
        self.compare_value = [ADC_MAX // 2] * NUM_SENSORS
        # Đã hoàn thành hiệu chuẩn chưa
        self.is_calibrated = False

    def update(self, raw_values):
        """Cập nhật min/max từ giá trị đọc được.

        Gọi liên tục trong vòng lặp hiệu chuẩn khi quét cảm biến
        qua cả line đen và nền trắng.

        Args:
            raw_values: list[int] – 8 giá trị ADC đã đảo từ sensor.read_raw().
        """
        for i in range(NUM_SENSORS):
            val = raw_values[i]
            # Giữ giá trị min hợp lý (tránh 0 tuyệt đối)
            if self.black_value[i] == CALIB_DEFAULT_BLACK:
                self.black_value[i] = val
            if val < self.black_value[i]:
                self.black_value[i] = val
            if val > self.white_value[i]:
                self.white_value[i] = val
            # Cập nhật ngưỡng
            self.compare_value[i] = (self.black_value[i] + self.white_value[i]) // 2

    def finalize(self):
        """Đánh dấu hoàn thành hiệu chuẩn."""
        self.is_calibrated = True

    def save(self):
        """Lưu dữ liệu hiệu chuẩn vào file JSON trên flash.

        Thay thế EEPROM trên Arduino. Lưu nguyên giá trị 12-bit,
        không mất độ phân giải như code Arduino gốc (chia 4 rồi nhân 4).
        """
        data = {
            "black": self.black_value,
            "white": self.white_value,
            "compare": self.compare_value,
        }
        try:
            with open(CALIB_FILE, "w") as f:
                json.dump(data, f)
            print("[CALIB] Saved to", CALIB_FILE)
        except OSError as e:
            print("[CALIB] Save failed:", e)

    def load(self):
        """Đọc dữ liệu hiệu chuẩn từ file JSON.

        Returns:
            bool: True nếu đọc thành công, False nếu file không tồn tại
                  hoặc dữ liệu không hợp lệ.
        """
        try:
            with open(CALIB_FILE, "r") as f:
                data = json.load(f)
            self.black_value = data["black"]
            self.white_value = data["white"]
            self.compare_value = data["compare"]
            self.is_calibrated = True
            print("[CALIB] Loaded from", CALIB_FILE)
            return True
        except (OSError, KeyError, ValueError) as e:
            print("[CALIB] Load failed:", e)
            return False

    def print_values(self):
        """In giá trị hiệu chuẩn ra console (debug)."""
        print("[CALIB] Black:  ", self.black_value)
        print("[CALIB] White:  ", self.white_value)
        print("[CALIB] Compare:", self.compare_value)
