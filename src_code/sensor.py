"""
sensor.py – Đọc mảng 8 cảm biến dò line.

Mapping từ diagram.jpeg:
  Sensor 8 (D26) → bit 7 ... Sensor 1 (VP/GPIO36) → bit 0
Tất cả chân đều trên ADC1 của ESP32.
"""

from machine import ADC, Pin

from config import (
    ADC_ATTEN,
    ADC_MAX,
    NUM_SENSORS,
    SENSOR_PINS,
)


class SensorArray:
    """Đọc 8 cảm biến IR analog, tạo bitmask và giá trị chuẩn hóa.

    Thứ tự: sensor 8 (trái, bit 7) đọc trước, sensor 1 (phải, bit 0) đọc sau.
    Giống logic read_sensor() trong Arduino: temp = temp << 1 rồi OR bit.
    """

    def __init__(self):
        """Khởi tạo 8 kênh ADC."""
        self._adcs = []
        for pin_num in SENSOR_PINS:
            adc = ADC(Pin(pin_num))
            adc.atten(ADC_ATTEN)  # ATTN_11DB → full range 0–3.3V
            self._adcs.append(adc)

    def read_raw(self):
        """Đọc 8 giá trị ADC thô (đảo giá trị: line đen → giá trị cao).

        Returns:
            list[int]: 8 giá trị đã đảo, index 0 = sensor 8 (trái),
                       index 7 = sensor 1 (phải).
        """
        values = [0] * NUM_SENSORS
        for i in range(NUM_SENSORS):
            values[i] = ADC_MAX - self._adcs[i].read()
        return values

    def read_bitmask(self, raw_values, compare_values):
        """Tạo bitmask 8-bit từ giá trị đọc và ngưỡng so sánh.

        Logic giống Arduino:
          temp = temp << 1
          if sensorValue[j] > compare_value[j]: temp |= 0x01

        Args:
            raw_values: 8 giá trị ADC đã đảo (từ read_raw()).
            compare_values: 8 ngưỡng so sánh (từ calibration).

        Returns:
            int: Bitmask 8-bit. Sensor 8 ở bit 7, sensor 1 ở bit 0.
        """
        mask = 0
        for i in range(NUM_SENSORS):
            mask = mask << 1
            if raw_values[i] > compare_values[i]:
                mask |= 0x01
        return mask

    @staticmethod
    def normalize(raw_values, black_values, white_values):
        """Chuẩn hóa giá trị sensor về 0–1000.

        Giống map() trong Arduino:
          sensorPID[j] = map(sensorValue[j], black, white, 0, 1000)

        Args:
            raw_values: 8 giá trị ADC đã đảo.
            black_values: 8 giá trị min (line đen).
            white_values: 8 giá trị max (nền trắng).

        Returns:
            list[int]: 8 giá trị chuẩn hóa 0–1000.
        """
        normalized = [0] * NUM_SENSORS
        for i in range(NUM_SENSORS):
            # Clamp giá trị trong khoảng [black, white]
            val = raw_values[i]
            bk = black_values[i]
            wh = white_values[i]

            if val < bk:
                val = bk
            if val > wh:
                val = wh

            # Map to 0–1000
            rng = wh - bk
            if rng > 0:
                normalized[i] = (val - bk) * 1000 // rng
            else:
                normalized[i] = 0

        return normalized
